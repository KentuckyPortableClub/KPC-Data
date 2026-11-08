"""Freeze rule (Brandon Nov 8 1:50 PM CST): a newer build with Quality's KEY YES replaces the held build; nothing of the old build goes live."""
import json, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_key_supersede as KS
bad = 0
def check(ok, what):
    global bad
    print(('PASS ' if ok else 'FAIL ') + what); bad += (not ok)
A = {'items': [{'what': 'us-key', 'build': 'US-42504172086', 'chat11': 'KEY YES (Quality regrade Nov 8)', 'date': '2026-11-08', 'time': '1:00 PM'},
               {'what': 'us-key', 'build': 'US-9', 'chat11': 'YES/NO'}, {'what': 'world-key', 'build': 'W-1', 'chat11': 'YES'}]}
check(bool(KS.reason(A, 'us-key', 'US-42230313177', 'US-42504172086')), 'newer build with KEY YES replaces the held build')
check(not KS.reason(A, 'us-key', 'US-42230313177', 'US-99'), 'newer build without a verdict: the held build stays (Nov 2 freeze)')
check(not KS.reason(A, 'us-key', 'US-42230313177', 'US-9'), 'a mixed verdict is not a YES')
check(not KS.reason(A, 'us-key', 'US-42504172086', 'US-42504172086'), 'same build: nothing to replace')
check(not KS.reason(A, 'ca-key', 'CA-1', 'W-1'), "another key's YES does not count")
check(not KS.reason({}, 'us-key', 'US-1', 'US-2'), 'no approved.json: held build stays')
with tempfile.TemporaryDirectory() as t:
    d = pathlib.Path(t, 'data/waiting/in/data/us-key'); d.mkdir(parents=True)
    (d / 'US-KY.json').write_text('{}'); (d / 'index.json').write_text('{"build":"US-42230313177"}')
    rep = KS.log_replaced('us-key', 'US-42230313177', 'US-42504172086', 'why', root=t)
    f = pathlib.Path(t, 'data/status/key-copy/replaced-us-key.json')
    check(f.exists() and rep['went_live'] == 0 and len(rep['files']) == 2 and all(x['sha1'] for x in rep['files']), 'old build logged (files, sha1), none of it live')
    check(d.joinpath('US-KY.json').exists(), 'logging deletes nothing')
wf = (ROOT / '.github/workflows/kpc-copy-from-links.yml').read_text(encoding='utf-8')
i, j = wf.find('import kpc_key_supersede as KS'), wf.find("print(f'::notice title=Copy::{k} build {hb} is held for chat 11")
check(0 < i < wf.find('if hb and sup:') < j, 'copy workflow asks the newer-YES test before the held-build hold')
check('KS.log_replaced(k, hb, nb0, sup)' in wf, 'copy workflow logs the replaced build')
check(subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_key_supersede.py')], capture_output=True).returncode == 0, 'selftest')
print('ALL PASS' if not bad else 'SOME FAILED'); sys.exit(1 if bad else 0)
