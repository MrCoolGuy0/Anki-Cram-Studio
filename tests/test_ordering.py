import copy
import importlib
from pathlib import Path
import random
import sys
import types
import unittest

if 'cram_studio' not in sys.modules:
    package=types.ModuleType('cram_studio');package.__path__=[str(Path(__file__).resolve().parents[1]/'cram_studio')];sys.modules['cram_studio']=package
o=importlib.import_module('cram_studio.ordering')
c=importlib.import_module('cram_studio.content')

def column(key,label,asc=True):
    enum=types.SimpleNamespace(values_by_number={1:types.SimpleNamespace(name='SORTING_'+('ASCENDING' if asc else 'DESCENDING'))})
    return types.SimpleNamespace(key=key,cards_mode_label=label,sorting_cards=1,DESCRIPTOR=types.SimpleNamespace(fields_by_name={'sorting_cards':types.SimpleNamespace(enum_type=enum)}))
class OrderingTests(unittest.TestCase):
    def test_every_native_sortable_column_is_offered_with_native_direction(self):
        cols=[column('cardDue','Due'),column('cardLapses','Lapses',False),column('cardIvl','Interval')];calls=[]
        col=types.SimpleNamespace(all_browser_columns=lambda:cols,find_cards=lambda q,**args:calls.append((q,args)) or [2,1])
        self.assertEqual(o.menu(col),[{'key':v.key,'label':v.cards_mode_label} for v in cols])
        for desc in (False,True):
            self.assertEqual(o.native_order(col,'is:due prop:lapses>=2','cardLapses',desc),[2,1]);self.assertEqual(calls[-1][1]['reverse'],not desc)
        with self.assertRaises(ValueError):o.native_order(col,'','bad; update cards',False)
    def test_due_presets_preserve_native_due_order_before_tie_breaking(self):
        calls=[]
        class DB:
            def all(self,sql,*ids):
                self_test.assertTrue(sql.startswith('select '));return [(1,2,10),(2,2,10),(3,2,20)]
        self_test=self;col=types.SimpleNamespace(all_browser_columns=lambda:[column('cardDue','Due')],find_cards=lambda q,**args:[1,2,3],db=DB())
        rows=[(1,1,10,0,1,''),(2,2,11,0,1,''),(3,3,11,0,1,'')];names={10:'Z',11:'A'}
        rank=o.card_rank(col,'','due_deck',False,rows,names);self.assertEqual(sorted(rank,key=rank.get),['2','1','3'])
        rank=o.card_rank(col,'','deck_due',False,rows,names);self.assertEqual(sorted(rank,key=rank.get),['2','3','1'])
        for _ in range(5):
            rank=o.card_rank(col,'','due_random',False,rows,names);self.assertEqual(rank['3'],2)
    def test_note_and_card_type_orders_keep_actual_cloze_order(self):
        initial=[{'nid':str(n),'deck':deck,'ordinal':ordinal,'id':f'{n}:{ordinal}'} for n,deck in [(1,'Z'),(2,'A')] for ordinal in (0,1,2)]
        for mode in ('random_notes','card_type','card_type_random','deck_random_notes'):
            qs=copy.deepcopy(initial);o.arrange(qs,mode);self.assertEqual({q['id'] for q in qs},{q['id'] for q in initial})
            if mode=='random_notes':
                for index in (0,3):self.assertEqual([q['ordinal'] for q in qs[index:index+3]],[0,1,2])
            if mode.startswith('card_type'):self.assertEqual([q['ordinal'] for q in qs],[0,0,1,1,2,2])
            if mode=='deck_random_notes':self.assertEqual([q['deck'] for q in qs],['A']*3+['Z']*3)
    def test_arbitrary_search_not_in_quick_buttons_is_forwarded_unchanged(self):
        raw='(prop:lapses>=3 or is:suspended) -tag:leech flag:2';self.assertEqual(c.search_query({'filters':{'search':raw}}),'('+raw+')')

if __name__=='__main__':unittest.main()
