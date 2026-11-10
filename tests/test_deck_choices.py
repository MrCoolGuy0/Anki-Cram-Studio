"""Sparse home/filtered membership, full-deck plans and resumable API batches."""
import ast
import copy
import importlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import types
import unittest
from concurrent.futures import Future

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
c=importlib.import_module('cram_studio.content');b=importlib.import_module('cram_studio.bulk_choices');g=importlib.import_module('cram_studio.gemini');s=importlib.import_module('cram_studio.storage')

def collection():
    db=sqlite3.connect(':memory:')
    db.executescript('create table cards(id integer primary key,nid integer,did integer,ord integer,odid integer default 0);create table notes(id integer primary key,mid integer,flds text);')
    models={1:{'id':1,'type':1,'name':'Cloze','flds':[{'name':'Text'}],'tmpls':[{'qfmt':'{{cloze:Text}}'}]},2:{'id':2,'type':0,'name':'Basic (and reversed card)','flds':[{'name':'Front'},{'name':'Back'}],'tmpls':[{'qfmt':'{{Front}}'},{'qfmt':'{{Back}}'}]}}
    decks=[types.SimpleNamespace(id=1,name='Course'),types.SimpleNamespace(id=10,name='Course::Lesson'),types.SimpleNamespace(id=20,name='Course::Lesson 2'),types.SimpleNamespace(id=90,name='Filtered')]
    class DB:
        def all(self,query,*params):
            if not query.lower().startswith('select '):raise AssertionError('Collection write attempted')
            return db.execute(query,params).fetchall()
    def get_card(cid):
        cid,nid,did,ordinal,odid,mid,fields=db.execute('select c.*,n.mid,n.flds from cards c join notes n on c.nid=n.id where c.id=?',(cid,)).fetchone()
        note=types.SimpleNamespace(id=nid,fields=fields.split('\x1f'),note_type=lambda:models[mid])
        return types.SimpleNamespace(id=cid,ord=ordinal,did=did,note=lambda:note)
    col=types.SimpleNamespace(db=DB(),decks=types.SimpleNamespace(all_names_and_ids=lambda **kwargs:decks,get_current_id=lambda:10),models=types.SimpleNamespace(all=lambda:list(models.values())),find_cards=lambda query:[2,3],get_card=get_card)
    return db,col,decks

class DeckScopeTests(unittest.TestCase):
    def setUp(self):
        self.db,self.col,self.decks=collection();self.addCleanup(self.db.close)
        for cid,did,odid,ordinal in ((1,10,0,0),(2,90,10,1),(3,20,0,0)):
            self.db.execute('insert into cards values(?,?,?,?,?)',(cid,100 if cid<3 else 101,did,ordinal,odid))
        self.db.execute('insert into notes values(100,1,?)',('{{c1::first}} and {{c2::second}}',));self.db.execute('insert into notes values(101,1,?)',('{{c1::third}}',))
        self.before='\n'.join(self.db.iterdump())
    def test_parent_total_and_lesson_include_borrowed_cards(self):
        cat=c.catalog(self.col);decks={d['id']:d for d in cat['decks']}
        self.assertEqual(decks['1']['count'],0);self.assertEqual(decks['1']['total_count'],3)
        self.assertEqual(decks['10']['count'],2);self.assertEqual(decks['10']['borrowed_count'],1);self.assertEqual(decks['90']['count'],1)
        self.assertEqual(sum(g['count'] for g in cat['scope_groups']),3)
    def test_regular_filtered_and_overlapping_selection_agree_with_snapshot(self):
        for ids,count in ((['10'],2),(['90'],1),(['10','90'],2),(['1','90'],3)):
            config={'decks':ids,'mode':'exam','limit':0,'shuffle':False}
            with self.subTest(ids=ids):
                matches=c.count_matches(self.col,config);out,total=c.snapshot(self.col,config,{})
                self.assertEqual((matches['count'],matches['total'],total,len(out['questions'])),(count,)*4)
                self.assertEqual(len({q['cid'] for q in out['questions']}),count)
        self.assertEqual('\n'.join(self.db.iterdump()),self.before)
    def test_filtered_view_keeps_filtered_label_regular_view_uses_home_label(self):
        for ids,label in ((['90'],'Filtered'),(['10'],'Course::Lesson')):
            out,_=c.snapshot(self.col,{'decks':ids,'mode':'exam','limit':0},{})
            borrowed=next(q for q in out['questions'] if q['cid']=='2');self.assertEqual(borrowed['deck'],label)
    def test_due_search_intersects_full_home_membership_and_no_subdeck_setting(self):
        config={'decks':['1'],'children':False,'filters':{'search':'is:due'}}
        self.assertEqual(c.count_matches(self.col,config)['count'],0)
        config.update(decks=['10']);self.assertEqual(c.count_matches(self.col,config),{'count':1,'total':2,'query':'(is:due)'})
        out,count=c.snapshot(self.col,dict(config,mode='exam',limit=0),{});self.assertEqual(count,1);self.assertEqual(out['questions'][0]['cid'],'2')
    def test_cloze_siblings_in_different_home_decks_keep_correct_lesson_label(self):
        self.db.execute('update cards set odid=20 where id=2')
        out,_=c.snapshot(self.col,{'decks':['1'],'mode':'exam','limit':0},{})
        by_id={q['cid']:q for q in out['questions']}
        self.assertEqual(by_id['1']['deck'],'Course::Lesson');self.assertEqual(by_id['2']['deck'],'Course::Lesson 2')
    def test_large_selection_batches_do_not_duplicate_home_filtered_card(self):
        self.decks[:]=[types.SimpleNamespace(id=i,name='D'+str(i)) for i in range(1,1002)]
        self.db.execute('update cards set did=700,odid=10 where id=2')
        ids=[str(i) for i in range(1,1002)]
        self.assertEqual(c.count_matches(self.col,{'decks':ids})['count'],3)
        self.assertEqual(len(c.scoped_rows(self.col,list(map(int,ids)))),3)
    def test_full_deck_regeneration_ignores_practice_filters_and_question_limit(self):
        config={'decks':['1','90'],'children':True,'mode':'flash','limit':1,'filters':{'search':'is:due'},'order':'shuffle'}
        plan=b.deck_choice_plan(self.col,config,{},'model')
        self.assertEqual((plan['cards'],plan['questions'],plan['sets']),(3,3,3));self.assertEqual({j['answer'] for j in plan['jobs']},{'first','second','third'})
        self.assertEqual('\n'.join(self.db.iterdump()),self.before)
    def test_bulk_normalizes_scope_and_never_falls_back_to_collection(self):
        for config in ({},{'decks':'10'},{'decks':['bad']}):
            with self.assertRaises(ValueError):b.bulk_config(config)
        self.assertEqual(b.bulk_config({'decks':['10','10'],'limit':1,'filters':{'search':'is:due'}})['decks'],['10'])
    def test_basic_auto_and_actual_native_reverse_directions_both_get_choice_sets(self):
        self.db.execute('delete from cards');self.db.execute('delete from notes')
        self.db.execute('insert into notes values(200,2,?)',('Short term\x1fA detailed definition describing this short term',))
        self.db.executemany('insert into cards values(?,?,?,?,?)',[(4,200,10,0,0),(5,200,10,1,0)])
        plan=b.deck_choice_plan(self.col,{'decks':['10']},{},'model')
        self.assertEqual((plan['cards'],plan['questions'],plan['sets']),(2,1,2))
        self.assertEqual({job['answer'] for job in plan['jobs']},{'Short term','A detailed definition describing this short term'})

class BatchControlTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    def controller(self,fail_second=False,pause_first=False):
        calls=[];tasks=[];updates=[];state={'attempts':0}
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):
                calls.append([j['id'] for j in jobs]);state['attempts']+=1
                if pause_first and state['attempts']==1:owner.stop()
                if fail_second and state['attempts']==2:raise g.AIError('Quota reached')
                return {j['id']:['New A','New B','New C'] for j in jobs}
        tree=ast.parse((ROOT/'cram_studio/deck_choices.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('start','stop')]
        ns={'threading':threading,'Gemini':Client,'generate_batches':g.generate_batches,
            'run_network':lambda mw,work,done:mw.taskman.run_in_background(work,done,uses_collection=False)};exec(compile(ast.Module(body=methods,type_ignores=[]),'<batch-methods>','exec'),ns)
        widget=types.SimpleNamespace(setText=lambda value:updates.append(value),setValue=lambda value:updates.append(value),setEnabled=lambda value:None)
        owner=types.SimpleNamespace(running=False,reading=False,closed=False,run_token=0,jobs=[{'id':str(i)} for i in range(15)],total=15,completed=0,model='model',changed_keys=set(),store=s.Store(self.tmp.name),controls=lambda:None,status=widget,progress=widget,pause=widget,generate=widget,mw=types.SimpleNamespace(taskman=types.SimpleNamespace(run_on_main=lambda fn:fn(),run_in_background=lambda work,done,*,uses_collection=True:tasks.append((work,done)))))
        for method in methods:setattr(owner,method.name,types.MethodType(ns[method.name],owner))
        owner.store.generation_parallelism=1;owner.store.set_key('key');owner.store.put({str(i):['Old A','Old B','Old C'] for i in range(15)})
        def finish(index):
            work,done=tasks[index];future=Future()
            try:future.set_result(work())
            except Exception as error:future.set_exception(error)
            done(future)
        return owner,calls,updates,finish
    def test_force_replaces_cached_sets_and_resume_skips_completed_batches(self):
        owner,calls,updates,finish=self.controller(pause_first=True);owner.start();finish(0)
        self.assertEqual((owner.completed,len(owner.jobs)),(10,5));self.assertEqual(owner.changed_keys,set(map(str,range(10))));self.assertFalse(owner.running)
        self.assertEqual(owner.store.cache()['10'],['Old A','Old B','Old C']);owner.start();finish(1)
        self.assertEqual(calls,[list(map(str,range(10))),list(map(str,range(10,15)))]);self.assertEqual(owner.completed,15);self.assertEqual(owner.jobs,[])
        self.assertTrue(all(values==['New A','New B','New C'] for values in owner.store.cache().values()));self.assertEqual(owner.store.data['history'],[])
    def test_failed_second_batch_retains_first_ten_and_only_retries_remaining(self):
        owner,calls,updates,finish=self.controller(fail_second=True);owner.start();finish(0)
        self.assertEqual((owner.completed,len(owner.jobs)),(10,5));self.assertIn('Quota reached',updates)
        owner.start();finish(1);self.assertEqual(owner.completed,15);self.assertEqual(calls[-1],['10','11','12','13','14'])
    def test_bulk_refresh_of_active_native_card_is_question_side_only_without_rating(self):
        from test_live_review import Environment
        tree=ast.parse((ROOT/'cram_studio/__init__.py').read_text());method=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='open_deck_choices')
        module=types.ModuleType('cram_studio.deck_choices');prior=sys.modules.get(module.__name__);sys.modules[module.__name__]=module
        self.addCleanup(lambda:sys.modules.pop(module.__name__,None) if prior is None else sys.modules.__setitem__(module.__name__,prior))
        for reveal in (False,True):
            e=Environment(self.tmp.name);e.live.begin('exam');e.packet();q=e.live.current['question'];model=e.live.store.data['model']
            jobs,_=c.prepare_choices([q],{},model);e.live.store.put({job['id']:['Old A','Old B','Old C'] for job in jobs});c.attach_choices([q],e.live.store.cache(),model)
            choices=copy.deepcopy(q['slots'][0]['choices']);token=(e.live.current['cid'],e.live.current['epoch'])
            class Dialog:
                def __init__(self,*args):self.closed=False;self.changed_keys={job['id'] for job in jobs}
                def show(self):pass
                def exec(self):
                    e.live.store.put({job['id']:['New A','New B','New C'] for job in jobs})
                    if reveal:e.packet('reviewAnswer')
            module.DeckChoices=Dialog
            ns={'__package__':'cram_studio','mw':e.mw,'live':e.live,'window':None,'deck_choices':None,'showWarning':lambda *args,**kwargs:self.fail('Unexpected warning')}
            exec(compile(ast.Module(body=[method],type_ignores=[]),'<open-deck-choices>','exec'),ns);ns['open_deck_choices']({'decks':['90']})
            self.assertEqual((e.live.current['cid'],e.live.current['epoch']),token);self.assertEqual(e.calls,['study'])
            if reveal:self.assertEqual(q['slots'][0]['choices'],choices);self.assertNotIn('choices_revision',e.live.current)
            else:self.assertEqual(e.live.current['choices_revision'],1);self.assertEqual(q['slots'][0]['wrong'],['New A','New B','New C'])
        s.clear_profile_stores()

if __name__=='__main__':unittest.main()
