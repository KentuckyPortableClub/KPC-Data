#!/usr/bin/env python3
"""Nov 16: the morning list must show the latest check, not a stale change-log
line. The five WWFF files were re-checked and now PASS, but today.md still
showed a Nov 2 checker crash because it used the last line of verdicts.jsonl,
and that PASS never landed in the log. A current PASS (or any new verdict)
replaces the old crash on the next run. An owner RELEASE on a key file is kept
when the latest check is only a PASS: the checker never writes RELEASE. Offline: a temp waiting room only,
nothing in the repo is written."""
import importlib.util, json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def load_mod(data, name):
    os.environ['DATA'] = str(data)
    sys.path.insert(0, str(HERE / '.github' / 'scripts'))
    # a fresh load so W / DATA are taken from this env
    path = HERE / '.github' / 'scripts' / (name + '.py')
    spec = importlib.util.spec_from_file_location(name + '_' + data.name, path)
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    return M


def setup():
    data = pathlib.Path(tempfile.mkdtemp(prefix='kpc-wwff-today-'))
    w = data / 'data' / 'waiting'
    inn = w / 'in' / 'data' / 'wwff'
    inn.mkdir(parents=True)
    # five list-shaped WWFF files still sitting in the inbox
    for name in ('D4FF', 'KFF', 'ONFF', 'PYFF', 'VEFF'):
        (inn / f'{name}.json').write_text('[["%s-0001","Park",1,2,"","","CT"]]' % name, encoding='utf-8')
    # CTFF is a real current HOLD in the latest check
    (inn / 'CTFF.json').write_text('[]', encoding='utf-8')
    crash = "F-4 checker error: AttributeError: 'list' object has no attribute 'get'"
    # stale change log: last line for the five is the Nov 2 crash
    lines = []
    for name in ('D4FF', 'KFF', 'ONFF', 'PYFF', 'VEFF', 'CTFF'):
        lines.append(json.dumps({'date': '2026-11-02T08:52Z', 'kind': 'wwff', 'path': f'data/wwff/{name}.json',
                                 'verdict': 'HOLD', 'why': [crash], 'notes': []}, ensure_ascii=False))
    (w / 'verdicts.jsonl').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # latest complete check: the five PASS, CTFF still held for a row drop
    results = []
    for name in ('D4FF', 'KFF', 'ONFF', 'PYFF', 'VEFF'):
        results.append({'path': f'data/wwff/{name}.json', 'kind': 'wwff', 'verdict': 'PASS', 'why': [], 'notes': []})
    results.append({'path': 'data/wwff/CTFF.json', 'kind': 'wwff', 'verdict': 'HOLD',
                    'why': ['F-W2 rows 702 -> 280 (under 80% of the saved list)'], 'notes': []})
    (w / 'verdicts.json').write_text(json.dumps({'checked': '2026-11-17T04:16Z', 'results': results}, indent=1), encoding='utf-8')
    return data, w


def row_for(text, name):
    for ln in text.splitlines():
        if f'data/wwff/{name}.json' in ln and ln.startswith('|'):
            return ln
    return ''


data, w = setup()
T = load_mod(data, 'kpc_waiting_today')
T.main()
md = (w / 'today.md').read_text(encoding='utf-8')
for name in ('D4FF', 'KFF', 'ONFF', 'PYFF', 'VEFF'):
    ln = row_for(md, name)
    check('PASS' in ln and 'checker error' not in ln,
          f'{name}: morning list shows the latest PASS, not the stale crash ({ln[:120]})')
ln = row_for(md, 'CTFF')
check('HOLD' in ln and 'F-W2' in ln, f'CTFF: a current HOLD is still listed ({ln[:140]})')

# with no verdicts.json, the change log is still used (fallback)
data2, w2 = setup()
(w2 / 'verdicts.json').unlink()
T2 = load_mod(data2, 'kpc_waiting_today')
T2.main()
md2 = (w2 / 'today.md').read_text(encoding='utf-8')
check('checker error' in row_for(md2, 'D4FF') and 'HOLD' in row_for(md2, 'D4FF'),
      'with no current check file, the change-log line is still used')

# a failed change-log write must not mark lastv updated, so the next run retries
WR = load_mod(data, 'kpc_waiting_room')
lastv = {}
row = {'kind': 'wwff', 'path': 'data/wwff/D4FF.json', 'verdict': 'PASS', 'why': [], 'notes': []}


def boom(*a, **k):
    raise OSError('disk full')


WR.append_jsonl_gz = boom
wrote = WR.record_verdict_change(lastv, row, '2026-11-16T22:00Z')
check(wrote is False and lastv == {},
      'if the change-log write fails, lastv is left unchanged so the next run tries again')

# a successful write records the new PASS
data3, w3 = setup()
WR3 = load_mod(data3, 'kpc_waiting_room')
WR3.W = w3
lastv3 = {'data/wwff/D4FF.json': json.dumps({'kind': 'wwff', 'notes': [], 'path': 'data/wwff/D4FF.json',
                                            'verdict': 'HOLD', 'why': ["F-4 checker error: AttributeError: 'list' object has no attribute 'get'"]},
                                           sort_keys=True, ensure_ascii=False)}
wrote3 = WR3.record_verdict_change(lastv3, row, '2026-11-16T22:00Z')
# the log should now end with PASS (plain or gz)
from kpc_json_any import iter_jsonl_any
log = [r for r in iter_jsonl_any(w3 / 'verdicts.jsonl') if r.get('path') == 'data/wwff/D4FF.json']
check(wrote3 is True and json.loads(lastv3['data/wwff/D4FF.json'])['verdict'] == 'PASS'
      and log and log[-1].get('verdict') == 'PASS' and log[-1].get('date') == '2026-11-16T22:00Z',
      f'a later PASS is appended to the change log and remembered ({log[-1] if log else None})')

# the owner's RELEASE on a key file must stay RELEASE when the latest check
# is only a PASS (the checker never writes RELEASE; preferring it used to
# turn the approval into PASS on the morning list). A later HOLD still shows.
def setup_release():
    data = pathlib.Path(tempfile.mkdtemp(prefix='kpc-today-release-'))
    w = data / 'data' / 'waiting'
    inn = w / 'in' / 'data' / 'us-key'
    inn.mkdir(parents=True)
    for name in ('US-AK', 'US-AZ', 'US-WA'):
        (inn / (name + '.json')).write_text('{}', encoding='utf-8')
    lines = [
        json.dumps({'date': '2026-11-11T18:04Z', 'kind': 'release', 'path': 'data/us-key/US-AK.json',
                    'verdict': 'RELEASE', 'by': 'KentuckyPortableClub'}, ensure_ascii=False),
        json.dumps({'date': '2026-11-11T18:04Z', 'kind': 'release', 'path': 'data/us-key/US-WA.json',
                    'verdict': 'RELEASE', 'by': 'KentuckyPortableClub'}, ensure_ascii=False),
        json.dumps({'date': '2026-11-10T12:00Z', 'kind': 'key', 'path': 'data/us-key/US-AZ.json',
                    'verdict': 'PASS', 'why': [], 'notes': []}, ensure_ascii=False),
    ]
    (w / 'verdicts.jsonl').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    results = [
        {'path': 'data/us-key/US-AK.json', 'kind': 'key', 'verdict': 'PASS', 'why': [], 'notes': []},
        {'path': 'data/us-key/US-WA.json', 'kind': 'key', 'verdict': 'HOLD',
         'why': ['F-O1 outlines 10 -> 8 (more than 1% lost)'], 'notes': []},
        {'path': 'data/us-key/US-AZ.json', 'kind': 'key', 'verdict': 'PASS', 'why': [], 'notes': []},
    ]
    (w / 'verdicts.json').write_text(json.dumps({'checked': '2026-11-17T04:16Z', 'results': results}, indent=1), encoding='utf-8')
    return data, w


def last_check(text, rel):
    for ln in text.splitlines():
        if rel in ln and ln.startswith('|'):
            parts = [x.strip() for x in ln.split('|')]
            return parts[4] if len(parts) > 4 else ''
    return ''


dataR, wR = setup_release()
TR = load_mod(dataR, 'kpc_waiting_today')
TR.main()
mdR = (wR / 'today.md').read_text(encoding='utf-8')
check(last_check(mdR, 'data/us-key/US-AK.json') == 'RELEASE',
      f'an owner RELEASE on a key file stays RELEASE when the latest check is PASS ({last_check(mdR, "data/us-key/US-AK.json") or mdR[:200]})')
check(last_check(mdR, 'data/us-key/US-WA.json') == 'HOLD' and 'F-O1' in mdR,
      f'a later HOLD after a RELEASE is still listed as HOLD ({last_check(mdR, "data/us-key/US-WA.json")})')
check(last_check(mdR, 'data/us-key/US-AZ.json') == 'PASS',
      f'a key file that was never RELEASE still shows PASS ({last_check(mdR, "data/us-key/US-AZ.json")})')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
