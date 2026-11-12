#!/usr/bin/env python3
"""Offline test, KPC owner 2026-11-12 (handoff item 8): the bots that add rows to the layer-intake queue write split files
data/intake/queue-<bot>-<n>.json, never the full queue.json (at the 1 MB cap) and never a *hold* file. Covers: the shared helper
(kpc_queue_files.py), the GIS hunter, the park detective, the retry-hosts list, the layer collector, the intake bot's own feed, and the
engine's reader; round trip through the intake bot's reader; dedupe across every queue file (hold files too); an in-place update going
back to the file it came from; the roll-over before the cap; nothing over 1 MB; and the workflow save paths (parsed YAML, plus a real
git add in a throwaway repo). No network (every connect is refused). Run: python3 -B tests/test_queue_writers_nov12.py"""
import hashlib, io, json, os, pathlib, re, socket, subprocess, sys, tempfile, contextlib
R = pathlib.Path(__file__).resolve().parents[1]; SCRIPTS = R / '.github' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('no network in this test'))
ok = True
def check(c, m):
    global ok; print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
CAP = 1048576

def world(rows_main=None, rows_split=None, rows_hold=None, pad_main=0):
    """A throwaway repo folder with data/intake/{queue.json, queue-nov12.json, queue-hold-nov12.json}; cwd goes there."""
    t = pathlib.Path(tempfile.mkdtemp()); d = t / 'data' / 'intake'; d.mkdir(parents=True)
    main = {'about': 'main', 'rows': rows_main or []}
    if pad_main: main['pad'] = 'x' * pad_main
    (d / 'queue.json').write_text(json.dumps(main, indent=1, ensure_ascii=False), encoding='utf-8')
    (d / 'queue-nov12.json').write_text(json.dumps({'about': 'split', 'rows': rows_split or []}, indent=1) + '\n', encoding='utf-8')
    (d / 'queue-hold-nov12.json').write_text(json.dumps({'about': 'hold', 'rows': rows_hold or []}, indent=1) + '\n', encoding='utf-8')
    os.chdir(t); return t, d

def row(u, **k): return {'url': u, 'area': k.pop('area', 'US-KY'), 'title': 't', 'from': 'x', 'added': '2026-11-12', **k}
def untouched(d, names): return all(sha(d / n) == H[n] for n in names)
def snap(d): return {n: sha(d / n) for n in ('queue.json', 'queue-nov12.json', 'queue-hold-nov12.json')}
def big_files(t): return [f for f in t.rglob('*') if f.is_file() and f.stat().st_size >= CAP]

import kpc_queue_files as QF
import kpc_intake_bot as IB   # the reader (module level reads env QUEUE at import: each case below passes the folder explicitly)

# ---- 1. the helper: append, shape, reader round trip, hold, atomic, roll-over
t, d = world([row('https://m.gov/a')], [row('https://s.gov/b')], [row('https://h.gov/never')]); H = snap(d)
w = QF.append_rows([row('https://n.gov/1'), row('https://n.gov/2', closes=['US-1'])], 'gis-hunter')
check([p.name for p in w] == ['queue-gis-hunter-1.json'], f'first append makes queue-gis-hunter-1.json: {[p.name for p in w]}')
doc = json.loads((d / 'queue-gis-hunter-1.json').read_text())
check(sorted(doc) == ['about', 'rows'] and len(doc['rows']) == 2, 'same shape as queue-nov12.json: {about, rows}')
check(untouched(d, H), 'queue.json, the split file and the hold file are byte-identical after the append')
got = [r['url'] for r in IB.split_queue_rows([row('https://m.gov/a')], d)]
check(got == ['https://n.gov/1', 'https://n.gov/2', 'https://s.gov/b'], f'ROUND TRIP: the intake bot reader returns the written rows, not the hold row: {got}')
check(not [f for f in d.iterdir() if f.name.endswith('.tmp')], 'no temp file left behind (atomic write)')
check(QF.known_keys(d) >= {'https://h.gov/never', 'https://m.gov/a', 'https://n.gov/1'}, 'known_keys spans queue.json, split files AND hold files')
check([r['url'] for r in QF.rows(d)] == ['https://m.gov/a', 'https://n.gov/1', 'https://n.gov/2', 'https://s.gov/b'], 'rows(): queue.json first, then the split files, no hold file')
for bad in ('hold', 'Hold-it', 'my-HOLD'):
    try: QF.append_rows([row('https://x.gov/')], bad, d); check(False, f'writer name {bad!r} refused')
    except ValueError: check(True, f'a writer name containing hold ({bad!r}) is refused')
check(all('hold' not in p.name.lower() for p in w), 'no file written has hold in its name')
w2 = QF.append_rows([row('https://n.gov/3')], 'gis-hunter')
check([p.name for p in w2] == ['queue-gis-hunter-1.json'] and len(json.loads((d / 'queue-gis-hunter-1.json').read_text())['rows']) == 3, 'a second append goes on the same file while it has room')

# roll-over: a nearly full file rolls to -2 before the cap; a big batch spreads over several files; none reaches the cap
t, d = world(); H = snap(d)
fat = lambda i: row(f'https://f.gov/{i}', note='n' * 3000)
QF.append_rows([fat(i) for i in range(280)], 'retry-hosts')       # ~ 280 x 3.1 KB = 870 KB
names = sorted(f.name for f in d.glob('queue-retry-hosts-*.json'))
check(len(names) == 1 and QF.ROLL_AT - 60000 < (d / names[0]).stat().st_size < QF.ROLL_AT, f'one file filled up to just under the roll size: {names} {(d / names[0]).stat().st_size}')
QF.append_rows([fat(i) for i in range(1000, 1100)], 'retry-hosts')
names = sorted(f.name for f in d.glob('queue-retry-hosts-*.json'))
check(names == ['queue-retry-hosts-1.json', 'queue-retry-hosts-2.json'], f'rolled to a new file before the cap: {names}')
check(all(f.stat().st_size < QF.ROLL_AT for f in d.glob('queue-retry-hosts-*.json')), 'every split file stays under the roll size (900,000 bytes)')
QF.append_rows([fat(i) for i in range(2000, 2800)], 'retry-hosts')   # a batch bigger than one file
fs = sorted(d.glob('queue-retry-hosts-*.json'))
check(len(fs) >= 4 and all(f.stat().st_size < QF.ROLL_AT for f in fs), f'a big batch is spread over {len(fs)} files, all under the roll size')
allu = [r['url'] for r in QF.rows(d)]
check(len(allu) == 280 + 100 + 800 and len(set(allu)) == len(allu), 'no row lost or doubled by the roll-over')
check(untouched(d, H) and not big_files(t), 'queue.json / hold file untouched; no file over 1 MB')
(d / 'queue-retry-hosts-9.json').write_text('{not json', encoding='utf-8')
QF.append_rows([row('https://z.gov/1')], 'retry-hosts')
check((d / 'queue-retry-hosts-9.json').read_text() == '{not json' and (d / 'queue-retry-hosts-10.json').exists(), 'an unreadable split file is never overwritten: the next number is used')

# ---- 2. GIS hunter: main() wiring (network pieces stubbed; no network anyway)
t, d = world([row('https://m.gov/a')], [row('https://s.gov/b')], [row('https://h.gov/never')]); H = snap(d)
os.environ.update({'AREAS': 'US-ZZ', 'HOLD': ''})
import kpc_gis_hunter as GH
def fake_b(area, todo, P, R, queue):
    for u in ('https://m.gov/a', 'https://s.gov/b', 'https://h.gov/never', 'https://new.gov/gh', 'https://new.gov/gh'):   # 3 already known (main / split / HOLD), a new one twice
        if u not in queue['seen']:
            queue['rows'].append({'url': u, 'title': 't', 'from': 'gis-hunter', 'added': '2026-11-12', 'closes': ['US-1'], 'note': 'n'}); queue['seen'].add(u)
GH.us_pool = lambda: {'US-ZZ': [('US-1', 'no outline')]}; GH.pins = lambda a: {}
GH.step_a = lambda *a: None; GH.step_b = fake_b; GH.step_b3 = lambda *a: None; GH.write_area = lambda *a: None; GH.write_questions = lambda *a: None
GH.verdict = lambda rec: 'no layer found'; GH.OUT = pathlib.Path('data/gis-hunter')
with contextlib.redirect_stdout(io.StringIO()): GH.main()
check(sorted(f.name for f in d.glob('queue-gis-hunter-*.json')) == ['queue-gis-hunter-1.json'], 'GIS hunter: appends to queue-gis-hunter-1.json')
check([r['url'] for r in json.loads((d / 'queue-gis-hunter-1.json').read_text())['rows']] == ['https://new.gov/gh'], 'GIS hunter: only the NEW url (known in queue.json / split / HOLD file: skipped)')
check(untouched(d, H), 'GIS hunter: queue.json and the hold file are byte-identical (it used to rewrite queue.json)')
check('https://new.gov/gh' in [r['url'] for r in IB.split_queue_rows([row('https://m.gov/a')], d)], 'GIS hunter: ROUND TRIP through the intake bot reader')
check(not big_files(t), 'GIS hunter: no file over 1 MB')

# ---- 3. park detective: new row, in-place update, hold row, cap
os.environ['OUT'] = 'data/detective'
import kpc_detective_bot as DB
def D_(*layers):
    return {'parks': {f'US-{i}': {'finds': [{'layer': u, 'rel': 'name match', 'where': 'x', 'publisher': 'P', 'licence': 'open', 'field': 'NAME', 'sure': 'YES'}]} for i, u in enumerate(layers, 1)}, 'counts': {}}
mk = lambda: world([row('https://m.gov/a', closes=['US-OLD'], **{'from': 'gap-filler'})], [row('https://s.gov/b')], [row('https://h.gov/never')])
t, d = mk(); H = snap(d)
DB.OUT = pathlib.Path('data/detective'); DB.in_repo = lambda p: True
with contextlib.redirect_stdout(io.StringIO()): DB.queue_append('US-KY', D_('https://new.gov/d', 'https://m.gov/a', 'https://s.gov/b', 'https://h.gov/never'))
rows_d = json.loads((d / 'queue-detective-1.json').read_text())['rows']
check([r['url'] for r in rows_d] == ['https://new.gov/d'] and rows_d[0]['from'] == 'gap-filler' and rows_d[0]['closes'] == ['US-1'], 'detective: the one new layer goes to queue-detective-1.json')
mainrows = json.loads((d / 'queue.json').read_text())['rows']; splitrows = json.loads((d / 'queue-nov12.json').read_text())['rows']
check(mainrows[0]['closes'] == ['US-OLD', 'US-2'], f'detective: in-place update of a queue.json row stays in queue.json (closes merged): {mainrows[0]["closes"]}')
check(splitrows[0]['closes'] == ['US-3'], 'detective: in-place update of a queue-nov12.json row goes back to queue-nov12.json')
check(sha(d / 'queue-hold-nov12.json') == H['queue-hold-nov12.json'], 'detective: the hold file is never touched and its url is not added again')
check(not [r for r in rows_d if r['url'] == 'https://h.gov/never'] and len(rows_d) == 1, 'detective: no copy of the held url anywhere else')
check((d / 'queue.json').read_text() == json.dumps(json.loads((d / 'queue.json').read_text()), indent=1, ensure_ascii=False), 'detective: queue.json keeps its own style (indent 1, no final newline)')
# style: a queue.json saved by the intake bot (sorted keys, final newline) keeps that style when a row is updated in place
t, d = world([row('https://m.gov/a', closes=['US-OLD'], **{'from': 'gap-filler'})])
(d / 'queue.json').write_text(json.dumps(json.loads((d / 'queue.json').read_text()), indent=1, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')
with contextlib.redirect_stdout(io.StringIO()): DB.queue_append('US-KY', D_('https://m.gov/a'))
qt = (d / 'queue.json').read_text()
check('US-2' not in qt and '"US-1"' in qt and qt == json.dumps(json.loads(qt), indent=1, ensure_ascii=False, sort_keys=True) + '\n', 'detective: a sorted-keys queue.json with a final newline keeps that style after an in-place update')
with contextlib.redirect_stdout(io.StringIO()): DB.queue_append('US-KY', D_('https://new.gov/d'))
check(len(json.loads((d / 'queue-detective-1.json').read_text())['rows']) == 1, 'detective: a second pass does not add the url again (dedupe)')
# cap: queue.json one byte short of the cap: an update that would reach it is left alone, the rest goes on
t, d = world([row('https://m.gov/a', closes=['US-OLD'], **{'from': 'gap-filler'})], pad_main=0)
m = json.loads((d / 'queue.json').read_text()); m['pad'] = ''; m['pad'] = 'x' * (CAP - 5 - len(json.dumps(m, indent=1))); (d / 'queue.json').write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding='utf-8')
H = snap(d); size0 = (d / 'queue.json').stat().st_size
with contextlib.redirect_stdout(io.StringIO()): DB.queue_append('US-KY', D_('https://m.gov/a', 'https://new.gov/e'))
check(size0 < CAP and sha(d / 'queue.json') == H['queue.json'], f'detective: queue.json at {size0} bytes is not grown past the cap (update skipped, file byte-identical)')
check([r['url'] for r in json.loads((d / 'queue-detective-1.json').read_text())['rows']] == ['https://new.gov/e'], 'detective: new row still lands in its split file')
check(not big_files(t), 'detective: no file over 1 MB')

# ---- 4. retry-hosts: appends only (retry-github.json is its own result file; no queue row is rewritten)
t, d = world([row('https://m.gov/a')], [row('https://s.gov/b')], [row('https://h.gov/never')]); H = snap(d)
(t / 'retry.json').write_text(json.dumps({'items': [{'id': 'R1', 'country': 'Xland', 'cc': 'XL', 'agency': 'Xagency', 'address': 'https://x.gov/arcgis/rest/services/P/MapServer'}]}), encoding='utf-8')
sys.argv = ['kpc_retry_hosts.py', str(t / 'retry.json')]
import kpc_retry_hosts as RH
lay = [{'id': i, 'name': f'L{i}', 'geometryType': 'esriGeometryPolygon'} for i in range(4)]
RH.get = lambda u: (200, json.dumps({'layers': lay}), u)
# the layer urls are https://x.gov/arcgis/rest/services/P/MapServer/<id>; pre-seed 0 in the hold file, 1 in queue.json (different case + trailing slash), 2 in queue-nov12
base = 'https://x.gov/arcgis/rest/services/P/MapServer'
for fn, u in (('queue-hold-nov12.json', f'{base}/0'), ('queue.json', f'{base.upper().replace("HTTPS", "https")}/1/'), ('queue-nov12.json', f'{base}/2')):
    dd = json.loads((d / fn).read_text()); dd['rows'].append(row(u)); (d / fn).write_text(json.dumps(dd, indent=1) + ('' if fn == 'queue.json' else '\n'), encoding='utf-8')
H = snap(d)
with contextlib.redirect_stdout(io.StringIO()): RH.main()
rr = json.loads((d / 'queue-retry-hosts-1.json').read_text())['rows']
check([r['url'] for r in rr] == [f'{base}/3'] and rr[0]['from'] == 'retry list (GitHub try)', f'retry-hosts: only the layer not known anywhere (hold, queue.json and split file all count) is appended: {[r["url"][-1] for r in rr]}')
check(untouched(d, H), 'retry-hosts: queue.json, the split file and the hold file are byte-identical')
res = json.loads((d / 'retry-github.json').read_text())
check(res['added_to_layer_list'] == 1 and len(res['tries']) == 1, 'retry-hosts: retry-github.json (its own result file, rewritten whole) is still written')
before = (d / 'queue-retry-hosts-1.json').read_bytes()
with contextlib.redirect_stdout(io.StringIO()): RH.main()
check((d / 'queue-retry-hosts-1.json').read_bytes() == before, 'retry-hosts: a second run adds nothing (rows are appended once, never rewritten)')
check('retry list (GitHub try)' in [r.get('from') for r in IB.split_queue_rows([row('https://m.gov/a')], d)], 'retry-hosts: ROUND TRIP through the intake bot reader')

# ---- 5. layer collector (new rows only; the stubs stand in for the network readers)
t, d = world([row('https://m.gov/a')], [row('https://s.gov/b')], [row('https://h.gov/never')]); H = snap(d)
os.environ['LINKS'] = str(t / 'links'); (t / 'links').mkdir()
import kpc_layer_collector as LC
def fake_crawled(want, log, qs, queue, seen, n):
    for u in ('https://m.gov/a', 'https://s.gov/b', 'https://h.gov/never', 'https://new.gov/c'):
        if u not in seen: queue['rows'].append({'url': u, 'title': 't', 'from': 'atlas crawler', 'added': '2026-11-12', 'closes': ['US-1']}); seen.add(u)
    return 0
LC.test_crawled = fake_crawled; LC.external = lambda *a: None; LC.handfiles = lambda *a: None; LC.converted = lambda *a: None
LC.LOG = pathlib.Path('data/intake/collector.json.gz'); LC.OLDLOG = pathlib.Path('data/intake/collector.json')
sys.argv = ['kpc_layer_collector.py']
with contextlib.redirect_stdout(io.StringIO()): LC.main()
check([r['url'] for r in json.loads((d / 'queue-layer-collector-1.json').read_text())['rows']] == ['https://new.gov/c'], 'layer collector: only the new url, in queue-layer-collector-1.json')
check(untouched(d, H), 'layer collector: queue.json and the hold file are byte-identical')

# ---- 6. intake bot feed (harvester A-band leads) and the engine reader
t, d = world([row('https://m.gov/a')], [row('https://s.gov/b')], [row('https://h.gov/never')]); H = snap(d)
(t / 'data' / 'harvest').mkdir()
(t / 'data' / 'harvest' / 'leads-GB.json').write_text(json.dumps({'leads': {k: {'band': 'A', 'url': k, 'cc': 'GB', 'title': 'x'} for k in ('https://h.gov/never', 'https://s.gov/b', 'https://new.gov/feed')}}), encoding='utf-8')
fed = IB.feed_split(d)
check(fed == 1 and [r['url'] for r in json.loads((d / 'queue-intake-feed-1.json').read_text())['rows']] == ['https://new.gov/feed'], 'intake feed: one new lead, in queue-intake-feed-1.json (held / split / main urls not re-added)')
check(untouched(d, H), 'intake feed: queue.json and the hold file are byte-identical (it used to save queue.json)')
check(IB.feed_split(d) == 0, 'intake feed: a second run adds nothing')
eng = t / 'eng'; (eng / 'registry').mkdir(parents=True)
os.makedirs(t / 'data' / 'parkinfo')
r = subprocess.run([sys.executable, str(SCRIPTS / 'kpc_engine_extra.py'), str(eng), 'data/intake/queue.json'], cwd=t, capture_output=True, text=True)
src = [s['url'] for s in json.loads((eng / 'registry' / 'club_extra.json').read_text())['sources']]
check(r.returncode == 0 and 'https://new.gov/feed' in src and 'https://s.gov/b' in src and 'https://m.gov/a' in src and 'https://h.gov/never' not in src,
      f'engine reader: queue.json + split files are read, the hold file is not: {sorted(src)}')

# ---- 7. nothing still writes the full queue.json
for n in ('kpc_gis_hunter.py', 'kpc_detective_bot.py', 'kpc_retry_hosts.py', 'kpc_layer_collector.py', 'kpc_intake_bot.py'):
    s = (SCRIPTS / n).read_text(encoding='utf-8')
    bad = re.findall(r"(?:open\(\s*(?:QUEUE|QUEUE_FILE|'data/intake/queue\.json')[^)]*'w'|save\(\s*(?:QUEUE_FILE|QUEUE)\b|pathlib\.Path\('data/intake/queue\.json'\)|json\.dump\(\s*(?:queue|Q)\b)", s)
    check(not bad, f'{n}: no write to the full queue.json left ({bad[:1]})')

# ---- 8. workflows: save paths (parsed YAML) and a real git add
import yaml
def pushes(name):
    wf = yaml.safe_load((R / '.github' / 'workflows' / name).read_text(encoding='utf-8')); out = []
    for j in (wf.get('jobs') or {}).values():
        for st in j.get('steps') or []:
            for line in str(st.get('run') or '').splitlines():
                if 'kpc_push_data.sh' in line and '"$' not in line.split('kpc_push_data.sh')[0]: out.append(line)
    return wf, out
for name, want in (('kpc-gis-hunter.yml', "'data/intake/queue-gis-hunter-*.json'"), ('kpc-retry-hosts.yml', "'data/intake/queue-retry-hosts-*.json'")):
    wf, ps = pushes(name)
    check(('on' in wf or True in wf) and 'jobs' in wf and any(want in p for p in ps), f'{name}: parses; a save step lists {want}')
    check(not any(re.search(r'data/intake/queue\.json(?!\w)', p) for p in ps), f'{name}: no save step still lists only the full queue.json')
for name in ('kpc-detective.yml', 'kpc-collector.yml', 'kpc-intake.yml'):
    wf, ps = pushes(name)
    check(any(re.search(r'\sdata/intake(\s|$)', p) for p in ps), f'{name}: its save step already lists the whole data/intake folder (covers queue-*.json)')
check(not [n for n in (R / '.github' / 'site-allow-list.txt').read_text().split('\n') if n.strip().startswith('data/intake') or n.strip().startswith('data/ ')], 'site allow-list: no data/intake entry, so queue files are never served')
g = pathlib.Path(tempfile.mkdtemp())
sh = lambda *a: subprocess.run(a, cwd=g, capture_output=True, text=True)
sh('git', 'init', '-q'); (g / 'data' / 'intake').mkdir(parents=True); (g / 'data' / 'intake' / 'queue-gis-hunter-1.json').write_text('{"rows":[]}')
sh('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'add', '-A'); sh('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'x')
(g / 'data' / 'intake' / 'queue-gis-hunter-1.json').write_text('{"rows":[1]}'); (g / 'data' / 'intake' / 'queue-gis-hunter-2.json').write_text('{"rows":[2]}')
(g / 'data' / 'intake' / 'queue-hold-x.json').write_text('{"rows":[3]}')
sh('bash', '-c', "git add -A -- 'data/intake/queue-gis-hunter-*.json' 2>/dev/null")
staged = sh('git', 'diff', '--cached', '--name-only').stdout.split()
check(staged == ['data/intake/queue-gis-hunter-1.json', 'data/intake/queue-gis-hunter-2.json'], f'git add -A with the quoted pattern stages the changed file AND the new rolled file, not a hold file: {staged}')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
