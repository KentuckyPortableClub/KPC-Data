#!/usr/bin/env python3
"""Park page reader, 22 Nov 2026: a page that builds itself is opened once in the browser and read like any other page.
When the browser is off or gives nothing, the park stays for a person, exactly as before. BROWSER=1 off: never opened.
Offline: invented parks and fake getters only (no Playwright needed). Prints PASS / FAIL and ends ALL PASS or SOME FAILED.
"""
import json, os, pathlib, sys, tempfile

CACHE = tempfile.mkdtemp(prefix='kpc-pp-browser-')
os.environ['KPC_MANNERS_CACHE'] = CACHE
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_manners as K  # noqa: E402
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


SHELL = b'<html><head><title>Loading</title></head><body><div id="app"></div><script src="app.js"></script></body></html>'
BUILT = ('<html><head><title>Invented Ridge State Forest</title></head><body><h1>Invented Ridge State Forest</h1>'
         '<p>Total area: 1,234 acres</p>' + '<p>The forest has trails and a pond for walkers in every season.</p>' * 12
         + '</body></html>')
URL = 'https://parks.invented.example.gov/ridge'


def tree(t):
    (t / 'parkinfo').mkdir(parents=True, exist_ok=True)
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-9001': ['Invented Ridge State Forest', URL, 'State Forest', '', '', 38.5, -85.5, 0, 0, 1]}}), encoding='utf-8')
    return PP.load_data(t)


class Fake:
    """Every address answers the empty shell; the browser (when offered) answers `built`."""
    def __init__(self, built=None):
        self.built, self.calls, self.browsed = built, [], []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        return 200, {'content-type': 'text/html'}, SHELL, url


class FakeWithBrowser(Fake):
    def browser_html(self, url):
        self.browsed.append(url)
        return self.built or ''


def run(getter):
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        areas, web, docs, truth = tree(t)
        out = t / 'out'
        state = {}
        facts, reqs = PP.read_parks(areas, web, docs, truth, getter, state, '2026-11-22', out_dir=str(out),
                                    state_path=str(out / 'state.json'), quiet=True)
        return facts['US-ZZ']['US-9001'], reqs


fact, _ = run(Fake())
check('no browser offered: the page stays script-built (for a person)', fact['page']['kind'] == 'script-built')

g = FakeWithBrowser(BUILT)
fact, reqs = run(g)
check('the browser is asked once for the page that builds itself', g.browsed == [URL])
check('the built page is read like any other page', fact['page']['kind'] == 'html')
check('the fact says the page was read in the browser', fact['page'].get('browser') is True)
check('its size is read from the built page', ((fact.get('confirm') or {}).get('size') or {}).get('acres') == 1234)
check('the browser read is counted as a request', reqs >= 2)

g = FakeWithBrowser('<html><body><div id="app">Loading...</div></body></html>')
fact, _ = run(g)
check('a built page that is still empty stays for a person', fact['page']['kind'] == 'script-built')

g = FakeWithBrowser('<html><body><h1>Just a moment</h1>' + '<p>Checking your browser before you go on to the page.</p>' * 12 + '</body></html>')
fact, _ = run(g)
check('a wall in the browser is not read as the park', fact['page']['kind'] == 'script-built')

os.environ.pop('BROWSER', None)
live = PP.LiveGetter({})
check('BROWSER=1 off: the live getter never opens a browser', live.browser_html(URL) == '')
check('BROWSER=1 off: the manners browser read says nothing', K.browser_html(URL, live.M) == '')
kc = PP.KeeperCopyGetter({'pages': {}}, pathlib.Path(CACHE), None)
check('the keeper copy with no live getter never opens a browser', kc.browser_html(URL) == '')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
