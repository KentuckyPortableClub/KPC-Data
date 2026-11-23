#!/usr/bin/env python3
"""22 Nov 2026 (owner: "just a script to run and pull everyone we need just the address or gps"): the PC address puller reads
only the own pages that gave no place, fills the address / point / directions, keeps every other fact, and reads each park
once. Invented pages, no network."""
import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
r = subprocess.run([sys.executable, '-I', str(ROOT / '.github/scripts/pc/kpc_pull_location.py'), '--selftest'], capture_output=True, text=True)
ok = r.returncode == 0 and 'ALL PASS' in r.stdout
print(('PASS ' if ok else 'FAIL ') + 'the address puller fills only the place facts, once per park, and leaves list pages alone')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
