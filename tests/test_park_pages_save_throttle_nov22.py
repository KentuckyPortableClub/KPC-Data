#!/usr/bin/env python3
"""Park page reader, 22 Nov 2026 (owner 5:12 PM: the PC run crawled through parks it only skips): the facts and state were
rewritten after EVERY park (each save re-reads and rewrites the area's facts file and the 5 MB state). Now a walk saves at
most every SAVE_EVERY_SECONDS, and always at the end, on a stop and on a reader error, so nothing is lost. Offline, invented
parks. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, socket, sys, tempfile

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
    def get(self, url, rng=None, deadline=None, max_time=None):
        return 200, {'content-type': 'text/html'}, BODY, url


REFS = [f'US-T{i:02d}' for i in range(25)]
areas = {'US-ZZ': {r: {'name': 'Invented Ridge State Park', 'website': f'https://parks.invented.example.gov/{r.lower()}',
                       'type': 'State Park', 'lat': 40.0, 'lon': -100.0, 'qsos': 1} for r in REFS}}
web = {r: {'url': a['website']} for r, a in areas['US-ZZ'].items()}
writes = []
real = PP._write_progress
PP._write_progress = lambda *a, **k: (writes.append(1), real(*a, **k))[1]
with tempfile.TemporaryDirectory() as td:
    out = pathlib.Path(td) / 'out'
    state = {}
    PP.read_parks(areas, web, {}, {}, Getter(), state, '2026-11-22', refs=REFS, out_dir=str(out), state_path=str(out / 'state.json'))
    saved = json.loads((out / 'facts' / 'US-ZZ.json').read_text())['parks']
    st = json.loads((out / 'state.json').read_text())
    check(f'25 parks in a quick walk are saved a few times, not after every park ({len(writes)} saves)', 1 <= len(writes) <= 3)
    check('every park is in the facts file at the end of the walk', set(saved) == set(REFS))
    check('the saved state says nothing is left', st.get('left') == [])
    writes.clear()
    state2 = json.loads((out / 'state.json').read_text())
    PP.read_parks(areas, web, {}, {}, Getter(), state2, '2026-11-22', refs=REFS, out_dir=str(out), state_path=str(out / 'state.json'), max_parks=3)
    st2 = json.loads((out / 'state.json').read_text())
    check('a run that stops part way still saves where it stopped', len(writes) >= 1 and len(st2.get('left') or []) == 22)
    check('and keeps every park already in the file', set(json.loads((out / 'facts' / 'US-ZZ.json').read_text())['parks']) == set(REFS))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
