#!/usr/bin/env python3
"""Nov 20: a site title or heading that is only a parks menu is not the park's name.
Synthetic page only; no real park names."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_park_pages_rules as R  # noqa: E402

FAILS = []


def check(ok, what):
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if not ok:
        FAILS.append(what)


check(R.is_menu_chrome('STATE PARKS MENU'), 'STATE PARKS MENU is menu chrome')
check(R.is_menu_chrome('Parks Menu'), 'Parks Menu is menu chrome')
check(not R.is_menu_chrome('Example Creek State Park'), 'a park name is not menu chrome')

html = '''<!DOCTYPE html><html><head><title>STATE PARKS MENU</title></head><body>
<h1>STATE PARKS MENU</h1>
<h2>Example Creek State Park</h2>
<p>A made-up park page used only as a fixture.</p>
</body></html>'''
vis = R.visible_of(html.encode(), {'content-type': 'text/html'}, 'https://example.gov/parks/example-creek')
nm = R.best_name_of(vis['title'], vis['heading'], vis.get('og') or '', vis.get('jsonld') or '')
check(vis['heading'] == 'Example Creek State Park',
      'the heading skips the menu and takes the next real heading')
check(nm['best'] == 'Example Creek State Park',
      'the best name is the real heading, not STATE PARKS MENU')
check('MENU' not in str(nm.get('best') or '').upper(),
      'the best name does not contain MENU')

# only a menu, no other heading
html2 = '''<!DOCTYPE html><html><head><title>STATE PARKS MENU</title></head><body>
<h1>STATE PARKS MENU</h1>
<p>A made-up page with no park heading.</p>
</body></html>'''
vis2 = R.visible_of(html2.encode(), {'content-type': 'text/html'}, 'https://example.gov/parks/none')
nm2 = R.best_name_of(vis2['title'], vis2['heading'], vis2.get('og') or '', vis2.get('jsonld') or '')
check(nm2['best'] is None or 'MENU' not in str(nm2['best']).upper(),
      'a page that is only a menu does not use the menu as the name')

# existing disagreeing title/heading trap still disagrees
html3 = (ROOT / 'tests/fixtures/park-pages/pages/trap-title.html').read_bytes()
vis3 = R.visible_of(html3, {'content-type': 'text/html'}, 'https://example.gov/foo')
nm3 = R.best_name_of(vis3['title'], vis3['heading'], '', '')
check(nm3['best'] is None and nm3.get('disagree') is True,
      'the existing disagreeing title/heading trap is unchanged')

print('ALL PASS' if not FAILS else 'SOME FAILED')
sys.exit(1 if FAILS else 0)
