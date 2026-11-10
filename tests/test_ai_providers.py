"""Short provider contracts, migration and key-isolation checks. No live API keys."""
import importlib
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
from test_core import c, g, s, FakeResponse

a=importlib.import_module('cram_studio.ai')
n=importlib.import_module('cram_studio.network_jobs')
t=importlib.import_module('cram_studio.gemini_transport')


def reply(sets,finish='stop',refusal=None):
    # Transport fixtures include the new single-response Groq contrast fields.
    sets=[contrast_row(row) for row in sets]
    return FakeResponse({'choices':[{'finish_reason':finish,'message':{
        'content':json.dumps({'sets':sets}), 'refusal':refusal}}]})

def contrast_row(row):
    row=dict(row)
    if 'wrong' in row:
        row.setdefault('answer_concept','The supplied answer concept')
        row.setdefault('wrong_concepts',row['wrong'])
        row.setdefault('wrong_reasons',['A different fact for this synthetic test']*3)
    return row


class ProviderTests(unittest.TestCase):
    def test_groq_contract_and_shared_prompt_validator(self):
        calls=[]
        def opener(req,timeout):
            calls.append(req);body=json.loads(req.data)
            self.assertEqual(req.full_url,'https://api.groq.com/openai/v1/chat/completions')
            self.assertEqual(req.get_header('Authorization'),'Bearer groq-secret-fixture')
            self.assertIsNone(req.get_header('X-goog-api-key'))
            self.assertNotIn('groq-secret-fixture',req.full_url+req.data.decode())
            self.assertEqual(timeout,35);self.assertEqual(body['model'],'openai/gpt-oss-20b')
            self.assertNotIn('generationConfig',body);self.assertEqual(body['reasoning_effort'],'low')
            self.assertFalse(body['stream'])
            fmt=body['response_format'];self.assertEqual(fmt['type'],'json_schema')
            schema=fmt['json_schema']['schema'];self.assertTrue(fmt['json_schema']['strict'])
            self.assertEqual(schema['type'],'object');self.assertFalse(schema['additionalProperties'])
            item=schema['properties']['sets']['items'];self.assertFalse(item['additionalProperties'])
            self.assertEqual(item['properties']['id']['enum'],['target'])
            prompt=body['messages'][1]['content']
            self.assertIn('question context AND the supplied correct answer',prompt)
            self.assertIn('REAL SIBLING TYPES',prompt);self.assertIn('answer_aliases',prompt)
            return reply([{'id':'target','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}])
        client=a.client('groq-secret-fixture','groq:openai/gpt-oss-20b',opener)
        self.assertIsInstance(client,a.Groq)
        self.assertEqual(client.generate([{'id':'target','clue':'Capital of France?','answer':'Paris'}]),
                         {'target':['Lyon','Nice','Bordeaux']})
        self.assertEqual(len(calls),1)

    def test_other_groq_text_models_use_json_mode_with_explicit_schema(self):
        def opener(req,timeout):
            body=json.loads(req.data);self.assertEqual(body['response_format'],{'type':'json_object'})
            self.assertNotIn('reasoning_effort',body)
            self.assertIn('JSON schema',body['messages'][0]['content'])
            return reply([{'id':'a','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}])
        self.assertEqual(a.Groq('key','llama-3.3-70b-versatile',opener).generate([{'id':'a','answer':'Paris'}])['a'][0],'Lyon')

    def test_aliases_and_wrong_counts_and_foreign_ids_rejected_for_groq(self):
        for row in [
            {'id':'a','answer_aliases':['equivalence partitioning'],'wrong':['equivalence partitioning','Boundary value analysis','Decision table testing']},
            {'id':'a','answer_aliases':[],'wrong':['Boundary value analysis']},
            {'id':'foreign','answer_aliases':[],'wrong':['A','B','C']},
        ]:
            with self.subTest(row=row),self.assertRaises(g.AIError):
                a.Groq('key','openai/gpt-oss-20b',lambda *_ ,**kw:reply([row])).generate([{'id':'a','answer':'partition testing'}])

    def test_writing_groups_preserve_original_formatting(self):
        source='The fruits are banana, mango, and lemon.'
        row={'id':'a','kind':'list','items':['banana','mango','lemon'],
             'connectors':['The fruits are ', ', ', ', and ', '.']}
        client=a.Groq('key','openai/gpt-oss-20b',lambda *_ ,**kw:reply([row]))
        out=client.group_answers([{'id':'a','question':'Name three fruits.','text':source}])
        self.assertEqual([source[start:end] for start,end in out['a']['spans']],row['items'])
        row['items'][0]='Bananas'
        with self.assertRaises(g.AIError):client.group_answers([{'id':'a','text':source}])

    def test_incomplete_refused_or_malformed_responses_never_save(self):
        for finish,refusal in [('length',None),('content_filter',None),('stop','Refused')]:
            with self.subTest(finish=finish),self.assertRaises(g.AIError):
                a.Groq('key','openai/gpt-oss-20b',lambda *_ ,**kw:reply([],finish,refusal)).generate([{'id':'a','answer':'Paris'}])
        with self.assertRaises(g.AIError):
            a.Groq('key','openai/gpt-oss-20b',lambda *_ ,**kw:FakeResponse({'choices':[]})).test()

    def test_groq_model_refresh_and_sensitive_errors(self):
        urls=[]
        def models(req,timeout):
            urls.append(req.full_url)
            return FakeResponse({'data':[{'id':'openai/gpt-oss-20b'}, {'id':'llama-3.3-70b-versatile'},
                {'id':'whisper-large-v3'},{'id':'canopylabs/orpheus-v1-english'},
                {'id':'removed','active':False}]})
        self.assertEqual(a.Groq('key','openai/gpt-oss-20b',models).models(),['llama-3.3-70b-versatile','openai/gpt-oss-20b'])
        self.assertEqual(urls,['https://api.groq.com/openai/v1/models'])
        for code in (400,401,403,404,422,429,500):
            calls=[]
            def fail(req,timeout):
                calls.append(1);raise urllib.error.HTTPError(req.full_url,code,'private-key',None,None)
            with self.subTest(code=code),self.assertRaises(g.AIError) as caught:a.Groq('private-key','model',fail).test()
            self.assertEqual(caught.exception.status_code,code)
            self.assertNotIn('private-key',str(caught.exception));self.assertIn('Groq',str(caught.exception))
            self.assertEqual(len(calls),1)

    def test_model_and_key_validation_cannot_inject_path_or_header(self):
        for value in ('../model','model?api_key=x','https://evil.test','model#x','a//b','a:b'):
            with self.subTest(value=value),self.assertRaises(g.AIError):a.Groq('key',value)
        for value in ('','bad key','bad\nheader','ñ'):
            with self.assertRaises(g.AIError):a.Groq(value,'openai/gpt-oss-20b')
        with self.assertRaises(g.AIError):a.model_token('gemini','groq:openai/gpt-oss-20b')
        with self.assertRaises(g.AIError):a.model_token('groq','groq:openai/gpt-oss-20b')
        self.assertEqual(a.model_token('gemini','models/gemini-test'),'gemini-test')

    def test_legacy_gemini_settings_keys_and_cache_remain_compatible(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            path=Path(folder)/'cram_studio';path.mkdir()
            (path/'practice.json').write_text(json.dumps({'version':1,'model':'gemini-my-model','cache':{'legacy':['A','B','C']},'history':[{'old':1}]}))
            store=s.Store(folder);store.set_key('gemini-key');self.assertEqual(store.provider(),'gemini')
            q={'clue':'Clue','slots':[{'answer':'Answer','number':1}]};slot=q['slots'][0]
            old=c.cache_key(q,slot,store.data['model']);store.put({old:['A','B','C']})
            store.select_provider('groq','openai/gpt-oss-20b');self.assertEqual(store.get_key(),'')
            store.set_key('groq-key');store.save()
            self.assertNotEqual(c.cache_key(q,slot,store.data['model']),old)
            self.assertEqual(store.get_key('gemini'),'gemini-key');self.assertEqual(store.get_key(),'groq-key')
            self.assertEqual(store.selected_model('gemini'),'gemini-my-model')
            store.select_provider('gemini',store.selected_model('gemini'))
            self.assertEqual(store.get_key(),'gemini-key');self.assertIn(old,store.choice_cache([q],store.data['model']))
            self.assertEqual(store.data['history'],[{'old':1}]);self.assertIn('legacy',store.cache())
            self.assertNotIn('groq-key',(path/'practice.json').read_text())

    def test_environment_and_forget_isolation(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'GEMINI_API_KEY':'google-env','GROQ_API_KEY':'groq-env'},clear=True):
            store=s.Store(folder);self.assertEqual(store.get_key(),'google-env')
            store.select_provider('groq','openai/gpt-oss-20b');self.assertEqual(store.get_key(),'groq-env')
            store.set_key('session-groq');store.set_key('session-google',provider='gemini')
            store.forget_key('groq');self.assertEqual(store.get_key(),'groq-env')
            self.assertEqual(store.get_key('gemini'),'session-google')
            # A paused deck plan may reference another provider than the active settings.
            self.assertEqual(store.get_model_key('gemini-old-model'),'session-google')
            self.assertEqual(store.get_model_key('groq:openai/gpt-oss-20b'),'groq-env')

    def test_native_groq_generation_does_not_reveal_rate_or_replace_queue(self):
        from concurrent.futures import Future
        from test_live_review import Environment
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            env=Environment(folder,filtered=True,resched=False)
            env.live.store.select_provider('groq','openai/gpt-oss-20b')
            env.live.store.set_key('groq-fixture');env.live.begin('exam',False);env.packet()
            requests=[]
            def request(client,path,body):
                requests.append((client.key,path,body['model']))
                jobs=json.loads(body['messages'][1]['content'].split('DATA:\n',1)[1])
                return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'sets':[
                    contrast_row({'id':job['id'],'answer_aliases':[],'wrong':['Alternative A','Alternative B','Alternative C']}) for job in jobs]})}}]}
            with patch.object(a.Groq,'request',request):
                env.live.generate();work,done=env.background.pop();future=Future();future.set_result(work());done(future)
            self.assertEqual(requests,[('groq-fixture','chat/completions','openai/gpt-oss-20b')])
            self.assertTrue(env.live.current['question']['ready']);self.assertEqual(env.calls,['study'])
            self.assertEqual(env.mw.reviewer.state,'question');self.assertFalse(env.col.deck['resched'])
            env.live.close();s.clear_profile_stores()

    def test_windows_key_files_are_distinct_and_no_plaintext_in_json(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True):
            store=s.Store(folder)
            def protected(data,protect):return b'protected:'+data if protect else data.removeprefix(b'protected:')
            with patch.object(s.os,'name','nt'),patch.object(s,'dpapi',side_effect=protected):
                store.set_key('google',True,provider='gemini');store.set_key('groq',True,provider='groq')
                self.assertTrue((store.path/'key.dpapi').exists());self.assertTrue((store.path/'key-groq.dpapi').exists())
                store.session_key='';store.session_keys.clear()
                self.assertEqual(store.get_key('gemini'),'google');self.assertEqual(store.get_key('groq'),'groq')
                store.forget_key('groq');self.assertTrue((store.path/'key.dpapi').exists())
                self.assertFalse((store.path/'key-groq.dpapi').exists())

    def test_network_pools_are_separate_per_provider_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            owner=n.NetworkJobs(type('Taskman',(),{})(),folder)
            try:
                one=owner.transport('https://api.groq.com');two=owner.transport('https://generativelanguage.googleapis.com')
                self.assertIsNot(one,two);self.assertIs(one,owner.transport('https://api.groq.com'))
                with self.assertRaises(urllib.error.URLError):one.open(urllib.request.Request('https://generativelanguage.googleapis.com/test'))
                with self.assertRaises(urllib.error.URLError):two.open(urllib.request.Request('https://api.groq.com/test'))
            finally:owner.close();owner.pool.shutdown(wait=True);owner.api_pool.shutdown(wait=True)


if __name__=='__main__':unittest.main()
