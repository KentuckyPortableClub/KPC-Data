#!/usr/bin/env python3
"""Re-list the servers of hosts that failed in outside research (pack blocked/failed-layer-hosts.md).

A dead address ('Service not found', 404, 'Invalid URL', 'answer rest') usually means the service was renamed or moved,
not that the data is gone. For each such host we read the server's own services directory (ArcGIS REST '?f=json') at the
roots the club's agency atlas already lists for that host, plus the standard ArcGIS roots ('/arcgis/rest/services',
'/server/rest/services'), walk one folder level, and keep services whose names look like park land.
'Token Required' hosts are re-listed too, but a service that needs a token is written as 'needs sign-in' and never used.
Writes registry/relisted.json (LEADS: a person or verify.py still has to approve them). No guessing beyond those roots.

  python3 registry/relist_failed.py [--pack <sources>] [--cache DIR] [--hosts a,b]"""
import argparse, json, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from core.polite import Polite        # noqa: E402

PARKY = re.compile(r'park|protect|conserv|wildlife|wma|refuge|natur|reserve|preserv|forest|recreat|boundar|land_?status|'
                   r'managed_?area|public_?land|trail|camp|wilderness|heritage|schutz|parc|parque|area_?protegida|snap|zone', re.I)


def roots_for(host, atlas_dir):
    roots = set()
    for f in pathlib.Path(atlas_dir).glob('*.md'):
        for u in re.findall(r'https?://[^\s)`\'"<>]*rest/services', f.read_text(errors='ignore')):
            if u.split('/')[2] == host: roots.add(u)
    if not re.match(r'services\d*\.arcgis\.(com|org)$', host):        # AGOL hosts need the org id: never guessed
        roots |= {f'https://{host}/arcgis/rest/services', f'https://{host}/server/rest/services'}
    return sorted(roots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', default=os.environ.get('KPC_SOURCES', '/workspace/pota/sources/sources'))
    ap.add_argument('--cache', default=str(HERE.parent / '.cache')); ap.add_argument('--hosts', default='')
    a = ap.parse_args()
    pk = json.load(open(HERE / 'pack_sources.json'))
    failed = pk['failed_hosts']
    P = Polite('KPC park engine: re-list failed hosts', cache_dir=a.cache)
    out = {}
    for host, info in failed.items():
        if a.hosts and host not in a.hosts.split(','): continue
        if not (info['dead'] or 'answer rest' in info['why'] or 'Token' in info['why']):
            out[host] = {'why_failed': info['why'], 'action': 'not re-listed: the failure was about the data (points / no name field / bad query), not the address'}
            continue
        rec = {'why_failed': info['why'], 'roots': {}, 'leads': []}
        for root in roots_for(host, pathlib.Path(a.pack) / 'tips/agency-atlas'):
            r = P.get(root + '?f=json', kind='layer')
            if r.blocked or r.status != 200:
                rec['roots'][root] = r.blocked or f'HTTP {r.status}'; continue
            try: d = json.loads(r.text())
            except ValueError: rec['roots'][root] = 'not JSON (not an ArcGIS services directory)'; continue
            if 'error' in d: rec['roots'][root] = 'needs sign-in' if d['error'].get('code') in (498, 499) else f"error {d['error'].get('code')}"; continue
            rec['roots'][root] = f"ok: {len(d.get('folders', []))} folders, {len(d.get('services', []))} services"
            svcs = list(d.get('services', []))
            for fo in d.get('folders', [])[:40]:
                if not PARKY.search(fo) and fo.lower() not in ('public', 'hosted', 'external', 'opendata', 'open_data', 'environment', 'nature'): continue
                r2 = P.get(f'{root}/{fo}?f=json', kind='layer')
                if r2.blocked or r2.status != 200: continue
                try: svcs += json.loads(r2.text()).get('services', [])
                except ValueError: pass
            for s in svcs:
                if PARKY.search(s.get('name', '')) and s.get('type') in ('MapServer', 'FeatureServer'):
                    rec['leads'].append(f"{root}/{s['name']}/{s['type']}")
        rec['leads'] = sorted(set(rec['leads']))[:80]
        out[host] = rec
        print(f"{host:34} {info['why'][:40]:40} roots={len(rec['roots'])} leads={len(rec['leads'])} {list(rec['roots'].values())[:2]}", flush=True)
    json.dump({'about': __doc__.split('\n\n')[0], 'hosts': out}, open(HERE / 'relisted.json', 'w'), indent=1, ensure_ascii=False)
    P.write_blocked(HERE)


if __name__ == '__main__':
    main()
