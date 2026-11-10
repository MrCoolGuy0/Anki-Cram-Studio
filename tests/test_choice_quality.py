"""Reported ambiguous sets and single-request provider-specific concept checks."""
import copy
import importlib
import json
import unittest
from test_core import c,g

a=importlib.import_module('cram_studio.ai')


class ChoiceQualityTests(unittest.TestCase):
    cases=[
        ('depletion','IPv4 limitations: IPv4 address [TARGET BLANK 1].',['scarcity','shortage','exhaustion']),
        ('Maximum Transmission Unit','The network establishes the [TARGET BLANK 1] (MTU).',
         ['Maximum Transfer Size','MTU size','Maximum Transfer Unit']),
        ('Copyright Act of 1976','Under Section 107 of the [TARGET BLANK 1], fair use is possible.',
         ['Copyright Law Of 1976','U.S. Copyright Act','U.S. Copyright Law']),
    ]

    def test_reported_ambiguities_are_rejected_even_without_model_aliases(self):
        for answer,clue,wrong in self.cases:
            with self.subTest(answer=answer),self.assertRaises(c.ChoiceValidationError):
                c.valid_distractors(answer,wrong,context=clue)

    def test_cache_prepare_and_attach_apply_context_guards_without_erasing_cache(self):
        for answer,clue,wrong in self.cases:
            question={'mode':'exam','clue':clue,'slots':[{'number':1,'answer':answer}]}
            for model in ('groq:model','gemini-model','grok:model'):
                with self.subTest(answer=answer,model=model):
                    q=copy.deepcopy(question);key=c.cache_key(q,q['slots'][0],model);cache={key:wrong};before=copy.deepcopy(cache)
                    jobs,ready=c.prepare_choices([q],cache,model);self.assertEqual((len(jobs),ready),(1,0))
                    c.attach_choices([q],cache,model,partial=True);self.assertFalse(q['ready']);self.assertNotIn('choices',q['slots'][0])
                    self.assertEqual(cache,before)

    def test_narrow_guards_do_not_merge_distinct_parameters_or_other_contexts(self):
        wrong=['Maximum segment size','Time to live','Receive window']
        self.assertEqual(c.valid_distractors('Maximum Transmission Unit',wrong,context='What is the MTU?'),wrong)
        self.assertNotEqual(c.contextual_choice_identity('exhaustion','Exercise physiology'),c.contextual_choice_identity('depletion','Exercise physiology'))
        self.assertNotEqual(c.contextual_choice_identity('U.S. Copyright Act','Name a legal document'),c.contextual_choice_identity('Copyright Act of 1976','Name a legal document'))

    def client(self,row,provider='groq'):
        calls=[]
        cls=a.Groq if provider=='groq' else a.Grok
        class Client(cls):
            def generate_json(self,prompt,schema,temperature):
                calls.append((prompt,schema,temperature));return {'sets':[row]}
        return Client('synthetic-key','model'),calls

    def row(self):
        return {'id':'x','answer_aliases':['MTU','MTU size'],'answer_concept':'Maximum transmission unit',
            'wrong':['Maximum segment size','Time to live','Receive window'],
            'wrong_concepts':['TCP maximum segment size','IP time to live','TCP receive window'],
            'wrong_reasons':['MSS limits TCP payload rather than the whole link packet.',
                'TTL limits forwarding lifetime rather than packet size.',
                'The receive window controls flow rather than link packet size.']}

    def test_groq_requires_canonical_distinctions_in_the_same_single_request(self):
        row=self.row();client,calls=self.client(row)
        job={'id':'x','answer':'Maximum Transmission Unit','clue':'Which link packet-size limit is MTU?'}
        self.assertEqual(client.generate([job]),{'x':row['wrong']});self.assertEqual(len(calls),1)
        prompt,schema,temperature=calls[0];self.assertEqual(temperature,.7)
        for text in ('HARD does not mean three synonyms','DISCARD and REPLACE','Maximum Transfer Unit','related and wrong is sufficient','question_for_this_blank'):
            self.assertIn(text,prompt)
        self.assertEqual(json.loads(prompt.split('DATA:\n',1)[1]),[job])
        required=schema['properties']['sets']['items']['required']
        for field in ('answer_concept','wrong_concepts','wrong_reasons'):self.assertIn(field,required)

    def test_unseen_aliases_and_duplicate_wrong_concepts_are_rejected(self):
        row=self.row();row.update(answer_aliases=[],answer_concept='The target concept',
            wrong=['A wholly different label','Different A','Different B'],
            wrong_concepts=['The target concept','Concept A','Concept B'])
        client,calls=self.client(row)
        with self.assertRaises(g.AIError):client.generate([{'id':'x','answer':'Original label'}])
        self.assertEqual(len(calls),1,'No hidden verification call or paid repair loop')
        row['wrong_concepts']=['Concept A','Concept A','Concept B'];client,calls=self.client(row)
        with self.assertRaises(g.AIError):client.generate([{'id':'x','answer':'Original label'}])

    def test_missing_or_invalid_contrasts_are_not_silently_accepted(self):
        for field in ('answer_concept','wrong_concepts','wrong_reasons'):
            for value in (None,'',[]):
                row=self.row();row[field]=value;client,calls=self.client(row)
                with self.subTest(field=field,value=value),self.assertRaises(g.AIError):
                    client.generate([{'id':'x','answer':'Maximum Transmission Unit','clue':'MTU'}])
                self.assertEqual(len(calls),1)
        row=self.row();row.pop('wrong_reasons');client,_=self.client(row)
        with self.assertRaises(g.AIError):client.generate([{'id':'x','answer':'Maximum Transmission Unit'}])

    def test_twelve_aliases_remain_supported(self):
        row=self.row();row['answer_aliases']=['Alias '+str(i) for i in range(12)];client,_=self.client(row)
        self.assertEqual(client.generate([{'id':'x','answer':'Maximum Transmission Unit'}])['x'],row['wrong'])

    def test_grok_and_gemini_do_not_require_the_groq_only_fields(self):
        row={'id':'x','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}
        client,calls=self.client(row,'grok');self.assertEqual(client.generate([{'id':'x','answer':'Paris'}])['x'],row['wrong'])
        self.assertNotIn('wrong_concepts',calls[0][1]['properties']['sets']['items']['properties'])
        captured=[]
        class Gemini(g.Gemini):
            def generate_json(self,*values):captured.append(values);return {'sets':[row]}
        Gemini('synthetic-key','model').generate([{'id':'x','answer':'Paris'}])
        self.assertNotIn('wrong_concepts',captured[0][1]['properties']['sets']['items']['properties'])
        # Both non-audit providers use the exact same shared instructions.
        self.assertEqual(captured[0][0],calls[0][0])
        self.assertIn('PRESENTATION MUST NOT REVEAL THE ANSWER',captured[0][0])

    def test_groq_inherits_entire_gemini_prompt_without_replacing_rules_or_data(self):
        job={'id':'x','answer':'Parasympathetic','clue':'Peripheral Nervous System: pupil constriction and slow heartbeat'}
        captured=[]
        class Gemini(g.Gemini):
            def generate_json(self,*values):
                captured.append(values);return {'sets':[{'id':'x','answer_aliases':[],'wrong':['Sympathetic','Somatic','Enteric']}]}
        Gemini('synthetic-key','model').generate([job])
        row={'id':'x','answer_aliases':[],'answer_concept':'Parasympathetic division',
             'wrong':['Sympathetic','Somatic','Enteric'],
             'wrong_concepts':['Sympathetic division','Somatic division','Enteric division'],
             'wrong_reasons':['Different control functions']*3}
        client,calls=self.client(row);self.assertEqual(client.generate([job])['x'],row['wrong'])
        common=captured[0][0].split('DATA:\n',1)[0]
        self.assertTrue(calls[0][0].startswith(common),'Groq must not shorten or replace common Gemini study rules')
        self.assertEqual(json.loads(calls[0][0].split('DATA:\n',1)[1]),[job])
        self.assertEqual(calls[0][0].count('DATA:\n'),1);self.assertEqual(len(calls),1)

    def test_naming_style_rule_covers_the_reported_suffix_and_all_case_patterns(self):
        for answer in ('Parasympathetic','PARASYMPATHETIC','parasympathetic','Parasympathetic Division'):
            row=self.row();row['wrong']=['Sympathetic','Somatic','Enteric']
            client,calls=self.client(row)
            client.generate([{'id':'x','answer':answer,'clue':'Which nervous-system division causes pupil constriction?'}])
            prompt=calls[0][0]
            for rule in ('ALL CAPS, all lowercase, Title Case, sentence case or mixed case',
                         'do not add a repeated category suffix','Never change the correct answer',
                         'Autonomic Nervous System','Never strip a meaningful word'):
                self.assertIn(rule,prompt)

    def test_writing_grouping_remains_identical_for_all_providers(self):
        captures=[]
        for cls in (g.Gemini,a.Groq,a.Grok):
            class Client(cls):
                def generate_json(self,*values):
                    captures.append(values);return {'sets':[{'id':'x','kind':'single','items':[],'connectors':[]}]}
            Client('synthetic-key','model').group_answers([{'id':'x','question':'A statement?','text':'One whole statement'}])
        self.assertEqual(captures[0],captures[1]);self.assertEqual(captures[1],captures[2])



if __name__=='__main__':unittest.main()
