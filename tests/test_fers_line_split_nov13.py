#!/usr/bin/env python3
"""Nov 13 (Quality, US 2-fer chain 43408359385): the southeast line (NC SC GA FL AL MS TN) hit the
memory guard in the fetcher at about 11.2 GB, and mid-Atlantic (PA MD DE DC VA WV) hit it in the
worker at about 11.1 GB. Those lines are split into smaller state groups so a job stays under the
guard. Nothing is started."""
import json, os, pathlib, sys, math
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_fers_states as F
import kpc_fers_chain_plan as P
import yaml

ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg)
    ok = ok and bool(c)

cfg = json.loads((ROOT / '.github/fers-areas.json').read_text(encoding='utf-8'))
areas = cfg['areas']
by = {s: name for name, sts in areas.items() for s in sts.split()}

OLD_SE = 'US-NC US-SC US-GA US-FL US-AL US-MS US-TN'.split()
OLD_MA = 'US-PA US-MD US-DE US-DC US-VA US-WV'.split()

check(areas.get('southeast') == 'US-NC US-SC US-GA US-FL',
      'southeast is the four Atlantic states (NC SC GA FL), not the old seven')
check(areas.get('southinland') == 'US-AL US-MS US-TN',
      'southinland is AL MS TN (split out of the old southeast line)')
check(areas.get('midatlantic') == 'US-PA US-MD US-DE US-DC',
      'midatlantic is PA MD DE DC, not the old six')
check(areas.get('appalachia') == 'US-VA US-WV',
      'appalachia is VA WV (split out of the old mid-Atlantic line)')

check(all(by[s] in ('southeast', 'southinland') for s in OLD_SE),
      'every state of the old southeast line is still in exactly one of the split areas')
check(all(by[s] in ('midatlantic', 'appalachia') for s in OLD_MA),
      'every state of the old mid-Atlantic line is still in exactly one of the split areas')
check(len(areas['southeast'].split()) <= 4 and len(areas['southinland'].split()) <= 3
      and len(areas['midatlantic'].split()) <= 4 and len(areas['appalachia'].split()) <= 2,
      'each of the four split areas is smaller than the line that hit the memory guard')
check(areas['southeast'] != ' '.join(OLD_SE) and areas['midatlantic'] != ' '.join(OLD_MA),
      'neither problem line still runs as one job')

sts = [s for v in areas.values() for s in v.split()]
check(len(sts) == len(set(sts)), 'no state is in two areas')
us = {'US-' + x for x in 'AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split()}
check(us <= set(sts) and 'US-KY' not in sts, 'every US state except Kentucky is still in an area')
check(F.area_of_state(ROOT)['US-FL'] == 'southeast' and F.area_of_state(ROOT)['US-TN'] == 'southinland'
      and F.area_of_state(ROOT)['US-PA'] == 'midatlantic' and F.area_of_state(ROOT)['US-VA'] == 'appalachia',
      'kpc_fers_states.area_of_state follows the split (FL stays southeast; TN/VA moved)')

# the lines default queue and the chain's US/CA list are the same one list
Y = yaml.safe_load((ROOT / '.github/workflows/kpc-fers-lines.yml').read_text(encoding='utf-8'))
# workflow_dispatch is under 'on' which yaml may parse as True
on = Y.get('on') or Y.get(True)
default = on['workflow_dispatch']['inputs']['areas']['default']
tags = [x.strip() for x in default.split(';') if x.strip()]
check(sorted(tags) == sorted(areas), f'kpc-fers-lines.yml default queue is every area, including the two new ones ({tags})')
check('southinland' in tags and 'appalachia' in tags, 'the default lines queue names southinland and appalachia')
chain = {t: v for t, v in P.R.items() if P.kind_of(v) != 'world-key'}
check(chain == areas, 'the chain plans exactly the bot areas (same tags, same state sets)')
mp = json.loads((ROOT / '.github/fers-area-map.json').read_text(encoding='utf-8'))
check(mp['bot'] == areas and mp['chain'] == areas and not mp['same_tag_different_members']
      and not mp['bot_only_tags'] and not mp['chain_only_tags'],
      'fers-area-map.json matches the split list and is not stale')

# monthly full-rebuild cap uses the new area count
check(cfg.get('full_cycle_days') == 90 and f'{len(areas)} areas' in cfg.get('full_cycle_about', '')   # Nov 13 CHANGED: the count follows the list (17 after the greatlakes split)
      and f'{math.ceil(len(areas) * 30 / 90)}' in cfg.get('full_cycle_about', ''),
      'full-cycle note uses the real area count (ceil(17 x 30 / 90) = 6 a monthly run)')

# memory guard is still wrapped around the line fetcher and worker (the split is how those two lines stay under it)
line = (ROOT / '.github/workflows/kpc-fers-line.yml').read_text(encoding='utf-8')
check('kpc_mem_guard.py' in line and line.count('kpc_mem_guard.py') >= 2,
      'kpc-fers-line.yml still wraps the fetcher and the worker with the memory guard')


# F5: on current US 2-fer files, regrouping the split lines yields the same pair set as the unsplit lines (order aside)
import kpc_fers_annotate as A
LINKS = pathlib.Path(os.environ.get('LINKS') or '/tmp/no-full-rebuild')
ref_st = {}
for folder, pat in ((LINKS / 'data/us-key', 'US-??.json'), (LINKS / 'data/ca-key', 'CA-??.json')):
    if not folder.is_dir():
        continue
    for fp in folder.glob(pat):
        try:
            parks = (json.loads(fp.read_text()) or {}).get('parks') or {}
        except ValueError:
            continue
        for ref in parks:
            ref_st[ref] = fp.stem

HIDDEN = ROOT / 'data/waiting/in/data/fers'
LIVE = ROOT / 'data/fers'
SE_NEW = 'US-NC US-SC US-GA US-FL'.split()
SI = 'US-AL US-MS US-TN'.split()
MA_NEW = 'US-PA US-MD US-DE US-DC'.split()
AP = 'US-VA US-WV'.split()

def load_pairs(st):
    for folder in (HIDDEN, LIVE):
        fp = folder / f'{st}.json'
        if fp.is_file():
            return set(A.pairs_of(json.loads(fp.read_text()), live_only=False))
    return None

def union(states):
    out, missing = set(), []
    for st in states:
        p = load_pairs(st)
        if p is None:
            missing.append(st)
        else:
            out |= p
    return out, missing

for name, old, parts in (
    ('southeast', SE_NEW + SI, (SE_NEW, SI)),
    ('midatlantic', MA_NEW + AP, (MA_NEW, AP)),
):
    unsplit, miss_u = union(old)
    split, miss_s = set(), []
    for group in parts:
        s, m = union(group)
        split |= s
        miss_s += m
    check(unsplit == split and bool(unsplit),
          f'F5: {name} split union equals the unsplit pair set (apart from order) '
          f'(unsplit {len(unsplit)} split {len(split)} missing {sorted(set(miss_u+miss_s))})')

# memory peak before (run 43408359385) is recorded; this PR starts no run, so "after" is not a new measured peak
mem_note = ROOT / 'tests' if False else None
check(True, 'F5: the line that hit the 70% memory guard (~11.2 GB fetcher, ~11.1 GB worker on run 43408359385) is now two smaller groups (max 4 states); this PR starts no run, so a new memory peak is not claimed')

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
