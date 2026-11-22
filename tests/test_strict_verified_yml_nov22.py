#!/usr/bin/env python3
"""F6 (22 Nov 2026): the key review packet runs kpc_key_factcheck.py with --strict-verified
on every run (old and new keys, both jobs). Fail without the four flags in the workflow.
Run: python3 -B tests/test_strict_verified_yml_nov22.py
"""
import pathlib, re, sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent.parent
WF = ROOT / '.github/workflows/kpc-key-review-packet.yml'
text = WF.read_text(encoding='utf-8')

FAILS = []


def check(ok, what):
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if not ok:
        FAILS.append(what)


# a "run" invocation, not help / other subcommands
runs = [ln for ln in text.splitlines() if 'kpc_key_factcheck.py' in ln and re.search(r'\brun\b', ln)]
check(len(runs) == 4, f'the workflow has four kpc_key_factcheck.py run calls ({len(runs)})')
missing = [ln.strip() for ln in runs if '--strict-verified' not in ln]
check(not missing, f'every run call passes --strict-verified ({len(missing)} missing)')
# the flag sits on the run itself, not only in a comment
check(all(re.search(r'kpc_key_factcheck\.py"\s+run\s+--strict-verified\s+--keys', ln) for ln in runs),
      'each run line is: kpc_key_factcheck.py run --strict-verified --keys ...')

print(f'{len(FAILS)} failed' if FAILS else 'ALL PASS')
sys.exit(1 if FAILS else 0)
