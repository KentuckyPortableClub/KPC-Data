#!/usr/bin/env python3
"""START THE GIS HUNTER WHEN ITS INPUTS CHANGE (chat 10, Oct 30 2026; Brandon 11:50 PM: '1 and 3' = the hunter starts itself after
every map rebuild and after a new layer is approved). Run by the daily copy. The hunter's work depends on: the US key's why-not
list + the state layer list (data/state-gis.json, where approved layers land) for the US; the Canada key files + the Canada Fable
pool for Canada. A changed fingerprint (vs data/gis-hunter/seen.json) = one full pass of that country (US first, then Canada when
both changed). Prints the gh command line to run, or nothing. Never fails.
  LINKS=links python3 kpc_hunter_trigger.py [--seed]   (--seed: record today's fingerprints, start nothing)"""
import glob, hashlib, json, os, pathlib, sys, time

L = pathlib.Path(os.environ.get('LINKS') or '../kpc-links')
SEEN = pathlib.Path('data/gis-hunter/seen.json')


def fp(paths):
    h = hashlib.sha1()
    for p in sorted(paths):
        try: h.update(os.path.basename(p).encode()); h.update(open(p, "rb").read())
        except OSError: pass
    return h.hexdigest()[:16]


def main():
    now = {'US': fp([str(L / 'data/us-key/why-not.json'), 'data/state-gis.json', str(L / 'data/state-gis.json')]),
           'CA': fp(glob.glob(str(L / 'data/ca-key/*.json')) + [str(L / '.claude/build/research/missing-after-key-canada.json')])}
    try: seen = json.load(open(SEEN))
    except (OSError, ValueError): seen = {}
    changed = [c for c in ('US', 'CA') if seen.get(c) != now[c]]
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    json.dump({**now, 'date': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}, open(SEEN, 'w'), indent=1)
    if '--seed' in sys.argv or not changed: return
    first, then = changed[0], (changed[1] if len(changed) > 1 else '')
    tag = 'auto-' + time.strftime('%Y%m%d%H%M', time.gmtime())
    print(f'::notice title=GIS hunter trigger::inputs changed for {" + ".join(changed)}: one full pass starts ({tag})')
    print(f'RUN={first} THEN={then} PASS={tag}')


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        print(f'::notice title=GIS hunter trigger::stopped ({type(e).__name__}: {e})')
    sys.exit(0)
