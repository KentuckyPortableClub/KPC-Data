#!/usr/bin/env python3
"""Hand copy sources, 21 Nov 2026 (job E): propose each hand copy's source page from what the bots saved, for a person to
review. The review file (park numbers) is PRIVATE and never committed; counts by state are public; no live data is written.
Offline, invented parks. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / '.github/scripts/draft/tools/kpc_hand_copies'
sys.path.insert(0, str(TOOL))
import kpc_hand_copy_sources as S  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


r = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_hand_copy_sources.py'), '--selftest'], capture_output=True, text=True)
check('the source helper self-test passes', r.returncode == 0 and 'SELF-TEST PASSED' in r.stdout)
check('the agency\'s rounding agrees, another size does not', S.agrees(2000, 2004) and not S.agrees(2000, 2100))
src = (TOOL / 'kpc_hand_copy_sources.py').read_text()
check('it fetches nothing', not any(w in src for w in ('urllib.request', 'requests.', 'http.client', 'kpc_manners', 'socket')))
gi = (ROOT / '.gitignore').read_text()
check('PRIVATE review files are never committed', 'PRIVATE-*' in gi and 'hand-copy-sources-out/' in gi)
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'acres.json').write_text(json.dumps({'US-9001': {'acres': 150, 'how': 'hand copy (ZZ Parks, page not given)', 'source_url': ''}}))
    facts = {'parks': {'US-9001': {'area': 'US-ZZ', 'page': {'url': 'https://zz.invented.example/p', 'status': 200, 'own_page': 'own',
                                                             'sizes': [{'acres': 150.2, 'as': '150 acres', 'total': True}]}}}}
    (t / 'pf.json').write_text(json.dumps(facts))
    rows, doc = S.run(str(t / 'acres.json'), None, str(t / 'pf.json'))
    check('park facts\' page is used when the page reader files are not given',
          rows[0]['match'] == 'yes' and rows[0]['from'] == 'own page (park facts)' and rows[0]['quoted_size_line'] == '150 acres')
    check('the counts file holds counts only', 'US-9001' not in json.dumps(doc))
    check('the review file has the columns a reviewer needs',
          S.COLS[:4] == ['park', 'state', 'hand_acres', 'proposed_source_url'] and 'quoted_size_line' in S.COLS and 'match' in S.COLS)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
