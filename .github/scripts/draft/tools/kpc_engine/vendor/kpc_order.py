#!/usr/bin/env python3
"""ONE WORK ORDER FOR EVERY PILE (chat 10, Oct 30 2026; Brandon 12:40 + 12:44 PM: 'Canada and USA to front of the line ... North
America express lane'). rank() = 0 US + Canada, 1 rest of North America (Mexico, Central America, Caribbean, Greenland, St Pierre),
2 world stages W1-W10, 3 everyone else. Used to SORT queues (intake, layer collector, look-ups, morning list); it never drops anything."""
import json, re

NA = set('MX CR PA BZ HN GT SV NI DO PR VI KY BS JM HT CU TT BB LC VC GD AG KN DM AW CW SX BQ TC VG AI MS BM GP MQ BL MF GL PM'.split())
W10 = ['GB', 'AU', 'JP', 'DE', 'PL', 'FR', 'ES', 'IT', 'NO', 'NL']   # notes/world-stages.md W1-W10
CODE = re.compile(r'\b(?:W-)?([A-Z]{2})-(?:[0-9]{3,5}|[A-Z]{2})\b|\bW-([A-Z]{2})\b')


def rank_cc(cc):
    cc = (cc or '').upper()
    if cc in ('US', 'CA', 'K', 'VE'): return (0, 0)   # POTA US = US-/K-, Canada = CA-/VE- in some lists
    if cc in NA: return (1, 0)
    if cc in W10: return (2, W10.index(cc))
    return (3, 0)


def rank(thing):
    """Best (lowest) rank of any park ref / area code found in a string, dict or list."""
    s = thing if isinstance(thing, str) else json.dumps(thing, ensure_ascii=False)
    codes = [a or b for a, b in CODE.findall(s)]
    return min((rank_cc(c) for c in codes), default=(4, 0))
