"""xAI API contract, saved-state migration and review boundaries; no real keys."""
import copy
from concurrent.futures import Future
import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from test_core import c, g, s, FakeResponse

a=importlib.import_module('cram_studio.ai')
n=importlib.import_module('cram_studio.network_jobs')


def response(sets,status='completed'):
    return {'status':status,'output':[{'type':'message','role':'assistant','status':'completed',
        'content':[{'type':'output_text','text':json.dumps({'sets':sets})}]}]}


class GrokTests(unittest.TestCase):
    def test_routing_and_model_namespaces_preserve_existing_provider_ids(self):
        for provider,model,cls in [('gemini','gemini-test',g.Gemini),('groq','openai/gpt-oss-20b',a.Groq),('grok','grok-4.7',a.Grok)]:
            token=a.model_token(provider,model)
            self.assertEqual(a.provider_for(token),provider);self.assertEqual(a.model_id(token),model)
            self.assertIsInstance(a.client('fixture-key',token),cls)
        self.assertEqual(a.model_token('gemini','gemini-test'),'gemini-test')
        for provider in a.PROVIDERS:
            for raw in ('grok:grok-4.7','groq:openai/gpt-oss-20b'):
                with self.assertRaises(g.AIError):a.model_token(provider,raw)

    def test_xai_responses_contract_auth_schema_and_shared_prompt(self):
        calls=[]
        def opener(req,timeout):
            calls.append(req.full_url);body=json.loads(req.data)
            self.assertEqual(req.full_url,'https://api.x.ai/v1/responses')
            self.assertEqual(req.get_header('Authorization'),'Bearer xai-fixture-secret')
            self.assertIsNone(req.get_header('X-goog-api-key'))
            self.assertNotIn('xai-fixture-secret',req.full_url+req.data.decode())
            self.assertEqual(timeout,35);self.assertEqual(body['model'],'grok-4.7')
            self.assertFalse(body['store']);self.assertFalse(body['stream'])
            self.assertEqual(body['max_output_tokens'],8192)
            self.assertNotIn('tools',body);self.assertNotIn('previous_response_id',body)
            self.assertNotIn('max_completion_tokens',body);self.assertNotIn('reasoning_effort',body)
            fmt=body['text']['format'];self.assertEqual(fmt['type'],'json_schema');self.assertTrue(fmt['strict'])
            schema=fmt['schema'];self.assertFalse(schema['additionalProperties'])
            self.assertEqual(schema['properties']['sets']['items']['properties']['id']['enum'],['a'])
            self.assertIn('question context AND the supplied correct answer',body['input'][1]['content'])
            result=response([{'id':'a','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}])
            # Only message output text is parsed; reasoning is never an answer.
            result['output'].insert(0,{'type':'reasoning','summary':[{'text':'not JSON'}]})
            return FakeResponse(result)
        client=a.client('xai-fixture-secret','grok:grok-4.7',opener)
        self.assertEqual(client.generate([{'id':'a','clue':'Capital of France?','answer':'Paris'}])['a'],['Lyon','Nice','Bordeaux'])
        self.assertEqual(len(calls),1)

    def test_refusal_incomplete_unknown_and_non_json_outputs_rejected(self):
        valid=response([{'id':'a','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}])
        bad=[]
        for status in ('incomplete','in_progress','failed','cancelled'):
            item=copy.deepcopy(valid);item['status']=status;bad.append(item)
        item=copy.deepcopy(valid);item['output'][0]['content']=[{'type':'refusal','refusal':'no'}];bad.append(item)
        item=copy.deepcopy(valid);item['output'][0]['status']='incomplete';bad.append(item)
        item=copy.deepcopy(valid);item['output'][0]['content'][0]['text']='bad JSON';bad.append(item)
        item=copy.deepcopy(valid);item['output']=[{'type':'function_call'}];bad.append(item)
        item=copy.deepcopy(valid);item['error']={'message':'private information'};bad.append(item)
        bad.extend([{},None,{'status':'completed','output':[]}])
        for value in bad:
            with self.subTest(value=value),self.assertRaises(g.AIError):
                a.Grok('fixture','grok-4.7',lambda *_ ,**kw:FakeResponse(value)).generate([{'id':'a','answer':'Paris'}])

    def test_grok_rejects_synonyms_and_preserves_writing_enumeration_spans(self):
        row={'id':'a','answer_aliases':['equivalence partitioning'],
             'wrong':['equivalence partitioning','Boundary value analysis','Decision table testing']}
        client=a.Grok('fixture','grok-4.7',lambda *_ ,**kw:FakeResponse(response([row])))
        with self.assertRaises(g.AIError):client.generate([{'id':'a','answer':'partition testing'}])
        text='The fruits are banana, mango, and lemon.'
        row={'id':'a','kind':'list','items':['banana','mango','lemon'],'connectors':['The fruits are ', ', ', ', and ', '.']}
        out=client.group_answers([{'id':'a','question':'Name the fruits.','text':text}])
        self.assertEqual([text[start:end] for start,end in out['a']['spans']],row['items'])

    def test_models_refresh_filters_media_and_uses_xai_origin(self):
        calls=[]
        def opener(req,timeout):
            calls.append(req.full_url)
            return FakeResponse({'data':[{'id':'grok-4.7'},{'id':'grok-text-other'},
                {'id':'grok-imagine-image-2.0'},{'id':'grok-imagine-video-1.5'},
                {'id':'grok-voice'},{'id':'grok-removed','active':False}]})
        self.assertEqual(a.Grok('fixture','grok-4.7',opener).models(),['grok-4.7','grok-text-other'])
        self.assertEqual(calls,['https://api.x.ai/v1/models'])

    def test_errors_explain_xai_credits_or_console_without_secrets_or_retry(self):
        for code in (400,401,402,403,404,422,429,500):
            calls=[]
            def fail(req,timeout):
                calls.append(req.full_url);raise urllib.error.HTTPError(req.full_url,code,'xai-fixture-secret',None,None)
            with self.subTest(code=code),self.assertRaises(g.AIError) as caught:
                a.Grok('xai-fixture-secret','grok-4.7',fail).test()
            message=str(caught.exception);self.assertNotIn('xai-fixture-secret',message)
            self.assertIn('Grok',message);self.assertEqual(caught.exception.status_code,code);self.assertEqual(len(calls),1)
            if code==402:self.assertIn('credits',message)
            if code in (401,402,403):self.assertIn('console.x.ai',message)

    def test_three_provider_keys_models_cache_and_forget_are_independent(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            store=s.Store(folder);store.data['model']='gemini-legacy';store.set_key('google-fixture')
            store.select_provider('groq','openai/gpt-oss-20b');store.set_key('groq-fixture')
            store.select_provider('grok','grok-4.7');self.assertEqual(store.get_key(),'');store.set_key('xai-fixture')
            store.save();reopened=s.Store(folder)
            self.assertEqual(reopened.provider(),'grok');self.assertEqual(reopened.selected_model('gemini'),'gemini-legacy')
            self.assertEqual(reopened.selected_model('groq'),'openai/gpt-oss-20b')
            self.assertEqual(store.get_model_key('gemini-legacy'),'google-fixture')
            self.assertEqual(store.get_model_key('groq:openai/gpt-oss-20b'),'groq-fixture')
            self.assertEqual(store.get_model_key('grok:grok-4.7'),'xai-fixture')
            store.forget_key('grok');self.assertEqual(store.get_key(),'')
            self.assertEqual(store.get_key('groq'),'groq-fixture');self.assertEqual(store.get_key('gemini'),'google-fixture')
            for secret in ('google-fixture','groq-fixture','xai-fixture'):
                self.assertNotIn(secret,(store.path/'practice.json').read_text())
            q={'clue':'Clue','slots':[{'answer':'Answer','number':1}]}
            keys={c.cache_key(q,q['slots'][0],a.model_token(provider,'same-id')) for provider in a.PROVIDERS}
            self.assertEqual(len(keys),3)

    def test_xai_environment_and_windows_cipher_file_are_separate(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'GEMINI_API_KEY':'google-env','GROQ_API_KEY':'groq-env','XAI_API_KEY':'xai-env'},clear=True):
            store=s.Store(folder);store.select_provider('grok','grok-4.7');self.assertEqual(store.get_key(),'xai-env')
            def protected(data,protect):return b'encrypted:'+data if protect else data.removeprefix(b'encrypted:')
            with patch.object(s.os,'name','nt'),patch.object(s,'dpapi',side_effect=protected):
                for provider in a.PROVIDERS:store.set_key(provider+'-fixture',True,provider)
                self.assertTrue((store.path/'key-grok.dpapi').exists())
                self.assertTrue((store.path/'key-groq.dpapi').exists());self.assertTrue((store.path/'key.dpapi').exists())
                store.session_key='';store.session_keys.clear()
                with patch.dict(os.environ,{},clear=True):
                    self.assertEqual(store.get_key('grok'),'grok-fixture')
                    self.assertEqual(store.get_key('groq'),'groq-fixture')
                    self.assertEqual(store.get_key('gemini'),'gemini-fixture')
                store.forget_key('grok');self.assertFalse((store.path/'key-grok.dpapi').exists())
                self.assertTrue((store.path/'key-groq.dpapi').exists());self.assertTrue((store.path/'key.dpapi').exists())

    def test_native_grok_generation_has_no_reveal_rating_or_scheduler_access(self):
        from test_live_review import Environment
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            env=Environment(folder,filtered=True,resched=False)
            env.live.store.select_provider('grok','grok-4.7');env.live.store.set_key('xai-fixture')
            env.live.begin('exam',False);env.packet();calls=[]
            def request(client,path,body):
                calls.append((client.key,path,body['model']))
                jobs=json.loads(body['input'][1]['content'].split('DATA:\n',1)[1])
                return response([{'id':job['id'],'answer_aliases':[],'wrong':['Alternative A','Alternative B','Alternative C']} for job in jobs])
            with patch.object(a.Grok,'request',request):
                env.live.generate();work,done=env.background.pop();future=Future();future.set_result(work());done(future)
            self.assertEqual(calls,[('xai-fixture','responses','grok-4.7')])
            self.assertTrue(env.live.current['question']['ready']);self.assertEqual(env.calls,['study'])
            self.assertEqual(env.mw.reviewer.state,'question');self.assertFalse(env.col.deck['resched'])
            env.live.close();s.clear_profile_stores()

    def test_main_grok_generation_uses_shared_pipeline_and_profile_cache_only(self):
        import types
        from test_progress import Controller,card,config
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            fixture=Controller(folder);owner=fixture.owner;owner.questions=[card('a','exam')]
            owner.config=config(mode='exam');owner.questions[0]['ready']=False
            owner.store.select_provider('grok','grok-4.7');owner.store.set_key('xai-fixture')
            tasks=[];calls=[]
            owner.mw.taskman=types.SimpleNamespace(run_on_main=lambda fn:fn(),
                run_in_background=lambda work,done,**kwargs:tasks.append((work,done)))
            def opener(req,timeout):
                calls.append(req.full_url);body=json.loads(req.data)
                jobs=json.loads(body['input'][1]['content'].split('DATA:\n',1)[1])
                return FakeResponse(response([{'id':job['id'],'answer_aliases':[],
                    'wrong':['Alternative A','Alternative B','Alternative C']} for job in jobs]))
            namespace=owner.generate.__func__.__globals__
            namespace.update(Gemini=lambda key,model:a.client(key,model,opener),
                generate_batches=g.generate_batches,cache_key=c.cache_key)
            owner.generate();work,done=tasks.pop();future=Future();future.set_result(work());done(future)
            self.assertTrue(owner.questions[0]['ready']);self.assertTrue(owner.store.cache())
            self.assertEqual(calls,['https://api.x.ai/v1/responses'])
            self.assertFalse(hasattr(owner.mw,'col'),'Independent generation does not need a collection or scheduler')

    def test_three_provider_transports_are_distinct_and_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            owner=n.NetworkJobs(type('Taskman',(),{})(),folder)
            try:
                origins=['https://api.x.ai','https://api.groq.com','https://generativelanguage.googleapis.com']
                transports=[owner.transport(origin) for origin in origins]
                self.assertEqual(len({id(t) for t in transports}),3)
                self.assertIs(transports[0],owner.transport(origins[0]))
            finally:owner.close();owner.pool.shutdown(wait=True);owner.api_pool.shutdown(wait=True)


if __name__=='__main__':unittest.main()
