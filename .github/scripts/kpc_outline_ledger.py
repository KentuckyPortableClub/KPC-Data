#!/usr/bin/env python3
"""OUTLINE-SOURCE LEDGER READER (Nov 7 2026; Brandon 7:30 PM CST: 'no reason to look for same park over and over when we might
already have it'). data/waiting/outline-sources/ledger.json.gz = {about, sources, rows: {ref or ref|area: {area, name, verdict,
outline: [{url, status, why}], pdf, parcel, src, date}}}. A park is SEARCHED when it has a row; it needs another search only when its
verdict is 'nothing found' or a retry, and the row is older than RESEARCH_DAYS (default 60).
  python3 kpc_outline_ledger.py US-0150 [CA-1234 ...]     one line per park
  python3 kpc_outline_ledger.py --summary                 verdict counts per country
Offline, read only. Never fails (a missing ledger = nothing searched yet)."""
import datetime as dt, gzip, json, os, pathlib, sys, collections

LEDGER = pathlib.Path(os.environ.get('OUTLINE_LEDGER') or 'data/waiting/outline-sources/ledger.json.gz')
AGAIN = ('nothing found', 'server down Nov 7: retry later')


def load(path=None):
    p = pathlib.Path(path or LEDGER)
    try:
        raw = gzip.open(p).read() if p.suffix == '.gz' else p.read_bytes()
        return (json.loads(raw) or {}).get('rows') or {}
    except Exception: return {}  # noqa: BLE001


def rows_for(ref, rows=None):
    rows = load() if rows is None else rows
    return [v for k, v in rows.items() if k == ref or k.startswith(ref + '|')]


def verdict(ref, rows=None):
    r = rows_for(ref, rows)
    return '; '.join(dict.fromkeys(f"{x.get('verdict')} ({x.get('date')})" for x in r)) if r else ''


def needs_search(ref, rows=None, today=None, days=None):
    days = int(days or os.environ.get('RESEARCH_DAYS') or 60)
    r = rows_for(ref, rows)
    if not r: return True
    today = today or dt.date.today()
    for x in r:
        if x.get('verdict') not in AGAIN: return False
        try:
            if (today - dt.date.fromisoformat(x.get('date'))).days < days: return False
        except Exception: return False  # noqa: BLE001
    return True


if __name__ == '__main__':
    R = load()
    if '--summary' in sys.argv:
        c = collections.defaultdict(collections.Counter)
        for k, v in R.items(): c[k.split('-')[0]][v.get('verdict')] += 1
        for cc, n in sorted(c.items()): print(cc, sum(n.values()), dict(n.most_common()))
    for ref in [a for a in sys.argv[1:] if not a.startswith('--')]:
        print(ref, verdict(ref, R) or 'not searched yet', '| search again' if needs_search(ref, R) else '| skip (already searched)')
