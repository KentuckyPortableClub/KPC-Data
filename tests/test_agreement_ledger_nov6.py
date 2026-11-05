#!/usr/bin/env python3
"""Nov 6: agreement ledger — two agreements, different agents; location-fix never edits POTA pins."""
import json, pathlib, sys, tempfile, os
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_agreement_ledger as AL
import kpc_pile_exit as PE

ok=True
def check(c,m):
  global ok
  if not c: ok=False; print('FAIL',m)
  else: print('PASS',m)

td=pathlib.Path(tempfile.mkdtemp())
AL.LEDGER = td/'ledger.csv'; AL.STATE = td/'state.json'
AL.save_rows([]); AL.save_state(AL.load_state())
st=AL.load_state()
check(st['auto'] is False, 'auto defaults false')
check(st['decided_by']==AL.DECIDED_BY, 'decided_by recorded')

rows=AL.propose('US-1','pile-exit','mystery-bot','join outline X','mystery-intake')
rows=AL.propose('CA-1930','location-fix','agent-A','corrected pin near the park','manual', pota_lat='0', pota_lon='0', rows=rows)
AL.save_rows(rows)

# same agent cannot confirm
try:
  AL.confirm('US-1','pile-exit','mystery-bot', rows=rows)
  check(False, 'same agent must raise')
except ValueError as e:
  check('same agent' in str(e), f'same agent rejected ({e})')

rows=AL.confirm('US-1','pile-exit','quality', rows=rows)
rows=AL.confirm('CA-1930','location-fix','checker', rows=rows, agreed_lat='46.8', agreed_lon='-71.2')
AL.save_rows(rows)

ready=AL.ready(rows=rows)
check(len(ready)==2, f'two ready rows ({len(ready)})')
ex=AL.exit_candidates(rows)
check(ex['auto'] is False and ex['count_ready']==1 and ex['would_exit']==[], 'auto=false: ready but would_exit empty')
check(ex['ready_but_auto_false'][0]['park']=='US-1', 'US-1 ready for exit when auto on')

loc=AL.location_fixes(rows)
check(len(loc)==1 and loc[0]['agreed_lat']=='46.8' and loc[0]['pota_lat']=='0', 'location-fix keeps pota_lat=0 and sets agreed_lat')
check('POTA source pin unchanged' in loc[0]['note'], 'note says POTA pin unchanged')

r00=AL.report_00(rows)
check(r00['confirmations_both']==1 and r00['proposals_only']==0, f'0,0 report both=1 ({r00})')

# empty ledger report
AL.save_rows([])
r0=AL.report_00()
check(r0['proposals_only']==0 and r0['confirmations_both']==0 and r0['total_location_fix_rows']==0, f'empty ledger 0/0/0 ({r0})')

# pile-exit path with auto false writes nothing
PE.AL.LEDGER=AL.LEDGER; PE.AL.STATE=AL.STATE
# restore one ready exit
rows=AL.propose('US-2','pile-exit','outside','fix','src')
rows=AL.confirm('US-2','pile-exit','checker', rows=rows); AL.save_rows(rows)
rep=PE.run()
check(rep['auto'] is False and rep['count_ready']==1 and rep.get('would_exit_now')==[], 'exit path respects auto=false')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
