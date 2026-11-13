#!/usr/bin/env python3
"""Nov 13 (KPC owner): the greatlakes 2-fer line (OH MI IN IL WI) hit the memory guard in the fetcher (run 43441416232), so it is
split like southeast and midatlantic were: greatlakes = OH MI IN, lakeswest = IL WI. And a recorded memory stop holds a line back
only while the line is still the same cut (the same states): a line cut smaller since the stop may run again.
Offline; prints PASS / FAIL lines."""
import json, os, pathlib, shutil, sys, tempfile, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_fers_states as F
import kpc_fers_chain_plan as P
import kpc_mem_guard as G
import yaml
ok = True
def check(c, msg):
    global ok; ok = ok and bool(c)
    print(('PASS ' if c else 'FAIL ') + msg)

cfg = json.loads((ROOT / '.github/fers-areas.json').read_text(encoding='utf-8'))
areas = cfg['areas']
check(areas.get('greatlakes') == 'US-OH US-MI US-IN', 'greatlakes is OH MI IN')
check(areas.get('lakeswest') == 'US-IL US-WI', 'lakeswest is IL WI (split out of the old greatlakes line)')
by = F.area_of_state(ROOT)
check(all(by[s] in ('greatlakes', 'lakeswest') for s in 'US-OH US-MI US-IN US-IL US-WI'.split()), 'every old greatlakes state is still in exactly one of the two lines')
flat = [s for v in areas.values() for s in v.split()]
check(len(flat) == len(set(flat)), 'no state or province is in two areas')
check(max(len(v.split()) for k, v in areas.items() if k in ('greatlakes', 'lakeswest')) <= 3, 'neither half has more than three states')
check(not any(k.startswith('W-') or v.startswith('W-') for k, v in areas.items()), 'no world area in fers-areas.json')
wf = yaml.safe_load((ROOT / '.github/workflows/kpc-fers-lines.yml').read_text(encoding='utf-8'))
on = wf.get(True) or wf.get('on')
tags = [t.strip() for t in on['workflow_dispatch']['inputs']['areas']['default'].split(';')]
check(sorted(tags) == sorted(areas), 'the default lines queue names every area once, lakeswest included')
chain = {t: v for t, v in P.R.items() if P.kind_of(v) != 'world-key'}
check(chain == areas, 'the chain plans exactly the bot areas')
mp = json.loads((ROOT / '.github/fers-area-map.json').read_text(encoding='utf-8'))
check(mp['bot'] == areas and mp['chain'] == areas and not mp['same_tag_different_members'], 'fers-area-map.json is not stale')
check('schedule' not in on, 'kpc-fers-lines.yml has no cron line')

# ---- a memory stop holds back only the same cut
td = pathlib.Path(tempfile.mkdtemp())
try:
    (td / 'data/status').mkdir(parents=True); (td / '.github').mkdir()
    def setup(area_states, breaks):
        (td / '.github/fers-areas.json').write_text(json.dumps({'areas': area_states}), encoding='utf-8')
        (td / 'data/status/line-breaks.json').write_text(json.dumps(breaks), encoding='utf-8')
    now = time.time()
    old = {'tag': 'greatlakes', 'states': 'US-OH US-MI US-IN US-IL US-WI', 'stage': 'fetcher', 'why': 'memory', 't': now}
    setup({'greatlakes': 'US-OH US-MI US-IN US-IL US-WI'}, [old])
    check(G.stopped_for_memory(str(td), 'greatlakes') is True, 'same states as at the stop: still held back (never retried blindly on the same cut)')
    setup({'greatlakes': 'US-IN US-MI US-OH US-WI US-IL'}, [old])
    check(G.stopped_for_memory(str(td), 'greatlakes') is True, 'the same states in another order are the same cut')
    setup({'greatlakes': 'US-OH US-MI US-IN', 'lakeswest': 'US-IL US-WI'}, [old])
    check(G.stopped_for_memory(str(td), 'greatlakes') is False, 'cut smaller since the stop: the old stop no longer holds the line back')
    check(G.stopped_for_memory(str(td), 'lakeswest') is False, 'the new line has no stop on record')
    setup({'greatlakes': 'US-OH US-MI US-IN'}, [old, {'tag': 'greatlakes', 'states': 'US-OH US-MI US-IN', 'why': 'memory', 't': now}])
    check(G.stopped_for_memory(str(td), 'greatlakes') is True, 'a new stop on the smaller cut holds it back again')
    setup({'greatlakes': 'US-OH US-MI US-IN'}, [{'tag': 'greatlakes', 'why': 'memory', 't': now}])
    check(G.stopped_for_memory(str(td), 'greatlakes') is True, 'a stop with no states on record counts as before (held back)')
    setup({'greatlakes': 'US-OH US-MI US-IN'}, [{'tag': 'mi', 'states': 'US-MI', 'why': 'memory', 't': now}])
    check(G.stopped_for_memory(str(td), 'mi') is True, 'a hand-made line tag that is not an area name counts as before')
    setup({'greatlakes': 'US-OH US-MI US-IN'}, [dict(old, why='time')])
    check(G.stopped_for_memory(str(td), 'greatlakes') is False, 'a break that was not a memory stop never counted')
    (td / '.github/fers-areas.json').write_text('{not json', encoding='utf-8')
    (td / 'data/status/line-breaks.json').write_text(json.dumps([old]), encoding='utf-8')
    check(G.stopped_for_memory(str(td), 'greatlakes') is True, 'an unreadable area list fails safe: the stop still holds')
    setup({'greatlakes': 'US-OH US-MI US-IN US-IL US-WI'}, [dict(old, t=now - 86400)])
    check(G.stopped_for_memory(str(td), 'greatlakes', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now - 3600))) is False, "the 'since' cut-off still works")
finally:
    shutil.rmtree(td, ignore_errors=True)

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
