#!/usr/bin/env python3
"""Park facts 9, 23 Nov 2026 (owner 'Yes'; rule sheet W5 MAP-LINK NAME): the park's own page links the agency's own map viewer
and the link itself names the place ('...Public_Access_Lands&ID=OTTER MARSH WILDLIFE AREA', '...?find=HERON ROCK WMA'). Park
facts keeps that name (page.map_names). Never a street-map or booking site, never the 32-character id of the map itself, never
a value that 3 or more parks' links carry (a map of everything), never from a list page or an unofficial site.
Invented parks. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pf', ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')
PF = importlib.util.module_from_spec(spec); spec.loader.exec_module(PF)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def park(name, urls, own='own', unofficial=False):
    f = {'area': 'US-ZZ', 'pota': {'name': name, 'type': 'State Wildlife Area', 'pin': [44.4, -88.5]}, 'asked': {'url': 'https://dnr.invented.gov/' + name[:5]},
         'page': {'read': '2026-11-23', 'kind': 'html', 'host': 'dnr.invented.gov'}, 'own_page': {'is': own},
         'name': {'heading': name, 'vs_pota': 'same'}, 'location': {'coords': [], 'addresses': [], 'directions': None},
         'maps': [{'url': u, 'kind': 'web-map', 'names_park': False, 'text': 'Map'} for u in urls]}
    if unofficial: f['unofficial'] = 'unofficial-host'
    return f


GEN = 'https://dnr.maps.arcgis.com/apps/webappviewer/index.html?id=e00cf4a26b8542ceba9858c28b3acbb6'
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    parks = {
        'US-9951': park('Otter Marsh State Wildlife Area', ['https://dnrmaps.invented.gov/H5/?Viewer=Public_Access_Lands&amp;ID=OTTER%20MARSH%20WILDLIFE%20AREA', GEN]),
        'US-9952': park('Heron Rock Wildlife Management Area', ['https://eea.maps.arcgis.com/apps/webappviewer/index.html?id=e00cf4a26b8542ceba9858c28b3acbb6&find=HERON%20ROCK%20WMA']),
        'US-9953': park('Pike Lake State Park', ['https://maps.google.com/maps?q=Pike+Lake+State+Park', 'https://dnr.invented.gov/maps/pike.pdf?name=Pike+Lake']),
        'US-9954': park('Elk Flats State Wildlife Area', ['https://dnrmaps.invented.gov/H5/?Viewer=Public_Access_Lands&ID=ELK%20FLATS%20WILDLIFE%20AREA'], own='list'),
        'US-9955': park('Fox Hollow State Wildlife Area', ['https://dnrmaps.invented.gov/H5/?Viewer=Public_Access_Lands&ID=FOX%20HOLLOW%20WILDLIFE%20AREA'], unofficial=True),
    }
    for i in range(3):   # the same value on three parks' links: a map of everything
        parks[f'US-996{i}'] = park(f'Shared Map Park {i}', ['https://dnrmaps.invented.gov/H5/?Viewer=Public_Access_Lands&find=Statewide%20Hunting%20Lands'])
    (t / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': parks}))
    pages, _ = PF.read_pages(str(t))
    names = lambda r: [m['name'] for m in pages[r].get('map_names') or []]
    check("the name in the agency map link is kept ('&amp;ID=OTTER%20MARSH%20WILDLIFE%20AREA')", names('US-9951') == ['OTTER MARSH WILDLIFE AREA'])
    check('the 32-character id of the map itself is never a name; find= is', names('US-9952') == ['HERON ROCK WMA'])
    check('a street-map site and a PDF give nothing', names('US-9953') == [])
    check('a list page gives nothing', names('US-9954') == [])
    check('an unofficial site gives nothing', names('US-9955') == [])
    check("a value on 3 or more parks' links is a map of everything: taken out of all", all(names(f'US-996{i}') == [] for i in range(3)))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
