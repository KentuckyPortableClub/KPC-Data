#!/usr/bin/env python3
"""Nov 6 improvements v2.1 (Quality v2 grade MUST-ADD): KPC-Data's world overrides carry the 'no' for AU-8945 Scarborough State
Beach vs QLD Places FeatureServer/11 record 805 (Godwin Beach, 11.7 km from the pin), and kpc_key_approved.py never joins a record a
world 'no' names (so the next scoreboard run cannot add record 805 back). Applies BEFORE improvements 06 (the label restore)."""
import json, os, pathlib, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)
e = json.load(open(ROOT / 'data/world-key/overrides.json', encoding='utf-8'))['parks'].get('AU-8945') or {}
check('AU-8945 no = ["805", "Godwin Beach", "Scarborough Beach"], verify-then-fix', e.get('no') == ['805', 'Godwin Beach', 'Scarborough Beach'] and e.get('decided_by') == 'Brandon standing rule 2026-11-05 verify-then-fix')
td = pathlib.Path(tempfile.mkdtemp(prefix='kpc-au8945-'))
try:
    (td / 'data/world-key').mkdir(parents=True); (td / 'data/waiting/questions').mkdir(parents=True)
    L = 'https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Location/Places/FeatureServer/11'
    json.dump({'parks': {'AU-8945': e, 'AU-0002': {'no': ['Old Name'], 'why': 'Oct 30 name-only NO'}}}, open(td / 'data/world-key/overrides.json', 'w'))
    json.dump({'cc': 'AU', 'parks': {'AU-8945': {'n': 'Scarborough State Beach', 'm': [], 'c': []}, 'AU-0001': {'n': 'Other Beach', 'm': [], 'c': []}, 'AU-0002': {'n': 'Old', 'm': [], 'c': []}}}, open(td / 'data/world-key/AU.json', 'w'))
    json.dump({'questions': [{'ref': 'AU-8945', 'answer': 'YES', 'layer': L, 'record': '805', 'record_name': 'Scarborough Beach'},
                             {'ref': 'AU-0001', 'answer': 'YES', 'layer': L, 'record': '806', 'record_name': 'Other Beach'},
                             {'ref': 'AU-0002', 'answer': 'YES', 'layer': L, 'record': '807', 'record_name': 'Old Name'}]}, open(td / 'data/waiting/questions/layers.json', 'w'))
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_key_approved.py')], cwd=td, capture_output=True, text=True, timeout=120, env=dict(os.environ, LINKS=str(td / 'nolinks')))
    P = json.load(open(td / 'data/world-key/AU.json'))['parks']
    check('kpc_key_approved.py: the YES on record 805 for AU-8945 is NOT joined (overrides no)', P['AU-8945']['m'] == [])
    check('kpc_key_approved.py: another YES on the same layer still joins (only the no is skipped)', [x[0] for x in P['AU-0001']['m']] == [806])
    check("an older name-only 'no' without decided_by does not block a later YES (a person's call, listed in NOTES)", [x[0] for x in P['AU-0002']['m']] == [807])
finally: shutil.rmtree(td, ignore_errors=True)
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
