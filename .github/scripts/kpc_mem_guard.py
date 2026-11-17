#!/usr/bin/env python3
"""Memory guard for the 2-fer steps (KPC owner, 2026-11-12; fetcher of run 43205747757: pass 1 peaked at 6,973 MB, pass 2 printed
nothing for 30 minutes and the runner got a shutdown signal; the whole southeast line was lost).

    python3 kpc_mem_guard.py [--label TEXT] -- COMMAND ...
    shell: python3 kpcdata/.github/scripts/kpc_mem_guard.py -- bash -e {0}      (a workflow step's own shell: the whole step is guarded)

Runs COMMAND as a child (its own process group) and watches it from OUTSIDE, standard library only. It reads Linux /proc when
it runs on Linux and asks Windows itself when it runs on Windows (KPC owner, 2026-11-16: the owner's PC runs the 2-fers now, and
this guard used preexec_fn, which Windows has not got, so every one of the 65 areas stopped before it started):
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
  - on Windows: the memory figures come from GlobalMemoryStatusEx and the tree from Win32_Process (working set), the child is
    started in its own process group, a stop is asked for with taskkill and then forced with taskkill /F, and there is no kernel
    backstop to lean on (Windows has none), so the floor does the work. Everything else reads the same.
  - the kernel backstop (Linux): the child (and everything it starts) gets oom_score_adj 1000, so if a spike between two samples empties the
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
WINDOWS = os.name == 'nt'


# ---------------------------------------------------------------- Windows (KPC owner, 2026-11-16)
def win_system():
    """(total MB, available MB, swap used MB) from Windows itself. GlobalMemoryStatusEx needs nothing installed."""
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
    m = MS(); m.dwLength = ctypes.sizeof(MS)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        return 0.0, 0.0, 0.0
    phys_used = m.ullTotalPhys - m.ullAvailPhys
    page_used = m.ullTotalPageFile - m.ullAvailPageFile
    return m.ullTotalPhys / MB, m.ullAvailPhys / MB, max(0.0, (page_used - phys_used) / MB)


_WIN_SNAP = {'t': 0.0, 'procs': {}}


def win_processes(ttl=1.0, now=time.monotonic):
    """{pid: (ppid, working set bytes)} for every process, kept for `ttl` seconds so one sample asks Windows once."""
    if now() - _WIN_SNAP['t'] < ttl and _WIN_SNAP['procs']:
        return _WIN_SNAP['procs']
    cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command',
           'Get-CimInstance Win32_Process | ForEach-Object '
           '{ "{0} {1} {2}" -f $_.ProcessId, $_.ParentProcessId, $_.WorkingSetSize }']
    out = ''
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout or ''
    except Exception:  # noqa: BLE001  the guard must never be what stops a run
        pass
    procs = {}
    for ln in out.splitlines():
        bits = ln.split()
        if len(bits) == 3:
            try: procs[int(bits[0])] = (int(bits[1]), int(bits[2]))
            except ValueError: continue
    if procs:
        _WIN_SNAP['t'], _WIN_SNAP['procs'] = now(), procs
    return procs


def win_tree(root):
    """(pids of root and every descendant, {pid: (ppid, 0, 'R', 0)} in the shape the Linux side uses)"""
    procs = win_processes()
    kids = {}
    for pid, (ppid, _rss) in procs.items(): kids.setdefault(ppid, []).append(pid)
    out, todo = set(), [root]
    while todo:
        p = todo.pop()
        if p in out: continue
        out.add(p); todo += kids.get(p, [])
    return out, {p: (procs[p][0], 0, 'R', 0) for p in out if p in procs}


def win_rss_mb(pids):
    procs = win_processes()
    return sum(procs[p][1] for p in pids if p in procs) / MB


def win_stop(pid, hard=False):
    """Ask the whole tree to stop (taskkill), or force it (taskkill /F). Windows has no SIGINT to send to a group."""
    cmd = ['taskkill', '/PID', str(pid), '/T'] + (['/F'] if hard else [])
    try: subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception: pass  # noqa: BLE001


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
    if WINDOWS: return win_system()
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
    if WINDOWS: return win_tree(root)
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
    if WINDOWS: return win_rss_mb(pids)
    t = 0
    for p in pids:
        try: t += int(open(f'/proc/{p}/statm').read().split()[1])
        except (OSError, ValueError, IndexError): pass
    return t * PAGE / MB


def pressure():
    """'some avg10' of /proc/pressure/memory (percent of time tasks waited on memory), or None. Windows has no such figure."""
    if WINDOWS: return None
    try:
        for ln in open('/proc/pressure/memory'):
            if ln.startswith('some'):
                return float(dict(x.split('=') for x in ln.split()[1:])['avg10'])
    except (OSError, KeyError, ValueError): return None
    return None


def oom_kills():
    if WINDOWS: return None   # Windows has no out-of-memory killer to count
    try:
        for ln in open('/proc/vmstat'):
            if ln.startswith('oom_kill '): return int(ln.split()[1])
    except (OSError, ValueError): pass
    return None


def what_pass(pids):
    """'pass 2' when a process in the tree runs with PASS=2 in its environment (kpc_fers.py), else ''. Linux only: on Windows a
    process's environment is not readable from outside without more privilege than this guard asks for, and the runner already
    names the pass in the log file it writes to."""
    if WINDOWS: return ''
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
    # Windows is asked through one PowerShell call a sample, so it is read a little less often than Linux /proc
    sample = sample if sample is not None else _num(env.get('KPC_MEM_GUARD_SAMPLE_S'), 5.0 if WINDOWS else 2.0)
    beat = beat if beat is not None else _num(env.get('KPC_MEM_GUARD_BEAT_S'), 60.0)
    grace = grace if grace is not None else _num(env.get('KPC_MEM_GUARD_GRACE_S'), 30.0)
    # KPC owner, 2026-11-16 (the owner's PC, run of 2026-11-16: 17 of 41 areas were stopped while the 2-fer tree held 421 to 4,881 MB
    # of an 11,373 MB limit; what fired was the MACHINE's free memory dipping under the floor for a moment). The machine's free memory
    # is other programs' business and bounces: a dip must HOLD for this long before the run is asked to stop. The tree's own size
    # (rss > lim) is the run's own doing and still acts at once, and so does a real emergency (under half the floor).
    floor_hold = _num(env.get('KPC_MEM_GUARD_FLOOR_HOLD_S'), 20.0)
    cancels_left = int(_num(env.get('KPC_MEM_GUARD_CANCELS'), 2.0))
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
    if WINDOWS:
        # Windows has no preexec_fn and no process groups to signal: its own group flag, and taskkill /T for the tree.
        p = subprocess.Popen(cmd, creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
    else:
        p = subprocess.Popen(cmd, preexec_fn=pre, start_new_session=True)
    pgid = p.pid

    def fwd(sig, _f):   # the runner cancels a step with SIGINT / SIGTERM to this process: pass it on to the guarded child
        if WINDOWS: win_stop(pgid, hard=False)
        else:
            try: os.killpg(pgid, sig)
            except OSError: pass
    for s in (signal.SIGINT, signal.SIGTERM):
        try: signal.signal(s, fwd)
        except (ValueError, OSError, AttributeError): pass

    peak, last_beat, cpu0, stop, stop_t, killed, why = 0.0, t0, None, None, None, False, ''
    # KPC owner, 2026-11-16: when the machine first fell under the floor, and whether the stop was the tree's own size
    low_since, stop_rss = None, False
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
            # Windows does not hand the CPU seconds of a tree to this guard, so the line leaves that out rather than printing 0
            used = '' if (cpu0 is None or WINDOWS) else f', CPU {cpu - cpu0:.0f} s in the last {t - last_beat:.0f} s'
            states = ''.join(sorted({info[q][2] for q in pids if q in info}))
            psi = pressure()
            say(f'memory guard: {name} {what_pass(pids)}'.rstrip() + f': {(t - t0) / 60:.0f} min, RSS {fmt(rss)} MB ({len(pids)} processes, '
                f'state {states or "-"}), peak {fmt(peak)} MB, machine available {fmt(avail)} of {fmt(total)} MB, swap used {fmt(swap)} MB'
                + (f', memory pressure {psi:.0f} %' if psi is not None else '') + used + f'; limit {fmt(lim)} MB, floor {fmt(floor)} MB')
            cpu0, last_beat = cpu, t
        if on and stop is None and avail >= floor: low_since = None
        if on and stop is None and avail < floor and low_since is None: low_since = t
        _low_held = low_since is not None and t - low_since >= floor_hold
        if on and stop is None and (rss > lim or (avail < floor and (_low_held or avail < floor / 2))):
            why = (f'the step passed {fmt(lim)} MB' if rss > lim else f'the machine had only {fmt(avail)} MB left (floor {fmt(floor)} MB)')
            stop = (rss, avail, what_pass(pids)); stop_t = t; stop_rss = rss > lim
            how = 'taskkill' if WINDOWS else 'SIGINT'
            say(f'memory guard: {name}: {why} (RSS {fmt(rss)} MB): asking it to stop ({how}), hard stop in {grace:.0f} s')
            if WINDOWS:
                win_stop(pgid, hard=False)
            else:
                try: os.killpg(pgid, signal.SIGINT)
                except OSError: pass
                for q in pids:
                    try: os.kill(q, signal.SIGINT)
                    except OSError: pass
        elif (stop is not None and not killed and not stop_rss and cancels_left > 0
              and t - stop_t >= grace and avail >= floor and rss <= lim):
            # KPC owner, 2026-11-16: it was asked to stop because the MACHINE was short, the machine is fine again and the run is
            # still going (on Windows a soft taskkill often does not reach a console program at all). Killing it now would throw
            # away a healthy area for a dip that has passed: US-MI was killed at 421 MB with 3,195 MB free.
            say(f'memory guard: {name}: the machine is back above the floor ({fmt(avail)} MB, floor {fmt(floor)} MB) and the run is '
                f'still going: the stop is called off ({cancels_left} left)')
            stop = None; stop_rss = False; low_since = None; cancels_left -= 1
        elif stop is not None and not killed and (t - stop_t >= grace or avail < floor / 2):
            say(f'memory guard: {name}: still running {t - stop_t:.0f} s after the request (available {fmt(avail)} MB): '
                f'killed ({"taskkill /F" if WINDOWS else "SIGKILL"})')
            killed = True
            if WINDOWS:
                win_stop(pgid, hard=True)
            else:
                for q in pids:
                    try: os.kill(q, signal.SIGKILL)
                    except OSError: pass
                try: os.killpg(pgid, signal.SIGKILL)
                except OSError: pass
        time.sleep(sample)
    # nothing of the guarded group may outlive it (a grandchild whose parent already exited)
    left, _ = tree(p.pid, pgid)
    if WINDOWS:
        if left - {p.pid}: win_stop(pgid, hard=True)
    else:
        for q in left - {p.pid}:
            try: os.kill(q, signal.SIGKILL)
            except OSError: pass
    code = rc if rc >= 0 else 128 - rc
    oom1 = oom_kills()
    if stop is None and rc == -getattr(signal, 'SIGKILL', 9) and oom0 is not None and oom1 is not None and oom1 > oom0:
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
    # Nov 13 (KPC owner): "the same cut" means the same states. When the line has been cut smaller since the stop (fers-areas.json
    # now lists other states under this tag), the old stop no longer holds it back. A stop with no states on record, or a tag
    # that is not an area name, counts as before.
    cur = None
    try: cur = (json.load(open(os.path.join(data, '.github/fers-areas.json'), encoding='utf-8')).get('areas') or {}).get(tag)
    except (OSError, ValueError, AttributeError): cur = None
    def same_cut(x):
        st = x.get('states')
        return not (isinstance(st, str) and st.split() and isinstance(cur, str) and cur.split()) or set(st.split()) == set(cur.split())
    return any(isinstance(x, dict) and x.get('tag') == tag and x.get('why') == 'memory' and float(x.get('t') or 0) >= t0 and same_cut(x) for x in L)


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
