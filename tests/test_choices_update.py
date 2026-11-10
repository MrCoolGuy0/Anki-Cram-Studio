"""Question-aware generation, multiline choices and native forced regeneration."""
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from concurrent.futures import Future

if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(Path(__file__).resolve().parents[1]/'cram_studio')];sys.modules['cram_studio']=package
c=importlib.import_module('cram_studio.content')
g=importlib.import_module('cram_studio.gemini')
l=importlib.import_module('cram_studio.live_review')
s=importlib.import_module('cram_studio.storage')

class ChoiceLayoutTests(unittest.TestCase):
    def test_numbered_source_forms_preserve_lines_and_nested_list_indents(self):
        for source in ('1. banana\n2. mango','1. banana<br>2. mango','<div>1. banana</div><div>2. mango</div>','<ol><li>banana</li><li>mango</li></ol>'):
            with self.subTest(source=source):self.assertEqual(c.choice_text(source),'1. banana\n2. mango')
        self.assertEqual(c.choice_text('<ol start="3"><li>banana</li><li value="7">mango</li></ol>'),'3. banana\n7. mango')
        self.assertEqual(c.choice_text('<ul><li>fruits<ol><li>banana</li><li>mango</li></ol></li></ul>'),'• fruits\n  1. banana\n  2. mango')
        self.assertEqual(c.choice_text('one<script>bad()</script><span hidden>secret</span><br>two'),'one\ntwo')
    def test_basic_and_cloze_correct_choices_keep_entire_list(self):
        model={'id':1,'name':'Basic','flds':[{'name':'Front'},{'name':'Back'}]}
        rows=[(1,1,1,0,1,'Name these two fruit examples in their original order\x1f<ol><li>banana</li><li>mango</li></ol>')]
        q=c.compile_questions(rows,{1:model},{1:'Deck'},{'mode':'exam','shuffle':False},{'1':{'answer':'Back'}})['questions'][0]
        clue,slots=c.cloze_question('Fruit: {{c1::<div>1. banana</div><div>2. mango</div>}} and {{c2::vegetables}}',{1})
        self.assertEqual(q['slots'][0]['answer'],'1. banana\n2. mango');self.assertEqual(slots[0]['answer'],'1. banana\n2. mango')
        self.assertIn('vegetables',clue);self.assertNotIn('banana',clue)
        jobs,_=c.prepare_choices([q],{},'model');cache={jobs[0]['id']:['1. apple\n2. pear','1. orange\n2. peach','1. grape\n2. lemon']}
        c.attach_choices([q],cache,'model');slot=q['slots'][0]
        self.assertEqual(slot['choices'][slot['correct']],'1. banana\n2. mango');self.assertTrue(all('\n2.' in v for v in slot['choices']))
    def test_distractor_validation_keeps_layout_and_rejects_duplicate_variants(self):
        wrong=['<ol><li>apple</li><li>pear</li></ol>','1. grape<br>2. lemon','1. peach\n2. orange']
        self.assertEqual(c.valid_distractors('1. banana\n2. mango',wrong)[0],'1. apple\n2. pear')
        with self.assertRaises(ValueError):c.valid_distractors('1. banana\n2. mango',['1. banana 2. mango','Other','Third'])
    def test_generation_uses_complete_clue_other_blanks_and_new_cache_revision(self):
        clue,slots=c.cloze_question('<b>Living organization</b><div>{{c1::cells}} form {{c1::tissues}}.</div>',{1})
        q={'mode':'exam','clue':clue,'slots':slots};jobs,_=c.prepare_choices([q],{},'model')
        self.assertEqual(jobs[0]['clue'],'Living organization\n(1) _____________ form (2) _____________.')
        self.assertEqual(jobs[0]['other_blanks'],[{'blank':2,'answer':'tissues'}])
        original=c.cache_key(q,slots[0],'model');slots[1]['answer']='organs';self.assertNotEqual(original,c.cache_key(q,slots[0],'model'))
        revision=c.PROMPT_VERSION
        try:c.PROMPT_VERSION=1;old_key=c.cache_key(q,slots[0],'model')
        finally:c.PROMPT_VERSION=revision
        pending,_=c.prepare_choices([q],{old_key:['A','B','C']},'model');self.assertEqual(len(pending),2)
    def test_each_ai_stem_targets_one_blank_with_correct_neighbor_context(self):
        clue,slots=c.cloze_question('Sex hormones ({{c1::estrogen}} and {{c1::testosterone}}) affect growth in puberty.',{1})
        question={'mode':'exam','clue':clue,'slots':slots};original_clue=question['clue']
        jobs,_=c.prepare_choices([question],{},'model')
        self.assertEqual(jobs[0]['question_for_this_blank'],'Sex hormones ([TARGET BLANK 1] and testosterone) affect growth in puberty.')
        self.assertEqual(jobs[1]['question_for_this_blank'],'Sex hormones (estrogen and [TARGET BLANK 2]) affect growth in puberty.')
        self.assertEqual(question['clue'],original_clue,'AI-only context must not reveal neighbors in the displayed question')
        self.assertEqual([s['answer'] for s in slots],['estrogen','testosterone'])
        self.assertEqual([job['blank'] for job in jobs],[1,2])
        single={'mode':'exam','clue':'What does this term mean?','slots':[{'number':1,'answer':'Meaning'}]}
        self.assertEqual(c.prepare_choices([single],{},'model')[0][0]['question_for_this_blank'],single['clue'])
    def test_new_difficulty_policy_does_not_reuse_v2_sets_or_erase_them(self):
        clue,slots=c.cloze_question('{{c1::cells}} form {{c1::tissues}}.',{1})
        question={'mode':'exam','clue':clue,'slots':slots};revision=c.PROMPT_VERSION
        try:
            c.PROMPT_VERSION=3
            old={c.cache_key(question,slot,'model'):['Old A','Old B','Old C'] for slot in slots}
        finally:c.PROMPT_VERSION=revision
        before=copy.deepcopy(old);jobs,ready=c.prepare_choices([question],old,'model')
        self.assertEqual((len(jobs),ready),(2,0));self.assertEqual(old,before)
        self.assertFalse(set(job['id'] for job in jobs)&set(old))
        current={job['id']:['New A','New B','New C'] for job in jobs}
        self.assertEqual(c.prepare_choices([question],current,'model'),([],2),'new policy sets remain cached on repeat visits')
    def test_gemini_contract_contains_question_context_and_preserves_multiline_output(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'sets':[{'id':'a','answer_aliases':[],'wrong':['1. apple\n2. pear','1. grape\n2. lemon','1. peach\n2. orange']}]})}]}}]}).encode()
        def opener(request,timeout):
            body=json.loads(request.data);prompt=body['contents'][0]['parts'][0]['text']
            instruction,data=prompt.split('DATA:\n',1)
            self.assertIn('BOTH that full question context AND',instruction);self.assertIn('clearly wrong',instruction)
            self.assertIn('NARROW answer category',instruction);self.assertIn('category outliers',instruction)
            self.assertIn('question_for_this_blank',instruction);self.assertIn('one defensible correct answer',instruction)
            self.assertEqual(json.loads(data),jobs);self.assertNotIn('secret-key',request.data.decode())
            return Response()
        jobs=[{'id':'a','clue':'Which two fruits match the pictured examples?','answer':'1. banana\n2. mango','blank':1,'other_blanks':[]}]
        result=g.Gemini('secret-key','test-model',opener).generate(jobs)
        self.assertEqual(result['a'][0],'1. apple\n2. pear')

class ChoiceIdentityTests(unittest.TestCase):
    def test_reported_alias_is_rejected_in_both_directions_and_as_duplicate_wrong_options(self):
        for answer,alias in [('PARTITION TESTING','Equivalence partitioning'),('Equivalence partitioning','Partition-testing')]:
            with self.subTest(answer=answer),self.assertRaises(ValueError):
                c.valid_distractors(answer,[alias,'Boundary value analysis','Decision table testing'])
        with self.assertRaises(ValueError):
            c.valid_distractors('Boundary value analysis',['Partition testing','Equivalence partitioning','State transition testing'])
        real_peers=['Boundary value analysis','Decision table testing','State transition testing']
        self.assertEqual(c.valid_distractors('Partition testing',real_peers),real_peers)
        self.assertNotEqual(c.choice_identity('Equivalence partition'),c.choice_identity('Equivalence partitioning'))

    def test_model_declared_contextual_alias_excludes_differently_spelled_same_answer(self):
        with self.assertRaises(ValueError):
            c.valid_distractors('Central processing unit',['CPU','Memory','Disk'],['CPU'])
        # Aliases may repeat the answer itself; siblings are not silently merged.
        self.assertEqual(c.valid_distractors('First stage',['Second stage','Third stage','Fourth stage'],['First stage']),['Second stage','Third stage','Fourth stage'])
        for aliases in (None,'CPU',[12],[''],['x'*601],['alias']*13):
            with self.subTest(aliases=aliases),self.assertRaises(ValueError):
                c.valid_distractors('Answer',['One','Two','Three'],aliases)

    def test_known_alias_in_a_current_revision_cache_is_not_prepared_or_attached(self):
        q={'mode':'exam','clue':'Which method groups equivalent inputs?','slots':[{'answer':'Partition testing','number':1}]}
        key=c.cache_key(q,q['slots'][0],'model')
        bad={key:['Equivalence partitioning','Boundary value analysis','Decision table testing']}
        jobs,ready=c.prepare_choices([q],bad,'model')
        self.assertEqual((len(jobs),ready),(1,0))
        c.attach_choices([q],bad,'model',partial=True)
        self.assertFalse(q['ready']);self.assertNotIn('choices',q['slots'][0])

    def client(self,entries):
        calls=[]
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'sets':entries})}]}}]}).encode()
        def opener(req,timeout):calls.append(json.loads(req.data));return Response()
        return g.Gemini('test-secret','test-model',opener),calls

    def test_single_request_schema_requires_aliases_but_stores_only_three_option_strings(self):
        client,calls=self.client([{'id':'a','answer_aliases':['CPU'],'wrong':['RAM','SSD','GPU']}])
        out=client.generate([{'id':'a','clue':'Which component executes instructions?','answer':'Central processing unit'}])
        self.assertEqual(out,{'a':['RAM','SSD','GPU']});self.assertEqual(len(calls),1)
        schema=calls[0]['generationConfig']['responseSchema']['properties']['sets']['items']
        self.assertIn('answer_aliases',schema['required'])
        self.assertEqual(schema['properties']['wrong']['minItems'],3)
        self.assertEqual(schema['properties']['wrong']['maxItems'],3)
        prompt=calls[0]['contents'][0]['parts'][0]['text'].split('DATA:\n')[0]
        for instruction in ('REAL SIBLING TYPES','conditional, not mandatory','established terms','pseudo-terms','EXACTLY THREE','Related and wrong is an acceptable fallback','surrounding subject','equivalence partitioning'):
            self.assertIn(instruction,prompt)
        self.assertNotIn('return an empty wrong array',prompt)

    def test_ai_alias_metadata_and_known_alias_cannot_be_returned_as_wrong_choices(self):
        cases=[
            ('Central processing unit',{'id':'a','answer_aliases':['CPU'],'wrong':['cpu','RAM','SSD']}),
            ('Partition testing',{'id':'a','answer_aliases':[],'wrong':['Equivalence partitioning','Boundary value analysis','Decision table testing']}),
            ('Answer',{'id':'a','wrong':['One','Two','Three']}),
            ('Answer',{'id':'a','answer_aliases':'alias','wrong':['One','Two','Three']}),
        ]
        for answer,entry in cases:
            with self.subTest(answer=answer):
                client,calls=self.client([entry])
                with self.assertRaises(g.AIError):client.generate([{'id':'a','answer':answer}])
                self.assertEqual(len(calls),1,'validation does not silently retry or add an API pass')

    def test_incomplete_model_output_is_invalid_without_a_semantic_question_refusal(self):
        entries=[{'id':'a','answer_aliases':[],'wrong':['One','Two','Three']},
                 {'id':'b','answer_aliases':[],'wrong':[]}]
        client,calls=self.client(entries)
        with tempfile.TemporaryDirectory() as td:
            store=s.Store(td);store.put({'previous':['Existing A','Existing B','Existing C']})
            before=store.cache()
            with self.assertRaisesRegex(g.AIError,'Exactly three wrong choices are required') as caught:
                g.generate_batches(client,[{'id':'a','answer':'Answer A'},{'id':'b','answer':'Answer B'}],store,threading.Event(),lambda *_:None)
            self.assertNotIn('revise the clue',str(caught.exception))
            self.assertNotIn('could not find three',str(caught.exception))
            self.assertEqual(store.cache(),before,'an unsafe batch never partially overwrites previous choices')
            self.assertEqual(len(calls),1)

class NativeRegenerateTests(unittest.TestCase):
    def setUp(self):
        from test_live_review import Environment
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.addCleanup(s.clear_profile_stores)
        self.e=Environment(self.tmp.name);self.e.live.store.set_key('test-key');self.e.live.begin('exam');self.e.packet();self.cache_current()
    def cache_current(self):
        q=self.e.live.current['question'];jobs,_=c.prepare_choices([q],{},self.e.live.store.data['model'])
        self.e.live.store.put({job['id']:['Old A','Old B','Old C'] for job in jobs});c.attach_choices([q],self.e.live.store.cache(),self.e.live.store.data['model'])
        return q
    def client(self,fail=False):
        seen=[]
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):
                seen.extend(jobs)
                if fail:raise g.AIError('Quota reached')
                return {job['id']:['New A','New B','New C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original);return seen
    def finish(self,index=0,callback=True):
        work,done=self.e.background[index];future=Future()
        try:future.set_result(work())
        except Exception as error:future.set_exception(error)
        if callback:done(future)
        return future
    def test_force_regenerates_cached_current_card_without_rating_or_navigation(self):
        e=self.e;seen=self.client();before=copy.deepcopy(e.live.current)
        e.message('generate');self.assertEqual(e.background,[],'ordinary ready uses cache')
        e.message('regenerate');self.assertTrue(e.live.current['generating']);self.assertEqual(e.live.current['question']['slots'][0]['choices'],before['question']['slots'][0]['choices'])
        self.finish();self.assertEqual(len(seen),1);self.assertEqual(e.live.current['choices_revision'],1)
        self.assertEqual(e.live.current['cid'],before['cid']);self.assertEqual(e.live.current['epoch'],before['epoch'])
        self.assertEqual(e.live.current['question']['slots'][0]['wrong'],['New A','New B','New C']);self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.data['history'],[])
        e.packet('reviewAnswer');e.message('regenerate');self.assertEqual(len(e.background),1,'answered cards cannot regenerate')
    def test_failed_regeneration_keeps_usable_existing_choices_and_cache(self):
        e=self.e;self.client(fail=True);before=copy.deepcopy(e.live.current['question']);cached=e.live.store.cache()
        e.message('regenerate');self.finish();self.assertEqual(e.live.current['question'],before);self.assertEqual(e.live.store.cache(),cached)
        self.assertEqual(e.live.current['error'],'Quota reached');self.assertFalse(e.live.current['generating']);self.assertEqual(e.calls,['study'])
    def test_regeneration_does_not_overwrite_an_answer_revealed_while_request_finishes(self):
        e=self.e;self.client();before=copy.deepcopy(e.live.current['question']);e.message('regenerate');future=self.finish(callback=False)
        e.packet('reviewAnswer');e.background[0][1](future)
        self.assertEqual(e.live.current['side'],'answer');self.assertEqual(e.live.current['question'],before);self.assertNotIn('choices_revision',e.live.current)
    def test_queued_regenerate_remains_forced_when_previous_card_worker_finishes(self):
        from test_live_review import Card
        e=self.e;seen=self.client();e.message('regenerate');e.mw.reviewer.card=Card(cid=2);e.mw.reviewer.card.fields[1]='Different correct answer';e.packet();self.cache_current()
        e.message('regenerate');self.assertEqual(len(e.background),1)
        self.finish();self.assertEqual(len(e.background),2);self.finish(1)
        self.assertEqual(e.live.current['cid'],'2');self.assertEqual(e.live.current['choices_revision'],1)
        self.assertEqual(seen[-1]['answer'],'Different correct answer');self.assertEqual(e.calls,['study'])

if __name__=='__main__':unittest.main()
