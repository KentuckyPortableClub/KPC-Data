#!/usr/bin/env python3
"""Remove keys / tokens saved inside link text in data/docs/*.json (G3, Nov 2 2026). Dry run by default: lists what would change;
--write rewrites the files with the documents bot's own scrub (kpc_docs_bot.scrub). Usage: scrub_docs_keys.py <repo root> [--write]"""
import glob, os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.path.insert(0, os.path.join(root, '.github/scripts'))
from kpc_docs_bot import scrub  # noqa: E402
n = 0
for f in sorted(glob.glob(os.path.join(root, 'data/docs/*.json'))):
    t = open(f, encoding='utf-8').read(); u = scrub(t)
    if u != t:
        n += 1; print(f'{f}: {t.count("AIza")} Google key(s), {len(t) - len(u)} characters removed')
        if '--write' in sys.argv: open(f, 'w', encoding='utf-8').write(u)
print(f'{n} file(s) {"cleaned" if "--write" in sys.argv else "would change (dry run)"}')
