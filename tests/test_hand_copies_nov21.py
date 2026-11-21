#!/usr/bin/env python3
"""Hand copies, 21 Nov 2026 (job C): list the hand-copied sizes that do not name their source; counts by state are public,
park numbers private; new lines follow the template (agency + source_url). Offline, invented parks.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED.
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / '.github/scripts/draft/tools/kpc_hand_copies'
sys.path.insert(0, str(TOOL))
import kpc_hand_copies as H  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


r = subprocess.run([sys.executable, '-B', str(TOOL / 'kpc_hand_copies.py'), '--selftest'], capture_output=True, text=True)
check('the hand-copy checker self-test passes', r.returncode == 0 and 'SELF-TEST PASSED' in r.stdout)
check('a hand copy with no page is missing its source', H.missing({'how': 'hand copy (ZZ Parks, page not given)', 'agency': 'ZZ Parks'}) == ['source_url'])
check('a hand copy with its page and agency names its source',
      H.missing({'agency': 'ZZ Parks', 'source_url': 'https://zz.invented.example/p'}) == [])
check("'unknown agency' counts as no agency", 'agency' in H.missing({'agency': 'unknown agency', 'source_url': 'https://zz.invented.example/p'}))
tpl = json.load(open(TOOL / 'hand-copy-template.json', encoding='utf-8'))
check('the template line carries agency and source_url', all(l.get('agency') and str(l.get('source_url', '')).startswith('https://')
                                                            for l in tpl['hand_copies']))
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    facts = {'parks': {'US-9001': {'area': 'US-ZZ', 'size': {'acres': 5, 'witness': 'hand_copy', 'source_url': None}},
                       'US-9002': {'area': 'US-ZZ', 'size': {'acres': 5, 'witness': 'agency_document', 'source_url': None}}}}
    (t / 'pf.json').write_text(json.dumps(facts))
    doc, private = H.check(None, None, str(t / 'pf.json'))
    check('park facts can be read too: only the hand copy is counted', doc['by_state'] == {'US-ZZ': {'hand copies': 1, 'missing a source': 1, 'no agency': 1, 'no source_url': 1}})
    H.write(str(t / 'out'), doc, private)
    check('the public file carries counts only', 'US-9001' not in (t / 'out/hand-copies-missing-source.json').read_text())
    check('the park number goes to the PRIVATE file', 'US-9001' in (t / 'out/PRIVATE-hand-copies-missing-source.csv').read_text())

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
