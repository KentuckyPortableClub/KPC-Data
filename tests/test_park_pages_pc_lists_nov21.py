#!/usr/bin/env python3
"""Page reader on the PC, 21 Nov 2026: a read given ONLY the private lists (no --areas) follows their order, and a saved state
never keeps the private read order (the parks left are saved sorted). Invented parks, offline fixtures (no request leaves).
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


REFS = ('US-9001', 'US-9002', 'US-9003', 'US-9004', 'US-9005', 'US-9006')
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: {'name': f'Invented Park {r[-1]}', 'qsos': 10 - i,
                                                                'website': f'https://parks.invented.example/{r}'}
                                                            for i, r in enumerate(REFS)}}), encoding='utf-8')
    fx = t / 'fx'; fx.mkdir()
    (fx / 'manifest.json').write_text(json.dumps({'pages': {}}), encoding='utf-8')
    (t / 'pri.csv').write_text('park\nUS-9005\nUS-9003\n', encoding='utf-8')

    def run(out, *extra):
        return subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'),
                               '--out', str(out), '--state', str(out / 'state.json'), '--fixtures', str(fx / 'manifest.json'),
                               '--today', '2026-11-21', '--quiet', *extra], capture_output=True, text=True)

    out = t / 'out1'
    r = run(out, '--priority-file', str(t / 'pri.csv'), '--max-parks', '2')
    facts = json.loads((out / 'facts' / 'US-ZZ.json').read_text()).get('parks', {}) if (out / 'facts' / 'US-ZZ.json').is_file() else {}
    check('with only --priority-file, the two priority parks are the two read', r.returncode == 0 and set(facts) == {'US-9005', 'US-9003'})
    st = json.loads((out / 'state.json').read_text()) if (out / 'state.json').is_file() else {}
    left = st.get('left') or []
    check('the parks left are all the others', set(left) == set(REFS) - {'US-9005', 'US-9003'})
    check('the parks left are saved sorted, not in the private read order', left == sorted(left))

    out = t / 'out2'
    (t / 'pri2.csv').write_text('park\nUS-9006\nUS-9001\nUS-9004\n', encoding='utf-8')
    r = run(out, '--priority-file', str(t / 'pri2.csv'), '--max-parks', '1')
    st = json.loads((out / 'state.json').read_text()) if (out / 'state.json').is_file() else {}
    left = st.get('left') or []
    check('a stopped run with a private list keeps the parks left sorted', r.returncode == 0 and left and left == sorted(left)
          and 'US-9006' not in left)
    wl = (out / 'worklist.json').read_text() if (out / 'worklist.json').is_file() else ''
    check('the saved worklist still names no private-list park', wl and not any(x in wl for x in ('US-9006', 'US-9001', 'US-9004')))

# A PC kit: the scripts in a plain folder's scripts/, the private list in a folder beside the kit (no git anywhere).
import shutil
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    kit = t / 'bots' / 'page-reader'
    shutil.copytree(ROOT / '.github' / 'scripts', kit / 'scripts', ignore=shutil.ignore_patterns('draft', '__pycache__'))
    data = kit / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: {'name': r, 'website': f'https://parks.invented.example/{r}'}
                                                            for r in REFS}}), encoding='utf-8')
    (kit / 'fx.json').write_text(json.dumps({'pages': {}}), encoding='utf-8')
    priv = t / 'bots' / 'PRIVATE'; priv.mkdir()
    (priv / 'priority-parks.csv').write_text('park\nUS-9004\n', encoding='utf-8')
    r = subprocess.run([sys.executable, '-B', str(kit / 'scripts' / 'kpc_park_pages.py'), 'read', '--data', str(kit / 'data'),
                        '--out', str(kit / 'out'), '--fixtures', str(kit / 'fx.json'), '--today', '2026-11-21', '--quiet',
                        '--priority-file', str(priv / 'priority-parks.csv'), '--max-parks', '1'], capture_output=True, text=True)
    f = kit / 'out' / 'facts' / 'US-ZZ.json'
    check('a PC kit reads a private list kept beside it (no git there), and reads that park first',
          r.returncode == 0 and f.is_file() and set(json.loads(f.read_text()).get('parks', {})) == {'US-9004'})
    (t / 'bots' / '.git').mkdir()
    r = subprocess.run([sys.executable, '-B', str(kit / 'scripts' / 'kpc_park_pages.py'), 'read', '--data', str(kit / 'data'),
                        '--out', str(kit / 'out2'), '--fixtures', str(kit / 'fx.json'), '--today', '2026-11-21', '--quiet',
                        '--priority-file', str(priv / 'priority-parks.csv'), '--max-parks', '1'], capture_output=True, text=True)
    check('the same kit inside a git folder refuses the list', r.returncode != 0 and 'must not live inside a git repository' in r.stderr)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
