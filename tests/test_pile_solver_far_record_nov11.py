#!/usr/bin/env python3
"""Nov 11 (data-quality review): the pile solver's 15 km band, short-name guard and 'km' text read the distance of the CLOSEST joined
record only. A park joined to two records of the same name, one holding the pin and one 20 km away in the same county, passed rule 3 as
'SOLVED-JOIN ... 0.0 km' with a ledger proposal that names only the near record, although the far record is past the 15 km line
(Brandon's ruling: over ~15 km = a person). The farthest 'far' record now decides. Offline: the Fetch object is a fake with boxes."""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _links_checkout; _links_checkout.use(ROOT)
os.environ.setdefault('DATA', str(ROOT))
import kpc_pile_solver as S
import kpc_agreement_ledger as AL
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)

PADUS = S.PADUS
class Two:
    """a1 holds the pin; a2 starts `km` km east of it. Same name, same county."""
    def __init__(self, km): self.km = km
    def record(self, rid, area='US-', src=None):
        x0 = -90.01 if rid == 'a1' else -90.0 + self.km / 85.0
        box = [[x0, 38.99], [x0 + 0.02, 38.99], [x0 + 0.02, 39.01], [x0, 39.01], [x0, 38.99]]
        return {'id': str(rid), 'name': 'Kaskaskia State Forest', 'attrs': {'Loc_Mang': 'Illinois DNR'}, 'rings': [box], 'layer': PADUS,
                'url': PADUS + '/query?f=json', 'label': 'USGS PAD-US', 'family': 'padus', 'html': PADUS + '/query?f=html'}
    def counties_at_pin(self, la, lo): return ({'17117': 'Macoupin'}, '')
    def counties_of(self, rings): return ({'17117': 'Macoupin'}, '')

td = pathlib.Path(tempfile.mkdtemp()); AL.LEDGER = td / 'ledger.csv'; AL.STATE = td / 'state.json'; AL.save_rows([]); AL.save_state(AL.load_state())
S.KEYS.clear()
kf = str(S.LINKS / 'data/us-key/US-IL.json')
S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Kaskaskia State Forest', 't': 'State Forest', 'm': [['a1', 'Kaskaskia State Forest', 0, 'name'], ['a2', 'Kaskaskia State Forest', 0, 'name']]}}}
base = {'ref': 'US-9990', 'area': 'US-IL', 'areas': 'US-IL', 'name': 'Kaskaskia State Forest', 'type': 'State Forest', 'flags': {'PIN_WAY_OUT'},
        'why': 'test', 'ids': ['a1', 'a2'], 'lat': '39.0', 'lon': '-90.0', 'action': 'HOLD', 'src': 'pile', 'h': 'x', 'page': ''}

r = S.solve(base, Two(20), {}, {})
check(r['verdict'] == 'NEEDS-PERSON' and '15' in r['reason'], f"one record holds the pin, the other is ~20 km out: NEEDS-PERSON ({r['verdict']}: {r['reason'][:90]})")
check(not AL.load_rows(), 'and no ledger join proposal is made for it')
r = S.solve(base, Two(8), {}, {})
check(r['verdict'] == 'SOLVED-JOIN' and 'although it is 8.' in r['reason'], f"the far record ~8 km out: still SOLVED-JOIN, and the text gives the far distance ({r['reason'][-80:]})")
S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Kaskaskia State Forest', 't': 'State Forest', 'm': [['a1', 'Kaskaskia State Forest', 0, 'name']]}}}
r = S.solve(dict(base, ids=['a1']), Two(20), {}, {})
check(r['verdict'] == 'SOLVED-JOIN' and 'rule 1' in r['reason'], f"a single record holding the pin: rule 1 as before ({r['verdict']})")
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
