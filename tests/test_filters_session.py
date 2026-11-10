import copy
import importlib
from pathlib import Path
import random
import sqlite3
import sys
import tempfile
import types
import unittest

if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(Path(__file__).resolve().parents[1]/'cram_studio')];sys.modules['cram_studio']=package
c=importlib.import_module('cram_studio.content')
PracticeSession=importlib.import_module('cram_studio.session').PracticeSession
Store=importlib.import_module('cram_studio.storage').Store

def flash(id_='a'):
    return {'id':id_,'kind':'basic','mode':'flash','clue':'A clue','deck':'Deck','slots':[{'answer':'Answer','answer_html':'Answer','number':1}]}
def exam(id_='a',answers=('Cells',)):
    return {'id':id_,'kind':'cloze','mode':'exam','clue':'(1) _____ (2) _____ (3) _____','deck':'Deck','slots':[{'answer':a,'answer_html':a,'number':i+1,'wrong':['Different A','Different B','Different C'],'choices':[a,'Different A','Different B','Different C'],'correct':0} for i,a in enumerate(answers)]}

class FilterTests(unittest.TestCase):
    def collection(self,ids=(1,3)):
        db=sqlite3.connect(':memory:');db.executescript('create table cards(id integer,nid integer,did integer,ord integer,due integer,odid integer default 0);create table notes(id integer,mid integer,flds text);create table revlog(id integer,cid integer);')
        for cid,did,due in [(1,10,-2),(2,10,5),(3,11,-1)]:
            db.execute('insert into cards(id,nid,did,ord,due) values(?,?,?,?,?)',(cid,cid,did,0,due));db.execute('insert into notes values(?,?,?)',(cid,2,'A question with context\x1fAnswer '+str(cid)))
        before='\n'.join(db.iterdump());queries=[]
        class DB:
            def all(self,sql,*params):
                if not sql.lower().startswith('select '):raise AssertionError('collection write attempted')
                return db.execute(sql,params).fetchall()
        def find(query):queries.append(query);return list(ids)
        model={'id':2,'name':'Basic','type':0,'flds':[{'name':'Front'},{'name':'Back'}]}
        col=types.SimpleNamespace(db=DB(),decks=types.SimpleNamespace(all_names_and_ids=lambda:[types.SimpleNamespace(id=10,name='Course::Lesson'),types.SimpleNamespace(id=11,name='Other')],get_current_id=lambda:10),models=types.SimpleNamespace(all=lambda:[model]),find_cards=find)
        return col,queries,db,before
    def test_empty_search_all_does_not_call_native_parser(self):
        col,queries,db,before=self.collection()
        out,count=c.snapshot(col,{'decks':['10'],'mode':'flash','shuffle':False,'filters':{'search':''}},{})
        self.assertEqual(count,2);self.assertEqual(len(out['questions']),2);self.assertEqual(queries,[]);self.assertEqual('\n'.join(db.iterdump()),before)
    def test_due_native_results_intersect_decks_and_count_consistently(self):
        col,queries,db,before=self.collection()
        config={'decks':['10'],'mode':'flash','shuffle':False,'filters':{'search':'is:due -rated:1'}}
        out,count=c.snapshot(col,config,{})
        self.assertEqual(count,1);self.assertEqual(out['questions'][0]['cid'],'1')
        self.assertEqual(c.count_matches(col,config)['count'],1);self.assertEqual(queries,['(is:due -rated:1)']*2)
        self.assertEqual('\n'.join(db.iterdump()),before)
    def test_or_search_and_refinements_are_grouped(self):
        query=c.search_query({'filters':{'search':'is:new or is:learn','tag':'School::Biology','note_type':'Basic and reversed','flag':'4'}})
        self.assertEqual(query,'(is:new or is:learn) ("tag:School::Biology") ("note:Basic and reversed") (flag:4)')
        self.assertEqual(c.search_query({'filters':{'flag':'any'}}),'(-flag:0)')
    def test_note_names_with_quotes_and_backslashes_are_escaped(self):
        self.assertEqual(c.search_query({'filters':{'note_type':'A "quote" \\ type'}}),'("note:A \\"quote\\" \\\\ type")')
    def test_invalid_search_is_reported_and_never_falls_back_to_all(self):
        col,_,_,_=self.collection()
        def invalid(query):raise ValueError('Invalid Anki search')
        col.find_cards=invalid
        for fn in (lambda:c.snapshot(col,{'decks':['10'],'filters':{'search':'broken ('}},{}),lambda:c.count_matches(col,{'decks':['10'],'filters':{'search':'broken ('}})):
            with self.assertRaisesRegex(ValueError,'Invalid Anki search'):fn()
    def test_invalid_flag_is_rejected(self):
        with self.assertRaises(ValueError):c.search_query({'filters':{'flag':'99'}})
    def test_filtered_deck_selection_uses_current_location_and_arbitrary_query(self):
        col,queries,db,before=self.collection(ids=(1,2,3));options=[]
        def names(**kwargs):
            options.append(kwargs);return [types.SimpleNamespace(id=10,name='Course::Lesson'),types.SimpleNamespace(id=11,name='Other'),types.SimpleNamespace(id=90,name='My filtered deck')]
        col.decks.all_names_and_ids=names
        db.execute('update cards set did=90 where id=1');before='\n'.join(db.iterdump())
        config={'decks':['90'],'mode':'flash','shuffle':False,'filters':{'search':'is:suspended or prop:lapses>=2'}}
        out,count=c.snapshot(col,config,{})
        self.assertEqual(count,1);self.assertEqual(out['questions'][0]['cid'],'1');self.assertEqual(out['questions'][0]['deck'],'My filtered deck');self.assertEqual(c.count_matches(col,config)['count'],1)
        self.assertTrue(all(option.get('include_filtered') for option in options));self.assertEqual('\n'.join(db.iterdump()),before)
    def test_three_different_c1_answers_have_separate_numbered_slots(self):
        clue,slots=c.cloze_question('A {{c1::cell}} forms {{c1::tissue}} and then {{c1::organs}}.',{1})
        self.assertEqual([s['number'] for s in slots],[1,2,3]);self.assertEqual([s['ordinal'] for s in slots],[1,1,1])
        self.assertEqual([s['answer'] for s in slots],['cell','tissue','organs'])
        self.assertEqual(clue.count('_____________'),3)
        for answer in ('cell','tissue','organs'):self.assertNotIn(answer,clue)
        self.assertEqual(len({c.cache_key({'clue':clue},s,'model') for s in slots}),3)
    def test_matching_cloze_card_is_blanked_before_note_grouping(self):
        m={'id':1,'name':'Cloze','type':1,'flds':[{'name':'Text'}]}
        value='{{c1::one}} {{c1::two}} {{c1::three}} {{c2::context}}'
        out=c.compile_questions([(1,1,10,0,1,value)],{1:m},{10:'Deck'},{'mode':'exam','shuffle':False},{})
        q=out['questions'][0];self.assertEqual(len(q['slots']),3);self.assertIn('context',q['clue'])

class QueueTests(unittest.TestCase):
    def test_default_off_finishes_with_a_mistake(self):
        session=PracticeSession([flash()]);packet=session.submit(0,{'known':False})
        self.assertIsNone(packet['queued']);self.assertEqual(len(session.questions),1)
        summary=session.summary();self.assertEqual(summary['earned'],0);self.assertFalse(summary['repeat_enabled']);self.assertEqual(summary['repeat_attempts'],0)
    def test_miss_returns_later_without_shifting_answered_indices(self):
        session=PracticeSession([flash('a'),flash('b'),flash('c')],True,random.Random(3))
        packet=session.submit(0,{'known':False});position=packet['queued']['position'];self.assertIn(position,(2,3))
        self.assertEqual(session.questions[0]['id'],'a');self.assertEqual(session.questions[1]['id'],'b');self.assertTrue(session.questions[position]['is_retry'])
        self.assertEqual(session.results['0']['earned'],0)
        for i in range(1,len(session.questions)):session.submit(i,{'known':True})
        summary=session.summary();self.assertEqual((summary['earned'],summary['total']),(2,3));self.assertEqual((summary['final_earned'],summary['mastered']),(3,3));self.assertEqual(summary['repeat_attempts'],1)
    def test_one_question_repeats_until_correct_with_no_fake_score_increase(self):
        session=PracticeSession([flash()],True,random.Random(0))
        session.submit(0,{'known':False});session.submit(1,{'known':False});session.submit(2,{'known':True})
        summary=session.summary();self.assertEqual((summary['earned'],summary['total']),(0,1));self.assertEqual(summary['final_earned'],1);self.assertEqual(summary['repeat_attempts'],2)
        self.assertEqual(len(session.originals()),1);self.assertEqual(len(session.originals(True)),1)
    def test_partial_credit_repeats_whole_three_blank_question(self):
        original=exam(answers=('Cells','Tissues','Organs'));copy_=copy.deepcopy(original)
        session=PracticeSession([original],True,random.Random(2));packet=session.submit(0,{'choices':[0,1,0]})
        self.assertEqual(packet['result']['earned'],2);retry=session.questions[1]
        self.assertEqual(len(retry['slots']),3)
        self.assertEqual([s['answer'] for s in retry['slots']],['Cells','Tissues','Organs'])
        self.assertEqual(original,copy_)
        for slot in retry['slots']:self.assertEqual(slot['choices'][slot['correct']],slot['answer'])
        session.submit(1,{'choices':[s['correct'] for s in retry['slots']]});self.assertEqual(session.summary()['earned'],2)
    def test_duplicate_grade_does_not_add_another_retry(self):
        session=PracticeSession([flash()],True);session.submit(0,{'known':False});packet=session.submit(0,{'known':True})
        self.assertEqual(len(session.questions),2);self.assertIsNone(packet['queued']);self.assertEqual(packet['result']['earned'],0)
    def test_insertion_position_is_random_within_remaining_queue(self):
        positions=set()
        for seed in range(12):
            session=PracticeSession([flash(str(i)) for i in range(6)],True,random.Random(seed))
            positions.add(session.submit(0,{'known':False})['queued']['position'])
        self.assertGreater(len(positions),1);self.assertTrue(all(2<=p<=6 for p in positions))
    def test_cannot_skip_current_question_or_finish_early(self):
        session=PracticeSession([flash('a'),flash('b')],True)
        with self.assertRaises(ValueError):session.submit(1,{'known':True})
        with self.assertRaises(ValueError):session.summary()
    def test_dont_know_grades_every_blank_as_wrong(self):
        session=PracticeSession([exam(answers=('A','B','C'))]);result=session.submit(0,{'unknown':True})['result']
        self.assertEqual((result['earned'],result['total']),(0,3));self.assertEqual(result['correct'],[False,False,False])
    def test_image_retry_preserves_the_same_mask_group(self):
        io=dict(flash(),kind='io',picture='<svg><rect class="mask target"/><rect class="mask inactive"/></svg>',mask_count=1)
        session=PracticeSession([io],True);session.submit(0,{'known':False});retry=session.questions[1]
        self.assertEqual(retry['picture'],io['picture']);self.assertEqual(retry['mask_count'],1)
    def test_default_migration_and_saved_repeat_setting(self):
        with tempfile.TemporaryDirectory() as td:
            store=Store(td);self.assertFalse(store.data['preferences']['repeat_mistakes'])
            store.data.pop('preferences');store.put({'cached':['A','B','C']})
            migrated=Store(td);self.assertFalse(migrated.data['preferences']['repeat_mistakes']);self.assertIn('cached',migrated.cache())
            migrated.data['preferences']['repeat_mistakes']=True;migrated.save();self.assertTrue(Store(td).data['preferences']['repeat_mistakes'])

if __name__=='__main__':unittest.main()
