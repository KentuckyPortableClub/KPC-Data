#!/usr/bin/env python3
"""Park page reader, 24 Nov 2026 (owner 7:32 AM, P-2 "yes"): a page that answers the plain reader with 403 gets ONE try in the
PC's browser. Offline: invented parks and fake getters only. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, sys, tempfile

os.environ['KPC_MANNERS_CACHE'] = tempfile.mkdtemp(prefix='kpc-pp-403-')
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


BUILT = ('<html><head><title>Invented Rim Recreation Area</title></head><body><h1>Invented Rim Recreation Area</h1>'
         + '<p>The area has a campground, trails and a boat ramp open in every season.</p>' * 12 + '</body></html>')
URL = 'https://www.invented-blm.example.gov/visit/invented-rim'


def tree(t):
    (t / 'parkinfo').mkdir(parents=True, exist_ok=True)
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-9001': ['Invented Rim Recreation Area', URL, 'BLM Recreation Area', '', '', 38.5, -110.5, 0, 0, 1]}}), encoding='utf-8')
    return PP.load_data(t)


class G:
    def __init__(self, status=403, built=None, browser=True):
        self.status, self.built, self.browsed = status, built, []
        if browser: self.browser_html = self._b

    def get(self, url, rng=None, deadline=None, max_time=None):
        return self.status, {'content-type': 'text/html'}, b'<html><body>Forbidden</body></html>', url

    def _b(self, url):
        self.browsed.append(url); return self.built or ''


def run(g):
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td); areas, web, docs, truth = tree(t); out = t / 'out'; state = {}
        facts, reqs = PP.read_parks(areas, web, docs, truth, g, state, '2026-11-24', out_dir=str(out),
                                    state_path=str(out / 'state.json'), quiet=True)
        return facts['US-ZZ']['US-9001'], state


fact, state = run(G(403, BUILT))
check('a 403 page gets one browser try and is read like any page', fact['page']['kind'] == 'html' and fact['page'].get('browser') is True)
check('a browser read that worked is not counted as a refusal', not (state.get('refusal_pages') or {}))
g = G(403, '')
fact, state = run(g)
# 27 Nov 2026 (owner: 'sure we are just polite'): a 401 / 403 is that page only, for this run: kind 'resting' (asked again next run)
check('the browser gives nothing: the page waits for the next run (resting), and was asked once', fact['page']['kind'] == 'resting' and len(g.browsed) == 1)
g = G(403, '<html><body><h1>Access denied</h1>' + '<p>Checking your browser before you go on to the page.</p>' * 12 + '</body></html>')
fact, _ = run(g)
check('a wall in the browser: the page waits for the next run (resting)', fact['page']['kind'] == 'resting')
fact, _ = run(G(403, BUILT, browser=False))
check('no browser offered: the page waits for the next run (resting, 27 Nov rule)', fact['page']['kind'] == 'resting')
g = G(404, BUILT)
fact, _ = run(g)
check('a dead page (404) is never sent to the browser', g.browsed == [])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
