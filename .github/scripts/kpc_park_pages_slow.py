#!/usr/bin/env python3
"""The parks still waiting on SLOW sites (job 10, 23 Nov 2026; owner 1:03 PM: "10 and 11 dont stop till you are done").

A site that asks for a long Crawl-delay in its robots.txt (New York's parks.ny.gov: 196 parks; Utah State Parks: 24) is never
read by the nightly walk: over 120 s it is skipped ('crawl-delay'), and a slow site gets 10 pages a night ('deferred'). This
lists those parks so the PC's 2g step can read only them, waiting as long as each site asks (robots.txt always wins: the delay
is obeyed in full, never cut short). Reads out/facts only; writes out/slow-refs.json (park numbers: stays on the PC).

  python kpc_park_pages_slow.py --out OUT
"""
import argparse, collections, glob, json, os, sys, urllib.parse

WAITING = ('crawl-delay', 'deferred')


def waiting(facts_dir):
    """-> ([park numbers], Counter(host))"""
    refs, hosts = [], collections.Counter()
    for f in sorted(glob.glob(os.path.join(facts_dir, '*.json'))):
        try:
            parks = (json.load(open(f, encoding='utf-8')) or {}).get('parks') or {}
        except (OSError, ValueError):
            continue
        for ref, fact in sorted(parks.items()):
            pg = (fact or {}).get('page') or {}
            if str(pg.get('status') or '') in WAITING and pg.get('kind') == 'resting':
                url = pg.get('final_url') or (fact.get('asked') or {}).get('url') or ''
                refs.append(ref)
                hosts[urllib.parse.urlparse(url).netloc.lower() or '(no address)'] += 1
    return refs, hosts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    refs, hosts = waiting(os.path.join(a.out, 'facts'))
    with open(os.path.join(a.out, 'slow-refs.json'), 'w', encoding='utf-8') as fh:
        json.dump(refs, fh)
    print(f'{len(refs):,} parks wait on slow sites.')
    for h, n in hosts.most_common(15):
        print(f'  {n:>5,}  {h}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
