#!/usr/bin/env python3
"""24 Nov 2026 (owner approved D; review fix 24 Nov): one settled-answers file, IDs first,
shared fingerprint, record number only a hint, S4 lists a missing saved record.
Invented parks only. No network. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
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


BOX = [-88.5004, 44.4996, -88.4996, 44.5004]
REC = {'name': 'Invented Marsh State Wildlife Area', 'acres': 500.0, 'box': BOX, 'OBJECTID': 'sgzza1'}
FP = SA.fingerprint_of(REC)

check('name_key keeps letters and digits only (Camel\'s Hump = Camels Hump)',
      SA.name_key("Camel's Hump") == SA.name_key('Camels Hump') == 'camelshump')
check('with no agency id, the fingerprint is a name hash + acres + box, never the display name',
      FP and FP['kind'] == 'name-acres-box' and FP.get('name_hash') == SA.name_hash(REC['name'])
      and 'name' not in FP and 'Invented' not in json.dumps(FP) and FP['acres'] == 500.0)
check('an agency ID carries its layer; without a layer it is not used as the fingerprint',
      SA.fingerprint_of({**REC, 'LinkID': 'SPRK433', 'layer': 'sgzza'})
      == {'kind': 'agency-id', 'layer': 'sgzza', 'id': 'SPRK433'}
      and SA.fingerprint_of({**REC, 'LinkID': 'SPRK433'}).get('kind') == 'name-acres-box')
check('the same agency ID on two layers does not match',
      not SA.fingerprints_match(
          SA.fingerprint_of({**REC, 'LinkID': 'SPRK433', 'layer': 'sgzza'}),
          SA.fingerprint_of({**REC, 'LinkID': 'SPRK433', 'layer': 'sgzzb'})))
check('the record number is not the fingerprint (it is only a hint)',
      SA.fingerprint_of(REC) != {'kind': 'agency-id', 'id': 'sgzza1'}
      and 'sgzza1' not in json.dumps(SA.fingerprint_of(REC)))

# Boxes: 42.1234 vs 42.1236 round to different 0.001° cells but each side is within 0.002°.
almost = {**REC, 'box': [x + 0.0002 for x in BOX]}
check('boxes that miss exact 0.001° rounding still match when each side is within 0.002°',
      SA.fingerprints_match(FP, SA.fingerprint_of(almost)))
# overlap even when sides differ by more than 0.002 (a slightly larger box around the same land)
overlap = {**REC, 'box': [BOX[0] - 0.01, BOX[1] - 0.01, BOX[2] + 0.01, BOX[3] + 0.01]}
check('overlapping boxes match even when the sides are more than 0.002° apart',
      SA.fingerprints_match(FP, SA.fingerprint_of(overlap)))
moved = {**REC, 'box': [-87.0, 45.0, -86.9, 45.1]}
check('a box with no overlap and sides more than 0.002° apart does not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of(moved)))

near = {**REC, 'acres': 530.0, 'box': [-88.5001, 44.4999, -88.4999, 44.5001]}
far_acres = {**REC, 'acres': 600.0}
check('acres within 10% and a close box still match, even if the record number changed, and apostrophes in the name do not break it',
      SA.fingerprints_match(FP, SA.fingerprint_of({**near, 'OBJECTID': 'sgzza99', 'name': "Invented Marsh State Wildlife Area"}))
      and SA.fingerprints_match(SA.fingerprint_of({**REC, 'name': "Invented Marsh State Wildlife Area"}),
                               SA.fingerprint_of({**REC, 'name': 'Invented Marsh State Wildlife Area'})))
check('acres more than 10% apart do not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of(far_acres)))
check('a different official name does not match',
      not SA.fingerprints_match(FP, SA.fingerprint_of({**REC, 'name': 'Invented Pond Wildlife Area'})))

ans = {'park': 'US-9001', 'status': 'settled', 'record': 'sgzza1', 'fingerprint': FP}
saved = {'sgzza1': REC}
check('reuse when the named record is in the saved copy and the fingerprint still matches',
      SA.decide_reuse(ans, saved)['action'] == 'reuse')
check('redo when a settled named record is present but the land changed',
      SA.decide_reuse(ans, {'sgzza1': far_acres})['action'] == 'redo')

# S4 + many pieces
s4 = SA.decide_reuse(ans, {})
check('S4: a missing named record is listed, not redone, not dropped',
      s4['action'] == 'missing-saved-record' and s4['record'] == 'sgzza1' and s4['park'] == 'US-9001')
s4b = SA.decide_reuse(ans, {'sgzza99': {**REC, 'OBJECTID': 'sgzza99'}})
check('S4: exactly one same-fingerprint new number is a hint, not an auto-reuse',
      s4b['action'] == 'missing-saved-record' and s4b['maybe_new_record'] == 'sgzza99'
      and s4b['maybe_new_records'] == ['sgzza99'])
many = {f'sgzzp{i}': {**REC, 'OBJECTID': f'sgzzp{i}'} for i in range(40)}
s4c = SA.decide_reuse(ans, many)
check('S4: many pieces sharing one fingerprint return all of them, and not a single first piece',
      s4c['action'] == 'missing-saved-record' and s4c['maybe_new_record'] is None
      and len(s4c['maybe_new_records']) == 40 and 'sgzzp0' in s4c['maybe_new_records'])
check('the S4 list returns every missing named record and does not drop the answer',
      [d['park'] for d in SA.list_missing_saved_records([ans], {})] == ['US-9001'])

# person-no never redo
pno = {'park': 'US-9001', 'status': 'person-no', 'record': 'sgzza1', 'fingerprint': FP}
check('person-no is listed, never redone, when the land changed',
      SA.decide_reuse(pno, {'sgzza1': far_acres})['action'] == 'list-for-person')
check('person-no is listed, never redone, when the named record is missing',
      SA.decide_reuse(pno, {})['action'] == 'list-for-person')
check('person-no still reuses when the named record and fingerprint still match',
      SA.decide_reuse(pno, saved)['action'] == 'reuse')

# File: IDs first, no display name on the row or in the fingerprint
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
    badfp = {'answers': [{'park': 'US-9001', 'status': 'settled', 'record': 'sgzza1',
                          'fingerprint': {**FP, 'name': 'Invented Marsh State Wildlife Area'}}]}
    path.write_text(json.dumps(badfp), encoding='utf-8')
    try:
        SA.load_answers(path)
        named_fp = False
    except ValueError as e:
        named_fp = 'name_hash' in str(e) or 'display name' in str(e)
    check('the loader refuses a display name inside the fingerprint', named_fp)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
