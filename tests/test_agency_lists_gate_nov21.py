#!/usr/bin/env python3
"""Agency-list gate, 21 Nov 2026: licence is not a gate for private matching-only use;
robots.txt blocks only on an explicit Disallow or a file that loaded but could not be parsed.
A 403, 404 or empty robots.txt is no rules (OK). Offline, invented agencies.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
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


good = {
    'enabled': True, 'agency': 'Invented', 'link_kind': 'ZZ page number',
    'source_url': 'https://lists.invented.example/l.csv',
    'licence': 'public domain (invented)', 'licence_ok': True,
    'robots': 'allowed (read 2026-11-21)',
    'terms_url': 'https://lists.invented.example/t', 'format': 'csv',
    'web_id': {'column': 'a'}, 'map': {'layer': 'l', 'field': 'f', 'value': 'v'},
}

check('robots_problem is the new gate helper', callable(getattr(AL, 'robots_problem', None)))
check('a fully checked invented agency may be read', AL.problems(good) == [])
check('licence_ok false is not a gate', AL.problems(dict(good, licence_ok=False)) == [])
check('no licence and no terms_url is not a gate', AL.problems(dict(good, licence='', terms_url='')) == [])
check('no licence_ok field is not a gate', AL.problems({k: v for k, v in good.items() if k != 'licence_ok'}) == [])

for robots, label in (
    ('unreadable (403) = no rules', '403 unreadable = no rules'),
    ('unknown (robots.txt returned 403)', 'old 403 label still means no rules'),
    ('not checked (404 = no rules)', '404 = no rules'),
    ('not checked (robots.txt is empty)', 'empty robots.txt = no rules'),
    ('', 'a blank robots reading is not a Disallow'),
    ('not checked for the exact list path (owner read the host in the browser, 2026-11-21: yes (404 = no rules))',
     'a 404 reading from the research table is not a block'),
    ('not checked for the exact list path (owner read the host in the browser, 2026-11-21, second pass: unreadable (403), no rules)',
     'a second-pass 403 reading is no rules'),
    ('not checked for the exact list path (owner read the host in the browser, 2026-11-21: yes for dataset pages; /api/ disallowed; Crawl-Delay 10)',
     'a Disallow for an unrelated path is not a block'),
):
    check(f'robots {label}: may be read', callable(getattr(AL, 'robots_problem', None)) and AL.robots_problem(robots) is None and AL.problems(dict(good, robots=robots)) == [])

check('explicit Disallow for AI crawlers: refused',
      callable(getattr(AL, 'robots_problem', None)) and AL.robots_problem('disallowed for AI crawlers (owner read it in the browser, 2026-11-21)')
      and any('Disallow' in w for w in AL.problems(dict(good, robots='disallowed for AI crawlers'))))
check('robots.txt loaded but could not be parsed: refused',
      callable(getattr(AL, 'robots_problem', None)) and AL.robots_problem('loaded but could not be parsed')
      and any('could not be parsed' in w for w in AL.problems(dict(good, robots='loaded but could not be parsed'))))

cfg = json.load(open(ROOT / '.github/agency-lists.json', encoding='utf-8'))
ags = cfg['agencies']
check('only the three agencies whose lists tie are on (owner, 22 Nov: agency data needs no approval)',
      {a['agency'] for a in ags if a.get('enabled')} == {'Florida DEP Division of Recreation and Parks (State Parks)', 'Manitoba Parks', 'Washington State Parks'})
n403 = sum(1 for a in ags if '403' in (a.get('robots') or '') and 'no rules' in (a.get('robots') or ''))
check('the 403 robots rows all say no rules (10)', n403 == 10)
check('no row still says unknown (robots.txt returned 403)',
      all('returned 403' not in (a.get('robots') or '') for a in ags))
sk = [a for a in ags if a['agency'].startswith('Saskatchewan')]
check('Saskatchewan AI-only robots rules are recorded, not applied (not a gate block)',
      sk and 'not applied' in sk[0]['robots'] and 'AI' in sk[0]['robots']
      and callable(getattr(AL, 'robots_problem', None)) and AL.robots_problem(sk[0]['robots']) is None
      and not sk[0].get('enabled'))

r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_agency_lists.py'), '--selftest'],
                   capture_output=True, text=True)
check('the agency lists self-test passes', r.returncode == 0 and 'SELF-TEST PASSED' in r.stdout)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
