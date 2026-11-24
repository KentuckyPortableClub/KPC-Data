#!/usr/bin/env python3
"""24 Nov 2026 (owner approved D): one settled-answers file, IDs first, shared fingerprint,
record number only a hint, S4 lists a missing saved record. Invented parks only. No network.
Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))


def _no_net(*a, **k):
    raise RuntimeError('no network in tests')


socket.socket.connect = _no_net
import kpc_settled_answers as SA  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


# Invented land: a 500-acre square around (-88.500, 44.500)
BOX = [-88.5004, 44.4996, -88.4996, 44.5004]
REC = {'name': 'Invented Marsh State Wildlife Area', 'acres': 500.0, 'box': BOX, 'OBJECTID': 'sgzza1'}
FP = SA.fingerprint_of(REC)

check('with no agency id, the fingerprint is name + acres + box to 0.001°',
      FP and FP['kind'] == 'name-acres-box' and FP['name'] == 'invented marsh state wildlife area'
      and FP['box'] == [-88.5, 44.5, -88.5, 44.5] and FP['acres'] == 500.0)
check('a LinkID is preferred over the record number',
      SA.fingerprint_of({**REC, 'LinkID': 'UNIT:4471'}) == {'kind': 'agency-id', 'id': 'UNIT:4471'})
check('the record number is not the fingerprint (it is only a hint)',
      SA.fingerprint_of(REC) != {'kind': 'agency-id', 'id': 'sgzza1'}
      and 'sgzza1' not in json.dumps(SA.fingerprint_of(REC)))

near = {**REC, 'acres': 530.0, 'box': [-88.5001, 44.4999, -88.4999, 44.5001]}  # +6%, box still 0.001
far_acres = {**REC, 'acres': 600.0}  # +20%
moved = {**REC, 'box': [-88.6, 44.5, -88.5, 44.6]}
check('acres within 10% and the same rounded box still match, even if the record number changed',
      SA.fingerprints_match(FP, SA.fingerprint_of({**near, 'OBJECTID': 'sgzza99'})))
check('acres more than 10% apart do not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of(far_acres)))
check('a box that rounds to a different 0.001° cell does not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of(moved)))
check('a different official name does not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of({**REC, 'name': 'Invented Pond Wildlife Area'})))

ans = {'park': 'US-9001', 'status': 'settled', 'record': 'sgzza1', 'fingerprint': FP}
saved = {'sgzza1': REC}
check('reuse when the named record is in the saved copy and the fingerprint still matches',
      SA.decide_reuse(ans, saved)['action'] == 'reuse')
check('redo when the named record is present but the land changed',
      SA.decide_reuse(ans, {'sgzza1': far_acres})['action'] == 'redo')

# S4
s4 = SA.decide_reuse(ans, {})
check('S4: a missing named record is listed, not redone, not dropped',
      s4['action'] == 'missing-saved-record' and s4['record'] == 'sgzza1' and s4['park'] == 'US-9001')
s4b = SA.decide_reuse(ans, {'sgzza99': {**REC, 'OBJECTID': 'sgzza99'}})
check('S4: a same-fingerprint new number is a hint only, not an auto-reuse',
      s4b['action'] == 'missing-saved-record' and s4b['maybe_new_record'] == 'sgzza99')
check('the S4 list returns every missing named record and does not drop the answer',
      [d['park'] for d in SA.list_missing_saved_records([ans], {})] == ['US-9001'])

# File: IDs first, no display name on the row
payload = {'about': 'invented test file', 'answers': [ans]}
with tempfile.TemporaryDirectory() as td:
    path = pathlib.Path(td) / 'settled-answers.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    loaded = SA.load_answers(path)
    check('a valid IDs-first file loads', loaded['answers'][0]['park'] == 'US-9001')
    bad = {'answers': [{'park': 'US-9001', 'status': 'settled', 'record': 'sgzza1',
                        'fingerprint': FP, 'name': 'Invented Marsh State Wildlife Area'}]}
    path.write_text(json.dumps(bad), encoding='utf-8')
    try:
        SA.load_answers(path)
        named = False
    except ValueError as e:
        named = 'display name' in str(e)
    check('the loader refuses a park display name on the row', named)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
