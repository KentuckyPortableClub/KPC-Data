#!/usr/bin/env python3
"""Job 10, 23 Nov 2026 (owner 1:03 PM: "10 and 11 dont stop till you are done"). The reader's address KEY dropped the query, so
every park page of a site that numbers its pages ('index.cfm?do=park.profile&parkId=98', '/?page_id=623') fell into ONE key:
one page fetched for all of them, each park called 'on a page shared by many parks', the kept copies written over each other,
and '/?page_id=623' taken for the agency's front page. About 2,000 parks (Oregon State Parks 162, California State Parks 253,
Parks Canada historic sites 385, Minnesota DNR 233 ...). Now the key keeps the query (tracking and language bits left off), a
numbered page is not the front page, a park read under the old key is read again, and a kept copy saved under the old key is
not used. Invented parks and sites, offline fixtures, no request. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages as P  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


H = 'https://stateparks.zz.invented.gov/index.cfm?do=park.profile&parkId='
CA = 'https://www.parks.zz.invented.gov/?page_id='
WORDS = 'Words about the place, its trails and its lake. ' * 12
page = lambda t: f'<html><head><title>{t} | Invented Parks</title></head><body><h1>{t}</h1><p>{WORDS}</p></body></html>'
check('the key keeps the page number', P.norm_url(H + '98') != P.norm_url(H + '97'))
check('tracking and language bits are left off', P.norm_url(H + '98&utm_source=x&lang=en') == P.norm_url(H + '98'))
check('the order of the query does not matter', P.norm_url('https://a.gov/p?b=2&a=1') == P.norm_url('https://a.gov/p?a=1&b=2'))
check('an address with no query keeps its old key (nothing else is read again)', P.norm_url('https://www.a.gov/parks/x/') == 'a.gov/parks/x')
check("'/?page_id=623' is a numbered page, not the front page", not R.is_agency_home(CA + '623') and R.is_agency_home('https://www.parks.zz.invented.gov/')
      and R.is_agency_home('https://www.parks.zz.invented.gov/?utm_source=x'))
PARKS = {'US-9901': ('Otter Bend State Park', H + '98'), 'US-9902': ('Heron Bluff State Park', H + '97'),
         'US-9903': ('Quail Hollow State Park', CA + '623')}
FX = {H + '98': page('Otter Bend State Park'), H + '97': page('Heron Bluff State Park'), CA + '623': page('Quail Hollow State Park')}
with tempfile.TemporaryDirectory() as d:
    t = pathlib.Path(d)
    data = t / 'data' / 'parkinfo'; data.mkdir(parents=True)
    (data / 'US-ZZ.json').write_text(json.dumps({'parks': {r: [n, u, 'State Park', '', '', 47.0, -101.0, 0, 0, 1] for r, (n, u) in PARKS.items()}}))
    (t / 'fx.json').write_text(json.dumps({'pages': {u: {'status': 200, 'body': b} for u, b in FX.items()}}))
    run = lambda *a: subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages.py'), 'read', '--data', str(t / 'data'),
                                     '--out', str(t / 'out'), '--state', str(t / 'out/state.json'), '--fixtures', str(t / 'fx.json'),
                                     '--today', '2026-11-23', '--areas', 'US-ZZ', '--quiet', *a], capture_output=True, text=True)
    r = run()
    check('the reader runs', r.returncode == 0)
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    check('two numbered pages of one site are two parks\' own pages, each with its own name',
          facts['US-9901']['own_page']['is'] == 'own' and facts['US-9902']['own_page']['is'] == 'own'
          and facts['US-9901']['name']['vs_pota'] == 'same' and facts['US-9902']['name']['vs_pota'] == 'same')
    check("'/?page_id=623' is read as the park's own page", facts['US-9903']['own_page']['is'] == 'own' and facts['US-9903']['page']['kind'] == 'html')
    st = json.loads((t / 'out/state.json').read_text())
    check('each read carries the new key rule', all(st['read'][r].get('key_rule') == P.URL_KEY_RULE for r in PARKS))
    # a park read under the OLD key is read again; one read under the new key is not
    st['read']['US-9901'].pop('key_rule'); (t / 'out/state.json').write_text(json.dumps(st))
    r = run('--today', '2026-11-24')
    facts = json.loads((t / 'out/facts/US-ZZ.json').read_text())['parks']
    check('a numbered page read under the old key is read again', not facts['US-9901'].get('unchanged'))
    st = json.loads((t / 'out/state.json').read_text())
    check('... and then carries the new key rule', st['read']['US-9901'].get('key_rule') == P.URL_KEY_RULE)
    # kept copies: a numbered page kept under the old key is not used
    man = t / 'kept' / 'manifest.json'; man.parent.mkdir()
    man.write_text(json.dumps({'pages': {H + '98': {'file': 'aa/x.gz', 'status': 200}, H + '97': {'file': 'aa/y.gz', 'status': 200, 'kr': P.URL_KEY_RULE},
                                         'https://a.zz.invented.gov/parks/z': {'file': 'aa/z.gz', 'status': 200}}}))
    m = P.kept_manifest(man)['pages']
    check('a kept numbered page saved under the old key is not used; one saved under the new key and pages with no query are',
          set(m) == {H + '97', 'https://a.zz.invented.gov/parks/z'})
    k = P.PageKeeper(str(t / 'kept2'), '2026-11-23'); k.keep(H + '98', H + '98', 200, {}, b'<html>a</html>'); k.keep(H + '97', H + '97', 200, {}, b'<html>b</html>')
    check('the keeper now saves two numbered pages as two files, marked with the key rule',
          len({v['file'] for v in k.man['pages'].values()}) == 2 and all(v.get('kr') == P.URL_KEY_RULE for v in k.man['pages'].values()))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
