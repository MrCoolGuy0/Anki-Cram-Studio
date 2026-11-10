"""Profile-only appearance, transactional editor and native review isolation."""
import ast
import base64
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
a=importlib.import_module('cram_studio.appearance')
s=importlib.import_module('cram_studio.storage')

class AppearanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=s.Store(self.tmp.name)
    def test_defaults_and_independent_light_dark_flash_exam_palettes(self):
        cfg=a.normalize_appearance({'size':{'width':76.24},'colors':{'light':{'flash':{'card':'#AbCdEf'}},'dark':{'exam':{'accent':'#123456'}}}})
        self.assertEqual(cfg['size'],{'width':76.2,'height':None})
        self.assertEqual(cfg['colors']['light']['flash'],{'card':'#abcdef'})
        self.assertEqual(cfg['colors']['light']['exam'],{})
        self.assertEqual(cfg['colors']['dark']['flash'],{})
        self.assertEqual(cfg['colors']['dark']['exam'],{'accent':'#123456'})
    def test_question_layout_and_choice_font_roundtrip_without_resetting_other_preferences(self):
        self.store.data['preferences']['text_zoom']=.6
        cfg=a.save_appearance(self.store,{'size':{'width':74},'examSize':{'height':70},'examLayout':{'questionHeight':68.25,'choiceTextSize':21}})
        self.assertEqual(cfg['examLayout'],{'questionHeight':68.2,'choiceTextSize':21})
        restored=s.Store(self.tmp.name)
        self.assertEqual(a.get_appearance(restored),cfg)
        self.assertEqual(restored.data['preferences']['text_zoom'],.6)
        self.assertEqual(cfg['size']['width'],74)
        self.assertEqual(a.normalize_appearance({})['examLayout'],{'questionHeight':60,'choiceTextSize':18})
    def test_invalid_question_layout_is_transactional(self):
        before=copy.deepcopy(self.store.data)
        for value in ([],None,{'questionHeight':True},{'questionHeight':29},{'questionHeight':76},{'choiceTextSize':11},{'choiceTextSize':33},{'choiceTextSize':'18'},{'choiceTextSize':float('nan')}):
            with self.subTest(value=value),self.assertRaises(ValueError):a.save_appearance(self.store,{'examLayout':value})
        self.assertEqual(self.store.data,before)
    def test_multiple_choice_size_is_independent_validated_and_persistent(self):
        cfg=a.save_appearance(self.store,{'size':{'width':70,'height':55},'examSize':{'width':90,'height':75}})
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),cfg)
        self.assertEqual(cfg['size'],{'width':70,'height':55})
        self.assertEqual(cfg['examSize'],{'width':90,'height':75})
        cfg['examSize']={};reset=a.save_appearance(self.store,cfg)
        self.assertEqual(reset['examSize'],{'width':None,'height':None})
        self.assertEqual(reset['size'],{'width':70,'height':55})
        before=copy.deepcopy(self.store.data)
        for size in ([],{'height':True},{'height':float('nan')},{'width':101},{'height':29},{'width':'70'}):
            with self.subTest(size=size),self.assertRaises(ValueError):a.save_appearance(self.store,{'examSize':size})
        self.assertEqual(self.store.data,before)
        self.assertEqual(a.normalize_appearance({})['examSize'],{'width':None,'height':None})
    def test_invalid_values_never_replace_saved_profile_or_touch_other_data(self):
        before=copy.deepcopy(self.store.data)
        for size in ({'width':True},{'height':float('nan')},{'width':float('inf')},{'width':34},{'height':86},{'height':'60'}):
            with self.subTest(size=size),self.assertRaises(ValueError):a.save_appearance(self.store,{'size':size})
        for color in ('red','#123','url(javascript:bad)','#ffffff;display:none',None):
            with self.subTest(color=color),self.assertRaises(ValueError):a.save_appearance(self.store,{'colors':{'light':{'exam':{'text':color}}}})
        for cfg in (None,[],{'size':[]},{'colors':[]},{'colors':{'dark':None}},{'colors':{'dark':{'flash':[]}}}):
            with self.assertRaises(ValueError):a.save_appearance(self.store,cfg)
        self.assertEqual(self.store.data,before);self.assertFalse((self.store.path/'practice.json').exists())
    def test_profile_roundtrip_reset_and_unrelated_cache_history_preserved(self):
        self.store.data['cache']={'set':{'answer':'private'}};self.store.data['history']=[{'earned':1}]
        self.store.data['preferences']['text_zoom']=1.4;self.store.session_key='not-exported'
        cfg=a.save_appearance(self.store,{'size':{'width':90,'height':60},'colors':{'dark':{'exam':{'background':'#112233'}}}})
        reloaded=s.Store(self.tmp.name);self.assertEqual(a.get_appearance(reloaded),cfg)
        self.assertEqual(reloaded.data['cache'],self.store.data['cache']);self.assertEqual(reloaded.data['history'],self.store.data['history'])
        self.assertEqual(reloaded.data['preferences']['text_zoom'],1.4);self.assertNotIn('not-exported',(self.store.path/'practice.json').read_text())
        a.save_appearance(self.store,{})
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),a.normalize_appearance({}))
        self.assertEqual(self.store.data['preferences']['text_zoom'],1.4)
    def test_corrupt_existing_appearance_falls_back_without_writing(self):
        self.store.data['preferences']['appearance']={'size':{'width':'invalid'}}
        self.assertEqual(a.get_appearance(self.store),a.normalize_appearance({}))
        self.assertEqual(self.store.data['preferences']['appearance']['size']['width'],'invalid')
    def test_question_surface_override_persists_without_affecting_other_palettes(self):
        cfg=a.save_appearance(self.store,{'colors':{'dark':{'exam':{'question':'#112233'}}}})
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),cfg)
        self.assertEqual(cfg['colors']['dark']['exam'],{'question':'#112233'});self.assertEqual(cfg['colors']['light']['exam'],{})
        with self.assertRaises(ValueError):a.save_appearance(self.store,{'colors':{'dark':{'exam':{'question':'url(x)'}}}})
    def test_automatic_palette_and_independent_roles_roundtrip(self):
        roles={'auto':True,'card':'#FfD9dA','answerText':'#123456','answerBackground':'#ddeeff','buttonBackground':'#223344','buttonText':'#ffffff','revealBackground':'#ccbbaa','revealText':'#112233','primaryText':'#eeeeee','selectionText':'#443322','correct':'#138468','correctBackground':'#abcdef','incorrectBackground':'#fedcba'}
        cfg=a.save_appearance(self.store,{'size':{'height':62},'colors':{'light':{'flash':roles},'dark':{'exam':roles}}})
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),cfg)
        self.assertEqual(cfg['colors']['light']['flash'],{key:value.lower() if isinstance(value,str) else value for key,value in roles.items()})
        self.assertEqual(cfg['colors']['light']['exam'],{});self.assertEqual(cfg['colors']['dark']['flash'],{})
        reset=a.save_appearance(self.store,{'size':cfg['size'],'colors':{}})
        self.assertEqual(reset['colors'],a.normalize_appearance({})['colors']);self.assertEqual(reset['size']['height'],62)
    def test_bad_new_roles_and_non_boolean_auto_cannot_write(self):
        before=copy.deepcopy(self.store.data)
        for role in ('answerText','answerBackground','buttonBackground','revealBackground','correctBackground'):
            with self.subTest(role=role),self.assertRaises(ValueError):a.save_appearance(self.store,{'colors':{'dark':{'flash':{role:'url(x)'}}}})
        for value in (1,'true',None,[],{}):
            with self.subTest(value=value),self.assertRaises(ValueError):a.save_appearance(self.store,{'colors':{'light':{'exam':{'auto':value}}}})
        self.assertEqual(self.store.data,before)
        self.assertEqual(a.normalize_appearance({'colors':{'light':{'flash':{'auto':False}}}})['colors']['light']['flash'],{})
    def test_native_bottom_appearance_only_updates_styles_and_cleans_on_exit(self):
        from test_live_review import Environment
        e=Environment(self.tmp.name);bottom=[];e.mw.bottomWeb=types.SimpleNamespace(eval=bottom.append)
        cfg=a.save_appearance(e.live.store,{'colors':{'light':{'flash':{'auto':True,'card':'#ffd9da','revealBackground':'#112233'}}}})
        e.live.begin('flash');e.packet();self.assertIn('cramBottomAppearance',bottom[-1]);self.assertIn('#112233',bottom[-1]);self.assertEqual(e.calls,['study'])
        content=types.SimpleNamespace(css=[],js=[],body='Native buttons, handlers and intervals',head='')
        e.live.web_content(content,types.SimpleNamespace(reviewer=e.mw.reviewer))
        self.assertEqual(content.body,'Native buttons, handlers and intervals');self.assertIn('window.cramBottomConfig=',content.head);self.assertIn('appearance.js',content.js[-1])
        e.live.current['appearance']=a.normalize_appearance({});e.live.emit();self.assertNotIn('#112233',bottom[-1])
        e.state('overview');self.assertIn('"config": {}',bottom[-1]);self.assertIn('"view": ""',bottom[-1]);self.assertEqual(e.calls,['study','overview']);self.assertEqual(e.live.store.data['history'],[])
        s.clear_profile_stores()
    def test_images_roundtrip_draft_reset_and_color_size_independence(self):
        image={'data':'data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\n'+b'local image').decode(),'name':'sample.png','opacity':60,'overlay':25,'smart':True}
        cfg=a.save_appearance(self.store,{'size':{'height':66},'colors':{'light':{'flash':{'card':'#aabbcc'}}},'images':{'background':image,'card':image}})
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),cfg);self.assertEqual(cfg['images']['card'],image)
        cfg['colors']=a.normalize_appearance({})['colors'];reset=a.save_appearance(self.store,cfg)
        self.assertEqual(reset['images']['card'],image);self.assertEqual(reset['size']['height'],66)
        reset.pop('images');reset=a.save_appearance(self.store,reset);self.assertNotIn('images',reset);self.assertEqual(reset['size']['height'],66)
    def test_images_reject_remote_script_invalid_payload_and_bad_controls_without_write(self):
        good='data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\nlocal').decode();before=copy.deepcopy(self.store.data)
        for data in ('https://example.test/a.png','file:///private.jpg','data:image/svg+xml;base64,PHN2Zz4=',good+'$', 'data:image/png;base64,YmFk', 'data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\n'+b'a'*262144).decode()):
            with self.subTest(data=data[:40]),self.assertRaises(ValueError):a.save_appearance(self.store,{'images':{'card':{'data':data}}})
        for key,value in (('opacity',True),('opacity',101),('opacity',float('nan')),('overlay',-1),('overlay','50'),('smart','yes')):
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):a.save_appearance(self.store,{'images':{'card':{'data':good,key:value}}})
        self.assertEqual(self.store.data,before);self.assertNotIn('images',a.normalize_appearance({}))
    def test_image_picker_cancel_and_error_never_save_before_explicit_save(self):
        owner,events,saved,closed=self.editor();scope=owner.bridge.__func__.__globals__;calls=[]
        scope['choose_image']=lambda parent:calls.append(parent)
        owner.bridge('cram_custom:'+json.dumps({'action':'choose-image','target':'card'}))
        self.assertEqual(calls,[owner]);self.assertEqual(events[-1],('image',{'target':'card','image':None}));self.assertEqual(saved,[]);self.assertNotIn('appearance',self.store.data['preferences'])
        owner.bridge('cram_custom:'+json.dumps({'action':'choose-image','target':'other'}));self.assertEqual(events[-1][0],'error');self.assertEqual(len(calls),1)
        def fail(parent):raise ValueError('Invalid image')
        scope['choose_image']=fail;owner.bridge('cram_custom:'+json.dumps({'action':'choose-image','target':'background'}));self.assertEqual(events[-1],('error','Invalid image'));self.assertEqual(saved,[]);self.assertEqual(closed,[])
    def test_native_bottom_appearance_does_not_copy_image_payloads(self):
        from test_live_review import Environment
        e=Environment(self.tmp.name);bottom=[];e.mw.bottomWeb=types.SimpleNamespace(eval=bottom.append)
        image={'data':'data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\nlocal').decode()}
        a.save_appearance(e.live.store,{'images':{'card':image}});e.live.begin('flash');e.packet()
        self.assertIn('images',e.live.current['appearance']);self.assertNotIn('base64',bottom[-1]);self.assertNotIn('images',bottom[-1]);self.assertEqual(e.calls,['study'])
        content=types.SimpleNamespace(css=[],js=[],head='',body='native ratings')
        e.live.web_content(content,types.SimpleNamespace(reviewer=e.mw.reviewer));self.assertNotIn('base64',content.head);self.assertEqual(content.body,'native ratings');s.clear_profile_stores()
    def test_harmony_choices_roundtrip_and_reset_preserve_images_size(self):
        image={'data':'data:image/png;base64,'+base64.b64encode(b'\x89PNG\r\n\x1a\nlocal').decode()}
        for harmony in a.HARMONIES:
            cfg=a.save_appearance(self.store,{'size':{'height':60},'images':{'card':image},'colors':{'light':{'flash':{'auto':True,'card':'#ffd9da','harmony':harmony,'answerText':'#123456'}},'dark':{'exam':{'auto':True,'harmony':harmony}}}})
            self.assertEqual(a.get_appearance(s.Store(self.tmp.name)),cfg)
            self.assertEqual(cfg['colors']['light']['flash']['harmony'],harmony);self.assertEqual(cfg['colors']['dark']['exam']['harmony'],harmony)
            self.assertEqual(cfg['colors']['light']['exam'],{});self.assertEqual(cfg['colors']['dark']['flash'],{})
        cfg['colors']=a.normalize_appearance({})['colors'];reset=a.save_appearance(self.store,cfg);self.assertIn('images',reset);self.assertEqual(reset['size']['height'],60);self.assertNotIn('harmony',reset['colors']['light']['flash'])
    def test_invalid_harmony_never_writes_and_current_keeps_legacy_schema(self):
        before=copy.deepcopy(self.store.data)
        for invalid in ('rainbow','triadic;display:none',None,True,1,[],{}):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):a.save_appearance(self.store,{'colors':{'light':{'flash':{'harmony':invalid}}}})
        self.assertEqual(self.store.data,before)
        self.assertEqual(a.normalize_appearance({'colors':{'light':{'flash':{'auto':True,'harmony':'current'}}}})['colors']['light']['flash'],{'auto':True})
    def test_disk_failure_rolls_back_in_memory_draft(self):
        original=self.store.save
        def fail():raise OSError('Disk full')
        self.store.save=fail
        with self.assertRaises(OSError):a.save_appearance(self.store,{'size':{'height':60}})
        self.assertNotIn('appearance',self.store.data['preferences'])
        self.store.save=original;a.save_appearance(self.store,{'size':{'height':55}});self.store.save=fail
        with self.assertRaises(OSError):a.save_appearance(self.store,{'size':{'height':60}})
        self.assertEqual(a.get_appearance(self.store)['size']['height'],55)
        self.assertEqual(a.get_appearance(s.Store(self.tmp.name))['size']['height'],55)
    def editor(self):
        tree=ast.parse((ROOT/'cram_studio/customize.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='bridge')
        namespace={'json':json,'get_appearance':a.get_appearance,'save_appearance':a.save_appearance,'theme_manager':types.SimpleNamespace(night_mode=True)}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'<customizer-bridge>','exec'),namespace)
        events=[];saved=[];closed=[]
        owner=types.SimpleNamespace(store=self.store,closed=False,assets='http://127.0.0.1/_addons/cram_studio/web/',emit=lambda e,d:events.append((e,d)),on_saved=saved.append,accept=lambda:closed.append('save'),reject=lambda:closed.append('cancel'))
        owner.bridge=types.MethodType(namespace['bridge'],owner)
        return owner,events,saved,closed
    def test_editor_ready_and_cancel_do_not_persist_preview_edits(self):
        owner,events,saved,closed=self.editor();owner.bridge('cram_custom:'+json.dumps({'action':'ready'}))
        self.assertEqual(events[-1][0],'load');self.assertTrue(events[-1][1]['dark'])
        owner.bridge('cram_custom:'+json.dumps({'action':'cancel'}))
        self.assertEqual(closed,['cancel']);self.assertEqual(saved,[]);self.assertNotIn('appearance',self.store.data['preferences'])
    def test_editor_save_validates_before_callback_and_closing(self):
        owner,events,saved,closed=self.editor()
        owner.bridge('cram_custom:'+json.dumps({'action':'save','config':{'size':{'height':900}}}))
        self.assertEqual(events[-1][0],'error');self.assertEqual(saved,[]);self.assertEqual(closed,[])
        owner.bridge('cram_custom:'+json.dumps({'action':'save','config':{'size':{'height':66}}}))
        self.assertEqual(closed,['save']);self.assertEqual(saved,[a.get_appearance(self.store)])
        owner.closed=True;owner.bridge('cram_custom:'+json.dumps({'action':'save','config':{}}))
        self.assertEqual(a.get_appearance(self.store)['size']['height'],66)
    def test_saving_while_native_reviewing_keeps_card_epoch_and_anki_state(self):
        from test_live_review import Environment
        e=Environment(self.tmp.name,True,False);e.live.begin('exam');e.packet()
        before=copy.deepcopy(e.live.current);deck=copy.deepcopy(e.col.deck);events=[]
        cfg=a.save_appearance(e.live.store,{'size':{'height':65},'colors':{'light':{'exam':{'card':'#fafafa'}}}})
        tree=ast.parse((ROOT/'cram_studio/__init__.py').read_text())
        method=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='appearance_saved')
        ns={'window':types.SimpleNamespace(closed=False,emit=lambda *args:events.append(args)),'live':e.live}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'<save-notification>','exec'),ns)
        ns['appearance_saved'](cfg)
        expected=copy.deepcopy(before);expected['appearance']=cfg
        self.assertEqual(e.live.current,expected);self.assertEqual(events,[('appearance',cfg)])
        self.assertEqual(e.col.deck,deck);self.assertEqual(e.calls,['study']);self.assertEqual(e.live.store.data['history'],[])
        s.clear_profile_stores()

if __name__=='__main__':unittest.main()
