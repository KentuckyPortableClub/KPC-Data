"""PART 2. The missing list: ONE file, what each park is missing, per kind, from the club's own files (via adapters.py only).
gaps.json -> {area: {ref: {kinds: [..], agency, agency_how, n, why_not: {kind: tag}}}} + gaps-summary.md."""
import datetime as dt, json, pathlib, re
from . import scope
from .adapters import CAMP_WORDS, TRAIL_TYPE

CHECK_ALL = set()      # --check-all camping,trail: treat every park in scope as missing these kinds (sample / audit runs)
TRAIL_PARK = re.compile(r'\b(trail|trace|greenway|rail[- ]trail|scenic river|wild and scenic|water ?trail|byway)\b', re.I)


def park_gaps(club, area, p, today=None):
    today = today or dt.date.today()
    ref = p['ref']; kinds = []; why = {}
    st = club.outline_status(area, ref)
    if st != 'official':
        kinds.append('outline'); why['outline'] = 'key: approximate only' if st == 'approx' else 'key: pin only'
    if not club.has_map(area, ref): kinds.append('map')
    if not club.has_page(area, ref): kinds.append('page')
    if area.startswith(('US-', 'CA-')):
        if not club.access_points(area, ref): kinds.append('parking')
        words = ' '.join(str(x) for x in (p.get('n'), p.get('t'), p.get('acc'), json.dumps(club.docs_row(area, ref).get('notes') or '')))
        if CAMP_WORDS.search(words) and not club.campgrounds(area, ref):
            kinds.append('camping'); why['camping'] = 'camping words on the park row, no campground row'
        if (TRAIL_TYPE.search(p.get('t') or '') or TRAIL_PARK.search(p.get('n') or '')) and not club.has_trail_line(area, ref):
            kinds.append('trail')
    if area.startswith('US-') or area.startswith('CA-'):     # hours / fees / closures: only where config/rules.json allows (default US-KY)
        h = club.hours_row(area, ref)
        if not (h.get('hours') or h.get('h')): kinds.append('hours')
        if not (h.get('fees') or h.get('f')): kinds.append('fees')
        last = club.closures_checked(area).get(ref)
        try: fresh = last and (today - dt.date.fromisoformat(str(last)[:10])).days <= 7
        except ValueError: fresh = False
        if not fresh: kinds.append('closures')
    kinds += [k for k in sorted(CHECK_ALL) if k not in kinds]
    kinds = [k for k in kinds if scope.allowed(k, area)]
    return kinds, why


def build(club, areas, out_dir, limit=None):
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    prev = {}
    if (out_dir / 'gaps.json').exists():
        try: prev = json.load(open(out_dir / 'gaps.json'))
        except ValueError: prev = {}
    G, parks_all = {}, {}
    for area in areas:
        parks = club.parks(area)
        if limit: parks = dict(list(parks.items())[:limit])
        parks_all[area] = parks
        rows = {}
        for ref, p in parks.items():
            kinds, why = park_gaps(club, area, p)
            if not kinds: continue
            ag, how = club.agency(p)
            rows[ref] = {'n': p.get('n'), 'kinds': kinds, 'agency': ag, 'agency_how': how, 'why_not': why}
        G[area] = rows
    json.dump(G, open(out_dir / 'gaps.json', 'w'), indent=1, ensure_ascii=False)
    L = ['# Missing list (gaps)', '', f'Built {dt.date.today().isoformat()} from the club files (read-only).', '',
         '| area | kind | parks | missing | solved since last night |', '|---|---|---|---|---|']
    for area in areas:
        for k in ['outline', 'map', 'page', 'parking', 'camping', 'trail', 'hours', 'fees', 'closures']:
            if not scope.allowed(k, area): continue
            miss = sum(1 for r in G[area].values() if k in r['kinds'])
            was = {ref for ref, r in (prev.get(area) or {}).items() if k in r.get('kinds', [])}
            now = {ref for ref, r in G[area].items() if k in r['kinds']}
            L.append(f'| {area} | {k} | {len(parks_all[area])} | {miss} | {len(was - now) if prev else "-"} |')
    if club.missing_files:
        L += ['', '## Club files not found (read as empty)', ''] + [f'- `{x}`' for x in sorted(club.missing_files)[:60]]
    (out_dir / 'gaps-summary.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    return G, parks_all
