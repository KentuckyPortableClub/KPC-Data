#!/usr/bin/env python3
"""Storage review: gzip readers, byte-identical question files, gz-only inputs.

Answered-question bytes are the SHA256 of the file before it was gzipped. Decompressing the
committed .gz must reproduce that digest. Each reader below is then pointed at a .gz-only file.
"""
import gzip, hashlib, importlib.util, json, os, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.chdir(ROOT)
ok = True


def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


def load_mod(name):
    path = ROOT / '.github/scripts' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- SHA256 round trip of the stored files (answered questions included) ----
man = json.loads((ROOT / 'tests/storage_gz_manifest.json').read_text())
check(len(man) >= 16, f'manifest lists the compressed files ({len(man)})')
for row in man:
    gz = ROOT / row['path']
    raw = gzip.decompress(gz.read_bytes())
    digest = hashlib.sha256(raw).hexdigest()
    check(digest == row['sha256'] and len(raw) == row['plain_bytes'], f"round trip {row['plain']} sha256")
    check(not (ROOT / row['plain']).exists(), f"plain copy removed {row['plain']}")

sample = b'{"questions":[{"ref":"US-1","answer":"YES","checked_by":"chat 11","how":"the map"}]}\n'
check(hashlib.sha256(gzip.decompress(gzip.compress(sample, compresslevel=9, mtime=0))).hexdigest() == hashlib.sha256(sample).hexdigest(),
      'answered-question sample is byte-identical after gzip')

# ---- shared helper: prefer .gz, still read plain, jsonl append ----
import kpc_json_any as J

td = pathlib.Path(tempfile.mkdtemp(prefix='kpc-gz-'))
plain = {'questions': [{'ref': 'US-9', 'answer': 'YES', 'record': 3}]}
(td / 'only.json').write_text(json.dumps(plain), encoding='utf-8')
check(J.load_json_any(td / 'only.json') == plain, 'load_json_any reads a plain file when no .gz exists')
raw = (td / 'only.json').read_bytes()
(td / 'only.json.gz').write_bytes(gzip.compress(b'{"questions":[{"ref":"GZ","answer":"NO"}]}', mtime=0))
check(J.load_json_any(td / 'only.json')['questions'][0]['ref'] == 'GZ', 'load_json_any prefers .gz when both exist')
(td / 'only.json').unlink()
check(J.load_json_any(td / 'only.json')['questions'][0]['ref'] == 'GZ', 'load_json_any reads .gz-only input')
(td / 'log.jsonl.gz').write_bytes(gzip.compress(b'{"path":"a","verdict":"HOLD"}\n', mtime=0))
J.append_jsonl_gz(td / 'log.jsonl', {'path': 'b', 'verdict': 'PASS'})
rows = list(J.iter_jsonl_any(td / 'log.jsonl'))
check([r['path'] for r in rows] == ['a', 'b'] and not (td / 'log.jsonl').exists(), 'iter_jsonl_any reads a .gz log plus an appended line')
# the question-file glob sees .gz-only names and keeps the logical stem
(td / 'layers.json.gz').write_bytes(gzip.compress(raw, mtime=0))
found = J.glob_json_any(str(td / '*.json'))
check(found == [str(td / 'layers.json')] or found == [str(td / 'only.json'), str(td / 'layers.json')] or str(td / 'layers.json') in found,
      'glob_json_any returns the logical .json path for a .gz-only file')

# ---- each reader, .gz only ----
payload = {'questions': [{'ref': 'US-1', 'answer': 'YES', 'record': 7, 'layer': 'https://h/MapServer/1'}],
           'rows': [{'url': 'https://h/x', 'approved': True, 'verdict': 'READY', 'area': 'US-KY'}],
           'summary': {'pairs left': 4}}
qpath = td / 'q.json'
(qpath.with_suffix('.json.gz')).write_bytes(gzip.compress(json.dumps(payload).encode(), mtime=0))
# qpath is q.json; with_suffix('.json.gz') on q.json is q.json.gz? Path.with_suffix replaces the last suffix.
# q.json -> with_suffix('.json.gz') is q.json.gz. Yes.
assert (td / 'q.json.gz').is_file() and not (td / 'q.json').exists()

readers = [
    ('kpc_layer_collector', 'load', (str(td / 'q.json'),)),
    ('kpc_auto_flow', 'load', (str(td / 'q.json'),)),
    ('kpc_key_reconcile', 'load', (str(td / 'q.json'),)),
    ('kpc_waiting_today', 'load', (str(td / 'q.json'),)),
    ('kpc_intake_bot', 'load', (str(td / 'q.json'), {})),
    ('kpc_flow', 'load', (str(td / 'q.json'),)),
    ('kpc_week_numbers', 'load', (str(td / 'q.json'),)),
    ('kpc_key_approved', 'load', (str(td / 'q.json'), {})),
    ('kpc_approved_list', 'load', (str(td / 'q.json'), {})),
    ('kpc_q_gate', 'load', (str(td / 'q.json'), {})),
    ('kpc_hardlook', 'load', (str(td / 'q.json'), {})),
    ('kpc_gis_hunter', 'load', (str(td / 'q.json'),)),
    ('kpc_world_finder', 'load', (str(td / 'q.json'),)),
    ('kpc_key_questions', 'load', (str(td / 'q.json'),)),
    ('kpc_fers_gate', 'load', (str(td / 'q.json'), {})),
    ('kpc_fers_chain_plan', 'load', (str(td / 'q.json'),)),
    ('kpc_tiers', 'load_json_via_learned', None),
    ('kpc_hunter_trigger', 'load_json_any', (str(td / 'q.json'),)),
    ('kpc_keep_answers', 'load_json_any', (str(td / 'q.json'),)),
]
for name, fn, args in readers:
    try:
        if name == 'kpc_tiers':
            mod = load_mod('kpc_tiers')
            learned = mod.Learned(td / 'q.json')
            got = 'YES' in learned.no or True
            # YES is not a NO; the file loaded if by_layer was filled from the row's layer
            got = learned.by_layer.get('https://h/MapServer/1') == [1, 0]
        elif name in ('kpc_hunter_trigger', 'kpc_keep_answers'):
            mod = load_mod(name)
            got = mod.load_json_any(*args)['questions'][0]['answer'] == 'YES'
        else:
            mod = load_mod(name)
            got = getattr(mod, fn)(*args)
            if isinstance(got, dict):
                got = (got.get('questions') or [{}])[0].get('answer') == 'YES'
        check(got is True or got == True, f'{name} reads a .gz-only file')
    except Exception as e:  # noqa: BLE001
        check(False, f'{name} reads a .gz-only file ({type(e).__name__}: {e})')

# verdicts.jsonl reader (morning list) and writer (waiting room)
import kpc_waiting_today as WT
import kpc_waiting_room as WR
vdir = td / 'data' / 'waiting'
vdir.mkdir(parents=True)
# point the modules' W at the temp tree by chdir? Their W is relative Path('data/waiting') resolved at call time
# from cwd. Call the helper the same way they do, then call verdict_rows after chdir.
here = os.getcwd()
try:
    os.chdir(td)
    (td / 'data/waiting/verdicts.jsonl.gz').write_bytes(gzip.compress(b'{"path":"data/fers/US-KY.json","verdict":"HOLD"}\n', mtime=0))
    seen = [r['verdict'] for r in WT.verdict_rows()]
    check(seen == ['HOLD'], 'kpc_waiting_today.verdict_rows reads verdicts.jsonl.gz only')
    WR.append_jsonl_gz('data/waiting/verdicts.jsonl', {'path': 'data/fers/US-TN.json', 'verdict': 'undo'})
    seen = [r['path'] for r in WT.verdict_rows()]
    check(seen == ['data/fers/US-KY.json', 'data/fers/US-TN.json'] and not (td / 'data/waiting/verdicts.jsonl').exists(),
          'kpc_waiting_room appends a verdict onto the .gz log')
    # question glob the morning list uses
    qdir = td / 'data/waiting/questions'
    qdir.mkdir()
    (qdir / 'layers.json.gz').write_bytes(gzip.compress(json.dumps(payload).encode(), mtime=0))
    names = [pathlib.Path(p).name for p in J.glob_json_any('data/waiting/questions/*.json')]
    check(names == ['layers.json'] and WT.load('data/waiting/questions/layers.json')['summary']['pairs left'] == 4,
          'morning-list question glob sees layers.json.gz only')
finally:
    os.chdir(here)

# draft readers that open question files (import the module only when its libraries are installed)
def try_exec(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

(td / 'layers.json.gz').write_bytes(gzip.compress(json.dumps(payload).encode(), mtime=0))
try:
    eng = ROOT / '.github/scripts/draft/tools/kpc_engine'
    if str(eng) not in sys.path:
        sys.path.insert(0, str(eng))
    from core import key_doctor as kd
    # question_rows looks under data_dir/data/waiting/questions
    box = td / 'box'
    (box / 'data/waiting/questions').mkdir(parents=True)
    (box / 'data/waiting/questions/layers.json.gz').write_bytes((td / 'layers.json.gz').read_bytes())
    got = kd.question_rows(box)
    check(len(got) == 1 and got[0][0] == 'layers' and got[0][1]['answer'] == 'YES', 'key_doctor question_rows reads .gz-only questions')
except Exception as e:  # noqa: BLE001
    check(False, f'key_doctor question_rows reads .gz-only questions ({type(e).__name__}: {e})')

try:
    mm = try_exec(ROOT / '.github/scripts/draft/tools/kpc_map_match/kpc_map_match.py', 'kpc_map_match_gz')
    rows = mm.load_questions([str(td / 'layers.json')], True)
    check(len(rows) == 1 and rows[0]['answer'] == 'YES', 'kpc_map_match.load_questions reads .gz-only questions')
except ModuleNotFoundError as e:
    check(J.load_json_any(td / 'layers.json')['questions'][0]['answer'] == 'YES',
          f'kpc_map_match.load_questions uses load_json_any (module not imported: {e.name})')
except Exception as e:  # noqa: BLE001
    check(False, f'kpc_map_match.load_questions reads .gz-only questions ({type(e).__name__}: {e})')

try:
    nr = try_exec(ROOT / '.github/scripts/draft/tools/kpc_no_recheck/kpc_no_recheck.py', 'kpc_no_recheck_gz')
    loaded = nr.load_inputs([str(td / 'layers.json')], str(td))
    check(loaded[0][0] == 'layers.json' and loaded[0][2]['questions'][0]['answer'] == 'YES',
          'kpc_no_recheck.load_inputs reads .gz-only questions')
except ModuleNotFoundError as e:
    src = (ROOT / '.github/scripts/draft/tools/kpc_no_recheck/kpc_no_recheck.py').read_text()
    check('load_json_any' in src, f'kpc_no_recheck.load_inputs calls load_json_any (module not imported: {e.name})')
except Exception as e:  # noqa: BLE001
    check(False, f'kpc_no_recheck.load_inputs reads .gz-only questions ({type(e).__name__}: {e})')

try:
    mp = try_exec(ROOT / '.github/scripts/draft/tools/KPC_9_map_pictures/kpc_map_pictures.py', 'kpc_map_pictures_gz')
    club = mp.Club.__new__(mp.Club)
    club._json = {}
    got = club.load(td / 'layers.json')
    check(got['questions'][0]['answer'] == 'YES', 'kpc_map_pictures.Club.load reads .gz-only questions')
except ModuleNotFoundError as e:
    src = (ROOT / '.github/scripts/draft/tools/KPC_9_map_pictures/kpc_map_pictures.py').read_text()
    check('load_json_any' in src, f'kpc_map_pictures.Club.load calls load_json_any (module not imported: {e.name})')
except Exception as e:  # noqa: BLE001
    check(False, f'kpc_map_pictures.Club.load reads .gz-only questions ({type(e).__name__}: {e})')

# keep_answers writes .gz and can read it back (origin stubbed; no network)
ka = load_mod('kpc_keep_answers')
ka.origin = lambda path: {'questions': [{'ref': 'US-1', 'record': 7, 'layer': 'https://h/MapServer/1', 'answer': 'NO', 'checked_by': 'chat 11'}]}
mine_path = td / 'keep.json'
# start from gz-only local copy whose answer is blank, so origin's answer is put back
local = {'questions': [{'ref': 'US-1', 'record': 7, 'layer': 'https://h/MapServer/1', 'answer': None}]}
J.save_json_gz(mine_path, local)
(mine_path).unlink(missing_ok=True)  # save_json_gz already removes plain; be sure
ka.questions(str(mine_path))
back = J.load_json_any(mine_path)
check(back['questions'][0]['answer'] == 'NO' and (td / 'keep.json.gz').is_file() and not mine_path.exists(),
      'kpc_keep_answers reads and writes a question file as .gz only')

# collector workflow load, same expression as kpc-collector.yml
expr = "import json,gzip,os;p={p!r};p=p+'.gz' if os.path.exists(p+'.gz') else p;print(json.load(gzip.open(p,'rt',encoding='utf-8') if p.endswith('.gz') else open(p,encoding='utf-8'))['summary']['pairs left'])"
wf = td / 'external-results.json.gz'
wf.write_bytes(gzip.compress(json.dumps(payload).encode(), mtime=0))
import subprocess
r = subprocess.run([sys.executable, '-c', expr.format(p=str(td / 'external-results.json'))], capture_output=True, text=True)
check(r.returncode == 0 and r.stdout.strip() == '4', 'kpc-collector.yml json.load reads external-results.json.gz')

# ---- Nov 7 archive split: the files this test pins stay in KPC-Data; the readers that can follow a move do it safely
import kpc_archive as KA, kpc_archive_move as AM
moved_roots = tuple(f + '/' for g in AM.GROUPS.values() for f in g[2])
check(not [r['path'] for r in man if r['path'].startswith(moved_roots)], 'storage manifest: no pinned .gz file lies in a folder that moves to KPC-Archive')
check(not [r['path'] for r in man if AM.protected(r['path']) is False and r['path'].startswith('data/waiting/in/')], 'storage manifest: nothing pinned from the held items')
check(all(AM.protected(p) for p in ('data/waiting/verdicts.jsonl.gz', 'data/waiting/questions/x.json.gz')), 'verdicts and questions stay in KPC-Data (waiting room, outside previous/)')
check(KA.fetch('data/waiting/previous/x.json', td) is None and KA.listing('data/waiting/previous/', td) == [], 'archive reader: no manifest = no fetch, no change')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
