"""Next round v2 (Quality grade of the next-round bundle, must-fix 1, Nov 5 2026): the Nov 5 mystery intake holds every row with no
pin distance and no registry id or an unchecked candidate (AU-2209, CA-0037, US-9473) and PT-0318 (the official SDF does not clearly
confirm it); counts match the rows; the 7 NTWA rows carry the CAPAD credit (Brandon's answers via Super, 8:55 AM CST Nov 5)."""
import collections, json, pathlib

F = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'waiting' / 'questions' / 'outside-intake-nov5.json'
D = json.load(open(F, encoding='utf-8'))
Q = {r['ref']: r for r in D['questions']}


def test_counts_match_the_rows():
    c = collections.Counter(r['intake'] for r in D['questions'])
    assert D['open'] == len(D['questions']) == 402 and (D['accepted'], D['held']) == (c['accepted'], c['held']) == (169, 233)
    assert sum(1 for r in D['questions'] if r['area'] == 'JP') == 36 and all(r['intake'] == 'held' for r in D['questions'] if r['area'] == 'JP')
    assert '389 outside-agent answers' in D['about'] and '13 JP MLIT A10 crosswalk joins = 402 rows' in D['about'] and '395' not in D['about']
    assert "Brandon's own words, relayed via Super, 8:00 AM CST Nov 5" in D['about'] and '8:55 AM CST Nov 5' in D['about']


def test_held_rows():
    for ref in ('AU-2209', 'CA-0037', 'US-9473', 'PT-0318'):
        assert Q[ref]['intake'] == 'held' and Q[ref]['bot_says'] == 'NOT SURE' and Q[ref]['intake_why'], ref
    assert any('one name only' in w for w in Q['FR-3611']['intake_why'])


def test_no_accepted_row_has_the_gaps():
    for r in D['questions']:
        if r['intake'] != 'accepted': continue
        assert str(r.get('pin_km') or '').strip() != '', r['ref']
        assert 'no registry id' not in str(r.get('agent_flags')), r['ref']
        assert 'not checked' not in str(r.get('evidence')).lower(), r['ref']
        assert r['bot_says'] == 'YES' and r['answer'] is None and not r['decided_by']


def test_ntwa_rows_carry_the_capad_credit():
    for ref in ('AU-7112', 'AU-7113', 'AU-7114', 'AU-7115', 'AU-7117', 'AU-7118', 'AU-7559'):
        r = Q[ref]
        assert r['intake_flags'] == 'credit:CAPAD' and "CAPAD (DCCEEW), CC BY 4.0" in r['outline'] and 'gis.environment.gov.au' in r['layer'], ref
    # rule 3: no row's source layer is WDPA / Protected Planet (SAPAD's own record ids are written 'SAPAD-WDPAID:', the DFFE layer is the source)
    assert not any(h in str(r.get('layer')).lower() for r in D['questions'] for h in ('protectedplanet', 'wdpa'))
