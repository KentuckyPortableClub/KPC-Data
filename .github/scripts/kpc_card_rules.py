#!/usr/bin/env python3
"""EVIDENCE-CARD SORTING RULES (KPC owner, 2026-11-17; Handoff 3 proof 3, the rules written in Handoff 2 "Evidence card per
problem park"). Plain code, one function per sort, each returning the one-line reason or None. Nothing here fetches, writes or
applies anything: a card goes in, a sort and a reason come out.

  NO ACTION            nothing at the pin and already checked within 90 days (a person's NO also stands here)
  EASY FIX             a pin typo explains the offset; a multi-state park measured in one state only
  PROPOSE JOIN         same unique name, pin inside, acres within 20%, not an easement, not held by another park
  NO OFFICIAL OUTLINE  a site inside a forest or park with no record of its own (never take the bigger surrounding place)
  NEEDS PERSON         record held by two parks, pin more than 14 km off, acres far off, anything unsure

The order is fixed: a person's NO first (it stands), then the NEEDS PERSON stops, then EASY FIX, PROPOSE JOIN, NO OFFICIAL OUTLINE,
NO ACTION; a card that none of them claims is NEEDS PERSON ("unsure"), never dropped.

A card is a dict (kpc_evidence_card.build_card makes one from stored files):
  ref, name, checked (YYYY-MM-DD), person_no (text or ''), pin_typo (bool), multistate_one_state (bool), inside_bigger (name or ''),
  nothing_at_pin (bool), official_acres (number or None), unsure (list of plain reasons),
  candidate: None or {name, km (distance pin->record, 0 = pin inside), acres, easement (bool), held_by (ref or ''),
                      held_by_count (int), name_unique (bool, default True), kind}
  python3 kpc_card_rules.py --selftest"""
import datetime as _dt, re, sys

SORTS = ('NO ACTION', 'EASY FIX', 'PROPOSE JOIN', 'NO OFFICIAL OUTLINE', 'NEEDS PERSON')
FAR_KM = 14.0          # pin more than 14 km off the record -> a person
ACRES_JOIN = 0.20      # acres within 20% for a join
ACRES_FAR = (0.5, 2.0) # outside half / double -> "acres far off"
RECENT_DAYS = 90       # checked within 90 days -> not listed again
BIG_KIND = re.compile(r'forest|national park|state park|provincial park|wilderness|grassland|recreation area|wildlife (management )?area|refuge|reserve', re.I)
EASEMENT = re.compile(r'easement|servitude|conservation agreement', re.I)


def norm_name(s):
    s = re.sub(r'&', ' and ', str(s or '').lower())
    s = re.sub(r"[^a-z0-9 ]+", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def _days_since(day, today):
    try: return (today - _dt.date.fromisoformat(str(day)[:10])).days
    except (TypeError, ValueError): return None


def _cand(card): return card.get('candidate') or None


def person_no(card, today=None):
    """A person's NO stands: never proposed again, never listed again."""
    n = str(card.get('person_no') or '').strip()
    return f"a person's NO stands ({n[:120]})" if n else None


def needs_person(card, today=None):
    """Record held by two parks (or by another park), pin more than 14 km off, acres far off, an easement named alike."""
    c = _cand(card)
    if not c: return None
    if int(c.get('held_by_count') or 0) >= 2: return f"record {c.get('name')!r} is held by {c.get('held_by_count')} parks: a person decides"
    if c.get('held_by'): return f"record {c.get('name')!r} is already held by {c['held_by']}: a person decides"
    km = c.get('km')
    if isinstance(km, (int, float)) and km > FAR_KM: return f"pin is {km:g} km from {c.get('name')!r} (more than {FAR_KM:g} km): a person decides"
    oa, ca = card.get('official_acres'), c.get('acres')
    same = norm_name(c.get('name')) == norm_name(card.get('name'))
    if same and oa and ca and not (ACRES_FAR[0] <= ca / oa <= ACRES_FAR[1]) and not card.get('inside_bigger'):
        return f"acres far off: record {ca:g} ac against the official {oa:g} ac"
    if c.get('easement') or EASEMENT.search(f"{c.get('name') or ''} {c.get('kind') or ''}"):
        return f"{c.get('name')!r} is an easement: never joined by name alone"
    return None


def easy_fix(card, today=None):
    if card.get('pin_typo'): return 'a pin typo explains the offset (the corrected pin falls inside the record)'
    if card.get('multistate_one_state'): return 'a multi-state park measured in one state only'
    return None


def propose_join(card, today=None):
    c = _cand(card)
    if not c or card.get('inside_bigger'): return None
    if norm_name(c.get('name')) != norm_name(card.get('name')) or c.get('name_unique') is False: return None
    if c.get('km') not in (0, 0.0): return None
    oa, ca = card.get('official_acres'), c.get('acres')
    if not (oa and ca) or abs(ca - oa) / oa > ACRES_JOIN: return None
    return f"same unique name, pin inside, acres {ca:g} against the official {oa:g} (within 20%), not an easement, not held by another park"


def no_official_outline(card, today=None):
    big = card.get('inside_bigger') or ''
    c = _cand(card)
    if not big and c and c.get('km') in (0, 0.0) and norm_name(c.get('name')) != norm_name(card.get('name')) \
            and BIG_KIND.search(f"{c.get('name') or ''} {c.get('kind') or ''}"):
        big = c.get('name')
    if big: return f"the pin is inside {big}, which is not this park: no record of its own (never take the bigger surrounding place)"
    return None


def no_action(card, today=None):
    if not card.get('nothing_at_pin') or _cand(card): return None
    d = _days_since(card.get('checked'), today or _dt.date.today())
    if d is None or d > RECENT_DAYS or d < 0: return None
    return f"nothing official at the pin; checked {card.get('checked')} ({d} days ago, within {RECENT_DAYS})"


ORDER = (('NO ACTION', person_no), ('NEEDS PERSON', needs_person), ('EASY FIX', easy_fix), ('PROPOSE JOIN', propose_join),
         ('NO OFFICIAL OUTLINE', no_official_outline), ('NO ACTION', no_action))


def sort_card(card, today=None):
    """(sort, reason, rule function name). Never None: a card no rule claims is NEEDS PERSON."""
    today = today or _dt.date.today()
    for sort, fn in ORDER:
        why = fn(card, today)
        if why: return sort, why, fn.__name__
    u = '; '.join(card.get('unsure') or []) or ('a record is near the pin but no rule fits it' if _cand(card) else
                                                 'nothing at the pin, and not checked within 90 days')
    return 'NEEDS PERSON', f'unsure: {u}'[:300], 'unsure'


def _selftest():
    t = _dt.date(2026, 11, 17); ok = True
    base = dict(ref='US-1', name='Pine Lake Park', checked='2026-11-10', official_acres=100.0)
    cases = [
        ({**base, 'person_no': 'NO 2026-11-16', 'candidate': dict(name='Pine Lake Park', km=0, acres=100)}, 'NO ACTION', "a person's NO stands"),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=100, held_by='US-2')}, 'NEEDS PERSON', 'held by another park'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=100, held_by_count=2)}, 'NEEDS PERSON', 'held by two parks'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=20, acres=100)}, 'NEEDS PERSON', 'more than 14 km'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=400)}, 'NEEDS PERSON', 'acres far off'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=100, easement=True)}, 'NEEDS PERSON', 'easement never by name alone'),
        ({**base, 'pin_typo': True}, 'EASY FIX', 'pin typo'),
        ({**base, 'multistate_one_state': True}, 'EASY FIX', 'multi-state'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=110)}, 'PROPOSE JOIN', 'join'),
        ({**base, 'candidate': dict(name='Pine Lake Park', km=0, acres=125)}, 'NEEDS PERSON', 'acres 25% off: not a join'),
        ({**base, 'candidate': dict(name='Big Woods National Forest', km=0, acres=90000)}, 'NO OFFICIAL OUTLINE', 'never the bigger place'),
        ({**base, 'inside_bigger': 'Wood Buffalo National Park'}, 'NO OFFICIAL OUTLINE', 'inside a bigger area'),
        ({**base, 'nothing_at_pin': True}, 'NO ACTION', 'nothing at pin, recent'),
        ({**base, 'nothing_at_pin': True, 'checked': '2026-06-01'}, 'NEEDS PERSON', 'nothing at pin, old check'),
        ({**base}, 'NEEDS PERSON', 'no evidence at all'),
    ]
    for card, want, what in cases:
        got = sort_card(card, t)
        good = got[0] == want and bool(got[1])
        ok &= good
        print(('PASS ' if good else 'FAIL ') + f'{what}: {got[0]} ({got[1][:80]})')
    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]: sys.exit(_selftest())
    print(__doc__)
