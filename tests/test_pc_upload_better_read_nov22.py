#!/usr/bin/env python3
"""22 Nov 2026 (owner 7:10 PM "Yeah"): the PC upload merge takes the PC's read of a park unless it is weaker than the one on file:
a PC read that came back busy, refused, dead or garbled never replaces a real page read; a real PC read replaces a busy or
refused one; two reads of the same strength: the newer wins. Invented parks. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_pc_upload as U  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def f(kind, read, name='Invented Ridge State Park'):
    return {'page': {'kind': kind, 'read': read}, 'name': {'heading': name}}


check('a real PC read replaces a busy one on file', U.better_read(f('resting', '2026-11-22'), f('html', '2026-11-21')))
check('a real PC read replaces a refused one on file', U.better_read(f('refused', '2026-11-20'), f('pdf', '2026-11-21')))
check('a PC read that got nothing never replaces a real page read', not U.better_read(f('html', '2026-11-10'), f('refused', '2026-11-22')))
check('a garbled PC name never replaces a clean one', not U.better_read(f('html', '2026-11-10'), f('html', '2026-11-22', 'hþéÿåîèêá')))
check('a clean PC name replaces a garbled one', U.better_read(f('html', '2026-11-22', 'þéÿåîèêá'), f('html', '2026-11-20')))
check('same strength: the newer read wins', U.better_read(f('html', '2026-11-10'), f('html', '2026-11-21')))
check('same strength: an older PC read does not replace a newer one', not U.better_read(f('html', '2026-11-22'), f('html', '2026-11-21')))
check('nothing on file: the PC read is taken', U.better_read(None, f('resting', '2026-11-21')))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
