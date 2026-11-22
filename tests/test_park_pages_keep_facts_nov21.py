#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026 (seen on the PC run): saving after each park replaced an area's facts file with that run's
parks alone. A park re-read as 'unchanged' kept only a stub, and a park the run had not reached yet vanished. Every park in
the file must survive a save; an unchanged park keeps its full fact. Offline, invented parks.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, socket, sys, tempfile, time

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


BODY = (b'<html><head><title>Invented Ridge State Park</title></head><body><h1>Invented Ridge State Park</h1><p>'
        + b'The park covers 1,234 acres of forest. ' * 30 + b'</p></body></html>')


class Getter:
    def __init__(self):
        self.calls = []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        return 200, {'content-type': 'text/html'}, BODY, url


REFS = ['US-C1', 'US-C2', 'US-C3']
areas = {'US-ZZ': {r: {'name': 'Invented Ridge State Park', 'website': f'https://parks.invented.example.gov/{r.lower()}',
                       'type': 'State Park', 'lat': 40.0, 'lon': -100.0, 'qsos': 1} for r in REFS}}
web = {r: {'url': a['website']} for r, a in areas['US-ZZ'].items()}
with tempfile.TemporaryDirectory() as td:
    out = pathlib.Path(td) / 'out'
    state = {}
    PP.read_parks(areas, web, {}, {}, Getter(), state, '2026-11-21', refs=REFS, out_dir=str(out), state_path=str(out / 'state.json'))
    path = out / 'facts' / 'US-ZZ.json'
    first = json.loads(path.read_text())['parks']
    check('the first run saves all three full facts', set(first) == set(REFS) and all('confirm' in first[r] for r in REFS))
    # a second run the same day: every park is fresh (unchanged); it stops after the first park
    state2 = json.loads((out / 'state.json').read_text())
    PP.read_parks(areas, web, {}, {}, Getter(), state2, '2026-11-21', refs=REFS, out_dir=str(out),
                  state_path=str(out / 'state.json'), max_parks=1)
    second = json.loads(path.read_text())['parks']
    check('a run that stops after one park keeps the parks it did not reach', set(second) == set(REFS))
    check('an unchanged park keeps its full fact, not a stub', all('confirm' in second.get(r, {}) and 'unchanged' not in second.get(r, {}) for r in REFS))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
