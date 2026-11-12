#!/usr/bin/env python3
"""kpc_chain.py (Nov 11 2026, fewer runs): the ONE rule for a bot that continues its own backlog by starting its next run.
The hard look reader and the outside documents merge used to start themselves again 'until drained' (570 and 597 runs in two
weeks, mostly self-starts): a row that could not be read this run (a host resting, robots.txt not readable) kept the backlog
above zero for ever, so every run started another one that read nothing. Now one run works through the backlog under a time
budget, and it starts ONE more run only when ALL of these hold:
  * rows are left (LEFT > 0, and LEFT could be read);
  * this run made progress (DONE > 0: at least one row got a final answer or one more try);
  * the chain is under its cap (CHAIN < CAP; CHAIN is the workflow input passed along the chain, 0 for a cron / by-hand start);
  * fewer than BRAKE runs of this workflow started in the last 24 h (RUNS24; a count that could not be read = no next run);
  * the bot is not paused (PAUSED=1).
Otherwise it stops and says why in one line ('backlog N left, cap reached ...'); the bot's own daily timer (NEXT_BY) goes on.
CLI: python3 kpc_chain.py '<bot name>'  (env LEFT, DONE, CHAIN, CAP, RUNS24, BRAKE, PAUSED, NEXT_BY) prints the line as a
::notice (::warning when paused), adds it to the job summary, prints NEXT=yes|no and CHAIN=<next value> (and writes next= /
chain= to GITHUB_OUTPUT).
Standard library only. Never fails (exit 0)."""
import os, sys


def _int(x):
    try: return int(str(x).strip())
    except (TypeError, ValueError): return None


def decide(left, done, chain, cap, runs24=None, brake=None, paused=False, next_by='the daily timer continues tomorrow'):
    """-> (go, next_chain, line). go=True means: start one more run with input chain=next_chain."""
    left, done, chain, cap = _int(left), _int(done), _int(chain) or 0, _int(cap)
    cap = 3 if cap is None else cap
    if left is None: return False, chain, f'could not read how many rows are left: no next run ({next_by})'
    if left <= 0: return False, chain, 'backlog drained: nothing left, no next run'
    if paused: return False, chain, f'backlog {left} left, but this bot is PAUSED: no next run (start it by hand if it is needed)'
    if not done: return False, chain, f'backlog {left} left, no progress this run (every row left waits on a host or a person): no next run ({next_by})'
    if chain >= cap: return False, chain, f'backlog {left} left, cap reached ({chain} of {cap} continuations in this chain): no next run ({next_by})'
    if brake is not None:
        r = _int(runs24)
        if r is None: return False, chain, f'backlog {left} left, could not count this bot\'s runs of the last 24 h: no next run (fail closed; {next_by})'
        if r >= _int(brake): return False, chain, f'backlog {left} left, {r} runs in 24 h (brake {brake}): no next run ({next_by})'
    return True, chain + 1, f'backlog {left} left, {done} row(s) done this run: starting continuation {chain + 1} of {cap}'


def main(argv):
    name = (argv[1] if len(argv) > 1 else 'Chain').replace('::', ':')
    e = os.environ.get
    go, nxt, line = decide(e('LEFT'), e('DONE'), e('CHAIN'), e('CAP'), e('RUNS24'), e('BRAKE') or None,
                           (e('PAUSED') or '').strip().lower() in ('1', 'yes', 'true'), e('NEXT_BY') or 'the daily timer continues tomorrow')
    kind = 'warning' if 'PAUSED' in line else 'notice'
    print(f'::{kind} title={name}: next run::{line}', flush=True)
    print(f"NEXT={'yes' if go else 'no'}\nCHAIN={nxt}", flush=True)
    try:
        if e('GITHUB_STEP_SUMMARY'): open(e('GITHUB_STEP_SUMMARY'), 'a', encoding='utf-8').write(f'- {name}: {line}\n')
        if e('GITHUB_OUTPUT'): open(e('GITHUB_OUTPUT'), 'a', encoding='utf-8').write(f"next={'yes' if go else 'no'}\nchain={nxt}\n")
    except OSError: pass
    return 0


if __name__ == '__main__':
    try: sys.exit(main(sys.argv))
    except Exception as ex: print(f'::warning title=Chain::stopped ({type(ex).__name__}): no next run\nNEXT=no', flush=True); sys.exit(0)  # noqa: BLE001
