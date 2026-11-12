#!/usr/bin/env python3
"""Pile solver, round 3 (Nov 7 2026): the park-type penalty and the Sinks Canyon designation check.

Penalty: report only. KPC_TYPE_PENALTY unset = the solver's outputs are the same bytes as before and no type-penalty.json exists.
Report mode writes data/pile-solver/type-penalty.json (every entry auto false), changes no verdict, never touches state['auto'].
Weights: every row of data/pile-solver/type-penalty-weights.json recomputes from its own counts with the stated formula.
Sinks Canyon (US-10890): a BLM park joined 3.1 km out to a record designated State Park / owned by a state is NEEDS-PERSON
(and makes no ledger proposal); KPC_DESIGNATION_CLASH=off gives the old SOLVED-JOIN; a pin inside the record still joins.
Offline. Writes only to temp folders.
"""
import inspect, json, os, pathlib, re, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import _links_checkout; _links_checkout.use(ROOT)   # Nov 11: any KPC-Links checkout, any start folder
os.environ.pop('KPC_TYPE_PENALTY', None)
os.environ.pop('KPC_DESIGNATION_CLASH', None)
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))

import kpc_pile_solver as S
import kpc_pile_penalty as TP
import kpc_agreement_ledger as AL

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


_td = pathlib.Path(tempfile.mkdtemp())
AL.LEDGER, AL.STATE = _td / 'ledger.csv', _td / 'ledger-state.json'   # never write the repo's ledger

W = json.loads((ROOT / TP.WEIGHTS_FILE).read_text(encoding='utf-8'))
P = W['params']

# ---------------------------------------------------------------- weights recompute from their own counts
check(W.get('auto') is False, 'weights file says auto false')
goff = W['global_official_rate']
bad = []
for grp in ('types', 'kinds', 'names'):
    for k, v in W[grp].items():
        if 'rate' not in v: continue
        s, raw = TP.shrunk_raw(v['official'], v['n'], goff, P)
        if raw != v['raw'] or abs(s - v['shrunk_rate']) > 0.0006 or abs(v['official'] / v['n'] - v['rate']) > 0.0006: bad.append((grp, k, raw, v['raw']))
check(not bad, f'every weight recomputes from its counts with the stated formula ({bad[:3]})')
check(W['kinds']['PUB']['raw'] == 25 and W['names']['airport']['raw'] == 25, 'PUB and airport names sit at the cap (25)')
check(W['names']['golf']['raw'] == 0 and W['names']['easement']['raw'] == 0, 'a class with no parks in the data has weight 0 (no evidence is not a penalty)')
check(W['names']['cemetery']['raw'] <= 2 and W['names']['school']['raw'] <= 2, 'cemetery / school names weigh at most 2 (they mostly do qualify)')
check(all(v['raw'] <= P['cap'] for g in ('types', 'kinds', 'names') for v in W[g].values()), 'no weight is over the cap')
lk = pathlib.Path(os.environ['LINKS']) / 'data/us-key'
if lk.is_dir():
    again = TP.build_weights(os.environ['LINKS'])
    check(abs(again['global_official_rate'] - goff) < 0.03, f"weights are close to a fresh run on the key (rate {again['global_official_rate']} vs {goff})")

# ---------------------------------------------------------------- the pure function
def row(verdict, rid='', flag='', name='Test Park', ref='US-1'):
    return {'ref': ref, 'pota_name': name, 'verdict': verdict, 'record_id': rid, 'pin_flag': flag, 'area': 'US-WY'}

pen = lambda r, kp, j=None: TP.type_penalty(r, kp, W, j)
check(pen(row('UNTOUCHED'), {}) is None, 'UNTOUCHED rows get no score')
x = pen(row('NEEDS-PERSON', 'a1'), {'n': 'X', 't': 'Park', 'bk': ['a1', 1, 'PUB', 'des']})
check(x['parts']['kind'] == 25 and x['penalty'] == 25 and x['score_after'] == 5, f"PUB record kind = 25, not joined ({x['penalty']})")
x = pen(row('NEEDS-PERSON'), {'n': 'X', 't': 'Park'})
check(x['penalty'] == W['types']['Park']['raw'] // 2 or x['penalty'] <= P['type_cap'], 'no code and a common type: small or zero')
x = pen(row('NEEDS-PERSON'), {'n': 'X', 't': 'No Such Type'})
check(x['penalty'] == 0, 'a type the key has not seen gets 0')
x = pen(row('NEEDS-PERSON'), {'n': 'Old Cemetery State Historic Site', 't': 'No Such Type'})
check(x['penalty'] <= 2, f"cemetery name <= 2 ({x['penalty']})")
x = pen(row('NEEDS-PERSON'), {'n': 'Rattlesnake BLM Backcountry Airstrip', 't': 'No Such Type'})
check(x['penalty'] == 25, 'airstrip name = 25')
# v2 rules on a join
rma = {'n': 'Something BLM Recreation Management Area', 't': 'BLM Recreation Management Area', 'bk': ['r1', 0.0, 'SP', 'des'],
       'm': [['r1', 'Something', 10, 'name']]}
x = pen(row('SOLVED-JOIN', 'r1'), rma)
check(x['parts']['type'] == 0 and x['penalty'] == 0 and not x['would_demote'], 'a join of a weak POTA type with a plain name match: no type penalty')
sinks = dict(rma, bk=[292692, 3.36, 'SP', 'des'], m=[[292692, 'Sinks Canyon', 79, 'name (designation code ignored)']])
x = pen(row('SOLVED-JOIN', '292692', 'POTA pin may be off'), sinks)
check(x['parts']['designation'] == 25 and x['score_before'] == 70 and x['score_after'] == 45 and x['would_demote'], 'Sinks Canyon shape: designation code ignored = 25, would demote')
x = pen(row('SOLVED-JOIN', 'other'), dict(rma, bk=['r1', 0, 'PUB', 'des']))
check(x['parts']['kind'] == 0 and 'ignored' in x['why'], "a join whose key bk is another record: that record's kind is ignored")
x = pen(row('SOLVED-JOIN', '292692'), sinks, ['292692'])
check(x['penalty'] == 0 and 'person-signed' in x['why'], 'a person-signed join (overrides join) gets no penalty')
x = pen(row('SOLVED-JOIN', 'r1'), dict(sinks, m=[['r1', 'S', 1, 'reviewed (Brandon)']], bk=['r1', 0, 'SP', 'des']))
check(x['penalty'] == 0, "a 'reviewed' match gets no penalty")
check(all(pen(row(v, 'r1'), {'n': 'Airport', 't': 'BLM Recreation Management Area', 'bk': ['r1', 0, 'PUB', 'des']})['score_after'] <= pen(row(v, 'r1'), {})['score_before']
         for v in ('SOLVED-JOIN', 'SOLVED-PIN', 'NEEDS-PERSON')), 'the penalty only subtracts')
src = inspect.getsource(TP.type_penalty) + inspect.getsource(TP.write_side) + inspect.getsource(TP.report)
check("'auto'" in src and 'state[' not in src and "['auto']" not in src and '.get(\'auto\')' not in src, 'penalty code never reads state auto; only the literal False is written')
check(TP.write_side.__doc__ and 'literal False' in TP.write_side.__doc__, 'write_side documents the literal False')

# ---------------------------------------------------------------- Sinks Canyon: the solver itself
PADUS = S.PADUS
PIN = (43.0, -108.8)


class OneRec:
    """a record 3.1 km east of the pin, same county; attrs say what the record is"""
    def __init__(self, attrs, box=None, name='Bridgeport Hollow'):
        self.attrs, self.box, self.name, self.skipped, self.n = attrs, box, name, [], 0
    def record(self, rid, area='US-', src=None):
        b = self.box or [[-108.765, 42.99], [-108.75, 42.99], [-108.75, 43.01], [-108.765, 43.01], [-108.765, 42.99]]
        return {'id': str(rid), 'name': self.name, 'attrs': self.attrs, 'rings': [b], 'layer': PADUS, 'url': PADUS + '/query?f=json',
                'label': 'USGS PAD-US', 'family': 'padus', 'html': PADUS + '/query?f=html'}
    def counties_at_pin(self, la, lo): return ({'56013': 'Fremont'}, '')
    def counties_of(self, rings): return ({'56013': 'Fremont'}, '')


S.KEYS.clear()
kf = str(S.LINKS / 'data/us-key/US-WY.json')
# Same shape as Sinks Canyon, with a name long enough to pass the Nov 6 short-name guard ('Sinks Canyon' alone is stopped by that guard on a
# re-solve; the real row was solved before it): park 'Bridgeport Hollow BLM Recreation Management Area', record 'Bridgeport Hollow'.
S.KEYS[kf] = {'parks': {'US-10890': {'n': 'Bridgeport Hollow BLM Recreation Management Area', 't': 'BLM Recreation Management Area',
                                      'm': [['292692', 'Bridgeport Hollow', 79, 'name (designation code ignored)']]}}}
pr = {'ref': 'US-10890', 'area': 'US-WY', 'areas': 'US-WY', 'name': 'Bridgeport Hollow BLM Recreation Management Area', 'type': 'BLM Recreation Management Area',
      'flags': {'PIN_WAY_OUT'}, 'why': 'test', 'ids': ['292692'], 'lat': str(PIN[0]), 'lon': str(PIN[1]), 'action': 'HOLD', 'src': 'pile', 'h': 'x', 'page': ''}
STATE_PARK = {'Des_Tp': 'SP', 'Own_Type': 'STAT', 'Own_Name': 'SPR'}
r = S.solve(dict(pr), OneRec(STATE_PARK), {}, {})
check(r['verdict'] == 'NEEDS-PERSON' and 'designation clash' in r['reason'] and 'State Park' in r['reason'],
      f"Sinks Canyon shape: a BLM park far from a state-park record is NEEDS-PERSON ({r['verdict']}: {r['reason'][:90]})")
check('POTA pin may be off' in r['pin_flag'], 'the pin flag is kept')
n_led = AL.LEDGER.exists() and len(AL.LEDGER.read_text(encoding='utf-8').strip().splitlines()) or 0
check(n_led == 0, 'no ledger join proposal was made for it')
r = S.solve(dict(pr), OneRec({'Des_Tp': 'SRMA', 'Own_Type': 'FED'}), {}, {})
check(r['verdict'] == 'SOLVED-JOIN', f"a BLM park far from a BLM-designated record still joins (rule 3 unchanged) ({r['verdict']})")
r = S.solve(dict(pr, name='Bridgeport Hollow State Park', type='State Park'), OneRec(STATE_PARK), {}, {})
check(r['verdict'] == 'SOLVED-JOIN', f"a state park against a state-park record still joins ({r['verdict']})")
r = S.solve(dict(pr), OneRec({}), {}, {})
check(r['verdict'] == 'SOLVED-JOIN', f"a live record with no designation fields: unchanged ({r['verdict']})")
inside = [[-108.9, 42.9], [-108.7, 42.9], [-108.7, 43.1], [-108.9, 43.1], [-108.9, 42.9]]
r = S.solve(dict(pr), OneRec(STATE_PARK, inside), {}, {})
check(r['verdict'] == 'SOLVED-JOIN', f"the pin inside the state-park record: still the two-agency join ({r['verdict']})")
os.environ['KPC_DESIGNATION_CLASH'] = 'off'
r = S.solve(dict(pr), OneRec(STATE_PARK), {}, {})
check(r['verdict'] == 'SOLVED-JOIN', f"KPC_DESIGNATION_CLASH=off gives the old answer ({r['verdict']})")
# the real name: 'Sinks Canyon' is a short name, so today's solver stops it with the Nov 6 guard even with the new check off
sk = dict(pr, name='Sinks Canyon BLM Recreation Management Area', ref='US-10891')
S.KEYS[kf]['parks']['US-10891'] = {'n': sk['name'], 't': sk['type'], 'm': [['292692', 'Sinks Canyon', 79, 'name (designation code ignored)']]}
r = S.solve(sk, OneRec(STATE_PARK, name='Sinks Canyon'), {}, {})
check(r['verdict'] == 'NEEDS-PERSON' and 'too short or generic' in r['reason'], f"the real Sinks Canyon names: the short-name guard stops it with the new check off ({r['reason'][:70]})")
os.environ.pop('KPC_DESIGNATION_CLASH')
r = S.solve(dict(sk), OneRec(STATE_PARK, name='Sinks Canyon'), {}, {})
check(r['verdict'] == 'NEEDS-PERSON' and 'designation clash' in r['reason'], 'with the new check on, the reason is the designation clash (clearer for the person)')

# ---------------------------------------------------------------- run(): off by default, report mode, auto untouched
def one_run(mode):
    root = pathlib.Path(tempfile.mkdtemp())
    (root / 'data/pile-solver').mkdir(parents=True)
    st0 = json.dumps({'version': S.VERSION, 'refs': {}, 'areas': {}, 'auto': False}, sort_keys=True)
    (root / 'data/pile-solver/state.json').write_text(st0, encoding='utf-8')
    if mode: os.environ['KPC_TYPE_PENALTY'] = mode
    else: os.environ.pop('KPC_TYPE_PENALTY', None)
    S.DATA = ROOT
    rows, stats, written = S.run(root, [dict(pr)], None, None, 0, 'backfill')
    os.environ.pop('KPC_TYPE_PENALTY', None)
    return root, rows, stats, written

# the penalty reads the weights from DATA (the repo); the offline run has no web, so the row is NEEDS-PERSON
r_off, rows_off, _s, w_off = one_run(None)
r_on, rows_on, _s2, w_on = one_run('report')
check(not (r_off / 'data/pile-solver/type-penalty.json').exists(), 'unset: no type-penalty.json')
side = r_on / 'data/pile-solver/type-penalty.json'
check(side.exists(), 'report: type-penalty.json is written')
if side.exists():
    j = json.loads(side.read_text(encoding='utf-8'))
    check(j['auto'] is False and all(e.get('auto') is False for e in j['rows']), 'every entry says auto false')
    check(len(j['rows']) == 1 and j['rows'][0]['ref'] == 'US-10890', 'one scored row')
check({k: v['verdict'] for k, v in rows_off.items()} == {k: v['verdict'] for k, v in rows_on.items()}, 'no verdict differs between off and report')
names_off = sorted(p.name for p in r_off.rglob('*') if p.is_file()); names_on = sorted(p.name for p in r_on.rglob('*') if p.is_file())
check(sorted(set(names_on) - set(names_off)) == ['type-penalty.json'], f'report adds only the side file ({sorted(set(names_on) - set(names_off))})')
for n in names_off:
    if n == 'state.json': continue
    a = next(r_off.rglob(n)).read_text(encoding='utf-8'); b = next(r_on.rglob(n)).read_text(encoding='utf-8')
    if a != b: check(False, f'{n} differs between off and report')
st = json.loads((r_on / 'data/pile-solver/state.json').read_text(encoding='utf-8'))
check(st.get('auto') is False, "state.json auto is still false after a report-mode run")
# an unwritable side path never skips the core outputs
import unittest.mock as M
with M.patch.object(TP, 'write_side', side_effect=OSError('read only')):
    r_bad, _rows, _s3, w_bad = (lambda: one_run('report'))()
check((r_bad / 'data/pile-solver/state.json').exists(), 'a failed side write does not skip state.json')
# MODE=auto with auto false is still a no-op
rows_a, stats_a, _w = S.run(tempfile.mkdtemp(), [dict(pr)], None, None, 0, 'auto')
check(stats_a.get('skipped') == 'auto off', 'MODE=auto with auto=false still does nothing')

sys.exit(0 if ok else 1)
