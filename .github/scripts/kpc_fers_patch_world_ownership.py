#!/usr/bin/env python3
"""Nov 8: patch Links kpc_fers.py ownership_step world branch so designations-only pairs are NOT mass-marked
'not sure: no park here owns land' when no land register exists for that country.

Before (Nov 6): world + no fee owners → always 'not sure' → W-AU run 42451234481 produced 1,255 such rows and 0 candidates
(was 528). After: designations-only with no '?' → 'ok' with an explicit 'ownership not checked' note (geometry 2-fer stands
until a land register exists). Owners that differ or are unknown still return not sure.

Usage: python3 kpc_fers_patch_world_ownership.py [path/to/kpc_fers.py]
Idempotent. Exit 0 if patched or already patched; 1 if the expected block is missing.
"""
import pathlib, sys

OLD = """    if REGION == 'world':
        if real and len(set(real.values())) <= 1 and '?' not in owners.values(): return 'ok', 'one owner (or designations on it): layered'
        return 'not sure', ('owners differ' if real else 'no park here owns land (designations only)') + '; no land register read for this country yet'
"""

NEW = """    if REGION == 'world':
        if real and len(set(real.values())) <= 1 and '?' not in owners.values(): return 'ok', 'one owner (or designations on it): layered'
        # Nov 8 (Data patch / Brandon t802u): no land register yet → do NOT mass-drop designations-only overlaps.
        if not real and '?' not in owners.values():
            return 'ok', 'designations only; no land register read for this country yet (ownership not checked)'
        return 'not sure', ('owners differ' if real else 'owner unknown') + '; no land register read for this country yet'
"""


def main(argv):
    path = pathlib.Path(argv[1] if len(argv) > 1 else '.github/scripts/kpc_fers.py')
    if not path.exists():
        print(f'::error title=world ownership patch::{path} not found')
        return 1
    text = path.read_text(encoding='utf-8')
    if NEW in text:
        print(f'::notice title=world ownership patch::{path} already patched')
        return 0
    if OLD not in text:
        print(f'::error title=world ownership patch::expected world ownership_step block not found in {path} (Links changed?)')
        return 1
    path.write_text(text.replace(OLD, NEW, 1), encoding='utf-8', newline='\n')
    print(f'::notice title=world ownership patch::patched {path}: designations-only world pairs stay ok until a land register exists')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
