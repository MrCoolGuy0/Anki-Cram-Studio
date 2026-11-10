"""Real bounded worker overlap, out-of-order checkpoints and quota recovery."""
import ast
from concurrent.futures import Future,ThreadPoolExecutor
import importlib
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    pkg=types.ModuleType('cram_studio');pkg.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=pkg
g=importlib.import_module('cram_studio.gemini')
n=importlib.import_module('cram_studio.network_jobs')
s=importlib.import_module('cram_studio.storage')


class Memory:
    def __init__(self):self.values={}
    def put(self,values):self.values.update(values)


class ParallelGeneration(unittest.TestCase):
    def jobs(self,count):return [{'id':str(i),'answer':'Term'} for i in range(count)]
    def test_two_batches_overlap_without_exceeding_two_requests(self):
        release=threading.Event();both=threading.Event();lock=threading.Lock();active=[0];maximum=[0];calls=[]
        class Client:
            def generate(self,jobs):
                with lock:
                    active[0]+=1;maximum[0]=max(maximum[0],active[0]);calls.append([j['id'] for j in jobs])
                    if active[0]==2:both.set()
                try:
                    if not release.wait(2):raise AssertionError('Requests did not overlap')
                    return {j['id']:['A','B','C'] for j in jobs}
                finally:
                    with lock:active[0]-=1
        store=Memory();runner=ThreadPoolExecutor(max_workers=1)
        future=runner.submit(g.generate_batches,Client(),self.jobs(30),store,threading.Event(),lambda *a:None,
                             batch_size=10,parallelism=2)
        try:
            self.assertTrue(both.wait(1));self.assertFalse(future.done());self.assertEqual(len(calls),2)
            release.set();self.assertEqual(future.result(timeout=2),30)
            self.assertEqual(maximum[0],2);self.assertEqual(len(store.values),30)
            self.assertEqual(sorted(x for group in calls for x in group),sorted(map(str,range(30))))
        finally:release.set();runner.shutdown(wait=True)
    def test_cancel_stops_new_requests_and_keeps_both_started_results(self):
        barrier=threading.Barrier(2);calls=[];event=threading.Event();store=Memory()
        class Client:
            def generate(self,jobs):
                calls.append(jobs);barrier.wait(timeout=2)
                return {j['id']:['A','B','C'] for j in jobs}
        with self.assertRaises(g.Cancelled):
            g.generate_batches(Client(),self.jobs(50),store,event,lambda *args:event.set(),batch_size=10,parallelism=2)
        self.assertEqual(len(calls),2);self.assertEqual(len(store.values),20)
    def test_priority_question_is_committed_before_parallel_batches_start(self):
        store=Memory();barrier=threading.Barrier(2);progress=[];first_seen=[]
        class Client:
            def generate(self,jobs):
                if jobs[0]['id']!='0':
                    first_seen.append('0' in store.values);barrier.wait(timeout=2)
                return {j['id']:['A','B','C'] for j in jobs}
        self.assertEqual(g.generate_batches(Client(),self.jobs(21),store,threading.Event(),
            lambda done,total:progress.append(done),first_size=1,batch_size=10,parallelism=2),21)
        self.assertEqual(progress[0],1);self.assertEqual(first_seen,[True,True])
    def test_default_single_card_path_remains_sequential(self):
        caller=threading.get_ident();seen=[];store=Memory()
        class Client:
            def generate(self,jobs):seen.append(threading.get_ident());return {j['id']:['A','B','C'] for j in jobs}
        g.generate_batches(Client(),self.jobs(6),store,threading.Event(),lambda *args:None)
        self.assertEqual(seen,[caller,caller])
    def test_priority_quota_failure_falls_back_before_other_requests_start(self):
        calls=[];store=Memory()
        class Client:
            def generate(self,jobs):
                calls.append(jobs);raise g.AIError('Rate limit',429)
        with self.assertRaises(g.AIError):
            g.generate_batches(Client(),self.jobs(30),store,threading.Event(),lambda *a:None,
                first_size=1,batch_size=10,parallelism=2)
        self.assertEqual(len(calls),1);self.assertEqual(store.generation_parallelism,1)
    def test_parallel_timing_context_is_thread_safe_and_marks_overlap(self):
        with tempfile.TemporaryDirectory() as folder:
            worker=n.NetworkJobs(types.SimpleNamespace(run_on_main=lambda fn:None),folder);store=Memory()
            class Client:
                def generate(self,jobs):
                    for _ in range(100):n.record_phase('http',.001)
                    return {j['id']:['A','B','C'] for j in jobs}
            try:
                future=worker.submit(lambda:g.generate_batches(Client(),self.jobs(20),store,threading.Event(),
                    lambda *a:None,batch_size=10,parallelism=2),lambda f:None)
                self.assertEqual(future.result(timeout=2),20);worker.pool.shutdown(wait=True)
                import json
                row=json.loads(worker.path.read_text())
                self.assertEqual(row['api_parallelism'],2)
                self.assertEqual(row['phases']['http']['count'],200)
                self.assertEqual(row['phases']['http']['total_ms'],200)
            finally:worker.close();worker.pool.shutdown(wait=True);worker.api_pool.shutdown(wait=True)
    def test_pause_is_labeled_separately_from_request_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            worker=n.NetworkJobs(types.SimpleNamespace(run_on_main=lambda fn:None),folder)
            try:
                def work():raise g.Cancelled('Generation paused')
                with self.assertRaises(g.Cancelled):worker.submit(work,lambda f:None).result(timeout=1)
                worker.pool.shutdown(wait=True)
                import json
                self.assertEqual(json.loads(worker.path.read_text())['status'],'cancelled')
            finally:worker.close();worker.api_pool.shutdown(wait=True)


class DeckCheckpointTests(unittest.TestCase):
    def check_failure(self,status):
        saved_tail=threading.Event();tasks=[];state={'fail':True};calls=[]
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):
                calls.append([j['id'] for j in jobs])
                if jobs[0]['id']=='0' and state['fail']:
                    if not saved_tail.wait(2):raise AssertionError('Tail was never saved')
                    raise g.AIError('Synthetic error',status)
                return {j['id']:['New A','New B','New C'] for j in jobs}
        methods=[]
        for cls in ast.parse((ROOT/'cram_studio/deck_choices.py').read_text()).body:
            if isinstance(cls,ast.ClassDef):methods=[fn for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name=='start']
        scope={'threading':threading,'Gemini':Client,'generate_batches':g.generate_batches,
               'run_network':lambda mw,work,done:tasks.append((work,done))}
        exec(compile(ast.Module(body=methods,type_ignores=[]),'actual-deck-start','exec'),scope)
        with tempfile.TemporaryDirectory() as folder:
            store=s.Store(folder);store.set_key('synthetic-key');store.put({str(i):['Old A','Old B','Old C'] for i in range(15)})
            def status_text(value):
                if value.startswith('5 / 15'):saved_tail.set()
            widget=types.SimpleNamespace(setText=status_text,setValue=lambda value:None)
            owner=types.SimpleNamespace(running=False,reading=False,closed=False,run_token=0,
                jobs=[{'id':str(i),'answer':'Term'} for i in range(15)],total=15,completed=0,model='model',
                changed_keys=set(),store=store,controls=lambda:None,status=widget,progress=widget,generate=widget,
                mw=types.SimpleNamespace(taskman=types.SimpleNamespace(run_on_main=lambda fn:fn())))
            start=types.MethodType(scope['start'],owner)
            def finish():
                work,done=tasks.pop(0);future=Future()
                try:future.set_result(work())
                except Exception as error:future.set_exception(error)
                done(future)
            start();finish()
            self.assertEqual(owner.completed,5)
            self.assertEqual([j['id'] for j in owner.jobs],list(map(str,range(10))))
            self.assertEqual(owner.changed_keys,set(map(str,range(10,15))))
            if status==429:self.assertEqual(store.generation_parallelism,1)
            state['fail']=False;start();finish()
            self.assertEqual(owner.completed,15);self.assertEqual(owner.jobs,[])
            self.assertEqual(calls[-1],list(map(str,range(10))))
            self.assertTrue(all(value==['New A','New B','New C'] for value in store.cache().values()))
    def test_out_of_order_success_survives_failure_and_resume_does_not_skip_ids(self):self.check_failure(500)
    def test_quota_error_preserves_other_result_and_resume_falls_back_to_one_request(self):self.check_failure(429)


if __name__=='__main__':unittest.main()
