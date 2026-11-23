#!/usr/bin/env python3
"""kpc_pull_location.py (22 Nov 2026, owner 7:52 PM: "maybe just a script to run and pull everyone we need just the address
or gps or what ever"): ONE quick pass over the parks' own official pages that the page reader read but that gave no address,
no map point or no directions. It opens only that page (plus, when the page has none, the one directions page it links on
the same site), finds the address, the map points and the directions with the reader's own finders, and writes them into
the reader's facts files on this PC. Nothing else in a park's facts changes.

Same manners as every KPC bot (kpc_manners): robots.txt always wins, never-contact and host rules hold, 1 request per 2 s per
site. It is quick because it works on several SITES at once (each site still one request per 2 s, one worker per site):
the long reader waited on each site in turn. Each park is done once (out\\pull-location.json remembers it); a closed window
carries on next time. Counts only, never a park name.
  python kpc_pull_location.py --out out --scripts scripts [--workers 8] [--max-minutes 180]   (--selftest)"""
import argparse, datetime, json, os, pathlib, sys, threading, time

REAL = ('html', 'pdf')
DIR_WORDS = ('direction', 'getting here', 'getting there', 'how to get', 'find us', 'location')


def wants_place(fact):
    """The park's own official page was read and gave no address and no point, or no directions naming a road or town."""
    if not isinstance(fact, dict) or fact.get('unofficial'):
        return False
    if ((fact.get('page') or {}).get('kind')) not in REAL or (fact.get('own_page') or {}).get('is') != 'own':
        return False
    loc = fact.get('location') or {}
    d = loc.get('directions') or {}
    return (not loc.get('addresses') and not loc.get('coords')) or not (d.get('roads') or d.get('towns'))


def page_of(R, M, url):
    st, headers, body, final = M.get(url)
    if st != 200 or not body:
        return None, st
    vis = R.visible_of(body, headers, final or url, [])
    return {'url': url, 'final': final or url, 'status': st, 'text': vis.get('text') or '', 'html': vis.get('html') or '',
            'links': vis.get('links') or []}, st


def pull_one(R, M, fact):
    """-> (new location, confirm address, confirm point, status) for one park, or (None, ..., status)."""
    url = (fact.get('page') or {}).get('final_url') or (fact.get('asked') or {}).get('url')
    if not url or R.is_wdpa(url):
        return None, None, None, 'no address on file'
    main, st = page_of(R, M, url)
    if not main:
        return None, None, None, str(st)
    pota = fact.get('pota') or {}
    pin = pota.get('pin') or [None, None]
    area = fact.get('area') or ''
    pages = [main]
    loc = R._location(main, pages, pota, area, pin)
    if not (loc.get('directions') or {}).get('roads') and not (loc.get('directions') or {}).get('towns'):
        host = R.host_of(main['final'])
        for link, text in main['links']:
            if R.host_of(link) == host and any(w in (str(text) + ' ' + link).lower() for w in DIR_WORDS) and link != main['final']:
                extra, _ = page_of(R, M, link)
                if extra:
                    d = R.directions_of(extra['text'])
                    if d and (d.get('roads') or d.get('towns')):
                        loc['directions'] = d
                    if not loc.get('addresses'):
                        loc['addresses'] = R.addresses_in(extra['text'])
                break
    addr, pt = R.confirm_place(loc)
    return loc, addr, pt, 'read'


def run(out, scripts, workers=8, max_minutes=180, today=None, manners=None):
    sys.path.insert(0, str(pathlib.Path(scripts).resolve()))
    import kpc_park_pages_rules as R
    if manners is None:
        from kpc_manners import Manners
        manners = lambda: Manners('KPC park page reader (addresses and map points)')
    today = today or datetime.date.today().isoformat()
    out = pathlib.Path(out)
    mp = out / 'pull-location.json'
    done = json.loads(mp.read_text(encoding='utf-8')) if mp.is_file() else {}
    files = {f: json.loads(f.read_text(encoding='utf-8')) for f in sorted((out / 'facts').glob('*.json'))}
    todo = {}
    for f, d in files.items():
        for ref, fact in (d.get('parks') or {}).items():
            if ref in done or not wants_place(fact):
                continue
            host = R.host_of((fact.get('page') or {}).get('final_url') or '') or '?'
            todo.setdefault(host, []).append((f, ref))
    total = sum(len(v) for v in todo.values())
    print(f'Own pages to read for an address, map point or directions: {total} on {len(todo)} sites '
          f'(done before: {len(done)}). Up to {max_minutes} minutes; closing the window is fine.', flush=True)
    lock, counts, deadline = threading.Lock(), {'read': 0, 'address': 0, 'point': 0, 'directions': 0, 'not read': 0}, time.time() + max_minutes * 60
    hosts = sorted(todo, key=lambda h: -len(todo[h]))
    queue = list(hosts)

    def save():
        for f, d in files.items():
            tmp = f.with_name(f.name + '.tmp')
            tmp.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
            tmp.replace(f)
        mp.write_text(json.dumps(done, indent=0, sort_keys=True), encoding='utf-8')

    def worker():
        M = manners()                          # one worker per site at a time: each site keeps its own 2 s pace
        while time.time() < deadline:
            with lock:
                if not queue: return
                host = queue.pop(0)
            for f, ref in todo[host]:
                if time.time() >= deadline: return
                fact = files[f]['parks'][ref]
                try:
                    loc, addr, pt, how = pull_one(R, M, fact)
                except Exception as e:  # noqa: BLE001
                    loc, how = None, f'error {type(e).__name__}'
                with lock:
                    if loc is None:
                        counts['not read'] += 1
                        if not how.startswith('error'): done[ref] = today + ' ' + how[:20]
                        continue
                    old = fact.get('location') or {}
                    for k in ('addresses', 'coords', 'directions'):
                        if loc.get(k) and not old.get(k): old[k] = loc[k]
                    fact['location'] = old
                    conf = fact.setdefault('confirm', {})
                    if addr and not conf.get('address'): conf['address'] = addr
                    if pt and not conf.get('coords') and (fact.get('own_page') or {}).get('is') == 'own': conf['coords'] = pt
                    fact.setdefault('page', {})['read'] = today          # a newer read: the upload keeps it
                    fact['location_pulled'] = today
                    done[ref] = today
                    counts['read'] += 1
                    counts['address'] += bool(old.get('addresses'))
                    counts['point'] += bool(old.get('coords'))
                    counts['directions'] += bool((old.get('directions') or {}).get('roads') or (old.get('directions') or {}).get('towns'))
                    if counts['read'] % 200 == 0:
                        save()
                        print(f"  {counts['read']} read so far: {counts['address']} with an address, {counts['point']} with a point, "
                              f"{counts['directions']} with directions", flush=True)

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, min(workers, len(hosts) or 1)))]
    for t in ts: t.start()
    for t in ts: t.join()
    save()
    left = total - counts['read'] - counts['not read']
    print(f"Done this run: {counts['read']} pages read ({counts['address']} with an address, {counts['point']} with a map point, "
          f"{counts['directions']} with directions); {counts['not read']} could not be read (refused, busy, robots or gone); "
          f"{max(0, left)} left for the next run.", flush=True)
    return 0


def selftest():
    import tempfile
    here = pathlib.Path(__file__).resolve().parent
    scripts = next((p for p in (here.parent, here.parent / 'page-reader' / 'scripts', here.parent.parent / 'page-reader' / 'scripts') if (p / 'kpc_park_pages_rules.py').is_file()), here.parent)
    pages = {
        'https://parks.zz.example.gov/test-lake': b'<html><body><h1>Test Lake State Park</h1><p>Visitor Center: 10 Test Lane, Testville, KY 40000</p>'
                                                b'<a href="/test-lake/directions">Directions</a></body></html>',
        'https://parks.zz.example.gov/test-lake/directions': b'<html><body><p>From I-99 take exit 12 and go north on Test Road 3 miles.</p></body></html>',
    }

    class FakeM:
        calls = []
        def get(self, u, **k):
            FakeM.calls.append(u)
            b = pages.get(u)
            return (200, {'content-type': 'text/html'}, b, u) if b else (404, {}, b'', u)

    with tempfile.TemporaryDirectory() as t:
        o = pathlib.Path(t); (o / 'facts').mkdir()
        own = {'is': 'own'}
        parks = {'K4-0001': {'area': 'US-KY', 'page': {'kind': 'html', 'final_url': 'https://parks.zz.example.gov/test-lake', 'read': '2026-11-01'},
                             'own_page': own, 'pota': {'name': 'Test Lake State Park', 'pin': [37.5, -85.0]}, 'location': {}, 'sizes': [1]},
                 'K4-0002': {'area': 'US-KY', 'page': {'kind': 'html', 'final_url': 'https://parks.zz.example.gov/gone'}, 'own_page': own,
                             'pota': {'name': 'Gone', 'pin': [37.5, -85.0]}, 'location': {}},
                 'K4-0003': {'area': 'US-KY', 'page': {'kind': 'html', 'final_url': 'https://parks.zz.example.gov/x'}, 'own_page': {'is': 'list'},
                             'pota': {}, 'location': {}}}
        (o / 'facts' / 'US-KY.json').write_text(json.dumps({'parks': parks}), encoding='utf-8')
        run(o, scripts, workers=2, today='2026-11-22', manners=FakeM)
        d = json.loads((o / 'facts' / 'US-KY.json').read_text(encoding='utf-8'))['parks']
        f1 = d['K4-0001']
        ok = (f1['location'].get('addresses') and f1['location']['addresses'][0]['text'] == '10 Test Lane, Testville, KY 40000'
              and 'I-99' in (f1['location'].get('directions') or {}).get('roads', [])
              and f1['page']['read'] == '2026-11-22' and f1.get('sizes') == [1] and f1['confirm']['address']['role'] == 'visitor-centre'
              and not d['K4-0002']['location'] and 'https://parks.zz.example.gov/x' not in FakeM.calls)
        n = len(FakeM.calls)
        run(o, scripts, workers=2, today='2026-11-23', manners=FakeM)       # a second run reads nothing again
        ok = ok and len(FakeM.calls) == n
    print('selftest', 'ALL PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out'); ap.add_argument('--scripts', default='scripts')
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--max-minutes', type=float, default=180)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else run(a.out, a.scripts, a.workers, a.max_minutes))
