#!/usr/bin/env python3
"""Park page reader, 26 Nov 2026 (owner 8:49 PM: 'webpage reader I think waste a lot of time going oh i read these 1000 pages
before'). The PC's state had 3,806 'resting' and 1,050 'refused' reads saved with the fingerprint of an EMPTY page, and the reader
took any fingerprint as 'read before', so those parks were passed over for 30 days and never really read (BLM 897, NY DEC 567).
  1  a resting read with no words is due the next day: the page is really asked
  2  a page really read (words) still waits for the refresh
  3  a refused page waits a week, then is asked again
  4  the due parks are read first, before parks read before
Invented parks, a fake getter, no network. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, sys, tempfile

os.environ['KPC_MANNERS_CACHE'] = tempfile.mkdtemp(prefix='kpc-pp-empty-')
os.environ.pop('BROWSER', None)
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


TEXT = ('<html><head><title>Invented Ridge State Forest</title></head><body><h1>Invented Ridge State Forest</h1>'
        + '<p>The forest has trails and a pond for walkers in every season.</p>' * 12 + '</body></html>')


class Fake:
    def __init__(self):
        self.calls = []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        return 200, {'content-type': 'text/html'}, TEXT.encode(), url


REFS = ['US-9001', 'US-9002', 'US-9003', 'US-9004']
URL = {r: f'https://parks.invented.example.gov/{r.lower()}' for r in REFS}
check('the empty-page fingerprint is the one on the PC', PP.EMPTY_FP == 'e3b0c44298fc')

with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    (t / 'parkinfo').mkdir(parents=True)
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        r: [f'Invented Park {r}', URL[r], 'State Forest', '', '', 38.5, -85.5, 0, 0, 1] for r in REFS}}), encoding='utf-8')
    areas, web, docs, truth = PP.load_data(t)
    out = t / 'out'
    (out / 'facts').mkdir(parents=True)
    old = {r: {'ref': r, 'page': {'kind': 'html'}} for r in REFS}   # each park has saved facts (has_old)
    (out / 'facts' / 'US-ZZ.json').write_text(json.dumps({'parks': old}), encoding='utf-8')
    state = {'read': {
        'US-9001': {'url': URL['US-9001'], 'fingerprint': PP.EMPTY_FP, 'date': '2026-11-25', 'kind': 'resting'},
        'US-9002': {'url': URL['US-9002'], 'fingerprint': 'a1b2c3d4e5f6', 'date': '2026-11-25', 'kind': 'html', 'key_rule': PP.URL_KEY_RULE},
        'US-9003': {'url': URL['US-9003'], 'fingerprint': PP.EMPTY_FP, 'date': '2026-11-23', 'kind': 'refused'},
        'US-9004': {'url': URL['US-9004'], 'fingerprint': PP.EMPTY_FP, 'date': '2026-11-10', 'kind': 'refused'}},
        'fingerprints': {}}
    g = Fake()
    PP.read_parks(areas, web, docs, truth, g, state, '2026-11-26', refs=['US-9002', 'US-9003', 'US-9004', 'US-9001'],
                  out_dir=str(out), quiet=True)
    asked = [c.rsplit('/', 1)[-1].upper() for c in g.calls]
    check(f'1: a resting read with no words is really asked the next day ({asked})', 'US-9001' in asked)
    check('2: a page really read yesterday still waits for the refresh', 'US-9002' not in asked)
    check('3: a page refused three days ago waits a week', 'US-9003' not in asked)
    check('3: a page refused 16 days ago is asked again', 'US-9004' in asked)
    check(f'4: the due parks are read first, in the worklist order ({asked})', asked[:2] == ['US-9004', 'US-9001'])
    check('1: the page read for real is saved with its words, not the empty fingerprint',
          state['read']['US-9001'].get('fingerprint') not in ('', PP.EMPTY_FP) and state['read']['US-9001'].get('kind') == 'html')

src = (ROOT / '.github/scripts/kpc_park_pages.py').read_text(encoding='utf-8')
check('a same-text check never counts two empty pages as the same page', "prev.get('fingerprint') != EMPTY_FP and prev.get('url') == url" in src)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
