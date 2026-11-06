#!/usr/bin/env python3
"""Replay regression for the report-only pile-solver rank (Nov 6).

KPC_RESEARCH_SOURCES defaults to off. Off, a replay of the frozen pile-solver
fixtures plus the Blackford Oaks W.M.A. two-name case reads and writes the same
bytes as the solver did before this change. Report mode may write
data/pile-solver/research-rank.json and may read the ranker and the abbreviation
list. It may not fetch a new host, ask a layer for different fields, change a
verdict, or set pile-solver auto.

Offline. Throws if anything opens the network. Does not write this repo.
"""
import builtins, hashlib, json, os, pathlib, shutil, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ.setdefault('LINKS', '/tmp/kpc-links')
os.environ.pop('KPC_RESEARCH_SOURCES', None)
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))

import kpc_pile_solver as S
import kpc_agreement_ledger as AL

STAMP = '2026-11-06 12:00 CST'
FX_PATH = ROOT / 'tests' / 'fixtures' / 'pile_solver' / 'cases.json'
GOLDEN = ROOT / 'tests' / 'fixtures' / 'pile_solver' / 'research-replay-off.json'
BANNED = '33TOOklri9xpic7U'
SIDE = 'data/pile-solver/research-rank.json'

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def _sha(path):
    p = pathlib.Path(path)
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _snap(directory):
    out = {}
    directory = pathlib.Path(directory)
    if not directory.exists():
        return out
    for p in sorted(directory.rglob('*')):
        if p.is_file():
            out[str(p.relative_to(directory))] = p.read_text(encoding='utf-8')
    return out


def _canon(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False, sort_keys=True))


class _Trace:
    """Record sandbox / repo / links files the solver opens. Ignore the stdlib."""

    def __init__(self, root, links):
        self.root = pathlib.Path(root).resolve()
        self.links = pathlib.Path(links).resolve() if links else None
        self.repo = ROOT.resolve()
        self.reads, self.writes = [], []
        self._open = builtins.open
        self._path_open = pathlib.Path.open

    def start(self):
        builtins.open = self._wrap
        trace = self

        def path_open(path, mode='r', *a, **k):
            trace._note(path, mode)
            return trace._path_open(path, mode, *a, **k)

        pathlib.Path.open = path_open

    def stop(self):
        builtins.open = self._open
        pathlib.Path.open = self._path_open

    def _note(self, file, mode):
        label = self._label(file)
        m = mode if isinstance(mode, str) else ''
        if not label:
            return
        if any(ch in m for ch in 'wa+'):
            self.writes.append(label)
        else:
            self.reads.append(label)

    def _label(self, file):
        if not isinstance(file, (str, pathlib.Path)):
            return None
        raw = str(file)
        if BANNED in raw:
            return 'BANNED/' + raw
        try:
            rp = pathlib.Path(raw).resolve()
        except OSError:
            return None
        rs = str(rp)
        if '/usr/lib' in rs or 'site-packages' in rs or '__pycache__' in rs or rs.endswith('.pyc'):
            return None
        for base, prefix in ((self.root, 'root/'), (self.repo, 'repo/'), (self.links, 'links/')):
            if base is None:
                continue
            try:
                return prefix + str(rp.relative_to(base))
            except ValueError:
                continue
        return None

    def _wrap(self, file, mode='r', *a, **k):
        self._note(file, mode)
        return self._open(file, mode, *a, **k)


def _blackford_fetcher():
    names = {'creek': 'Blackford Creek', 'oaks': 'Blackford Oaks Wildlife Management Area'}

    class F:
        n = 0
        skipped = []

        def __init__(self):
            self.M = type('M', (), {})()

        def record(self, rid, area='US-', src=None):
            box = [[-85.1, 37.0], [-84.9, 37.0], [-84.9, 37.2], [-85.1, 37.2], [-85.1, 37.0]]
            return {'id': str(rid), 'name': names[str(rid)], 'attrs': {'Loc_Mang': 'KDFWR'}, 'rings': [box],
                    'layer': S.PADUS, 'url': S.PADUS + '/query?f=json', 'label': 'USGS PAD-US', 'family': 'padus',
                    'html': S.PADUS + '/query?f=html'}

    return F()


def replay(flag):
    """One isolated replay. flag None or 'off' is the default. 'report' may rank."""
    prev_flag = os.environ.get('KPC_RESEARCH_SOURCES')
    prev = (S.LINKS, S.DATA, S.now_cst, S.T0)
    if flag is None:
        os.environ.pop('KPC_RESEARCH_SOURCES', None)
    else:
        os.environ['KPC_RESEARCH_SOURCES'] = flag
    if hasattr(S, 'RESEARCH_RANKS'):
        S.RESEARCH_RANKS.clear()
    S.KEYS.clear()
    S.LAYERS.clear()
    S.LAYERS_CA.clear()
    S.LAYERS_W.clear()
    S.now_cst = lambda: STAMP
    S.T0 = __import__('time').time()
    fx = json.loads(FX_PATH.read_text(encoding='utf-8'))
    root = pathlib.Path(tempfile.mkdtemp(prefix='pile-replay-'))
    links = root / 'links'
    (links / 'data/us-key').mkdir(parents=True)
    (links / 'data/ca-key').mkdir(parents=True)
    (links / 'data/world-key').mkdir(parents=True)
    (root / 'data/answer-sheet').mkdir(parents=True)
    (root / 'data/world-key').mkdir(parents=True)
    (links / 'data/us-key/overrides.json').write_text('{"parks": {}}\n', encoding='utf-8')
    (links / 'data/ca-key/overrides.json').write_text('{"parks": {}}\n', encoding='utf-8')
    (links / 'data/us-key/layers.json').write_text(json.dumps(fx.get('layers') or {}), encoding='utf-8')
    key = {'parks': {'US-7777': {
        'n': 'Blackford Oaks W.M.A.', 't': 'Wildlife Management Area',
        'm': [['creek', 'Blackford Creek', 0, 'name'],
              ['oaks', 'Blackford Oaks Wildlife Management Area', 0, 'name']]}}}
    (links / 'data/us-key/US-KY.json').write_text(json.dumps(key), encoding='utf-8')
    S.LINKS = links
    S.DATA = root
    AL.LEDGER = root / 'ledger.csv'
    AL.STATE = root / 'ledger-state.json'
    AL.save_rows([])
    AL.save_state({'auto': False})
    real_open = urllib.request.urlopen

    def no_net(*_a, **_k):
        raise AssertionError('a fetch went around the frozen fixtures')

    urllib.request.urlopen = no_net
    # The links checkout the detective was imported with, not the sandbox.
    links_checkout = pathlib.Path(os.environ.get('LINKS') or '')
    trace = _Trace(root, links_checkout)
    trace.start()
    verdicts, urls = [], []
    offline, blackford, ledger = {}, {}, ''
    try:
        for case in fx.get('cases') or []:
            S.KEYS.clear()
            S.LAYERS.clear()
            S.LAYERS.update(fx.get('layers') or {})
            c = case['pile']
            S.KEYS[str(S.LINKS / f"data/us-key/{c['area']}.json")] = {'parks': {c['park']: case.get('key') or {}}}
            S.KEYS[str(S.DATA / f"data/world-key/{c['area']}.json")] = {'parks': {c['park']: case.get('key') or {}}}
            p = {'ref': c['park'], 'area': c['area'], 'areas': c['area'], 'name': c['name'], 'type': c['type'],
                 'flags': set(c['flags'].split()), 'why': c['why'], 'ids': c['ids'], 'lat': c['lat'], 'lon': c['lon'],
                 'action': c['action'], 'src': 'pile', 'h': 'x', 'page': ''}
            manners = S.FixtureManners(fx.get('responses') or {})
            F = S.Fetch(manners) if case.get('online', True) else None
            ov = {c['park']: case['override']} if case.get('override') else {}
            sheet = {c['park']: case['sheet']} if case.get('sheet') else {}
            verdicts.append(_canon(S.solve(p, F, ov, sheet)))
            urls.extend(manners.asked)
        if hasattr(S, 'RESEARCH_RANKS'):
            S.RESEARCH_RANKS.clear()
        out = root / 'offline'
        (out / 'data/detective').mkdir(parents=True)
        (out / 'data/detective/questions.json').write_text('{"questions": []}', encoding='utf-8')
        S.KEYS.clear()
        for case in fx['cases']:
            c = case['pile']
            S.KEYS[str(S.LINKS / f"data/us-key/{c['area']}.json")] = {'parks': {c['park']: case.get('key') or {}}}
            S.KEYS[str(S.DATA / f"data/world-key/{c['area']}.json")] = {'parks': {c['park']: case.get('key') or {}}}
        S.LAYERS.update(fx.get('layers') or {})
        pile = [dict(p, flags=set(p['flags'].split()), h=S.sha(p), areas=p['area'], ids=p['ids'], src='pile',
                     ref=p['park'], lat=p['lat'], lon=p['lon'])
                for p in [c['pile'] for c in fx['cases'] if not c.get('online', True)]]
        S.run(out, pile, None)
        if hasattr(S, 'RESEARCH_RANKS'):
            S.RESEARCH_RANKS.clear()
        bout = root / 'blackford'
        (bout / 'data/detective').mkdir(parents=True)
        (bout / 'data/detective/questions.json').write_text('{"questions": []}', encoding='utf-8')
        S.KEYS.clear()
        S.LAYERS.clear()
        bp = {'ref': 'US-7777', 'area': 'US-KY', 'areas': 'US-KY', 'name': 'Blackford Oaks W.M.A.',
              'type': 'Wildlife Management Area', 'flags': set(), 'why': 'two-name replay', 'ids': ['creek', 'oaks'],
              'lat': '37.1', 'lon': '-85.0', 'action': 'HOLD', 'src': 'pile', 'h': 'blackford-oaks-wma', 'page': ''}
        S.run(bout, [bp], _blackford_fetcher())
        trace.stop()
        offline = _snap(out)
        blackford = _snap(bout)
        ledger = (root / 'ledger.csv').read_text(encoding='utf-8') if (root / 'ledger.csv').exists() else ''
    finally:
        trace.stop()
        urllib.request.urlopen = real_open
        S.LINKS, S.DATA, S.now_cst, S.T0 = prev
        if prev_flag is None:
            os.environ.pop('KPC_RESEARCH_SOURCES', None)
        else:
            os.environ['KPC_RESEARCH_SOURCES'] = prev_flag
        shutil.rmtree(root, ignore_errors=True)
    return {
        'reads': sorted(set(trace.reads)),
        'writes': sorted(set(trace.writes)),
        'urls': urls,
        'verdicts': verdicts,
        'offline_files': offline,
        'blackford_files': blackford,
        'ledger': ledger,
    }


def _without_side(files):
    return {k: v for k, v in files.items() if k != SIDE}


def _side_auto_false(files):
    if SIDE not in files:
        return False, 'no side file'
    doc = json.loads(files[SIDE])
    if doc.get('auto') is not False:
        return False, doc.get('auto')
    for row in doc.get('ranks') or []:
        if row.get('auto') is not False:
            return False, row
    return True, doc


def main():
    repo_before = {
        'state': _sha(ROOT / 'data/pile-solver/state.json'),
        'ledger': _sha(ROOT / 'data/agreement-ledger/ledger.csv'),
        'ledger_state': _sha(ROOT / 'data/agreement-ledger/state.json'),
    }
    state = json.loads((ROOT / 'data/pile-solver/state.json').read_text(encoding='utf-8'))
    check(state.get('auto') is False, 'repo pile-solver state.json auto is false before the replay')

    golden = json.loads(GOLDEN.read_text(encoding='utf-8'))
    off = replay(None)
    check(off == golden, 'flag unset: replay reads, writes, urls, verdicts, and files match the pre-change bytes')
    explicit = replay('off')
    check(explicit == off, "KPC_RESEARCH_SOURCES=off matches the unset flag byte for byte")
    check(BANNED not in json.dumps(off), 'flag off: the Grant County NM host is not read or written')
    check(not any(SIDE in k for k in off['offline_files']), 'flag off: the offline replay writes no rank side file')
    check(SIDE not in off['blackford_files'], 'flag off: the two-name replay writes no rank side file')
    outline_q = [u for u in off['urls'] if 'objectIds=' in u]
    county_q = [u for u in off['urls'] if 'outFields=GEOID' in u]
    check(outline_q and all('outFields=%2A' in u for u in outline_q),
          'flag off: outline queries still ask for every field (outFields=*)')
    check(county_q and all('outFields=GEOID%2CNAME%2CSTATE' in u for u in county_q),
          'flag off: county queries still ask for GEOID, NAME, and STATE only')

    report = replay('report')
    check(report['urls'] == off['urls'], 'report mode: the same layer URLs are read, including the same fields')
    check(report['verdicts'] == off['verdicts'], 'report mode: frozen-fixture verdicts are unchanged')
    check(report['ledger'] == off['ledger'], 'report mode: the agreement ledger bytes are unchanged')
    check(report['offline_files'] == off['offline_files'],
          'report mode: an offline replay (nothing fetched) writes the same files and no side file')
    check(_without_side(report['blackford_files']) == off['blackford_files'],
          'report mode: the two-name case writes the same solver files')
    extra_reads = sorted(set(report['reads']) - set(off['reads']))
    missing_reads = sorted(set(off['reads']) - set(report['reads']))
    extra_writes = sorted(set(report['writes']) - set(off['writes']))
    missing_writes = sorted(set(off['writes']) - set(report['writes']))
    check(missing_reads == [], f'report mode does not drop a read the default replay made ({missing_reads[:4]})')
    check(extra_reads == ['repo/data/research-sources/abbreviations.csv'],
          f'report mode reads the abbreviation list and nothing else extra ({extra_reads})')
    check(missing_writes == [], f'report mode does not drop a write the default replay made ({missing_writes[:4]})')
    check(extra_writes == ['root/blackford/data/pile-solver/research-rank.json'],
          f'report mode adds only the rank side file ({extra_writes})')
    check(BANNED not in json.dumps(report['urls']) and BANNED not in json.dumps(report['reads']),
          'report mode does not touch the Grant County NM host')

    ranked_ok, doc = _side_auto_false(report['blackford_files'])
    check(ranked_ok, f'report mode writes the side file with auto false ({doc if not ranked_ok else "ok"})')
    if ranked_ok:
        row = doc['ranks'][0]
        names = [(r.get('id'), r.get('score'), r.get('name')) for r in row['ranked']]
        check(row['park'] == 'Blackford Oaks W.M.A.' and row['ranked'][0]['id'] == 'oaks'
              and row['ranked'][0]['score'] > row['ranked'][1]['score'],
              f'Blackford Oaks W.M.A. ranks the wildlife area above Blackford Creek ({names})')
        check(all('verdict' not in r for r in row['ranked']), 'a rank is not a join verdict')
        bf = json.loads(report['blackford_files']['data/waiting/in/data/pile-solver/US-KY.json'])
        park = bf['parks']['US-7777']
        check(park['record_id'] == 'creek' and park['verdict'] == 'SOLVED-JOIN',
              f'the verdict stays the distance tie-break (creek), not the rank winner ({park["record_id"]} {park["verdict"]})')
        check(json.loads(report['blackford_files']['data/pile-solver/state.json']).get('auto') is False,
              'the replay state.json auto stays false')

    os.environ['KPC_RESEARCH_SOURCES'] = 'report'
    import kpc_research_sources as RS
    direct = RS.rank_outlines('Blackford Oaks W.M.A.', [
        {'id': 'creek', 'name': 'Blackford Creek'},
        {'id': 'oaks', 'name': 'Blackford Oaks Wildlife Management Area'},
    ])
    check(direct and direct[0]['id'] == 'oaks' and direct[0]['score'] >= 84 and direct[0]['score'] > direct[1]['score'],
          f'direct rank: dotted W.M.A. matches the wildlife area ({direct[:2]})')
    sga = RS.rank_outlines('Allegan SGA', [
        {'id': 'creek', 'name': 'Allegan Creek'},
        {'id': 'sga', 'name': 'Allegan State Game Area'},
    ])
    check(sga and sga[0]['id'] == 'sga' and sga[0]['score'] >= 84,
          f'abbreviation list: SGA ranks the state game area first ({sga[:2]})')
    os.environ.pop('KPC_RESEARCH_SOURCES', None)
    check(RS.rank_outlines('Blackford Oaks W.M.A.', [{'id': 'oaks', 'name': 'Blackford Oaks Wildlife Management Area'}]) == [],
          'flag off: rank_outlines returns nothing')
    full, core = RS.toolbox_canon('Blackford Oaks W.M.A.', report=False)
    check(core == 'blackford oaks' and 'wildlife management area' in full,
          f'toolbox canon expands dotted W.M.A. ({full!r} / {core!r})')
    check(RS.gated_source_fields('https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest') == {}
          and RS.gated_source_fields('https://example.test/layer', ['NAME']) == {},
          'flag off: source/field mapping returns nothing, including the banned host')
    os.environ['KPC_RESEARCH_SOURCES'] = 'report'
    check(RS.gated_source_fields('https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest', ['NAME']) == {},
          'report mode still refuses the Grant County NM host')
    check(RS.gated_source_fields('https://example.test/layer', ['NAME', 'ACRES']) == {},
          'this change adds no source/field mapping even in report mode')
    os.environ.pop('KPC_RESEARCH_SOURCES', None)

    src = (ROOT / '.github/scripts/kpc_pile_solver.py').read_text(encoding='utf-8')
    check("state['auto'] = True" not in src and 'state["auto"] = True' not in src,
          'the solver source does not set auto true')
    check(BANNED not in src and BANNED not in (ROOT / '.github/scripts/kpc_research_sources.py').read_text(encoding='utf-8'),
          'the new solver code does not name the banned host')
    check(repo_before == {
        'state': _sha(ROOT / 'data/pile-solver/state.json'),
        'ledger': _sha(ROOT / 'data/agreement-ledger/ledger.csv'),
        'ledger_state': _sha(ROOT / 'data/agreement-ledger/state.json'),
    }, 'the replay leaves the repo state.json and the agreement ledger untouched')
    print('ALL PASS' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    if '--dump-golden' in sys.argv:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(json.dumps(replay(None), ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        print('WROTE', GOLDEN)
        sys.exit(0)
    sys.exit(main())
