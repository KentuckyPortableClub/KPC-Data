#!/usr/bin/env python3
"""Nov 16: the waiting-room documents check must not treat a denied-page URL as a
real map or as a fault. Illinois already stores three google.com/maps links marked
"denied page" (not shown as a map); F-D2 was holding the file for those same
links. A banned-host URL that is not marked denied is still a fault. The retest stub returns the #107 shape ({sample, results}), not the old
(tested, dead) pair. Offline: synthetic records only, nothing is fetched, and
nothing in the repo is written."""
import importlib.util, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-wr-docs-'))
os.environ['DATA'] = str(tmp); os.environ['LINKS'] = str(tmp / 'nolinks')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
spec = importlib.util.spec_from_file_location('wr_docs_denied', HERE / '.github/scripts/kpc_waiting_room.py')
WR = importlib.util.module_from_spec(spec); spec.loader.exec_module(WR)

seen = []


def stub_retest(urls, n=20):
    # After #107, retest returns {sample, results}, not (tested, dead).
    kept = [u for u in urls if u]
    seen.append(kept)
    sample = kept[:n]
    return {'sample': sample, 'results': [{'url': u, 'result': 'ok', 'detail': ''} for u in sample]}


WR.retest = stub_retest

G1 = "https://www.google.com/maps/place/39%C2%B006'01.1%22N+88%C2%B047'57.1%22W"
G2 = "https://www.google.com/maps/place/41%C2%B011'49.2%22N+88%C2%B053'48.8%22W"
G3 = "https://www.google.com/maps/place/42%C2%B012'16.2%22N+90%C2%B012'19.1%22W"
DENIED = "opened, a government data / policies page, not this park's map (chat 11 regrade 2)"
REAL = 'https://example.test/parks/oak-woods-map.pdf'


def park(name, map_url, *, kind=None, status='ok', rules_url='', rules_kind=None):
    m = {'url': map_url, 'how': "a link on the park's page ('Map')", 'status': status}
    if kind: m['kind'] = kind
    r = {'url': rules_url, 'how': '', 'status': 'not found' if not rules_url else 'ok'}
    if rules_kind: r['kind'] = rules_kind
    return {'n': name, 't': 'State Park', 'page': 'https://example.test/parks/' + name.lower().replace(' ', '-'), 'map': m, 'rules': r}


def area(parks):
    return {'area': 'US-XX', 'parks': parks}


def fd(holds, tag):
    return [h for h in holds if h.startswith(tag)]


# (a) the Illinois-shaped hole: three distinct Google Maps links already marked
# denied. Today's check counted them as maps and held the file with F-D2.
seen.clear()
parks = {
    'US-0001': park('Rock Cave', G1, kind='denied page', status=DENIED),
    'US-0002': park('Sandy Ford', G2, kind='denied page', status=DENIED),
    'US-0003': park('Rall Woods', G3, kind='denied page', status=DENIED),
    'US-0004': park('Oak Woods', REAL, kind='pdf', status='ok'),
}
holds, _ = WR.c_docs('data/docs/US-XX.json', area(parks), area(parks), {})
check(not fd(holds, 'F-D2'), f'three denied Google Maps links are not an F-D2 fault ({fd(holds, "F-D2")})')
check(not fd(holds, 'F-D1'), 'denied-page URLs are not counted as shared maps either')
check(REAL in (seen[-1] if seen else []) and G1 not in (seen[-1] if seen else []) and G2 not in (seen[-1] if seen else []) and G3 not in (seen[-1] if seen else []),
      'the link re-test is given the real map and not the denied-page URLs')

# (b) a banned-host map that is not marked denied is still a fault
seen.clear()
parks_bad = {
    'US-0004': park('Oak Woods', REAL, kind='pdf', status='ok'),
    'US-0005': park('Pine Ridge', G1, kind='page', status='ok'),
}
holds, _ = WR.c_docs('data/docs/US-XX.json', area(parks_bad), area(parks_bad), {})
check(len(fd(holds, 'F-D2')) == 1 and '1 map links on a banned host' in fd(holds, 'F-D2')[0],
      f'one unmarked Google Maps link is still F-D2 ({fd(holds, "F-D2")})')

# (c) a mix: two denied + one unmarked banned host -> F-D2 counts only the unmarked one
seen.clear()
mix = {
    'US-0001': park('Rock Cave', G1, kind='denied page', status=DENIED),
    'US-0002': park('Sandy Ford', G2, kind='denied page', status=DENIED),
    'US-0005': park('Pine Ridge', G3, kind='page', status='ok'),
}
holds, _ = WR.c_docs('data/docs/US-XX.json', area(mix), area(mix), {})
check(len(fd(holds, 'F-D2')) == 1 and '1 map links on a banned host' in fd(holds, 'F-D2')[0] and G3[:40] in fd(holds, 'F-D2')[0],
      f'F-D2 counts only the unmarked banned link, not the denied ones ({fd(holds, "F-D2")})')

# (d) many parks sharing one denied URL do not trip F-D1; the same URL as a real map still does
same_denied = {f'US-{1000+i}': park(f'Lake {i}', G1, kind='denied page', status=DENIED) for i in range(25)}
holds, _ = WR.c_docs('data/docs/US-XX.json', area(same_denied), area(same_denied), {})
check(not fd(holds, 'F-D1') and not fd(holds, 'F-D2'),
      '25 parks with the same denied-page URL are not F-D1 or F-D2')
same_real = {f'US-{2000+i}': park(f'Lake {i}', 'https://example.test/statewide-map.pdf', kind='pdf', status='ok') for i in range(25)}
holds, _ = WR.c_docs('data/docs/US-XX.json', area(same_real), area(same_real), {})
check(len(fd(holds, 'F-D1')) == 1 and '25 of 25' in fd(holds, 'F-D1')[0],
      f'25 parks with the same real map URL are still F-D1 ({fd(holds, "F-D1")})')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
