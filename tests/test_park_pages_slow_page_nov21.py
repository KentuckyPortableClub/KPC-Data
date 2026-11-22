#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026 (seen on the PC run): (1) ONE download that passes its own cap (get_max_seconds) is one slow
page, not the end of the run: the reader goes on to the next park; only the run's own deadline stops it as 'minutes'.
(2) A link with a space ('...query=38.2, -106.7') is sent escaped, so it no longer skips the park on every run.
Offline, invented parks. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import os, pathlib, socket, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.environ['KPC_NO_NET'] = '1'
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('test: no network'))
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


BODY = b'<html><head><title>Park</title></head><body><h1>Park</h1></body></html>'


class CapGetter:
    """The second address answers as a download cut at its own cap; the run's deadline is far away."""
    def __init__(self):
        self.calls = []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        if url.endswith('/b2'):
            return 'err:deadline', {}, b'', url
        return 200, {'content-type': 'text/html'}, BODY, url


areas = {'US-ZZ': {r: {'name': n, 'website': f'https://parks.invented.example/{r[-2:].lower()}', 'type': 'State Park',
                       'lat': 40.0, 'lon': -100.0, 'qsos': 1}
                   for r, n in (('US-B1', 'Alpha'), ('US-B2', 'Beta'), ('US-B3', 'Gamma'))}}
web = {r: {'url': a['website']} for r, a in areas['US-ZZ'].items()}
g = CapGetter(); state = {}
facts, _ = PP.read_parks(areas, web, {}, {}, g, state, '2026-11-21', refs=['US-B1', 'US-B2', 'US-B3'],
                         deadline=time.time() + 3600, get_max_seconds=90)
got = facts.get('US-ZZ') or {}
check('a download cut at its own cap does not end the run (the next park is read)', 'US-B3' in got and state.get('stopped') != 'minutes')
check('the slow park is kept as resting, to be asked again', (got.get('US-B2') or {}).get('page', {}).get('kind') == 'resting')


class FakeManners:
    def __init__(self):
        self.urls = []

    def get(self, url, **k):
        self.urls.append(url)
        return 200, {'content-type': 'text/html'}, BODY, url


lg = PP.LiveGetter.__new__(PP.LiveGetter); lg.M = FakeManners(); lg.calls = []
lg.get('https://maps.invented.example/maps/search/?api=1&query=38.2458, -106.7502')
check('a link with a space is sent escaped', lg.M.urls == ['https://maps.invented.example/maps/search/?api=1&query=38.2458,%20-106.7502'])
lg.get('https://parks.invented.example/a%20b/park?x=1&y=2#top')
check('an address that is already escaped is sent unchanged', lg.M.urls[-1] == 'https://parks.invented.example/a%20b/park?x=1&y=2#top')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
