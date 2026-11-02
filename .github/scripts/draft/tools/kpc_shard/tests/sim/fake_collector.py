#!/usr/bin/env python3
"""Fake slow 'layer collector' for the kpc_shard simulation (no network). Per area it 'reads' each layer:
2 s gap per host inside this job (the bot's own manners) + simulated latency per request. Writes <out>/<AREA>.json,
<out>/state-<i>.json (via kpc_shard.write_part_state) and <out>/work/requests.log (one JSON line per request).
Same contract as a real bot: AREAS env, --out, --max-minutes (exit 3), --resume, --limit."""
import argparse, datetime as dt, hashlib, json, os, sys, time
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import kpc_shard  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--max-minutes', type=float, default=50)
ap.add_argument('--resume', action='store_true')
ap.add_argument('--limit', type=int)
ap.add_argument('--areas')
ap.add_argument('--layers', default=str(Path(__file__).with_name('sim_layers_12.json')))
ap.add_argument('--gap', type=float, default=2.0)
ap.add_argument('--latency', type=float, default=0.3)
a = ap.parse_args()
start = time.time()
layers = json.loads(Path(a.layers).read_text())
areas = kpc_shard.parse_areas(a.areas) if a.areas else kpc_shard.areas_from_env(list(layers))
areas = areas[:a.limit] if a.limit else areas
out = Path(a.out)
(out / 'work').mkdir(parents=True, exist_ok=True)
job = int(os.environ.get('KPC_SHARD_I', '1'))
sf = out / f'state-{job}.json'
state = json.loads(sf.read_text())['areas'] if (a.resume and sf.exists()) else {}
log = open(out / 'work' / 'requests.log', 'a')
last = {}
counts = {'layers': 0, 'features': 0}
for area in areas:
    if state.get(area, {}).get('done'):
        continue
    if time.time() - start > a.max_minutes * 60:
        state.setdefault(area, {'done': None})
        continue
    rows = []
    by_host = {}
    for ly in layers.get(area, []):
        by_host.setdefault(urlparse(ly['url']).hostname, []).append(ly)
    queue = []                                   # round-robin over hosts so per-host gaps overlap
    while any(by_host.values()):
        for h in list(by_host):
            if by_host[h]:
                queue.append((h, by_host[h].pop(0)))
    for h, ly in queue:
        wait = last.get(h, -1e9) + a.gap - time.time()
        if wait > 0:
            time.sleep(wait)
        t0 = time.time()
        last[h] = t0
        time.sleep(a.latency)
        t1 = time.time()
        log.write(json.dumps({'host': h, 'job': job, 'area': area, 't0': t0, 't1': t1}) + '\n')
        log.flush()
        n = int(hashlib.sha1(ly['layer'].encode()).hexdigest()[:4], 16) % 500
        rows.append({'layer': ly['layer'], 'source_url': ly['url'], 'features': n, 'read_date': dt.date.today().isoformat(),
                     'why': 'synthetic layer read for the kpc_shard simulation'})
    rows.sort(key=lambda r: r['layer'])
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    (out / f'{area}.json').write_text(json.dumps({'area': area, 'collected_at': now, 'layers': rows}, indent=1) + '\n')
    state[area] = {'done': now, 'counts': {'layers': len(rows), 'features': sum(r['features'] for r in rows)}}
    counts['layers'] += len(rows)
    counts['features'] += sum(r['features'] for r in rows)
kpc_shard.write_part_state(out, state, counts, job)
left = [x for x in areas if not state.get(x, {}).get('done')]
print(f'fake_collector job {job}: {len(areas) - len(left)} done, {len(left)} left, {time.time() - start:.1f}s')
sys.exit(3 if left else 0)
