#!/usr/bin/env python3
"""23 Nov 2026 (owner 2:15 PM, a screenshot: "The system cannot find the path specified ... Python was not found"): two PC batch
files went out with a Linux path where Windows needs its null device, so the Python check failed on his PC. Every batch file
for the PC must use Windows line ends and Windows paths only. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


bats = sorted((ROOT / '.github/scripts/pc').glob('*.bat'))
check('there are PC batch files', len(bats) >= 5)
for b in bats:
    raw = b.read_bytes()
    check(f'{b.name}: no Linux path (/dev/, /tmp/, /home/)', not any(x in raw for x in (b'/dev/', b'/tmp/', b'/home/')))
    check(f'{b.name}: Windows line ends only', raw.count(b'\n') == raw.count(b'\r\n'))
    check(f'{b.name}: starts with @echo off', raw.lstrip(b'\xef\xbb\xbf').lower().startswith(b'@echo off'))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
