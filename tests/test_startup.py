"""Exercise the actual dialog startup methods without loading native Qt."""
import ast
import json
from pathlib import Path
import types
import unittest

class StartupTests(unittest.TestCase):
    def environment(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'cram_studio/dialog.py').read_text())
        dialog=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CramDialog')
        methods=[n for n in dialog.body if isinstance(n,ast.FunctionDef) and n.name in ('bootstrap','fail')]
        jobs=[]
        class Query:
            def __init__(self,parent,op,success):self.success=success;jobs.append(self)
            def failure(self,fn):self.failed=fn;return self
            def run_in_background(self):pass
        namespace={'QueryOp':Query,'catalog':lambda col:None,'theme_manager':types.SimpleNamespace(night_mode=False)}
        exec(compile(ast.Module(body=methods,type_ignores=[]),'<startup-methods>','exec'),namespace)
        emitted=[]
        owner=types.SimpleNamespace(closed=False,booting=False,busy=False,initial_deck=None,
            store=types.SimpleNamespace(config=lambda:{'model':'gemini-test','history':[],'preferences':{'repeat_mistakes':False}},get_key=lambda:'',provider_label=lambda:'Google Gemini',saved_sessions=lambda:[]),
            mw=types.SimpleNamespace(serverURL=lambda:'http://127.0.0.1/'),emit=lambda event,data:emitted.append((event,data)))
        for name in ('bootstrap','fail'):setattr(owner,name,types.MethodType(namespace[name],owner))
        return owner,jobs,emitted
    def test_duplicate_startup_is_coalesced_and_success_can_refresh(self):
        owner,jobs,events=self.environment();owner.bootstrap();owner.bootstrap();self.assertEqual(len(jobs),1)
        jobs[0].success({'models':[{'name':'Basic'}],'current':'1','decks':[]})
        self.assertFalse(owner.booting);self.assertEqual(events[0][0],'bootstrap');self.assertEqual(owner.models,[{'name':'Basic'}])
        owner.bootstrap();self.assertEqual(len(jobs),2)
    def test_failed_startup_allows_retry_and_closed_window_stops(self):
        owner,jobs,events=self.environment();owner.bootstrap();jobs[0].failed(ValueError('Collection unavailable'))
        self.assertFalse(owner.booting);self.assertEqual(events,[('error','Collection unavailable')])
        owner.bootstrap();self.assertEqual(len(jobs),2);jobs[1].failed(ValueError('again'));owner.closed=True;owner.bootstrap();self.assertEqual(len(jobs),2)

class LauncherTests(unittest.TestCase):
    def environment(self,state='overview'):
        calls=[];warnings=[];actions=[]
        class Action:
            def __init__(self,label,parent):
                self.label=label;self.keys=[];actions.append(self)
                self.triggered=types.SimpleNamespace(connect=lambda fn:setattr(self,'callback',fn))
            def setObjectName(self,name):self.name=name
            def setShortcuts(self,keys):self.keys=keys
            def setShortcut(self,key):self.keys=[key]
            def setShortcutContext(self,context):self.context=context
            def setAutoRepeat(self,repeat):self.repeat=repeat
        class Collection:
            decks=types.SimpleNamespace(get_current_id=lambda:90)
            @property
            def sched(self):raise AssertionError('Launch shortcuts must not access the scheduler')
        mw=types.SimpleNamespace(state=state,col=Collection(),
            addonManager=types.SimpleNamespace(setWebExports=lambda *args:None),
            form=types.SimpleNamespace(menuTools=types.SimpleNamespace(addAction=lambda action:None)),
            raise_=lambda:calls.append('raise main'),activateWindow=lambda:calls.append('focus main'))
        def move(state):calls.append(state);mw.state=state
        mw.moveToState=move
        namespace={'__name__':'cram_studio','mw':mw,'gui_hooks':types.SimpleNamespace(),
            'QAction':Action,'QKeySequence':lambda key:key,
            'Qt':types.SimpleNamespace(ShortcutContext=types.SimpleNamespace(WindowShortcut='window')),
            'showWarning':lambda message,**kwargs:warnings.append(message)}
        tree=ast.parse((Path(__file__).resolve().parents[1]/'cram_studio/__init__.py').read_text())
        tree.body=[node for node in tree.body if not isinstance(node,(ast.Import,ast.ImportFrom))]
        exec(compile(tree,'<actual-addon-launchers>','exec'),namespace)
        controller=types.SimpleNamespace(dialog=None,is_review=lambda:False,open=lambda:calls.append('setup'))
        namespace['live_controller']=lambda:controller
        namespace['open_cram']=lambda did=None:calls.append(('practice',did))
        return namespace,mw,controller,actions,calls,warnings
    def test_menu_keys_keep_legacy_alias_and_window_scope(self):
        ns,mw,controller,actions,calls,warnings=self.environment()
        main,native=actions[:2]
        self.assertEqual((main.label,main.keys),('MAIN CRAM',['Ctrl+Alt+M','Ctrl+Shift+T']))
        self.assertEqual((native.label,native.keys),('ANKI CRAM',['Ctrl+Alt+A']))
        self.assertEqual((main.context,native.context),('window','window'))
        self.assertFalse(main.repeat);self.assertFalse(native.repeat)
        main.callback(False);native.callback(False)
        self.assertEqual(calls,[('practice',90),'setup']);self.assertEqual(warnings,[])
    def test_deck_list_opens_selected_deck_setup_without_starting_review(self):
        ns,mw,controller,actions,calls,warnings=self.environment('deckBrowser')
        actions[1].callback(False)
        self.assertEqual(calls,['overview','setup']);self.assertEqual(mw.state,'overview')
        self.assertEqual(mw.col.decks.get_current_id(),90);self.assertEqual(warnings,[])
    def test_closed_profile_and_other_states_do_not_launch(self):
        ns,mw,controller,actions,calls,warnings=self.environment('review')
        actions[1].callback(False)
        self.assertEqual(calls,[]);self.assertEqual(len(warnings),1)
        mw.col=None;warnings.clear();actions[1].callback(False)
        self.assertEqual(calls,[]);self.assertEqual(warnings,[])
    def test_existing_setup_or_active_review_is_focused_without_restart(self):
        ns,mw,controller,actions,calls,warnings=self.environment('review')
        ns['live']=controller
        controller.is_review=lambda:True
        actions[1].callback(False)
        self.assertEqual(calls,['raise main','focus main'])
        calls.clear();controller.dialog=types.SimpleNamespace(
            raise_=lambda:calls.append('raise setup'),activateWindow=lambda:calls.append('focus setup'))
        actions[1].callback(False)
        self.assertEqual(calls,['raise setup','focus setup']);self.assertEqual(warnings,[])
    def test_overview_keeps_existing_buttons_with_shortcut_tooltips(self):
        ns,mw,controller,actions,calls,warnings=self.environment()
        links=[];handler=object()
        self.assertIs(ns['overview'](handler,links),handler)
        ns['overview'](handler,links)
        self.assertEqual(links,[])


class LiveChoiceDefaultTests(unittest.TestCase):
    """Actual setup dialog with small Qt spies; no network or reviewer startup."""
    def environment(self,preferences=None):
        import copy
        import importlib
        import tempfile
        storage=importlib.import_module('cram_studio.storage')
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);store=storage.Store(tmp.name)
        store.data['preferences'].update(preferences or {})
        class Signal:
            def connect(self,fn):self.callback=fn
        class Widget:
            def __init__(self,*args):
                self.checked=False;self.enabled=True;self.accepted=Signal();self.rejected=Signal();self.clicked=Signal();self.toggled=Signal()
            def setChecked(self,value):self.checked=bool(value)
            def isChecked(self):return self.checked
            def setEnabled(self,value):self.enabled=value
            def setVisible(self,value):self.visible=value
            def setWindowTitle(self,*args):pass
            def resize(self,*args):pass
            def setSpacing(self,*args):pass
            def addWidget(self,*args):pass
            def setTextFormat(self,*args):pass
            def setWordWrap(self,*args):pass
            def setText(self,*args):pass
            def button(self,*args):return Widget()
            def accept(self):self.saved=True
            def reject(self):self.cancelled=True
        class Buttons(Widget):
            StandardButton=types.SimpleNamespace(Ok=1,Cancel=2)
        namespace={name:Widget for name in ('QDialog','QVBoxLayout','QLabel','QRadioButton','QCheckBox','QPushButton')}
        namespace.update(QDialogButtonBox=Buttons,Qt=types.SimpleNamespace(TextFormat=types.SimpleNamespace(PlainText=0)),
                         filtered_status=lambda deck:'Anki reviews',AISettings=lambda owner:None)
        tree=ast.parse((Path(__file__).resolve().parents[1]/'cram_studio/live_start.py').read_text())
        tree.body=[node for node in tree.body if isinstance(node,ast.ClassDef)]
        exec(compile(tree,'<actual-live-start>','exec'),namespace)
        controller=types.SimpleNamespace(store=store,mw=types.SimpleNamespace(col=types.SimpleNamespace(decks=types.SimpleNamespace(current=lambda:{'name':'Deck'}))))
        before=copy.deepcopy(store.data)
        return namespace['LiveStartDialog'],controller,store,before
    def test_new_and_legacy_defaults_enabled_without_writing_on_open(self):
        for preferences in ({},{'live_generate':False},{'live_generate':True,'live_mode':'exam'}):
            with self.subTest(preferences=preferences):
                Dialog,c,store,before=self.environment(preferences);dialog=Dialog(c)
                self.assertTrue(dialog.auto.isChecked());self.assertEqual(store.data,before)
                self.assertFalse((store.path/'practice.json').exists())
    def test_start_flashcards_keeps_enabled_preference_for_next_mcq_start(self):
        Dialog,c,store,_=self.environment();dialog=Dialog(c)
        self.assertFalse(dialog.auto.enabled);dialog.save()
        self.assertEqual(c.mode,'flash');self.assertFalse(c.auto_generate)
        self.assertTrue(store.data['preferences']['live_generate']);self.assertTrue(store.data['preferences']['live_generate_configured'])
        second=Dialog(c);second.exam.setChecked(True);second.update_choices();self.assertTrue(second.auto.enabled);second.save()
        self.assertEqual(c.mode,'exam');self.assertTrue(c.auto_generate)
    def test_manual_opt_out_persists_through_flashcard_start_and_reopen(self):
        Dialog,c,store,_=self.environment();dialog=Dialog(c);dialog.exam.setChecked(True);dialog.auto.setChecked(False);dialog.save()
        self.assertFalse(c.auto_generate);self.assertFalse(Dialog(c).auto.isChecked())
        flash=Dialog(c);flash.exam.setChecked(False);flash.save()
        self.assertFalse(store.data['preferences']['live_generate']);self.assertFalse(Dialog(c).auto.isChecked())
    def test_cancel_does_not_persist_the_new_default(self):
        Dialog,c,store,before=self.environment({'live_generate':False});dialog=Dialog(c);dialog.reject()
        self.assertEqual(store.data,before);self.assertFalse(hasattr(c,'auto_generate'))

if __name__=='__main__':unittest.main()
