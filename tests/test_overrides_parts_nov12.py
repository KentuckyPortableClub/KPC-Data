#!/usr/bin/env python3
"""Nov 12 2026 (KPC owner): the KPC-Data half of KPC-Links #151 / E4 (US overrides split into overrides.json = manifest + parts
overrides-parks-NN.json). Checked here, offline, temp folders only:
  1) every KPC-Data reader of the Links US overrides gives the SAME whole set in both layouts (single file / manifest + parts):
     kpc_pile_penalty.key_join_of, kpc_pile_solver.decisions, kpc_release_approved.per_park_release (the ovr it hands to
     release_split), key_doctor.overrides_whole, kpc_fers_states.hand_rows (the per-state 2-fer hash 'data:' part);
  2) a missing / corrupt / stray part, a ref in two files, a 'no' in a part = a LOUD failure (never a partial set);
  3) the waiting room's override merge: single -> single byte for byte as main (1ddf3a7) when git has main; parts over single;
     parts over parts with a newer local decision kept; a part count that shrinks leaves no stale file; no park in two places;
     a bad incoming set goes nowhere; the result loads with KPC-Links' own kpc_overrides.load when a copy is found;
  4) the copy step (kpc-copy-from-links.yml, its inline Python run on a temp git tree): the set comes over whole;
  5) the pile-solver pre-check runs kpc_precheck_whole.py when KPC-Links has it, kpc_precheck.py otherwise (script + workflow);
  6) the edited workflows parse, triggers / cron / concurrency equal main's; no unmarked '|| true' added;
  7) a guard: no KPC-Data code reads data/us-key/overrides.json by name except through kpc_overrides_whole.
KPC-Links' kpc_overrides.py is looked for at $KPC_LINKS_OVERRIDES_PY, $LINKS/.github/scripts, ../links/.github/scripts (SKIP lines
when none). The real split: $KPC_E4_SPLIT=<dir with before/data/us-key/overrides.json and after/data/us-key/*> (SKIP when unset).
Run: python3 -B tests/test_overrides_parts_nov12.py"""
import copy, importlib.util, json, os, pathlib, re, shutil, subprocess, sys, tempfile, types

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
BASE = '1ddf3a7a79fc'   # KPC-Data main before this change
os.environ.pop('LINKS', None)
sys.path.insert(0, str(S))
import kpc_overrides_whole as OVW  # noqa: E402

ok = True


def check(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (f'  [{extra}]' if extra and not cond else ''), flush=True)
    ok = ok and bool(cond)


def skip(name, why): print(f'SKIP {name} ({why})', flush=True)


def raises(fn, *a, **k):
    try: fn(*a, **k)
    except OVW.OverridesError as e: return str(e) or True
    except Exception: return False  # noqa: BLE001  (a different error is not a pass)
    return False


def links_module():
    for c in (os.environ.get('KPC_LINKS_OVERRIDES_PY'), os.environ.get('KPC_LINKS') and pathlib.Path(os.environ['KPC_LINKS']) / '.github/scripts/kpc_overrides.py',
              ROOT.parent / 'links/.github/scripts/kpc_overrides.py'):
        if c and pathlib.Path(c).is_file():
            sp = importlib.util.spec_from_file_location('_links_kpc_overrides_test', c); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
            return m
    return None


LK = links_module()


# ------------------------------------------------------------------ fixtures
def doc(n=120, tag='', no_every=7):
    parks = {}
    for i in range(1, n + 1):
        r = f'US-{1000 + i * 13}'
        e = {'join': [f'rec{i}{tag}', f'x{i}'], 'fp': {f'rec{i}{tag}': [f'Record {i}', 'tst']}, 'when': '2026-11-01', 'why': f'person {i} · signed {tag}'}
        if i % no_every == 0: e['no'] = [f'bad{i}', f'Wrong Park {i}']
        parks[r] = e
    return {'note': 'test overrides', 'blocked_ids_about': 'ids never joined', 'blocked_ids': ['b1', 'b2'], 'parks': parks}


class Small:
    """pack small so a 120-park fixture splits into several parts (local copy only; a tree without KPC-Links' module uses it)"""
    def __init__(s, cap=9000, pack=8000, fill=5000): s.v = (cap, pack, fill)
    def __enter__(s): s.old = (OVW.CAP, OVW.PACK, OVW.FILL); OVW.CAP, OVW.PACK, OVW.FILL = s.v
    def __exit__(s, *a): OVW.CAP, OVW.PACK, OVW.FILL = s.old


def write_single(d, dd):
    d = pathlib.Path(d); d.mkdir(parents=True, exist_ok=True)
    for f in d.glob(OVW.PART_GLOB): f.unlink()
    (d / 'overrides.json').write_text(json.dumps(dd, indent=1, ensure_ascii=False), encoding='utf-8')


def split_files(dd, sticky=None, **k):
    with Small(**k): return OVW.layout_like(sticky or {}, dd) if sticky else OVW.layout(pathlib.Path(tempfile.mkdtemp()) / 'overrides.json', dd)


def write_files(d, files):
    d = pathlib.Path(d); d.mkdir(parents=True, exist_ok=True)
    for f in d.glob(OVW.PART_GLOB): f.unlink()
    for n, b in files.items(): (d / n).write_bytes(b)


def tree(single=None, files=None, ca=None):
    t = pathlib.Path(tempfile.mkdtemp(prefix='kpc-ovr-'))
    if single is not None: write_single(t / 'data/us-key', single)
    if files is not None: write_files(t / 'data/us-key', files)
    if ca is not None: write_single(t / 'data/ca-key', ca)
    return t


def canon(x): return OVW.canon_sha(x)


D = doc()
FILES = split_files(D)
check('fixture: the 120-park document splits into a manifest + several parts', len(FILES) >= 4 and 'overrides.json' in FILES, sorted(FILES))
man = json.loads(FILES['overrides.json'])
check("fixture: every park with a 'no' stays in the manifest, none in a part",
      set(man['parks']) == {r for r, v in D['parks'].items() if v.get('no')} and all(not OVW.has_no(v) for n in man['parts'] for v in json.loads(FILES[n])['parks'].values()))
T1, T2 = tree(single=D), tree(files=FILES)
w1, w2 = OVW.load_whole(T1 / 'data/us-key/overrides.json'), OVW.load_whole(T2 / 'data/us-key/overrides.json')
check('helper: both layouts load to the same whole park set', canon(w1['parks']) == canon(w2['parks']) == canon(D['parks']))
check('helper: headers (note aside) and blocked_ids are the same in both layouts',
      w1['blocked_ids'] == w2['blocked_ids'] and w1['blocked_ids_about'] == w2['blocked_ids_about'])

# ------------------------------------------------------------------ KPC-Links' own module = the local copy
if LK is None:
    skip('local copy = KPC-Links kpc_overrides (load / layout)', 'no KPC-Links kpc_overrides.py found')
else:
    with Small():
        LK.CAP, LK.PACK, LK.FILL = OVW.CAP, OVW.PACK, OVW.FILL
        lf = LK.layout(pathlib.Path(tempfile.mkdtemp()) / 'overrides.json', D)
    check('local copy = KPC-Links kpc_overrides: layout gives the same bytes', lf == FILES)
    check('local copy = KPC-Links kpc_overrides: load gives the same document', LK.load(T2 / 'data/us-key/overrides.json') == w2)
    LK.CAP, LK.PACK, LK.FILL = 1_000_000, 900_000, 700_000
    t = tree(files=FILES); (t / 'data/us-key/overrides-parks-99.json').write_text('{"parks": {}}')
    check('helper prefers the KPC-Links module that sits in the same tree', OVW.module(t / 'data/us-key/overrides.json') is OVW)   # no module in a temp tree
    (t / '.github/scripts').mkdir(parents=True); shutil.copy(LK.__file__, t / '.github/scripts/kpc_overrides.py')
    m = OVW.module(t / 'data/us-key/overrides.json')
    check('helper: a tree with .github/scripts/kpc_overrides.py is read with that module', m is not OVW and hasattr(m, 'layout'))
    check('helper: an error of the KPC-Links module comes out as OverridesError (stray part)', bool(raises(OVW.load_whole, t / 'data/us-key/overrides.json')))

# ------------------------------------------------------------------ fail closed (the helper)
def bad_tree(how):
    t = tree(files=FILES); d = t / 'data/us-key'; p1 = json.loads(FILES['overrides.json'])['parts'][0]
    if how == 'missing': (d / p1).unlink()
    if how == 'corrupt': (d / p1).write_text('{"parks": {', encoding='utf-8')
    if how == 'digest':
        x = json.loads((d / p1).read_text()); r = next(iter(x['parks'])); x['parks'][r]['join'].append('handedit'); (d / p1).write_text(json.dumps(x))
    if how == 'stray': (d / 'overrides-parks-77.json').write_text('{"parks": {}}')
    if how == 'two':
        m = json.loads((d / 'overrides.json').read_text()); x = json.loads((d / p1).read_text()); r = next(iter(x['parks']))
        m['parks'][r] = x['parks'][r]; (d / 'overrides.json').write_text(json.dumps(m))
    if how == 'nopart':
        m = json.loads((d / 'overrides.json').read_text()); x = json.loads((d / p1).read_text()); r = next(iter(x['parks']))
        x['parks'][r]['no'] = ['z']; m['parts_sha256'][p1] = OVW.canon_sha(x['parks']); (d / p1).write_text(json.dumps(x)); (d / 'overrides.json').write_text(json.dumps(m))
    if how == 'nomanifest': (d / 'overrides.json').unlink()
    return t


for how in ('missing', 'corrupt', 'digest', 'stray', 'two', 'nopart', 'nomanifest'):
    check(f'helper fails closed: {how} part / file -> OverridesError (missing_ok does not hide it)',
          bool(raises(OVW.load_whole, bad_tree(how) / 'data/us-key/overrides.json', missing_ok=True)))
check('helper: no manifest and no part file + missing_ok = an empty set (temp trees, as before)',
      OVW.load_whole(pathlib.Path(tempfile.mkdtemp()) / 'data/us-key/overrides.json', missing_ok=True) == {'parks': {}})

# ------------------------------------------------------------------ reader 1: pile penalty
import kpc_pile_penalty as TP  # noqa: E402
k1, k2 = TP.key_join_of(T1), TP.key_join_of(T2)
check('kpc_pile_penalty.key_join_of: the same joins in both layouts (every park)', k1 == k2 and len(k1) == len(D['parks']))
check('kpc_pile_penalty.key_join_of: a missing part is a loud error', bool(raises(TP.key_join_of, bad_tree('missing'))))
check('kpc_pile_penalty.key_join_of: no overrides at all = {} (as before)', TP.key_join_of(pathlib.Path(tempfile.mkdtemp())) == {})

# ------------------------------------------------------------------ reader 2: pile solver decisions() and its pre-check
for name in ('kpc_key_rules', 'kpc_precheck'):   # KPC-Links modules the solver imports at load (not needed for decisions())
    if name not in sys.modules:
        try: __import__(name)
        except Exception: sys.modules[name] = types.ModuleType(name)  # noqa: BLE001
try:
    import kpc_pile_solver as PS  # noqa: E402
except Exception as e:  # noqa: BLE001
    PS = None; skip('kpc_pile_solver.decisions', f'does not import here ({type(e).__name__}: {str(e)[:80]})')
if PS is not None:
    CA = {'parks': {'CA-0101': {'join': ['c1'], 'when': '2026-11-02'}}}
    def dec(t):
        PS.LINKS, PS.DATA = t, t
        return PS.decisions()[0]
    a, b = dec(tree(single=D, ca=CA)), dec(tree(files=FILES, ca=CA))
    check('kpc_pile_solver.decisions: the same overrides in both layouts (US whole + CA)', a == b and len(a) == len(D['parks']) + 1)
    check('kpc_pile_solver.decisions: a part that fails its digest is a loud error', bool(raises(dec, bad_tree('digest'))))
    for whole in (True, False):
        t = pathlib.Path(tempfile.mkdtemp()); (t / '.github/scripts').mkdir(parents=True)
        for n in ('kpc_precheck.py', 'kpc_precheck_whole.py') if whole else ('kpc_precheck.py',):
            (t / '.github/scripts' / n).write_text(f"import os, pathlib\npathlib.Path(os.environ['OUT']).mkdir(parents=True, exist_ok=True)\n(pathlib.Path(os.environ['OUT']) / 'which.txt').write_text('{n}')\n")
        PS.LINKS = t; old = os.environ.pop('PILE', None); os.environ['RUNNER_TEMP'] = str(t)
        try: got = (PS.pile_path().parent / 'which.txt').read_text()
        finally:
            os.environ.pop('RUNNER_TEMP', None)
            if old is not None: os.environ['PILE'] = old
        check(f"kpc_pile_solver.pile_path runs {'kpc_precheck_whole.py when KPC-Links has it' if whole else 'kpc_precheck.py on a KPC-Links checkout from before the split'}",
              got == ('kpc_precheck_whole.py' if whole else 'kpc_precheck.py'), got)

# ------------------------------------------------------------------ reader 3: per-park release (release_split gets the whole set)
import kpc_waiting_room as W  # noqa: E402
import kpc_release_approved as RA  # noqa: E402
sys.path.insert(0, str(S / 'draft/tools/kpc_engine'))
from core import key_doctor as KD  # noqa: E402


def per_park(t):
    got = []
    old = (W.DATA, W.W, W.LINKS, RA.DRY, KD.release_split)
    d = pathlib.Path(tempfile.mkdtemp()); W.DATA, W.W, W.LINKS, RA.DRY = d, d / 'data/waiting', t, True
    (W.W / 'in/data/us-key').mkdir(parents=True)
    (W.W / 'in/data/us-key/index.json').write_text(json.dumps({'build': 'US-b1'}))
    (W.W / 'in/data/us-key/US-ZZ.json').write_text(json.dumps({'parks': {'US-1013': {'n': 'A', 'm': [[1, 'A', 2, 'exact: A']]}}}))
    KD.release_split = lambda new, live, fail, ovr: (got.append(ovr), (new, {}))[1]
    A = {'items': [{'what': 'us-key', 'chat11': 'KEY NO 2026-11-12 US-1013', 'chat2': 'rechecked', 'date': '2026-11-12', 'time': '10:00 AM', 'build': 'US-b1'}]}
    out = []
    try:
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): RA.per_park_release(A, out, {})
    finally: W.DATA, W.W, W.LINKS, RA.DRY, KD.release_split = old
    return got, buf.getvalue()


g1, _ = per_park(T1); g2, _ = per_park(T2)
check('kpc_release_approved.per_park_release: release_split gets the same whole overrides in both layouts',
      len(g1) == len(g2) == 1 and canon(g1[0]) == canon(g2[0]) == canon(D['parks']))
g3, said = per_park(bad_tree('missing'))
check('kpc_release_approved.per_park_release: a missing part = ::error, nothing released per park', g3 == [] and '::error title=Per-park release::' in said, said[:200])

# ------------------------------------------------------------------ reader 4: key doctor
o1, o2 = KD.overrides_whole(T1), KD.overrides_whole(T2)
check('key_doctor.overrides_whole: the same document in both layouts, single-file shape (no parts key)',
      canon(o1['parks']) == canon(o2['parks']) and 'parts' not in o2)
check('key_doctor.overrides_whole: a corrupt part is a loud error', bool(raises(KD.overrides_whole, bad_tree('corrupt'))))

# ------------------------------------------------------------------ reader 5: per-state 2-fer hash data part
import kpc_fers_states as FS  # noqa: E402
h1, h2 = FS.hand_rows(T1), FS.hand_rows(T2)
check("kpc_fers_states.hand_rows: the us overrides rows are the same in both layouts (the 'data:' part of every state hash)",
      h1['data/us-key/overrides.json'] == h2['data/us-key/overrides.json'] and len(h2['data/us-key/overrides.json']) == len(D['parks']))
import io, contextlib  # noqa: E402
with contextlib.redirect_stderr(io.StringIO()): hb = FS.hand_rows(bad_tree('stray'))
check('kpc_fers_states.hand_rows: an unreadable set is marked (every state hash then differs), never an empty slice',
      FS.UNREADABLE in hb['data/us-key/overrides.json'])
try:
    kd = pathlib.Path(tempfile.mkdtemp())
    p1 = FS.state_hash('US-ZZ', T1, kd, {}, {'US-1013': 'US-ZZ'}, 'c', h1)[1]
    p2 = FS.state_hash('US-ZZ', T2, kd, {}, {'US-1013': 'US-ZZ'}, 'c', h2)[1]
    pb = FS.state_hash('US-ZZ', T2, kd, {}, {'US-1013': 'US-ZZ'}, 'c', hb)[1]
    k = 'data:data/us-key/overrides.json'
    check('kpc_fers_states.state_hash: the same parts in both layouts; an unreadable set gives another overrides part', p1 == p2 and pb[k] != p1[k])
except Exception as e:  # noqa: BLE001
    skip('kpc_fers_states.state_hash on fixtures', f'{type(e).__name__}: {str(e)[:100]}')


# ------------------------------------------------------------------ the waiting room's override merge
class Room:
    def __init__(s, live_single=None, live_files=None, held_single=None, held_files=None):
        s.d = pathlib.Path(tempfile.mkdtemp(prefix='kpc-room-'))
        s.old = (W.DATA, W.W, W.LINKS); W.DATA, W.W, W.LINKS = s.d, s.d / 'data/waiting', s.d / 'nolinks'
        if live_single is not None: write_single(s.d / 'data/us-key', live_single)
        if live_files is not None: write_files(s.d / 'data/us-key', live_files)
        if held_single is not None: write_single(W.W / 'in/data/us-key', held_single)
        if held_files is not None: write_files(W.W / 'in/data/us-key', held_files)
    def live(s): return {f.name: f.read_bytes() for f in sorted((s.d / 'data/us-key').iterdir()) if OVW.is_member(f.name)}
    def held(s): return sorted(f.name for f in (W.W / 'in/data/us-key').glob('*')) if (W.W / 'in/data/us-key').is_dir() else []
    def release_all(s):
        for f in sorted((W.W / 'in/data/us-key').glob('*.json')): W.mode_release(f'data/us-key/{f.name}')
    def close(s): W.DATA, W.W, W.LINKS = s.old


def loads_clean(d):
    p = pathlib.Path(d) / 'data/us-key/overrides.json'
    try: return (LK.load(p) if LK else OVW.load(p))
    except Exception as e: return f'{type(e).__name__}: {e}'  # noqa: BLE001


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): r = fn(*a)
    return r, buf.getvalue()


WHO = 'KPC-Links kpc_overrides.load' if LK else 'the local copy (no KPC-Links module found)'

# a) single -> single: byte for byte as main
def main_module():
    r = subprocess.run(['git', 'show', f'{BASE}:.github/scripts/kpc_waiting_room.py'], cwd=ROOT, capture_output=True)
    if r.returncode: return None
    t = pathlib.Path(tempfile.mkdtemp()) / 'kpc_waiting_room_main.py'; t.write_bytes(r.stdout)
    sp = importlib.util.spec_from_file_location('kpc_waiting_room_main', t); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


WM = main_module()
if WM is None: skip('single -> single byte for byte as main', f'git has no {BASE}')
else:
    live = {'note': 'n', 'parks': {'US-1': {'join': ['a'], 'when': '2026-11-08'}, 'US-2': {'join': ['b', 'c'], 'when': '2026-11-09', 'fp': {'c': ['C', 1]}}}}
    for label, inc in (('nothing kept (the file goes live as it is)', {'note': 'n', 'parks': {'US-1': {'join': ['a'], 'when': '2026-11-09'}, 'US-2': {'join': ['b', 'c'], 'when': '2026-11-10'}}}),
                       ('newer edits here kept (merged)', {'note': 'n', 'parks': {'US-2': {'join': ['b'], 'when': '2026-11-02'}, 'US-3': {'no': ['z'], 'when': '2026-11-09'}}})):
        res = []
        for mod in (WM, W):
            d = pathlib.Path(tempfile.mkdtemp()); old = (mod.DATA, mod.W); mod.DATA, mod.W = d, d / 'data/waiting'
            try:
                write_single(d / 'data/us-key', live); inc_p = d / 'in.json'; inc_p.write_text(json.dumps(inc, indent=2))
                _, said = quiet(mod.promote_file, 'data/us-key/overrides.json', None, inc_p)
                res.append(((d / 'data/us-key/overrides.json').read_bytes(), (d / 'data/waiting/previous/data/us-key/overrides.json').read_bytes(), said))
            finally: mod.DATA, mod.W = old
        check(f'single -> single, {label}: live file, undo copy and messages byte for byte as main', res[0] == res[1])

# b) main (before this change) on parts over single: the fork this change prevents
if WM is not None:
    d = pathlib.Path(tempfile.mkdtemp()); old = (WM.DATA, WM.W); WM.DATA, WM.W = d, d / 'data/waiting'
    try:
        write_single(d / 'data/us-key', D); write_files(d / 'in', FILES)
        for n in FILES: quiet(WM.promote_file, f'data/us-key/{n}', None, d / 'in' / n)
        r = loads_clean(d)
        check('before this change: parts over a single copy fork it (park in two places / load fails) - the bug, shown', isinstance(r, str), str(r)[:80])
    finally: WM.DATA, WM.W = old

# c) parts incoming over a single local copy (the first copy after KPC-Links E4)
R = Room(live_single=D, held_files=FILES)
try:
    _, said = quiet(R.release_all)
    check('parts over single: the live set is the incoming files byte for byte (nothing newer here)', R.live() == FILES, said[-300:])
    r = loads_clean(R.d)
    check(f'parts over single: the result loads cleanly with {WHO}, every park once', isinstance(r, dict) and canon(r['parks']) == canon(D['parks']))
    check('parts over single: the held files left the waiting room; the old single file is the undo copy',
          R.held() == [] and json.loads((W.W / 'previous/data/us-key/overrides.json').read_text()) == D)
finally: R.close()

# d) parts incoming over single local, with a NEWER local decision
Dl = copy.deepcopy(D); rr = sorted(json.loads(FILES[man['parts'][1]])['parks'])[3]
Dl['parks'][rr]['join'].append('localjoin'); Dl['parks'][rr]['when'] = '2026-11-11'
Dl['parks']['US-99999'] = {'join': ['onlyhere'], 'when': '2026-11-11', 'why': 'hand edit on the KPC-Data copy'}
R = Room(live_single=Dl, held_files=FILES)
try:
    _, said = quiet(R.release_all)
    r = loads_clean(R.d)
    check(f'parts over single + newer edits here: kept (Nov 9 rule) and the result loads cleanly with {WHO}',
          isinstance(r, dict) and 'localjoin' in r['parks'][rr]['join'] and 'US-99999' in r['parks'] and len(r['parks']) == len(D['parks']) + 1, str(r)[:120])
    check('parts over single + newer edits: the warning names the kept parks', '::warning title=Overrides kept::' in said and rr in said)
    check('parts over single + newer edits: same part names as the incoming set (sticky layout), no extra file', sorted(R.live()) == sorted(FILES))
finally: R.close()

# e) parts over parts, a newer local decision kept, the 'no' moves to the manifest
Di = copy.deepcopy(D); Di['parks'][rr]['why'] += ' (rebuilt)'; Di['parks'][rr]['when'] = '2026-11-05'
INC = split_files(Di, sticky=FILES)
Dl = copy.deepcopy(D); Dl['parks'][rr]['no'] = ['localno']; Dl['parks'][rr]['when'] = '2026-11-11'
LIVE = split_files(Dl, sticky=FILES)
R = Room(live_files=LIVE, held_files=INC)
try:
    _, said = quiet(R.release_all)
    r = loads_clean(R.d)
    lm = json.loads(R.live()['overrides.json'])
    check(f'parts over parts + newer local NO: kept, the park sits in the manifest only, loads cleanly with {WHO}',
          isinstance(r, dict) and r['parks'][rr].get('no') == ['localno'] and rr in lm['parks']
          and all(rr not in json.loads(b)['parks'] for n, b in R.live().items() if n != 'overrides.json'), str(r)[:120])
    ch = [n for n in INC if R.live().get(n) != INC[n]]
    check('parts over parts + one kept park: only its part and the manifest differ from the incoming files', sorted(ch) == sorted({'overrides.json', man['parts'][1]}), ch)
finally: R.close()

# f) the part count shrinks: no stale part left (live, undo copy), the old held part leaves the waiting room
LIVE3 = split_files(D, fill=2500)
INC2 = split_files(D, fill=7900, pack=8500)
R = Room(live_files=LIVE3, held_files=INC2)
try:
    (W.W / 'in/data/us-key/overrides-parks-31.json').write_text('{"parks": {}}')   # an old held part a superseded build left
    n_live, n_inc = len(LIVE3) - 1, len(INC2) - 1
    _, said = quiet(R.release_all)
    check(f'part count {n_live} -> {n_inc}: exactly the incoming files are live, no stale part', R.live() == INC2 and n_live > n_inc, sorted(R.live()))
    check(f'part count shrinks: the result loads cleanly with {WHO}', isinstance(loads_clean(R.d), dict))
    prev = W.W / 'previous/data/us-key'
    check('part count shrinks: the undo copy is the old set whole (no part of another set)', {f.name: f.read_bytes() for f in prev.iterdir()} == LIVE3)
    check('part count shrinks: the old held part left the waiting room (named in the notice)', R.held() == [] and 'overrides-parks-31.json' in said)
finally: R.close()

# g) a bad incoming set goes nowhere (digest), the judge holds it, the live set stays
BAD = dict(FILES); p1 = man['parts'][0]; x = json.loads(BAD[p1]); x['parks'][next(iter(x['parks']))]['join'].append('hand'); BAD[p1] = json.dumps(x).encode()
R = Room(live_single=D, held_files=BAD)
try:
    v = W.judge(f'data/us-key/{p1}', json.loads(BAD[p1]), *W.live_of(f'data/us-key/{p1}'))
    check('judge: a part of a set that does not read whole is HELD (F-4), never passed alone', v['verdict'] == 'HOLD' and 'does not read whole' in ' '.join(v['why']), v)
    before = R.live()
    _, said = quiet(R.release_all)
    check('a bad incoming set: ::error, the live copy is unchanged, every held file stays', R.live() == before and len(R.held()) == len(BAD) and '::error title=Overrides set::' in said)
finally: R.close()

R = Room(live_single=D, held_files=FILES)
try:
    vs = [W.judge(f'data/us-key/{n}', json.loads(FILES[n]), *W.live_of(f'data/us-key/{n}')) for n in sorted(FILES)]
    check('judge: a whole set PASSes, each part with a note that it goes live with overrides.json', all(v['verdict'] == 'PASS' for v in vs)
          and all('goes live with' in ' '.join(v['notes']) for v in vs if not v['path'].endswith('/overrides.json')), [v['why'] for v in vs])
    W.grade_queue(vs)
    gq = (R.d / 'data/status/grade-queue.md').read_text()
    check('grade list: the manifest line counts the WHOLE set (no 4,000 "gone" parks); parts point at it',
          'a part of the override set, counted with data/us-key/overrides.json' in gq and f"0 new, 0 changed, 0 gone, {len(D['parks'])} same" in gq, gq[:400])
    W.mode_check(False)
    check('mode_check (no promotion) keeps the held set and promotes nothing', R.held() == sorted(FILES) and R.live() == {'overrides.json': (R.d / 'data/us-key/overrides.json').read_bytes()})
finally: R.close()

# h) the release-approved folder path: keep_held never rewrites an overrides file
R = Room(live_single=D, held_files=FILES)
try:
    f = W.W / 'in/data/us-key' / man['parts'][0]; before = f.read_bytes()
    r = next(iter(json.loads(before)['parks']))
    src = (S / 'kpc_release_approved.py').read_text(encoding='utf-8')
    check('release-approved: keep_held is skipped for override files (a verdict hold never makes an override row a pin)',
          "and not W.ov_member(r2) else 0" in src and W.ov_member(f'data/us-key/{f.name}') and W.ov_member('data/us-key/overrides.json') and not W.ov_member('data/us-key/US-KY.json'))
finally: R.close()

# i) the real split (KPC-Links E4's own files)
E4 = os.environ.get('KPC_E4_SPLIT')
if not E4: skip('round trip on the real split', 'KPC_E4_SPLIT not set')
else:
    E4 = pathlib.Path(E4); single = json.loads((E4 / 'before/data/us-key/overrides.json').read_text(encoding='utf-8'))
    real = {f.name: f.read_bytes() for f in (E4 / 'after/data/us-key').iterdir() if OVW.is_member(f.name)}
    mine = OVW.layout(pathlib.Path(tempfile.mkdtemp()) / 'overrides.json', single)
    check(f"real split: the local copy's layout of the single file = KPC-Links E4's files byte for byte ({len(real)} files)", mine == real, sorted(mine))
    wr = OVW.load_whole(E4 / 'after/data/us-key/overrides.json')
    check(f"real split: whole set = the single file ({len(wr['parks'])} parks, canonical sha256 {canon(wr['parks'])[:12]})", canon(wr['parks']) == canon(single['parks']))
    R = Room(held_files=real); write_single(R.d / 'data/us-key', single)
    shutil.copy(E4 / 'before/data/us-key/overrides.json', R.d / 'data/us-key/overrides.json')
    try:
        _, said = quiet(R.release_all)
        check('real split over the real single copy: live = E4 files byte for byte, loads with ' + WHO, R.live() == real and isinstance(loads_clean(R.d), dict), said[-200:])
    finally: R.close()
    sl = copy.deepcopy(single); ref = sorted(json.loads(real['overrides-parks-02.json'])['parks'])[100]
    sl['parks'][ref]['join'] = list(sl['parks'][ref].get('join') or []) + ['kpcdata-hand']; sl['parks'][ref]['when'] = '2099-01-01'
    R = Room(held_files=real); write_single(R.d / 'data/us-key', sl)
    try:
        _, said = quiet(R.release_all)
        r = loads_clean(R.d); ch = sorted(n for n in real if R.live().get(n) != real[n])
        check(f'real split + one newer hand edit here: kept in its part ({ch}), loads cleanly with {WHO}, every park once',
              isinstance(r, dict) and 'kpcdata-hand' in r['parks'][ref]['join'] and len(r['parks']) == len(single['parks']) and ch == ['overrides-parks-02.json', 'overrides.json'], ch)
    finally: R.close()

# ------------------------------------------------------------------ the copy step (inline Python of kpc-copy-from-links.yml)
import yaml  # noqa: E402
WF = ROOT / '.github/workflows'
cy = yaml.safe_load((WF / 'kpc-copy-from-links.yml').read_text(encoding='utf-8'))
run = [s for s in cy['jobs']['copy']['steps'] if s.get('id') == 'kept_green_1'][0]['run']
i = run.index("KD=$(cd kpcdata && python3 - <<'PY'"); j = run.index('\nPY\n', i); code = run[i:j].split('\n', 1)[1]


def copy_step(links_files, data_files, seen_from):
    t = pathlib.Path(tempfile.mkdtemp(prefix='kpc-copy-')); L, K = t / 'links', t / 'kpcdata'
    for base, fs in ((L, links_files), (K, data_files)):
        for n, b in fs.items(): (base / 'data/us-key').mkdir(parents=True, exist_ok=True); (base / 'data/us-key' / n).write_bytes(b)
    g = lambda *a: subprocess.run(['git', '-C', str(K)] + list(a), capture_output=True, text=True)
    g('init', '-q'); g('-c', 'user.name=t', '-c', 'user.email=t@t', 'add', '-A'); g('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'base')
    import hashlib
    (K / 'data/waiting').mkdir(parents=True)
    (K / 'data/waiting/key-files-seen.json').write_text(json.dumps({f'data/us-key/{n}': hashlib.sha1(b).hexdigest() for n, b in seen_from.items()}))
    for n, b in links_files.items(): (K / 'data/us-key' / n).write_bytes(b)   # the rsync before it
    (K / 'code.py').write_text(code)
    r = subprocess.run([sys.executable, '-I', 'code.py'], cwd=K, capture_output=True, text=True)
    (K / 'code.py').unlink()
    return r, {f.name: f.read_bytes() for f in (K / 'data/us-key').iterdir()}


KEY = {'US-ZZ.json': b'{"parks": {}}'}
r, got = copy_step({**FILES, **KEY}, {'overrides.json': json.dumps(D, indent=1).encode(), **KEY}, {'overrides.json': json.dumps(D, indent=1).encode(), **KEY})
check('copy step: the first split set comes over whole (manifest + every part); an unchanged key file stays KPC-Data\'s',
      r.returncode == 0 and 'DIRS=data/us-key' in r.stdout and all(got.get(n) == b for n, b in FILES.items()), (r.stdout + r.stderr)[-300:])
check("copy step: the notice counts the parts with their overrides.json, not as key files",
      f'1 key file(s) changed by a build since the last copy (overrides.json) + {len(FILES) - 1} overrides part file(s) of the same set' in r.stdout, r.stdout[:300])
OLDP = split_files(doc(tag='old'), sticky=None)
NEWP = dict(OLDP); mm = json.loads(OLDP['overrides.json']); rn = next(iter(mm['parks'])); mm['parks'][rn]['why'] += ' changed'
NEWP['overrides.json'] = (json.dumps(mm, indent=1, ensure_ascii=False) + '\n').encode()
HERE_P = {n: (b if n == 'overrides.json' else b'{"parks": {"US-1": {"join": ["kpcdata-own-layout"]}}}\n') for n, b in OLDP.items()}
r, got = copy_step({**NEWP, **KEY}, {**HERE_P, **KEY}, {**OLDP, **KEY})
check("copy step: only the manifest changed in KPC-Links, yet every part comes over too (KPC-Data's own parts never mix with a new manifest)",
      r.returncode == 0 and all(got.get(n) == b for n, b in NEWP.items()), (r.stdout + r.stderr)[-300:])
r, got = copy_step({'overrides.json': b'{"parks": {}}', **KEY}, {'overrides.json': b'{"parks": {"US-1": {}}}', **KEY}, {'overrides.json': b'{"parks": {}}', **KEY})
check('copy step: nothing changed in KPC-Links = data/us-key does not come over (the step then puts the folder back), as before',
      r.returncode == 0 and r.stdout.rstrip().endswith('DIRS=') and 'us-key: 0 key file(s) changed' in r.stdout, r.stdout[-200:])

# ------------------------------------------------------------------ workflows: parse, triggers as main, no unmarked || true added
def at_base(name):
    r = subprocess.run(['git', 'show', f'{BASE}:.github/workflows/{name}'], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


for name in ('kpc-copy-from-links.yml', 'kpc-pile-solver.yml'):
    now = (WF / name).read_text(encoding='utf-8'); y = yaml.safe_load(now)
    check(f'{name}: parses with PyYAML (on / jobs present)', isinstance(y, dict) and (True in y or 'on' in y) and isinstance(y.get('jobs'), dict))
    old = at_base(name)
    if old is None: skip(f'{name}: triggers, permissions, concurrency equal main', f'git has no {BASE}'); continue
    yo = yaml.safe_load(old)
    check(f'{name}: triggers (cron), permissions and concurrency equal main', y.get(True) == yo.get(True) and y.get('permissions') == yo.get('permissions') and y.get('concurrency') == yo.get('concurrency'))
    added = [l for l in now.splitlines() if l not in set(old.splitlines())]
    check(f'{name}: no unmarked "|| true" added', not [l for l in added if '|| true' in l and '# ok:' not in l], added)
ps = (WF / 'kpc-pile-solver.yml').read_text(encoding='utf-8')
check('kpc-pile-solver.yml: both pre-check runs use kpc_precheck_whole.py when KPC-Links has it, kpc_precheck.py otherwise',
      ps.count('PRE=.github/scripts/kpc_precheck_whole.py') == 2 and 'python3 .github/scripts/kpc_precheck.py' not in ps and ps.count('python3 "$PRE"') == 2)

# ------------------------------------------------------------------ guard: no reader of the US overrides by name
ALLOW = {'kpc_overrides_whole.py'}
bad = []
for f in sorted(list(S.rglob('*.py')) + list(WF.glob('*.yml'))):
    if f.name in ALLOW or '/tests/' in f.as_posix(): continue
    for i, l in enumerate(f.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if 'us-key/overrides.json' in l and re.search(r'json\.load|\bload\(|_ld\(|open\(|read_text|read_bytes', l) and 'OVW.' not in l:
            bad.append(f'{f.relative_to(ROOT)}:{i}')
check('guard: no KPC-Data code reads data/us-key/overrides.json by name outside kpc_overrides_whole', not bad, bad)

print('ALL PASSED' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
