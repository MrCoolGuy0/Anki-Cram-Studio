"""Persistent, bounded AI HTTP connections. No cookies or saved credentials."""
from http.cookiejar import DefaultCookiePolicy
import threading
import urllib.error
from urllib.parse import urlsplit


class PooledHTTP:
    def __init__(self, origin='https://generativelanguage.googleapis.com'):
        import requests
        self.origin = origin
        self.lock = threading.RLock()
        self.closed = False
        self.session = requests.Session()
        self.session.headers.clear()
        class NoMachineAuth(requests.auth.AuthBase):
            def __call__(self, request):return request
        self.session.auth = NoMachineAuth()
        self.session.cookies.set_policy(DefaultCookiePolicy(allowed_domains=()))
        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1,
                                                pool_block=True, max_retries=0)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def open(self, request, timeout=35):
        import requests
        from urllib3.exceptions import HTTPError as StreamError
        address = urlsplit(request.full_url)
        if address.scheme+'://'+address.netloc != self.origin or address.username or address.password:
            raise urllib.error.URLError('Unexpected API origin')
        self.lock.acquire()
        try:
            if self.closed:raise urllib.error.URLError('Connection closed')
            response = self.session.request(request.get_method(), request.full_url,
                data=request.data, headers=dict(request.header_items()),
                timeout=timeout, stream=True, allow_redirects=False)
            if response.status_code >= 300:
                code=response.status_code;response.close()
                raise urllib.error.HTTPError(request.full_url, code, 'API request failed', None, None)
        except (requests.RequestException, StreamError) as error:
            self.lock.release()
            raise urllib.error.URLError('API connection failed') from None
        except BaseException:
            self.lock.release()
            raise
        owner = self
        class Response:
            def __enter__(self):return self
            def read(self, size):
                try:return response.raw.read(size, decode_content=True)
                except (requests.RequestException, StreamError, OSError):
                    raise urllib.error.URLError('API read failed') from None
            def __exit__(self, *args):
                try:response.close()
                finally:owner.lock.release()
        return Response()

    def close(self):
        with self.lock:
            self.closed=True
            self.session.close()
