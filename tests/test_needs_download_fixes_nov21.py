#!/usr/bin/env python3
"""needs-download status fixes, 21 Nov 2026: the open rows whose layer is already on the box (a hand file on boundary-cache) are
closed by merging .github/needs-download-fixes-nov21.json; nothing else changes and nothing is downloaded. Works on a temp copy
of the list (the live data/needs-download.json is only read). Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / '.github/needs-download-fixes-nov21.json'
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


fix = json.loads(FIX.read_text(encoding='utf-8'))
check('every fix row closes a row (status done) and names the file on the box',
      fix['rows'] and all(r['status'] == 'done' and 'already on the box' in r['note'] and '.geojson.gz' in r['note'] for r in fix['rows']))
check('the fixes name no park', not re.search(r'\b(?:US|CA)-\d{4,5}\b', json.dumps(fix)))
live = ROOT / 'data/needs-download.json'
live_before = live.read_bytes() if live.is_file() else None
with tempfile.TemporaryDirectory() as t:
    copy = pathlib.Path(t) / 'needs-download.json'
    if live.is_file():
        shutil.copy(live, copy)
    else:   # a checkout without data: the same rows, as they stood on 21 Nov
        rows = [dict(r, status='open', added='2026-11-10') for r in fix['rows']]
        rows.append({'id': 'US-OH|zzohio', 'area': 'US-OH', 'layer': 'zzohio', 'status': 'open', 'who': 'person', 'added': '2026-11-10'})
        copy.write_text(json.dumps({'format': 1, 'rows': rows}), encoding='utf-8')
    before = json.loads(copy.read_text(encoding='utf-8'))
    env = dict(os.environ, KPC_NEEDS_FILE=str(copy))
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_needs_download.py'), 'merge', str(FIX)],
                       capture_output=True, text=True, env=env, cwd=str(ROOT))
    after = json.loads(copy.read_text(encoding='utf-8'))
    b = {x['id']: x for x in before['rows']}
    a = {x['id']: x for x in after['rows']}
    ids = {x['id'] for x in fix['rows']}
    check('the merge runs', r.returncode == 0)
    check('the fixed rows are done', all(a[i]['status'] == 'done' for i in ids if i in a))
    check('no other row changed status', all(a[k]['status'] == b[k]['status'] for k in b if k not in ids))
    check('no row was added or lost', set(a) == set(b))
    check('the Ohio and Yukon rows stay open (no saved file was found)',
          all(a[k]['status'] == b[k]['status'] for k in b if a[k].get('area') in ('US-OH', 'CA-YT')))
    check('the live list was not touched', (live.read_bytes() if live.is_file() else None) == live_before)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
