#!/usr/bin/env python3
"""Nov 11 (data-quality review): kpc_pota_activity.py kept last week's numbers only for a location whose request FAILED. A location that
answered with an empty list lost all its parks' numbers, and a whole short answer was saved. Now a location of 10+ parks under half its
size keeps last week's numbers, and a whole answer under 80% of last week's is refused. Offline: urlopen is replaced in this process."""
import contextlib, io, json, os, pathlib, sys, tempfile, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


API = {}


class Resp:
    def __init__(self, b): self.b = b
    def read(self): return self.b
    def __enter__(self): return self
    def __exit__(self, *a): return False


def fake(req, *a, **k):
    u = req.full_url
    assert u.startswith('https://api.pota.app/'), u
    v = API[u]
    if isinstance(v, Exception): raise v
    return Resp(json.dumps(v).encode())


urllib.request.urlopen = fake
time.sleep = lambda *a, **k: None
import kpc_pota_activity as A   # noqa: E402


def parks(loc, n, act=1): return [{'reference': f'{loc}-{i:04d}', 'activations': act, 'attempts': 2, 'locationDesc': loc} for i in range(n)]


d = pathlib.Path(tempfile.mkdtemp(prefix='kpc-act-')); os.chdir(d)
API['https://api.pota.app/locations'] = [{'locationDesc': 'US-KY'}, {'locationDesc': 'FR'}, {'locationDesc': 'DE'}]
API['https://api.pota.app/location/parks/US-KY'] = parks('US-KY', 600)
API['https://api.pota.app/location/parks/FR'] = parks('FR', 400)
API['https://api.pota.app/location/parks/DE'] = parks('DE', 50)


def go():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): A.main()
    return buf.getvalue(), json.load(open('data/pota/activity.json'))['parks']


out, got = go()
check(len(got) == 1050, 'first run: 1050 parks')
API['https://api.pota.app/location/parks/DE'] = []
out, got = go()
check(len(got) == 1050 and 'DE' in out, f'a location that answers with an empty list keeps last week\'s numbers ({len(got)} parks)')
API['https://api.pota.app/location/parks/DE'] = RuntimeError('503')
out, got = go()
check(len(got) == 1050, 'a failed location still keeps them')
API['https://api.pota.app/location/parks/DE'] = parks('DE', 50, act=3)
API['https://api.pota.app/location/parks/FR'] = parks('FR', 220)       # 220 of 400 and 330 of 600 are each over half, but the total (600 of 1050) is under 80%: refused
API['https://api.pota.app/location/parks/US-KY'] = parks('US-KY', 330)
snap = open('data/pota/activity.json').read()
out, got = go()
check(open('data/pota/activity.json').read() == snap and '::warning title=POTA activity::' in out and 'Nothing was changed' in out, 'a whole answer under 80% of last week is refused, the file is untouched, the log says so')
API['https://api.pota.app/location/parks/FR'] = parks('FR', 390)       # an ordinary small change
API['https://api.pota.app/location/parks/US-KY'] = parks('US-KY', 600)
out, got = go()
check(len(got) == 1040 and got['DE-0000'][0] == 3, 'an ordinary change is saved (390 FR, DE activations 3)')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
