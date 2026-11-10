"""Collection-write tripwires and native-delegation tests; no scheduler emulation.

These tests validate the add-on boundary. They do not run Anki's Rust scheduler
or diagnose the scheduling history of a user's actual collection.
"""
import ast
import copy
from concurrent.futures import Future
import importlib
import json
from pathlib import Path
import sqlite3
import tempfile
import types
import unittest
from unittest.mock import patch

from test_progress import Controller,Store
from test_live_review import Environment,Card

ROOT=Path(__file__).resolve().parents[1]
c=importlib.import_module('cram_studio.content')
g=importlib.import_module('cram_studio.gemini')
bulk=importlib.import_module('cram_studio.bulk_choices')

def column(key):
    enum=types.SimpleNamespace(values_by_number={1:types.SimpleNamespace(name='SORTING_CARDS_ASCENDING')})
    return types.SimpleNamespace(key=key,cards_mode_label=key,sorting_cards=1,
        DESCRIPTOR=types.SimpleNamespace(fields_by_name={'sorting_cards':types.SimpleNamespace(enum_type=enum)}))

class ReadOnlyCollection:
    """Full scheduling/revlog data on SQLite, plus forbidden API tripwires."""
    def __init__(self):
        db=self.connection=sqlite3.connect(':memory:');self.denied=[];self.queries=[]
        db.executescript('''
          create table cards(id integer primary key,nid integer,did integer,ord integer,
            mod integer,usn integer,type integer,queue integer,due integer,ivl integer,
            factor integer,reps integer,lapses integer,left integer,odue integer,odid integer,flags integer,data text);
          create table notes(id integer primary key,mid integer,flds text,tags text,mod integer,usn integer);
          create table revlog(id integer primary key,cid integer,usn integer,ease integer,ivl integer,lastIvl integer,factor integer,time integer,type integer);
          create table col(id integer primary key,conf text,decks text,dconf text);
        ''')
        self.deck_data=[{'id':10,'name':'ITPM','dyn':0}, {'id':11,'name':'ITPM::Lesson','dyn':0},
                        {'id':90,'name':'Filtered','dyn':1,'resched':False}]
        self.options={'fsrs':True,'desiredRetention':.9,'new':{'delays':[1,10]},'lapse':{'delays':[10]},'reviewLimit':200}
        db.execute('insert into col values(1,?,?,?)',(json.dumps({'rollover':4,'collapseTime':1200}),json.dumps(self.deck_data),json.dumps(self.options)))
        # New, same-day learning, review, relearning, suspended, buried, filtered
        # rescheduling/preview metadata, and distinct cloze siblings.
        states=[(0,0,0,10,0),(1,1,0,10,0),(2,2,0,10,0),(3,1,0,11,0),
                (2,-1,0,11,0),(2,-2,0,11,0),(2,2,10,90,0),(2,4,10,90,0),(2,2,0,11,0)]
        for cid,(kind,queue,odid,did,ordinal) in enumerate(states,1):
            db.execute('insert into notes values(?,?,?,?,?,?)',(cid,1,'A detailed clue for item '+str(cid)+'\x1fTerm '+str(cid),' test ',1700000000,8))
            due=1700000100 if queue in (1,4) else 200
            db.execute('insert into cards values('+','.join('?' for _ in range(18))+')',
                (cid,cid,did,ordinal,1700000001,8,kind,queue,due,12,2450,7,2,1001,190 if odid else 0,odid,3,json.dumps({'s':9.5,'d':6.1,'dr':.9})))
            db.execute('insert into revlog values(?,?,?,?,?,?,?,?,?)',(1700000000000+cid,cid,8,3,12,8,2450,4500,1))
        db.execute('insert into notes values(100,2,?,?,?,?)',('{{c1::First}} is {{c2::Second}}',' cloze ',1700000000,8))
        for cid,ordinal in ((20,0),(21,1)):
            db.execute('insert into cards select ?,100,11,?,mod,usn,type,queue,due,ivl,factor,reps,lapses,left,odue,odid,flags,data from cards where id=3',(cid,ordinal))
        db.commit();db.execute('pragma query_only=ON')
        self.db=types.SimpleNamespace(all=self.read)
        self.media=types.SimpleNamespace(escape_media_filenames=lambda value:value)
        self.decks=types.SimpleNamespace(all_names_and_ids=lambda **kwargs:[types.SimpleNamespace(id=d['id'],name=d['name']) for d in self.deck_data],get_current_id=lambda:10,current=lambda:self.deck_data[0])
        self.model_data=[{'id':1,'name':'Basic','type':0,'flds':[{'name':'Front'},{'name':'Back'}]},
                         {'id':2,'name':'Cloze','type':1,'flds':[{'name':'Text'}]}]
        self.models=types.SimpleNamespace(all=lambda:self.model_data)
        self.baseline=self.state()
    def __getattr__(self,name):
        self.denied.append(name);raise AssertionError('MAIN CRAM must not access collection API: '+name)
    def read(self,sql,*args):
        if not sql.lstrip().lower().startswith('select '):
            self.denied.append(sql);raise AssertionError('Collection write attempted: '+sql)
        self.queries.append(sql);return self.connection.execute(sql,args).fetchall()
    def all_browser_columns(self):return [column(key) for key in ('cardDue','cardLapses','cardRetrievability')]
    def get_card(self,cid):
        cid,nid,did,ordinal,mid,fields=self.read('select c.id,c.nid,c.did,c.ord,n.mid,n.flds from cards c join notes n on n.id=c.nid where c.id=?',cid)[0]
        card=Card(cid=cid,ordinal=ordinal);card.did=did;card.fields=fields.split('\x1f');card.model=copy.deepcopy(next(m for m in self.model_data if m['id']==mid))
        card.n=types.SimpleNamespace(id=nid,fields=card.fields,note_type=lambda:card.model)
        return card
    def find_cards(self,query,order=None,reverse=False):
        # This is only a read-only search spy, not an Anki search parser test.
        where='queue in (1,2,4)' if 'is:due' in query else '1'
        if 'is:new' in query:where='type=0'
        if 'is:learn' in query:where='type in (1,3)'
        return [r[0] for r in self.read('select id from cards where '+where+' order by due '+('desc' if reverse else 'asc')+',id')]
    def state(self):return self.connection.serialize(),copy.deepcopy(self.deck_data),copy.deepcopy(self.options),self.connection.total_changes
    def assert_unchanged(self,test):
        test.assertEqual(self.state(),self.baseline);test.assertEqual(self.denied,[])

class MainScheduleBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.col=ReadOnlyCollection();self.addCleanup(self.col.connection.close)
    def test_every_practice_mode_filter_and_order_leaves_all_schedule_and_revlog_bytes_unchanged(self):
        orders=('shuffle','created_asc','created_desc','due_random','due_deck','deck_due','anki:cardLapses','retrievability_asc','retrievability_desc')
        for mode in ('flash','exam','mixed'):
            for query in ('','is:due','is:new','is:learn'):
                for order in orders:
                    with self.subTest(mode=mode,query=query,order=order):
                        cfg={'decks':['10'],'mode':mode,'children':True,'limit':0,'order':order,'filters':{'search':query}}
                        out,count=c.snapshot(self.col,cfg,{})
                        self.assertGreater(count,0);self.assertTrue(out['questions']);c.count_matches(self.col,cfg)
                        self.col.assert_unchanged(self)
        self.assertGreater(len(self.col.queries),100)
    def test_actual_main_start_generate_grade_resume_retry_reset_and_close_never_touch_schedule(self):
        for mode in ('flash','exam','mixed'):
            with self.subTest(mode=mode):
                fixture=Controller(Path(self.temp.name)/mode);o=fixture.owner;tasks=[]
                o.mw.col=self.col;o.mw.taskman=types.SimpleNamespace(run_on_main=lambda fn:fn(),run_in_background=lambda work,done,*,uses_collection=True:tasks.append((work,done)))
                env=o.start.__func__.__globals__
                env.update(snapshot=c.snapshot,catalog=c.catalog,count_matches=c.count_matches,cache_key=c.cache_key,generate_batches=g.generate_batches)
                class LocalChoiceClient:
                    def __init__(self,*args):pass
                    def generate(self,jobs):return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
                env['Gemini']=LocalChoiceClient
                def drain():
                    while fixture.jobs:
                        job=fixture.jobs.pop(0);job.success(job.op(self.col))
                o.bridge('cram:'+json.dumps({'action':'ready'}));drain()
                cfg={'decks':['10'],'mode':mode,'children':True,'limit':0,'order':'created_asc','filters':{'search':''}}
                o.bridge('cram:'+json.dumps({'action':'preview','config':cfg,'request_id':1}));drain()
                o.store.data['preferences']['repeat_mistakes']=True
                o.bridge('cram:'+json.dumps({'action':'start','config':cfg}));drain()
                if not o.started:
                    o.generate()
                    for work,done in tasks:
                        future=Future();future.set_result(work());done(future)
                self.assertTrue(o.started);sid=o.session_id
                first=o.questions[0];wrong={'known':False} if first['mode']=='flash' else {'unknown':True}
                o.submit({'index':0,'picks':wrong});o.save_progress({'index':1,'picks':{},'revealed':[]})
                o.closeEvent(types.SimpleNamespace(accept=lambda:None,ignore=lambda:self.fail('Unexpected close failure')))
                restored=Controller(Path(self.temp.name)/mode).owner;restored.mw.col=self.col;restored.resume(sid)
                self.assertEqual(len(restored.results),1)
                for index in range(1,len(restored.questions)):
                    q=restored.questions[index];picks={'known':True} if q['mode']=='flash' else {'choices':[slot['correct'] for slot in q['slots']]}
                    restored.submit({'index':index,'picks':picks})
                restored.finish();self.assertFalse(restored.store.saved_sessions());self.assertEqual(len(restored.store.data['history']),1)
                restored.retry(False);new_sid=restored.session_id;self.assertNotEqual(new_sid,sid)
                restored.bridge('cram:'+json.dumps({'action':'home'}));restored.bridge('cram:'+json.dumps({'action':'reset_progress','session_id':new_sid}))
                self.assertFalse(restored.store.saved_sessions());self.col.assert_unchanged(self)
    def test_full_deck_choice_regeneration_plan_is_also_read_only(self):
        plan=bulk.deck_choice_plan(self.col,{'decks':['10'],'children':True},{},'test-model')
        self.assertGreater(plan['sets'],0);self.col.assert_unchanged(self)
    def test_write_tripwires_really_fail(self):
        with self.assertRaises(sqlite3.OperationalError):self.col.connection.execute('update cards set due=999')
        with self.assertRaises(AssertionError):self.col.read('update cards set due=999')
        with self.assertRaises(AssertionError):_ = self.col.sched
        self.assertEqual(self.col.state(),self.col.baseline)

class NativeScheduleBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.addCleanup(importlib.import_module('cram_studio.storage').clear_profile_stores)
    def test_native_card_identity_order_and_scheduling_fields_are_never_replaced(self):
        for mode in ('flash','exam'):
            for filtered,resched in ((False,False),(True,False),(True,True)):
                with self.subTest(mode=mode,filtered=filtered,resched=resched):
                    e=Environment(self.temp.name,filtered,resched);e.live.begin(mode);deck=copy.deepcopy(e.col.deck)
                    for cid,queue,kind in ((503,2,'Basic'),(12,0,'Cloze'),(808,1,'Basic')):
                        native=Card(cid=cid,kind=kind)
                        native.queue=queue;native.due=200;native.ivl=12;native.factor=2450;native.reps=8;native.lapses=2;native.data='{"s":9.5,"d":6.1}';native.odid=10 if filtered else 0;native.odue=190 if filtered else 0
                        e.mw.reviewer.card=native;before=copy.deepcopy(native.__dict__);e.packet();e.packet('reviewAnswer')
                        self.assertIs(e.mw.reviewer.card,native);self.assertEqual(native.__dict__,before);self.assertEqual(e.live.current['cid'],str(cid));self.assertEqual(e.col.deck,deck)
                    self.assertEqual(e.calls,['study']);e.live.close();self.assertEqual(e.col.deck,deck)
    def test_all_four_rating_callbacks_are_the_original_native_functions_in_every_deck_mode(self):
        for mode in ('flash','exam'):
            for filtered,resched in ((False,False),(True,False),(True,True)):
                with self.subTest(mode=mode,filtered=filtered,resched=resched):
                    e=Environment(self.temp.name,filtered,resched);e.live.begin(mode);e.packet();before=copy.deepcopy(e.col.deck)
                    if mode=='exam':
                        q=e.live.current['question'];jobs,_=c.prepare_choices([q],{},e.live.store.data['model'])
                        e.live.store.put({j['id']:['Wrong A','Wrong B','Wrong C'] for j in jobs});c.attach_choices([q],e.live.store.cache(),e.live.store.data['model'])
                    calls=[];tokens=[object() for _ in range(4)]
                    def native_callback(ease):
                        def run():calls.append((ease,e.mw.reviewer.card.id,e.col.deck.get('resched')));return tokens[ease-1]
                        return run
                    originals=[native_callback(i) for i in range(1,5)];keys=[(str(i),fn) for i,fn in enumerate(originals,1)]
                    e.live.shortcuts('review',keys)
                    if mode=='exam':
                        for _,fn in keys:fn()
                        self.assertEqual(calls,[],'front-side MCQ choices never rate')
                    e.packet('reviewAnswer')
                    for i,(_,fn) in enumerate(keys):
                        # Native callbacks own all side effects. The skin neither
                        # chooses ease nor computes/replaces any returned interval.
                        fn();self.assertEqual(calls[-1],(i+1,e.mw.reviewer.card.id,resched))
                    self.assertEqual(len(calls),4);self.assertEqual(e.col.deck,before);self.assertEqual(e.calls,['study'])
                    self.assertEqual(e.live.store.data['history'],[])
    def test_native_bridge_commands_pass_through_unchanged_and_custom_commands_cannot_rate(self):
        for resched in (False,True):
            e=Environment(self.temp.name,True,resched);e.live.begin('exam');e.packet()
            for side in ('reviewQuestion','reviewAnswer'):
                e.packet(side)
                for raw in ('ans','ease1','ease2','ease3','ease4','edit','undo'):
                    handled=(False,object());self.assertIs(e.live.message(handled,raw,e.mw.reviewer),handled)
                for action in ('ans','ease1','ease2','ease3','ease4','grade','reschedule','set_due_date','finish'):
                    e.message(action)
            self.assertEqual(e.calls,['study']);self.assertEqual(e.col.deck['resched'],resched)
    def test_native_undo_is_delegated_and_stale_or_other_window_commands_cannot_call_it(self):
        e=Environment(self.temp.name);e.live.begin('flash');e.packet();packet=copy.deepcopy(e.live.current)
        message='cram_live:'+json.dumps({'action':'undo','cid':packet['cid'],'epoch':packet['epoch']})
        handled=(False,object());self.assertIs(e.live.message(handled,message,object()),handled)
        e.message('undo',epoch=-1);self.assertEqual(e.calls,['study'])
        e.message('undo');self.assertEqual(e.calls,['study','native undo'])
        e.mw.reviewer.card=Card(cid=123);e.packet();e.live.message((False,None),message,e.mw.reviewer)
        self.assertEqual(e.calls,['study','native undo']);self.assertEqual(e.live.current['cid'],'123')

class SourceBoundaryTests(unittest.TestCase):
    def test_no_direct_collection_scheduler_or_mutation_api_in_runtime_sources(self):
        forbidden={'sched','_backend','update_card','update_cards','set_due_date','reschedule_cards','schedule_cards_as_new','rebuild_filtered_deck','empty_filtered_deck','set_deck','bury_cards','unbury_cards','suspend_cards','unsuspend_cards','set_config','set_config_bool','set_config_string'}
        for path in (ROOT/'cram_studio').glob('*.py'):
            tree=ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Attribute):self.assertNotIn(node.attr,forbidden,path.name+': '+node.attr)
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('execute','executemany','executescript'):
                    self.fail(path.name+': unexpected SQL mutation-capable call')

if __name__=='__main__':unittest.main()
