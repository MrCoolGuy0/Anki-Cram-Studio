"""Shared Writing enumeration regressions; synthetic responses, no API charges."""
import copy
import importlib
import json
import tempfile
import unittest
from unittest.mock import patch
from test_writing import basic,w,c,g

a=importlib.import_module('cram_studio.ai')
TERMS=['sweet','salty','sour','bitter','umami']
TEXT='sweet, salty, sour, bitter, and umami'

def question(cloze=False):
    if not cloze:return basic(TEXT,'The five primary tastes are:')
    clue,slots=c.cloze_question('<b>GENERAL SENSORY SYSTEM</b><br>The five primary tastes are {{c1::'+TEXT+'}}.',{1})
    return dict(basic('unused'),kind='cloze',clue=clue,slots=slots)

class WritingProviderParity(unittest.TestCase):
    def test_reported_five_item_list_is_ready_offline_in_basic_and_one_cloze(self):
        for cloze in (False,True):
            q=question(cloze);before=copy.deepcopy(q)
            jobs,ready,_=w.attach([q],{})
            self.assertEqual((jobs,ready),([],1));plan=q['writing']
            self.assertEqual([i['answer'] for i in plan['items']],TERMS)
            self.assertEqual(plan['template'].count('data-write-item='),5)
            self.assertIn(', and ',plan['template']);self.assertNotIn('<ol>',plan['template'])
            self.assertEqual(q['slots'],before['slots']);self.assertEqual(q['clue'],before['clue'])
            events,state=w.attempt(q,[],'SWEET',0);self.assertEqual(state['accepted'],[0])
            self.assertEqual(len(state['remaining']),4)
            events,state=w.attempt(q,events,'1. SALTY\n2. sour\n3. bitter\n4. umami',1)
            self.assertTrue(state['complete']);self.assertEqual(len(state['accepted']),5)
    def test_bad_old_single_cache_cannot_override_the_clear_count(self):
        q=question(True);sub=w.cloze_sources(q)[0]
        jobs,ready,_=w.attach([q],{w.plan_key(sub):{'kind':'single','spans':[]}})
        self.assertEqual((jobs,ready),([],1));self.assertEqual(len(q['writing']['items']),5)
    def test_counted_fast_path_handles_comma_and_semicolon_and_non_oxford_lists(self):
        for text in (TEXT,'sweet, salty, sour, bitter and umami','sweet; salty; sour; bitter; umami'):
            q=basic(text,'List 5 tastes.');jobs,ready,_=w.attach([q],{})
            self.assertEqual((jobs,ready),([],1));self.assertEqual([i['answer'] for i in q['writing']['items']],TERMS)
    def test_fast_path_does_not_guess_compounds_dates_prose_counts_or_multiple_cloze_targets(self):
        cases=[('research and development, testing, maintenance','The three activities are:'),
               ('January 1, 1978','Name two dates.'),
               ('sweet, salty, sour, bitter','The five tastes are:'),
               ('mango, banana, most importantly apple','The three fruits are:'),
               ('NO, it depends on the organization','The two options are:')]
        for text,clue in cases:
            self.assertIsNone(w.counted_simple_list(basic(text,clue),text))
        q=question(True);q['clue']+=' <span data-blank="1">_____</span>'
        self.assertIsNone(w.counted_simple_list(dict(w.cloze_sources(q)[0]),TEXT))
    def test_all_providers_share_prompt_and_tolerate_empty_gaps_case_and_spacing(self):
        captures=[];text='The parts are <b>sweet</b>, salty, sour, bitter, and umami.'
        # Real HTML is not passed to AI; use the exact visible source text.
        text=w.source(basic(text)).text
        row={'id':'x','kind':'list','items':[v.upper() for v in TERMS],
             'connectors':['',' ', ', ', 'AND', 'THE PARTS ARE']}
        for cls in (g.Gemini,a.Groq,a.Grok):
            class Client(cls):
                def generate_json(self,*values):captures.append(values);return {'sets':[copy.deepcopy(row)]}
            result=Client('synthetic','model').group_answers([{'id':'x','question':'Which five parts?','text':text}])
            raw=result['x'];self.assertEqual([text[s:e] for s,e in raw['spans']],TERMS)
            self.assertNotIn('',raw['connectors']);self.assertIn('The parts are',raw['connectors'])
        self.assertEqual(captures[0],captures[1]);self.assertEqual(captures[1],captures[2])
        self.assertIn('Do not treat one cloze block as automatically one answer item',captures[0][0])
    def test_normalized_alignment_keeps_source_whitespace_case_and_rich_markup(self):
        q=basic('<b>Logical</b>  Link Control, Media Access Control','Name the sublayers.')
        text=w.source(q).text
        raw=w.grouping_from_items(text,{'kind':'list','items':['logical link control','MEDIA ACCESS CONTROL'],'connectors':['']})
        plan=w.build_plan(q,raw)
        self.assertEqual([v['answer'] for v in plan['items']],['Logical  Link Control','Media Access Control'])
        self.assertIn('<b>',plan['template']);self.assertIn('</b>',plan['template'])
        self.assertTrue(w.match_input(plan,'llc',[],0)['status']!='correct')
    def test_alignment_never_accepts_synonyms_changed_numbers_dropped_items_or_cut_words(self):
        cases=[(TEXT,['sweet','salty','sour','bitter','savory'],[]),
               ('Section 4(c)(4), Section 5',['Section 4(c)(3)','Section 5'],[]),
               (TEXT,TERMS[:-1],[]),('banana, mango',['ana','mango'],[]),
               ('banana, mango',['banana','mango'],['invented framing'])]
        for text,items,connectors in cases:
            with self.subTest(text=text,items=items),self.assertRaises(ValueError):
                w.grouping_from_items(text,{'kind':'list','items':items,'connectors':connectors})
    def test_native_counted_cloze_works_for_every_provider_without_network_or_rating(self):
        from test_live_review import Environment,Card,l
        for provider,model in [('gemini','test-model'),('groq','openai/gpt-oss-20b'),('grok','grok-test')]:
            with self.subTest(provider=provider),tempfile.TemporaryDirectory() as td,patch.object(l,'Gemini',side_effect=AssertionError('Clear counted list must not call AI')):
                e=Environment(td,True,False);e.live.store.select_provider(provider,model);e.live.store.set_key('synthetic')
                e.mw.reviewer.card=Card(kind='Cloze');e.mw.reviewer.card.fields[0]='The five primary tastes are {{c1::'+TEXT+'}}.'
                e.live.begin('write',True);e.packet();e.message('ready');p=e.live.current;deck=copy.deepcopy(e.col.deck)
                self.assertEqual(len(p['question']['writing']['items']),5);self.assertEqual(e.background,[])
                e.message('write_submit',text='SWEET',target=0);self.assertEqual(p['writing_state']['accepted'],[0])
                e.message('write_submit',text='salty sour bitter umami',target=1);self.assertTrue(p['writing_state']['complete'])
                self.assertEqual(e.calls,['study']);self.assertEqual(e.col.deck,deck)
    def test_main_partial_five_item_progress_survives_resume(self):
        from test_progress import Controller,config
        with tempfile.TemporaryDirectory() as td:
            q=question(True);w.attach([q],{});first=Controller(td);sid=first.launch([q],config(mode='write'))
            first.owner.write_submit({'index':0,'events':[],'text':'sweet','target':0});events=first.events[-1][1]['events']
            first.owner.save_progress({'index':0,'written':{'0':{'events':events,'draft':'sal','target':1}}},full=True)
            second=Controller(td);second.owner.resume(sid);packet=second.events[-1][1]
            self.assertEqual(len(second.owner.questions[0]['writing']['items']),5)
            self.assertEqual(packet['view']['written']['0']['state']['accepted'],[0])
            self.assertEqual(packet['view']['written']['0']['draft'],'sal');self.assertEqual(second.owner.results,{})

if __name__=='__main__':unittest.main()
