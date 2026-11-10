"""The real skin/controller against a native-reviewer spy. No scheduler emulation."""
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from concurrent.futures import Future

if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(Path(__file__).resolve().parents[1]/'cram_studio')];sys.modules['cram_studio']=package
l=importlib.import_module('cram_studio.live_review')
s=importlib.import_module('cram_studio.storage')

def model(kind='Basic'):
    if kind=='Cloze':return {'id':2,'name':kind,'type':1,'flds':[{'name':'Text'},{'name':'Back Extra'}],'tmpls':[{'qfmt':'{{cloze:Text}}'}]}
    return {'id':1,'name':'Basic (and reversed card)','type':0,'flds':[{'name':'Front'},{'name':'Back'}],'tmpls':[{'qfmt':'{{Front}}'},{'qfmt':'{{Back}}'}]}
class Card:
    def __init__(self,cid=1,ordinal=0,kind='Basic'):
        self.id=cid;self.ord=ordinal;self.did=90;self.fields=['Short front','The much longer back answer'] if kind=='Basic' else ['{{c1::life}} is {{c2::good}}','Extra'];self.model=model(kind)
        self.n=types.SimpleNamespace(id=100+cid,fields=self.fields,note_type=lambda:self.model)
    def note(self):return self.n
    def question(self):return 'Original native question'
class Collection:
    def __init__(self,filtered=False,resched=False):
        self.deck={'id':90,'name':'Statistics','dyn':int(filtered),'resched':resched}
        self.decks=types.SimpleNamespace(current=lambda:self.deck)
    @property
    def sched(self):raise AssertionError('The skin must not access the scheduler')
    @property
    def db(self):raise AssertionError('The skin must not write/read a replacement card queue')
class Environment:
    def __init__(self,path,filtered=False,resched=False):
        self.calls=[];self.background=[];self.web=[];self.col=Collection(filtered,resched)
        reviewer=types.SimpleNamespace(card=Card(),state='question',web=types.SimpleNamespace(eval=self.web.append),_mungeQA=lambda text:text)
        self.mw=types.SimpleNamespace(state='overview',col=self.col,reviewer=reviewer,pm=types.SimpleNamespace(profileFolder=lambda:path),
            overview=types.SimpleNamespace(_linkHandler=self.study),onEditCurrent=lambda:self.calls.append('edit'),onBrowse=lambda:self.calls.append('browse'),undo=lambda:self.calls.append('native undo'),
            moveToState=self.state,taskman=types.SimpleNamespace(run_in_background=lambda work,done,*,uses_collection=True:self.background.append((work,done))))
        self.blank_keys={}
        def shortcut_factory(key,callback):
            item=types.SimpleNamespace(enabled=False,deleted=False,callback=callback)
            item.setEnabled=lambda value:setattr(item,'enabled',value)
            item.deleteLater=lambda:setattr(item,'deleted',True)
            self.blank_keys[key]=item;return item
        self.live=l.LiveReviewer(self.mw,'cram_studio',shortcut_factory=shortcut_factory,
            network_runner=lambda mw,work,done:mw.taskman.run_in_background(work,done,uses_collection=False))
    def study(self,command):self.calls.append(command);self.mw.state='review'
    def state(self,state):self.calls.append(state);self.live.state_change(state,self.mw.state);self.mw.state=state
    def packet(self,side='reviewQuestion'):
        self.mw.reviewer.state='answer' if side=='reviewAnswer' else 'question'
        return self.live.card_html('<b>Original Anki HTML</b>',self.mw.reviewer.card,side)
    def message(self,action,**override):
        p=self.live.current
        return self.live.message((False,None),'cram_live:'+json.dumps({'action':action,'cid':p['cid'],'epoch':p['epoch'],**override}),self.mw.reviewer)

class NativeReviewTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.addCleanup(s.clear_profile_stores)
    def test_opt_in_and_same_study_now_entry_without_queue_or_deck_mutation(self):
        for filtered,resched in ((False,False),(True,False),(True,True)):
            e=Environment(self.tmp.name,filtered,resched);before=copy.deepcopy(e.col.deck)
            self.assertEqual(e.packet(),'<b>Original Anki HTML</b>')
            e.mw.state='overview';e.live.begin('flash');self.assertEqual(e.calls,['study'])
            html=e.packet();self.assertIn('ANKI CRAM',html);self.assertEqual(e.col.deck,before)
            self.assertEqual(e.live.current['display'],'flash')
            self.assertIn('Original Anki HTML',e.packet('reviewAnswer'))
            if filtered:self.assertIn('rescheduling '+('on' if resched else 'off'),html)
    def test_basic_and_reverse_follow_actual_card_instead_of_shorter_field(self):
        e=Environment(self.tmp.name)
        a=l.review_question(Card(ordinal=0),e.live.store,e.col);b=l.review_question(Card(ordinal=1),e.live.store,e.col)
        self.assertEqual(a['slots'][0]['answer'],'The much longer back answer');self.assertEqual(a['clue'],'Short front')
        self.assertEqual(b['slots'][0]['answer'],'Short front');self.assertEqual(b['clue'],'The much longer back answer')
    def test_cloze_tests_only_current_ordinal(self):
        e=Environment(self.tmp.name)
        for ordinal,answer,context in ((0,'life','good'),(1,'good','life')):
            q=l.review_question(Card(ordinal=ordinal,kind='Cloze'),e.live.store,e.col)
            self.assertEqual([slot['answer'] for slot in q['slots']],[answer]);self.assertIn(context,q['clue']);self.assertNotIn(answer,q['clue'])
    def test_typed_and_unmapped_custom_notes_preserve_native_flashcards(self):
        e=Environment(self.tmp.name);card=Card();card.model['tmpls'][0]['qfmt']='{{Front}}{{type:Back}}'
        self.assertIsNone(l.review_question(card,e.live.store,e.col))
        typed=Card(ordinal=1,kind='Cloze');typed.model['tmpls'][0]['qfmt']='{{cloze:Text}}{{type:cloze:Text}}';self.assertIsNone(l.review_question(typed,e.live.store,e.col))
        scripted=Card();scripted.model['tmpls'][0]['qfmt']='{{Front}}<script>customCardSetup()</script>';self.assertIsNone(l.review_question(scripted,e.live.store,e.col))
        scripted_back=Card();scripted_back.model['tmpls'][0]['afmt']='{{Back}}<script>customAnswerSetup()</script>';self.assertIsNone(l.review_question(scripted_back,e.live.store,e.col))
        card.model['name']='A custom template';card.model['tmpls'][0]['qfmt']='{{Front}}';self.assertIsNone(l.review_question(card,e.live.store,e.col))
    def test_supported_flashcards_use_same_cloze_slots_but_keep_native_answer_available(self):
        e=Environment(self.tmp.name);e.mw.reviewer.card=Card(kind='Cloze')
        e.mw.reviewer.card.fields[0]='{{c1::life}} is {{c2::good}} and {{c1::brief}}'
        e.live.begin('flash');e.packet();p=e.live.current
        self.assertEqual(p['display'],'flash');self.assertEqual([s['answer'] for s in p['question']['slots']],['life','brief'])
        self.assertIn('good',p['question']['clue']);self.assertIn('(2)',p['question']['clue'])
        self.assertIn('Original Anki HTML',e.packet('reviewAnswer'));self.assertEqual(e.calls,['study'])
    def test_number_keys_are_choices_only_on_question_then_use_original_native_callbacks(self):
        e=Environment(self.tmp.name);e.live.begin('exam');e.packet()
        q=e.live.current['question'];jobs,_=l.prepare_choices([q],{},e.live.store.data['model']);e.live.store.put({job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs});l.attach_choices([q],e.live.store.cache(),e.live.store.data['model'])
        calls=[];space_calls=[];callbacks=[lambda i=i:calls.append(i) for i in range(1,5)];edit=lambda:None;browse=lambda:None;space=lambda:space_calls.append('native Space');undo=lambda:None
        keys=[(str(i),callbacks[i-1]) for i in range(1,5)]+[('e',edit),('b',browse),(' ',space),('Ctrl+Z',undo)]
        e.live.shortcuts('review',keys);keys[1][1]();self.assertEqual(calls,[]);self.assertIn('choose(1)',e.web[-1])
        e.packet('reviewAnswer')
        for _,fn in keys[:4]:fn()
        self.assertEqual(calls,[1,2,3,4]);self.assertIs(keys[4][1],edit);self.assertIs(keys[5][1],browse);keys[6][1]();self.assertEqual(space_calls,['native Space']);self.assertIs(keys[7][1],undo)
    def test_reveal_and_rating_bridge_messages_pass_through_to_anki(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet()
        for message in ('ans','ease1','ease2','ease3','ease4','edit'):
            original=(False,None);self.assertEqual(e.live.message(original,message,e.mw.reviewer),original)
        self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.data['history'],[])
    def test_arrow_shortcuts_route_from_any_native_focus_only_for_ready_mcq(self):
        e=Environment(self.tmp.name);e.live.begin('exam');e.packet();self.assertEqual(e.blank_keys,{})
        q=e.live.current['question'];jobs,_=l.prepare_choices([q],{},e.live.store.data['model'])
        e.live.store.put({job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs});l.attach_choices([q],e.live.store.cache(),e.live.store.data['model']);e.live.emit()
        up=e.blank_keys['Up'];down=e.blank_keys['Down'];self.assertTrue(up.enabled);self.assertTrue(down.enabled)
        # Equivalent to focus being in the native bottom webview: Qt calls the
        # callback, which explicitly targets the main review webview.
        down.callback();self.assertIn('moveBlank(1)',e.web[-1]);up.callback();self.assertIn('moveBlank(-1)',e.web[-1])
        e.packet('reviewAnswer');self.assertFalse(up.enabled);self.assertFalse(down.enabled)
        count=len(e.web);down.callback();self.assertEqual(len(e.web),count);self.assertEqual(e.calls,['study'])
        e.live.close();self.assertTrue(up.deleted);self.assertTrue(down.deleted);self.assertEqual(e.live.blank_shortcuts,{})
    def test_arrow_shortcuts_disable_on_flash_fallback_and_leaving_review(self):
        e=Environment(self.tmp.name);e.live.begin('exam');e.packet();q=e.live.current['question']
        q['ready']=True;e.live.emit();keys=list(e.blank_keys.values());self.assertTrue(all(k.enabled for k in keys))
        e.message('flash');self.assertFalse(any(k.enabled for k in keys));e.state('overview');self.assertFalse(any(k.enabled for k in keys))
    def test_edit_browse_and_undo_delegate_to_native_handlers(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet()
        for action in ('edit','browse','undo'):self.assertEqual(e.message(action),(True,None))
        self.assertEqual(e.calls,['study','edit','browse','native undo'])
        # Anki selects the undone card itself; the hook skins that card and clears picks.
        old=e.live.current['epoch'];e.mw.reviewer.card=Card(cid=2);e.packet();self.assertEqual(e.live.current['cid'],'2');self.assertGreater(e.live.current['epoch'],old)
    def test_regular_study_and_browser_preview_are_unchanged_after_exit(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet();e.message('exit')
        self.assertFalse(e.live.active);e.mw.state='review';self.assertEqual(e.packet(),'<b>Original Anki HTML</b>')
        e.live.active=True;self.assertEqual(e.live.card_html('Preview',e.mw.reviewer.card,'previewQuestion'),'Preview')
    def test_edit_invalidates_only_changed_content_not_schedule(self):
        e=Environment(self.tmp.name);e.live.begin('exam');e.packet();epoch=e.live.current['epoch']
        e.mw.reviewer.card.fields[1]='Corrected answer';e.packet('reviewAnswer')
        self.assertGreater(e.live.current['epoch'],epoch);self.assertEqual(e.live.current['question']['slots'][0]['answer'],'Corrected answer');self.assertEqual(e.col.deck['resched'],False)
    def test_text_size_is_a_shared_display_preference_without_answering(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet()
        e.message('text_zoom',value=1.6)
        self.assertEqual(e.live.store.data['preferences']['text_zoom'],1.6)
        self.assertEqual(e.live.current['text_zoom'],1.6)
        e.mw.reviewer.card=Card(cid=2);e.packet()
        self.assertEqual(e.live.current['text_zoom'],1.6)
        e.message('text_zoom',value=9)
        self.assertEqual(e.live.store.data['preferences']['text_zoom'],1.6)
        self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.data['history'],[])
    def test_interface_zoom_restores_both_webviews_on_exit(self):
        e=Environment(self.tmp.name);top=[1.1];bottom=[1.25]
        e.mw.reviewer.web.zoomFactor=lambda:top[0]
        e.mw.reviewer.web.setZoomFactor=lambda value:top.__setitem__(0,value)
        e.mw.bottomWeb=types.SimpleNamespace(zoomFactor=lambda:bottom[0],setZoomFactor=lambda value:bottom.__setitem__(0,value))
        e.live.begin('flash');e.packet();e.message('view_zoom',delta=.1)
        self.assertAlmostEqual(top[0],1.2);self.assertAlmostEqual(bottom[0],1.35)
        e.message('view_zoom',reset=True);self.assertEqual(top[0],1);self.assertEqual(bottom[0],1)
        e.message('exit');self.assertEqual(top[0],1.1);self.assertEqual(bottom[0],1.25)
        self.assertEqual(e.live.view_zooms,[]);self.assertEqual(e.calls,['study','overview'])
    def test_filtered_schedule_label_distinguishes_native_preview_from_live_reviews(self):
        for resched in (False,True):
            e=Environment(self.tmp.name,True,resched);e.live.begin('flash');html=e.packet()
            self.assertIn('Ratings update your schedule' if resched else 'Anki preview, schedule unchanged',html)
            self.assertEqual(e.col.deck['resched'],resched)
    def test_fullscreen_hover_suppresses_menu_only_during_anki_cram(self):
        for mode in ('flash','exam'):
            e=Environment(self.tmp.name);menus=[];original=lambda:menus.append('show')
            e.mw.fullscreen=True;e.mw.show_menubar=original;e.mw.hide_menubar=lambda:menus.append('hide')
            e.live.begin(mode);self.assertEqual(menus,['hide'])
            e.mw.show_menubar();self.assertEqual(menus,['hide','hide'])
            # Anki's shared fullscreen flag can also refer to another window.
            e.mw.isFullScreen=lambda:False;e.mw.show_menubar();self.assertEqual(menus[-1],'show')
            del e.mw.isFullScreen
            # F11 exits through Anki's own action and restores its normal menu.
            e.mw.fullscreen=False;e.mw.show_menubar();self.assertEqual(menus[-1],'show')
            e.mw.fullscreen=True;e.state('overview');self.assertIs(e.mw.show_menubar,original)
            e.mw.show_menubar();self.assertEqual(menus[-1],'show')
            self.assertFalse(e.live.active);self.assertEqual(e.calls,['study','overview'])
    def test_fullscreen_guard_restores_on_profile_close_and_failed_start(self):
        e=Environment(self.tmp.name);original=lambda:None
        e.mw.show_menubar=original;e.mw.hide_menubar=lambda:None;e.mw.fullscreen=True
        e.live.begin('flash');e.live.close();self.assertIs(e.mw.show_menubar,original)
        e.mw.state='overview'
        def fail(command):raise ValueError('Native Study Now failed')
        e.mw.overview._linkHandler=fail
        with self.assertRaisesRegex(ValueError,'Native Study Now'):e.live.begin('exam')
        self.assertIs(e.mw.show_menubar,original);self.assertFalse(e.live.active)
    def test_fullscreen_guard_preserves_later_addon_wrappers(self):
        e=Environment(self.tmp.name);calls=[]
        e.mw.show_menubar=lambda:calls.append('native show');e.mw.hide_menubar=lambda:calls.append('hide');e.mw.fullscreen=True
        e.live.begin('flash');guard=e.mw.show_menubar
        def another_addon():calls.append('other addon');return guard()
        e.mw.show_menubar=another_addon;e.state('overview')
        self.assertIs(e.mw.show_menubar,another_addon)
        e.mw.show_menubar();self.assertEqual(calls[-2:],['other addon','native show'])
    def test_clean_header_in_both_modes_has_only_exit_and_preserves_deck_status(self):
        for mode in ('flash','exam'):
            e=Environment(self.tmp.name,True,False);e.live.begin(mode);html=e.packet()
            self.assertIn('class="cl-context"',html);self.assertIn('Statistics',html);self.assertIn('rescheduling off',html)
            self.assertIn('aria-label="Exit ANKI CRAM"',html)
            for action in ('edit','browse','undo','keys','text-minus','text-plus','text-reset'):
                self.assertNotIn('data-live-action="'+action+'"',html)
    def test_stale_web_commands_cannot_edit_another_card(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet();e.message('edit',epoch=-1)
        self.assertEqual(e.calls,['study'])
    def test_assets_are_scoped_and_native_bottom_html_is_never_replaced(self):
        e=Environment(self.tmp.name);content=types.SimpleNamespace(css=[],js=[],body='Native answer buttons and intervals')
        e.live.web_content(content,object());self.assertEqual(content.css,[])
        e.live.web_content(content,e.mw.reviewer)
        self.assertEqual([Path(p).name for p in content.js],['appearance.js','writing.js','live.js'])
        self.assertEqual([Path(p).name for p in content.css],['live.css','appearance.css','writing.css'])
        bottom=types.SimpleNamespace(reviewer=e.mw.reviewer);e.live.web_content(content,bottom);self.assertEqual(len(content.css),3)
        e.live.begin('flash');e.live.web_content(content,bottom);self.assertEqual(len(content.css),4);self.assertEqual(content.body,'Native answer buttons and intervals')
    def test_profile_store_is_shared_but_practice_history_is_not_used_by_native_review(self):
        e=Environment(self.tmp.name);self.assertIs(e.live.store,s.profile_store(self.tmp.name));e.live.begin('flash');e.packet();e.packet('reviewAnswer');self.assertEqual(e.live.store.data['history'],[])
    def test_background_choices_do_not_answer_card_and_stale_result_cannot_replace_next_card(self):
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam');e.packet()
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):
                e.mw.reviewer.card=Card(cid=2);e.packet()
                return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original)
        e.message('generate');self.assertTrue(e.live.busy);work,done=e.background[0]
        old_epoch=e.live.current['epoch'];future=Future()
        try:future.set_result(work())
        except Exception as error:future.set_exception(error)
        new_epoch=e.live.current['epoch'];done(future)
        self.assertGreater(new_epoch,old_epoch);self.assertEqual(e.live.current['epoch'],new_epoch);self.assertEqual(e.live.current['cid'],'2');self.assertEqual(e.calls,['study']);self.assertTrue(e.live.store.cache())
    def test_manual_request_on_next_card_resumes_after_cancelled_inflight_request(self):
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam');e.packet();attempts=[]
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):
                attempts.append(1)
                if len(attempts)==1:
                    e.mw.reviewer.card=Card(cid=2);e.mw.reviewer.card.fields[1]='A different answer';e.packet();e.message('generate')
                return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original)
        e.message('generate')
        for index in range(2):
            work,done=e.background[index];future=Future()
            try:future.set_result(work())
            except Exception as error:future.set_exception(error)
            done(future)
        self.assertEqual(len(attempts),2);self.assertTrue(e.live.current['question']['ready']);self.assertFalse(e.live.current['generating']);self.assertEqual(e.live.current['cid'],'2');self.assertEqual(e.calls,['study'])


class NativeFlashSpaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.addCleanup(s.clear_profile_stores)
    def test_space_routes_to_flash_flip_before_and_after_reveal_without_rating(self):
        for filtered,resched in ((False,False),(True,False),(True,True)):
            with self.subTest(filtered=filtered,resched=resched):
                e=Environment(self.tmp.name,filtered,resched);e.live.begin('flash');e.packet();deck=copy.deepcopy(e.col.deck)
                calls=[];keys=[(' ',lambda:calls.append('native Space')),('1',lambda:calls.append('Again')),('Ctrl+Z',lambda:calls.append('undo'))]
                e.live.shortcuts('review',keys);keys[0][1]();self.assertEqual(calls,[]);self.assertIn('cramNative.flip(',e.web[-1])
                e.packet('reviewAnswer')
                for _ in range(5):keys[0][1]()
                self.assertEqual(calls,[]);self.assertEqual(e.live.current['side'],'answer');self.assertEqual(e.col.deck,deck)
                keys[1][1]();keys[2][1]();self.assertEqual(calls,['Again','undo']);self.assertEqual(e.calls,['study'])
    def test_space_switches_dynamically_but_other_modes_and_image_occlusion_delegate(self):
        e=Environment(self.tmp.name);e.live.begin('exam');e.packet();calls=[];keys=[('Space',lambda:calls.append('native Space'))]
        e.live.shortcuts('review',keys);keys[0][1]();self.assertEqual(calls,[]);self.assertIn('cramNative.reveal(',e.web[-1])
        e.message('switch_mode',mode='flash');keys[0][1]();self.assertEqual(calls,[]);self.assertIn('cramNative.flip(',e.web[-1])
        e.packet('reviewAnswer');e.message('switch_mode',mode='write');keys[0][1]();self.assertEqual(len(calls),1)
        e.live.current.update(mode='flash',display='io');e.live.mode='flash';keys[0][1]();self.assertEqual(len(calls),2)
        e.live.current.update(mode='exam',display='native');e.live.mode='exam';keys[0][1]();self.assertEqual(len(calls),3)

    def test_exam_space_requests_reveal_without_rating_and_answer_space_stays_native(self):
        for filtered,resched in ((False,False),(True,False),(True,True)):
            with self.subTest(filtered=filtered,resched=resched):
                e=Environment(self.tmp.name,filtered,resched);e.live.begin('exam');e.packet();deck=copy.deepcopy(e.col.deck)
                calls=[];keys=[(' ',lambda:calls.append('native Space')),('1',lambda:calls.append('Again')),('Ctrl+Z',lambda:calls.append('undo'))]
                e.live.shortcuts('review',keys);keys[0][1]();self.assertEqual(calls,[]);self.assertIn('cramNative.reveal()',e.web[-1])
                e.live.overlay_focus=True;before=len(e.web);keys[0][1]();self.assertEqual(len(e.web),before)
                e.live.overlay_focus=False;e.packet('reviewAnswer');keys[0][1]();keys[1][1]();keys[2][1]()
                self.assertEqual(calls,['native Space','Again','undo']);self.assertEqual(e.col.deck,deck);self.assertEqual(e.calls,['study'])
    def test_space_outside_anki_cram_and_modified_space_keep_native_callbacks(self):
        e=Environment(self.tmp.name);calls=[];original=lambda:calls.append('native');modified=lambda:calls.append('modified')
        keys=[(' ',original),('Ctrl+Space',modified)];e.live.shortcuts('review',keys);self.assertIs(keys[0][1],original)
        e.live.begin('flash');e.packet();e.live.shortcuts('review',keys);self.assertIs(keys[1][1],modified)
        e.state('overview');keys[0][1]();self.assertEqual(calls,['native'])
        e.live.active=True;e.mw.state='review';e.live.current=None;keys[0][1]();self.assertEqual(calls,['native','native'])

class NativeModeSwitchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.addCleanup(s.clear_profile_stores)
    def test_modes_change_current_presentation_only_in_normal_and_filtered_reviews(self):
        for filtered,resched in ((False,False),(True,False),(True,True)):
            for side in ('reviewQuestion','reviewAnswer'):
                with self.subTest(filtered=filtered,resched=resched,side=side):
                    e=Environment(self.tmp.name,filtered,resched);e.live.begin('flash');e.packet()
                    if side=='reviewAnswer':e.packet(side)
                    card=e.mw.reviewer.card;deck=copy.deepcopy(e.col.deck);card_data=copy.deepcopy(card.__dict__)
                    first=e.live.current;card_epoch=first['card_epoch'];epoch=first['epoch']
                    for mode in ('exam','write','flash','write','exam'):
                        e.message('switch_mode',mode=mode);p=e.live.current
                        self.assertEqual(p['cid'],str(card.id));self.assertIs(e.mw.reviewer.card,card)
                        self.assertEqual(p['side'],'answer' if side=='reviewAnswer' else 'question')
                        self.assertEqual(e.mw.reviewer.state,p['side']);self.assertEqual(p['display'],mode)
                        self.assertEqual(p['card_epoch'],card_epoch);self.assertGreater(p['epoch'],epoch);epoch=p['epoch']
                        self.assertIn('cramNative.switchMode(',e.web[-1]);self.assertEqual(e.live.store.data['preferences']['live_mode'],mode)
                    self.assertEqual(e.col.deck,deck);self.assertEqual(card.fields,card_data['fields'])
                    self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.data['history'],[])
    def test_writing_attempts_survive_switch_back_but_new_card_and_undo_start_fresh(self):
        e=Environment(self.tmp.name);e.mw.reviewer.card.fields[1]='<ul><li>banana</li><li>mango</li></ul>'
        e.live.begin('write');e.packet();e.message('write_submit',text='banana',target=0)
        old=copy.deepcopy(e.live.current);self.assertEqual(old['writing_state']['accepted'],[0])
        e.message('switch_mode',mode='exam');e.message('switch_mode',mode='write')
        self.assertEqual(e.live.current['writing_events'],old['writing_events']);self.assertEqual(e.live.current['writing_state'],old['writing_state'])
        e.packet();self.assertEqual(e.live.current['writing_events'],[]);self.assertEqual(e.live.mode_packets,{})
        e.mw.reviewer.card=Card(cid=2);e.packet();self.assertEqual(e.live.current['cid'],'2');self.assertEqual(e.live.mode_packets,{})
    def test_old_epoch_actions_and_background_callbacks_cannot_modify_new_mode(self):
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam',True);e.packet();e.message('generate')
        self.assertTrue(e.live.busy);work,done=e.background[0];old_epoch=e.live.current['epoch'];cancel=e.live.cancel
        e.message('switch_mode',mode='write');current=copy.deepcopy(e.live.current)
        self.assertTrue(cancel.is_set());self.assertFalse(e.live.busy)
        future=Future();future.set_result(None);done(future)
        e.message('write_submit',text='The much longer back answer',target=0,epoch=old_epoch)
        self.assertEqual(e.live.current,current);self.assertEqual(e.calls,['study'])
    def test_invalid_modes_stale_sources_and_failed_preference_save_do_not_switch(self):
        e=Environment(self.tmp.name);e.live.begin('flash');e.packet();epoch=e.live.current['epoch']
        e.message('switch_mode',mode='bad');self.assertEqual(e.live.mode,'flash');self.assertEqual(e.live.current['epoch'],epoch)
        e.live.store.save=lambda:(_ for _ in ()).throw(OSError('disk unavailable'))
        e.message('switch_mode',mode='write');self.assertEqual(e.live.mode,'flash');self.assertEqual(e.live.current['epoch'],epoch)
        self.assertEqual(e.live.store.data['preferences'].get('live_mode','flash'),'flash')
        e.mw.reviewer.card.fields[1]='Edited source';e.message('switch_mode',mode='exam')
        self.assertEqual(e.live.mode,'flash');self.assertEqual(e.calls,['study'])
    def test_header_menu_is_scoped_and_overlay_focus_is_cleared_on_next_card(self):
        e=Environment(self.tmp.name);e.live.begin('flash');markup=e.packet()
        self.assertIn('aria-label="Settings"',markup)
        for mode in ('flash','write','exam'):self.assertIn('data-live-mode="'+mode+'"',markup)
        e.message('overlay_focus',open=True);self.assertTrue(e.live.overlay_focus)
        e.packet();self.assertFalse(e.live.overlay_focus)
    def test_switching_from_flashcards_honors_saved_gemini_preparation_preference(self):
        for enabled in (False,True):
            with self.subTest(enabled=enabled):
                e=Environment(self.tmp.name);e.live.store.set_key('test-key')
                e.live.store.data['preferences'].update(live_generate=enabled,live_generate_configured=True)
                e.mw.reviewer.card.fields[:]=['Ethernet sublayers','LLC and MAC']
                e.live.begin('flash',False);e.packet();e.message('switch_mode',mode='write')
                self.assertEqual(e.live.auto_generate,enabled);self.assertEqual(e.live.current['question']['ready'],not enabled)
                if enabled:
                    jobs,_,_=l.writing.attach([e.live.current['question']],{})
                    e.live.store.put({jobs[0]['id']:{'kind':'list','spans':[[0,3],[8,11]],'connectors':[]}})
                    e.message('ready')
                    self.assertTrue(e.live.current['question']['ready']);self.assertEqual(len(e.live.current['question']['writing']['items']),2)
                    self.assertEqual(e.live.current['writing_state']['remaining'],[0,1]);self.assertIn('cramNative.receive(',e.web[-1])

class NativeAutomaticChoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.addCleanup(s.clear_profile_stores)
    def test_switch_to_multiple_choice_can_prepare_choices_after_native_reveal(self):
        e=Environment(self.tmp.name,True,False);e.live.store.set_key('test-key')
        e.live.store.data['preferences'].update(live_generate=True,live_generate_configured=True)
        e.live.begin('flash');e.packet();e.packet('reviewAnswer');card=e.mw.reviewer.card;deck=copy.deepcopy(e.col.deck)
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original)
        e.message('switch_mode',mode='exam');e.message('ready')
        self.assertEqual(len(e.background),1,'already revealed cards still need their choices')
        work,done=e.background[0];future=Future();future.set_result(work());done(future)
        p=e.live.current;self.assertTrue(p['question']['ready']);self.assertEqual(p['side'],'answer');self.assertEqual(p['display'],'exam')
        self.assertEqual(len(p['question']['slots'][0]['choices']),4)
        self.assertIs(e.mw.reviewer.card,card);self.assertEqual(e.col.deck,deck);self.assertEqual(e.calls,['study'])
        self.assertEqual(e.live.store.data['history'],[]);e.message('ready');self.assertEqual(len(e.background),1)
    def test_choice_preparation_in_progress_survives_native_reveal(self):
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original)
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam',True);e.packet();e.message('ready')
        cancel=e.live.cancel;work,done=e.background[0]
        e.packet('reviewAnswer');self.assertFalse(cancel.is_set(),'revealing must not discard pending choices for this card')
        e.message('ready');self.assertEqual(len(e.background),1)
        future=Future();future.set_result(work());done(future)
        self.assertTrue(e.live.current['question']['ready']);self.assertFalse(e.live.current['generating'])
        self.assertEqual(e.live.current['side'],'answer');self.assertEqual(e.calls,['study'])
    def test_revealed_choices_obey_opt_out_and_manual_preparation(self):
        e=Environment(self.tmp.name);e.live.store.get_key=lambda provider=None:'';e.live.begin('flash',False);e.packet();e.packet('reviewAnswer')
        e.message('switch_mode',mode='exam');e.message('ready');self.assertEqual(e.background,[])
        e.message('generate');self.assertTrue(e.live.current['error']);self.assertEqual(e.background,[])
        q=e.live.current['question'];jobs,_=l.prepare_choices([q],{},e.live.store.data['model'])
        e.live.store.put({job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs})
        e.message('generate');self.assertTrue(q['ready']);self.assertEqual(e.background,[])
        self.assertEqual(e.live.current['side'],'answer');self.assertEqual(e.calls,['study'])
    def test_revealed_choice_worker_cannot_replace_another_mode_or_card(self):
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam',True);e.packet();e.packet('reviewAnswer');e.message('ready')
        self.assertEqual(len(e.background),1);_,done=e.background[0];cancel=e.live.cancel
        e.message('switch_mode',mode='write');current=copy.deepcopy(e.live.current)
        self.assertTrue(cancel.is_set());future=Future();future.set_result(None);done(future)
        self.assertEqual(e.live.current,current)
        e.mw.reviewer.card=Card(cid=2);e.packet();current=copy.deepcopy(e.live.current);done(future)
        self.assertEqual(e.live.current,current);self.assertEqual(e.calls,['study'])
    def test_auto_ready_generates_missing_once_without_reveal_or_rating(self):
        e=Environment(self.tmp.name);e.live.store.set_key('test-key');e.live.begin('exam',True);e.packet()
        class Client:
            def __init__(self,*args):pass
            def generate(self,jobs):return {job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs}
        original=l.Gemini;l.Gemini=Client;self.addCleanup(setattr,l,'Gemini',original)
        e.message('ready');e.message('ready');self.assertEqual(len(e.background),1)
        work,done=e.background[0];future=Future();future.set_result(work());done(future)
        self.assertTrue(e.live.current['question']['ready']);self.assertEqual(e.live.current['side'],'question');self.assertEqual(e.calls,['study'])
        e.message('ready');self.assertEqual(len(e.background),1,'cached choices do not regenerate')
    def test_saved_choices_no_key_and_flashcard_paths_do_not_request_network(self):
        e=Environment(self.tmp.name);e.live.store.get_key=lambda provider=None:'';e.live.begin('exam',True);e.packet();e.message('ready')
        self.assertEqual(e.background,[]);self.assertTrue(e.live.current['error']);self.assertEqual(e.calls,['study'])
        question=e.live.current['question'];jobs,_=l.prepare_choices([question],{},e.live.store.data['model'])
        e.live.store.put({job['id']:['Wrong A','Wrong B','Wrong C'] for job in jobs});e.message('ready')
        self.assertTrue(e.live.current['question']['ready']);self.assertEqual(e.background,[])
        e.state('overview');e.live.begin('flash',False);e.packet();e.message('ready');self.assertEqual(e.background,[])

if __name__=='__main__':unittest.main()
