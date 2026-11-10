"""Bounded MAIN controller regressions. Synthetic data; no collection writes."""
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from test_progress import Controller,card,config
import test_startup
from cram_studio import writing

class MainParityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.fixture=Controller(self.temp.name);self.owner=self.fixture.owner

    def test_restart_random_replaces_only_active_checkpoint_and_never_resumes_old_answers(self):
        o=self.owner;other=self.fixture.launch([card('other')],config('other'))
        sid=self.fixture.launch([card('a'),card('b'),card('c')],dict(config(),repeat_mistakes=True))
        o.submit({'index':0,'picks':{'known':False}})
        self.assertEqual(len(o.questions),4)
        # A no-op RNG is still required to produce a different random order.
        with patch('random.SystemRandom.shuffle',lambda *args:None):o.restart()
        self.assertNotEqual(o.session_id,sid)
        self.assertEqual([q['id'] for q in o.questions],['b','c','a'])
        self.assertEqual(o.results,{})
        self.assertFalse(any(q['is_retry'] for q in o.questions))
        self.assertEqual(o.view.get('written',{}),{})
        self.assertEqual(o.store.data['history'],[])
        self.assertEqual({v['id'] for v in o.store.saved_sessions()},{other,o.session_id})
        before=o.practice.snapshot()
        for action in ('restart','grade','write_submit'):
            o.bridge('cram:'+json.dumps({'action':action,'session_id':sid,'index':0,'picks':{'known':True}}))
        self.assertEqual(o.practice.snapshot(),before,'late old-session events are ignored')

    def test_restart_fixed_sequence_preserves_order_and_never_opens_anki_collection(self):
        o=self.owner
        class Forbidden:
            def __getattr__(self,name):raise AssertionError('Restart must not access Anki: '+name)
        o.mw.col=Forbidden()
        self.fixture.launch([card('c'),card('a'),card('b')],dict(config(),order='created_desc'))
        o.submit({'index':0,'picks':{'known':True}});o.restart()
        self.assertEqual([q['id'] for q in o.questions],['c','a','b'])
        self.assertEqual(o.results,{})
        self.assertEqual(self.fixture.jobs,[])

    def test_writing_complete_cannot_be_resubmitted_or_replaced_by_stale_frontend_events(self):
        o=self.owner;q=card(mode='write');q['slots'][0].update(answer='banana',answer_html='banana')
        writing.attach([q],{},whole=True);self.fixture.launch([q],config(mode='write'))
        o.write_submit({'index':0,'text':'BANANA','target':0,'events':[]})
        saved=copy.deepcopy(o.view['written']['0']['events'])
        o.save_progress({'index':0,'written':{'0':{'events':[],'draft':'','target':0}}})
        self.assertEqual(o.view['written']['0']['events'],saved)
        o.write_submit({'index':0,'text':'a second accidental Enter','target':0,'events':[]})
        self.assertEqual(o.view['written']['0']['events'],saved)
        o.submit({'index':0,'picks':{'writing':[]}})
        self.assertEqual(o.results['0']['earned'],1)
        self.assertEqual(o.results['0']['total'],1)

    def test_writing_wrong_can_be_revealed_and_finished_without_correcting(self):
        o=self.owner;q=card(mode='write');q['slots'][0].update(answer='banana',answer_html='banana')
        writing.attach([q],{},whole=True);self.fixture.launch([q,card('next')],config(mode='write'))
        o.write_submit({'index':0,'text':'stone','target':0,'events':[]})
        self.assertEqual(self.fixture.events[-1][1]['state']['last']['status'],'wrong')
        o.submit({'index':0,'picks':{'unknown':True}})
        self.assertEqual(o.results['0']['earned'],0)
        o.submit({'index':1,'picks':{'known':True}})
        self.assertEqual(len(o.results),2)

    def test_individual_mask_checkpoint_survives_reopen_and_rejects_invalid_masks(self):
        o=self.owner;q=card(mode='flash',kind='io');q.update(mask_count=2,slots=[],picture='<div></div>')
        sid=self.fixture.launch([q])
        o.save_progress({'index':0,'ioMasks':{'0':{'open':[0,0,1,2,-1,True],'closed':[],'seen':True}}})
        other=Controller(self.temp.name);other.owner.resume(sid)
        self.assertEqual(other.owner.view['ioMasks'],{'0':{'open':[0,1],'closed':[],'seen':True}})
        self.assertEqual(other.owner.results,{})

    def test_entry_buttons_are_scoped_to_main_native_webview_and_do_not_start_a_review(self):
        ns,mw,live,actions,calls,warnings=test_startup.LauncherTests().environment('overview')
        ns['Path']=Path;ns['__file__']=str(Path(__file__).resolve().parents[1]/'cram_studio/__init__.py')
        scripts=[];mw.web=types.SimpleNamespace(eval=scripts.append)
        ns['entry_buttons'](types.SimpleNamespace(web=mw.web))
        self.assertIn('window.cramEntryMount()',scripts[-1])
        ns['entry_buttons'](types.SimpleNamespace(eval=lambda _:self.fail('unrelated webview')))
        self.assertEqual(len(scripts),1)
        ns['message']((False,None),'cram_live_open',None)
        self.assertEqual(calls,['setup'])
        mw.state='review';ns['entry_buttons'](mw.web)
        self.assertEqual(len(scripts),1)

class OverviewVisibilityTests(unittest.TestCase):
    def test_only_duplicate_overview_bar_hides_and_native_review_restores_it(self):
        ns,mw,live,actions,calls,warnings=test_startup.LauncherTests().environment('overview')
        visible=[True];events=[]
        mw.bottomWeb=types.SimpleNamespace(isVisible=lambda:visible[0],hide=lambda:(visible.__setitem__(0,False),events.append('hide')),show=lambda:(visible.__setitem__(0,True),events.append('show')))
        ns['message']((False,None),'cram_overview_controls:1',None)
        self.assertFalse(visible[0]);self.assertEqual(ns['overview_bottom_visibility'],True)
        ns['live_state']('review','overview')
        self.assertTrue(visible[0]);self.assertIsNone(ns['overview_bottom_visibility'])
        before=list(events);ns['message']((False,None),'cram_overview_controls:0',None)
        self.assertEqual(events,before)

    def test_native_bottom_links_remain_unmodified_except_old_cram_entries(self):
        ns,*_=test_startup.LauncherTests().environment('overview')
        links=[['O','opts','Options'],['','cram_studio_open','MAIN CRAM'],['','cram_live_open','ANKI CRAM'],['','studylist_open','Study List']]
        ns['overview'](None,links)
        self.assertEqual(links,[['O','opts','Options'],['','studylist_open','Study List']])

if __name__=='__main__':unittest.main()
