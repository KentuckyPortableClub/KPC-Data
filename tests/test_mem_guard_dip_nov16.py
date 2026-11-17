#!/usr/bin/env python3
"""KPC owner, 2026-11-16: a passing dip in the MACHINE's free memory no longer throws away a healthy run.

The owner's PC run of 2026-11-16 finished 24 of 41 areas. The other 17 were stopped by the guard while the 2-fer tree held
421 MB to 4,881 MB of an 11,373 MB limit: what fired every time was the machine's free memory dipping under the floor for a
moment. US-MI was asked to stop with 1,758 MB free and force-killed 31 s later with 3,195 MB free, holding 421 MB.

Two changes, both only for the MACHINE floor (the tree's own size still acts at once, and so does under half the floor):
  * the dip must HOLD for KPC_MEM_GUARD_FLOOR_HOLD_S (20 s) before the run is asked to stop;
  * if the machine is back above the floor when the grace period ends and the run is still going, the stop is called off.

Run:  python3 tests/test_mem_guard_dip_nov16.py
"""
import importlib.util, io, pathlib, sys, contextlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mg', ROOT / '.github/scripts/kpc_mem_guard.py')
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + msg)


class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): self.t += 2.0; return self.t


def go(avails, rss=421.0, env=None, cmd=None):
    """Run the guard over a scripted list of 'machine free MB' readings. -> (exit code, log)."""
    seq = list(avails); clock = Clock()
    e = {'KPC_MEM_GUARD_SAMPLE_S': '0', 'KPC_MEM_GUARD_BEAT_S': '100000', 'KPC_MEM_GUARD_GRACE_S': '30',
         'KPC_MEM_LABEL': 'US-MI pass 1'}
    e.update(env or {})
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = G.run(cmd or [sys.executable, '-c', 'import time; time.sleep(0.6)'], env=e,
                   read_system=lambda: (16247.0, (seq.pop(0) if seq else 9000.0), 0.0),
                   read_rss=lambda p: rss, now=clock)
    return rc, out.getvalue()


FLOOR = G.limits(16247.0, {})[1]
check(f'the floor on a 16 GB machine is {FLOOR:,.0f} MB', 1900 < FLOOR < 2000)

# US-MI: free memory dips under the floor for ~6 s, then recovers well above it
rc, log = go([3000.0, 1758.0, 1800.0, 1900.0, 3195.0, 3200.0, 3200.0, 3200.0])
check(f'a dip of a few seconds no longer stops the run (exit {rc})', rc == 0 and 'asking it to stop' not in log)

# a real, sustained shortage still stops it
rc, log = go([1500.0] * 40)
check(f'a shortage that holds does stop the run (exit {rc})', rc == G.STOP_CODE and 'asking it to stop' in log)

# an emergency (under half the floor) still acts at once, without waiting out the hold
rc, log = go([800.0] * 40)
check(f'under half the floor still acts at once (exit {rc})', rc == G.STOP_CODE and 'asking it to stop' in log)

# the tree's OWN size is the run's doing: it still acts at once, with plenty of machine memory free
rc, log = go([9000.0] * 40, rss=12000.0)
check(f'the tree passing its own limit still stops at once (exit {rc})', rc == G.STOP_CODE and 'passed' in log)

# the stop is called off when the machine recovers before the grace period ends and the run is still going
slow = [sys.executable, '-c', 'import time; time.sleep(30)']
rc, log = go([1500.0] * 12 + [9000.0] * 60, env={'KPC_MEM_GUARD_GRACE_S': '4'}, cmd=slow)
check('a stop is called off when the machine recovers and the run is still going', 'called off' in log)
check('and that run is not killed', 'killed (' not in log)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
