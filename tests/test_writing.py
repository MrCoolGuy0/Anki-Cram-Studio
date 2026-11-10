"""Writing mode: source mapping, flexible layouts and passive reviewer integration."""
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
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
w=importlib.import_module('cram_studio.writing')
c=importlib.import_module('cram_studio.content')
g=importlib.import_module('cram_studio.gemini')
st=importlib.import_module('cram_studio.storage')

def basic(answer,clue='Name the fruits.'):
    return {'id':'note:1','cid':'1','nid':'1','kind':'basic','deck':'Deck','mode':'write','clue':clue,
            'slots':[{'number':1,'answer':c.choice_text(answer),'answer_html':c.clean(answer)}]}

def mapped(q,terms):
    text=w.source(q).text;cursor=0;spans=[]
    for term in terms:
        a=text.index(term,cursor);cursor=a+len(term);spans.append([a,cursor])
    q['writing']=w.build_plan(q,{'kind':'list','spans':spans});q['ready']=True
    return q

class SourceTests(unittest.TestCase):
    def test_numbered_bulleted_and_html_lists_need_no_ai_or_typed_numbers(self):
        for answer in ['1. banana\n2. mango\n3. lemon','1) banana<br>2) mango<br>3) lemon','<ol><li>banana</li><li>mango</li><li>lemon</li></ol>','<ul><li>banana</li><li>mango</li><li>lemon</li></ul>']:
            with self.subTest(answer=answer):
                q=basic(answer);plan=w.automatic(q)
                self.assertEqual([i['answer'] for i in plan['items']],['banana','mango','lemon'])
                self.assertIn('data-write-item="2"',plan['template']);self.assertNotIn('banana',plan['template'])
                self.assertEqual(w.match_input(plan,'BANANA',[],0)['matched'],[0])

    def test_basic_context_and_original_and_commas_markup_survive(self):
        q=mapped(basic('<b>Favorite fruits</b><div>The three types of fruit are <strong>banana</strong>, mango, and lemon.</div>'),['banana','mango','lemon'])
        plan=q['writing'];template=plan['template']
        self.assertIn('<b>Favorite fruits</b>',template);self.assertIn('The three types of fruit are ',template)
        self.assertIn(', and ',template);self.assertIn('<strong>',template);self.assertNotIn('<ol>',template)
        self.assertEqual(plan['items'][0]['parts'],['banana'])

    def test_compound_item_across_rich_text_is_not_split_or_flattened(self):
        q=mapped(basic('<div>Activities are <b>research</b> and development, testing, and maintenance.</div>'),['research and development','testing','maintenance'])
        self.assertEqual(q['writing']['items'][0]['parts'],['research',' and development'])
        self.assertIn('data-write-piece="1" hidden',q['writing']['template'])
        self.assertEqual(w.match_input(q['writing'],'research',[],0)['status'],'incomplete')
        self.assertEqual(w.match_input(q['writing'],'research and development',[],0)['matched'],[0])

    def test_no_with_explanation_is_one_answer(self):
        q=basic('NO, it depends on the organization.','Does this always apply?');plan=w.automatic(q)
        self.assertEqual(len(plan['items']),1)
        self.assertEqual(w.match_input(plan,'no',[],0)['status'],'incomplete')
        self.assertEqual(w.match_input(plan,'no, it depends on the organization',[],0)['matched'],[0])

    def test_singular_plural_is_one_item_without_a_leftover_suffix_blank(self):
        q=basic('BANANAS');plan=w.automatic(q)
        self.assertEqual(w.match_input(plan,'banana',[],0)['matched'],[0])
        self.assertEqual(w.match_input(plan,'bananas',[],0)['matched'],[0])
        self.assertEqual(len(plan['items']),1)

    def test_five_same_clozes_create_five_targets_without_ai(self):
        clue,slots=c.cloze_question('Fruit: {{c1::banana}}, {{c1::mango}}, {{c1::durian}}, {{c1::orange}}, and {{c1::lemon}}; {{c2::other clue}}.',{1})
        q={'kind':'cloze','mode':'write','clue':clue,'slots':slots};jobs,ready,_=w.attach([q],{})
        self.assertEqual((jobs,ready),([],1));self.assertEqual(len(q['writing']['items']),5)
        self.assertIn('other clue',q['writing']['template']);self.assertNotIn('banana',q['writing']['template'])
        self.assertEqual(w.match_input(q['writing'],'mango',[],0)['matched'],[1])
        self.assertEqual(w.match_input(q['writing'],'lemon, banana',[],0)['matched'],[4,0])

    def test_bad_model_ranges_cannot_drop_items_rewrite_words_or_inject_html(self):
        text='The fruits are banana, mango, and lemon.'
        for spans in ([[15,20],[23,28]],[[15,21],[23,28]],[[15,21],[23,28],[26,37]],[[-1,2],[3,5]]):
            with self.subTest(spans=spans),self.assertRaises(ValueError):w.validate_spans(text,{'kind':'list','spans':spans})
        q=basic('<script>bad()</script><span hidden>secret</span>Term')
        self.assertNotIn('bad',w.build_plan(q)['template']);self.assertNotIn('secret',w.build_plan(q)['template'])

class MatchingTests(unittest.TestCase):
    def setUp(self):self.q=mapped(basic('banana, mango, and lemon.'),['banana','mango','lemon']);self.plan=self.q['writing']
    def test_one_box_accepts_original_numbered_bullets_spacing_and_no_and(self):
        for value in ['banana, mango, and lemon','BANANA, MANGO, LEMON','1. banana\n2. mango\n3. lemon','1)banana; 2)mango; 3)lemon','• banana\n• mango\n• lemon','banana | mango / lemon','banana mango lemon','lemon, banana, mango']:
            with self.subTest(value=value):self.assertEqual(set(w.match_input(self.plan,value,[],0)['matched']),{0,1,2})

    def test_strict_vs_requested_ignore_extra_text_option(self):
        noisy='banana, waaaaaaaaaaahahaha, mango, jdjdjdjd, lemon'
        self.assertEqual(w.match_input(self.plan,noisy,[],0)['status'],'wrong')
        loose=copy.deepcopy(self.plan);loose['ignore_extra']=True
        self.assertEqual(w.match_input(loose,noisy,[],0)['matched'],[0,1,2])
        for value in ['bananass','mangosteen','lemongrass']:
            self.assertEqual(w.match_input(loose,value,[],0)['status'],'wrong')

    def test_unknown_content_and_duplicate_entries_are_not_silently_ignored_in_strict_mode(self):
        for value in ['banana, potato, mango, lemon','banana, banana, mango, lemon','banana, mango, lemon, 99','bananass, mango, lemon']:
            with self.subTest(value=value):self.assertEqual(w.match_input(self.plan,value,[],0)['status'],'wrong')

    def test_order_only_when_question_requires_it(self):
        self.assertEqual(w.match_input(self.plan,'lemon',[],0)['matched'],[2])
        q=mapped(basic('banana, mango, and lemon.','Give these fruits in order.'),['banana','mango','lemon'])
        self.assertTrue(q['writing']['ordered']);self.assertEqual(w.match_input(q['writing'],'lemon',[],0)['status'],'wrong')

    def test_screenshot_quotes_hyphen_and_enye_variants_preserve_display(self):
        for answer,typed in [('"set at naught"','set at naught'),('“set at naught”','"SET AT NAUGHT"'),('In Writing','in-writing'),('In‑Writing','in writing'),('Jaypoy Laviña','Jaypoy Lavina'),('JAYPOY LAVIN\u0303A','jaypoy lavina')]:
            with self.subTest(answer=answer,typed=typed):
                q=basic(answer);plan=w.build_plan(q);original=copy.deepcopy(plan)
                self.assertEqual(w.match_input(plan,typed,[],0)['matched'],[0]);self.assertEqual(plan,original)
                self.assertEqual(plan['items'][0]['answer'],answer)
        q=mapped(basic('"banana", In Writing, and Jaypoy Laviña.'),['"banana"','In Writing','Jaypoy Laviña'])
        self.assertEqual(w.match_input(q['writing'],'bananas, in-writing, Jaypoy Lavina',[],0)['matched'],[0,1,2])

    def test_combined_presentation_differences_do_not_require_a_date_specific_rule(self):
        for answer,typed in [('January 1, 1978','january 1 1978'),('JANUARY 1,1978','January 1, 1978'),('“Jaypoy Laviña, in-writing”','jaypoy lavina in writing'),('mango, banana','MANGOS BANANAS'),('NO, it depends on the organization','no it depends on the organization')]:
            with self.subTest(answer=answer,typed=typed):self.assertTrue(w.equivalent(answer,typed))
        for answer,typed in [('January 1, 1978','January 1 1979'),('January 1, 1978','January 11 1978'),('January 1, 1978','January 11978'),('4(c)(4)','4(c)(5)'),('2*(3+4)','2*3+4'),('f(a,b)','f(a b)')]:
            with self.subTest(answer=answer,typed=typed):self.assertFalse(w.equivalent(answer,typed))

    def test_common_plural_forms_work_both_ways_without_fuzzy_concept_matching(self):
        for first,second in [('banana','bananas'),('body','bodies'),('box','boxes'),('leaf','leaves'),('analysis','analyses'),('child','children'),('tooth','teeth'),('nucleus','nuclei'),('mango','mangoes'),('lens','lenses'),('virus','viruses')]:
            with self.subTest(first=first,second=second):
                self.assertTrue(w.equivalent(first,second));self.assertTrue(w.equivalent(second,first))
        for first,second in [('banana','bandana'),('mango','mangosteen'),('estrogen','estrone'),('testosterone','progesterone'),('no','yes'),('not required','required'),('Layer 1','Layer 2'),('-10','10'),('C++','C'),('physics','physic'),('diabetes','diabete'),('news','new'),('lens','len')]:
            with self.subTest(first=first,second=second):self.assertFalse(w.equivalent(first,second))

    def test_plural_multi_item_and_noise_settings_do_not_change_group_count(self):
        state=w.evaluate(self.plan,[{'text':'BANANAS, MANGOS, AND LEMONS','target':0}])
        self.assertTrue(state['complete']);self.assertEqual(len(self.plan['items']),3)
        self.assertEqual(w.match_input(self.plan,'bananas, unrelated, mangos, lemons',[],0)['status'],'wrong')
        plan=copy.deepcopy(self.plan);plan['ignore_extra']=True
        self.assertEqual(w.match_input(plan,'bananas, unrelated, mangoes, lemons',[],0)['matched'],[0,1,2])

    def test_extra_text_does_not_accept_a_more_specific_or_changed_numeric_reference(self):
        for answer,typed in [('Section 4','section 4(c)(4)'),('Section 4','Section 4(c)'),('Section 4(c)','Section 4(c)(4)'),('Section 4','Section 4/5'),('4','-4'),('4','4.1'),('4','0.4'),('Section 4(c)(4)','Section 4(c)(5)'),('Section 4','Section 4, c, 4'),('January 1, 1978','January 1 1978 1979'),('C','C++')]:
            for loose in (False,True):
                with self.subTest(answer=answer,typed=typed,loose=loose):
                    plan=w.build_plan(basic(answer));plan['ignore_extra']=loose
                    self.assertEqual(w.match_input(plan,typed,[],0)['status'],'wrong')
        plan=w.build_plan(basic('Section 4'));plan['ignore_extra']=True
        self.assertEqual(w.match_input(plan,'section 4',[],0)['matched'],[0])
        self.assertEqual(w.match_input(plan,'Answer: Section 4.',[],0)['matched'],[0])

    def test_partial_enum_progress_and_first_attempt_misses_are_recomputed(self):
        events,state=w.attempt(self.q,[],'potato',0);self.assertEqual(state['accepted'],[])
        events,state=w.attempt(self.q,events,'banana',0);self.assertEqual(state['accepted'],[0])
        events,state=w.attempt(self.q,events,'mango, lemon',1);self.assertTrue(state['complete'])
        grade=c.grade(self.q,{'writing':events});self.assertEqual((grade['earned'],grade['total']),(2,3))
        self.assertFalse(grade['correct'][0]);self.assertEqual(self.q['writing'],self.plan)

    def test_reveal_can_finish_with_missing_items_without_giving_them_credit(self):
        events,_=w.attempt(self.q,[],'mango',0)
        with self.assertRaises(ValueError):c.grade(self.q,{'writing':events})
        self.assertEqual(c.grade(self.q,{'writing':events,'unknown':True})['earned'],1)

    def test_meaningful_numbers_and_compound_and_are_part_of_the_item(self):
        q=mapped(basic('Layer 1, Layer 2, and research and development.'),['Layer 1','Layer 2','research and development'])
        for value in ['Layer','Layer 3','research development']:
            self.assertNotEqual(w.match_input(q['writing'],value,[],0)['status'],'correct')
        self.assertEqual(w.match_input(q['writing'],'1. Layer 1\n2. Layer 2\n3. research and development',[],0)['matched'],[0,1,2])

    def test_malformed_input_cannot_fake_grade_or_exceed_bounds(self):
        for picks in ({'writing':'banana'},{'writing':[{'text':'banana','target':True}]},{'writing':[{'text':[], 'target':0}]},{'writing':[{'text':'x'*20001,'target':0}]}):
            with self.subTest(picks=picks),self.assertRaises(ValueError):c.grade(self.q,picks)

class GroupingTests(unittest.TestCase):
    def test_cached_plan_reuses_source_and_invalidates_when_question_or_back_changes(self):
        q=self.q=basic('The fruits are banana, mango, and lemon.')
        jobs,ready,_=w.attach([q],{});self.assertEqual((len(jobs),ready),(1,0));key=jobs[0]['id']
        text=w.source(q).text;spans=[[text.index(v),text.index(v)+len(v)] for v in ['banana','mango','lemon']]
        cache={key:{'kind':'list','spans':spans}};w.attach([q],cache)
        self.assertTrue(q['ready']);self.assertIn('The fruits are ',q['writing']['template'])
        q2=copy.deepcopy(q);q2['clue']='Another question';self.assertNotEqual(w.plan_key(q2),key)
        before=copy.deepcopy(cache);w.attach([q],cache);self.assertEqual(cache,before)

    def test_no_key_fallback_requires_no_manual_item_setup(self):
        q=basic('research and development, testing, and maintenance')
        jobs,ready,_=w.attach([q],{},whole=True)
        self.assertEqual((jobs,ready),([],1));self.assertEqual(len(q['writing']['items']),1)

    def test_model_only_selects_exact_source_substrings(self):
        q=basic('The fruits are banana, mango, and lemon.');text=w.source(q).text
        entries={'sets':[{'id':'a','kind':'list','items':['banana','mango','lemon']}]};requests=[]
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(entries)}]}}]}).encode()
        def opener(req,timeout):requests.append(req);return Response()
        client=g.Gemini('secret','test',opener);jobs=[{'id':'a','question':q['clue'],'text':text}]
        result=client.group_answers(jobs);self.assertEqual(len(result['a']['spans']),3);self.assertEqual(len(requests),1)
        entries['sets'][0]['items'][0]='bananas'
        with self.assertRaises(g.AIError):client.group_answers(jobs)

    def test_model_connector_roles_cover_unfamiliar_wording_using_literal_source(self):
        text='mango, banana, with the final spotlight going to apple'
        entry={'id':'a','kind':'list','items':['mango','banana','apple'],'connectors':['with the final spotlight going to']};requests=[]
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'sets':[entry]})}]}}]}).encode()
        def opener(req,timeout):requests.append(req);return Response()
        client=g.Gemini('secret','test',opener);result=client.group_answers([{'id':'a','question':'Name the fruits.','text':text}])
        self.assertEqual(result['a']['connectors'],entry['connectors'])
        body=json.loads(requests[0].data);self.assertIn('connectors',body['generationConfig']['responseSchema']['properties']['sets']['items']['required'])
        entry['connectors']=['made up wording']
        with self.assertRaises(g.AIError):client.group_answers([{'id':'a','question':'Name the fruits.','text':text}])

    def test_background_grouping_batches_cancel_and_does_not_save_failed_batches(self):
        jobs=[{'id':str(i)} for i in range(7)];calls=[];cancel=threading.Event()
        class Client:
            def group_answers(self,batch):calls.append(len(batch));return {j['id']:{'kind':'single','spans':[]} for j in batch}
        with tempfile.TemporaryDirectory() as td:
            store=st.Store(td);w.generate(Client(),jobs,store,cancel,lambda *_:None)
            self.assertEqual(calls,[1,5,1]);self.assertEqual(len(store.cache()),7)
            cancel.set();w.generate(Client(),jobs,store,cancel,lambda *_:None);self.assertEqual(calls,[1,5,1])

class WritingAliasAndPairTests(unittest.TestCase):
    def test_source_repeated_initials_allow_expansion_or_abbreviation_without_rewriting(self):
        for authored,typed in [('frame check sequence (FCS)','frame check sequence'),('frame check sequence (FCS)','fcs'),('FCS (frame check sequence)','frame check sequence'),('Logical Link Control (LLC)','logical link control'),('University of Santo Tomas (UST)','ust')]:
            with self.subTest(authored=authored,typed=typed):
                q=basic(authored);plan=w.build_plan(q);original=copy.deepcopy(plan)
                self.assertEqual(w.match_input(plan,typed,[],0)['status'],'correct');self.assertEqual(plan,original)
    def test_parenthetical_meaning_numbers_wrong_initials_and_negation_stay_required(self):
        for authored,typed in [('Section 4(c)(4)','Section 4'),('Type 2 diabetes (adult onset)','Type 2 diabetes'),('frame check sequence (XYZ)','frame check sequence'),('NO (not optional)','NO'),('C (programming language)','C'),('Frame check sequence (FCS)','frame checksum sequence')]:
            for ignore in (False,True):
                with self.subTest(authored=authored,typed=typed,ignore=ignore):
                    plan=w.build_plan(basic(authored));plan['ignore_extra']=ignore
                    self.assertNotEqual(w.match_input(plan,typed,[],0)['status'],'correct')
    def test_abbreviated_terms_in_a_batch_remain_source_grounded(self):
        q=mapped(basic('frame check sequence (FCS), Logical Link Control (LLC)'),['frame check sequence (FCS)','Logical Link Control (LLC)'])
        self.assertEqual(w.match_input(q['writing'],'frame check sequence, logical link control',[],0)['matched'],[0,1])
    def test_two_independent_terms_are_valid_groups_and_old_policy_cache_is_not_reused(self):
        q=basic('LLC and MAC','Ethernet sublayers');text=w.source(q).text
        raw={'kind':'list','spans':[[0,3],[8,11]],'connectors':[]}
        import hashlib
        old='writing:'+hashlib.sha256(json.dumps([1,q['clue'],q['slots'][0]['answer_html'],q['slots'][0]['answer']],ensure_ascii=False).encode()).hexdigest()
        jobs,_,_=w.attach([q],{old:{'kind':'single','spans':[]}})
        self.assertEqual(len(jobs),1);self.assertNotEqual(jobs[0]['id'],old)
        w.attach([q],{jobs[0]['id']:raw});self.assertEqual([v['answer'] for v in q['writing']['items']],['LLC','MAC'])
        self.assertEqual(w.match_input(q['writing'],'LLC',[],0)['matched'],[0])
        self.assertEqual(w.match_input(q['writing'],'MAC',[],0)['matched'],[1]);self.assertEqual(text,'LLC and MAC')

class ClozeEnumerationTests(unittest.TestCase):
    def question(self,value):
        clue,slots=c.cloze_question(value,{1})
        return dict(basic('unused'),kind='cloze',clue=clue,slots=slots)

    def cached(self,q,terms,connectors=()):
        jobs,_,_=w.attach([q],{});self.assertEqual(len(jobs),1)
        text=jobs[0]['text'];spans=[];cursor=0
        for term in terms:
            start=text.index(term,cursor);cursor=start+len(term);spans.append([start,cursor])
        cache={jobs[0]['id']:{'kind':'list','spans':spans,'connectors':list(connectors)}}
        self.assertEqual(w.attach([q],cache)[0],[])
        return cache

    def test_one_cloze_list_becomes_three_items_with_original_connectors(self):
        for value,connector in [('mango, banana, apple',None),('mango, banana, and then apple','and then'),('mango, banana, most importantly apple','most importantly'),('mango, banana, with the final spotlight going to apple','with the final spotlight going to')]:
            with self.subTest(value=value):
                q=self.question('Name the fruit: {{c1::'+value+'}}. Context {{c2::still visible}}.')
                self.cached(q,['mango','banana','apple'],[connector] if connector else [])
                plan=q['writing'];self.assertEqual([i['answer'] for i in plan['items']],['mango','banana','apple'])
                self.assertEqual([i['cloze_slot'] for i in plan['items']],[0,0,0]);self.assertIn('still visible',plan['template'])
                self.assertEqual(plan['template'].count('data-write-item='),3)
                if connector:self.assertIn(connector,plan['template'])
                self.assertNotIn('mango',plan['template']);self.assertNotIn('apple',plan['template'])
                events,state=w.attempt(q,[],'banana',0);self.assertEqual(state['accepted'],[1])
                events,state=w.attempt(q,events,'mango apple',0);self.assertTrue(state['complete'])
                self.assertEqual(c.grade(q,{'writing':events})['total'],3)
                self.assertTrue(w.evaluate(plan,[{'text':value,'target':0}])['complete'])

    def test_separate_and_combined_blocks_share_one_stable_item_index(self):
        q=self.question('{{c1::<b>mango</b>, banana, and apple}} plus {{c1::orange}}; {{c2::pear}}.')
        self.cached(q,['mango','banana','apple'])
        plan=q['writing'];self.assertEqual([i['answer'] for i in plan['items']],['mango','banana','apple','orange'])
        self.assertEqual([i['cloze_slot'] for i in plan['items']],[0,0,0,1]);self.assertIn('<b>',plan['template']);self.assertIn('pear',plan['template'])
        self.assertIn('data-write-item="3"',plan['template']);self.assertNotIn('data-blank=',plan['template'])
        self.assertTrue(w.evaluate(plan,[{'text':'mango banana apple orange','target':0}])['complete'])

    def test_explicit_numbered_lists_work_offline_inside_a_cloze(self):
        q=self.question('Name fruit: {{c1::<ol><li>banana</li><li>mango</li><li>apple</li></ol>}}.')
        jobs,ready,_=w.attach([q],{});self.assertEqual((jobs,ready),([],1))
        self.assertEqual([i['answer'] for i in q['writing']['items']],['banana','mango','apple'])
        self.assertIn('<ol>',q['writing']['template']);self.assertEqual(w.match_input(q['writing'],'mango',[],0)['matched'],[1])

    def test_dates_statements_and_compounds_remain_whole_when_grouped_single(self):
        for answer in ['January 1, 1978','research and development','NO, it depends on the organization']:
            q=self.question('Recall: {{c1::'+answer+'}}.')
            jobs,_,_=w.attach([q],{});cache={j['id']:{'kind':'single','spans':[],'connectors':[]} for j in jobs}
            w.attach([q],cache);self.assertEqual(len(q['writing']['items']),1)
            self.assertEqual(q['writing']['items'][0]['answer'],answer)
        self.assertEqual(w.match_input(q['writing'],'no',[],0)['status'],'incomplete')

    def test_source_connector_metadata_rejects_invention_or_dropped_numbers(self):
        text='mango, banana, most importantly apple'
        spans=[[text.index(t),text.index(t)+len(t)] for t in ['mango','banana','apple']]
        self.assertEqual(len(w.validate_spans(text,{'kind':'list','spans':spans,'connectors':['most importantly']})),3)
        for connectors in ([],['imaginary connector'],['most importantly 4'],'most importantly'):
            with self.subTest(connectors=connectors),self.assertRaises(ValueError):w.validate_spans(text,{'kind':'list','spans':spans,'connectors':connectors})

    def test_repeated_blocks_deduplicate_ai_jobs_but_keep_distinct_targets(self):
        q=self.question('{{c1::mango, banana, apple}} and {{c1::mango, banana, apple}}.')
        self.cached(q,['mango','banana','apple'])
        self.assertEqual(len(q['writing']['items']),6)
        before=copy.deepcopy(q);w.attach([q],{},whole=True)
        self.assertEqual(len(q['writing']['items']),2,'offline fallback keeps each original block complete')
        self.assertEqual(before['slots'],q['slots']);self.assertEqual(before['clue'],q['clue'])

    def test_partial_combined_cloze_survives_main_disk_resume(self):
        from test_progress import Controller,config
        with tempfile.TemporaryDirectory() as td:
            q=self.question('Fruit: {{c1::mango, banana, most importantly apple}}.')
            cache=self.cached(q,['mango','banana','apple'],['most importantly'])
            a=Controller(td);a.owner.store.put(cache);sid=a.launch([q],config(mode='write'))
            a.owner.write_submit({'index':0,'events':[],'text':'banana','target':0});events=a.events[-1][1]['events']
            a.owner.save_progress({'index':0,'written':{'0':{'events':events,'draft':'mang','target':0}}},full=True)
            b=Controller(td);b.owner.resume(sid);packet=b.events[-1][1]
            self.assertEqual(packet['view']['written']['0']['state']['accepted'],[1]);self.assertEqual(len(b.owner.questions[0]['writing']['items']),3)
            self.assertEqual(packet['view']['written']['0']['draft'],'mang')

class NativeWritingTests(unittest.TestCase):
    def test_native_combined_cloze_grouping_and_each_member_stay_on_the_same_card(self):
        from test_live_review import Environment,Card,l
        class Client:
            def __init__(self,*args):pass
            def group_answers(self,jobs):
                result={}
                for job in jobs:
                    spans=[[job['text'].index(v),job['text'].index(v)+len(v)] for v in ['mango','banana','apple']]
                    result[job['id']]={'kind':'list','spans':spans,'connectors':['most importantly']}
                return result
        with tempfile.TemporaryDirectory() as td,patch.object(l,'Gemini',Client):
            e=Environment(td,True,False);e.live.store.set_key('test-key');e.mw.reviewer.card=Card(kind='Cloze')
            e.mw.reviewer.card.fields[0]='Fruits: {{c1::mango, banana, most importantly apple}}; {{c2::another clue}}.'
            e.live.begin('write',True);e.packet();self.assertFalse(e.live.current['question']['ready'])
            cid=e.live.current['cid'];before=copy.deepcopy(e.col.deck);e.message('ready')
            work,done=e.background.pop();future=Future();future.set_result(work());done(future)
            p=e.live.current;self.assertEqual(len(p['question']['writing']['items']),3)
            for target,term in enumerate(['mango','banana','apple']):
                e.message('write_submit',text=term,target=target);self.assertEqual(p['cid'],cid)
                self.assertEqual(e.calls,['study']);self.assertEqual(e.col.deck,before)
            self.assertTrue(p['writing_state']['complete']);self.assertEqual(p['side'],'question')
            e.packet('reviewAnswer');self.assertEqual(p['side'],'answer');self.assertEqual(e.calls,['study'])

    def test_native_single_date_accepts_missing_comma_without_splitting_into_items(self):
        from test_live_review import Environment,Card,l
        class Client:
            def __init__(self,*args):pass
            def group_answers(self,jobs):return {j['id']:{'kind':'single','spans':[],'connectors':[]} for j in jobs}
        with tempfile.TemporaryDirectory() as td,patch.object(l,'Gemini',Client):
            e=Environment(td);e.live.store.set_key('test-key');e.mw.reviewer.card=Card(kind='Cloze')
            e.mw.reviewer.card.fields[0]='Created before {{c1::January 1, 1978}}.'
            e.live.begin('write',True);e.packet();e.message('ready');work,done=e.background.pop();future=Future();future.set_result(work());done(future)
            self.assertEqual(len(e.live.current['question']['writing']['items']),1)
            e.message('write_submit',text='january 1 1978',target=0)
            self.assertTrue(e.live.current['writing_state']['complete']);self.assertEqual(e.calls,['study'])

    def test_native_typing_does_not_answer_rate_or_change_queue(self):
        from test_live_review import Environment
        with tempfile.TemporaryDirectory() as td:
            e=Environment(td);e.live.begin('write');packet=e.packet();p=e.live.current
            self.assertEqual(p['display'],'write');self.assertTrue(p['question']['ready'])
            answer=p['question']['writing']['items'][0]['answer']
            before=list(e.calls)
            msg='cram_live:'+json.dumps({'cid':p['cid'],'epoch':p['epoch'],'action':'write_submit','text':answer,'target':0})
            self.assertEqual(e.live.message((False,None),msg,e.mw.reviewer),(True,None))
            self.assertTrue(p['writing_state']['complete']);self.assertEqual(e.calls,before)
            self.assertEqual(e.mw.reviewer.state,'question')

    def test_native_filtered_on_off_and_source_edits_keep_anki_in_charge(self):
        from test_live_review import Environment
        for resched in (False,True):
            with self.subTest(resched=resched),tempfile.TemporaryDirectory() as td:
                e=Environment(td,True,resched);e.live.begin('write');e.packet();p=e.live.current
                original=copy.deepcopy(e.col.deck);epoch=p['epoch']
                e.message('write_submit',text=p['question']['writing']['items'][0]['answer'],target=0)
                self.assertEqual(e.col.deck,original);self.assertEqual(e.calls,['study'])
                e.mw.reviewer.card.fields[1]='A corrected answer';e.packet();p=e.live.current
                self.assertGreater(p['epoch'],epoch);self.assertEqual(p['writing_events'],[])
                self.assertEqual(p['question']['writing']['items'][0]['answer'],'A corrected answer')
                e.message('write_submit',epoch=epoch,text='old answer',target=0)
                self.assertEqual(p['writing_events'],[]);self.assertEqual(e.calls,['study'])
                e.packet('reviewAnswer');e.message('write_submit',text='A corrected answer',target=0)
                self.assertEqual(p['writing_events'],[]);self.assertEqual(e.col.deck,original)

    def test_native_grouping_error_falls_back_and_cancelled_result_cannot_replace_full_answer(self):
        from test_live_review import Environment,Card,l
        class Client:
            def __init__(self,*args):pass
            def group_answers(self,jobs):raise g.AIError('Quota reached')
        with tempfile.TemporaryDirectory() as td,patch.object(l,'Gemini',Client):
            e=Environment(td);e.live.store.set_key('test-key');e.mw.reviewer.card.fields[1]='banana, mango, and lemon'
            e.live.begin('write',True);e.packet();self.assertFalse(e.live.current['question']['ready'])
            e.message('ready');work,done=e.background.pop();future=Future()
            try:future.set_result(work())
            except Exception as error:future.set_exception(error)
            done(future);p=e.live.current
            self.assertTrue(p['question']['ready']);self.assertEqual(len(p['question']['writing']['items']),1)
            self.assertIn('Quota',p['error']);self.assertEqual(e.calls,['study'])
            e.mw.reviewer.card=Card(cid=2);e.mw.reviewer.card.fields[1]='apple, pear, and grape';e.packet()
            e.message('ready');work,done=e.background.pop();epoch=e.live.current['epoch']
            e.message('write_whole');self.assertTrue(e.live.current['question']['ready'])
            future=Future();future.set_result(None);done(future)
            self.assertEqual(e.live.current['epoch'],epoch);self.assertFalse(e.live.current['generating'])
            self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.cache(),{})

    def test_native_valid_grouping_is_cached_once_and_does_not_reveal_or_rate(self):
        from test_live_review import Environment,l
        class Client:
            def __init__(self,*args):pass
            def group_answers(self,jobs):
                out={}
                for job in jobs:
                    spans=[[job['text'].index(term),job['text'].index(term)+len(term)] for term in ['banana','mango','lemon']]
                    out[job['id']]={'kind':'list','spans':spans}
                return out
        with tempfile.TemporaryDirectory() as td,patch.object(l,'Gemini',Client):
            e=Environment(td);e.live.store.set_key('test-key');e.mw.reviewer.card.fields[1]='banana, mango, and lemon'
            e.live.begin('write',True);e.packet();e.message('ready');e.message('ready')
            self.assertEqual(len(e.background),1);work,done=e.background.pop();future=Future();future.set_result(work());done(future)
            self.assertEqual(len(e.live.current['question']['writing']['items']),3)
            e.message('ready');self.assertEqual(e.background,[]);self.assertEqual(e.calls,['study'])
            self.assertEqual(e.live.current['side'],'question');self.assertEqual(e.live.store.data['history'],[])

    def test_main_partial_writing_survives_disk_reopen_and_does_not_reset_other_sessions(self):
        from test_progress import Controller,config
        with tempfile.TemporaryDirectory() as td:
            a=Controller(td);q=mapped(basic('<ol><li>banana</li><li>mango</li><li>lemon</li></ol>'),['banana','mango','lemon'])
            sid=a.launch([q],config(mode='write'));o=a.owner
            o.write_submit({'index':0,'events':[],'text':'BANANA','target':0})
            events=a.events[-1][1]['events']
            o.save_progress({'index':0,'written':{'0':{'events':events,'draft':'man','target':1}}},full=True)
            b=Controller(td);b.owner.resume(sid);packet=b.events[-1][1]
            self.assertEqual(packet['view']['written']['0']['state']['accepted'],[0])
            self.assertEqual(packet['view']['written']['0']['draft'],'man')
            self.assertEqual(b.owner.questions[0]['mode'],'write')

    def test_main_ignore_extra_option_and_partial_results_persist_without_auto_grading(self):
        from test_progress import Controller,config
        with tempfile.TemporaryDirectory() as td:
            a=Controller(td);q=basic('<ol><li>banana</li><li>mango</li><li>lemon</li></ol>')
            sid=a.launch([q],dict(config(mode='write'),write_ignore_extra=True,repeat_mistakes=True));o=a.owner
            o.write_submit({'index':0,'events':[],'text':'banana, noise, mango, noise, lemon','target':0})
            events=a.events[-1][1]['events'];self.assertTrue(a.events[-1][1]['state']['complete'])
            self.assertEqual(o.results,{},'matching does not count as a grade')
            b=Controller(td);b.owner.resume(sid)
            self.assertTrue(b.owner.config['write_ignore_extra']);self.assertTrue(b.owner.questions[0]['writing']['ignore_extra'])
            b.owner.submit({'index':0,'picks':{'writing':events}})
            self.assertEqual(b.owner.results['0']['earned'],3)

if __name__=='__main__':unittest.main()
