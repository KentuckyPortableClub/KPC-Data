#!/usr/bin/env python3
"""Next round C3 (rule 21; Brandon's yes relayed via Super, Nov 5): an override 'no' is enforced on name joins in the pile solver.
A key name join (NAME_JOIN 'same name + pin inside', alias) whose record a person ruled out in overrides.json, by id OR by the exact
record name (kpc_key_rules.is_no, as the key reads it), is never proposed again; a live record whose name is a 'no' is dropped too.
Offline (fake key rows and a fake record reader). Needs LINKS (a KPC-Links checkout) for the solver import."""
import os, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent.parent
os.chdir(HERE); sys.path.insert(0, '.github/scripts')
ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)
import kpc_pile_solver as S   # noqa: E402
P = {'ref': 'US-0001', 'name': 'Sample Creek State Park', 'area': 'US-ZZ', 'lat': '37.5', 'lon': '-85.5', 'type': 'State Park', 'flags': {'NO_OUTLINE'},
     'why': 'test', 'action': 'FIND', 'ids': [], 'page': ''}
JOIN = ['pad1', 'Sample Creek State Park', 12.0, 'same name (POTA writes the kind into the name) + pin inside']
KEY = {}
S.key_row = lambda area, ref: KEY.get(ref, {})   # noqa: E731
class F:   # fake reader: the record holds the pin
    def __init__(s, name): s.name = name
    def record(s, rid, area): return {'id': str(rid), 'name': s.name, 'attrs': {}, 'rings': [[[-85.6, 37.4], [-85.4, 37.4], [-85.4, 37.6], [-85.6, 37.6], [-85.6, 37.4]]],
                                      'layer': 'https://example.gov/x/MapServer/0', 'url': '', 'label': 'State parks (official)', 'family': 'state', 'html': 'https://example.gov/x'}
    def counties_at_pin(s, la, lo): return {'1': 'Test County'}, ''
    def counties_of(s, rings): return {'1': 'Test County'}, ''
KEY['US-0001'] = {'m': [JOIN]}
base = S.solve(dict(P), F('Sample Creek State Park'), {}, {})
check(base['verdict'] == 'SOLVED-JOIN', f"no override: the name join is proposed ({base['verdict']}: {base['reason'][:80]})")
for label, ov in (('by id', {'no': ['pad1']}), ('by exact name', {'no': ['Sample Creek State Park']}), ('by name, other case and a trailing space (the key folds case and trims the ends; inner spaces must match)', {'no': ['SAMPLE CREEK STATE PARK ']})):
    r = S.solve(dict(P), F('Sample Creek State Park'), {'US-0001': ov}, {})
    check(r['verdict'] == 'NEEDS-PERSON' and 'rule 21' in r['reason'] and r['record_id'] == '', f"override 'no' {label}: never proposed ({r['verdict']}: {r['reason'][:90]})")
    r = S.solve(dict(P), None, {'US-0001': ov}, {})
    check(r['verdict'] == 'NEEDS-PERSON' and 'rule 21' in r['reason'], f"override 'no' {label}, offline run: same ({r['reason'][:60]})")
# a 'no' on one of two joins leaves the other
KEY['US-0001'] = {'m': [JOIN, ['pad2', 'Sample Creek State Park Addition', 3.0, 'same name']]}
r = S.solve(dict(P), None, {'US-0001': {'no': ['pad2']}}, {})
check('rule 21' not in r['reason'], f"a 'no' on one record leaves the other join to the normal checks ({r['reason'][:70]})")
# the live record's own name is a 'no' (the record was renamed on its layer since the key was built)
KEY['US-0001'] = {'m': [['pad3', 'Sample Creek State Park', 0, 'same name']]}
r = S.solve(dict(P), F('Sample Creek State Park Annex'), {'US-0001': {'no': ['Sample Creek State Park Annex']}}, {})
check(r['verdict'] == 'NEEDS-PERSON' and 'rule 21' in r['reason'], f"live record named in a 'no': dropped, never joined ({r['reason'][:90]})")
r = S.solve(dict(P), F('Sample Creek State Park'), {'US-0001': {'no': ['Other Place']}}, {})   # live name = key name
check(r['verdict'] == 'SOLVED-JOIN', f"a 'no' on another name does not block the join ({r['verdict']})")
# the pile ids fallback honours a 'no' too
KEY['US-0001'] = {}
r = S.solve(dict(P, ids=['pad9']), None, {'US-0001': {'no': ['pad9']}}, {})
check(r['verdict'] == 'NEEDS-PERSON' and 'no joined record left' in r['reason'], f"pile ids: a 'no' id is not used ({r['reason'][:60]})")
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
