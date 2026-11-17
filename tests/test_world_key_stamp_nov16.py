#!/usr/bin/env python3
"""KPC owner, 2026-11-16: the world key's build stamp reaches the waiting room.

The waiting room's file list took EVERY .json of data/us-key and data/ca-key, so those keys' index.json (the build stamp:
build id, build time, rules hash) was held with their country files. The world rule took two-letter country files only, so
data/world-key/index.json matched nothing and was never held. Two things followed:
  * every world KEY YES read 'NONE (no build stamp: a YES cannot name a build yet)';
  * the supersede test needs a held build id, so it could never replace a superseded world build, and held world country
    files piled up from different builds on different rules (on 2026-11-16, 29 of 83 matched neither the live key nor the
    current build).
The world rule files (layers.json, overrides.json, area-tables.json) must stay OUT: area-tables.json is part of the world
rules hash, and none of them is a key.

Run:  python3 tests/test_world_key_stamp_nov16.py
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_waiting_room as W  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg)


kind = lambda p: W.kind_of(p)[0]

check("the world key's build stamp is held like a key file", kind('data/world-key/index.json') == 'key')
check('and it is checked by the same checker as the US and Canada stamps',
      W.kind_of('data/world-key/index.json')[1] is W.kind_of('data/us-key/index.json')[1]
      is W.kind_of('data/ca-key/index.json')[1])
check('world country files are unchanged', kind('data/world-key/AU.json') == 'key' and kind('data/world-key/GB.json') == 'key')
check('the world RULE files stay out (area-tables.json is part of the world rules hash)',
      [kind(f'data/world-key/{f}') for f in ('layers.json', 'overrides.json', 'area-tables.json', 'eea-designations.json')] == [None] * 4)
check('a path that is not a world key file is still nothing', kind('data/world-key/review/AU.md') is None)

# the checker must cope with an index.json: it is now run on one, and a crash there would stop the divert
fn = W.kind_of('data/world-key/index.json')[1]
try:
    live = json.loads((ROOT / 'data/world-key/index.json').read_text(encoding='utf-8'))
    new = subprocess.run(['git', '-C', str(ROOT.parent / 'kpc-links'), 'show', 'HEAD:data/world-key/index.json'],
                         capture_output=True, text=True).stdout
    new = json.loads(new) if new.strip() else dict(live)
    why, _ = fn('data/world-key/index.json', new, live, {})
    check(f'the key checker reads a world index.json without stopping ({"held: " + str(why[0])[:60] if why else "passes"})', True)
except Exception as e:  # noqa: BLE001
    check(f'the key checker reads a world index.json without stopping ({type(e).__name__}: {str(e)[:90]})', False)

# a stamp carries what a YES needs to name
try:
    st = json.loads((ROOT / 'data/world-key/index.json').read_text(encoding='utf-8'))
    check(f"the stamp names a build and the rules it was built on ({st.get('build')}, rules {st.get('rules')})",
          bool(st.get('build')) and bool(st.get('rules')))
except Exception as e:  # noqa: BLE001
    check(f'the stamp could not be read ({type(e).__name__})', False)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
