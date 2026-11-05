#!/usr/bin/env python3
"""Brandon's two-agreements rule (Part B 03 check): a solver 'unique name <=15 km' SOLVED-JOIN is only a PROPOSAL.
It never takes a join or leaves the pile on the solver's say-so: the ledger row stays unconfirmed, the same agent
cannot confirm it, a join row never counts as a pile-exit, nothing exits with auto=false, and the waiting room never
releases pile-solver files by itself."""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.environ.setdefault('LINKS', '/tmp/fers/L')
os.environ.setdefault('DATA', str(ROOT))
import kpc_pile_solver as S
import kpc_agreement_ledger as AL
ok = True
def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)

class FarRec:
    def __init__(s, km=8, name='Kaskaskia State Forest'): s.km, s.name = km, name
    def record(s, rid, area='US-', src=None):
        dx = max(0.02, s.km / 85.0)
        box = [[-90.0 + dx, 38.9], [-90.0 + dx + 0.05, 38.9], [-90.0 + dx + 0.05, 39.1], [-90.0 + dx, 39.1], [-90.0 + dx, 38.9]]
        return {'id': str(rid), 'name': s.name, 'attrs': {'Loc_Mang': 'Illinois DNR'}, 'rings': [box], 'layer': S.PADUS,
                'url': S.PADUS + '/query?f=json', 'label': 'USGS PAD-US', 'family': 'padus', 'html': S.PADUS + '/query?f=html'}
    def counties_at_pin(s, la, lo): return ({'17117': 'Macoupin'}, '')
    def counties_of(s, rings): return ({'17117': 'Macoupin'}, '')

td = pathlib.Path(tempfile.mkdtemp())
AL.LEDGER = td / 'ledger.csv'; AL.STATE = td / 'state.json'; AL.save_rows([]); AL.save_state({'auto': False})
S.KEYS.clear()
kf = str(S.LINKS / 'data/us-key/US-IL.json')
S.KEYS[kf] = {'parks': {'US-9990': {'n': 'Kaskaskia State Forest', 't': 'State Forest', 'm': [['a1', 'Kaskaskia State Forest', 0, 'name']]}}}
base = {'ref': 'US-9990', 'area': 'US-IL', 'areas': 'US-IL', 'name': 'Kaskaskia State Forest', 'type': 'State Forest',
        'flags': {'PIN_WAY_OUT'}, 'why': 'test', 'ids': ['a1'], 'lat': '39.0', 'lon': '-90.0', 'action': 'HOLD', 'src': 'pile', 'h': 'x', 'page': ''}
r = S.solve(base, FarRec(8), {}, {})
check(r['verdict'] == 'SOLVED-JOIN' and 'needs second agreement' in r['pin_flag'], f'8 km unique name -> SOLVED-JOIN labelled as needing a second agreement ({r["pin_flag"]})')
rows = AL.load_rows()
j = [x for x in rows if x['park'] == 'US-9990' and x['kind'] == 'join']
check(len(j) == 1 and j[0]['proposed_by'] == 'pile-solver' and not j[0]['confirmed_by'] and not j[0]['decided_by'],
      'ledger row is a proposal only (no confirmed_by, no decided_by)')
check(AL.ready('join', rows) == [], 'no join is ready on the solver alone')
check(AL.exit_candidates(rows, auto=True)['would_exit'] == [], 'nothing leaves the pile on the solver alone, even with auto on')
try:
    AL.confirm('US-9990', 'join', 'pile-solver', rows=rows); check(False, 'same agent confirm must raise')
except ValueError:
    check(True, 'the solver cannot confirm its own proposal')
rows = AL.confirm('US-9990', 'join', 'Quality', rows=rows)
check(len(AL.ready('join', rows)) == 1, 'a DIFFERENT agent confirming makes the join ready (two agreements)')
check(AL.exit_candidates(rows, auto=True)['would_exit'] == [], 'a join agreement is not a pile-exit (needs its own pile-exit agreement)')
check(AL.exit_candidates(rows)['would_exit'] == [], 'auto=false: nothing exits')
import kpc_waiting_room as WR
check('pilesolver' in WR.NEVER_AUTO and WR.kind_of('data/pile-solver/US-IL.json')[0] == 'pilesolver', 'waiting room never auto-releases pile-solver files')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
