#!/usr/bin/env python3
"""Memory guard for the 2-fer steps (KPC owner, 2026-11-12; fetcher of run 43205747757: pass 1 peaked at 6,973 MB, pass 2 printed
nothing for 30 minutes and the runner got a shutdown signal; the whole southeast line was lost).

    python3 kpc_mem_guard.py [--label TEXT] -- COMMAND ...
    shell: python3 kpcdata/.github/scripts/kpc_mem_guard.py -- bash -e {0}      (a workflow step's own shell: the whole step is guarded)

Runs COMMAND as a child (its own process group) and watches it from OUTSIDE (standard library, Linux /proc only):
  - every KPC_MEM_GUARD_SAMPLE_S (2) seconds: the resident memory of the child's whole process tree, and what the SYSTEM still has
    (MemAvailable in /proc/meminfo, and the cgroup's room when the job runs under a cgroup memory limit): the runner dies when the
    machine runs out, not when one process reaches a number;
  - every KPC_MEM_GUARD_BEAT_S (60) seconds one 'memory guard:' line (RSS, peak, available, swap, memory pressure, CPU seconds the
    tree used in the last minute, the pass in hand), so a silent half hour can never happen again in the log, even when Python is
    inside one long C call;
  - when the tree passes the limit (KPC_MEM_GUARD_MB, default 70 % of MemTotal) or the system's available memory falls under the
    floor (KPC_MEM_GUARD_FLOOR_MB, default the larger of 1,536 MB and 12 % of MemTotal): SIGINT to the whole group (Python stops
    with KeyboardInterrupt: kpc_fers.py catches only Exception, HardStop and ParkTimeout, so nothing turns it into an answer, and
    nothing is saved by the stopped pass), then SIGKILL after KPC_MEM_GUARD_GRACE_S (30) seconds, or at once when the system falls
    under half the floor. Exit code 86, one ::error line, one line in the step summary and one line in KPC_MEM_STOP_FILE
    (default $RUNNER_TEMP/kpc-mem-stop.txt) for the workflow.
  - the kernel backstop: the child (and everything it starts) gets oom_score_adj 1000, so if a spike between two samples empties the
    machine, the kernel's out-of-memory killer takes the 2-fer process first, never the runner agent. Raising one's own score needs no
    privilege. A kernel kill of the child is reported as a memory stop too (the oom_kill count in /proc/vmstat went up): exit 86.
    NOT used, on purpose: RLIMIT_AS / ulimit -v. kpc_fers.py's pair test (find_spots, 'except Exception' around area_spots /
    line_spots) would catch the MemoryError and count the pair as tested with no spot: a wrong 'no 2-fer', not a crash.
Otherwise the child's own exit code is passed through unchanged (0, 1 = crash, 3 = KPC_HARD_END, ...; a signal N = 128 + N).
KPC_MEM_GUARD=off: heartbeat lines only, never a stop. The limits are read from MemTotal at run time; a set value is clamped so the
runner agent always keeps at least 2,048 MB above the limit and the floor is never under 1,024 MB. No result file is ever written.
"""
import os
import signal
import subprocess
import sys
import time

STOP_CODE = 86
MB = 1048576.0


def _num(v, d):
    try: return float(v)
    except (TypeError, ValueError): return d


def meminfo(path='/proc/meminfo'):
    """{'MemTotal': MB, 'MemAvailable': MB, 'SwapTotal': MB, 'SwapFree': MB}"""
    out = {}
    try:
        for ln in open(path):
            k, _, v = ln.partition(':')
            if k in ('MemTotal', 'MemAvailable', 'MemFree', 'SwapTotal', 'SwapFree'): out[k] = int(v.split()[0]) / 1024.0
    except OSError: pass
    out.setdefault('MemAvailable', out.get('MemFree', 0.0))
    return out


def cgroup_room():
    """MB left under this process's cgroup memory limit (v2 memory.max - memory.current, v1 limit - usage), minus nothing for the
    page cache (conservative); None when there is no limit or nothing can be read."""
    try: lines = open('/proc/self/cgroup').read().split('\n')
    except OSError: return None
    for ln in lines:
        parts = ln.split(':', 2)
        if len(parts) != 3: continue
        hid, ctl, path = parts
        if hid == '0' and ctl == '':
            base = '/sys/fs/cgroup' + path
            mx, cur = os.path.join(base, 'memory.max'), os.path.join(base, 'memory.current')
        elif 'memory' in ctl.split(','):
            base = '/sys/fs/cgroup/memory' + path
            mx, cur = os.path.join(base, 'memory.limit_in_bytes'), os.path.join(base, 'memory.usage_in_bytes')
        else: continue
        try:
            lim = open(mx).read().strip()
            if lim == 'max' or int(lim) >= 1 << 60: continue
            inact = 0
            try:
                for s in open(os.path.join(base, 'memory.stat')):
                    k, v = s.split()
                    if k in ('inactive_file', 'total_inactive_file'): inact = max(inact, int(v))
            except (OSError, ValueError): pass
            return (int(lim) - int(open(cur).read()) + inact) / MB
        except (OSError, ValueError): continue
    return None


def system():
    """(MemTotal MB, available MB, swap used MB): available = the smaller of MemAvailable and the cgroup's room."""
    m = meminfo()
    av = m.get('MemAvailable', 0.0)
    cg = cgroup_room()
    if cg is not None: av = min(av, cg)
    return m.get('MemTotal', 0.0), av, max(0.0, m.get('SwapTotal', 0.0) - m.get('SwapFree', 0.0))


def _stat(pid):
    """(ppid, pgid, state, utime+stime ticks) of a process, or None."""
    try: s = open(f'/proc/{pid}/stat').read()
    except OSError: return None
    rest = s[s.rfind(')') + 2:].split()
    return int(rest[1]), int(rest[2]), rest[0], int(rest[11]) + int(rest[12])


def tree(root, pgid=None):
    """Pids of root and every descendant, plus any process still in the child's process group (a grandchild whose parent died)."""
    kids, info = {}, {}
    for d in os.listdir('/proc'):
        if not d.isdigit(): continue
        st = _stat(int(d))
        if st is None: continue
        info[int(d)] = st; kids.setdefault(st[0], []).append(int(d))
    out, todo = set(), [root]
    while todo:
        p = todo.pop()
        if p in out or p not in info: continue
        out.add(p); todo += kids.get(p, [])
    if pgid: out |= {p for p, st in info.items() if st[1] == pgid}
    return out, info


PAGE = os.sysconf('SC_PAGE_SIZE') if hasattr(os, 'sysconf') else 4096
TICK = os.sysconf('SC_CLK_TCK') if hasattr(os, 'sysconf') else 100


def rss_mb(pids):
    t = 0
    for p in pids:
        try: t += int(open(f'/proc/{p}/statm').read().split()[1])
        except (OSError, ValueError, IndexError): pass
    return t * PAGE / MB


def pressure():
    """'some avg10' of /proc/pressure/memory (percent of time tasks waited on memory), or None."""
    try:
        for ln in open('/proc/pressure/memory'):
            if ln.startswith('some'):
                return float(dict(x.split('=') for x in ln.split()[1:])['avg10'])
    except (OSError, KeyError, ValueError): return None
    return None


def oom_kills():
    try:
        for ln in open('/proc/vmstat'):
            if ln.startswith('oom_kill '): return int(ln.split()[1])
    except (OSError, ValueError): pass
    return None


def what_pass(pids):
    """'pass 2' when a process in the tree runs with PASS=2 in its environment (kpc_fers.py), else ''."""
    best = ''
    for p in sorted(pids):
        try: env = open(f'/proc/{p}/environ', 'rb').read().split(b'\0')
        except OSError: continue
        for e in env:
            if e.startswith(b'PASS='): best = 'pass ' + e[5:].decode(errors='replace')
    return best


def limits(total, env=os.environ):
    """(limit MB for the tree, floor MB for the system's available memory), from MemTotal; clamped so the runner keeps room."""
    lim = _num(env.get('KPC_MEM_GUARD_MB'), 0) or total * 0.70
    floor = _num(env.get('KPC_MEM_GUARD_FLOOR_MB'), 0) or max(1536.0, total * 0.12)
    if total > 0: lim = min(lim, max(256.0, total - 2048.0))
    return lim, max(1024.0, floor)


def label(env=os.environ):
    if env.get('KPC_MEM_LABEL'): return env['KPC_MEM_LABEL']
    sts = (env.get('STATES') or '').split()
    tag = env.get('RUN_TAG') or env.get('REGION') or ''
    job = env.get('GITHUB_JOB') or ''
    bits = [b for b in (tag, ' '.join(sts) and f"({' '.join(sts)})", job and f'[{job}]') if b]
    return ' '.join(bits) or 'the 2-fer step'


def keeps(env=os.environ):
    n = len((env.get('STATES') or '').split())
    return ('these %d states keep their previous files; the others are not affected' % n) if n > 1 else \
        'this state keeps its previous file; the others are not affected'


def say(line):
    sys.stdout.write(line + '\n'); sys.stdout.flush()


def fmt(x): return f'{x:,.0f}'


def run(cmd, env=os.environ, sample=None, beat=None, grace=None, read_system=None, read_rss=None, now=time.monotonic):
    """Start cmd, watch it, return the exit code (STOP_CODE after a memory stop). read_system() -> (total, avail, swap) and
    read_rss(pids) -> MB can be injected (tests)."""
    sample = sample if sample is not None else _num(env.get('KPC_MEM_GUARD_SAMPLE_S'), 2.0)
    beat = beat if beat is not None else _num(env.get('KPC_MEM_GUARD_BEAT_S'), 60.0)
    grace = grace if grace is not None else _num(env.get('KPC_MEM_GUARD_GRACE_S'), 30.0)
    read_system = read_system or system
    read_rss = read_rss or rss_mb
    on = str(env.get('KPC_MEM_GUARD') or 'on').lower() not in ('off', '0', 'no')
    total, avail, _ = read_system()
    lim, floor = limits(total, env)
    name = label(env)
    say(f'memory guard: {name}: watching; machine {fmt(total)} MB, available {fmt(avail)} MB; stop when the step passes '
        f'{fmt(lim)} MB or the machine has under {fmt(floor)} MB left' + ('' if on else ' (KPC_MEM_GUARD=off: lines only, no stop)'))

    def pre():
        try:
            with open('/proc/self/oom_score_adj', 'w') as f: f.write('1000')   # the kernel takes the 2-fer process first, never the runner
        except OSError: pass
    oom0 = oom_kills()
    t0 = now()
    p = subprocess.Popen(cmd, preexec_fn=pre, start_new_session=True)
    pgid = p.pid

    def fwd(sig, _f):   # the runner cancels a step with SIGINT / SIGTERM to this process: pass it on to the guarded group
        try: os.killpg(pgid, sig)
        except OSError: pass
    for s in (signal.SIGINT, signal.SIGTERM):
        try: signal.signal(s, fwd)
        except (ValueError, OSError): pass

    peak, last_beat, cpu0, stop, stop_t, killed, why = 0.0, t0, None, None, None, False, ''
    while True:
        rc = p.poll()
        if rc is not None: break
        pids, info = tree(p.pid, pgid)
        rss = read_rss(pids)
        total, avail, swap = read_system()
        peak = max(peak, rss)
        t = now()
        if t - last_beat >= beat:
            cpu = sum(info[q][3] for q in pids if q in info) / float(TICK)
            used = '' if cpu0 is None else f', CPU {cpu - cpu0:.0f} s in the last {t - last_beat:.0f} s'
            states = ''.join(sorted({info[q][2] for q in pids if q in info}))
            psi = pressure()
            say(f'memory guard: {name} {what_pass(pids)}'.rstrip() + f': {(t - t0) / 60:.0f} min, RSS {fmt(rss)} MB ({len(pids)} processes, '
                f'state {states or "-"}), peak {fmt(peak)} MB, machine available {fmt(avail)} of {fmt(total)} MB, swap used {fmt(swap)} MB'
                + (f', memory pressure {psi:.0f} %' if psi is not None else '') + used + f'; limit {fmt(lim)} MB, floor {fmt(floor)} MB')
            cpu0, last_beat = cpu, t
        if on and stop is None and (rss > lim or avail < floor):
            why = (f'the step passed {fmt(lim)} MB' if rss > lim else f'the machine had only {fmt(avail)} MB left (floor {fmt(floor)} MB)')
            stop = (rss, avail, what_pass(pids)); stop_t = t
            say(f'memory guard: {name}: {why} (RSS {fmt(rss)} MB): asking it to stop (SIGINT), hard stop in {grace:.0f} s')
            try: os.killpg(pgid, signal.SIGINT)
            except OSError: pass
            for q in pids:
                try: os.kill(q, signal.SIGINT)
                except OSError: pass
        elif stop is not None and not killed and (t - stop_t >= grace or avail < floor / 2):
            say(f'memory guard: {name}: still running {t - stop_t:.0f} s after the request (available {fmt(avail)} MB): killed (SIGKILL)')
            killed = True
            for q in pids:
                try: os.kill(q, signal.SIGKILL)
                except OSError: pass
            try: os.killpg(pgid, signal.SIGKILL)
            except OSError: pass
        time.sleep(sample)
    # nothing of the guarded group may outlive it (a grandchild whose parent already exited)
    left, _ = tree(p.pid, pgid)
    for q in left - {p.pid}:
        try: os.kill(q, signal.SIGKILL)
        except OSError: pass
    code = rc if rc >= 0 else 128 - rc
    oom1 = oom_kills()
    if stop is None and rc == -signal.SIGKILL and oom0 is not None and oom1 is not None and oom1 > oom0:
        stop, why = (peak, read_system()[1], ''), 'the kernel ran out of memory and killed it (oom_kill in /proc/vmstat went up)'
    if stop is None:
        say(f'memory guard: {name}: finished with exit {code}; peak {fmt(peak)} MB of the {fmt(lim)} MB limit')
        return code
    at, av, ps = stop
    msg = (f'memory guard: {name}{" " + ps if ps else ""} stopped at {fmt(at)} MB (limit {fmt(lim)}, system available {fmt(av)} MB): '
           f'{keeps(env)}')
    print(f'::error title=memory guard::{msg}. Why: {why}. It needs a smaller cut or more memory; it is not retried on the same cut.', flush=True)
    f = env.get('KPC_MEM_STOP_FILE') or (os.path.join(env['RUNNER_TEMP'], 'kpc-mem-stop.txt') if env.get('RUNNER_TEMP') else '')
    if f:
        try:
            with open(f, 'a', encoding='utf-8') as fh: fh.write(msg + '\n')
        except OSError: pass
    if env.get('GITHUB_STEP_SUMMARY'):
        try:
            with open(env['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as fh:
                fh.write(f'**Memory guard:** {msg}. **Needs a smaller cut or more memory** (not retried on the same cut).\n')
        except OSError: pass
    return STOP_CODE


def stopped_for_memory(data, tag, since=None):
    """True when data/status/line-breaks.json records a memory-guard stop of this line tag (at or after 'since', 'YYYY-MM-DD HH:MM UTC'
    or ISO). Used by the chain plan and the lines' retry round: a memory stop is never retried blindly on the same cut."""
    import json
    try: L = json.load(open(os.path.join(data, 'data/status/line-breaks.json'), encoding='utf-8'))
    except (OSError, ValueError): return False
    t0 = 0.0
    if since:
        for f in ('%Y-%m-%d %H:%M UTC', '%Y-%m-%dT%H:%M:%SZ'):
            try:
                import calendar
                t0 = calendar.timegm(time.strptime(since, f)); break
            except ValueError: continue
    return any(isinstance(x, dict) and x.get('tag') == tag and x.get('why') == 'memory' and float(x.get('t') or 0) >= t0 for x in L)


def main(argv):
    a = argv[1:]
    env = dict(os.environ)
    while a and a[0] != '--':
        if a[0] == '--label' and len(a) > 1: env['KPC_MEM_LABEL'] = a[1]; a = a[2:]
        else: break
    if a and a[0] == '--': a = a[1:]
    if not a:
        print('usage: kpc_mem_guard.py [--label TEXT] -- COMMAND ...', file=sys.stderr); return 2
    return run(a, env)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
