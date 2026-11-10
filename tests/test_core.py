import copy
import importlib
import json
import pathlib
import sqlite3
import sys
import tempfile
import threading
import types
import unittest
import urllib.error

# Load pure modules without importing Anki's GUI entry point.
ROOT=pathlib.Path(__file__).resolve().parents[1]
package=types.ModuleType('cram_studio'); package.__path__=[str(ROOT/'cram_studio')];sys.modules['cram_studio']=package
c=importlib.import_module('cram_studio.content')
g=importlib.import_module('cram_studio.gemini')
s=importlib.import_module('cram_studio.storage')

def model(mid=1,name='Cloze',fields=('Text','Back Extra'),kind=1):
    return {'id':mid,'name':name,'type':kind,'flds':[{'name':n} for n in fields]}
def compile_(rows,models,mode='exam',**cfg):
    return c.compile_questions(rows,models,{10:'Course::Lesson',11:'Course::Other'},{'mode':mode,'shuffle':False,'limit':0,**cfg},{})
class ContentTests(unittest.TestCase):
    def test_exam_multi_blank_order_and_repeated_id(self):
        rows=[(102,7,10,1,1,'{{c1::Cells}} make {{c2::tissue}} and {{c1::organs}}.\x1f') ,(101,7,10,0,1,'{{c1::Cells}} make {{c2::tissue}} and {{c1::organs}}.\x1f')]
        out=compile_(rows,{1:model()})['questions'];self.assertEqual(len(out),2)
        q=out[0];self.assertEqual([v['answer'] for v in q['slots']],['Cells','organs'])
        self.assertNotIn('Cells',q['clue']);self.assertIn('tissue',q['clue']);self.assertIn('(2)',q['clue'])
        self.assertEqual(out[1]['slots'][0]['answer'],'tissue');self.assertIn('Cells',out[1]['clue'])
    def test_flash_cards_do_not_repeat_all_clozes(self):
        value='{{c1::Cells}} make {{c2::tissue}}.\x1f'
        out=compile_([(102,7,10,1,1,value),(101,7,10,0,1,value)],{1:model()},'flash')['questions']
        self.assertEqual([q['slots'][0]['answer'] for q in out],['Cells','tissue'])
        self.assertIn('tissue',out[0]['clue']);self.assertNotIn('Cells',out[0]['clue'])
        self.assertIn('Cells',out[1]['clue']);self.assertNotIn('tissue',out[1]['clue'])
    def test_only_selected_cloze_cards_are_blank(self):
        out=compile_([(1,1,10,1,1,'{{c1::one}} and {{c2::two}}\x1f')],{1:model()})['questions'][0]
        self.assertEqual(out['slots'][0]['answer'],'two');self.assertIn('one',out['clue'])
    def test_nested_cloze_no_double_outer_blank(self):
        clue,slots=c.cloze_question('{{c1::outer {{c2::inner}}}}',{1,2})
        self.assertEqual(len(slots),1);self.assertEqual(slots[0]['answer'],'outer inner')
        clue,slots=c.cloze_question('{{c1::outer {{c2::inner}}}}',{2})
        self.assertIn('outer',clue);self.assertEqual(slots[0]['answer'],'inner')
    def test_basic_auto_reversed_deduplicated(self):
        m=model(2,'Basic (and reversed card)',('Front','Back'),0)
        rows=[(1,1,10,0,2,'A long explanation or clue\x1fShort'),(2,1,10,1,2,'A long explanation or clue\x1fShort')]
        q=compile_(rows,{2:m})['questions'];self.assertEqual(len(q),1);self.assertEqual(q[0]['slots'][0]['answer'],'Short')
        self.assertEqual(q[0]['clue'],'A long explanation or clue')
    def test_custom_mapping_and_basic_override(self):
        m=model(2,'Custom',('Title','Meaning','Example'),0)
        out=c.compile_questions([(1,1,10,0,2,'Term\x1fMeaning\x1fClue')],{2:m},{10:'Deck'},{'mode':'flash','shuffle':False},{'2':{'answer':'Title','clue':'Example'}})['questions'][0]
        self.assertEqual(out['clue'],'Clue');self.assertEqual(out['slots'][0]['answer'],'Term')
        basic=model(3,'Basic',('Front','Back'),0)
        out=c.compile_questions([(1,1,10,0,3,'Long answer in front\x1fClue')],{3:basic},{10:'Deck'},{'mode':'flash','shuffle':False},{'3':{'answer':'Front'}})['questions'][0]
        self.assertEqual(out['slots'][0]['answer'],'Long answer in front')
    def test_hidden_template_script_removed_local_images_kept(self):
        value='<b>Heading</b><script>leak()</script><span hidden>Secret</span><div style="display:none">hidden</div>{{FrontSide}} [sound:test.mp3] <img src="a.png" onerror="bad()"><img src="https://evil.test/x">'
        value=c.clean(value)
        self.assertIn('<b>Heading</b>',value);self.assertIn('src="a.png"',value)
        for bad in ('leak','Secret','hidden','FrontSide','sound','onerror','https:'):self.assertNotIn(bad,value)
    def test_normal_body_weight_survives_inside_bold_heading_wrapper(self):
        # Anki's editor can display a normal span inside a surrounding <b>.
        # Dropping its normal-weight declaration makes the body appear bold.
        for weight in ('normal','400','400 !important'):
            with self.subTest(weight=weight):
                source='<b>Bone Repair and Remodeling<br><span style="font-weight:'+weight+'">When the bone gets fractured, <strong>authored emphasis</strong> stays.</span></b>'
                output=c.clean(source)
                self.assertIn('<b>Bone Repair and Remodeling',output)
                self.assertIn('style="font-weight:400'+('!important' if 'important' in weight else '')+'"',output)
                self.assertIn('<strong>authored emphasis</strong>',output)
                self.assertEqual(c.clean(output),output,'repeated sanitization must retain normal overrides')
    def test_weight_cascade_keeps_last_valid_declaration_and_priority(self):
        cases={
            'font-weight:bold;font-weight:normal':'font-weight:400',
            'font-weight:normal!important;font-weight:bold':'font-weight:400!important',
            'FONT-WEIGHT: 400 ! IMPORTANT; font-weight:900!important':'font-weight:900!important',
            'font-weight:600':'font-weight:600',
            'font-weight:bolder':'font-weight:bolder',
            'font-weight:lighter':'font-weight:lighter',
            'font-weight:normal;font-weight:invalid':'font-weight:400',
            'not-font-weight:bold':'',
            'font-weight:expression(alert(1))':'',
            'font-weight:var(--untrusted)':'',
        }
        for source,expected in cases.items():
            with self.subTest(source=source):self.assertEqual(c.safe_font_weight(source),expected)
        output=c.clean('<span style="font-weight:normal;color:expression(bad);background-image:url(javascript:bad)" onclick="bad()">Text</span>')
        self.assertIn('font-weight:400',output)
        for unsafe in ('expression','javascript','onclick','url('):self.assertNotIn(unsafe,output)
    def test_cloze_formatting_keeps_normal_body_in_every_mode_and_cache_identity(self):
        source='<b>Bone Repair and Remodeling<br><span style="font-weight:normal">When the bone gets fractured, the repair begins with {{c1::blood clot formation}} and is followed by a {{c2::cartilaginous callus}}.</span></b>'
        for mode in ('flash','exam','mixed'):
            with self.subTest(mode=mode):
                question=compile_([(1,1,10,0,1,source+'\x1f')],{1:model()},mode)['questions'][0]
                self.assertIn('font-weight:400',question['clue'])
                self.assertIn('<b>Bone Repair and Remodeling',question['clue'])
                self.assertIn('cartilaginous callus',question['clue'])
                self.assertNotIn('blood clot formation',question['clue'])
                self.assertEqual(question['slots'][0]['answer'],'blood clot formation')
                old=copy.deepcopy(question);old['clue']=old['clue'].replace(' style="font-weight:400"','')
                self.assertEqual(c.cache_key(question,question['slots'][0],'same-model'),c.cache_key(old,old['slots'][0],'same-model'),'format correction must reuse existing AI choices')
    def test_basic_and_custom_fields_keep_explicit_body_weight(self):
        clue='<b>Heading<br><span style="font-weight:400">A regular explanation with <b>intentional bold</b>.</span></b>'
        for note_type in ('Basic','Custom'):
            question=compile_([(1,1,10,0,2,clue+'\x1fTerm')],{2:model(2,note_type,('Front','Back'),0)},'flash')['questions'][0]
            self.assertIn('font-weight:400',question['clue']);self.assertIn('<b>intentional bold</b>',question['clue'])
    def test_io_active_group_and_header(self):
        m=model(4,'Image Occlusion',('Occlusion','Image','Header','Back Extra'),0);m['originalStockKind']=6
        fields=['{{c1::image-occlusion:rect:left=.1:top=.2:width=.2:height=.1:oi=1}}{{c2::image-occlusion:rect:left=.5:top=.6:width=.1:height=.1:oi=1}}{{c2::image-occlusion:ellipse:left=.7:top=.1:rx=.1:ry=.1:oi=1}}','<div><img src="anatomy.png"></div>','Name the structures','Extra']
        q=c.io_question(fields,m,2)
        self.assertEqual(q['mask_count'],2);self.assertEqual(q['picture'].count('mask target'),2)
        self.assertEqual(q['picture'].count('mask inactive'),1);self.assertNotIn('image-occlusion:',q['picture']);self.assertEqual(q['clue'],'Name the structures')
        self.assertIn('io-image"><img',q['picture'])
        fields[0]=fields[0].replace(':oi=1','');q=c.io_question(fields,m,2)
        self.assertNotIn('inactive',q['picture']);self.assertIsNone(c.io_question(fields,m,3))
    def test_io_legacy_skipped_without_revealing_answer(self):
        m=model(4,'Image Occlusion Enhanced',('Image','Question Mask'),0)
        self.assertIsNone(c.io_question(['<img src="a.png">','<img src="mask.svg">'],m,1))
    def test_partial_credit_and_invalid_picks(self):
        q={'mode':'exam','slots':[{'correct':0},{'correct':3}]}
        self.assertEqual(c.grade(q,{'choices':[0,2]}),{'earned':1,'total':2,'correct':[True,False]})
        for picks in ([0],[0,None],[True,3],[0,4]):
            with self.assertRaises(ValueError):c.grade(q,{'choices':picks})
        self.assertEqual(c.grade({'mode':'flash'},{'known':False})['earned'],0)
    def test_cache_changes_on_context_answer_model(self):
        q={'clue':'A _____'};slot={'answer':'B'};key=c.cache_key(q,slot,'m1')
        for clue,answer,model_ in [('C _____','B','m1'),('A _____','D','m1'),('A _____','B','m2')]:
            self.assertNotEqual(key,c.cache_key({'clue':clue},{'answer':answer},model_))
        self.assertNotEqual(key,c.cache_key(q,dict(slot,number=2),'m1'))
    def test_distinct_choices_and_locked_answer(self):
        self.assertEqual(len(c.valid_distractors('Cells',['Tissues','Organs','Systems'])),3)
        for wrong in (['cells!','Organs','Systems'],['Organs','Organs!','Systems'],['','a','b'],['a','b']):
            with self.assertRaises(ValueError):c.valid_distractors('Cells',wrong)
    def test_no_truncation_and_limit(self):
        m=model(2,'Basic',('Front','Back'),0)
        rows=[(i,i,10,0,2,f'Question number {i}\x1fAnswer {i}') for i in range(1,158)]
        self.assertEqual(len(compile_(rows,{2:m})['questions']),157)
        self.assertEqual(len(compile_(rows,{2:m},limit=30)['questions']),30)
    def test_deck_boundary_and_and_exact_selection(self):
        decks=[{'id':'1','name':'A'},{'id':'2','name':'A::One'},{'id':'3','name':'AB::Two'},{'id':'4','name':'B'}]
        self.assertEqual(c.selected_decks(decks,['1']),[1,2]);self.assertEqual(c.selected_decks(decks,['1'],False),[1])
    def test_prepare_reuses_cached_and_randomizes_correct_options(self):
        q=compile_([(1,1,10,0,2,'Long enough clue\x1fAnswer')],{2:model(2,'Basic',('Front','Back'),0)})['questions']
        jobs,ready=c.prepare_choices(q,{},'m');self.assertEqual(ready,0);self.assertEqual(len(jobs),1)
        cache={jobs[0]['id']:['Wrong A','Wrong B','Wrong C']};jobs,ready=c.prepare_choices(q,cache,'m');self.assertEqual((jobs,ready),([],1))
        c.attach_choices(q,cache,'m');slot=q[0]['slots'][0];self.assertEqual(slot['choices'][slot['correct']],'Answer');self.assertEqual(len(set(slot['choices'])),4)

class SnapshotTests(unittest.TestCase):
    def test_sqlite_collection_is_unchanged(self):
        db=sqlite3.connect(':memory:');db.executescript('create table cards(id integer,nid integer,did integer,ord integer,due integer,odid integer default 0);create table notes(id integer,mid integer,flds text);create table revlog(id integer,cid integer);insert into cards(id,nid,did,ord,due) values(1,1,10,0,123);insert into notes values(1,2,"A long question'+chr(31)+'Answer");insert into revlog values(99,1);')
        before='\n'.join(db.iterdump())
        class DB:
            def all(self,sql,*args):
                if not sql.lower().startswith('select '):raise AssertionError('Collection write attempted')
                return db.execute(sql,args).fetchall()
        m=model(2,'Basic',('Front','Back'),0)
        col=types.SimpleNamespace(db=DB(),decks=types.SimpleNamespace(all_names_and_ids=lambda:[types.SimpleNamespace(id=10,name='Deck')],get_current_id=lambda:10),models=types.SimpleNamespace(all=lambda:[m]))
        out,count=c.snapshot(col,{'decks':['10'],'mode':'flash','shuffle':False},{})
        self.assertEqual(count,1);self.assertEqual(len(out['questions']),1)
        self.assertEqual('\n'.join(db.iterdump()),before)
        out,count=c.snapshot(col,{'decks':['missing'],'mode':'flash'},{})
        self.assertEqual(out['questions'],[])

class FakeResponse:
    def __init__(self,data):self.data=json.dumps(data).encode()
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return self.data

class GeminiTests(unittest.TestCase):
    def test_rest_contract_no_key_in_url_or_body(self):
        def opener(req,timeout):
            self.assertEqual(timeout,35);self.assertTrue(req.full_url.endswith('models/gemini-test:generateContent'))
            self.assertEqual(req.get_header('X-goog-api-key'),'secret-test-key')
            body=json.loads(req.data);self.assertNotIn('secret-test-key',req.full_url+req.data.decode())
            self.assertEqual(body['generationConfig']['responseMimeType'],'application/json')
            self.assertEqual(body['generationConfig']['responseSchema']['properties']['sets']['items']['properties']['id']['enum'],['a'])
            return FakeResponse({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps({'sets':[{'id':'a','answer_aliases':[],'wrong':['Lyon','Nice','Bordeaux']}]})}]}}]})
        out=g.Gemini('secret-test-key','gemini-test',opener).generate([{'id':'a','clue':'Capital of France?','answer':'Paris','blank':1}])
        self.assertEqual(out['a'][0],'Lyon')
    def test_errors_dont_include_secret_or_error_body(self):
        for code in (400,401,403,404,429,500):
            def opener(req,timeout):raise urllib.error.HTTPError(req.full_url,code,'secret-test-key',None,None)
            with self.assertRaises(g.AIError) as cm:g.Gemini('secret-test-key','gemini-test',opener).request('test')
            self.assertNotIn('secret-test-key',str(cm.exception))
    def test_bad_ai_choices_rejected(self):
        payload={'sets':[{'id':'a','answer_aliases':[],'wrong':['Paris','Nice','Lyon']}]}
        def opener(req,timeout):return FakeResponse({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(payload)}]}}]})
        client=g.Gemini('key','model',opener)
        with self.assertRaises(g.AIError):client.generate([{'id':'a','answer':'Paris'}])
        payload['sets'][0]={'id':'unknown','answer_aliases':[],'wrong':['A','B','C']}
        with self.assertRaises(g.AIError):client.generate([{'id':'a','answer':'Paris'}])
    def test_model_pagination(self):
        urls=[]
        def opener(req,timeout):
            urls.append(req.full_url)
            return FakeResponse({'models':[{'name':'models/gemini-m','supportedGenerationMethods':['generateContent']}],**({'nextPageToken':'a b'} if len(urls)==1 else {})})
        self.assertEqual(g.Gemini('key','model',opener).models(),['gemini-m']);self.assertIn('pageToken=a%20b',urls[1])
    def test_completed_batches_survive_later_error_and_cancellation(self):
        with tempfile.TemporaryDirectory() as td:
            store=s.Store(td);event=threading.Event();jobs=[{'id':str(i)} for i in range(6)]
            class Client:
                def generate(self,items):
                    if items[0]['id']=='5':raise g.AIError('quota')
                    return {j['id']:['a','b','c'] for j in items}
            with self.assertRaises(g.AIError):g.generate_batches(Client(),jobs,store,event,lambda d,t:None)
            self.assertEqual(len(s.Store(td).cache()),5)
            event.set()
            with self.assertRaises(g.Cancelled):g.generate_batches(Client(),jobs,store,event,lambda d,t:None)

class StorageTests(unittest.TestCase):
    def test_profiles_and_history_are_separate_and_atomic(self):
        with tempfile.TemporaryDirectory() as td:
            a=s.Store(pathlib.Path(td)/'A');b=s.Store(pathlib.Path(td)/'B')
            a.put({'key':['a','b','c']});self.assertEqual(b.cache(),{})
            for i in range(40):a.history({'index':i})
            a=s.Store(pathlib.Path(td)/'A');self.assertEqual(len(a.data['history']),30);self.assertEqual(a.data['history'][0]['index'],39)
            a.set_key('test-secret');self.assertEqual(a.get_key(),'test-secret')
            self.assertNotIn('test-secret',(a.path/'practice.json').read_text())
            self.assertFalse(list(a.path.glob('.cram-*')))
    def test_corrupt_file_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            store=s.Store(td);file=store.path/'practice.json';file.write_text('broken')
            with self.assertRaises(ValueError):s.Store(td)
            self.assertEqual(file.read_text(),'broken')

if __name__=='__main__':unittest.main()
