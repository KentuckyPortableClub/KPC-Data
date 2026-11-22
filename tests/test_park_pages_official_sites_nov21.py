#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026 (owner's ruling, 8:17 PM): the agencies' own sites that are not on a .gov / .gc.ca address
count as official (Canadian provinces and their park agencies, Ontario conservation authorities, cities, state agencies on
.com / .org, land trusts that own the place). Map, wiki and directory sites never do. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


YES = ['https://bcparks.ca/x', 'https://www.ontarioparks.com/park/x', 'https://www.environnement.gouv.qc.ca/biodiversite/x',
       'https://www.sepaq.com/pq/x', 'https://www2.gnb.ca/content/x', 'https://parks.novascotia.ca/park/x', 'https://www.gov.mb.ca/sd/x',
       'https://www.albertaparks.ca/x', 'https://yukon.ca/en/x', 'https://www.trca.ca/parks/x', 'https://www.agfc.com/x',
       'https://tnstateparks.com/parks/x', 'https://www.gastateparks.org/x', 'https://www.state.nj.us/dep/parksandforests/x',
       'https://www.michigandnr.com/x', 'https://www.nature.org/en-us/x']
NO = ['https://en.wikipedia.org/wiki/x', 'https://www.arcgis.com/home/x', 'https://mapcarta.com/x', 'https://www.alltrails.com/x',
      'https://www.stateparks.com/x', 'https://www.protectedplanet.net/x', 'https://notbcparks.ca/x', 'https://bcparks.ca.example.com/x',
      'https://www.nevadawilderness.org/x', 'https://southwestexplorers.com/x']
check('the agencies\' own sites count as official', all(R.official_host(u) for u in YES))
check('map, wiki, directory and look-alike sites do not', not any(R.official_host(u) for u in NO))
check('.gov / .gc.ca / canada.ca still count as before', all(R.official_host(u) for u in
      ('https://www.nps.gov/x', 'https://www.dnr.state.mn.us/x', 'https://parks.canada.ca/x', 'https://www.env.gov.bc.ca/x')))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
