"""Profile-owned AI workers, independent of both Anki TaskManager pools.

Timing records contain numbers/status only, never keys, URLs or study text.
All disk work stays on the worker; UI completion uses Anki's main-thread bridge.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
import json
from pathlib import Path
import threading
import time

_pools = {}
_context = threading.local()


def current_transport(origin="https://generativelanguage.googleapis.com"):
    owner = getattr(_context, 'owner', None)
    return owner.transport(origin) if owner is not None else None


def record_phase(name, seconds):
    data = getattr(_context, 'timings', None)
    if data is not None and name in ('http', 'decode', 'cache_save', 'api_queue'):
        with getattr(_context, 'timing_lock', None) or nullcontext():
            item = data['phases'].setdefault(name, {'count': 0, 'total_ms': 0, 'max_ms': 0})
            elapsed = max(0, seconds * 1000)
            item['count'] += 1
            item['total_ms'] = round(item['total_ms'] + elapsed, 2)
            item['max_ms'] = round(max(item['max_ms'], elapsed), 2)


def parallel_context():
    owner = getattr(_context, 'owner', None)
    data = getattr(_context, 'timings', None)
    lock = getattr(_context, 'timing_lock', None)
    if data is not None:data['api_parallelism'] = 2
    pool = owner.api_pool if owner is not None else ThreadPoolExecutor(max_workers=2)
    def wrap(work):
        queued=time.perf_counter()
        def run():
            _context.owner, _context.timings, _context.timing_lock = owner, data, lock
            try:
                record_phase('api_queue',time.perf_counter()-queued)
                return work()
            finally:_context.owner, _context.timings, _context.timing_lock = None, None, None
        return run
    return pool, owner is None, wrap


class NetworkJobs:
    def __init__(self, taskman, profile):
        self.taskman = taskman
        self.path = Path(profile) / 'cram_studio' / 'generation-timings.jsonl'
        self.pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix='CramAI')
        self.api_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='CramBatch')
        self.closed = False
        self.log_lock = threading.Lock()
        self.transports = {}
        self.transport_lock = threading.Lock()

    def transport(self, origin="https://generativelanguage.googleapis.com"):
        from .gemini_transport import PooledHTTP
        with self.transport_lock:
            if self.closed:
                import urllib.error
                raise urllib.error.URLError('Profile closed')
            identity = (threading.get_ident(), origin)
            if identity not in self.transports:self.transports[identity] = PooledHTTP(origin)
            return self.transports[identity]

    def _write_timing(self, value):
        try:
            with self.log_lock:
                if self.closed:
                    return
                self.path.parent.mkdir(parents=True, exist_ok=True)
                if self.path.exists() and self.path.stat().st_size > 65536:
                    self.path.replace(self.path.with_suffix('.previous.jsonl'))
                with self.path.open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(value, separators=(',', ':')) + '\n')
        except OSError:
            pass  # Diagnostics must never turn a successful generation into a failure.

    def submit(self, work, done):
        queued = time.perf_counter()
        def run():
            started = time.perf_counter()
            data = {'queued_ms': round((started - queued) * 1000, 2),
                    'phases': {}, 'status': 'error'}
            _context.timings = data
            _context.owner = self
            _context.timing_lock = threading.Lock()
            try:
                result = work()
                data['status'] = 'ok'
                return result
            except BaseException as error:
                if type(error).__name__ == 'Cancelled':data['status'] = 'cancelled'
                if getattr(error, 'status_code', None) == 429:data['http_status'] = 429
                raise
            finally:
                data['work_ms'] = round((time.perf_counter() - started) * 1000, 2)
                _context.timings = None
                _context.owner = None
                _context.timing_lock = None
                self._write_timing(data)
        future = self.pool.submit(run)
        def completed(future):
            if not self.closed:
                self.taskman.run_on_main(lambda: done(future) if not self.closed else None)
        future.add_done_callback(completed)
        return future

    def close(self):
        with self.transport_lock:
            self.closed = True
            transports = list(self.transports.values())
            self.transports.clear()
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.api_pool.shutdown(wait=False, cancel_futures=True)
        if transports:
            def cleanup():
                for transport in transports:transport.close()
            threading.Thread(target=cleanup, name='CramHTTPclose', daemon=True).start()


def run_network(mw, work, done):
    profile = str(Path(mw.pm.profileFolder()).resolve())
    pool = _pools.get(profile)
    if pool is None or pool.closed:
        pool = _pools[profile] = NetworkJobs(mw.taskman, profile)
    return pool.submit(work, done)


def close_network():
    pools = list(_pools.values())
    _pools.clear()
    for pool in pools:
        pool.close()
