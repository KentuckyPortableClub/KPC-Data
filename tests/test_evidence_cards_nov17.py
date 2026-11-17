#!/usr/bin/env python3
"""Evidence-card sorting (KPC owner, 2026-11-17; Handoff 3 proof 3). Offline.
  1. one check per sorting rule (kpc_card_rules.py selftest), including: never take the bigger surrounding place, an easement is
     never joined by name alone, a person's NO stands, a record held by another park goes to a person, nothing is ever dropped
  2. the cards are made from stored files only (no request): POTA record from data/parkinfo, the official page from data/docs,
     the key's own words (why-not.json); "pin is inside a bigger area: X" -> NO OFFICIAL OUTLINE, never X
  3. the comparison against the hand answers lists EVERY disagreement with both answers and the rules' reason.
     tests/fixtures/trace-hold-nov17/review-answers-SYNTHETIC.csv is SYNTHETIC (the Nov 16 hand answers were not reachable): it
     proves the comparison, not the agreement. When the manager session drops the public-safe copy in as review-answers.csv, it is
     compared too: the rules must agree on most rows (over half) and every disagreement is printed.
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import datetime, json, pathlib, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
FX = ROOT / 'tests/fixtures/trace-hold-nov17'
sys.path.insert(0, str(S))
ok = True
DAY = datetime.date(2026, 11, 17)   # the answers are judged as on the day they were written


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k): raise OSError('test: no network')
socket.socket.connect = _no_net
import kpc_card_rules as R  # noqa: E402
import kpc_evidence_card as EC  # noqa: E402

r = subprocess.run([sys.executable, '-B', str(S / 'kpc_card_rules.py'), '--selftest'], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if line.startswith(('PASS ', 'FAIL ')): print('   ' + line)
check('1. every sorting rule (kpc_card_rules.py --selftest)', r.returncode == 0 and 'SELFTEST PASS' in r.stdout)
check('1. the sort order is fixed: a person\'s NO, then the NEEDS PERSON stops, then EASY FIX, PROPOSE JOIN, NO OFFICIAL OUTLINE, NO ACTION',
      [f.__name__ for _, f in R.ORDER] == ['person_no', 'needs_person', 'easy_fix', 'propose_join', 'no_official_outline', 'no_action'])

with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    (t / 'data/parkinfo').mkdir(parents=True); (t / 'data/docs').mkdir(parents=True); (t / 'links/data/ca-key').mkdir(parents=True)
    (t / 'data/parkinfo/CA.json').write_text(json.dumps({'parks': {'CA-0663': ['Wood Buffalo Site', 'https://example.gc.ca/p', 'Historic Site', '', '', 59.0, -112.0],
                                                                    'CA-2969': ['Little Fish Natural Area', '', 'Natural Area', '', '', 54.0, -114.0]}}))
    (t / 'data/docs/CA-AB.json').write_text(json.dumps({'parks': {'CA-0663': {'page': 'https://example.gc.ca/p', 'agency': 'Parks Canada', 'checked': '2026-11-01',
                                                                               'map': {'url': '', 'status': 'none'}}}}))
    (t / 'links/data/ca-key/why-not.json').write_text(json.dumps({'parks': {
        'CA-0663': {'st': 'AB', 'tag': 'needs-parcel', 'why': 'the pin is inside a bigger area: Wood Buffalo National Park Of Canada'},
        'CA-2969': {'st': 'AB', 'tag': 'no-layer', 'why': 'no official record found (Natural Area)'}}}))
    st = EC.Stores(t, t / 'links', checked_default='2026-11-11')
    c1 = EC.build_card('CA-0663', st, today=DAY); c2 = EC.build_card('CA-2969', st, today=DAY)
    check(f"2. a card from stored files: POTA record, official page, the key's words ({c1['sources']})",
          c1['pota']['name'] == 'Wood Buffalo Site' and c1['pota']['pin'] == [59.0, -112.0] and c1['official_page']['agency'] == 'Parks Canada'
          and c1['area'] == 'CA-AB' and c1['fetched'] == 0)
    check(f"2. 'pin is inside a bigger area' -> {c1['sort']} ({c1['reason'][:90]})", c1['sort'] == 'NO OFFICIAL OUTLINE' and 'never take the bigger' in c1['reason'])
    check(f"2. nothing at the pin, key checked 2026-11-11 -> {c2['sort']}", c2['sort'] == 'NO ACTION' and c2['reason'])

res = EC.compare(FX / 'review-answers-SYNTHETIC.csv', EC.Stores(), DAY)
print(f"   SYNTHETIC comparison: {res['rows']} rows, {res['agree']} agree, {res['disagree']} disagree")
for d in res['disagreements']: print(f"   disagree {d['ref']}: hand {d['hand']} / rules {d['rules']} ({d['rules_reason'][:100]}) [hand note: {d['hand_note']}]")
check('3. SYNTHETIC answers: the comparison runs on every row and lists every disagreement with both answers and the reason',
      res['rows'] == 20 and res['agree'] + res['disagree'] == 20 and all(d['rules_reason'] and d['hand'] for d in res['disagreements']))
check('3. SYNTHETIC answers: exactly the two rows written to disagree are the ones listed (US-8016, US-8017)',
      sorted(d['ref'] for d in res['disagreements']) == ['US-8016', 'US-8017'])
real = FX / 'review-answers.csv'
if real.exists():
    rr = EC.compare(real, EC.Stores())
    print(f"   Nov 16 hand answers: {rr['rows']} rows, {rr['agree']} agree ({rr['share_agree']}), {rr['disagree']} disagree")
    for d in rr['disagreements']: print(f"   disagree {d['ref']}: hand {d['hand']} / rules {d['rules']} ({d['rules_reason'][:100]})")
    check('3. Nov 16 hand answers: the rules agree on most rows and every disagreement is listed', rr['share_agree'] and rr['share_agree'] > 0.5)
else:
    print('NOTE: tests/fixtures/trace-hold-nov17/review-answers.csv (the public-safe Nov 16 hand answers) is not here yet; only the SYNTHETIC set was compared')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
