#!/usr/bin/env python3
"""Local simulation of kpc_shard + kpc-sharded.yml with the fake collector (no network, no GitHub).
Scenarios: 1 job vs 4 groups (hosts plan), 4 groups by weight only, a chained run (exit 3 -> join lists left -> next run),
a host used by every area, and the join refusal. Writes sim_results.json next to this file; work goes in --work."""
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARD = HERE.parents[1] / 'kpc_shard.py'
BOT = HERE / 'fake_collector.py'
PY = sys.executable
DATES = re.compile(r'\d{4}-\d{2}-\d{2}(T[0-9:.]+Z?)?')


def sh(args, env=None, **kw):
    return subprocess.run([PY, *map(str, args)], capture_output=True, text=True, env={**os.environ, **(env or {})}, **kw)


def plan(cmd, areas, groups, layers):
    extra = ['--map', layers] if cmd == 'hosts' else []
    r = sh([SHARD, cmd, '--areas', areas, '--groups', groups, '--weights', HERE / 'sim_weights_12.json', *extra])
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout), r.stderr.strip()


def static_spread(mx, layers):
    sys.path.insert(0, str(SHARD.parent))
    import kpc_shard
    return dict(sorted(kpc_shard.host_spread([m['areas'].split(',') for m in mx], kpc_shard.load_hostmap(layers)).items(),
                       key=lambda kv: -kv[1])[:4])


def run_matrix(mx, parts, layers, max_minutes=50):
    """Every group as its own process, all at once (= max-parallel groups)."""
    t = time.time()
    procs = []
    for leg in mx:
        out = parts / str(leg['i'])
        procs.append(subprocess.Popen([PY, BOT, '--out', out, '--max-minutes', str(max_minutes), '--layers', layers],
                                      env={**os.environ, 'AREAS': leg['areas'], 'KPC_SHARD_I': str(leg['i'])},
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    rcs = [p.wait() for p in procs]
    return time.time() - t, rcs


def host_concurrency(parts):
    """Max number of distinct jobs on one host at the same moment: by single request, and by area window
    (from a job's first to last request on that host while working one area)."""
    reqs = []
    for f in Path(parts).rglob('requests.log'):
        reqs += [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    def peak(iv):
        best = {}
        for h in {x[0] for x in iv}:
            ev = sorted([(t0, 1, j) for hh, j, t0, t1 in iv if hh == h] + [(t1, -1, j) for hh, j, t0, t1 in iv if hh == h],
                        key=lambda e: (e[0], e[1]))
            on, m = {}, 0
            for t, d, j in ev:
                on[j] = on.get(j, 0) + d
                m = max(m, sum(1 for v in on.values() if v > 0))
            best[h] = m
        return best
    req = peak([(r['host'], r['job'], r['t0'], r['t1']) for r in reqs])
    win = {}
    for r in reqs:
        k = (r['host'], r['job'], r['area'])
        a, b = win.get(k, (r['t0'], r['t1']))
        win[k] = (min(a, r['t0']), max(b, r['t1']))
    area = peak([(h, j, a, b) for (h, j, _), (a, b) in win.items()])
    return req, area, len(reqs)


def compare(base, data):
    files = sorted(p.name for p in Path(base).glob('US-*.json'))
    other = sorted(p.name for p in Path(data).glob('US-*.json'))
    same_norm = raw_same = 0
    diffs = []
    for n in files:
        a, b = (Path(base) / n).read_bytes(), (Path(data) / n).read_bytes() if (Path(data) / n).exists() else b''
        raw_same += a == b
        if DATES.sub('D', a.decode()) == DATES.sub('D', b.decode()):
            same_norm += 1
        else:
            diffs.append(n)
    return {'files': len(files), 'same_file_set': files == other, 'byte_identical_except_dates': same_norm,
            'byte_identical_raw': raw_same, 'differ': diffs}


def join(parts, into, areas):
    r = subprocess.run([PY, SHARD, 'join', '--parts', parts, '--into', into, '--areas', areas],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', default='/tmp/kpc_shard_sim')
    a = ap.parse_args()
    W = Path(a.work)
    shutil.rmtree(W, ignore_errors=True)
    W.mkdir(parents=True)
    L = HERE / 'sim_layers_12.json'
    areas = ','.join(json.loads(L.read_text()))
    R = {'areas': areas, 'gap_s': 2.0, 'latency_s': 0.3, 'python': sys.version.split()[0]}

    # 1. one job, all 12 areas (today's way)
    base = W / 'base'
    t = time.time()
    r = subprocess.run([PY, BOT, '--out', base, '--layers', L], env={**os.environ, 'AREAS': areas, 'KPC_SHARD_I': '1'},
                       capture_output=True, text=True)
    R['one_job'] = {'seconds': round(time.time() - t, 1), 'rc': r.returncode}
    # 2. hosts plan, 4 groups, in parallel, then join
    mx, note = plan('hosts', areas, 4, L)
    sec, rcs = run_matrix(mx, W / 'hosts4' / 'parts', L)
    rc, out = join(W / 'hosts4' / 'parts', W / 'hosts4' / 'data', areas)
    req, win, n = host_concurrency(W / 'hosts4' / 'parts')
    R['hosts_4_groups'] = {'matrix': mx, 'plan_note': note, 'groups_touching_host_top4': static_spread(mx, L), 'seconds': round(sec, 1), 'job_rcs': rcs, 'join_rc': rc,
                           'join': out, 'speedup': round(R['one_job']['seconds'] / sec, 2), 'requests': n,
                           'max_jobs_per_host_request': req, 'max_jobs_per_host_area_window': win,
                           'compare_to_one_job': compare(base, W / 'hosts4' / 'data')}
    # 3. weight-only plan, 4 groups (what happens without `hosts`)
    mx, note = plan('plan', areas, 4, L)
    sec, rcs = run_matrix(mx, W / 'plan4' / 'parts', L)
    rc, out = join(W / 'plan4' / 'parts', W / 'plan4' / 'data', areas)
    req, win, n = host_concurrency(W / 'plan4' / 'parts')
    R['weight_only_4_groups'] = {'matrix': mx, 'groups_touching_host_top4': static_spread(mx, L), 'seconds': round(sec, 1), 'join_rc': rc,
                                 'speedup': round(R['one_job']['seconds'] / sec, 2),
                                 'max_jobs_per_host_request': req, 'max_jobs_per_host_area_window': win,
                                 'compare_to_one_job': compare(base, W / 'plan4' / 'data')}
    # 4. chain: time runs out (max-minutes 0.05 = 3 s) -> exit 3 -> join exit 3 lists left -> next run takes only those
    mx, _ = plan('hosts', areas, 4, L)
    sec1, rcs1 = run_matrix(mx, W / 'chain' / 'run1', L, max_minutes=0.05)
    rc1, out1 = join(W / 'chain' / 'run1', W / 'chain' / 'data', areas)
    left = out1.split('left=')[-1].strip()
    mx2, _ = plan('hosts', left, 4, L) if left else ([], '')
    sec2, rcs2 = run_matrix(mx2, W / 'chain' / 'run2', L)
    rc2, out2 = join(W / 'chain' / 'run2', W / 'chain' / 'data', areas)
    R['chain'] = {'run1_job_rcs': rcs1, 'run1_join_rc': rc1, 'run1_left': left, 'run2_matrix': mx2, 'run2_job_rcs': rcs2,
                  'run2_join_rc': rc2, 'run2_join': out2, 'compare_to_one_job': compare(base, W / 'chain' / 'data')}
    # 5. one host used by every area
    U = HERE / 'sim_layers_12_universal.json'
    mx, note = plan('hosts', areas, 4, U)
    t = time.time()
    r = subprocess.run([PY, BOT, '--out', W / 'u_base', '--layers', U], env={**os.environ, 'AREAS': areas, 'KPC_SHARD_I': '1'},
                       capture_output=True, text=True)
    ub = time.time() - t
    sec, rcs = run_matrix(mx, W / 'univ' / 'parts', U)
    req, win, n = host_concurrency(W / 'univ' / 'parts')
    R['universal_host'] = {'groups': len(mx), 'matrix': mx, 'one_job_seconds': round(ub, 1), 'seconds': round(sec, 1),
                           'speedup': round(ub / sec, 2), 'max_jobs_per_host_area_window': win}
    # 6. join refusal: part 2 also writes an area from part 1
    bad = W / 'refuse' / 'parts'
    shutil.copytree(W / 'hosts4' / 'parts', bad)
    first = sorted((bad / '1').glob('US-*.json'))[0]
    shutil.copy(first, bad / '2' / first.name)
    rc, out = join(bad, W / 'refuse' / 'data', areas)
    R['join_refusal'] = {'duplicated': first.name, 'rc': rc, 'message': out,
                         'data_dir_created': (W / 'refuse' / 'data').exists()}
    (HERE / 'sim_results.json').write_text(json.dumps(R, indent=1) + '\n')
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
