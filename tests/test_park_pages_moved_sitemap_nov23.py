#!/usr/bin/env python3
"""Job 10, 23 Nov 2026 (owner 1:03 PM: "10 and 11 dont stop till you are done"). New York's 567 parks link the DEC's OLD site,
www.dec.ny.gov, whose robots.txt never answers: the reader never read them, and the finder never looked (they were not 'dead').
Rule L-moved: a link on an agency site that MOVED (MOVED_SITES) and could not be read is a dead link, and the finder looks on
the NEW site, never the old one. Rule L-sitemap: the site's own sitemap (robots.txt 'Sitemap:' lines, else /sitemap.xml, a
sitemap index followed into its parts) names the park's page in its address; each address is read and judged as before (L1).
Invented parks and sites, offline fixtures, no request. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages as P  # noqa: E402
import kpc_park_pages_find as FIND  # noqa: E402
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


OLD, NEW = 'https://www.dec.zz.invented.gov', 'https://dec.zz.invented.gov'
FIND.MOVED_SITES['www.dec.zz.invented.gov'] = 'dec.zz.invented.gov'
WORDS = 'Words about the place, its trails and its lake. ' * 12
PIN = (47.0, -101.0)
NEAR = 'data-lat="47.0100" data-lng="-101.0100"'
page = lambda t, pt='': (f'<html><head><title>{t} | Invented DEC</title></head><body><h1>{t}</h1><div class="map" {pt}></div>'
                         f'<p>{WORDS}</p></body></html>')
PARKS = {
    'US-9701': ('Cedar Hollow State Forest', OLD + '/lands/123.html', 'State Forest'),   # old site: found by the sitemap = SURE
    'US-9702': ('Birch Knob State Forest', OLD + '/lands/124.html', 'State Forest'),     # old site: the sitemap does not name it
    'US-9703': ('Elm Ridge State Forest', NEW + '/places/elm-ridge-state-forest', 'State Forest'),   # own pages on the new site:
    'US-9704': ('Fir Lake State Forest', NEW + '/places/fir-lake-state-forest', 'State Forest'),     # the sister parks' folder
}
FX = {
    NEW + '/': {'status': 200, 'body': '<html><head><title>Invented DEC</title></head><body><h1>Welcome</h1><p>' + WORDS + '</p></body></html>'},
    NEW + '/robots.txt': {'status': 200, 'type': 'text/plain', 'body': 'User-agent: *\nAllow: /\nSitemap: ' + NEW + '/sitemap.xml\nSitemap: https://other.invented.com/sitemap.xml\n'},
    NEW + '/sitemap.xml': {'status': 200, 'type': 'application/xml', 'body': '<?xml version="1.0"?><sitemapindex><sitemap><loc>' + NEW
                           + '/sitemap-news.xml</loc></sitemap><sitemap><loc>' + NEW + '/sitemap-places.xml</loc></sitemap></sitemapindex>'},
    NEW + '/sitemap-places.xml': {'status': 200, 'type': 'application/xml', 'body': '<?xml version="1.0"?><urlset>' + ''.join(
        f'<url><loc>{NEW}/places/{s}</loc></url>' for s in ('cedar-hollow-campground', 'cedar-hollow-forest', 'elm-ridge-state-forest',
                                                            'fir-lake-state-forest')) + '</urlset>'},
    NEW + '/sitemap-news.xml': {'status': 200, 'type': 'application/xml', 'body': '<urlset><url><loc>' + NEW + '/news/birch-knob-fire</loc></url></urlset>'},
    NEW + '/places/cedar-hollow-campground': {'status': 200, 'body': page('Cedar Hollow Campground', NEAR)},
    NEW + '/places/cedar-hollow-forest': {'status': 200, 'body': page('Cedar Hollow State Forest')},
    NEW + '/places/elm-ridge-state-forest': {'status': 200, 'body': page('Elm Ridge State Forest', NEAR)},
    OLD + '/robots.txt': {'status': 'robots-unreadable', 'body': ''},
}


with tempfile.TemporaryDirectory() as d:
    t = pathlib.Path(d)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [n, u, k, '', '', PIN[0], PIN[1], 0, 0, 1] for r, (n, u, k) in PARKS.items()}}))
    (t / 'fx.json').write_text(json.dumps({'pages': FX}))
    getter = P.FixtureGetter(json.loads((t / 'fx.json').read_text()), t)
    facts = {'US-ZZ': {
        'US-9701': {'asked': {'url': PARKS['US-9701'][1]}, 'page': {'kind': 'resting', 'status': 'robots-unreadable'}, 'own_page': {'is': 'own'}},
        'US-9702': {'asked': {'url': PARKS['US-9702'][1]}, 'page': {'kind': 'resting', 'status': 'robots-unreadable'}, 'own_page': {'is': 'own'}},
        'US-9703': {'asked': {'url': PARKS['US-9703'][1]}, 'page': {'kind': 'html', 'final_url': PARKS['US-9703'][1]}, 'own_page': {'is': 'own'}},
        'US-9704': {'asked': {'url': PARKS['US-9704'][1]}, 'page': {'kind': 'html', 'final_url': PARKS['US-9704'][1]}, 'own_page': {'is': 'own'}}}}
    check('a link on the old site that could not be read is a dead link (L-moved)', FIND.why_needed(facts['US-ZZ']['US-9701']) == 'dead link')
    check('a park already read on the new site is not looked for', FIND.why_needed(facts['US-ZZ']['US-9703']) == '')
    check('an old-site link that WAS read is not touched', FIND.why_needed({'asked': {'url': OLD + '/lands/9.html'}, 'page': {'kind': 'html'},
                                                                           'own_page': {'is': 'own'}}) == '')
    areas, web, docs, _ = P.load_data(str(t / 'data'))
    st = {}
    rows, written, reqs = FIND.find_links(areas, facts, getter, st, '2026-11-23', quiet=True, web=web, docs=docs,
                                          table=frozenset({'zz.invented.gov'}))
    rows = {r['ref']: r for r in rows}
    check("old site: the new site's sitemap names the park (DEC style, 'State' left out), the page has its own name and sits in the "
          "folder its sister forests use on a known agency site = SURE (sitemap)",
          rows['US-9701']['level'] == 'sure' and rows['US-9701']['how'] == 'sitemap' and rows['US-9701']['url'] == NEW + '/places/cedar-hollow-forest')
    check("the never-read old pages teach no sister folder (nothing asked under the old site's /lands/)", OLD + '/lands/' not in getter.calls)
    check('the sure page stops the walk: the campground of the same name is never read', NEW + '/places/cedar-hollow-campground' not in getter.calls)
    check('a name the sitemap does not carry (only a news page): not found', rows['US-9702']['level'] == 'no')
    check('the old site is never asked', not any(u.startswith(OLD) for u in getter.calls))
    check('the sitemap is read one time for the whole site, its news part too, never another site\'s sitemap',
          getter.calls.count(NEW + '/sitemap-places.xml') == 1 and not any('other.invented.com' in u for u in getter.calls))
    check('the found page is written as the park\'s page', 'US-9701' in written.get('US-ZZ', {}))
    check('sitemap picks: every core word in the last part, fewest extra words first, 2 at most',
          FIND.sitemap_picks([NEW + '/places/a/cedar-hollow-state-forest-annex', NEW + '/places/cedar-hollow', NEW + '/x/cedar', NEW + '/places/cedar-hollow-state-forest'],
                             'Cedar Hollow State Forest') == [NEW + '/places/cedar-hollow', NEW + '/places/cedar-hollow-state-forest'])
    check('a one-short-word core gives no picks (too loose)', FIND.sitemap_picks([NEW + '/places/oak'], 'Oak State Park') == [])
    check('the moved table holds New York DEC and Michigan DNR', FIND.moved_to('https://www.dec.ny.gov/lands/53165.html') == 'https://dec.ny.gov/'
          and FIND.moved_to('https://www2.dnr.state.mi.us/parksandtrails/Details.aspx?id=1') == 'https://www.michigan.gov/')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
