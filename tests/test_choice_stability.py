"""Choice error reasons, stable shuffles and native shown-hook lifecycle."""
import copy
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from test_core import c,g,s


class ChoiceStabilityTests(unittest.TestCase):
    def test_specific_reasons_for_invalid_choice_sets_without_answer_text(self):
        cases=[([],[],'Exactly three'),
            (['Paris','Lyon','Nice'],[],'repeats the correct answer'),
            (['Capital of France','Lyon','Nice'],['Capital of France'],'alias of the correct answer'),
            (['Lyon','LYON','Nice'],[],'repeat the same option'),
            (['','Lyon','Nice'],[],'is empty'),
            (['x'*601,'Lyon','Nice'],[],'600-character limit'),
            ([None,'Lyon','Nice'],[],'must be text')]
        for wrong,aliases,reason in cases:
            class Client(g.Gemini):
                label='Groq'
                def generate_json(self,*args):return {'sets':[{'id':'a','answer_aliases':aliases,'wrong':wrong}]}
            with self.subTest(reason=reason),self.assertRaises(g.AIError) as caught:
                Client('private-key','model').generate([{'id':'a','answer':'Paris'}])
            message=str(caught.exception);self.assertIn(reason,message)
            self.assertNotIn('private-key',message);self.assertNotIn('Paris',message)
            self.assertIn('existing saved choices are kept',message)

    def test_unknown_or_missing_fields_have_specific_safe_format_errors(self):
        for parsed,reason in [({'sets':[]},'wrong number'),({'sets':[{'id':'other'}]},'unknown or repeated'),
            ({'sets':[{'id':'a','answer_aliases':[]}]},'missing required choice fields')]:
            class Client(g.Gemini):
                def generate_json(self,*args):return parsed
            with self.subTest(parsed=parsed),self.assertRaisesRegex(g.AIError,reason):
                Client('private-key','model').generate([{'id':'a','answer':'Paris'}])

    def test_unexpected_parser_error_does_not_echo_provider_content(self):
        class Client(g.Gemini):
            def generate_json(self,*args):return {'sets':[{'id':'a','answer_aliases':[],
                'wrong':['One','Lyon','Nice']}]}
        with patch.object(g,'valid_distractors',side_effect=ValueError('PRIVATE_MODEL_TEXT')):
            with self.assertRaises(g.AIError) as caught:Client('private-key','model').generate([{'id':'a','answer':'Paris'}])
        self.assertNotIn('PRIVATE_MODEL_TEXT',str(caught.exception));self.assertNotIn('private-key',str(caught.exception))
        self.assertIn('invalid format',str(caught.exception))

    def test_random_positions_are_local_and_attached_choices_stay_fixed(self):
        q={'id':'q','kind':'basic','mode':'exam','clue':'Question','ready':False,
           'slots':[{'number':1,'answer':'Right'}]}
        key=c.cache_key(q,q['slots'][0],'model');cache={key:['Wrong 1','Wrong 2','Wrong 3']}
        for position in range(4):
            question=copy.deepcopy(q)
            class Shuffle:
                def shuffle(self,values):values[:]=values[position:]+values[:position]
            with patch.object(c.random,'SystemRandom',return_value=Shuffle()):
                c.attach_choices([question],cache,'model')
            self.assertEqual(question['slots'][0]['correct'],(-position)%4)
            original=copy.deepcopy(question)
            class MustNotShuffle:
                def shuffle(self,values):raise AssertionError('Ready choices must not shuffle on refresh')
            with patch.object(c.random,'SystemRandom',return_value=MustNotShuffle()):
                self.assertEqual(c.attach_choices([question],cache,'model',partial=True),[])
            self.assertEqual(question,original)

    @unittest.skipUnless(shutil.which('node'),'Node required for actual shown-hook execution')
    def test_repeated_native_render_installs_only_one_callback_per_hook_array(self):
        from test_live_review import Environment
        with tempfile.TemporaryDirectory() as folder:
            env=Environment(folder);env.live.begin('exam',False);markup=env.packet()
            script=re.findall(r'<script>(.*?)</script>',markup,re.S)[-1]
            program='''const vm=require('node:vm');let mounts=0;
const ctx={onShownHook:[],cramNative:{mount:()=>mounts++},setTimeout:fn=>fn()};ctx.window=ctx;
const source=JSON.parse(process.argv[1]);
for(let i=0;i<40;i++)vm.runInNewContext(source,ctx);
if(ctx.onShownHook.length!==1)throw Error('Accumulated '+ctx.onShownHook.length+' shown hooks');
ctx.onShownHook[0]();if(mounts!==1)throw Error('Extra mounts');
ctx.onShownHook=[];vm.runInNewContext(source,ctx);
if(ctx.onShownHook.length!==1)throw Error('Missing hook after Anki replaces array');
ctx.onShownHook[0]();if(mounts!==2)throw Error('New array did not mount');'''
            result=subprocess.run(['node','-e',program,json.dumps(script)],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr);env.live.close();s.clear_profile_stores()


if __name__=='__main__':unittest.main()
