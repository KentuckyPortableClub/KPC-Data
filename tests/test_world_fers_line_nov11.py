#!/usr/bin/env python3
"""World 2-fer line wiring, TEST ONLY (owner rule, 2026-11-11). Offline: fake files in temp folders, no network, nothing is started.
  * the line workflow's BUILD_KIND is world-key for W-* (and still us-key / ca-key), the same as kind_of() in the chain planner
  * the key-copy loop (run as real bash, taken from the workflow) keeps the NEW key of BUILD_KIND and copies the live others, world included
  * the planner skips world while no country is on the ready list; with a fixture ready file it plans the world areas, but only when
    the US and Canada 2-fers are OK on the current rules (READY line, same key files, report fers_rules == current hash); unknown = wait
  * the chain's area list has ONE home (the planner); fers-areas.json (older bot) holds no W-* area; US / CA are planned before world
  * the line's world path never asks a saved-copy-only host (the host check refuses it; see also KPC-Links tests)"""
import importlib.util, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def links_clone():
    for c in (os.environ.get('LINKS'), HERE.parent / 'links', HERE.parent / 'kpc-links'):
        if c and (pathlib.Path(c) / '.github/scripts/kpc_fers_ready.py').exists(): return pathlib.Path(c)
    return None


REAL = links_clone()
spec = importlib.util.spec_from_file_location('kpc_fers_chain_plan', HERE / '.github/scripts/kpc_fers_chain_plan.py')
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
Y = (HERE / '.github/workflows/kpc-fers-line.yml').read_text(encoding='utf-8')

# ---- 1 BUILD_KIND: evaluate the workflow's own expression
m = re.search(r"^  BUILD_KIND: \$\{\{ (.*?) \}\}", Y, re.M)
expr = m.group(1)


def gh_eval(expr, states):
    """the tiny GitHub expression subset used here: startsWith(inputs.states, 'X') && 'a' || ... || 'z'"""
    for part in expr.split(' || '):
        mm = re.fullmatch(r"startsWith\(inputs\.states, '([^']+)'\) && '([^']+)'", part.strip())
        if mm:
            if states.startswith(mm.group(1)): return mm.group(2)
            continue
        mm = re.fullmatch(r"'([^']+)'", part.strip())
        if mm: return mm.group(1)
        raise ValueError(part)


cases = {'US-OH': 'us-key', 'US-KY': 'us-key', 'CA-ON': 'ca-key', 'CA-BC CA-YT': 'ca-key', 'W-GB': 'world-key', 'W-AU W-JP': 'world-key', 'W-GB W-IE W-FR': 'world-key'}
check(all(gh_eval(expr, st) == k for st, k in cases.items()), 'BUILD_KIND in kpc-fers-line.yml: W-* = world-key, CA-* = ca-key, else us-key')
check(all(P.kind_of(st) == k for st, k in cases.items()), 'kind_of() in the chain planner gives the same answer for the same states')
check(all(P.KIND_OF(sts) == 'world-key' for t, sts in P.R.items() if t.startswith('world')), 'every planner world area is a world-key area')
try:
    import yaml; yaml.safe_load(Y); check(True, 'kpc-fers-line.yml parses as YAML')
except ImportError: check(True, 'SKIP yaml not installed')

# ---- 2 the key-copy loop, as real bash, from the workflow text
loops = {l.strip() for l in Y.split('\n') if l.strip().startswith('for k in us-key ca-key world-key;')}
check(len(loops) == 1 and Y.count('for k in us-key ca-key world-key;') == 3, 'the key-copy loop is the same line in all three stages')
loop = loops.pop().replace('kpcdata/data/', 'kpcdata/data/')
for build, src, expect_copied in (('world-key', 'build', {'us-key', 'ca-key'}), ('us-key', 'build', {'ca-key', 'world-key'}), ('ca-key', 'build', {'us-key', 'world-key'}),
                                  ('world-key', 'live', {'us-key', 'ca-key', 'world-key'})):
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        for k in ('us-key', 'ca-key', 'world-key'):
            (t / 'kpcdata/data' / k).mkdir(parents=True); (t / 'kpcdata/data' / k / 'X.json').write_text('{"live":1}')
        subprocess.run(['bash', '-e', '-c', loop], cwd=t, env=dict(os.environ, KEY_SOURCE=src, BUILD_KIND=build), check=True)
        got = {k for k in ('us-key', 'ca-key', 'world-key') if (t / 'data' / k / 'X.json').exists()}
        check(got == expect_copied, f'key copy: KEY_SOURCE={src} BUILD_KIND={build}: live copies of {sorted(got)} (the build key is kept, not overwritten)')
check('SAVED_DIR=cache/world' in Y and '-D "$SAVED_DIR"' in Y, "checker stage: a world country's saved copy goes to cache/world")

# ---- 3 one list of areas
fa = json.load(open(HERE / '.github/fers-areas.json'))['areas']
check(not any(s.startswith('W-') for v in fa.values() for s in v.split()), 'fers-areas.json (older bot) holds no W-* area: the chain planner is the one home of the world areas')
wsts = [s for t, v in P.R.items() if t.startswith('world') for s in v.split()]
check(len(wsts) == len(set(wsts)) and wsts and all(s.startswith('W-') for s in wsts), 'no country is in two world areas')
check(not any(kind_ == 'world-key' for _, v in P.R.items() for kind_ in [P.kind_of(v)] if not v.startswith('W-')), 'a world-key area holds only W-* codes')
check(list(P.KEY_ORDER) == ['us-key', 'ca-key', 'world-key'], 'planning order: US, then Canada, then world')
if REAL:
    have = {f.stem for f in (REAL / 'data/world-key').glob('[A-Z][A-Z].json')}
    check({s[2:] for s in wsts} <= have, 'every world area country has a file in the world key')

# ---- 4 the planner with fixtures
STUB = 'def rules_hash(kind, root=None): return "cur-" + kind\ndef verdict(*a, **k): return None\ndef graded_no(*a, **k): return None\n'
w = lambda p, d: (pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True), pathlib.Path(p).write_text(d if isinstance(d, str) else json.dumps(d)))
READY_US_CA = {'US-*': {'match': r'^US-[A-Z]{2}$', 'ownership': {'source': 'PAD-US'}, 'management': {'source': 'PAD-US'}},
               'CA-*': {'match': r'^CA-[A-Z]{2}$', 'ownership': {'source': 'CPCAD'}, 'management': {'source': 'CPCAD'}}}
READY_W = {'W-*': {'match': r'^W-[A-Z]{2}$', 'ownership': {'source': 'fixture'}, 'management': {'source': 'fixture'}}}
NOW = 1794300000
STAMP = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(NOW))
LATER = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(NOW + 7200))
green = lambda *sts: {s: {'parks': 1, 'rules': 'cur-us-key'} for s in sts}


MINI_READY = '''import json, pathlib, re
def load_ready(root=None): return json.load(open(pathlib.Path(root) / '.github' / 'fers-ready-areas.json'))
def area_ready(area, ready):
    for ent in (ready.get('areas') or {}).values():
        if (ent.get('ownership') or {}).get('source') and (ent.get('management') or {}).get('source') and re.fullmatch(ent.get('match') or '(?!)', str(area).upper()): return True
    return False
'''


def fixture(t, ready, world_in_ready=False):
    D, Lk = pathlib.Path(t) / 'data', pathlib.Path(t) / 'links'
    w(Lk / '.github/scripts/kpc_key_freeze.py', STUB)
    # the real ready-list module when a KPC-Links clone is beside this one, else the stub of its two calls
    if REAL: shutil.copy(REAL / '.github/scripts/kpc_fers_ready.py', Lk / '.github/scripts/kpc_fers_ready.py')
    else: w(Lk / '.github/scripts/kpc_fers_ready.py', MINI_READY)   # no clone here: a 12-line copy of the two calls the planner makes
    w(Lk / '.github/fers-ready-areas.json', {'require': ['ownership', 'management'], 'areas': ready})
    allsts = {s for v in P.R.values() for s in v.split()}
    us = sorted(s[3:] for s in allsts if s.startswith('US-')); ca = sorted(s for s in allsts if s.startswith('CA-'))
    w(Lk / 'data/us-key/index.json', {'build': 'US-9', 'rules': 'cur-us-key', 'states': green(*us)})
    w(Lk / 'data/ca-key/index.json', {'build': 'CA-9', 'rules': 'cur-ca-key'})
    w(Lk / 'data/world-key/index.json', {'build': 'W-9', 'rules': 'cur-world-key'})
    for k, sh, b in (('us', 'us', 'US-9'), ('ca', 'ca', 'CA-9'), ('world', 'world', 'W-9')): w(Lk / f'data/status/key-check/last-{sh}.json', {'build': b})
    for k in ('us-key', 'ca-key', 'world-key'): w(D / f'data/{k}/index.json', {'build': {'us-key': 'US-9', 'ca-key': 'CA-9', 'world-key': 'W-9'}[k]})
    return D, Lk


def plan(D, Lk, gate='off', now=NOW):
    for m_ in ('kpc_key_freeze', 'kpc_fers_ready'): sys.modules.pop(m_, None)
    sys.path[:] = [p for p in sys.path if not p.endswith('/links/.github/scripts')]
    r, seen, notes = P.plan(str(D), str(Lk), gate, 20, now)
    w(D / 'data/status/fers-chain/seen.json', seen)
    return r, seen, notes


def finish_all(D, Lk, seen, tags, rules='cur-fers', stamp=LATER):
    """every area in tags has a READY line after its start and a report on the given rules hash"""
    for tg in tags:
        w(D / f'data/fers/line-{tg}.json', {'verdict': 'READY FOR CHAT 8', 'date': stamp}); w(D / f'data/fers/report-{tg}.json', {'fers_rules': rules})


# STUB rules_hash('fers') is 'cur-fers'
tags_us_ca = [t for t, v in P.R.items() if P.kind_of(v) != 'world-key']
world_tags = [t for t, v in P.R.items() if P.kind_of(v) == 'world-key']
if REAL: pass
with tempfile.TemporaryDirectory() as t:   # 4a world not ready: skipped, nothing starts for world, US / CA unaffected
    D, Lk = fixture(t, READY_US_CA)
    r, s, n = plan(D, Lk)
    check(not any(x['key'] == 'world-key' for x in r) and not (s.get('world-key') or {}).get('ran'), 'world not on the ready list: no world area is planned')
    check(any(x.startswith('world-key: not on KPC-Links') and 'worldwest' in x for x in n), 'the plan says plainly which world areas were skipped as not ready')
    check(r and all(x['key'] != 'world-key' for x in r), 'US / Canada areas are still planned as before')
with tempfile.TemporaryDirectory() as t:   # 4b real Links ready file (if a clone is here): world areas skipped
    if REAL:
        D, Lk = fixture(t, READY_US_CA); shutil.copy(REAL / '.github/fers-ready-areas.json', Lk / '.github/fers-ready-areas.json')
        r, s, n = plan(D, Lk)
        check(not any(x['key'] == 'world-key' for x in r), "with KPC-Links' real fers-ready-areas.json no world area is planned")
    else: print('SKIP no KPC-Links clone beside this repo (set LINKS=...)')
with tempfile.TemporaryDirectory() as t:   # 4c world ready but US / CA not OK (nothing finished): world waits, and says why
    D, Lk = fixture(t, {**READY_US_CA, **READY_W})
    r, s, n = plan(D, Lk)
    check(not any(x['key'] == 'world-key' for x in r), 'world ready but US / Canada lines have not finished: world waits')
    wt = (s.get('world-key') or {}).get('waiting') or {}
    check(all('waits for US and Canada 2-fers' in wt.get(tg, '') for tg in world_tags), f'every world area says it waits for US and Canada ({list(wt.items())[:1]})')
    check([x['key'] for x in r].count('us-key') + [x['key'] for x in r].count('ca-key') == len(r) and len(r) > 0, 'US / Canada areas were planned in that same run, world got none')
    # US / CA lines finish on the current rules -> OK -> world plans, most 20 at a time here
    finish_all(D, Lk, s, tags_us_ca)
    r2, s2, n2 = plan(D, Lk, now=NOW + 8 * 3600)
    check(sorted(x['tag'] for x in r2) == sorted(world_tags) and all(x['key'] == 'world-key' and x['states'].startswith('W-') for x in r2),
          f'US / Canada OK + world ready (fixture): worldwest / worldnorth / worldeast are planned ({[x["tag"] for x in r2]})')
    # a US area whose report is on OLD rules -> world waits
    seen_back = json.load(open(D / 'data/status/fers-chain/seen.json'))
    for variant, mut in (('report on old 2-fer rules', lambda: w(D / 'data/fers/report-southeast.json', {'fers_rules': 'old-hash'})),
                         ('report has no fers_rules', lambda: w(D / 'data/fers/report-southeast.json', {})),
                         ('line only PART READY', lambda: w(D / 'data/fers/line-canadaeast.json', {'verdict': 'PART READY FOR CHAT 8', 'date': LATER})),
                         ('line STOPPED', lambda: w(D / 'data/fers/line-pacific.json', {'verdict': 'STOPPED', 'date': LATER})),
                         ('line file missing', lambda: (D / 'data/fers/line-mountain.json').unlink()),
                         ('US key file changed after the line', lambda: w(Lk / 'data/us-key/US-OH.json', {'parks': {'US-1': {'m': [[1, 'x']]}}}))):
        finish_all(D, Lk, None, tags_us_ca)
        for x in (D / 'data/status/fers-chain/seen.json',): x.write_text(json.dumps(seen_back))
        mut()
        r3, s3, n3 = plan(D, Lk, now=NOW + 8 * 3600)
        check(not any(x['key'] == 'world-key' for x in r3), f'world waits when US / Canada are not OK: {variant}')
        if 'US key file changed' in variant: (Lk / 'data/us-key/US-OH.json').unlink()
with tempfile.TemporaryDirectory() as t:   # 4d no rules hash known: unknown = wait
    D, Lk = fixture(t, {**READY_US_CA, **READY_W}); w(Lk / '.github/scripts/kpc_key_freeze.py', STUB.replace('return "cur-" + kind', 'raise RuntimeError("no") if kind == "fers" else "cur-" + kind') if False else STUB.replace('def rules_hash(kind, root=None): return "cur-" + kind', 'def rules_hash(kind, root=None):\n    if kind == "fers": raise RuntimeError("no")\n    return "cur-" + kind'))
    r, s, n = plan(D, Lk); finish_all(D, Lk, s, tags_us_ca, rules='')
    r2, s2, _ = plan(D, Lk, now=NOW + 8 * 3600)
    check(not any(x['key'] == 'world-key' for x in r2) and 'rules hash is unknown' in json.dumps(s2.get('world-key', {})), 'no current 2-fer rules hash: world waits (unknown = wait)')
with tempfile.TemporaryDirectory() as t:   # 4e only world ready, no US / CA on the list: nothing to be OK -> world waits
    D, Lk = fixture(t, READY_W)
    r, s, n = plan(D, Lk)
    check(not r and 'no US or Canada area is on the ready list' in json.dumps(s.get('world-key', {})), 'no ready US / Canada area: world waits (nothing is OK)')
import io, contextlib
CLEAN = lambda a: {'area': a, 'answer': 'YES'}
def gate_on_case(rows, stamps, us_stamps=True):
    """US/CA OK, world ready, gate on; audit rows/stamps given. -> (planned tags, seen, printed text)"""
    with tempfile.TemporaryDirectory() as t:
        D, Lk = fixture(t, {**READY_US_CA, **READY_W}); r, s, n = plan(D, Lk)
        finish_all(D, Lk, s, tags_us_ca)
        allc = {c for v in P.R.values() for c in v.split()}
        aud = {c: {'rows': 0, 'built': 'x'} for c in allc if (c[:2] in ('US', 'CA') and us_stamps)}
        aud.update({c: {'rows': 0, 'built': 'x'} for c in stamps})
        w(D / 'data/status/audited.json', aud); w(D / 'data/waiting/questions/map-audit.json', {'questions': rows})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): r2, s2, _ = plan(D, Lk, gate='on', now=NOW + 8 * 3600)
        return [x['tag'] for x in r2], s2, buf.getvalue()
tg, s2, out = gate_on_case([], [])
check(sorted(tg) == sorted(world_tags), f'gate ON, no world audit rows, US/CA OK, ready: world planned ({tg})')
check(all(f'{x}: no world audit rows yet: audit gate not applied' in out for x in world_tags), 'the pass-through is logged for each world area')
tg, s2, out = gate_on_case([{'area': 'W-GB', 'answer': 'NO'}], [])
check('worldwest' not in tg and 'map audit not clean' in s2['world-key']['waiting']['worldwest'] and 'worldnorth' in tg, 'one world audit row (NO): that area waits, others without rows pass')
tg, s2, out = gate_on_case([], ['W-GB'])
check('worldwest' not in tg and 'not audited in this pass' in s2['world-key']['waiting']['worldwest'], 'audit evidence for one country: gate applies to the whole area (unaudited countries wait)')
allw = [c for c in P.R['worldwest'].split()]
tg, s2, out = gate_on_case([CLEAN(c) for c in allw], allw)
check('worldwest' in tg and 'worldwest: no world audit rows' not in out, 'all world rows clean and audited: planned, gate applied (not passed through)')
with tempfile.TemporaryDirectory() as t:   # a US / CA area with no audit rows and the gate ON: still waits (the pass-through is world only)
    D, Lk = fixture(t, {**READY_US_CA, **READY_W})
    r, s, n = plan(D, Lk, gate='on')
    wt = {**s['us-key']['waiting'], **s['ca-key'].get('waiting', {})}
    check(not r and tags_us_ca and all('map audit not clean' in wt.get(x, '') and 'not audited' in wt.get(x, '') for x in tags_us_ca if x in wt) and 'southeast' in wt,
          'a US / Canada area with no audit rows and the gate ON still waits (no pass-through leak)')
with tempfile.TemporaryDirectory() as t:   # 4g a half-ready world area (one country missing from the ready list) does not start
    ready = {**READY_US_CA, 'W-some': {'match': r'^W-(GB|IE|FR|ES|PT|BE|NL|LU|DE)$', 'ownership': {'source': 'fixture'}, 'management': {'source': 'fixture'}}}
    D, Lk = fixture(t, ready); r, s, n = plan(D, Lk); finish_all(D, Lk, s, tags_us_ca)
    r2, s2, _ = plan(D, Lk, now=NOW + 8 * 3600)
    check(not r2, 'worldwest needs ALL its countries on the ready list (W-CH is missing here): nothing starts')

# ---- 5 saved-only hosts: the Data host check (the vendored copy of the net guard's rule)
HR = importlib.util.spec_from_file_location('kpc_host_rules', HERE / '.github/scripts/kpc_host_rules.py'); H = importlib.util.module_from_spec(HR); HR.loader.exec_module(H)
layers = {}
if REAL and (REAL / 'data/world-key/layers.json').exists(): layers = json.load(open(REAL / 'data/world-key/layers.json'))
hosts = {u for u in layers.values() if isinstance(u, str) and re.match(r'https?://', u)}
blocked = [u for u in hosts if not H.host_ok(u)[0]] if hosts else []
check(not hosts or len(blocked) > 0, f'world key layers on saved-copy-only hosts are refused by the host check ({len(blocked)} of {len(hosts)} layer addresses)' if hosts else 'SKIP no world layers file here')
for u in ('https://services7.arcgis.com/x/ArcGIS/rest/services/a/FeatureServer/0/query', 'https://apps.fs.usda.gov/arcx/rest/services/x/MapServer/0/query', 'https://services.arcgis.com/33TOOklri9xpic7U/x'):
    check(not H.host_ok(u)[0], f'saved-only host refused: {u.split("/")[2]}')
# the world line path reads only saved copies: it must not call urlopen at all while planning
import urllib.request
calls = []; real_open = urllib.request.OpenerDirector.open
urllib.request.OpenerDirector.open = lambda self, *a, **k: calls.append(a) or (_ for _ in ()).throw(AssertionError('network call'))
try:
    with tempfile.TemporaryDirectory() as t:
        D, Lk = fixture(t, {**READY_US_CA, **READY_W}); r, s, n = plan(D, Lk); finish_all(D, Lk, s, tags_us_ca); plan(D, Lk, now=NOW + 8 * 3600)
finally: urllib.request.OpenerDirector.open = real_open
check(not calls, 'planning world areas makes no web request of any kind')

# ---- 6 ONE US / Canada list (KPC owner, 2026-11-12, part C): the chain reads .github/fers-areas.json; the old list R is retired
import ast
mp = json.load(open(HERE / '.github/fers-area-map.json'))
check(mp == json.loads(json.dumps(P.area_map(str(HERE)), sort_keys=True)) or mp == json.loads(json.dumps(P.area_map(str(HERE)))), 'fers-area-map.json is current (regenerate: python3 .github/scripts/kpc_fers_chain_plan.py map)')
for name, lst in (('chain (R)', mp['chain']), ('bot (fers-areas.json)', mp['bot'])):
    sts = [x for v in lst.values() for x in v.split()]
    check(len(sts) == len(set(sts)) and 'US-KY' not in sts, f'{name}: no state twice, Kentucky in neither')
check(mp['chain'] == mp['bot'], 'the chain areas ARE the bot areas (one list): a chain line can never write a state set the bot does not')
check(all(mp[k] == [] for k in ('states_only_in_chain', 'states_only_in_bot', 'same_tag_different_members', 'chain_only_tags', 'bot_only_tags')),
      'no difference left between the two maps (CA-SI / CA-SP are in the chain now; no tag names two member sets)')
check({t: v for t, v in P.R.items() if P.kind_of(v) != 'world-key'} == json.load(open(HERE / '.github/fers-areas.json'))['areas'], "the planner's US / CA areas are read from .github/fers-areas.json")
src = (HERE / '.github/scripts/kpc_fers_chain_plan.py').read_text(encoding='utf-8')
check(not re.search(r"\bR = \{'southeast'", src) and 'US-VA US-WV US-GA' not in src, 'the old hard-coded chain list (9-state southeast with VA / WV) is gone from the planner')
for wf in ('kpc-fers-lines.yml', 'kpc-fers-pending.yml', 'kpc-fers-water.yml'):
    txt = (HERE / '.github/workflows' / wf).read_text(encoding='utf-8')
    check(not re.search(r"\bR = \{", txt) and "R = json.load(open('.github/fers-areas.json'" in txt, f'{wf}: no inline copy of an area list; it reads .github/fers-areas.json')
    if wf != 'kpc-fers-pending.yml':
        import yaml
        jb = yaml.safe_load(txt)['jobs']['plan']['steps']
        check(any(str(x.get('uses', '')).startswith('actions/checkout') for x in jb[:1]), f'{wf}: the plan job checks out the repo first, so the list can be read')
# live state is not orphaned: every area tag left in seen.json after the migration is a chain tag; retired tags are kept aside
seen_real = json.load(open(HERE / 'data/status/fers-chain/seen.json'))
mig = {k: P.migrate(seen_real.get(k) or {}) for k in ('us-key', 'ca-key')}
tags_seen = {t for k in mig for t in (mig[k].get('areas') or {})} | {t for k in mig for t in (mig[k].get('ran') or [])}
check(tags_seen <= set(mp['chain']), f'after the migration every area tag in data/status/fers-chain/seen.json is a chain tag ({sorted(tags_seen)})')
old_tags = {t for k in ('us-key', 'ca-key') for t in (seen_real.get(k, {}).get('areas') or {})} - set(mp['chain'])
check(old_tags <= {t for k in mig for t in (mig[k].get('retired') or {})}, f'retired tags are kept in seen[key][retired], not dropped ({sorted(old_tags)})')
with tempfile.TemporaryDirectory() as t:
    D, Lk = fixture(t, READY_US_CA); r, s_, n = plan(D, Lk)
    check('plains' in [x['tag'] for x in r] or 'plains' in s_['us-key']['areas'], 'plains (a bot area) is planned under its own tag')
    finish_all(D, Lk, s_, ['plains'])
    r2, s2, _ = plan(D, Lk, now=NOW + 8 * 3600)
    check('plains' not in [x['tag'] for x in r2] and 'plains' in s2['us-key']['ran'], 'an area with a READY line under its tag is recognised as done (not restarted)')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
