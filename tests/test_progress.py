"""Short disk/reopen regressions, exercising actual MAIN controller methods."""
import ast
import copy
import importlib
import json
import random
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
import uuid
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
content=importlib.import_module('cram_studio.content')
Store=importlib.import_module('cram_studio.storage').Store
PracticeSession=importlib.import_module('cram_studio.session').PracticeSession

def card(identity='a',mode='flash',kind='basic'):
    slots=[{'number':1,'answer':'Correct','answer_html':'<b>Correct</b>'}]
    if mode=='exam':slots[0].update(wrong=['Wrong one','Wrong two','Wrong three'],choices=['Wrong one','Correct','Wrong two','Wrong three'],correct=1)
    return {'id':identity,'cid':identity,'deck':'Subject::Lesson','kind':kind,'mode':mode,'clue':'A <span class="ct-blank" data-blank="0">_____</span> clue','slots':slots,'ready':True}

def config(deck='1',mode='flash'):
    return {'decks':[deck],'mode':mode,'limit':0,'children':True,'order':'shuffle','order_desc':False,'filters':{'search':'','tag':'','note_type':'','flag':''}}

class Controller:
    def __init__(self,profile):
        self.clock=[1000];self.events=[];self.jobs=[]
        fixture=self
        class Query:
            def __init__(self,parent,op,success):self.op=op;self.success=success;fixture.jobs.append(self)
            def failure(self,fn):self.failed=fn;return self
            def run_in_background(self):pass
        node=next(n for n in ast.parse((ROOT/'cram_studio/dialog.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='CramDialog')
        node.bases=[]
        clock=types.SimpleNamespace(time=lambda:self.clock[0],strftime=lambda *args:'2026-10-23 10:00')
        namespace=dict(writing=importlib.import_module('cram_studio.writing'),copy=copy,json=json,time=clock,uuid=uuid,threading=threading,PracticeSession=PracticeSession,random=random,
            QueryOp=Query,catalog=lambda col:None,snapshot=lambda *args:None,theme_manager=types.SimpleNamespace(night_mode=False),
            attach_choices=content.attach_choices,prepare_choices=content.prepare_choices,
            run_network=lambda mw,work,done:mw.taskman.run_in_background(work,done,uses_collection=False))
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-main-controller>','exec'),namespace)
        cls=namespace['CramDialog'];self.owner=owner=cls.__new__(cls)
        owner.closed=False;owner.booting=False;owner.busy=False;owner.generating=False;owner.questions=[];owner.results={};owner.started=0;owner.finished=False
        owner.session_id=None;owner.view={};owner.elapsed=0;owner.token=0;owner.cancel=threading.Event();owner.initial_deck=None;owner.models=[]
        owner.store=Store(profile);owner.store.generation_parallelism=1;owner.mw=types.SimpleNamespace(serverURL=lambda:'http://127.0.0.1/')
        owner.emit=lambda event,data=None:self.events.append((event,copy.deepcopy(data)))
    def launch(self,questions=None,options=None):
        o=self.owner;o.questions=questions or [card('a'),card('b')];o.config=options or config()
        o.store.put({content.cache_key(q,s,o.store.data['model']):s['wrong'] for q in o.questions if q['mode']=='exam' for s in q['slots']})
        o.launch();return o.session_id

class ProgressTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
    def test_restart_preserves_queue_results_retries_and_original_score(self):
        a=Controller(self.temp.name);sid=a.launch(options=dict(config(),repeat_mistakes=True));o=a.owner
        o.submit({'index':0,'picks':{'known':False}});a.clock[0]+=30
        o.save_progress({'index':1,'picks':{},'revealed':[1],'activeSlot':0,'zoom':1.5,'scroll':120})
        before=copy.deepcopy(o.practice.snapshot());a.clock[0]+=10
        accepted=[];o.closeEvent(types.SimpleNamespace(accept=lambda:accepted.append(True),ignore=lambda:accepted.append(False)))
        self.assertEqual(accepted,[True])
        b=Controller(self.temp.name);b.clock[0]=100000;b.owner.resume(sid);r=b.owner
        self.assertEqual(r.practice.snapshot(),before);self.assertEqual(r.view['index'],1);self.assertEqual(r.view['revealed'],[1]);self.assertEqual(r.view['zoom'],1.5)
        self.assertEqual(r.elapsed,40,'closed time is excluded');self.assertEqual(b.jobs,[],'resume must not query/rebuild or make AI requests')
        for i in range(1,len(r.questions)):r.submit({'index':i,'picks':{'known':True}})
        r.finish();self.assertEqual(r.store.saved_sessions(),[]);history=Store(self.temp.name).data['history']
        self.assertEqual(len(history),1);self.assertEqual(history[0]['earned'],1);self.assertEqual(history[0]['repeat_attempts'],1)
        r.finish();self.assertEqual(len(r.store.data['history']),1,'finish is idempotent')
    def test_flashcard_recall_remains_available_after_flipping_back_and_reopening(self):
        a=Controller(self.temp.name);sid=a.launch([card(),card('b')]);o=a.owner
        o.save_progress({'index':0,'picks':{},'revealed':[],'flashSeen':[0,1,999,True]})
        self.assertEqual(o.view['flashSeen'],[0]);self.assertEqual(o.view['revealed'],[])
        b=Controller(self.temp.name);b.owner.resume(sid)
        self.assertEqual(b.owner.view['flashSeen'],[0]);self.assertEqual(b.owner.view['revealed'],[])
        self.assertEqual(b.owner.results,{});self.assertEqual(b.owner.store.data['history'],[])
    def test_mcq_choices_partial_picks_and_active_blank_are_not_reshuffled(self):
        a=Controller(self.temp.name);q=card(mode='exam',kind='cloze');q['slots'].append(dict(q['slots'][0],number=2,answer='Other',answer_html='Other'))
        sid=a.launch([q,card('b')],config(mode='exam'));o=a.owner
        choices=copy.deepcopy(o.questions[0]['slots']);o.save_progress({'index':0,'picks':{'0':[2,None]},'revealed':[],'activeSlot':1,'zoom':1})
        b=Controller(self.temp.name);b.owner.resume(sid)
        self.assertEqual(b.owner.questions[0]['slots'],choices);self.assertEqual(b.owner.view['picks'],{'0':[2,None]});self.assertEqual(b.owner.view['activeSlot'],1)
        self.assertEqual(b.events[-1][0],'session');self.assertTrue(b.events[-1][1]['restored']);self.assertEqual(b.owner.store.data['history'],[])
    def test_multiple_sets_are_kept_and_exact_start_resumes_instead_of_rebuilding(self):
        a=Controller(self.temp.name);one=a.launch();a.owner.bridge('cram:'+json.dumps({'action':'home'}))
        two=a.launch([card('other')],config('2'));self.assertNotEqual(one,two)
        self.assertEqual(len(Store(self.temp.name).saved_sessions()),2)
        b=Controller(self.temp.name);b.owner.start({'config':config()})
        self.assertEqual(b.owner.session_id,one);self.assertEqual(b.jobs,[]);self.assertEqual(len(b.owner.store.saved_sessions()),2)
        b.owner.bridge('cram:'+json.dumps({'action':'reset_progress','session_id':two}))
        self.assertEqual([item['id'] for item in Store(self.temp.name).saved_sessions()],[one])
    def test_checkpoints_are_small_and_stale_session_messages_are_ignored(self):
        a=Controller(self.temp.name);sid=a.launch();o=a.owner
        path=o.store._session_path(sid);before=path.read_bytes();before_mtime=path.stat().st_mtime_ns
        o.bridge('cram:'+json.dumps({'action':'checkpoint','session_id':sid,'view':{'index':999,'picks':{'0':[None]},'revealed':[999],'activeSlot':0}}))
        self.assertEqual(o.view['index'],0);self.assertEqual(o.view['revealed'],[])
        self.assertEqual(path.read_bytes(),before);self.assertEqual(path.stat().st_mtime_ns,before_mtime,'UI saves do not rewrite the full queue/cache')
        view=o.store.session_view(sid);o.bridge('cram:'+json.dumps({'action':'checkpoint','session_id':'f'*32,'view':{'index':1}}))
        self.assertEqual(o.store.session_view(sid),view)
    def test_finish_removes_only_current_set_and_retains_preferences_and_cache(self):
        a=Controller(self.temp.name);one=a.launch([card()]);two=a.launch([card('two')],config('2'))
        a.owner.store.put({'saved-choice':['A','B','C']});a.owner.submit({'index':0,'picks':{'known':True}});a.owner.finish()
        store=Store(self.temp.name);self.assertEqual([item['id'] for item in store.saved_sessions()],[one]);self.assertNotIn(two,store.data['sessions']);self.assertIn('saved-choice',store.cache());self.assertTrue(store.data['preferences']['auto_advance'])
    def test_profiles_are_separate_and_corrupt_snapshots_are_preserved(self):
        a=Controller(Path(self.temp.name)/'A');sid=a.launch()
        self.assertEqual(Store(Path(self.temp.name)/'B').saved_sessions(),[])
        target=a.owner.store._session_path(sid);target.write_text('broken')
        with self.assertRaisesRegex(ValueError,'preserved'):a.owner.store.session(sid)
        self.assertEqual(target.read_text(),'broken');self.assertIn(sid,a.owner.store.data['sessions'])
        with self.assertRaises(ValueError):a.owner.store.delete_session('../practice')
    def test_snapshot_restore_is_independent_and_rejects_missing_or_nonsequential_results(self):
        session=PracticeSession([card(),card('b')]);session.submit(0,{'known':True});data=session.snapshot()
        restored=PracticeSession.restore(data);restored.questions[0]['clue']='Changed';self.assertNotEqual(session.questions[0]['clue'],restored.questions[0]['clue'])
        data['results']={'1':data['results']['0']}
        with self.assertRaises(ValueError):PracticeSession.restore(data)
    def test_failed_atomic_replace_keeps_previous_disk_snapshot(self):
        a=Controller(self.temp.name);sid=a.launch();o=a.owner;path=o.store._session_path(sid);before=path.read_bytes()
        with patch('cram_studio.storage.os.replace',side_effect=OSError('disk write failed')):
            with self.assertRaises(OSError):o.save_progress(full=True)
        self.assertEqual(path.read_bytes(),before);self.assertEqual(list(o.store.path.glob('.cram-*')),[])
    def test_failed_completion_or_reset_retains_session_index_and_history(self):
        a=Controller(self.temp.name);sid=a.launch([card()]);o=a.owner;o.submit({'index':0,'picks':{'known':True}})
        with patch.object(o.store,'save',side_effect=OSError('disk write failed')):
            with self.assertRaises(OSError):o.finish()
            self.assertFalse(o.finished);self.assertIn(sid,o.store.data['sessions']);self.assertEqual(o.store.data['history'],[])
            with self.assertRaises(OSError):o.store.delete_session(sid)
            self.assertIn(sid,o.store.data['sessions'])
        o.finish();self.assertEqual(len(Store(self.temp.name).data['history']),1);self.assertEqual(o.store.saved_sessions(),[])
    def test_reset_and_close_cancel_stale_generation_without_anki_writes(self):
        a=Controller(self.temp.name);sid=a.launch();o=a.owner;o.generating=True;token=o.token
        o.bridge('cram:'+json.dumps({'action':'reset_progress','session_id':sid}))
        self.assertGreater(o.token,token);self.assertTrue(o.cancel.is_set());self.assertIsNone(o.session_id);self.assertEqual(o.store.saved_sessions(),[])
        self.assertEqual(o.store.data['history'],[])
    def test_grade_is_durable_even_without_a_frontend_checkpoint_and_pending_ai_stays_paused(self):
        a=Controller(self.temp.name);sid=a.launch([card(),card('b',mode='exam')]);o=a.owner
        o.submit({'index':0,'picks':{'known':True}})
        o.questions[1]['ready']=False;o.questions[1]['slots'][0].pop('choices');o.save_progress(full=True)
        b=Controller(self.temp.name);b.owner.resume(sid)
        self.assertEqual(len(b.owner.results),1);self.assertFalse(b.owner.questions[1]['ready']);self.assertFalse(b.owner.generating);self.assertEqual(b.jobs,[])

if __name__=='__main__':unittest.main()
