#!/usr/bin/env python3
"""Nov 16 2026 (KPC owner): the memory guard must run on Windows, because the owner's PC runs the 2-fers now.

What went wrong: the guard started the child with preexec_fn and start_new_session, which are Linux only. On the PC every one
of the 65 areas died in the first second with "ValueError: preexec_fn is not supported on Windows platforms", and the summary
then read "3121 same, 0 new" because nothing had been measured at all.

These tests do not need Windows: they feed the Windows readers the text Windows gives and check what the guard does with it,
and they check that the Linux road is unchanged.
"""
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_mem_guard as G  # noqa: E402

FAIL = []


def ok(cond, what):
    print(('PASS ' if cond else 'FAIL ') + what)
    if not cond:
        FAIL.append(what)


class Out:
    def __init__(self, text, code=0):
        self.stdout, self.stderr, self.returncode = text, '', code


def with_fake_powershell(text, fn, *a, **k):
    """run fn with subprocess.run answering like PowerShell, and the snapshot cleared"""
    real = subprocess.run
    G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}
    subprocess.run = lambda *x, **y: Out(text)
    try:
        return fn(*a, **k)
    finally:
        subprocess.run = real
        G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}


# Win32_Process as the guard asks for it: pid, parent pid, working set bytes
PS = """4 0 1048576
900 4 20971520
1000 900 104857600
1001 1000 524288000
1002 1000 1048576000
2000 4 8388608
"""


def main():
    # ---- the readers
    procs = with_fake_powershell(PS, G.win_processes)
    ok(procs.get(1001) == (1000, 524288000), 'win_processes reads pid, parent and working set')
    ok(len(procs) == 6, f'win_processes reads every line ({len(procs)})')

    pids, info = with_fake_powershell(PS, G.win_tree, 1000)
    ok(pids == {1000, 1001, 1002}, f'win_tree takes the child and its children, nothing else ({sorted(pids)})')
    ok(info[1001][0] == 1000, 'win_tree keeps the parent in the shape the Linux side uses')
    ok(round(with_fake_powershell(PS, G.win_rss_mb, pids)) == 1600, 'win_rss_mb adds the tree up (100 + 500 + 1000 MB)')

    pids2, _ = with_fake_powershell(PS, G.win_tree, 900)
    ok(pids2 == {900, 1000, 1001, 1002}, 'win_tree follows grandchildren')

    ok(with_fake_powershell('', G.win_processes) == {}, 'no answer from Windows is an empty list, never a crash')

    def boom(*a, **k):
        raise OSError('powershell is not there')
    real = subprocess.run
    G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}
    subprocess.run = boom
    try:
        ok(G.win_processes() == {}, 'PowerShell missing is an empty list, never a crash')
    finally:
        subprocess.run = real
        G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}

    # the snapshot is kept for a moment, so one sample asks Windows once
    calls = []
    subprocess.run = lambda *x, **y: (calls.append(1), Out(PS))[1]
    G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}
    try:
        G.win_processes(); G.win_processes(); G.win_processes()
        ok(len(calls) == 1, f'three reads in the same moment ask Windows once ({len(calls)})')
    finally:
        subprocess.run = real
        G._WIN_SNAP['t'], G._WIN_SNAP['procs'] = 0.0, {}

    # ---- the start: Windows must not get preexec_fn, Linux must keep it
    seen = {}
    real_popen = subprocess.Popen

    class P:
        def __init__(s, cmd, **kw):
            seen.clear(); seen.update(kw); s.pid = 4242; s._n = 0

        def poll(s):
            s._n += 1
            return 0 if s._n > 1 else None

    was = G.WINDOWS
    subprocess.Popen = P
    try:
        G.WINDOWS = True
        code = G.run(['anything'], env={'KPC_MEM_GUARD': 'off', 'KPC_MEM_GUARD_SAMPLE_S': '0'},
                     read_system=lambda: (16000.0, 9000.0, 0.0), read_rss=lambda p: 10.0)
        ok('preexec_fn' not in seen, 'on Windows the child is started without preexec_fn')
        ok('start_new_session' not in seen, 'on Windows the child is started without start_new_session')
        ok(seen.get('creationflags', 0) == getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0),
           'on Windows the child gets its own process group flag')
        ok(code == 0, f'the child\'s own exit code still comes back ({code})')

        G.WINDOWS = False
        G.run(['anything'], env={'KPC_MEM_GUARD': 'off', 'KPC_MEM_GUARD_SAMPLE_S': '0'},
              read_system=lambda: (16000.0, 9000.0, 0.0), read_rss=lambda p: 10.0)
        ok('preexec_fn' in seen and seen.get('start_new_session') is True,
           'on Linux nothing changed: preexec_fn and its own session')
    finally:
        subprocess.Popen = real_popen
        G.WINDOWS = was

    # ---- the readers that Linux has and Windows has not
    G.WINDOWS = True
    try:
        ok(G.pressure() is None, 'memory pressure is simply not reported on Windows')
        ok(G.oom_kills() is None, 'there is no out-of-memory count to read on Windows')
        ok(G.what_pass({1}) == '', 'the pass is not read out of another process on Windows')
    finally:
        G.WINDOWS = was

    # ---- the limits do not care which machine this is
    lim, floor = G.limits(16000.0, env={})
    ok(abs(lim - 11200.0) < 1 and abs(floor - 1920.0) < 1,
       f'on a 16 GB machine: stop at {lim:,.0f} MB, floor {floor:,.0f} MB')

    print('ALL PASS' if not FAIL else f'{len(FAIL)} FAILED')
    return 1 if FAIL else 0


if __name__ == '__main__':
    raise SystemExit(main())
