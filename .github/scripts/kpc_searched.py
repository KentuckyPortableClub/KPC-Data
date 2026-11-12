#!/usr/bin/env python3
"""SEARCHED-PARK MEMORY (KPC owner, 2026-11-12: "I dont want to be searching same park").
data/intake/searched-parks.json = {"about": ..., "parks": {ref: [{"date": "YYYY-MM-DD", "search": "outline | pin", "result": "found-source | official-pin |
hand-download | nothing-found", "where": "who searched + the file"}, ...]}}. A park searched within DAYS (90) (or, on the world list, its whole country: "areas") is skipped by the
park pickers (park detective, GIS hunter) unless a NEW source appeared for its area after that search: a row in any
data/intake/queue*.json (not a *hold* file) whose 'added' date is later and whose area is the park's area (or its country).
Reads only; never fetches."""
import datetime, json, pathlib

DAYS = 90
FILE = pathlib.Path('data/intake/searched-parks.json')


def _load(p):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return None  # noqa: BLE001


def _day(s):
    try: return datetime.date.fromisoformat(str(s)[:10])
    except Exception: return None  # noqa: BLE001


def new_source_dates(folder='data/intake'):
    """area -> newest 'added' date of a probe-able queue row (queue.json + split files, never the hold file)."""
    out = {}
    for f in sorted(pathlib.Path(folder).glob('queue*.json')):
        if 'hold' in f.name: continue
        for r in ((_load(f) or {}).get('rows') or []):
            a, d = str((r or {}).get('area') or ''), _day((r or {}).get('added')) if isinstance(r, dict) else None
            if a and d and d > out.get(a, datetime.date.min): out[a] = d
    return out


class Searched:
    def __init__(self, file=None, folder='data/intake', today=None, days=None):
        self.parks, self.areas = {}, {}
        files = [pathlib.Path(file)] if file else sorted(FILE.parent.glob('searched-parks*.json'))   # the main file + its splits (1 MB cap)
        for f in files:
            d = _load(f) or {}
            for k, v in (d.get('parks') or {}).items(): self.parks.setdefault(k, []).extend(v if isinstance(v, list) else [])
            for k, v in (d.get('areas') or {}).items(): self.areas.setdefault(k, []).extend(v if isinstance(v, list) else [])
        self.new = new_source_dates(folder)
        self.today = today or datetime.date.today(); self.days = DAYS if days is None else days

    def skip(self, ref, area='', kind='outline'):
        """'' = search it; else the reason it is skipped (a search of this kind within DAYS, no new source since). kind: outline
        (layer / boundary hunts: the park pickers) or pin (official-point hunts). An entry with no 'search' counts as outline."""
        cc = ref.split('-')[0]
        ents = self.parks.get(ref) or ([] if cc in ('US', 'CA') else self.areas.get(cc) or [])   # world list: a country searched as a whole
        ds = [d for d in (_day(x.get('date')) for x in ents if isinstance(x, dict) and (x.get('search') or 'outline') == kind) if d]
        if not ds: return ''
        last = max(ds)
        if (self.today - last).days > self.days: return ''
        for a in {area, cc, ('US' if cc == 'US' else ''), ('CA' if cc == 'CA' else '')} - {''}:
            if self.new.get(a) and self.new[a] > last: return ''
        return f'searched {last.isoformat()} (within {self.days} days), no new source for {area or cc} since'
