"""Automatic visual-answer fallback; no network, real collection or scheduler."""
import copy
import tempfile
import unittest
from test_core import c, model, compile_
from test_live_review import Environment, Card, s
from cram_studio import writing
from cram_studio.session import PracticeSession

IMAGE='<img src="formula screenshot.png" alt="Formula">'

class ImageAnswerTests(unittest.TestCase):
    def test_main_image_answer_in_every_mode_keeps_original_and_needs_no_ai(self):
        for mode in ('flash','exam','write','mixed'):
            for answer in (IMAGE,'<p>The formula:</p>'+IMAGE):
                with self.subTest(mode=mode,answer=answer):
                    q=compile_([(1,1,10,0,2,'Which formula should be used?\x1f'+answer)],
                               {2:model(2,'Basic',('Front','Back'),0)},mode)['questions'][0]
                    self.assertEqual(q['mode'],'flash');self.assertTrue(q['image_answer'])
                    self.assertIn(IMAGE,q['slots'][0]['answer_html']);self.assertNotIn('<img',q['clue'])
                    self.assertEqual(c.prepare_choices([q],{},'model'),([],0))
                    self.assertEqual(writing.attach([q],{})[0],[])

    def test_image_cloze_is_a_hidden_slot_and_only_current_ordinal_falls_back(self):
        text='Use {{c1::this method}} with {{c2::'+IMAGE+'}}.'
        qs=compile_([(1,1,10,0,1,text+'\x1f'),(2,1,10,1,1,text+'\x1f')],{1:model()},'exam')['questions']
        self.assertEqual(qs[0]['mode'],'exam');self.assertNotIn('image_answer',qs[0])
        image=qs[1];self.assertEqual(image['mode'],'flash');self.assertTrue(image['image_answer'])
        self.assertNotIn('<img',image['clue']);self.assertIn('this method',image['clue'])
        self.assertEqual(image['slots'][0]['answer_html'],IMAGE)

    def test_image_question_with_text_answer_stays_in_requested_mode(self):
        for mode in ('exam','write'):
            q=compile_([(1,1,10,0,2,IMAGE+'<p>Name this formula.</p>\x1fQuadratic formula')],
                       {2:model(2,'Basic',('Front','Back'),0)},mode)['questions'][0]
            self.assertEqual(q['mode'],mode);self.assertNotIn('image_answer',q)

    def test_hidden_image_does_not_change_text_question_mode(self):
        q=compile_([(1,1,10,0,2,'A longer clue\x1fTerm<span hidden>'+IMAGE+'</span>')],
                   {2:model(2,'Basic',('Front','Back'),0)},'exam')['questions'][0]
        self.assertEqual(q['mode'],'exam');self.assertNotIn('<img',q['slots'][0]['answer_html'])

    def test_custom_answer_mapping_retains_image_and_caption(self):
        m=model(3,'Custom',('Prompt','Answer photo','Extra'),0)
        q=c.compile_questions([(1,1,10,0,3,'Prompt\x1f'+IMAGE+'<b>Caption</b>\x1fExtra')],
            {3:m},{10:'Deck'},{'mode':'write','limit':0},
            {'3':{'answer':'Answer photo','clue':'Prompt'}})['questions'][0]
        self.assertEqual(q['mode'],'flash');self.assertIn('<b>Caption</b>',q['slots'][0]['answer_html'])

    def test_main_recall_and_resume_keep_image_without_a_scheduler(self):
        q=compile_([(1,1,10,0,2,'Recall the formula\x1f'+IMAGE)],
                   {2:model(2,'Basic',('Front','Back'),0)},'write')['questions'][0]
        session=PracticeSession([q]);saved=session.snapshot()
        restored=PracticeSession.restore(saved)
        self.assertEqual(restored.questions[0]['mode'],'flash')
        self.assertEqual(restored.questions[0]['slots'][0]['answer_html'],IMAGE)
        self.assertEqual(restored.submit(0,{'known':True})['result']['earned'],1)

    def test_live_auto_flash_keeps_selected_mode_for_next_card_and_native_ratings(self):
        with tempfile.TemporaryDirectory() as td:
            self.addCleanup(s.clear_profile_stores)
            for mode in ('flash','exam','write'):
                for filtered,resched in ((False,False),(True,False),(True,True)):
                    with self.subTest(mode=mode,filtered=filtered,resched=resched):
                        e=Environment(td,filtered,resched);e.mw.reviewer.card.fields[:]=['Which formula?',IMAGE]
                        deck=copy.deepcopy(e.col.deck);e.live.begin(mode,True);e.packet();p=e.live.current
                        self.assertEqual(p['display'],'flash');self.assertEqual(e.live.mode,mode)
                        self.assertTrue(e.live.can_flip_flashcard());e.message('ready')
                        self.assertEqual(e.background,[],'image fallback must not generate choices/groups')
                        native=[];keys=[(' ',lambda:native.append('Space')),('1',lambda:native.append('Again'))]
                        e.live.shortcuts('review',keys);keys[0][1]()
                        self.assertIn('cramNative.flip()',e.web[-1]);self.assertEqual(native,[])
                        e.packet('reviewAnswer');keys[0][1]();self.assertEqual(native,[])
                        keys[1][1]();self.assertEqual(native,['Again'])
                        self.assertEqual(e.col.deck,deck);self.assertEqual(e.calls,['study'])
                        for msg in ('ans','ease1','ease2','ease3','ease4'):
                            self.assertEqual(e.live.message((False,None),msg,e.mw.reviewer),(False,None))
                        e.mw.reviewer.card=Card(cid=2);e.packet()
                        self.assertEqual(e.live.current['display'],mode)
                        e.state('overview');self.assertFalse(e.live.can_flip_flashcard())

    def test_live_mode_switches_cannot_turn_photo_into_empty_writing_or_mcq(self):
        with tempfile.TemporaryDirectory() as td:
            self.addCleanup(s.clear_profile_stores)
            e=Environment(td);e.mw.reviewer.card.fields[:]=['Which formula?',IMAGE]
            e.live.begin('exam');e.packet()
            for mode in ('write','flash','exam','write'):
                e.message('switch_mode',mode=mode)
                self.assertEqual(e.live.current['display'],'flash');self.assertTrue(e.live.can_flip_flashcard())
                self.assertEqual(e.live.current['question']['slots'][0]['answer_html'],IMAGE)
            self.assertEqual(e.calls,['study'])

if __name__=='__main__':unittest.main()
