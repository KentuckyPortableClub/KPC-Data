#!/usr/bin/env python3
"""kpc_shard: run a KPC map bot over several areas at once (library + command line).

  plan   --areas <list|all> --groups N [--weights FILE | --parkinfo DIR]   -> GitHub matrix JSON
  hosts  --areas <list|all> --groups N --map FILE [--max-per-host 2]       -> matrix JSON, <=2 groups per shared host
  join   --parts DIR --into DATA_DIR [--areas LIST] [--state FILE]          -> copy parts in, merge state, exit 3 if left
  --selftest                                                                -> offline tests, prints PASS or FAIL

Exit codes: 0 = done, 3 = areas left (next run takes them), 4 = join refused (two parts wrote the same area,
nothing copied), anything else = a real crash.  Python 3.12, standard library only.
The club order inside each group comes from kpc_order.rank() (imported, never copied).
"""
import argparse, datetime as dt, json, math, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
EXIT_DONE, EXIT_LEFT, EXIT_REFUSED = 0, 3, 4
AREA_RE = re.compile(r'^[A-Z]{2}(?:-[A-Z0-9]{1,5})?$')


# ---------------------------------------------------------------- kpc_order import (sibling, parent, ..., tests/ last)
def _import_kpc_order():
    tried = []
    env = os.environ.get('KPC_ORDER_DIR')
    cands = ([Path(env)] if env else []) + [HERE, HERE.parent, HERE.parent.parent, HERE.parent / 'tools']
    for d in cands:
        tried.append(str(d))
        if (d / 'kpc_order.py').is_file():
            if str(d) not in sys.path:
                sys.path.insert(0, str(d))
            import kpc_order
            return kpc_order, d
    d = HERE / 'tests'                                     # selftest-only copy, see README
    if (d / 'kpc_order.py').is_file():
        sys.path.insert(0, str(d))
        import kpc_order
        print(f'kpc_shard: warning: using the tests/ copy of kpc_order.py (not found in {", ".join(tried)})',
              file=sys.stderr)
        return kpc_order, d
    raise SystemExit(f'kpc_shard: kpc_order.py not found (looked in {", ".join(tried)}); set KPC_ORDER_DIR')


kpc_order, KPC_ORDER_DIR = _import_kpc_order()


def club_rank(area):
    """kpc_order.rank() of an area code. Bare country codes ('CA', 'MX', 'GB') are not matched by rank()'s regex,
    so they go through kpc_order.rank_cc() instead (also imported)."""
    r = kpc_order.rank(area)
    if r == (4, 0) and re.fullmatch(r'[A-Z]{2}', area or ''):
        r = kpc_order.rank_cc(area)
    return r


def club_sort(areas):
    """Club order (US + Canada, North America, W1-W10, rest), stable: ties keep the given order."""
    pos = {a: i for i, a in enumerate(areas)}
    return sorted(areas, key=lambda a: (club_rank(a), pos[a]))


# ---------------------------------------------------------------- inputs
def parse_areas(text):
    out = []
    for a in re.split(r'[\s,]+', text or ''):
        a = a.strip().upper()
        if a and a not in out:
            out.append(a)
    return out


def load_weights(weights=None, parkinfo=None):
    """{area: parks}. A weights file {area: n}, or count parks in parkinfo/*.json ({"parks": {ref: [...]}})."""
    w = {}
    if weights:
        for k, v in json.loads(Path(weights).read_text(encoding='utf-8')).items():
            try:
                w[k.upper()] = max(0.0, float(v))
            except (TypeError, ValueError):
                print(f'kpc_shard: weight for {k} is not a number, using 1', file=sys.stderr)
                w[k.upper()] = 1.0
        return w
    d = Path(parkinfo or 'data/parkinfo')
    if d.is_dir():
        for f in sorted(d.glob('*.json')):
            try:
                w[f.stem.upper()] = float(len(json.loads(f.read_text(encoding='utf-8')).get('parks') or {}))
            except Exception as e:                        # one bad file never stops the plan
                print(f'kpc_shard: {f.name} unreadable ({e}), weight 1', file=sys.stderr)
                w[f.stem.upper()] = 1.0
    return w


def resolve_areas(text, weights, limit=None, done=()):
    if (text or 'all').strip().lower() == 'all':
        areas = sorted(weights)
    else:
        areas = parse_areas(text)
    areas = [a for a in areas if a not in set(done)]
    return areas[:limit] if limit else areas


def done_areas(state_file):
    if not state_file or not Path(state_file).is_file():
        return set()
    st = json.loads(Path(state_file).read_text(encoding='utf-8'))
    return {a for a, e in _state_areas(st).items() if e.get('done')}


# ---------------------------------------------------------------- plan (weight balance, biggest first)
def _finish(groups):
    """Drop empty groups, club order inside each group, groups ordered by their best member, numbered from 1."""
    groups = [club_sort(g) for g in groups if g]
    groups.sort(key=lambda g: (club_rank(g[0]), g[0]))
    return groups


def plan_groups(areas, weights, n):
    """Greedy biggest-first fill: each area (heaviest first) goes to the lightest group."""
    n = max(1, min(int(n), len(areas) or 1))
    order = sorted(areas, key=lambda a: (-weights.get(a, 1.0), club_rank(a), a))
    groups, load = [[] for _ in range(n)], [0.0] * n
    for a in order:
        g = min(range(n), key=lambda k: (load[k], k))
        groups[g].append(a)
        load[g] += weights.get(a, 1.0)
    return _finish(groups)


def matrix(groups):
    return [{'i': i, 'areas': ','.join(g)} for i, g in enumerate(groups, 1)]


# ---------------------------------------------------------------- hosts (<= cap groups touch any one host)
def load_hostmap(path):
    """{area: [host | url | {host|url|source_url: ...}]} or a layer list [{area|state, url|host}] -> {area: set(host)}."""
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(raw, dict) and isinstance(raw.get('layers'), list):
        raw = raw['layers']
    pairs = []
    if isinstance(raw, dict):
        for a, v in raw.items():
            for x in (v if isinstance(v, list) else [v]):
                pairs.append((a, x))
    else:
        for row in raw:
            pairs.append((row.get('area') or row.get('state'), row))
    out = {}
    for a, x in pairs:
        if isinstance(x, dict):
            x = x.get('host') or x.get('url') or x.get('source_url') or ''
        x = str(x).strip()
        h = (urlparse(x).hostname if '://' in x else x.split('/')[0]).lower() if x else ''
        if a and h:
            out.setdefault(str(a).upper(), set()).add(h)
    return out


def host_spread(groups, hosts_of):
    spread = {}
    for g in groups:
        for h in set().union(*[hosts_of.get(a, set()) for a in g]) if g else ():
            spread[h] = spread.get(h, 0) + 1
    return spread


def _greedy_hosts(order, weights, hosts_of, n, cap):
    groups, load, ghosts, hcount = [[] for _ in range(n)], [0.0] * n, [set() for _ in range(n)], {}
    for a in order:
        hs = hosts_of.get(a, set())
        ok = [k for k in range(n) if all(h in ghosts[k] or hcount.get(h, 0) < cap for h in hs)]
        if not ok:
            return None
        k = min(ok, key=lambda k: (load[k], -len(hs & ghosts[k]), k))
        for h in hs - ghosts[k]:
            hcount[h] = hcount.get(h, 0) + 1
        ghosts[k] |= hs
        groups[k].append(a)
        load[k] += weights.get(a, 1.0)
    return groups


def _bundle_hosts(order, weights, hosts_of, n, cap, shared):
    """Always valid: areas linked by a shared host form one component; a component is split into at most `cap`
    bundles and each bundle goes whole into one group, so no shared host can reach more than `cap` groups."""
    parent = {a: a for a in order}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    first = {}
    for a in order:
        for h in hosts_of.get(a, set()) & shared:
            if h in first:
                parent[find(a)] = find(first[h])
            else:
                first[h] = a
    comps = {}
    for a in order:
        comps.setdefault(find(a), []).append(a)
    target = sum(weights.get(a, 1.0) for a in order) / n
    bundles = []
    for comp in comps.values():
        cw = sum(weights.get(a, 1.0) for a in comp)
        k = max(1, min(cap, len(comp), math.ceil(cw / target) if target else 1))
        sub, sl = [[] for _ in range(k)], [0.0] * k
        for a in comp:                                    # comp is already heaviest-first
            j = min(range(k), key=lambda j: (sl[j], j))
            sub[j].append(a)
            sl[j] += weights.get(a, 1.0)
        bundles += [b for b in sub if b]
    bundles.sort(key=lambda b: (-sum(weights.get(a, 1.0) for a in b), order.index(b[0])))
    groups, load = [[] for _ in range(n)], [0.0] * n
    for b in bundles:
        k = min(range(n), key=lambda k: (load[k], k))
        groups[k] += b
        load[k] += sum(weights.get(a, 1.0) for a in b)
    return groups


def _improve(groups, weights, hosts_of, cap, rounds=200):
    """Local search: move or swap one area out of the heaviest group while the host rule still holds."""
    W = lambda g: sum(weights.get(a, 1.0) for a in g)
    ok = lambda gs: all(v <= cap for v in host_spread(gs, hosts_of).values())
    for _ in range(rounds):
        loads = [W(g) for g in groups]
        hi = max(range(len(groups)), key=lambda k: loads[k])
        best = None
        for lo in range(len(groups)):
            if lo == hi:
                continue
            for a in groups[hi]:
                for b in [None] + groups[lo]:
                    d = weights.get(a, 1.0) - (weights.get(b, 1.0) if b else 0.0)
                    new_hi, new_lo = loads[hi] - d, loads[lo] + d
                    if d <= 0 or max(new_hi, new_lo) >= loads[hi] - 1e-9:
                        continue
                    if best and max(new_hi, new_lo) >= best[0]:
                        continue
                    trial = [list(g) for g in groups]
                    trial[hi].remove(a)
                    trial[lo].append(a)
                    if b:
                        trial[lo].remove(b)
                        trial[hi].append(b)
                    if ok(trial):
                        best = (max(new_hi, new_lo), trial)
        if not best:
            break
        groups = best[1]
    return groups


def host_groups(areas, weights, hosts_of, n, cap=2):
    """Balance by weight under the rule: at most `cap` groups (= jobs at once) ever touch one host.
    Try A (host-aware greedy, biggest first, lightest feasible group, ties -> group already using the hosts);
    if A gets stuck, or B balances better, use B (component bundles, always valid). Both are then improved by a
    local search (move/swap one area out of the heaviest group if the host rule still holds). Returns (groups, method)."""
    n = max(1, min(int(n), len(areas) or 1))
    order = sorted(areas, key=lambda a: (-weights.get(a, 1.0), club_rank(a), a))
    count = {}
    for a in areas:
        for h in hosts_of.get(a, set()):
            count[h] = count.get(h, 0) + 1
    shared = {h for h, c in count.items() if c > cap}      # a host used by <= cap areas can never break the rule
    hs = {a: hosts_of.get(a, set()) & shared for a in areas}
    cands = []
    ga = _greedy_hosts(order, weights, hs, n, cap)
    if ga is not None:
        cands.append(('greedy', ga))
    cands.append(('bundles', _bundle_hosts(order, weights, hs, n, cap, shared)))
    cands = [(m, _improve(g, weights, hs, cap)) for m, g in cands]

    def score(g):
        loads = [sum(weights.get(a, 1.0) for a in x) for x in g if x]
        return (max(loads) if loads else 0, sum(host_spread(g, hs).values()))
    method, best = min(cands, key=lambda c: score(c[1]))
    best = _finish(best)
    assert all(v <= cap for v in host_spread(best, hs).values())
    return best, method


# ---------------------------------------------------------------- join
def _state_areas(st):
    """Accept {"areas": {A: {"done": ts|null, "counts": {...}}}} or {"done": {A: ts}}."""
    areas = {}
    for a, e in (st.get('areas') or {}).items():
        areas[a.upper()] = dict(e) if isinstance(e, dict) else {'done': e}
    for a, ts in (st.get('done') or {}).items() if isinstance(st.get('done'), dict) else ():
        areas.setdefault(a.upper(), {})['done'] = ts
    return areas


def _when(ts):
    if not ts:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    if ts is True:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc) + dt.timedelta(seconds=1)
    try:
        t = dt.datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
        return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc) + dt.timedelta(seconds=1)


def _add_counts(into, c):
    for k, v in (c or {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            into[k] = into.get(k, 0) + v
    return into


def file_area(rel):
    """Area of a part file: its name up to the first '.' or '_' (US-TX.json, US-TX_layers.geojson)."""
    stem = re.split(r'[._]', Path(rel).name, maxsplit=1)[0].upper()
    return stem if AREA_RE.match(stem) else None


def join_parts(parts, into, areas=None, state=None, now=None):
    """Returns (exit_code, report). Copies nothing at all if two parts wrote the same area."""
    parts, into = Path(parts), Path(into)
    state = Path(state) if state else into / 'state.json'
    rep = {'parts': [], 'copied': [], 'skipped': [], 'conflicts': [], 'stray': [], 'warnings': []}
    seen, plan = {}, []                                      # area -> first part; [(src, rel)]
    states = []
    dirs = sorted([d for d in parts.iterdir() if d.is_dir()], key=lambda d: d.name) if parts.is_dir() else []
    for d in dirs:
        m = re.search(r'(\d+)$', d.name)
        if not m:
            rep['warnings'].append(f'{d.name}: no group number, ignored')
            continue
        i = int(m.group(1))
        rep['parts'].append(i)
        st, mine = {}, set()
        sf = next((p for p in (d / f'state-{i}.json', d / 'state.json') if p.is_file()), None)
        if sf is None:
            sf = next(iter(sorted(d.glob('state-*.json'))), None)
        if sf:
            try:
                st = json.loads(sf.read_text(encoding='utf-8'))
            except Exception as e:
                rep['warnings'].append(f'part {i}: {sf.name} unreadable ({e})')
        sa = _state_areas(st)
        states.append((i, st, sa))
        wrote = set(sa)
        for f in sorted(p for p in d.rglob('*') if p.is_file()):
            rel = f.relative_to(d)
            if f == sf or re.fullmatch(r'state(-\d+)?\.json', f.name) and len(rel.parts) == 1:
                continue
            if rel.parts[0] == 'work' or any(x.startswith('.') for x in rel.parts):
                rep['skipped'].append(f'{i}/{rel}')
                continue
            a = file_area(rel)
            if not a:
                rep['skipped'].append(f'{i}/{rel}')
                continue
            wrote.add(a)
            plan.append((f, rel, i, a))
        for a in sorted(wrote):
            if a in seen and seen[a] != i:
                rep['conflicts'].append({'area': a, 'parts': [seen[a], i]})
            seen.setdefault(a, i)
        if areas:
            rep['stray'] += [f'{i}:{a}' for a in sorted(wrote - set(areas))]
    rels = {}
    for f, rel, i, a in plan:                               # same path from two parts = conflict too
        if rel in rels and rels[rel] != i and not any(c['area'] == a for c in rep['conflicts']):
            rep['conflicts'].append({'area': a, 'file': str(rel), 'parts': [rels[rel], i]})
        rels.setdefault(rel, i)
    if rep['conflicts']:
        rep['refused'] = True
        rep['left'] = []
        return EXIT_REFUSED, rep
    for f, rel, i, a in plan:
        dst = into / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        rep['copied'].append(str(rel))
    old = {}
    if state.is_file():
        try:
            old = json.loads(state.read_text(encoding='utf-8'))
        except Exception as e:
            rep['warnings'].append(f'{state}: unreadable ({e}), starting fresh')
    merged = _state_areas(old)
    counts = {}
    for i, st, sa in states:
        _add_counts(counts, st.get('counts'))
        for a, e in sa.items():
            if a not in merged or _when(e.get('done')) >= _when(merged[a].get('done')):
                merged[a] = e
    expect = list(areas) if areas else sorted(merged)
    left = [a for a in expect if not (merged.get(a) or {}).get('done')]
    out = {'areas': {a: merged[a] for a in sorted(merged)}, 'counts': counts,
           'counts_total': _add_counts(dict(old.get('counts_total') or old.get('counts') or {}), counts),
           'left': left, 'updated': now or dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(out, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    rep.update(refused=False, left=left, done=[a for a in expect if a not in left], counts=counts, state=str(state))
    return (EXIT_LEFT if left else EXIT_DONE), rep


# ---------------------------------------------------------------- helpers for the bots
def areas_from_env(default=None):
    """The bot's list of areas from $AREAS (comma/space separated). None/'all' -> default."""
    v = os.environ.get('AREAS', '').strip()
    return default if not v or v.lower() == 'all' else parse_areas(v)


def write_part_state(out, areas, counts=None, i=None):
    """Write <out>/state-<i>.json: {"group": i, "areas": {A: {"done": ts|null, "counts": {...}}}, "counts": {...}}."""
    i = int(i if i is not None else os.environ.get('KPC_SHARD_I', '1'))
    p = Path(out) / f'state-{i}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'group': i, 'areas': areas, 'counts': counts or {}}, indent=1, sort_keys=True) + '\n',
                 encoding='utf-8')
    return p


# ---------------------------------------------------------------- command line
def _emit(m, out, name, extra):
    print(json.dumps(m, separators=(',', ':')))
    if out:
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / name).write_text(json.dumps({'matrix': m, **extra}, indent=1) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(prog='kpc_shard', description=__doc__.split('\n')[0])
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--out', help='write plan/join reports here (stdout always gets the result)')
    common.add_argument('--max-minutes', type=float, default=50, help='contract flag; these steps take seconds')
    common.add_argument('--limit', type=int, help='only the first N areas (tests)')
    common.add_argument('--areas', default='all')
    for name in ('plan', 'hosts'):
        p = sub.add_parser(name, parents=[common])
        p.add_argument('--groups', type=int, default=8)
        p.add_argument('--weights', help='{area: number} JSON')
        p.add_argument('--parkinfo', default='data/parkinfo', help='dir of parkinfo/*.json (weight = parks)')
        p.add_argument('--resume', action='store_true', help='skip areas the --state file says are done')
        p.add_argument('--state', help='state.json to read for --resume')
        if name == 'hosts':
            p.add_argument('--map', required=True, help='{area: [hosts|urls]} or the bot layer list')
            p.add_argument('--max-per-host', type=int, default=2)
    p = sub.add_parser('join', parents=[common])
    p.add_argument('--parts', required=True)
    p.add_argument('--into', required=True)
    p.add_argument('--state', help='merged state file (default <into>/state.json)')
    p.add_argument('--resume', action='store_true', help='contract flag; join always merges with --state')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd in ('plan', 'hosts'):
        w = load_weights(a.weights, a.parkinfo)
        done = done_areas(a.state) if a.resume else set()
        areas = resolve_areas(a.areas, w, a.limit, done)
        if not areas:
            _emit([], a.out, f'{a.cmd}.json', {'note': 'no areas'})
            return EXIT_DONE
        miss = [x for x in areas if x not in w]
        if miss:
            print(f'kpc_shard: no weight for {",".join(miss)}, using 1', file=sys.stderr)
        extra = {}
        if a.cmd == 'plan':
            groups = plan_groups(areas, w, a.groups)
        else:
            hm = load_hostmap(a.map)
            groups, method = host_groups(areas, w, hm, a.groups, a.max_per_host)
            extra = {'method': method, 'host_groups': dict(sorted(host_spread(groups, hm).items()))}
        loads = [sum(w.get(x, 1.0) for x in g) for g in groups]
        print(f'kpc_shard {a.cmd}: {len(areas)} areas -> {len(groups)} groups, loads {loads}'
              + (f', method {extra["method"]}, busiest host in {max(extra["host_groups"].values(), default=0)} groups'
                 if extra else ''), file=sys.stderr)
        _emit(matrix(groups), a.out, f'{a.cmd}.json', {'loads': loads, **extra})
        return EXIT_DONE
    if a.cmd == 'join':
        areas = None if a.areas.strip().lower() == 'all' else parse_areas(a.areas)
        rc, rep = join_parts(a.parts, a.into, areas, a.state)
        if a.out:
            Path(a.out).mkdir(parents=True, exist_ok=True)
            (Path(a.out) / 'join_report.json').write_text(json.dumps(rep, indent=1) + '\n', encoding='utf-8')
        if rc == EXIT_REFUSED:
            print(f'join REFUSED, nothing copied: ' + '; '.join(
                f'{c["area"]} written by parts {c["parts"]}' + (f' ({c["file"]})' if 'file' in c else '')
                for c in rep['conflicts']))
        else:
            print(f'join: parts={len(rep["parts"])} files={len(rep["copied"])} done={len(rep["done"])} '
                  f'left={len(rep["left"])} skipped={len(rep["skipped"])}')
        for s in rep['stray']:
            print(f'warning: part wrote an area outside --areas: {s}', file=sys.stderr)
        print('left=' + ','.join(rep['left']))
        return rc
    ap.print_help()
    return 2


# ---------------------------------------------------------------- selftest (offline, tests/ fixtures)
def selftest():
    T = HERE / 'tests'
    fx, ex = T / 'fixtures', T / 'expected'
    res = []

    def check(name, ok, why=''):
        res.append(ok)
        print(f'{"ok  " if ok else "FAIL"} {name}' + ('' if ok else f'  -- {why}'))

    def load(p):
        return json.loads(Path(p).read_text(encoding='utf-8'))
    try:
        check('kpc_order imported (not copied into kpc_shard.py)', hasattr(kpc_order, 'rank'), str(KPC_ORDER_DIR))
        check('club order: US+CA, NA, W1-W10, rest',
              club_sort(['ZA', 'GB', 'MX', 'CA', 'US-RI', 'AU', 'US-TX']) == ['CA', 'US-RI', 'US-TX', 'MX', 'GB', 'AU', 'ZA'],
              str(club_sort(['ZA', 'GB', 'MX', 'CA', 'US-RI', 'AU', 'US-TX'])))
        w = load_weights(parkinfo=fx / 'parkinfo')
        check('weights from parkinfo/*.json', w == load(ex / 'weights_from_parkinfo.json'), str(w))
        g = plan_groups(resolve_areas('all', w), w, 3)
        check('plan from parkinfo, 3 groups', matrix(g) == load(ex / 'plan_parkinfo_3.json'), json.dumps(matrix(g)))
        ws = load_weights(weights=fx / 'weights.json')
        areas = resolve_areas('all', ws)
        for n in (1, 4, 8, 12):
            g = plan_groups(areas, ws, n)
            loads = [sum(ws[a] for a in x) for x in g]
            flat = sorted(a for x in g for a in x)
            check(f'plan {n} groups: every area once, balanced, club order kept',
                  flat == sorted(areas) and max(loads) - min(loads) <= max(ws.values())
                  and all(x == club_sort(x) for x in g), str(g))
        check('plan weights, 4 groups = expected', matrix(plan_groups(areas, ws, 4)) == load(ex / 'plan_weights_4.json'))
        check('plan --resume skips done areas',
              'US-TX' not in resolve_areas('all', ws, done=done_areas(fx / 'state_done.json')))
        hm = load_hostmap(fx / 'hosts.json')
        g, meth = host_groups(areas, ws, hm, 4)
        sp = host_spread(g, hm)
        check('hosts: no host in more than 2 groups', max(sp.values()) <= 2, str(sp))
        check('hosts 4 groups = expected', {'matrix': matrix(g), 'method': meth} == load(ex / 'hosts_4.json'),
              json.dumps({'matrix': matrix(g), 'method': meth}))
        naive = host_spread(plan_groups(areas, ws, 4), hm)
        check('hosts beats weight-only plan on the same map', max(naive.values()) > 2, str(naive))
        hl = load_hostmap(fx / 'layer_list.json')
        check('hosts reads a bot layer list (urls)', hl.get('US-KY') == {'edits.nationalmap.gov', 'kygisserver.ky.gov'},
              str(hl))
        g, meth = host_groups(areas, ws, {a: {'edits.nationalmap.gov'} for a in areas}, 6)
        check('hosts: one host used by every area -> only 2 groups', len(g) == 2, str(g))
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / 'data').mkdir()
            shutil.copy(fx / 'state_before.json', td / 'data' / 'state.json')
            rc, rep = join_parts(fx / 'parts_ok', td / 'data', ['US-TX', 'US-RI', 'US-KY', 'US-TN'],
                                 now='2026-10-31T00:00:00Z')
            st = load(td / 'data' / 'state.json')
            check('join ok: exit 0, files copied', rc == 0 and sorted(rep['copied']) == load(ex / 'join_copied.json'),
                  f'{rc} {rep["copied"]}')
            check('join ok: merged state (newest done wins, counts summed)', st == load(ex / 'join_state.json'),
                  json.dumps(st))
            check('join skips work/ and non-area files', set(rep['skipped']) == {'1/work/raw.txt', '2/report.txt'},
                  str(rep['skipped']))
            rc, rep = join_parts(fx / 'parts_left', td / 'data2', ['US-TX', 'US-RI', 'US-KY'], now='x')
            check('join left: exit 3 and lists US-KY', rc == 3 and rep['left'] == ['US-KY'], f'{rc} {rep["left"]}')
            rc, rep = join_parts(fx / 'parts_conflict', td / 'data3', None)
            check('join refuses two parts writing one area, copies nothing',
                  rc == 4 and rep['conflicts'] and not (td / 'data3').exists(), f'{rc} {rep}')
            # CLI round trip with real exit codes
            cli = [sys.executable, str(Path(__file__).resolve())]
            r = subprocess.run(cli + ['plan', '--areas', 'US-TX,US-RI,US-KY', '--groups', '2', '--weights',
                                      str(fx / 'weights.json'), '--out', str(td / 'o')], capture_output=True, text=True)
            check('CLI plan prints matrix JSON', r.returncode == 0 and json.loads(r.stdout)[0]['i'] == 1
                  and (td / 'o' / 'plan.json').is_file(), r.stdout + r.stderr)
            r = subprocess.run(cli + ['join', '--parts', str(fx / 'parts_conflict'), '--into', str(td / 'd4')],
                               capture_output=True, text=True)
            check('CLI join refusal exit 4', r.returncode == 4 and 'REFUSED' in r.stdout, r.stdout + r.stderr)
            r = subprocess.run(cli + ['join', '--parts', str(fx / 'parts_left'), '--into', str(td / 'd5'), '--areas',
                                      'US-TX,US-RI,US-KY'], capture_output=True, text=True)
            check('CLI join left exit 3', r.returncode == 3 and 'left=US-KY' in r.stdout, r.stdout + r.stderr)
    except Exception as e:
        import traceback
        traceback.print_exc()
        check('selftest ran without crashing', False, repr(e))
    ok = all(res)
    print('PASS' if ok else 'FAIL', f'({sum(res)}/{len(res)} checks)')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
