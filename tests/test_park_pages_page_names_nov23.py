#!/usr/bin/env python3
"""23 Nov 2026, from the owner's own run (2:30 PM: "Before I waste more time want to see if the park page reader actually getting
the right stuff", "Just look at my pc files"). Three things the new reads showed:
 1. Parks Canada's heritage directory (385 parks): the page's menus ('Language selection') come before its own h1, and the
    title says 'Parks Canada - X National Historic Site of Canada': the name was lost. Now the h1 wins over earlier h2/h3
    menus, those menu headings are not names, and 'Parks Canada - ' / ' of Canada' are cut.
 2. Wisconsin DNR: the h1 is 'Rib Mountain', the title 'Rib Mountain State Park | Wisconsin DNR': the full name is taken.
 3. Minnesota DNR (253 parks): the page's h1 is still a script template ("' + park.name + '"): it is a page that builds
    itself and goes to the browser.
Checked on 100 of the owner's kept pages: 92 the same, 4 better, 0 worse. Invented pages here. Prints PASS / FAIL."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R  # noqa: E402
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


WORDS = '<p>' + 'Words about the place, its history and its visitors. ' * 12 + '</p>'


def name_of(html, pota_name, url='https://www.pc.gc.ca/apps/dfhd/page_nhs_eng.aspx?id=1', typ='National Historic Site'):
    v = R.visible_of(html.encode(), {'content-type': 'text/html'}, url, [])
    pg = {'kind': 'html', 'final': url, 'url': url, 'text': v['text'], 'html': v.get('html') or '', 'title': v.get('title'),
          'heading': v.get('heading'), 'og': v.get('og'), 'jsonld': v.get('jsonld'), 'links': v.get('links') or [],
          'headings': v.get('headings') or []}
    f = R.build_facts('CA-1', 'CA', {'name': pota_name, 'type': typ, 'pin': [None, None], 'link': url, 'qsos': 1}, {},
                      {'url': url, 'from': 'pota'}, [pg], '2026-11-23', [], 'own', 'x', read_blocks=True)
    return (f.get('name') or {}).get('best'), (f.get('name') or {}).get('vs_pota')


PC = ('<html><head><title>Parks Canada - Otter Point Lighthouse National Historic Site of Canada</title></head><body>'
      '<h2>Language selection</h2><h2>Menus</h2><h2>Topics menu</h2><h2>You are here:</h2><h1></h1>'
      '<h1>Otter Point Lighthouse National Historic Site of Canada</h1>' + WORDS + '</body></html>')
best, vs = name_of(PC, 'Otter Point Lighthouse National Historic Site')
check(f"Parks Canada: the h1 after the menus, less 'of Canada' = the park's own name (got {best!r}, {vs})",
      best == 'Otter Point Lighthouse National Historic Site' and vs == 'same')
check("'Language selection', 'Menus', 'You are here:' are menus, not names", all(R.is_menu_chrome(x) for x in ('Language selection', 'Menus', 'You are here:')))
check("'Parks Canada - ' and ' of Canada' are cut from a title", R.cut_tail('Parks Canada - Fort X National Historic Site of Canada') == 'Fort X National Historic Site')
WI = ('<html><head><title>Heron Ridge State Park | Wisconsin DNR</title></head><body><h2>Main navigation</h2>'
      '<h2>Parks_Property Landing Page_Heron Ridge</h2><h2>Breadcrumb</h2><h1>Heron Ridge</h1><h2>State Park</h2>' + WORDS + '</body></html>')
best, vs = name_of(WI, 'Heron Ridge State Park', url='https://dnr.wisconsin.gov/topic/parks/heronridge', typ='State Park')
check(f"Wisconsin: h1 'Heron Ridge' + title 'Heron Ridge State Park | Wisconsin DNR' = the full name (got {best!r}, {vs})",
      best == 'Heron Ridge State Park' and vs == 'same')
OTHER = ('<html><head><title>Otter Creek State Park | Agency</title></head><body><h1>Otter Creek</h1>' + WORDS + '</body></html>')
best, vs = name_of(OTHER, 'Otter Creek State Park', url='https://x.zz.invented.gov/p', typ='State Park')
check('an h1 alone still names the park (same core)', vs in ('same', 'same-core'))
MN = ('<html><head><title>Minnesota State Park | Minnesota DNR</title></head><body><script>var t = "<h1>\' + park.name + \'</h1>";</script>'
      '<h1>\' + park.name + \'</h1>' + WORDS + '</body></html>')
check("Minnesota: an h1 that is still a script template = a page that builds itself", R.unfilled_template(MN))
check('a plain h1 is not a template', not R.unfilled_template(OTHER) and not R.unfilled_template(PC))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
