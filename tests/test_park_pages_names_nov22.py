#!/usr/bin/env python3
"""Page reader + park facts, 22 Nov 2026 (owner: "names i am sure we not doing a good job of confirming park names"): 7,303 of
8,763 read pages were marked 'name differs' because the first heading was site wording ("Main navigation", "Explore This Park",
"Official websites use .mass.gov", "Language selection"), while the page title named the park ("Cherokee State Park | Kentucky
State Parks"). Now the heading, the title and each part of the title (split at | - : and the like, brackets dropped) are tried,
and the name agrees when any one of them is the same as POTA's. A page that names another park still differs. Invented parks,
offline fixtures. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


h = getattr(R, 'name_agreeing', None)
check('the reader has a name check that looks past the site wording', callable(h))
if callable(h):
    check('heading "Main navigation", title "Cherokee State Park | Kentucky State Parks": agrees',
          h({'heading': 'Main navigation', 'title': 'Cherokee State Park | Kentucky State Parks'}, 'Cherokee State Park')[1] in ('same', 'same-core'))
    check('title in brackets "Big Bend National Park (U.S. National Park Service)": agrees',
          h({'heading': 'Explore This Park', 'title': 'Big Bend National Park (U.S. National Park Service)'}, 'Big Bend National Park')[1] in ('same', 'same-core'))
    check('title "Banff National Park - Parks Canada": agrees', h({'heading': 'Language selection', 'title': 'Banff National Park - Parks Canada'}, 'Banff National Park')[1] in ('same', 'same-core'))
    check('a page that names another park still differs', h({'heading': 'Welcome', 'title': 'Pine Mountain State Park | Kentucky'}, 'Cherokee State Park') == (None, None))

REFS = ['US-9401', 'US-9402']
U = lambda r: f'https://parks.invented.example/park/{r}'
BODIES = {'US-9401': '<html><head><title>Invented Lake State Park | Invented State Parks</title></head><body><nav><h1>Main navigation</h1></nav><p>'
                     + 'Words about the park. ' * 40 + '</p></body></html>',
          'US-9402': '<html><head><title>Other Ridge State Park | Invented State Parks</title></head><body><h1>Main navigation</h1><p>'
                     + 'Words about the park. ' * 40 + '</p></body></html>'}
NAMES = {'US-9401': 'Invented Lake State Park', 'US-9402': 'Invented Hollow State Park'}
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [NAMES[r], U(r), 'State Park', '', '', 38.5, -85.5, 0, 0, 1] for r in REFS}}), encoding='utf-8')
    (t / 'fx.json').write_text(json.dumps({'pages': {U(r): {'status': 200, 'body': BODIES[r]} for r in REFS}}), encoding='utf-8')
    out = t / 'out'; out.mkdir()
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'), '--out', str(out),
                        '--state', str(out / 'state.json'), '--fixtures', str(t / 'fx.json'), '--today', '2026-11-22', '--areas', 'US-ZZ', '--quiet'],
                       capture_output=True, text=True)
    facts = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    n1 = (facts.get('US-9401') or {}).get('name') or {}
    n2 = (facts.get('US-9402') or {}).get('name') or {}
    check('reader: a page titled with the park name agrees even under a "Main navigation" heading',
          r.returncode == 0 and n1.get('vs_pota') in ('same', 'same-core') and not n1.get('disagree'))
    check('reader: a page titled with another park still differs', n2.get('vs_pota') not in ('same', 'same-core'))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
