"""Every generation entry starts with both Anki worker pools occupied."""
import ast
from concurrent.futures import ThreadPoolExecutor
import importlib
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
if 'cram_studio' not in sys.modules:
    package = types.ModuleType('cram_studio')
    package.__path__ = [str(ROOT/'cram_studio')]
    sys.modules['cram_studio'] = package
network = importlib.import_module('cram_studio.network_jobs')


class BackgroundJobs(unittest.TestCase):
    def test_all_six_generation_entries_start_with_anki_pools_busy(self):
        shared = ThreadPoolExecutor(max_workers=2)
        collection = ThreadPoolExecutor(max_workers=1)
        release = threading.Event()
        occupied = [threading.Event() for _ in range(3)]
        for pool, event in zip([shared, shared, collection], occupied):
            pool.submit(lambda event=event: (event.set(), release.wait(3)))
        callbacks = []
        calls = []
        for path in (ROOT/'cram_studio').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if not isinstance(node, ast.Call):continue
                if ((isinstance(node.func, ast.Name) and node.func.id == 'run_network')
                    or (isinstance(node.func, ast.Attribute) and node.func.attr == 'network_runner')):
                    calls.append(node)
        try:
            self.assertTrue(all(event.wait(1) for event in occupied))
            with tempfile.TemporaryDirectory() as profile:
                def forbidden(*args, **kwargs):self.fail('Gemini must not submit to either Anki executor')
                mw = types.SimpleNamespace(pm=types.SimpleNamespace(profileFolder=lambda: profile),
                    taskman=types.SimpleNamespace(run_on_main=callbacks.append, run_in_background=forbidden))
                owner = types.SimpleNamespace(mw=mw, owner=types.SimpleNamespace(mw=mw), network_runner=network.run_network)
                self.assertEqual(len(calls), 6)
                for call in calls:
                    future = eval(compile(ast.Expression(call), 'actual-controller-submission', 'eval'),
                        {'self': owner, 'run_network': network.run_network,
                         'work': lambda: 'Gemini begins', 'done': lambda future: None})
                    self.assertEqual(future.result(timeout=.5), 'Gemini begins')
                self.assertFalse(release.is_set())
                workers = list(network._pools.values())
                network.close_network()
                for worker in workers:worker.pool.shutdown(wait=True)
        finally:
            network.close_network();release.set()
            shared.shutdown(wait=True);collection.shutdown(wait=True)


if __name__ == '__main__':unittest.main()
