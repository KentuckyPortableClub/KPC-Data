"""A made-up web for the page reader's tests (26 Nov 2026). Nothing here can reach a server: every socket is shut first, and
urllib's urlopen is replaced by a lookup in a dictionary. Tests only; the reader never imports this file."""
import email.message, io, socket, time, urllib.error, urllib.request


def shut_network():
    def _no(*a, **k):
        raise OSError('NETWORK CLOSED IN TESTS')
    socket.socket.connect = _no
    socket.socket.connect_ex = _no
    socket.create_connection = _no
    socket.getaddrinfo = _no


shut_network()


class _Resp(io.BytesIO):
    def __init__(self, status, body, headers, url):
        super().__init__(body)
        self.status = status
        self.headers = email.message.Message()
        for k, v in (headers or {}).items():
            self.headers[k] = v
        self._url = url

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class FakeWeb:
    """pages: {url: (status, body bytes|str, headers dict) | Exception | callable(req) -> such a tuple}.
    A url not listed answers 404. Every call is recorded in self.calls as (method, url, headers)."""

    def __init__(self, pages):
        self.pages = dict(pages)
        self.calls = []
        self.sleeps = []

    def urlopen(self, req, timeout=None, context=None, **k):
        url = req.full_url if hasattr(req, 'full_url') else str(req)
        hdrs = dict(req.header_items()) if hasattr(req, 'header_items') else {}
        self.calls.append((getattr(req, 'get_method', lambda: 'GET')(), url, hdrs))
        ans = self.pages.get(url, (404, b'', {}))
        if callable(ans):
            ans = ans(req)
        if isinstance(ans, BaseException):
            raise ans
        st, body, headers = ans
        body = body.encode('utf-8') if isinstance(body, str) else body
        final = (headers or {}).get('X-Final-Url') or url
        if st >= 300 and st != 304 or st == 304:
            m = email.message.Message()
            for kk, vv in (headers or {}).items():
                m[kk] = vv
            raise urllib.error.HTTPError(url, st, 'fake', m, io.BytesIO(body))
        return _Resp(st, body, headers, final)

    def install(self, *modules):
        """Replace urlopen and time.sleep (recorded, not slept) for the reader's modules."""
        urllib.request.urlopen = self.urlopen
        for m in modules:
            if hasattr(m, 'time'):
                m.time.sleep = lambda s: self.sleeps.append(s)
        return self

    def asked(self, part=''):
        return [u for _, u, _ in self.calls if part in u]
