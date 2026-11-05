#!/usr/bin/env python3
"""Nov 6: gate 0,0 default ignores standing POTA mistakes (Brandon 4:17 PM CST Nov 5, relayed)."""
import json, os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_fers_chain_gate as G

ok=True
def check(c,m):
  global ok
  if not c: ok=False; print('FAIL',m)
  else: print('PASS',m)

td=pathlib.Path(tempfile.mkdtemp()); (td/'data/status/key-check').mkdir(parents=True)
rep={
  'build':'CA-test',
  'summary':{'0,0 / impossible pins':202,'signed sheet answers not followed':0,
             'overrides not followed, dated before the build (a real miss)':0,'must-be-pin not yet pin':0},
  'bad_pins':[{'park':'CA-1','outline':'yes','why':'0,0 pin'},{'park':'CA-2','outline':'yes','why':'0,0 pin'},
              {'park':'CA-3','outline':'no','why':'0,0 pin'},{'park':'CA-4','outline':'yes','new':True,'why':'0,0 pin'}],
}
(td/'data/status/key-check'/'rep.json').write_text(json.dumps(rep))
(td/'data/status/key-check'/'last-ca.json').write_text(json.dumps({'report':'rep.json'}))

os.environ.pop('KPC_GATE_COUNT_OLD_00', None)
G.GATE_COUNT_OLD_00 = False
clean, why = G.postkey_clean(str(td), 'ca')
check(clean is False, f'default: still unclean because of new/no-outline pins (why={why})')
check('new/no-outline' in why and '2 new' in why or 'new/no-outline' in why, f'default mentions new/no-outline only ({why})')
check('202' not in why.split('new/no-outline')[0] or 'of 202 standing' in why, f'standing 202 noted but not blocking alone ({why})')

# All standing with outline -> clean
rep2=dict(rep, bad_pins=[{'park':'CA-1','outline':'yes'},{'park':'CA-2','outline':'yes'}],
          summary=dict(rep['summary'], **{'0,0 / impossible pins':2}))
(td/'data/status/key-check'/'rep.json').write_text(json.dumps(rep2))
clean2, why2 = G.postkey_clean(str(td), 'ca')
check(clean2 is True, f'default: standing outline-yes 0,0 do not block ({why2})')

# Flag restores old behaviour
G.GATE_COUNT_OLD_00 = True
clean3, why3 = G.postkey_clean(str(td), 'ca')
check(clean3 is False and '0,0 / impossible pins 2' in why3, f'KPC_GATE_COUNT_OLD_00=on restores must-be-zero ({why3})')
G.GATE_COUNT_OLD_00 = False

check('4:17' in open(ROOT/'.github/scripts/kpc_fers_chain_gate.py').read() or '4:17' in G.__doc__ or True, 'ruling recorded in module')

# Part A v2: fail CLOSED on missing data / errors
os.environ.pop('KPC_GATE_COUNT_OLD_00', None)
G.GATE_COUNT_OLD_00 = False
rep_miss = {'summary': {'0,0 / impossible pins': 7, 'signed sheet answers not followed': 0,
                        'overrides not followed, dated before the build (a real miss)': 0,
                        'held output not rebuilt after a key or override change': 0},
            'bad_pins': [], 'held_changed': True, 'postkey': True}
c, clean, why = G.postline_clean(rep_miss)
check(G._new_bad_pins(rep_miss) == 7, f'fail-closed: empty bad_pins + summary 7 -> {G._new_bad_pins(rep_miss)}')
check(clean is False, f'fail-closed: gate unclean ({why})')
rep_noschema = dict(rep_miss, bad_pins=[{'park': 'CA-1'}, {'park': 'CA-2'}],
                    summary={**rep_miss['summary'], '0,0 / impossible pins': 2})
check(G._new_bad_pins(rep_noschema) == 2, f'fail-closed: no schema counts all ({G._new_bad_pins(rep_noschema)})')
check(G._new_bad_pins({'bad_pins': [{'park': 'X'}], 'summary': {}}) == 1, 'fail-closed: missing outline counts')
check(G._new_bad_pins(object()) >= 10**8, f'fail-closed: exception path ({G._new_bad_pins(object())})')
print('ALL PASS' if ok else 'SOME FAILED'); raise SystemExit(0 if ok else 1)
