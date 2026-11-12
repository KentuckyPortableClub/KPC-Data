#!/usr/bin/env python3
"""Nov 6 Part B: 15 km ledger proposals + short-name guard."""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _links_checkout; _links_checkout.use(ROOT)   # Nov 11: any KPC-Links checkout, any start folder
os.environ.setdefault('DATA', str(ROOT))
import kpc_pile_solver as S
import kpc_agreement_ledger as AL
ok=True
def check(c,m):
  global ok
  print(('PASS ' if c else 'FAIL ')+m); ok = ok and bool(c)

check(S.is_short_name('Rock Creek'), 'Rock Creek is short')
check(S.is_short_name('Seven Mile'), 'Seven Mile is short')
check(not S.is_short_name('Kaskaskia State Forest'), 'Kaskaskia State Forest is not short')
check(not S.is_short_name('Suwannee River Wilderness State Trail'), 'Suwannee Trail is not short')

PADUS=S.PADUS
class FarRec:
  def __init__(self, km=10, name='Kaskaskia State Forest'):
    self.km, self.name, self.skipped = km, name, []
  def record(self, rid, area='US-', src=None):
    dx = max(0.02, self.km / 85.0)
    box = [[-90.0+dx, 38.9], [-90.0+dx+0.05, 38.9], [-90.0+dx+0.05, 39.1], [-90.0+dx, 39.1], [-90.0+dx, 38.9]]
    return {'id': str(rid), 'name': self.name, 'attrs': {'Loc_Mang': 'Illinois DNR'}, 'rings': [box], 'layer': PADUS,
            'url': PADUS+'/query?f=json', 'label': 'USGS PAD-US', 'family': 'padus', 'html': PADUS+'/query?f=html'}
  def counties_at_pin(self, la, lo): return ({'17117': 'Macoupin'}, '')
  def counties_of(self, rings): return ({'17117': 'Macoupin'}, '')

S.KEYS.clear()
kf = str(S.LINKS / 'data/us-key/US-IL.json')
base = {'ref': 'US-9990', 'area': 'US-IL', 'areas': 'US-IL', 'name': 'Kaskaskia State Forest', 'type': 'State Forest',
        'flags': {'PIN_WAY_OUT'}, 'why': 'test', 'ids': ['a1'], 'lat': '39.0', 'lon': '-90.0', 'action': 'HOLD', 'src': 'pile', 'h': 'x', 'page': ''}

S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Kaskaskia State Forest', 't': 'State Forest', 'm': [['a1', 'Kaskaskia State Forest', 0, 'name']]}}}
r = S.solve(base, FarRec(20), {}, {})
check(r['verdict']=='NEEDS-PERSON' and '15' in r['reason'], f'>15 km NEEDS-PERSON ({r["verdict"]}: {r["reason"][:80]})')

S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Rock Creek', 't': '', 'm': [['a1', 'Rock Creek', 0, 'name']]}}}
r = S.solve(dict(base, name='Rock Creek', type=''), FarRec(8, 'Rock Creek'), {}, {})
check(r['verdict']=='NEEDS-PERSON' and 'short' in r['reason'].lower(), f'short-name guard ({r["reason"][:80]})')

td = pathlib.Path(tempfile.mkdtemp()); AL.LEDGER=td/'ledger.csv'; AL.STATE=td/'state.json'; AL.save_rows([]); AL.save_state(AL.load_state())
S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Kaskaskia State Forest', 't': 'State Forest', 'm': [['a1', 'Kaskaskia State Forest', 0, 'name']]}}}
r = S.solve(base, FarRec(8), {}, {})
check(r['verdict']=='SOLVED-JOIN', f'8 km SOLVED-JOIN ({r["verdict"]})')
check('ledger proposal' in r['pin_flag'], f'ledger flag ({r["pin_flag"]})')
rows=AL.load_rows()
check(any(x.get('proposed_by')=='pile-solver' and x.get('kind')=='join' for x in rows), f'ledger row ({rows})')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
