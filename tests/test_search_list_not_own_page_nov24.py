#!/usr/bin/env python3
"""24 Nov 2026 (owner approved E, 5:39 AM CT): a search or list page is not a park's own page, and a county is
tagged only when the page names the park. Invented parks and addresses only. No network. Prints PASS / FAIL,
ends ALL PASS or SOME FAILED."""
import pathlib, socket, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))


def _no_net(*a, **k):
    raise RuntimeError('no network in tests')


socket.socket.connect = _no_net
import kpc_park_pages as PP  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


NAME = 'Invented Marsh State Wildlife Area'
OWN = 'https://dnr.invented.gov/wildlife/invented-marsh'
SEARCH = 'https://dnr.invented.gov/search?q=invented+marsh'
LIST = 'https://dnr.invented.gov/parks/directory'
OWN_TEXT = '<html><title>Invented Marsh State Wildlife Area</title><h1>Invented Marsh State Wildlife Area</h1><p>The wildlife area is in Otter County.</p></html>'
OTHER_TEXT = '<html><title>Wildlife areas of Invented</title><h1>Wildlife areas of Invented</h1><p>This search lists every area in Aroostook County.</p></html>'

check('a /search?q= address is a search or list page', R.is_search_or_list_url(SEARCH))
check('a /directory path is a search or list page', R.is_search_or_list_url(LIST))
check("the park's own address is not a search or list page", not R.is_search_or_list_url(OWN))
check("a park id query is not a search or list page",
      not R.is_search_or_list_url('https://dnr.invented.gov/wildlife/park?id=4471'))

kind, why = PP._own_is(SEARCH, ['US-9981'], {}, OWN_TEXT, NAME)
check('a search address is not the park\'s own page, even when the result names the park',
      kind == 'list' and 'search or list' in why)

kind, why = PP._own_is(OWN, ['US-9981'], {}, OWN_TEXT, NAME)
check("the park's own official page that names it stays its own page", kind == 'own')

check('the own page that names the park may be tagged with its county',
      R.page_names_park(OWN_TEXT, NAME) and R.counties_of(OWN_TEXT) == ['Otter'])
# _location is the gate: counties stay empty when the page does not name the park
loc = R._location({'final': OWN, 'text': OTHER_TEXT},
                  [{'final': OWN, 'text': OTHER_TEXT, 'html': OTHER_TEXT, 'links': []}],
                  {'name': NAME, 'type': 'State Wildlife Area', 'pin': [44.5, -88.5]}, 'US-ZZ', [44.5, -88.5])
check('no county tag when the page does not name the park, even if a county word is on the page',
      loc.get('counties') == [])
loc2 = R._location({'final': OWN, 'text': OWN_TEXT},
                   [{'final': OWN, 'text': OWN_TEXT, 'html': OWN_TEXT, 'links': []}],
                   {'name': NAME, 'type': 'State Wildlife Area', 'pin': [44.5, -88.5]}, 'US-ZZ', [44.5, -88.5])
check('a county is tagged when the own page names the park and names the county',
      loc2.get('counties') == ['Otter'])

# Real address shapes (review of #187): generic/synthetic names only, never a held park.
ME_SEARCH = 'https://apps.web.maine.gov/cgi-bin/online/doc/parksearch/index.pl?c=N'
NS_OWN = 'https://novascotia.com/listing/invented-marsh-provincial-park/'
EMPTY_KW = 'https://dnr.invented.gov/facilities/Detail?Keywords=&unit=4471'
check('a parksearch/index.pl?c=N address is a search or list page', R.is_search_or_list_url(ME_SEARCH))
check('a /listing/<name>/ address is not a search or list page', not R.is_search_or_list_url(NS_OWN))
check('a Detail?Keywords=& address (empty Keywords) is not a search or list page',
      not R.is_search_or_list_url(EMPTY_KW))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
