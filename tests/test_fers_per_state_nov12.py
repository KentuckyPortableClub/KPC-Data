#!/usr/bin/env python3
"""2-fers per state / province (KPC owner, 2026-11-12, part C). Offline: temp folders, local git 'origin' repos, stub builders; no network.
  1 one failed / short state: the others save; the failed state's saved file is byte for byte as before; the table lists it red;
    nothing else is blocked; a state another run saved since the job started is never overwritten (stale base)
  2 a key change in one state moves the hash of that state and of the neighbours it ACTUALLY pairs with, not of a state with no shared
    pair; reuse is OFF by default; an unchanged state is byte-identical reused vs rebuilt; a shared-code change moves every state
  3 a line that breaks (the southeast fetcher case) saves nothing and touches no other line's files; a dirty state does not dirty the
    gate for a line whose own states are clean and unchanged; a cancelled run saves nothing
  4 the two area maps cannot disagree: the chain plans exactly the bot's state sets
  5 workflows parse, no new cron, only rebuilt states are stamped (honest), the fers rules hash is not moved by this patch
  6 no cross-border pair is written by two states (owner rule; fail closed on a double write; a row is never lost)"""
import importlib.util, json, os, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def mod(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


sys.path.insert(0, str(HERE / '.github/scripts'))
F = mod('kpc_fers_states', HERE / '.github/scripts/kpc_fers_states.py')
P = mod('kpc_fers_chain_plan', HERE / '.github/scripts/kpc_fers_chain_plan.py')
CG = mod('kpc_fers_chain_gate', HERE / '.github/scripts/kpc_fers_chain_gate.py')
ENV0 = {k: v for k, v in os.environ.items() if not k.startswith(('GITHUB_', 'KPC_'))}


def w(p, d):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(d if isinstance(d, str) else json.dumps(d, sort_keys=True))


def git(cwd, *a):
    return subprocess.run(['git', '-C', str(cwd), *a], capture_output=True, text=True, env=dict(ENV0, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t',
                          GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t'))


# parks: FL 0001 0002, GA 0003 0004, AL 0005, HI 0009 (no neighbour at all)
PARKS = {'US-FL': ['US-0001', 'US-0002'], 'US-GA': ['US-0003', 'US-0004'], 'US-AL': ['US-0005'], 'US-HI': ['US-0009']}


def spot(a, b, kind='area', x=0):
    return {'refs': sorted([a, b]), 'kind': kind, 'id': f"{'+'.join(sorted([a, b]))}@{kind}@{x}", 'center': [30, -85], 'status': 'candidate', 'passes': [1, 1, 1]}


def sfile(st, spots, passes=('pass1', 'pass2', 'pass3', 'pass5'), day='2026-11-12', **kw):
    return {'st': st, 'about': 'x', 'ids': {}, 'spots': spots, **{p: day for p in passes}, **kw}


SAVED = {'US-FL': sfile('US-FL', [spot('US-0001', 'US-0002'), spot('US-0001', 'US-0003')], day='2026-11-10'),
         'US-GA': sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0004', 'US-0005')], day='2026-11-10'),
         'US-AL': sfile('US-AL', [spot('US-0005', 'US-0005', 'line')], day='2026-11-10'),
         'US-HI': sfile('US-HI', [spot('US-0009', 'US-0009', 'line')], day='2026-11-10')}
STUB = "def rules_hash(kind, root=None):\n    return open(__file__[:-len('kpc_key_freeze.py')] + 'RULES').read().strip()\n"


def setup(t, held=('US-FL', 'US-GA', 'US-AL', 'US-HI')):
    """-> (origin, kpcdata clone, links, work). Saved files are held in the waiting room (data/waiting/in/data/fers)."""
    t = pathlib.Path(t); origin, kd, lk, work = t / 'origin.git', t / 'kpcdata', t / 'links', t / 'work/data/fers'
    subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', str(origin)], check=True)
    subprocess.run(['git', 'clone', '-q', str(origin), str(kd)], check=True, capture_output=True)
    git(kd, 'checkout', '-q', '-b', 'main')
    for st, refs in PARKS.items(): w(kd / f'data/parkinfo/{st}.json', {'parks': {r: [f'park {r}', 'u', 't', 'a', 'b', 30.0, -85.0, 99] for r in refs}})
    for st in held: w(kd / f'data/waiting/in/data/fers/{st}.json', SAVED[st])
    for st in SAVED: w(kd / f'data/fers/{st}.json', sfile(st, [], day='2026-11-01'))
    git(kd, 'add', '-A'); git(kd, 'commit', '-qm', 'base'); git(kd, 'push', '-q', 'origin', 'main')
    w(lk / '.github/scripts/kpc_key_freeze.py', STUB); w(lk / '.github/scripts/RULES', 'cef323de4c9a')
    w(lk / '.github/key-rules-version.json', {'fers': 1})
    for st, refs in PARKS.items(): w(lk / f'data/us-key/{st}.json', {'parks': {r: {'m': [[1, 'x']], 'read': '2026-11-01'} for r in refs}})
    work.mkdir(parents=True)
    return origin, kd, lk, work


def pick(kd, lk, work, states, **env):
    import io, contextlib
    e = dict(ENV0, STATES=states, KPCDATA=str(kd), LINKS=str(lk), WORK=str(work), RUNNER_TEMP=str(work.parent), TODAY='2026-11-12', **env)
    (work.parent / 'kpc-fers-red.txt').unlink(missing_ok=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): c, rows = F.pick(e, buf)
    return c, rows, buf.getvalue()


def blob(kd, rel):
    p = pathlib.Path(kd) / rel
    return p.read_bytes() if p.exists() else None


# ================= 1 one failed / short state
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    before = {st: blob(kd, f'data/waiting/in/data/fers/{st}.json') for st in SAVED}
    live_before = {st: blob(kd, f'data/fers/{st}.json') for st in SAVED}
    w(work / 'US-FL.json', sfile('US-FL', [spot('US-0001', 'US-0002')], passes=('pass1',), incomplete='pass 1 stopped for time'))   # short
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0004', 'US-0005')]))
    w(work / 'US-AL.json', sfile('US-AL', [spot('US-0005', 'US-0005', 'line')]))
    c, rows, out = pick(kd, lk, work, 'US-FL US-GA US-AL US-HI')
    check(c == 0, f'one short state: the job still saves the others (exit {c})')
    check(rows['US-FL']['verdict'] == 'failed' and 'short' in rows['US-FL']['why'], f"the short state is failed / short ({rows['US-FL']['verdict']}: {rows['US-FL']['why'][:60]})")
    check(rows['US-HI']['verdict'] == 'not-built', 'a state the job made no file for is not-built (kept)')
    check(blob(kd, 'data/fers/US-FL.json') == live_before['US-FL'] and blob(kd, 'data/fers/US-HI.json') == live_before['US-HI'],
          'the failed and the not-built state: nothing copied, so the waiting-room divert holds nothing new for them')
    check(all(blob(kd, f'data/waiting/in/data/fers/{st}.json') == before[st] for st in SAVED), 'every previously SAVED (held) file is byte for byte as before (pick never writes the waiting room)')
    check(json.loads(blob(kd, 'data/fers/US-GA.json'))['pass5'] == '2026-11-12' and json.loads(blob(kd, 'data/fers/US-AL.json'))['pass5'] == '2026-11-12', 'the green states GA and AL are copied for the save')
    st_ = git(kd, 'status', '--porcelain', '-uall', '--', 'data/fers').stdout
    check('US-FL' not in st_ and 'US-HI' not in st_ and 'US-GA.json' in st_ and 'stamps/US-GA.json' in st_, 'git sees only the green states (and their stamps) as changed')
    red = (work.parent / 'kpc-fers-red.txt').read_text()
    check('US-FL failed' in red and 'US-HI not-built' in red and 'US-GA' not in red, 'the red list names exactly the kept states (the job turns red after its save)')
    check('| US-FL | no | failed | kept from main | - |' in out and '| US-GA | yes | built | saved |' in out, 'the run table: state | built? | verdict | saved or kept from main | hash stamped | why')
# break save: only states that finished every pass today
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004')]))
    w(work / 'US-AL.json', sfile('US-AL', [spot('US-0005', 'US-0005', 'line')], passes=('pass1', 'pass2')))
    c, rows, out = pick(kd, lk, work, 'US-GA US-AL', ONLY_FINISHED='1')
    check(rows['US-GA']['verdict'] == 'built' and rows['US-AL']['verdict'] == 'not-built', 'after a break (ONLY_FINISHED): only a state that finished every pass today is saved')
# stale base: another run saved GA since this job started -> never overwritten
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    other = pathlib.Path(t) / 'other'; subprocess.run(['git', 'clone', '-q', str(o), str(other)], check=True, capture_output=True)
    w(other / 'data/waiting/in/data/fers/US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004')], day='2026-11-12'))
    git(other, 'commit', '-qam', 'another run saved GA'); git(other, 'push', '-q', 'origin', 'HEAD:main')
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0004', 'US-0005')]))
    w(work / 'US-AL.json', sfile('US-AL', [spot('US-0005', 'US-0005', 'line')]))
    c, rows, out = pick(kd, lk, work, 'US-GA US-AL')
    check(rows['US-GA']['verdict'] == 'failed' and 'stale base' in rows['US-GA']['why'] and rows['US-AL']['verdict'] == 'built',
          'a state another run saved since this job started is kept (stale base, red); the other state still saves')
    check(blob(kd, 'data/fers/US-GA.json') == json.dumps(sfile('US-GA', [], day='2026-11-01'), sort_keys=True).encode(), 'the stale state is not copied (the other run\'s file stands)')

# ================= 2 per-state hash: only the state and its pair neighbours move
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    nb = F.neighbours(kd)
    check(nb['US-FL'] == {'US-GA'} and nb['US-GA'] == {'US-FL', 'US-AL'} and nb['US-AL'] == {'US-GA'} and nb['US-HI'] == set(),
          f'pair neighbours come from the saved results ({ {k: sorted(v) for k, v in nb.items()} })')
    H0 = {st: F.state_hash(st, lk, kd)[0] for st in SAVED}
    w(lk / 'data/us-key/US-FL.json', {'parks': {r: {'m': [[2, 'y']], 'read': '2026-11-12'} for r in PARKS['US-FL']}})
    H1 = {st: F.state_hash(st, lk, kd)[0] for st in SAVED}
    moved = sorted(st for st in SAVED if H0[st] != H1[st])
    check(moved == ['US-FL', 'US-GA'], f'a key change in FL moves FL and GA (they share a pair), not AL (no FL pair) or HI ({moved})')
    w(lk / 'data/us-key/US-FL.json', {'parks': {r: {'m': [[2, 'y']], 'read': '2026-11-30'} for r in PARKS['US-FL']}})
    check({st: F.state_hash(st, lk, kd)[0] for st in SAVED} == H1, "a key file re-dated only (the per-park 'read' date) moves no state")
    w(lk / '.github/scripts/RULES', 'aaaaaaaaaaaa')
    H2 = {st: F.state_hash(st, lk, kd)[0] for st in SAVED}
    check(all(H2[st] != H1[st] for st in SAVED), 'a shared 2-fer code change (the fers rules hash) moves every state: full rebuild')
    w(lk / '.github/scripts/RULES', 'cef323de4c9a')
    # stamp the states as built on today's inputs, then plan
    for st in SAVED:
        h, parts, used = F.state_hash(st, lk, kd)
        rel, sp, sd = F.saved_copy(kd, st)
        w(F.stamp_path(kd, st), {'st': st, 'area_hash': h, 'area_parts': {k: v[:12] for k, v in parts.items()}, 'out_sha': F.sha(sp.read_bytes()), 'rules': 'cef323de4c9a'})
    import io
    b_off, rows_off = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED)), io.StringIO())
    b_on, rows_on = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse'), io.StringIO())
    check(sorted(b_off) == sorted(SAVED) and all(r['would'] == 'reuse' for r in rows_off), 'reuse is OFF by default: every state is rebuilt; the table only says what WOULD be reused (shadow)')
    check(b_on == [], 'with KPC_AREA_HASH=reuse and nothing changed: nothing to build')
    w(lk / 'data/us-key/US-FL.json', {'parks': {r: {'m': [[3, 'z']]} for r in PARKS['US-FL']}})
    b_on, rows_on = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse'), io.StringIO())
    check(sorted(b_on) == ['US-FL', 'US-GA'], f'with reuse on, a FL key change rebuilds FL + GA only ({b_on})')
    b_full, _ = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse', FORCE='full'), io.StringIO())
    check(sorted(b_full) == sorted(SAVED), 'force full rebuild (FORCE=full) still rebuilds every state')
    # a shared-code change: rebuild every state unless the key half's D4 reader says the proof is valid
    w(lk / 'data/us-key/US-FL.json', {'parks': {r: {'m': [[2, 'y']]} for r in PARKS['US-FL']}})
    for st in SAVED:
        h, parts, used = F.state_hash(st, lk, kd); rel, sp, sd = F.saved_copy(kd, st)
        w(F.stamp_path(kd, st), {'st': st, 'area_hash': h, 'area_parts': {k: v[:12] for k, v in parts.items()}, 'out_sha': F.sha(sp.read_bytes()), 'rules': 'cef323de4c9a'})
    w(lk / '.github/scripts/RULES', 'bbbbbbbbbbbb')
    b_np, _ = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse'), io.StringIO())
    check(sorted(b_np) == sorted(SAVED), 'shared code moved, no proof reader / no proof: every state rebuilds (fail closed)')
    w(lk / '.github/scripts/kpc_area_hash.py', "def code_hash(repo, kind): return 'bbbbbbbbbbbb'\ndef proof_valid(repo, kind, frm, to): return (frm == 'cef323de4c9a' and to == 'bbbbbbbbbbbb', 'P1')\n")
    b_pv, rows_pv = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse'), io.StringIO())
    check(b_pv == [] and all('proven no result change (P1)' in r['why'] for r in rows_pv), "only shared code moved + a VALID proof from the key half's reader: reused (D4)")
    w(lk / '.github/scripts/kpc_area_hash.py', "def code_hash(repo, kind): return 'bbbbbbbbbbbb'\ndef proof_valid(repo, kind, frm, to): return (False, 'stale')\n")
    b_sp, _ = F.plan(dict(ENV0, LINKS=str(lk), KPCDATA=str(kd), STATES=' '.join(SAVED), KPC_AREA_HASH='reuse'), io.StringIO())
    check(sorted(b_sp) == sorted(SAVED), 'a stale / failed proof: every state rebuilds')
    (lk / '.github/scripts/kpc_area_hash.py').unlink(); w(lk / '.github/scripts/RULES', 'cef323de4c9a')
    # byte-identical: an unchanged state rebuilt by a deterministic builder == its saved bytes; pick then changes nothing for it
    def stub_build(st):   # stands in for kpc_fers.py (deterministic: same inputs -> same bytes)
        return F.saved_copy(kd, st)[1].read_bytes()
    al_saved = F.saved_copy(kd, 'US-AL')[1].read_bytes()
    (work / 'US-AL.json').write_bytes(stub_build('US-AL'))
    check((work / 'US-AL.json').read_bytes() == al_saved, 'an unchanged state: full-rebuild output == the reused saved file, byte for byte (stub builder)')
    c, rows, out = pick(kd, lk, work, 'US-AL')
    check(rows['US-AL']['verdict'] in ('built', 'reused') and blob(kd, 'data/waiting/in/data/fers/US-AL.json') == al_saved, 'saving it again leaves the held copy byte for byte the same')
# a state with no saved result at all pairs with every state of its key (fail closed)
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t, held=('US-FL', 'US-GA'))
    for st in SAVED: (kd / f'data/fers/{st}.json').unlink()
    git(kd, 'commit', '-qam', 'no live');
    h, parts, used = F.state_hash('US-HI', lk, kd)
    check(set(used) == {'US-FL', 'US-GA', 'US-AL'}, f'a state with no saved 2-fer result counts every state of its key as a neighbour (fail closed) ({used})')

# ================= 3 a broken line does not touch other lines; the gate is per state; a cancel saves nothing
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    before = {st: blob(kd, f'data/waiting/in/data/fers/{st}.json') for st in SAVED}
    # southeast fetcher broke: no checker, no pick for southeast. Another line (here: AL alone) saves only its own state.
    w(work / 'US-AL.json', sfile('US-AL', [spot('US-0005', 'US-0005', 'line')]))
    w(work / 'US-FL.json', sfile('US-FL', []))   # a neighbour file the builder wrote in the runner: never saved by this line
    c, rows, out = pick(kd, lk, work, 'US-AL')
    st_ = git(kd, 'status', '--porcelain').stdout
    check(set(rows) == {'US-AL'} and 'US-FL' not in st_ and 'US-GA' not in st_, "a line saves only its own states; a neighbour's file in the runner is never copied")
    check(all(blob(kd, f'data/waiting/in/data/fers/{st}.json') == before[st] for st in SAVED), "the broken line's states and every held file are untouched")
# gate: one dirty, unchanged state no longer dirties a clean line
with tempfile.TemporaryDirectory() as t:
    D = pathlib.Path(t)
    w(D / 'data/waiting/in/data/fers/US-AK.json', {'v': 1}); w(D / 'data/waiting/in/data/fers/US-IA.json', {'v': 1})
    clean = {'preline': {'verdict': 'GO'}, 'stale_inputs': [], 'touch_held': []}
    dirty = {'preline': {'verdict': 'HOLD'}, 'stale_inputs': ['the last pre-line check (pacific) said HOLD'], 'touch_held': []}
    check(CG.postline_clean({'areas': {'US-AK': dirty, 'US-IA': clean}})[1] is False, 'old rule kept for a first check: any dirty state = not clean')
    st0 = CG.held_states(D)
    check(CG.postline_clean({'areas': {'US-AK': dirty, 'US-IA': clean}}, only={'US-IA'})[1] is True, 'per state: a check that judges only the changed states (IA) is clean although AK (unchanged) is dirty')
    check(CG.postline_clean({'areas': {'US-AK': dirty, 'US-IA': clean}}, only={'US-AK', 'US-IA'})[1] is False, 'a dirty state whose own held file changed still resets the streak')
    check(CG.postline_clean({'areas': {'US-AK': dirty}}, only=set())[0] is False, 'a check where nothing changed is not counted either way')
    w(D / 'data/waiting/in/data/fers/US-IA.json', {'v': 2})
    check({a for a, h in CG.held_states(D).items() if st0.get(a) != h} == {'US-IA'}, 'held_states tells which states changed (IA), per state')
# workflow conditions: a cancelled run saves nothing (evaluated with GitHub's rules)
import yaml


def ev(expr, ctx):
    e = expr.strip()
    if e.startswith('${{'): e = e[3:-2]
    status = ('success()' in e or 'failure()' in e or 'cancelled()' in e or 'always()' in e)
    for f, v in (('success()', ctx['_success']), ('failure()', ctx['_failure']), ('cancelled()', ctx['_cancelled']), ('always()', True)): e = e.replace(f, repr(v))
    e = re.sub(r"\b((?:steps|needs|inputs|matrix|vars)\.[A-Za-z0-9_.\-]+)", lambda m: repr(ctx.get(m.group(1), '')), e)
    e = e.replace('&&', ' and ').replace('||', ' or ').replace('!=', ' __NE__ ').replace('!', ' not ').replace(' __NE__ ', ' != ')
    r = bool(eval(e, {}, {}))   # noqa: S307 (test only, our own workflow text)
    return r if status else (r and ctx['_success'])


Y = {n: yaml.safe_load((HERE / f'.github/workflows/{n}').read_text()) for n in ('kpc-fers.yml', 'kpc-fers-line.yml', 'kpc-fers-lines.yml', 'kpc-fers-chain.yml')}
fs = {s.get('id') or s.get('name'): s for s in Y['kpc-fers.yml']['jobs']['fers']['steps']}
save = fs['kept_green_5']; brk = next(s for k, s in fs.items() if 'run broke' in str(k))
for name, cx in (('cancelled', dict(_success=False, _failure=False, _cancelled=True)), ('failed', dict(_success=False, _failure=True, _cancelled=False))):
    for look in ('success', 'failure', 'cancelled'):
        c_ = dict(cx, **{'steps.wait.outputs.wait': '0', 'steps.kept_green_3.outcome': look, 'matrix.r.region': 'na'})
        if name == 'cancelled':
            check(not ev(save['if'], c_) and not ev(brk['if'], c_), f'kpc-fers.yml: a cancelled run (Look {look}) runs neither Save nor the break save')
chk = {s.get('name'): s for s in Y['kpc-fers-line.yml']['jobs']['checker']['steps']}
sv = next(s for n, s in chk.items() if str(n).startswith('Save'))
check(not ev(sv['if'], {'_success': False, '_failure': False, '_cancelled': True, 'steps.kept_green_10.outcome': 'success', 'steps.kept_green_10.outputs.verdict': 'written'}),
      'kpc-fers-line.yml checker Save: never on a cancelled run (the Nov 12 condition is kept)')
check('kpc_fers_states.py pick' in sv['run'] and 'kpc_fers_states.py pick' in save['run'] and 'kpc_fers_states.py pick' in brk['run'], 'all three 2-fer saves go through the per-state pick')
check(save['run'].index('kpc_fers_states.py pick') < save['run'].index('kpc_waiting_room.py divert') < save['run'].index('kpc_push_data.sh'),
      'kpc-fers.yml Save: per-state pick, then the waiting-room divert, then the one push')
check(sv['run'].index('kpc_fers_states.py pick') < sv['run'].index('kpc_waiting_room.py divert') < sv['run'].index('kpc_push_data.sh') < sv['run'].index('kpc-fers-red.txt'),
      'line Save: pick, divert, push, and only then red for a kept state (it blocks nobody)')
check('rm -q --cached --ignore-unmatch "data/fers/reuse-p' not in sv['run'] and 'rm -f kpcdata/data/fers/reuse-p' not in sv['run'], "the line no longer deletes the bot's committed pair answers (reuse-p*-<tag>)")
check(Y['kpc-fers-lines.yml']['jobs']['line'].get('strategy', {}).get('fail-fast') is False and Y['kpc-fers-chain.yml']['jobs']['line']['strategy']['fail-fast'] is False,
      'lines run fail-fast: false (one broken line does not stop the others)')

# ================= 4 one map
bot = json.load(open(HERE / '.github/fers-areas.json'))['areas']
chain_us_ca = {t: v for t, v in P.R.items() if P.kind_of(v) != 'world-key'}
check(chain_us_ca == bot, 'the chain plans exactly the bot areas (same tags, same state sets)')
check(sorted(x for v in chain_us_ca.values() for x in v.split()) == sorted(x for v in bot.values() for x in v.split()), 'every chain line writes the same state set as the bot (no state cut two ways)')
with tempfile.TemporaryDirectory() as t:   # a stomp under another cut is impossible: a line for a set that is not a bot area is refused by pick? no: pick saves only
    o, kd, lk, work = setup(t)   # its own states, and the stale-base check keeps any state another run saved meanwhile (shown in 1)
    check(F.areas(HERE) == bot and F.area_of_state(HERE)['US-FL'] == 'southeast', 'kpc_fers_states.areas() is the one list')
lines_tags = [l.strip() for l in Y['kpc-fers-lines.yml'][True]['workflow_dispatch']['inputs']['areas']['default'].split(';')]
check(sorted(lines_tags) == sorted(bot), f'kpc-fers-lines.yml default queue = every area of fers-areas.json ({lines_tags})')
A = mod('kpc_fers_areas', HERE / '.github/scripts/kpc_fers_areas.py')
os.environ.pop('FULL', None)
one = A.plan('US-FL')
check(len(one) == 1 and one[0]['states'] == 'US-FL' and one[0]['tag'] == 'fl' and one[0]['seed'] == 'southeast' and one[0]['full'] == '', 'kpc-fers.yml region=US-FL: one job for Florida alone (tag fl, seeded from southeast, not a round-robin full rebuild)')

# a finished kpc-fers.yml pass counts for the chain only on the same per-state hash
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0004', 'US-0005')], passes=('pass1',)))
    w(work / 'US-AL.json', sfile('US-AL', [spot('US-0005', 'US-0005', 'line')], passes=('pass1',)))
    pick(kd, lk, work, 'US-GA US-AL')
    for st in ('US-GA', 'US-AL'):   # the waiting-room divert moves the new file into data/waiting/in (as the real Save does)
        shutil.copy(kd / f'data/fers/{st}.json', kd / f'data/waiting/in/data/fers/{st}.json')
    check(P.bot_passes(kd, lk, ['US-GA', 'US-AL']) == 1, 'bot pass 1 done on the same per-state hash: the chain line starts at pass 2 (skip_pass1)')
    w(lk / 'data/us-key/US-AL.json', {'parks': {'US-0005': {'m': [[9, 'q']]}}})
    check(P.bot_passes(kd, lk, ['US-GA', 'US-AL']) == 0, 'a key file the chain measures on differs from the one the bot used: pass 1 runs again (0)')
    check(P.bot_passes(kd, lk, ['US-GA', 'US-FL']) == 0, 'a state with no stamp: 0 (every pass runs)')

# ================= 5 workflows parse, no new cron, honest stamps, hashes
BASE = '6ceb67d70b7b9435f4fbd9369e7cd9673554c988'
for wf in sorted((HERE / '.github/workflows').glob('kpc-fers*.yml')):
    y = yaml.safe_load(wf.read_text())
    old = subprocess.run(['git', '-C', str(HERE), 'show', f'{BASE}:.github/workflows/{wf.name}'], capture_output=True, text=True)
    if old.returncode: print(f'INFO {BASE} not in this clone: trigger compare skipped for {wf.name}'); continue
    o_ = yaml.safe_load(old.stdout)[True]; n_ = y[True]
    crons = lambda x: [c.get('cron') for c in (x.get('schedule') or [])] if isinstance(x, dict) else []
    ins = lambda x, k: set(((x.get(k) or {}).get('inputs') or {})) if isinstance(x, dict) else set()
    check(sorted(n_) == sorted(o_) and crons(n_) == crons(o_) and all(ins(n_, k) >= ins(o_, k) and ins(n_, k) - ins(o_, k) <= {'skip_pass1'} for k in ('workflow_dispatch', 'workflow_call')),
          f'{wf.name}: parses; same triggers, same crons (no new cron), inputs unchanged except the new skip_pass1')
with tempfile.TemporaryDirectory() as t:
    o, kd, lk, work = setup(t)
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0004', 'US-0005')]))
    w(work / 'US-FL.json', sfile('US-FL', [], passes=('pass1',), incomplete='x'))
    c, rows, out = pick(kd, lk, work, 'US-FL US-GA')
    stamps = sorted(p.stem for p in (kd / 'data/fers/stamps').glob('*.json'))
    g = json.loads((kd / 'data/fers/stamps/US-GA.json').read_text())
    check(stamps == ['US-GA'], f'only the rebuilt state is stamped ({stamps}); no region-wide claim')
    check(g['area_hash'] == rows['US-GA']['area_hash'] and g['out_sha'] == F.sha(blob(kd, 'data/fers/US-GA.json')) and g['rules'] == 'cef323de4c9a' and g['why'] == 'built'
          and set(g) >= {'rules', 'area_hash', 'area_parts', 'out_sha', 'built_sha'}, 'the stamp carries the shared-scheme fields (rules, area_hash, area_parts, out_sha, built_sha) and matches the saved bytes')
LK = os.environ.get('LINKS') or str(HERE.parent / 'links')
if (pathlib.Path(LK) / '.github/scripts/kpc_key_freeze.py').exists():
    check(F.fers_rules(LK) == 'cef323de4c9a', f'the fers rules hash on KPC-Links is unchanged by this patch ({F.fers_rules(LK)})')
else: print('INFO no KPC-Links clone: fers rules hash not recomputed')

# ================= 6 no cross-border pair written by two states
with tempfile.TemporaryDirectory() as t:   # one job with FL and GA: the builder filed the FL-GA pair in both files (one-state style)
    o, kd, lk, work = setup(t)
    w(work / 'US-FL.json', sfile('US-FL', [spot('US-0001', 'US-0002'), spot('US-0001', 'US-0003')]))
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0001', 'US-0003'), spot('US-0004', 'US-0005')]))
    c, rows, out = pick(kd, lk, work, 'US-FL US-GA')
    fl = {F.pair_key(s) for s in json.loads(blob(kd, 'data/fers/US-FL.json'))['spots']}; ga = {F.pair_key(s) for s in json.loads(blob(kd, 'data/fers/US-GA.json'))['spots']}
    check(c == 0 and not (fl & ga) and 'US-0001+US-0003@area' in fl, f'the FL-GA pair is written once, by its owner (US-FL, alphabetically first) ({sorted(fl & ga)})')
with tempfile.TemporaryDirectory() as t:   # GA alone; FL's saved file already holds the pair: GA leaves it to FL
    o, kd, lk, work = setup(t)
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0001', 'US-0003')]))
    c, rows, out = pick(kd, lk, work, 'US-GA')
    ga = {F.pair_key(s) for s in json.loads(blob(kd, 'data/fers/US-GA.json'))['spots']}
    check('US-0001+US-0003@area' not in ga and rows['US-GA'].get('dropped') == 1, 'GA alone: a pair owned by FL that FL already holds is left to FL')
with tempfile.TemporaryDirectory() as t:   # GA alone; FL holds no copy: GA keeps it (a row is never lost)
    o, kd, lk, work = setup(t)
    w(kd / 'data/waiting/in/data/fers/US-FL.json', sfile('US-FL', [spot('US-0001', 'US-0002')])); git(kd, 'commit', '-qam', 'fl'); git(kd, 'push', '-q', 'origin', 'main')
    w(work / 'US-GA.json', sfile('US-GA', [spot('US-0003', 'US-0004'), spot('US-0001', 'US-0003')]))
    c, rows, out = pick(kd, lk, work, 'US-GA')
    ga = {F.pair_key(s) for s in json.loads(blob(kd, 'data/fers/US-GA.json'))['spots']}
    check('US-0001+US-0003@area' in ga, 'GA alone, FL has no copy of the pair: GA keeps it (never lost)')
with tempfile.TemporaryDirectory() as t:   # owner rule off + both files of one job hold the pair: join-refused, nothing saved
    o, kd, lk, work = setup(t)
    w(work / 'US-FL.json', sfile('US-FL', [spot('US-0001', 'US-0003')])); w(work / 'US-GA.json', sfile('US-GA', [spot('US-0001', 'US-0003')]))
    live = {st: blob(kd, f'data/fers/{st}.json') for st in ('US-FL', 'US-GA')}
    c, rows, out = pick(kd, lk, work, 'US-FL US-GA', KPC_FERS_PAIR_OWNER='off')
    check(c == 2 and all(rows[s]['verdict'] == 'join-refused' for s in ('US-FL', 'US-GA')) and all(blob(kd, f'data/fers/{s}.json') == live[s] for s in live)
          and not (kd / 'data/fers/stamps').exists(), 'a double write inside one job fails closed: join-refused, nothing saved, nothing stamped')
CA = {'CA-0005+CA-0045@area': ['CA-AB', 'CA-BC']}
check(F.owner({'refs': ['US-0010', 'CA-0001']}, {'US-0010': 'US-ME', 'CA-0001': 'CA-NB'}, 'US-ME') == 'CA-NB' and F.owner({'refs': ['CA-0005', 'CA-0045']}, {'CA-0005': 'CA-BC', 'CA-0045': 'CA-AB'}, 'CA-BC') == 'CA-AB',
      'owner rule: the alphabetically first state of the pair (CA-NB + US-ME -> CA-NB; CA-AB + CA-BC -> CA-AB)')
AT = frozenset({'US-GA', 'US-NC', 'US-TN', 'US-VA', 'US-WV', 'US-ME'})
check(F.owner({'refs': ['US-4556', 'US-0003']}, {'US-4556': AT, 'US-0003': frozenset({'US-GA'})}, 'US-GA') == 'US-GA' and F.owner({'refs': ['US-4556', 'US-4560']}, {'US-4556': AT, 'US-4560': AT}, 'US-TN') == 'US-TN',
      'a park listed in several states (the Appalachian Trail) does not decide the owner: the one-state park does; two multi-state parks stay in the file')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
