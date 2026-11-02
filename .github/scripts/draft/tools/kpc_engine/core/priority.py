"""US + Canada work order (club, PRIORITY_US_CA_chat10.md, Nov 1). Open US/CA parks are worked in this order, so a run
that stops at --max-minutes (exit 3) has already done the parks that matter most:

  1 state trails (and provincial trails)          -- national trails are left to the club's trail-line tool (rank 7)
  2 state parks + state recreation areas (and provincial parks)
  3 historic sites, national and state            -- record-number and parcel tricks (Hard Look) pay off here
  4 everything else (state forests, WMAs, heritage areas, national parks, refuges, ...)
  5 county, city and regional parks
  6 BLM areas
  7 national scenic / historic trails             -- covered elsewhere; done last
World rows keep rank 4, so they sit with the US/CA middle of the list. The engine still decides nothing: this only
changes the ORDER of the work, never what is found."""
import json, pathlib, re

WORK_ORDER = pathlib.Path(__file__).resolve().parents[1] / 'config' / 'work_order.json'
_SEEDS = None

CLASSES = [
    (7, 'national trail', re.compile(r'\bNational (Scenic|Historic|Recreation) Trail\b', re.I)),
    (6, 'BLM area', re.compile(r'\bBLM\b|Bureau of Land Management|\bNational Conservation Area\b|\bRecreation Management Area\b|'
                               r'\bSpecial Recreation Management\b|\bWilderness Study Area\b', re.I)),
    (1, 'state trail', re.compile(r'\b(Trail|Trace|Greenway|Rail[- ]?Trail|Railtrail|Water Trail|Bikeway|Towpath)\b', re.I)),
    (3, 'historic site', re.compile(r'\bHistoric(al)? (Site|Park|Landmark|District|Area)\b|\bNational (Historic|Battlefield|Military)\b|'
                                    r'\bBattlefield\b|\bMonument\b|\bFort\b|\bLieu historique\b|\bHeritage (Site|Park)\b', re.I)),
    (2, 'state park / recreation area', re.compile(r'\b(State|Provincial|Territorial) (Resort )?(Park|Recreation(al)? Area|Beach)\b|'
                                                   r'\bState Recreation Area\b|\bParc (national|provincial) d|\bParc national\b(?! du Canada)', re.I)),
    (5, 'county / city / regional park', re.compile(r'\b(County|City|Municipal|Metro(politan)?|Regional|Township|Town|Village|Borough|Parish)( Memorial)? '
                                                    r'(Park|Forest|Preserve|Recreation)|\bMetroPark|\bConservation Area\b.*\bRegion', re.I)),
]


def park_class(row):
    """(rank, label) for one gap row ({area, ref, park, agency, ...})."""
    area = row.get('area') or row.get('st') or ''
    if not area.startswith(('US', 'CA')): return 4, 'world'
    name = f"{row.get('park') or row.get('name') or ''} {row.get('agency') or ''}"
    for rank, label, rx in CLASSES:
        if rx.search(name):
            if rank == 1 and re.search(r'\bNational\b', name, re.I): return 7, 'national trail'
            return rank, label
    if re.search(r'\bState Park\b', row.get('agency') or '', re.I): return 2, 'state park / recreation area'
    return 4, 'other'


def seeds(reload=False):
    """Round 5 seeded work order (config/work_order.json): the Mapping agent's biggest gaps + trail gaps go first."""
    global _SEEDS
    if _SEEDS is None or reload:
        try: d = json.load(open(WORK_ORDER))
        except (OSError, ValueError): d = {}
        _SEEDS = d.get('seeds', []) if d.get('enabled', True) else []
    return _SEEDS


def seed_of(row, kind=None):
    """-> (weight, seed id) for the first matching seed, or (99, None). kind: the plug-in working the row."""
    area = row.get('area') or row.get('st') or ''
    cc = area.split('-')[0]
    best = (99, None)
    for s in seeds():
        if kind and s.get('kinds') and kind not in s['kinds']: continue
        if s.get('refs'):
            if row.get('ref') not in s['refs']: continue
        else:
            A = s.get('areas') or []
            if not ('*' in A or area in A or cc in A): continue
            if cc in (s.get('exclude') or []): continue
        if s['w'] < best[0]: best = (s['w'], s['id'])
    return best


def order_groups(groups, kind=None):
    """Sort agency groups by their best club rank, seeded gaps first inside each rank (config/work_order.json, round 5),
    then biggest first. The club's class order (state trails first ... BLM last) is never overridden by a seed."""
    out = []
    key = lambda r: (park_class(r)[0], seed_of(r, kind)[0])
    for agency, rows in groups:
        rows = sorted(rows, key=key)
        out.append((agency, rows))
    return sorted(out, key=lambda kv: (key(kv[1][0]) if kv[1] else (99, 9), -len(kv[1]), kv[0]))
