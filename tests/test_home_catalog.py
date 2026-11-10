"""Actual native deck metadata for visual grouping; disposable collection only."""
import importlib
from pathlib import Path
import sys
import tempfile
import types
import unittest
pkg=types.ModuleType('cram_studio');pkg.__path__=[str(Path(__file__).resolve().parents[1]/'cram_studio')];sys.modules.setdefault('cram_studio',pkg)
c=importlib.import_module('cram_studio.content')
class HomeCatalog(unittest.TestCase):
    def test_native_filtered_and_regular_metadata_without_collection_changes(self):
        from anki.collection import Collection
        with tempfile.TemporaryDirectory() as td:
            col=Collection(str(Path(td)/'test.anki2'))
            try:
                normal=col.decks.id('MIDTERMS::SEPC::Lesson 1');filtered=col.decks.new_filtered('Today only')
                before=col.db.all('select id,did,odid,due,queue,type,ivl,reps,lapses from cards');out=c.catalog(col);rows={row['id']:row for row in out['decks']}
                self.assertTrue(rows[str(filtered)]['filtered']);self.assertFalse(rows[str(normal)]['filtered']);self.assertEqual(col.db.all('select id,did,odid,due,queue,type,ivl,reps,lapses from cards'),before)
            finally:col.close()
if __name__=='__main__':unittest.main()
