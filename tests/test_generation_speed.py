"""Local HTTP/1.1 and real storage checks. Never calls Google or uses a real key."""
import importlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import sys
import tempfile
import threading
import types
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
g=importlib.import_module('cram_studio.gemini')
n=importlib.import_module('cram_studio.network_jobs')
t=importlib.import_module('cram_studio.gemini_transport')
s=importlib.import_module('cram_studio.storage')
c=importlib.import_module('cram_studio.content')


class LocalHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state={'connections':0,'requests':[]}
        class Handler(BaseHTTPRequestHandler):
            protocol_version='HTTP/1.1'
            def setup(self):
                super().setup();self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                cls.state['connections']+=1
            def log_message(self,*args):pass
            def handle_one_request(self):
                try:super().handle_one_request()
                except ConnectionResetError:self.close_connection=True
            def do_GET(self):self.do_POST()
            def do_POST(self):
                raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
                cls.state['requests'].append({'path':self.path,'body':raw,'headers':dict(self.headers)})
                code=429 if self.path.endswith('quota') else 302 if self.path.endswith('redirect') else 200
                body=(b'x'*2_000_005) if self.path.endswith('huge') else json.dumps({'ok':True}).encode()
                self.send_response(code);self.send_header('Content-Length',str(len(body)))
                self.send_header('Content-Type','application/json');self.send_header('Set-Cookie','should_not_persist=yes')
                if code==302:self.send_header('Location','http://127.0.0.1:1/not-allowed')
                self.end_headers()
                try:self.wfile.write(body)
                except (BrokenPipeError,ConnectionResetError):pass
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.server.daemon_threads=True
        cls.origin='http://127.0.0.1:'+str(cls.server.server_port)
        cls.thread=threading.Thread(target=lambda:cls.server.serve_forever(poll_interval=.02),daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(1)
    def setUp(self):
        self.start_connections=self.state['connections'];self.start_requests=len(self.state['requests'])
        self.http=t.PooledHTTP(self.origin);self.addCleanup(self.http.close)
    def request(self,path='test',key='fake-key',payload=None):
        client=g.Gemini(key,'fake-model',opener=self.http.open)
        with patch.object(g,'BASE',self.origin+'/v1beta/'):
            return client.request(path,payload)
    def test_reuses_one_connection_across_new_clients_without_persisting_key_or_cookie(self):
        for i in range(5):self.assertEqual(self.request(key='fake-'+str(i),payload={'n':i}),{'ok':True})
        self.assertEqual(self.state['connections']-self.start_connections,1)
        rows=self.state['requests'][self.start_requests:]
        self.assertEqual([row['headers']['X-goog-api-key'] for row in rows],['fake-'+str(i) for i in range(5)])
        self.assertTrue(all('Cookie' not in row['headers'] and 'Authorization' not in row['headers'] for row in rows))
        self.assertFalse(self.http.session.cookies)
    def test_redirect_and_rate_limit_never_retry_or_forward_request(self):
        for path in ['quota','redirect']:
            before=len(self.state['requests'])
            with self.assertRaises(g.AIError) as caught:self.request(path)
            self.assertNotIn('fake-key',str(caught.exception));self.assertEqual(len(self.state['requests']),before+1)
    def test_stream_read_limit_and_recovery(self):
        with self.assertRaises(g.AIError) as caught:self.request('huge')
        self.assertIn('too large',str(caught.exception))
        self.assertEqual(self.request(),{'ok':True})
    def test_origin_is_checked_before_network(self):
        before=len(self.state['requests'])
        with self.assertRaises(urllib.error.URLError):
            self.http.open(urllib.request.Request('http://127.0.0.1:1/wrong',headers={'x-goog-api-key':'fake-key'}))
        self.assertEqual(len(self.state['requests']),before)
    def test_worker_context_reuses_connection_across_clients(self):
        original=t.PooledHTTP
        with tempfile.TemporaryDirectory() as folder:
            callbacks=[];worker=n.NetworkJobs(types.SimpleNamespace(run_on_main=callbacks.append),folder)
            def work():
                for _ in range(4):self.assertEqual(g.Gemini('fake-key','fake-model').request('test'),{'ok':True})
            try:
                with patch.object(t,'PooledHTTP',lambda origin=None:original(self.origin)),patch.object(g,'BASE',self.origin+'/v1beta/'):
                    worker.submit(work,lambda f:None).result(timeout=2)
                    worker.pool.shutdown(wait=True)
                self.assertEqual(self.state['connections']-self.start_connections,1)
            finally:
                worker.close();worker.pool.shutdown(wait=True)


class BatchAndCacheTests(unittest.TestCase):
    def batches(self,answers,first=None,cancel_after=None):
        batches=[];saved={};event=threading.Event();progress=[]
        class Client:
            def generate(self,jobs):
                batches.append([j['id'] for j in jobs]);return {j['id']:['A','B','C'] for j in jobs}
        class Store:
            def put(self,values):saved.update(values)
        def report(done,total):
            progress.append(done)
            if cancel_after and done>=cancel_after:event.set()
        jobs=[{'id':str(i),'answer':answer} for i,answer in enumerate(answers)]
        try:g.generate_batches(Client(),jobs,Store(),event,report,first_size=first,batch_size=10)
        except g.Cancelled:pass
        return batches,saved,progress
    def test_bulk_25_short_answers_uses_three_requests_and_saves_all(self):
        batches,saved,progress=self.batches(['Term']*25)
        self.assertEqual(list(map(len,batches)),[10,10,5]);self.assertEqual(len(saved),25);self.assertEqual(progress,[10,20,25])
    def test_first_question_stays_fast_and_cancellation_retains_completed_work(self):
        batches,saved,_=self.batches(['Term']*25,first=1)
        self.assertEqual(list(map(len,batches)),[1,10,10,4]);self.assertEqual(len(saved),25)
        batches,saved,progress=self.batches(['Term']*25,cancel_after=10)
        self.assertEqual(len(batches),1);self.assertEqual(len(saved),10);self.assertEqual(progress,[10])
    def test_long_answers_reduce_batch_size_without_truncating(self):
        batches,saved,_=self.batches(['x'*1300]*4)
        self.assertEqual(list(map(len,batches)),[1,1,1,1]);self.assertEqual(len(saved),4)
    def test_active_card_cache_does_not_copy_unrelated_choices_or_writing_plans(self):
        with tempfile.TemporaryDirectory() as folder:
            store=s.Store(folder);q={'clue':'Question','slots':[{'answer':'Term','number':1}]}
            key=c.cache_key(q,q['slots'][0],'model')
            class Unrelated:
                def __deepcopy__(self,memo):raise AssertionError('Unrelated cache was copied')
            store.data['cache']={str(i):Unrelated() for i in range(10000)}
            store.data['cache'][key]=['A','B','C']
            subset=store.choice_cache([q],'model');self.assertEqual(subset,{key:['A','B','C']})
            subset[key].append('D');self.assertEqual(store.data['cache'][key],['A','B','C'])


if __name__=='__main__':unittest.main()
