#!/usr/bin/env python3
"""21 Nov 2026: a page with a long run of digits and commas ('1,2,3,...') hung the park page reader for 20 minutes inside the
size-sum pattern of kpc_truth_bot (it could split the run in 2**n ways). The run must now be read in well under a second, and
ordinary size sentences must read exactly as before. Invented text only. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


code = ("import sys; sys.path.insert(0, sys.argv[1]); import kpc_truth_bot as TB\n"
        "t = 'Data ' + '1,' * 40 + 'x and 5 acres. The park covers 1,234 acres.'\n"
        "print(sorted(r['acres'] for r in TB.sizes_in(t, 'Invented Park')))\n")
try:
    r = subprocess.run([sys.executable, '-B', '-c', code, str(ROOT / '.github/scripts')], capture_output=True, text=True, timeout=20)
    done, out = r.returncode == 0, r.stdout.strip()
except subprocess.TimeoutExpired:
    done, out = False, 'timed out'
check(f'a page with a 40-comma digit run is read in seconds, not hours ({out})', done and '1234.0' in out)

import kpc_truth_bot as TB  # noqa: E402
def sums(t):
    return [(r['acres'], r['as']) for r in TB.sizes_in(t, 'Invented Park') if r.get('why') in ('sum of the pieces named in one sentence', 'history')]
check('two lakes of 40 and 60 acres: one sum of 100', sums('The park has two lakes of 40 and 60 acres.') == [(100.0, '40 + 60 acres')])
check('1,234 and 5,678 acres: one sum with thousands commas', sums('Two tracts of 1,234 and 5,678 acres.') == [(6912.0, '1234 + 5678 acres')])
check('10, 20, and 30 acres: the comma before "and" still reads', sums('Fields of 10, 20, and 30 acres.') == [(60.0, '10 + 20 + 30 acres')])
check('12 acres, 30 acres and 1,000 acres: one sum', sums('Tracts of 12 acres, 30 acres and 1,000 acres.') == [(1042.0, '12 + 30 + 1000 acres')])
check('a number with three thousands commas is never touched', TB.sum_scan_text('It covers 1,234,567,890 acres') == 'It covers 1,234,567,890 acres')
check('the scanned copy keeps every position', len(TB.sum_scan_text('a ' + '1,' * 30 + ' b')) == len('a ' + '1,' * 30 + ' b'))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
