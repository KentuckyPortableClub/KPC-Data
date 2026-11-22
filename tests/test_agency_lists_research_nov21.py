#!/usr/bin/env python3
"""Agency park lists from the owner's research table, 21 Nov 2026 (job D).
Every agency of the table is in the config, each OFF with a one-line reason; a licence is not a gate for private matching-only
use; robots.txt blocks only on an explicit Disallow or a file that loaded but could not be parsed (a 403, 404 or empty file is
no rules); a saved-copies-only or never-contact host is still refused.
Offline, invented hosts. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_agency_lists as AL  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


cfg = json.load(open(ROOT / '.github/agency-lists.json', encoding='utf-8'))
ags = cfg['agencies']
check('the research table is in the config (at least 90 agencies)', len(ags) >= 90)
check('only the three agencies whose lists tie are on (owner, 22 Nov: agency data needs no approval)',
      {a['agency'] for a in ags if a.get('enabled') is True} == {'Florida DEP Division of Recreation and Parks (State Parks)', 'Manitoba Parks', 'Washington State Parks'} and all(a.get('enabled') in (True, False) for a in ags))
check('every agency has a one-line reason starting "off:" (or "on (owner, 22 Nov" for the three)',
      all(str(a.get('status', '')).startswith('on (owner, 22 Nov 2026' if a.get('enabled') else 'off: ') and '\n' not in a['status'] and len(a['status']) > 10 for a in ags))
check('every agency names when and how it was checked', all('2026-11-21' in str(a.get('checked', '')) for a in ags))
check('agency names are unique (one crosswalk file each)', len({AL.slug(a['agency']) for a in ags}) == len(ags))
for k in ('Parks Canada', 'OR State Parks', "Parks Canada (Canada's Historic Places)", 'MI DNR', 'AR Game and Fish', 'NY State Parks',
          'US Forest Service', 'TX Parks and Wildlife', 'SC DNR', 'ME Parks', 'Sepaq'):
    check(f'the earlier entry "{k}" is kept with its link kind', any(a['agency'] == k and (a['link_kind'] or k == 'Parks Canada') for a in ags))
sk = [a for a in ags if a['agency'].startswith('Saskatchewan')]
check('Saskatchewan stays off; AI-only robots rules are recorded, not applied', sk and not sk[0].get('enabled') and 'not applied' in sk[0]['robots'] and 'AI' in sk[0]['robots'] and not sk[0]['robots'].startswith('allowed'))
check('every source is an https address or empty', all(not a['source_url'] or a['source_url'].startswith('https://') for a in ags))
check('licence_ok is true only where the licence text was read (4 agencies)', sum(1 for a in ags if a.get('licence_ok') is True) == 4)
check('an agency with no official list has no source', all(a['source_url'] == '' for a in ags if 'no official list' in a['status']))
check('no entry names a WDPA source', not AL.WDPA.search(json.dumps(ags)))
import kpc_host_rules as HR  # noqa: E402
blocked = [a for a in ags if a['source_url'] and not HR.host_ok(a['source_url'])[0]]
check('every source on a saved-copies-only host says so in its reason, or is an owner-switched-on list read by the keeper only',
      blocked and all('saved copies only' in a['status'] or (a.get('enabled') and a['status'].startswith('on (owner, ') and 'store keeper only' in a['status']) for a in blocked))

good = {'enabled': True, 'agency': 'Invented', 'link_kind': 'ZZ page number', 'source_url': 'https://lists.invented.example/l.csv',
        'licence': 'public domain (invented)', 'licence_ok': True, 'robots': 'allowed (read 2026-11-21)',
        'terms_url': 'https://lists.invented.example/t', 'format': 'csv', 'web_id': {'column': 'a'}, 'map': {'layer': 'l', 'field': 'f', 'value': 'v'}}
check('a fully checked invented agency may be read', AL.problems(good) == [])
check('licence not checked as allowing our use: still allowed (licence is not a gate)', not any('licence' in w.lower() for w in AL.problems(dict(good, licence_ok=False))))
check('no licence_ok at all: still allowed (licence is not a gate)', not any('licence' in w.lower() for w in AL.problems({k: v for k, v in good.items() if k != 'licence_ok'})))
check('robots.txt 403 unreadable = no rules: still allowed', AL.problems(dict(good, robots='unreadable (403) = no rules')) == [])
check('robots.txt disallows AI crawlers: refused', any('Disallow' in w or 'robots' in w for w in AL.problems(dict(good, robots='disallowed for AI crawlers'))))
for u in ('https://services5.arcgis.com/x/ArcGIS/rest/services/L/FeatureServer/0', 'https://services.arcgis.com/x/arcgis/rest/services/L/FeatureServer/0',
          'https://apps.fs.usda.gov/arcx/rest/services/EDW/x/MapServer/0', 'https://ncnhde.natureserve.org/l.csv'):
    check(f'host {u.split("/")[2]} is never read', AL.problems(dict(good, source_url=u)) != [])
r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_agency_lists.py'), '--selftest'], capture_output=True, text=True)
check('the agency lists self-test passes', r.returncode == 0 and 'SELF-TEST PASSED' in r.stdout)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
