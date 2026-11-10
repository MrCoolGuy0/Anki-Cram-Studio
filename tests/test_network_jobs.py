"""Bounded real-worker checks; synthetic replies, never a live Gemini key."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package = types.ModuleType('cram_studio')
    package.__path__ = [str(ROOT/'cram_studio')]
    sys.modules['cram_studio'] = package
n = importlib.import_module('cram_studio.network_jobs')
g = importlib.import_module('cram_studio.gemini')


class NetworkJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.workers = []
        def close():
            n.close_network()
            for worker in self.workers:worker.pool.shutdown(wait=True)
        self.addCleanup(close)
        self.callbacks = []
        self.mw = types.SimpleNamespace(pm=types.SimpleNamespace(profileFolder=lambda: self.temp.name),
            taskman=types.SimpleNamespace(run_on_main=self.callbacks.append))
    def submit(self, work, done):
        future = n.run_network(self.mw, work, done)
        self.workers.extend(worker for worker in n._pools.values() if worker not in self.workers)
        return future
    def drain(self):
        for worker in self.workers:worker.pool.shutdown(wait=True)
        for fn in list(self.callbacks):fn()
        self.callbacks.clear()
    def test_work_runs_off_main_and_result_waits_for_main_thread_bridge(self):
        seen=[]
        future=self.submit(lambda: threading.current_thread() is threading.main_thread(),
            lambda future: seen.append((future.result(), threading.current_thread() is threading.main_thread())))
        self.assertFalse(future.result(timeout=1));self.assertEqual(seen, [])
        self.drain();self.assertEqual(seen, [(False, True)])
    def test_error_future_is_delivered_without_logging_error_text(self):
        seen=[]
        def work():raise ValueError('SECRET study text must never be logged')
        future=self.submit(work, lambda future:seen.append(type(future.exception())))
        with self.assertRaises(ValueError):future.result(timeout=1)
        self.drain();self.assertEqual(seen, [ValueError])
        raw=(Path(self.temp.name)/'cram_studio/generation-timings.jsonl').read_text()
        self.assertNotIn('SECRET', raw);self.assertEqual(json.loads(raw)['status'], 'error')
    def test_profile_close_cancels_queued_work_and_suppresses_old_callbacks(self):
        release=threading.Event();entered=[threading.Event() for _ in range(3)];seen=[]
        try:
            for event in entered:
                self.submit(lambda event=event:(event.set(),release.wait(2)),lambda future:seen.append('old'))
            self.assertTrue(all(event.wait(1) for event in entered))
            pending=self.submit(lambda:seen.append('queued work'),lambda future:seen.append('queued callback'))
            n.close_network();self.assertTrue(pending.cancelled());self.assertEqual(seen, [])
        finally:release.set()
        self.drain();self.assertEqual(seen, [])
    def test_diagnostics_failure_does_not_fail_generation(self):
        with patch.object(Path, 'open', side_effect=PermissionError('denied')):
            future=self.submit(lambda:'valid choices',lambda future:None)
            self.assertEqual(future.result(timeout=1),'valid choices');self.drain()
    def test_http_decode_and_save_timings_exclude_key_and_study_text(self):
        def opener(request, timeout):
            self.assertEqual(timeout,35)
            reply={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'sets':[
                {'id':'entry','answer_aliases':[],'wrong':['London','Tokyo','Berlin']} ]})}]}}]}
            class Response:
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def read(self,limit):return json.dumps(reply).encode()
            return Response()
        class Store:
            def put(self,values):self.values=values
        client=g.Gemini('secret-key','test-model',opener=opener);store=Store()
        work=lambda:g.generate_batches(client,[{'id':'entry','clue':'SECRET QUESTION capital of France?','answer':'Paris','blank':1}],
            store,threading.Event(),lambda *args:None)
        future=self.submit(work,lambda future:None)
        self.assertEqual(future.result(timeout=1),1);self.drain()
        raw=(Path(self.temp.name)/'cram_studio/generation-timings.jsonl').read_text()
        self.assertNotIn('secret-key',raw);self.assertNotIn('SECRET QUESTION',raw);self.assertNotIn('Paris',raw)
        data=json.loads(raw);self.assertEqual(data['status'],'ok')
        self.assertEqual({name:phase['count'] for name,phase in data['phases'].items()},
                         {'http':1,'decode':1,'cache_save':1})
    def test_timing_log_rotates_at_bounded_size(self):
        worker=n.NetworkJobs(self.mw.taskman,self.temp.name);self.workers.append(worker)
        worker.path.parent.mkdir(parents=True,exist_ok=True);worker.path.write_text('x'*65537)
        worker._write_timing({'queued_ms':0,'work_ms':1,'status':'ok','phases':{}})
        self.assertLess(worker.path.stat().st_size,1000)
        self.assertEqual(worker.path.with_suffix('.previous.jsonl').stat().st_size,65537)


if __name__ == '__main__':unittest.main()
