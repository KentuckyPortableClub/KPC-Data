#!/usr/bin/env python3
"""Owner's rulings, 23 Nov 2026 12:51 AM. (1) 'Yes': a page name with the same words as POTA's, calling the place another kind
('Anthony Branch Fishery Area' / 'Anthony Branch State Fish and Wildlife Area'), is the same name ('same-words'). Not when a
word that is not a kind word differs, and never when another park of the area carries the page's name as its own.
(2) 'Yes': the associations' sites that carry their members' park pages count as official (Saskatchewan Regional Parks,
Nebraska's NRD association, Ontario's conservation areas). Invented parks. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import importlib.util, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R
spec = importlib.util.spec_from_file_location('pf', ROOT / '.github/scripts/draft/tools/kpc_park_facts/kpc_park_facts.py')
PF = importlib.util.module_from_spec(spec); spec.loader.exec_module(PF)
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


h = R.name_agreeing
check('same words, another kind: "Otter Branch Fishery Area" is "Otter Branch State Fish and Wildlife Area"',
      h({'heading': 'Main navigation', 'title': 'Otter Branch Fishery Area | | Invented DNR'}, 'Otter Branch State Fish and Wildlife Area')[1] == 'same-words')
check('"Sandhill Forest SNA" is "Sandhill Forest State Natural Area"', h({'heading': 'Sandhill Forest SNA'}, 'Sandhill Forest State Natural Area')[1] in ('same-core', 'same-words'))
check('a word that is not a kind word on one side only still differs (North Unit)', h({'heading': 'Otter Branch Wildlife Area North Unit'}, 'Otter Branch State Wildlife Area') == (None, None))
check('another place still differs', h({'heading': 'Otter Creek Fishery Area'}, 'Otter Branch State Fish and Wildlife Area') == (None, None))
check("never when another park of the area carries the page's name as its own",
      h({'heading': 'Otter Branch State Park'}, 'Otter Branch State Fish and Wildlife Area', {R.norm_written('Otter Branch State Park')}) == (None, None))
check('an exact name is still "same", not "same-words"', h({'heading': 'Otter Branch State Park'}, 'Otter Branch State Park')[1] == 'same')
check('kind words alone never agree', h({'heading': 'Wildlife Areas'}, 'State Wildlife Area') == (None, None))
for u in ('https://saskregionalparks.ca/park/invented', 'https://www.nrdnet.org/invented', 'https://ontarioconservationareas.ca/invented'):
    check('official (owner 23 Nov): ' + u.split('/')[2], R.official_host(u))
check('Wikipedia is still not official', not R.official_host('https://en.wikipedia.org/wiki/Invented'))

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    def park(name, heading):
        return {'area': 'US-ZZ', 'pota': {'name': name, 'type': 'State Park', 'pin': [41.0, -88.0]}, 'asked': {'url': 'https://dnr.invented.gov/' + name[:4]},
                'page': {'read': '2026-11-23', 'kind': 'html', 'host': 'dnr.invented.gov'}, 'own_page': {'is': 'own'},
                'name': {'heading': heading, 'title': '', 'vs_pota': 'differs'}, 'location': {'coords': [], 'addresses': [], 'directions': None}}
    (t / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': {
        'US-9901': park('Otter Branch State Fish and Wildlife Area', 'Otter Branch Fishery Area'),
        'US-9902': park('Heron Marsh State Wildlife Area', 'Heron Marsh State Park'), 'US-9903': park('Heron Marsh State Park', 'Heron Marsh State Park')}}))
    pages, _ = PF.read_pages(str(t))
    check('park facts: saved facts read before the ruling now say same-words', pages['US-9901']['name_vs_pota'] == 'same-words')
    check("park facts: a page that carries ANOTHER park's own name stays differs", pages['US-9902']['name_vs_pota'] == 'differs' and pages['US-9903']['name_vs_pota'] == 'same')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
