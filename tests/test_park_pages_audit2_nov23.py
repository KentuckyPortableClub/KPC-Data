#!/usr/bin/env python3
"""Park page reader, 23 Nov 2026 (owner 'Yes' to the outside audit's four MUST-FIX items):
  1. a park 'read recently' whose facts are NOT in the out folder is read again (before: an empty stub was saved and its
     read date was set to today, so the 30-day clock never ran out); a skipped fresh park keeps the date of its real read;
  2 and 3 are in the workflow (checked as text): the saved facts come in before a run; facts files over 2 MB are kept;
  4. '23 540 hectares' is 23,540 ha, not 540; '45,6 km2' is read; 'Route 9 100 acres' stays 100.
Also: ctparks.com is an official site (Connecticut State Parks). Offline, invented parks.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.environ['KPC_NO_NET'] = '1'
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('test: no network'))
import kpc_park_pages as PP  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


BODY = (b'<html><head><title>Invented Ridge State Park</title></head><body><h1>Invented Ridge State Park</h1><p>'
        + b'The park covers 1,234 acres of forest. ' * 30 + b'</p></body></html>')


class Getter:
    def __init__(self):
        self.calls = []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        return 200, {'content-type': 'text/html'}, BODY, url


REFS = ['US-C1', 'US-C2']
areas = {'US-ZZ': {r: {'name': 'Invented Ridge State Park', 'website': f'https://parks.invented.example.gov/{r.lower()}',
                       'type': 'State Park', 'lat': 40.0, 'lon': -100.0, 'qsos': 1} for r in REFS}}
web = {r: {'url': a['website']} for r, a in areas['US-ZZ'].items()}

# 1. read on 1 Nov into one folder; a later run into an EMPTY folder (a GitHub run, a new PC folder) must read again
with tempfile.TemporaryDirectory() as td:
    a, b = pathlib.Path(td) / 'a', pathlib.Path(td) / 'b'
    state = {}
    PP.read_parks(areas, web, {}, {}, Getter(), state, '2026-11-01', refs=REFS, out_dir=str(a), state_path=str(a / 'state.json'))
    st = json.loads((a / 'state.json').read_text())
    g = Getter()
    PP.read_parks(areas, web, {}, {}, g, json.loads(json.dumps(st)), '2026-11-10', refs=REFS, out_dir=str(b), state_path=str(b / 'state.json'))
    facts_b = json.loads((b / 'facts' / 'US-ZZ.json').read_text())['parks']
    check('with no facts in the out folder, a recently read park is read again (no stub)', len(g.calls) >= 2
          and set(facts_b) == set(REFS) and all('confirm' in facts_b[r] and not facts_b[r].get('unchanged') for r in REFS))
    # a fresh skip in the SAME folder keeps the real read date
    st_a = json.loads((a / 'state.json').read_text())
    g2 = Getter()
    PP.read_parks(areas, web, {}, {}, g2, st_a, '2026-11-10', refs=REFS, out_dir=str(a), state_path=str(a / 'state.json'))
    st_a2 = json.loads((a / 'state.json').read_text())
    check('a fresh park in a folder that holds its facts is not fetched', g2.calls == [])
    check('a skipped fresh park keeps the date of its real read (the clock runs out)',
          all(st_a2['read'][r]['date'] == '2026-11-01' for r in REFS))
    facts_a = json.loads((a / 'facts' / 'US-ZZ.json').read_text())['parks']
    check('a skipped fresh park keeps its full facts', all('confirm' in facts_a[r] for r in REFS))
    # a stub saved before the fix counts as no facts: the park is read again
    fa = json.loads((a / 'facts' / 'US-ZZ.json').read_text())
    fa['parks']['US-C1'] = {'ref': 'US-C1', 'unchanged': True, 'page': {'read': '2026-11-02'}}
    (a / 'facts' / 'US-ZZ.json').write_text(json.dumps(fa))
    g3 = Getter()
    PP.read_parks(areas, web, {}, {}, g3, json.loads((a / 'state.json').read_text()), '2026-11-11', refs=REFS, out_dir=str(a),
                  state_path=str(a / 'state.json'))
    fa2 = json.loads((a / 'facts' / 'US-ZZ.json').read_text())['parks']
    check('an old empty stub is read again and replaced by full facts', len(g3.calls) == 1 and 'confirm' in fa2['US-C1'])
    # merge_unchanged never leaves a stub
    parks = {'US-X9': {'ref': 'US-X9', 'unchanged': True, 'page': {'read': '2026-11-10'}}}
    PP.merge_unchanged(str(b), {'US-ZZ': parks})
    check('an unchanged park with no earlier facts is left out, not saved as a stub', 'US-X9' not in parks)

# 2 and 3: the workflow
yml = (ROOT / '.github/workflows/kpc-park-pages.yml').read_text()
check('the read job starts from the facts saved on tools-out', 'git archive origin/tools-out park-pages/facts' in yml)
check('facts files and state.json are never deleted for size', "-size +2M -not -path '*/facts/*' -not -name state.json -delete" in yml
      and '-size +2M -delete' not in yml)

# 4. metric sizes
def ha(text):
    return sorted(round(r['acres']) for r in R.sizes_labelled(text, 'Invented Lake Park', 'Provincial Park'))


check("'23 540 hectares' is 23,540 ha (58,169 acres)", any(abs(x - 58169) <= 2 for x in ha('The park covers 23 540 hectares of boreal forest.')))
check("'23 540 hectares' is not read as 540 ha", not any(abs(x - 1334) <= 2 for x in ha('The park covers 23 540 hectares of boreal forest.')))
check("'45,6 km2' is read (4,560 ha = 11,268 acres)", any(abs(x - 11268) <= 3 for x in ha('Superficie : 45,6 km2 de territoire protégé.')))
check("a no-break space thousands mark: '1 234 hectares'", any(abs(x - 3049) <= 2 for x in ha('It covers 1 234 hectares.')))
check("'Route 9 100 acres' stays 100", R.metric_numbers('Route 9 100 acres') == 'Route 9 100 acres')
check('ctparks.com is an official site', R.official_host('https://ctparks.com/parks/invented-ridge'))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
