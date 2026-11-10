"""Bounded regressions for cloze isolation, native ordering and progressive generation."""
import ast
import copy
import importlib
import pathlib
import sys
import tempfile
import threading
import types
import unittest
from concurrent.futures import Future

ROOT=pathlib.Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
c=importlib.import_module('cram_studio.content')
g=importlib.import_module('cram_studio.gemini')
Store=importlib.import_module('cram_studio.storage').Store
PracticeSession=importlib.import_module('cram_studio.session').PracticeSession

def questions():
    m={'id':1,'name':'Cloze','type':1,'flds':[{'name':'Text'}]}
    rows=[(9,100,10,1,1,'{{c1::life}} is {{c2::good}}'),(8,100,10,0,1,'{{c1::life}} is {{c2::good}}'),(10,101,10,0,1,'A {{c1::newer}} note')]
    return rows,m

class OrderingAndReadyTests(unittest.TestCase):
    def test_one_actual_cloze_number_in_every_mode(self):
        rows,m=questions()
        for mode in ('flash','exam','mixed'):
            out=c.compile_questions(rows,{1:m},{10:'Deck'},{'mode':mode,'order':'created_asc','limit':0},{})['questions']
            self.assertEqual(len(out),3)
            self.assertEqual([s['answer'] for s in out[0]['slots']],['life']);self.assertIn('good',out[0]['clue']);self.assertNotIn('life',out[0]['clue'])
            self.assertEqual([s['answer'] for s in out[1]['slots']],['good']);self.assertIn('life',out[1]['clue']);self.assertNotIn('good',out[1]['clue'])
            self.assertIn('data-blank="0"',out[0]['clue'])
    def test_creation_desc_keeps_c1_before_c2_within_same_note(self):
        rows,m=questions();out=c.compile_questions(rows,{1:m},{10:'Deck'},{'mode':'flash','order':'created_desc','limit':0},{})['questions']
        self.assertEqual([q['cid'] for q in out],['10','8','9'])
    def test_native_rank_is_applied_before_limit(self):
        rows,m=questions();out=c.compile_questions(rows,{1:m},{10:'Deck'},{'mode':'exam','order':'retrievability_asc','_card_rank':{'9':0,'10':1,'8':2},'limit':2},{})['questions']
        self.assertEqual([q['cid'] for q in out],['9','10'])
    def test_retrievability_is_never_fabricated(self):
        rows,m=questions()
        with self.assertRaisesRegex(ValueError,'supplied by Anki'):c.compile_questions(rows,{1:m},{10:'Deck'},{'order':'retrievability_desc'},{})
        with self.assertRaisesRegex(ValueError,'does not expose'):c.native_retrievability_order(types.SimpleNamespace(),'',False)
    def test_native_column_direction_and_no_browser_preference_mutation(self):
        for default in ('ASCENDING','DESCENDING'):
            enum=types.SimpleNamespace(values_by_number={7:types.SimpleNamespace(name='SORTING_'+default)})
            colspec=types.SimpleNamespace(key='retrievability',sorting_cards=7,DESCRIPTOR=types.SimpleNamespace(fields_by_name={'sorting_cards':types.SimpleNamespace(enum_type=enum)}))
            calls=[]
            def find(query,**kwargs):calls.append((query,kwargs));return [9,8]
            col=types.SimpleNamespace(all_browser_columns=lambda:[colspec],find_cards=find)
            for descending in (False,True):
                self.assertEqual(c.native_retrievability_order(col,'is:due',descending),[9,8]);self.assertEqual(calls[-1][1]['reverse'],(default=='ASCENDING')==descending);self.assertIs(calls[-1][1]['order'],colspec)
    def test_partial_choices_preserve_live_option_indices(self):
        rows,m=questions();qs=c.compile_questions(rows,{1:m},{10:'Deck'},{'mode':'exam','shuffle':False,'limit':0},{})['questions']
        jobs,_=c.prepare_choices(qs,{},'model');cache={jobs[0]['id']:['one','two','three']}
        changed=c.attach_choices(qs,cache,'model',partial=True)
        self.assertEqual([q['id'] for q in changed],[qs[0]['id']]);self.assertFalse(qs[1]['ready']);before=copy.deepcopy(qs[0]['slots'])
        with self.assertRaisesRegex(ValueError,'still being prepared'):c.grade(qs[1],{'unknown':True})
        cache[jobs[1]['id']]=['a','b','c'];changed=c.attach_choices(qs,cache,'model',partial=True)
        self.assertEqual(qs[0]['slots'],before);self.assertEqual([q['id'] for q in changed],[qs[1]['id']])
    def test_first_small_batch_then_larger_batches_and_pause_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            store=Store(td);batches=[];progress=[];event=threading.Event()
            class Client:
                def generate(self,jobs):batches.append([j['id'] for j in jobs]);return {j['id']:['a','b','c'] for j in jobs}
            g.generate_batches(Client(),[{'id':str(i)} for i in range(9)],store,event,lambda done,total:progress.append(done),first_size=1)
            self.assertEqual(list(map(len,batches)),[1,5,3]);self.assertEqual(progress,[1,6,9]);self.assertEqual(len(store.cache()),9)

class ProgressiveDialogTests(unittest.TestCase):
    def test_actual_controller_allows_grading_during_generation_and_ignores_stale_callbacks(self):
        tree=ast.parse((ROOT/'cram_studio/dialog.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CramDialog')
        names=('generate','launch','submit','stop_generation','save_progress','session_packet','clear_saved_picks')
        methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
        background=[];main=[];events=[]
        class Tasks:
            def run_on_main(self,fn):main.append(fn)
            def run_in_background(self,work,done,*,uses_collection=True):background.append((work,done))
        class Client:
            def __init__(self,key,model):pass
            def generate(self,jobs):
                if main:
                    main.pop(0)()
                    self_test.assertTrue(owner.questions[0]['ready']);self_test.assertFalse(owner.questions[1]['ready'])
                    owner.submit({'index':0,'picks':{'choices':[owner.questions[0]['slots'][0]['correct']]}})
                return {j['id']:['wrong a','wrong b','wrong c'] for j in jobs}
        import time,uuid
        env=dict(writing=importlib.import_module('cram_studio.writing'),threading=threading,time=time,uuid=uuid,Gemini=Client,generate_batches=g.generate_batches,cache_key=c.cache_key,prepare_choices=c.prepare_choices,attach_choices=c.attach_choices,PracticeSession=PracticeSession,
            run_network=lambda mw,work,done:mw.taskman.run_in_background(work,done,uses_collection=False))
        exec(compile(ast.Module(body=methods,type_ignores=[]),'<dialog-methods>','exec'),env)
        with tempfile.TemporaryDirectory() as td:
            self_test=self
            store=Store(td);store.generation_parallelism=1;store.set_key('test-key')
            rows,m=questions();qs=c.compile_questions(rows,{1:m},{10:'Deck'},{'mode':'exam','shuffle':False,'limit':0},{})['questions']
            owner=types.SimpleNamespace(busy=False,generating=False,closed=False,started=0,questions=qs,results={},config={},store=store,token=0,cancel=threading.Event(),emit=lambda e,d:events.append((e,copy.deepcopy(d))),mw=types.SimpleNamespace(taskman=Tasks()))
            for name in names:setattr(owner,name,types.MethodType(env[name],owner))
            owner.generate();self.assertFalse(owner.busy);self.assertTrue(owner.generating);self.assertEqual(events[0][0],'session');self.assertFalse(owner.questions[0]['ready'])
            work,done=background[0];future=Future();future.set_result(work())
            # First completed request unlocks question 1 while the session is active.
            self.assertEqual(events[-1][0],'graded');self.assertEqual(len(owner.results),1)
            saved=copy.deepcopy(owner.questions[0]['slots']);main.pop(0)();self.assertEqual(saved,owner.questions[0]['slots'])
            done(future);self.assertFalse(owner.generating);self.assertEqual(len(owner.results),1);self.assertTrue(all(q.get('ready') for q in owner.questions))
            owner.stop_generation();count=len(events);done(future);self.assertEqual(len(events),count,'old workers cannot update a replacement session')

if __name__=='__main__':unittest.main()
