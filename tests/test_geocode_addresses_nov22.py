#!/usr/bin/env python3
"""22 Nov 2026 (owner 10:26 PM: "run the address through a script one time and convert it into some format the matching tool
could use"): the PC address converter splits US street addresses, never sends a mailbox or a Canadian address, adds each
matched point once as a page point with the address's role, and asks for each address only once. No network."""
import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
r = subprocess.run([sys.executable, '-I', str(ROOT / '.github/scripts/pc/kpc_geocode_addresses.py'), '--selftest'], capture_output=True, text=True)
ok = r.returncode == 0 and 'ALL PASS' in r.stdout
print(('PASS ' if ok else 'FAIL ') + 'addresses become page points once, with their role; mailboxes and Canada are never sent')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
