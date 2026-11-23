#!/usr/bin/env python3
"""One list of official sites, 23 Nov 2026 (owner: "U sure the not offical pages are not offical"). The link tool had its own
list and called 1,115 parks' pages 'other site' or 'not an agency site' although the page reader reads those sites as the
agency's own (Tourism Saskatchewan, novascotia.com, TravelOK, Suwannee River district, county and town sites). The keys then
passed over everything those pages gave. Now the link tool asks the reader's list too. And park facts leaves out an empty
'no link' row when the reader read the park's own official page from the official-links bot's address (371 parks), so the
reader's own-page test stands. Wikipedia, trail and map sites stay not official. Invented parks.
Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
T = ROOT / '.github/scripts/draft/tools'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


L = load('kpc_link_ids', T / 'kpc_link_ids/kpc_link_ids.py')
PF = load('pf', T / 'kpc_park_facts/kpc_park_facts.py')
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


site = lambda u: L.read_link(u, 'Invented Park', 'State Park', 'US-ZZ')['site']
check("a site on the reader's list of agencies' sites is official here too (Tourism Saskatchewan)",
      site('https://www.tourismsaskatchewan.com/provincialpark/1/invented-park') == 'government site')
check('TravelOK and a river district site too', site('https://www.travelok.com/state-parks/invented') == 'government site'
      and site('https://map.mysuwanneeriver.com/invented') == 'government site')
check('a county address the reader knows is a government site', site('https://www.co.invented.pa.us/parks/invented') == 'government site')
check('Wikipedia, a trail site and plain arcgis.com stay not an agency site', {site('https://en.wikipedia.org/wiki/Invented_Park'),
      site('https://www.alltrails.com/invented'), site('https://www.arcgis.com/home/item.html?id=1')} == {'not an agency site'})
check('an unknown .com stays other site', site('https://invented-trails-club.com/park') == 'other site')

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    page = {'area': 'US-ZZ', 'pota': {'name': 'Invented Park', 'type': 'State Park', 'pin': [41.0, -88.0]}, 'asked': {'url': 'https://dnr.invented.gov/p'},
            'page': {'read': '2026-11-23', 'kind': 'html', 'final_url': 'https://dnr.invented.gov/p', 'host': 'dnr.invented.gov'},
            'own_page': {'is': 'own'}, 'name': {'heading': 'Invented Park', 'vs_pota': 'same'}, 'location': {'coords': [], 'addresses': [], 'directions': None}}
    (t / 'pages').mkdir(); (t / 'pages' / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': {'US-9801': page, 'US-9802': dict(page, own_page={'is': 'list'})}}))
    pages, _ = PF.read_pages(str(t / 'pages'))
    parks = {r: {'area': 'US-ZZ', 'name': 'Invented Park', 'type': 'State Park', 'pin': [41.0, -88.0]} for r in ('US-9801', 'US-9802', 'US-9803')}
    links = {r: {'page_kind': 'no link', 'site': None, 'usable': False} for r in parks}
    rows, c = PF.combine(parks, {}, pages, links)
    check("POTA lists no link, the reader read the park's own official page: the empty link row is left out", 'link' not in rows['US-9801'] and 'page' in rows['US-9801'])
    check('a list page is not an own page: its no-link row stays', 'link' in rows['US-9802'])
    check('a park with no page: its no-link row stays', 'link' in rows['US-9803'])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
