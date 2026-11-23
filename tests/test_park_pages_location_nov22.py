#!/usr/bin/env python3
"""22 Nov 2026 (owner: "the address and directions seem very low"): the reader's address and directions finders.
Invented pages only. Each check fails on the finders before this change."""
import pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_park_pages_rules as R  # noqa: E402

bad = []


def check(name, ok):
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        bad.append(name)


def addr(t):
    return [a['text'] for a in R.addresses_in(t)]


check('a numbered highway address split over two lines is found and cut at the ZIP',
      addr('Park\n12345 Highway 999\nTestville, KY 40000\nTest County Lodge (18 miles from park)') == ['12345 Highway 999, Testville, KY 40000'])
check('a County Road address with direction words is found',
      addr('4321 S. County Road 275 W. Testburg, IN 47000 Phone 555-0100') == ['4321 S. County Road 275 W. Testburg, IN 47000'])
check('a farm-to-market road address is found',
      addr('Find us at 1500 FM 9999, Test Falls, TX 78000.') == ['1500 FM 9999, Test Falls, TX 78000'])
check('a full state name before the ZIP counts',
      addr('Headquarters 2680 Test Trace Parkway, Testtown, Mississippi 38000. Open daily.') == ['2680 Test Trace Parkway, Testtown, Mississippi 38000'])
check('the phone, email or "link to this page" after the ZIP is cut off',
      addr('Contact\n7234 Old Test Road SW Testdon, IN 47100 Link to this page: example.gov/test') == ['7234 Old Test Road SW Testdon, IN 47100'])
check('the words just before an address give its role (visitor center)',
      [a['role'] for a in R.addresses_in('Visitor Center: 10 Test Lane, Testville, KY 40000')] == ['visitor-centre'])
check('a P.O. box over two lines is a mailing address',
      [(a['text'], a['role']) for a in R.addresses_in('Mailing address\nPO Box 12\nTest Park, TX 79000')] == [('PO Box 12, Test Park, TX 79000', 'mailing')])
check('still silent: numbers and a street word with no ZIP are not an address',
      addr('Call 555-1234. Our 25 years of service on Main Street.') == [] and addr('Meet at the gate.\nNo ZIP here.') == [])

menu = ('Directions\nHours and seasons\nReservations\nFees and passes\nAlerts\nDirections\n'
        'From I-99 take exit 642 and go north on US-99 for 3 miles to the park entrance on Test Road.\nHours\nOpen daily')
d = R.directions_of(menu) or {}
check('a "Directions" menu item is skipped; the real directions under the second heading are kept',
      d.get('sent', '').startswith('From I-99 take exit 642') and 'I-99' in d.get('roads', []) and 'Test Road' in d.get('roads', []))
d = R.directions_of('Test Marsh Wildlife Area\nNorth Unit: Find it from State Highway 99 (Testville) and go East on 222nd Ave for one mile.') or {}
check('a "Find it from..." sentence with no heading is directions; numbered roads and the town in brackets are kept',
      'State Highway 99' in d.get('roads', []) and '222nd Ave' in d.get('roads', []) and 'Testville' in d.get('towns', [])
      and 'State Highway' not in d.get('roads', []))
d = R.directions_of('Test Wildlife Area is a 135-acre property located 2 miles north of Testlake off Testby Road in Test County.') or {}
check('a "located 2 miles north of..." sentence is directions; the town after "north of" is kept, the county is not',
      d.get('roads') == ['Testby Road'] and d.get('towns') == ['Testlake'])
d = R.directions_of('Find it 8 miles northwest of Testette off of Highway V just west of Interstate 99/94.') or {}
check('a lettered highway counts and "Interstate" is not a town',
      'Highway V' in d.get('roads', []) and 'Interstate' not in d.get('towns', []))
check('a "Directions:" line is directions',
      ((R.directions_of('Directions: Take I-99 to exit 29 and follow signs for 4 miles.') or {}).get('roads') or []) == ['I-99', 'exit 29'])
check('still silent: a page with no way to get there has no directions',
      R.directions_of('Welcome to the park. We have trails and picnic tables.') is None)

# 22 Nov 9 PM (owner: "dont think it is doing the best job"): Canada and escaped page code
check('a Canadian address with a province and postal code is found and cut at the postal code',
      addr('c/o Test Falls Provincial Park PO Box 252 4853 Highway 11/17 Testfalls, ON P0T 1W0 Phone 807-555-0100') == ['4853 Highway 11/17 Testfalls, ON P0T 1W0'])
check('a concession road address is found', addr('Physical Address: 4998 Concession Road 7 Testton, ON L9R 1W1') == ['4998 Concession Road 7 Testton, ON L9R 1W1'])
check('a French address is found', addr('1234, chemin du Lac-Test, Saint-Test (Québec) J0T 1A0') == ['1234, chemin du Lac-Test, Saint-Test (Québec) J0T 1A0'])
check('an address inside escaped page code is read clean',
      addr('Test Landmark &lt;p&gt; &lt;strong&gt;Mailing:&lt;/strong&gt; PO Box 103&lt;br&gt; Testbay, NL A0K 4H0') == ['PO Box 103, Testbay, NL A0K 4H0'])
check('a plain Box address with a full province name is found', addr('Box 130, Testville, Saskatchewan S0K 2B0') == ['Box 130, Testville, Saskatchewan S0K 2B0'])
d = R.directions_of('Le parc est situé à 30 km de Testville par la route 132.') or {}
check('French directions in kilometres name the road and the town', d.get('roads') == ['route 132'] and d.get('towns') == ['Testville'])
d = R.directions_of('Located 30 km north of Testtown on Highway 3.') or {}
check('"located 30 km north of" counts as directions', d.get('roads') == ['Highway 3'] and d.get('towns') == ['Testtown'])

# 22 Nov 11 PM (owner: "have you even look at the weblinks"): a point printed as two labelled lines
pts = [(round(c['lat'], 4), round(c['lon'], 4)) for c in R.html_coords('', 'Location Info\nLatitude: 51.8027° N\nLongitude: -106.4602° W')]
check('a point printed as Latitude / Longitude lines (with N and W) is read', pts == [(51.8027, -106.4602)])
pts = [(round(c['lat'], 4), round(c['lon'], 4)) for c in R.html_coords('', 'Lat: 44.5012, Long: 80.2010 W')]
check('Lat / Long with a W letter gives a west (negative) longitude', pts == [(44.5012, -80.201)])

tool = ROOT / '.github' / 'scripts' / 'pc' / 'kpc_reread_location.py'
r = subprocess.run([sys.executable, '-I', str(tool), '--selftest'], capture_output=True, text=True)
check('the PC tool marks only own pages with no address, point or directions for reading again, once',
      r.returncode == 0 and 'ALL PASS' in r.stdout)

print('ALL PASS' if not bad else f'{len(bad)} FAIL')
sys.exit(1 if bad else 0)
