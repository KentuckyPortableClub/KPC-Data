#!/usr/bin/env python3
"""CAMP & ACTIVATE BOT (Fable, chat 10 'bot workshop', Oct 28 2026; RULE SHEET E + Brandon's rulings CA-1..CA-6, mapping.md).
It says WHICH CAMPGROUND IS IN WHICH PARK. Review lists + a data file only: it never touches a key, an outline, a card or a 2-fer row.

What it reads (never writes):
  campgrounds  Kentucky: data/campinfo/US-KY.json 'camps' (job 4's facts: name, point, agency, kind, booking) + the day-use shelters
               from data/campfed/US-KY.json (kind 's'). Other states: data/campfed + data/campstate + data/campstate-manual rows
               ([id, name, lat, lon, ...]); a campstate-manual row placed 'by the US Census geocoder' is a street address, so it
               can only ever be NEARBY ('location approximate', rule 1a / example 8).
  outlines     Kentucky: KPC-Links data/ky-answer-key.json tracts read from the ky-*.geojson layers, the same way the truth
               checker's ours_ky() does it: proclamation lines left out, Daniel Boone = the Forest Service OWNED land
               (ky-dbnf-owned.geojson), a KPC-drawn / OpenStreetMap outline = approximate. Other states: the US key only names
               record ids; their polygons live in the boundary-cache release (cache/us/US-XX.json.gz, 'recs' with '_r' rings) which
               the workflow downloads; without that copy the area gets a stub ('outlines not loadable here yet').
  patches      data/fers/<area>.json spots with status 'candidate' (the main list + the 'small overlap' tier). Never 'very tight',
               'not sure', 'water only', dropped or merged rows, never a missing-boundary pair (rule 2).
  lines        line parks (Sheltowee Trace, Trail of Tears, Lewis and Clark): ky-sheltowee.geojson (Forest Service line) and
               data/trails/<ref>.json (official NPS lines). Pine Mountain's line is approximate = NOT SURE, kept out (rule 3).
  closures     data/closures/<area>.json: a hunt closure on a park of an 'activate both' row hides that row for its dates (CA-5).

The rules it applies (Sheet E, short):
  1 INSIDE = the campground's POINT is inside the park's owned / managed outline AND more than 15 m from the edge; 0-15 m = 'at
    the edge: check the official map' (check-first list). CA-1: points first; a loop outline straddling the line = 'part inside'
    (we hold no loop outlines yet, so every row is a point row today).
  2 CAMP HERE, ACTIVATE BOTH = the point is inside a RULED 2-fer patch polygon (main + small tiers), by the patch, never by
    'inside both outlines'. The short 2-fer notice goes on every such row. CA-5: during a hunt closure no 'activate both'.
  3 LINE PARKS = the point is within 100 ft (30.5 m) of the official line AND on public land (inside some official outline).
  4 NEARBY = outside THIS park's outline, within 5 miles straight line (CA-3) of its edge (or of its pin when it has no outline:
    then the row says 'no official boundary'), sorted by distance, never counted toward an activation.
  5 WORDING = review.md uses Sheet E rule 5's lines (⛺ / 📍 Nearby / both notices once / 'last checked' / the outline source label).
  6 UNSURE = at the edge, approximate outline, a merged pair whose points disagree, a rounded (3-decimal) point, or an 'activate
    both' row on a hunt area with no dates yet -> the CHECK FIRST list with the reason. Two records with one name within 1 mile =
    ONE row (chat 8's merge rule): the RIDB point wins for a federal campground, the state's point for a state one.
  CA-2 every kind is shown with its kind; day-use shelters / picnic areas are DAY-USE INFO, never camping rows.
  CA-4 dispersed / designated-campsite zones with no point = a park NOTE ('dispersed'), never a row.

KNOWN ANSWERS (TEST=1, Kentucky): chat 8's desk run (KPC-Links .claude/build/research/KPC_CampActivate_KY_desk.md) is the answer
key: 99 campgrounds / 79 placed / 50 inside 35 parks / 2 'activate both' (Twin Knobs, Great Meadows) / 0 line rows / 4 check first,
Zilpo = CHECK FIRST, and the per-park 'inside' lists. The bot prints every difference (never hides one); GATE=PASS only when all match.

Env: AREAS='US-KY US-TN' (blank = the next CHUNKS (6) unfinished areas in the workshop queue; prints LEFT=<n>) · LINKS (KPC-Links checkout, default 'links') · OUT (data/campsites) · TEST=1
     (Kentucky gate -> state['test'], prints TEST=PASS|FAIL and GATE=…) · GEO_CACHE (cache/us) · STATUS=1 (write the status lines)
Never fails (exit 0 always). Pure Python geometry (no shapely): point-in-polygon, metres to the nearest edge, metres to a polyline.
"""
import glob, gzip, json, math, os, pathlib, re, subprocess, sys, time

OUT = pathlib.Path(os.environ.get('OUT') or 'data/campsites')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
CACHE_US = pathlib.Path(os.environ.get('GEO_CACHE') or 'cache/us')
TODAY = time.strftime('%Y-%m-%d')
VER = 1
EDGE_M = 15.0            # rule 1b (G-M3)
LINE_M = 30.5            # rule 3: 100 ft
NEAR_M = 5 * 1609.344    # CA-3: 5 miles straight line
MERGE_M = 1609.344       # chat 8: same-name records within 1 mile = one row
KIND = {'c': 'campground', 's': 'day-use shelter / picnic area', 'b': 'cabins / lodging', 'l': 'lodge', 'g': 'group camp', 'h': 'horse camp',
        'w': 'walk-in / backcountry', 'r': 'RV', 't': 'tent'}
NOTICE_INFO = ('ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go. '
               '[About our information](https://kentuckyportableclub.github.io/KPC-Links/kpc-about-info.html)')
NOTICE_2FER = "⚠️ Parks' boundaries may overlap here, but we can't confirm it. Check both official boundary maps and make your own call before you count it."
KY_LAYERS = {'bstate': ('ky-state-parks.geojson', 'Kentucky State Parks (DGI)'), 'bwma': ('ky-hunting-areas.geojson', 'KDFWR public hunting areas'),
             'bsnp': ('ky-nature-preserves.geojson', 'Office of Kentucky Nature Preserves'), 'bsna': ('ky-natural-areas.geojson', 'KY natural areas'),
             'bdbnfo': ('ky-dbnf-owned.geojson', 'Forest Service Basic Ownership (owned land)'), 'bnps': ('ky-nps.geojson', 'NPS units'),
             'bwild': ('ky-wild-rivers.geojson', 'KY wild river corridors'), 'bwilder': ('ky-wilderness.geojson', 'wilderness'),
             'bfws': ('ky-fws.geojson', 'FWS refuges'), 'bpad': ('ky-padus-parks.geojson', 'USGS PAD-US'), 'bkpc': ('ky-kpc-drawn.geojson', 'OpenStreetMap outline (unofficial)')}
KY_LINES = {'US-11181': ('Sheltowee Trace', 'ky-sheltowee.geojson', 'Forest Service line'),
            'US-3791': ('Trail of Tears', 'data/trails/US-3791.json', 'NPS official line'),
            'US-4572': ('Lewis and Clark', 'data/trails/US-4572.json', 'NPS official line')}
NOT_SURE_LINES = {'US-10102': 'Pine Mountain: line not official yet'}   # rule 3: approximate line = NOT SURE, kept out
DESK = LINKS / '.claude/build/research/KPC_CampActivate_KY_desk.md'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: from kpc_truth_bot import QUEUE   # the workshop's area order (Kentucky first, then the 2-fer regions, southeast first)
except Exception: QUEUE = ['US-KY']  # noqa: BLE001
STAT = {}


def notice(m): print('::notice title=Camp and activate::' + str(m).replace('\n', ' ')[:900], flush=True)
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def save(p, d):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')


# ---------------- geometry (pure Python; poly_acres / point_in copied from kpc_truth_bot.py) ----------------
def poly_acres(geom):
    """Acres of a GeoJSON polygon / multipolygon (equirectangular equal-area approximation, good to ~1%)."""
    def ring(r):
        if len(r) < 3: return 0.0
        lat0 = sum(p[1] for p in r) / len(r); kx = 111320 * math.cos(math.radians(lat0)); ky = 110540
        a = 0.0
        for i in range(len(r)):
            x1, y1 = r[i][0] * kx, r[i][1] * ky; x2, y2 = r[(i + 1) % len(r)][0] * kx, r[(i + 1) % len(r)][1] * ky
            a += x1 * y2 - x2 * y1
        return abs(a) / 2
    t = geom.get('type'); c = geom.get('coordinates') or []
    polys = c if t == 'MultiPolygon' else [c] if t == 'Polygon' else []
    m2 = 0.0
    for p in polys:
        if not p: continue
        m2 += ring(p[0]) - sum(ring(h) for h in p[1:])
    return m2 / 4046.856


def polys_of(geom):
    t = geom.get('type'); c = geom.get('coordinates') or []
    return c if t == 'MultiPolygon' else [c] if t == 'Polygon' else []


def point_in(la, lo, geom):
    """True when the point is inside the polygon / multipolygon (holes respected)."""
    for p in polys_of(geom):
        inn = False
        for ri, r in enumerate(p):
            hit = False
            for i in range(len(r)):
                x1, y1 = r[i]; x2, y2 = r[(i + 1) % len(r)]
                if (y1 > la) != (y2 > la) and lo < (x2 - x1) * (la - y1) / ((y2 - y1) or 1e-12) + x1: hit = not hit
            if ri == 0: inn = hit
            elif hit: inn = False
        if inn: return True
    return False


def bbox(geom):
    xs, ys = [], []
    for p in polys_of(geom):
        for r in p:
            for pt in r: xs.append(pt[0]); ys.append(pt[1])
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def near_box(la, lo, bb, m):
    """Is the point within m metres of the box (cheap filter before the slow edge walk)?"""
    if not bb: return False
    dy = m / 110540; dx = m / (111320 * math.cos(math.radians(la)) or 1e-9)
    return bb[0] - dx <= lo <= bb[2] + dx and bb[1] - dy <= la <= bb[3] + dy


def seg_m(la, lo, a, b, kx, ky):
    """Metres from the point to the segment a-b (local equirectangular plane)."""
    px, py = lo * kx, la * ky; ax, ay = a[0] * kx, a[1] * ky; bx, by = b[0] * kx, b[1] * ky
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def edge_m(la, lo, geom):
    """Metres from the point to the nearest polygon edge (every ring of every piece)."""
    kx = 111320 * math.cos(math.radians(la)); ky = 110540; best = float('inf')
    for p in polys_of(geom):
        for r in p:
            for i in range(len(r)):
                d = seg_m(la, lo, r[i], r[(i + 1) % len(r)], kx, ky)
                if d < best: best = d
    return best


def line_m(la, lo, lines):
    """Metres from the point to the nearest polyline (lines = list of [[lon, lat], ...])."""
    kx = 111320 * math.cos(math.radians(la)); ky = 110540; best = float('inf')
    for ln in lines:
        for i in range(len(ln) - 1):
            d = seg_m(la, lo, ln[i], ln[i + 1], kx, ky)
            if d < best: best = d
    return best


def hav_m(la1, lo1, la2, lo2):
    p = math.pi / 180; a = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(a))


def ring_poly(ring):
    """A list of [lon, lat] points (open or closed) -> a GeoJSON Polygon."""
    r = [list(p[:2]) for p in ring if isinstance(p, (list, tuple)) and len(p) >= 2]
    if len(r) < 3: return None
    if r[0] != r[-1]: r.append(r[0])
    return {'type': 'Polygon', 'coordinates': [r]}


def lines_of(geom):
    t = geom.get('type'); c = geom.get('coordinates') or []
    return [c] if t == 'LineString' else c if t == 'MultiLineString' else []


# ---------------- campgrounds ----------------
def norm_name(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\(.*?\)|-\s*daniel boone nat\.? for\.?|campgrounds?|group area|group camp|horse camp|recreation area|\bky\b|\btn\b', ' ', s)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()


def rounded(la, lo=None):
    """A point whose LATITUDE has 3 decimals or fewer (RIDB rounds some points to ~100 m): unreliable near an edge. Chat 8's
    desk test (Zilpo 38.075, Hurricane Creek 36.92); a short longitude alone (-83.5 for -83.500) is not counted."""
    s = repr(float(la))
    return '.' not in s or len(s.split('.')[1]) <= 3


def camps_ky(area):
    """Kentucky: job 4's records (data/campinfo) = the facts list; day-use shelters from the federal list."""
    d = load(f'data/campinfo/{area}.json', {})
    rows = []
    for cid, c in (d.get('camps') or {}).items():
        rows.append({'id': cid, 'name': c.get('name') or cid, 'lat': c.get('lat'), 'lon': c.get('lon'), 'park': c.get('park') or '', 'agency': c.get('agency') or '',
                     'kind': c.get('kind') or 'c', 'booking': (c.get('booking') or {}).get('url') or c.get('official_page') or '', 'list': c.get('list') or '',
                     'sites': (c.get('sites') or {}).get('total'), 'federal': c.get('list') == 'campfed' or c.get('agency') in ('FS', 'NPS', 'USACE', 'FWS', 'TVA', 'BLM'),
                     'approx': False, 'src': d.get('read') or ''})
    day = []
    st = area.split('-')[-1]
    for r in load(f'data/campfed/{area}.json', {}).get('camps') or []:
        if len(r) > 7 and r[7] == 's':
            day.append({'id': r[0], 'name': r[1], 'lat': r[2], 'lon': r[3], 'agency': r[4], 'kind': 's', 'booking': r[6] if len(r) > 6 else '', 'list': 'campfed'})
    return rows, day, [f'data/campinfo/{area}.json ({len(rows)} records, read {d.get("read")})', f'data/campfed/{area}.json day-use rows ({len(day)})'] if st else []


def camps_other(area):
    """Other states: the three harvest files. Rows: campfed [id, name, lat, lon, agency, reservable, url, kind]; campstate /
    campstate-manual [id, name, lat, lon, kind, potaRef, officialUrl, reserveUrl, (manual: note, level, status, ...)]."""
    rows, day, read = [], [], []
    f = f'data/campfed/{area}.json'
    for r in load(f, {}).get('camps') or []:
        row = {'id': r[0], 'name': r[1], 'lat': r[2], 'lon': r[3], 'park': '', 'agency': r[4] if len(r) > 4 else '', 'kind': r[7] if len(r) > 7 else 'c',
               'booking': r[6] if len(r) > 6 else '', 'list': 'campfed', 'sites': None, 'federal': True, 'approx': False}
        (day if row['kind'] == 's' else rows).append(row)
    read.append(f'{f} ({len(rows)} rows)')
    for lst in ('campstate', 'campstate-manual'):
        f = f'data/{lst}/{area}.json'; n = 0
        for r in load(f, {}).get('camps') or []:
            if lst == 'campstate-manual' and (len(r) < 10 or r[9] != 'point'): continue   # park-level rows have no point of their own
            approx = lst == 'campstate-manual' and 'geocoder' in str(r[8] if len(r) > 8 else '').lower()
            rows.append({'id': r[0], 'name': r[1], 'lat': r[2], 'lon': r[3], 'park': r[5] if len(r) > 5 else '', 'agency': 'state', 'kind': r[4] if len(r) > 4 else 'c',
                         'booking': (r[7] if len(r) > 7 else '') or (r[6] if len(r) > 6 else ''), 'list': lst, 'sites': None, 'federal': False, 'approx': approx}); n += 1
        read.append(f'{f} ({n} rows)')
    return rows, day, read


def merge_rows(rows):
    """Chat 8's rule: two records with one name within 1 mile = ONE row, both ids kept; the RIDB point wins for a federal
    campground, the state's for a state one. Points more than 500 m apart are remembered (check first: the answer may flip)."""
    placed = sorted([r for r in rows if r.get('lat') is not None and r.get('lon') is not None], key=lambda r: (not r['federal'], r['id']))
    def same(a, b):
        x, y = set(norm_name(a).split()), set(norm_name(b).split())
        return bool(x and y) and (x <= y or y <= x)   # 'Grove' = 'Grove Drive-In Campground'; 'Holly Bay' = 'Holly Bay Campground'
    gone = set(); merged = []
    for i, keep in enumerate(placed):
        if keep['id'] in gone: continue
        for o in placed[i + 1:]:
            if o['id'] in gone or not same(keep['name'], o['name']) or hav_m(keep['lat'], keep['lon'], o['lat'], o['lon']) > MERGE_M: continue
            gone.add(o['id'])
            keep.setdefault('ids', [keep['id']]).append(o['id'])
            keep.setdefault('other_points', []).append({'id': o['id'], 'lat': o['lat'], 'lon': o['lon'], 'name': o['name'], 'list': o['list'],
                                                        'apart_m': round(hav_m(keep['lat'], keep['lon'], o['lat'], o['lon']))})
            keep['booking'] = keep['booking'] or o['booking']; keep['park'] = keep['park'] or o['park']; keep['sites'] = keep['sites'] or o['sites']
            merged.append((keep['name'], o['name'], round(hav_m(keep['lat'], keep['lon'], o['lat'], o['lon']))))
    return [r for r in rows if r['id'] not in gone], merged


# ---------------- outlines ----------------
class Outlines:
    """Per park: pieces [(geom, bbox, label, approx)], a pin, the park's name / type / notes."""
    def __init__(self):
        self.parks = {}   # ref -> {'n','t','pieces':[(geom,bb,src,approx)], 'pin':(la,lo), 'notes':[], 'src': label}
        self.lines = {}   # ref -> {'n', 'lines': [[lon,lat]...], 'src'}
        self.public = []  # (geom, bb) of every official outline = 'public land' for the line check
        self.label = ''


def ky_outlines():
    """Kentucky: the answer key's tracts read from the layers (ours_ky's way: proclamation lines out, Daniel Boone = owned land)."""
    O = Outlines(); O.label = 'official agency files (Kentucky layers)'
    ak = load(LINKS / 'data/ky-answer-key.json', {}).get('parks') or {}
    kyd = {x['c']: x for x in load(LINKS / 'kpc-ky-data.json', {}).get('parks') or [] if x.get('c')}
    feats = {}
    for k, (f, src) in KY_LAYERS.items():
        for x in load(LINKS / f, {}).get('features') or []:
            g = x.get('geometry') or {}
            if g.get('type') not in ('Polygon', 'MultiPolygon'): continue
            p = x.get('properties') or {}
            feats.setdefault(k, []).append((p.get('NAME') or '', p.get('ref') or '', g, bbox(g)))
            O.public.append((g, bbox(g)))
    for ref, p in ak.items():
        pin = (kyd.get(ref, {}).get('la'), kyd.get(ref, {}).get('lo'))
        P = O.parks[ref] = {'n': p.get('n') or ref, 't': p.get('t') or '', 'pieces': [], 'pin': pin if pin[0] is not None else None, 'notes': [], 'src': set()}
        if p.get('run_by'): P['notes'].append(f"run by {p['run_by']}")
        if p.get('note'): P['notes'].append(str(p['note'])[:200])
        for t in p.get('tracts') or []:
            layer, name, how = t[0], t[1], (t[3] if len(t) > 3 else '')
            if layer == 'bdbnf' or re.search(r'proclamation|outer line|purchase', str(how), re.I): continue   # the park = owned land, never the outer line
            for nm, fref, g, bb in feats.get(layer, []):
                if (fref and fref == ref) or nm == name:
                    approx = layer == 'bkpc'
                    P['pieces'].append((g, bb, KY_LAYERS[layer][1], approx)); P['src'].add(KY_LAYERS[layer][1])
        P['src'] = ', '.join(sorted(P['src']))
    for ref, (nm, f, src) in KY_LINES.items():
        path = (LINKS / f) if f.endswith('.geojson') else pathlib.Path(f)
        g = load(path, {})
        lines = []
        for x in (g.get('features') or ([g] if g.get('geometry') else [])):
            lines += lines_of(x.get('geometry') or {})
        if lines:
            O.lines[ref] = {'n': (ak.get(ref) or {}).get('n') or nm, 'lines': lines, 'src': src}
    return O


def cache_outlines(area):
    """Other states: the US key's record ids -> polygons from the boundary-cache copy (cache/us/US-XX.json.gz 'recs', each with
    '_r' = rings as [[lon, lat], ...]; hole / outer structure is not kept, so each ring is tested even-odd on its own).
    Returns None when the cache copy is not here (the workflow downloads it; this sandbox has none)."""
    key = load(f'data/us-key/{area}.json', {})
    f = CACHE_US / f'{area}.json.gz'
    if not key.get('parks') or not f.exists(): return None
    try:
        with gzip.open(f, 'rt', encoding='utf-8') as fh: recs = json.load(fh).get('recs') or []
    except Exception: return None  # noqa: BLE001
    byid = {}
    for r in recs:
        if r.get('_r'): byid[str(r.get('OBJECTID') if r.get('OBJECTID') is not None else r.get('id'))] = r
    O = Outlines(); O.label = 'official land records (PAD-US / state layers via the US key)'
    for ref, p in key['parks'].items():
        P = O.parks[ref] = {'n': p.get('n') or ref, 't': p.get('t') or '', 'pieces': [], 'pin': None, 'notes': [], 'src': ''}
        for m in p.get('m') or []:
            r = byid.get(str(m[0]))
            if not r: continue
            g = {'type': 'MultiPolygon', 'coordinates': [[ring] for ring in r['_r'] if len(ring) >= 3]}
            P['pieces'].append((g, bbox(g), str(m[3] if len(m) > 3 else 'record')[:60], False)); O.public.append((g, bbox(g)))
        P['src'] = 'PAD-US / state layer' if P['pieces'] else ''
        if p.get('far') in ('well outside', 'outside'): P['notes'].append('pin well outside this outline (key)')
    return O


# ---------------- patches ----------------
def patches(area):
    """Ruled 2-fer patches: status 'candidate' (main + small tier), as polygons; river / trail stretches without a zone polygon
    are lines (a point within 100 ft of the stretch counts)."""
    out = []
    for s in load(f'data/fers/{area}.json', {}).get('spots') or []:
        st = str(s.get('status') or '')
        if not st.startswith('candidate'): continue          # 'not sure', 'water only', 'dropped', 'merged into…' never count
        if s.get('tier') or 'very tight' in str(s.get('small') or ''): continue   # the 'very tight' tier is members-only, never a campground answer
        refs = s.get('refs') or []
        if isinstance(refs, str):
            try: refs = json.loads(refs.replace("'", '"'))
            except Exception: refs = re.findall(r'US-\d+|CA-\d+', refs)  # noqa: BLE001
        geom = None; line = None
        if s.get('zone'): geom = {'type': 'Polygon', 'coordinates': [[list(p[:2]) for p in ring] for ring in s['zone'] if len(ring) >= 3]} if isinstance(s['zone'][0][0], (list, tuple)) else ring_poly(s['zone'])
        elif s.get('kind') in ('area', 'same land'): geom = ring_poly(s.get('shape') or [])
        else: line = [list(p[:2]) for p in (s.get('shape') or []) if len(p) >= 2]
        if not geom and not line: continue
        out.append({'id': s.get('id'), 'refs': refs, 'names': s.get('names') or {}, 'acres': s.get('acres'), 'tier': 'small overlap' if s.get('small') else 'main',
                    'kind': s.get('kind'), 'geom': geom, 'bb': bbox(geom) if geom else None, 'line': line, 'label': s.get('label') or '', 'ownership': s.get('ownership') or ''})
    return out


def hunt_closures(area):
    """Hunt closures per park from the closures file: [(ref, label, from, expires)]."""
    out = {}
    for it in load(f'data/closures/{area}.json', {}).get('items') or []:
        txt = ' '.join(str(it.get(k) or '') for k in ('label', 'details', 'kind'))
        if re.search(r'\bhunt', txt, re.I) and it.get('class') in ('part', 'whole') and it.get('ref'):
            out.setdefault(it['ref'], []).append({'label': str(it.get('label') or '')[:200], 'from': it.get('from'), 'expires': it.get('expires'), 'link': it.get('link') or ''})
    return out


def hunt_now(cl):
    for c in cl:
        f, e = c.get('from'), c.get('expires')
        if (not f or str(f) <= TODAY) and (not e or str(e) >= TODAY): return c
    return None


# ---------------- the run ----------------
def run_area(area, state, test):
    ky = area == 'US-KY'
    rows, day, read = (camps_ky if ky else camps_other)(area)
    O = ky_outlines() if ky else cache_outlines(area)
    res = {'area': area, 'about': 'Camp & activate (RULE SHEET E + CA-1..6): which campground is in which park. Planning aid, not a guarantee; every row keeps its source.',
           'read': {'when': TODAY, 'inputs': read, 'outline_source': O.label if O else 'outlines not loadable here yet: needs the boundary-cache copies (cache/us/US-XX.json.gz)',
                    'patches': f'data/fers/{area}.json candidate rows (main + small tiers)', 'ver': VER},
           'counts': {}, 'inside': {}, 'both': [], 'line': [], 'nearby': {}, 'check_first': [], 'no_point': [], 'dayuse': [], 'dispersed': {}, 'merged': [], 'disagree': []}
    if O is None:
        res['counts'] = {'campgrounds': len(rows), 'stub': 1}
        res['stub'] = 'outlines not loadable here yet: needs the boundary-cache copies (the workflow downloads them: gh release download boundary-cache … US-*.json.gz)'
        save(OUT / f'{area}.json', res); state['areas'][area] = {'status': 'stub', 'when': TODAY, 'counts': res['counts']}
        notice(f'{area}: {res["stub"]}'); return res
    rows, merged = merge_rows(rows)
    res['merged'] = [{'kept': a, 'merged': b, 'apart_m': m} for a, b, m in merged]
    P = patches(area); HC = hunt_closures(area)
    parks = O.parks
    for r in rows:
        if r.get('lat') is None or r.get('lon') is None:
            res['no_point'].append({'id': r['id'], 'name': r['name'], 'park': r['park'], 'why': 'no point (name only): needs a real point from the agency page'})
            if re.search(r'dispersed|designated camp|primitive camp|backcountry', r['name'], re.I) and r['park']:
                res['dispersed'][r['park']] = f"{r['name']}: camping allowed under the agency's rules (no single point); see the agency page"
            continue
    placed = [r for r in rows if r.get('lat') is not None and r.get('lon') is not None]
    # 1 inside / at the edge, per park
    for r in placed:
        la, lo = r['lat'], r['lon']
        r['_in'] = []; r['_near'] = []
        for ref, pk in parks.items():
            if not pk['pieces']:
                if pk['pin'] and ref not in O.lines:
                    d = hav_m(la, lo, pk['pin'][0], pk['pin'][1])
                    if d <= NEAR_M: r['_near'].append((ref, d, 'no official boundary: we cannot say if it is inside'))
                continue
            inside = None; depth = 0.0; best = float('inf')
            for g, bb, lab, ap in pk['pieces']:
                if not near_box(la, lo, bb, NEAR_M): continue
                if near_box(la, lo, bb, 0):
                    for poly in polys_of(g):   # the depth = metres to the edge of the polygon PIECE that holds the point; two layers of one park (state park + its WMA): the SMALLEST depth is kept (the safe claim; chat 8's measure)
                        pg = {'type': 'Polygon', 'coordinates': poly}
                        if point_in(la, lo, pg):
                            d = edge_m(la, lo, pg)
                            if inside is None or d < depth: inside, depth = (g, lab, ap), d
                if inside is None:
                    d = edge_m(la, lo, g)
                    if d < best: best = d
            if inside is not None:
                r['_in'].append((ref, depth, inside[1], inside[2]))
            elif best <= NEAR_M:
                r['_near'].append((ref, best, ''))
        for o in r.get('other_points') or []:
            o['inside'] = [ref for ref, pk in parks.items() if any(near_box(o['lat'], o['lon'], bb, 0) and point_in(o['lat'], o['lon'], g) for g, bb, l, a in pk['pieces'])]
        if r['approx']:   # a geocoded street address: NEARBY at best (rule 1a, example 8)
            r['_near'] += [(ref, d, 'location approximate (street address): nearby only until a real point exists') for ref, d, s, a in r['_in']]; r['_in'] = []
    # 2 patches
    for r in placed:
        la, lo = r['lat'], r['lon']; r['_both'] = []
        for p in P:
            hit = (p['geom'] and near_box(la, lo, p['bb'], 0) and point_in(la, lo, p['geom'])) or (p['line'] and line_m(la, lo, [p['line']]) <= LINE_M)
            if hit: r['_both'].append(p)
        for o in r.get('other_points') or []:   # the merged record's other point: does it give another answer?
            o['both'] = [p['id'] for p in P if (p['geom'] and near_box(o['lat'], o['lon'], p['bb'], 0) and point_in(o['lat'], o['lon'], p['geom'])) or (p['line'] and line_m(o['lat'], o['lon'], [p['line']]) <= LINE_M)]
    # 3 line parks
    for r in placed:
        la, lo = r['lat'], r['lon']; r['_line'] = []
        for ref, L in O.lines.items():
            if ref in NOT_SURE_LINES: continue
            d = line_m(la, lo, L['lines'])
            if d <= LINE_M:
                public = any(near_box(la, lo, bb, 0) and point_in(la, lo, g) for g, bb in O.public)
                r['_line'].append((ref, d, public))
    # ---- write the lists
    for r in placed:
        base = {'id': r['id'], 'name': r['name'], 'kind': KIND.get(r['kind'], r['kind']), 'agency': r['agency'], 'booking': r['booking'], 'sites': r['sites'], 'lat': r['lat'], 'lon': r['lon']}
        if r.get('ids'): base['ids'] = r['ids']
        checks = []
        rounded_pt = rounded(r['lat'], r['lon'])
        for ref, d, lab, ap in r['_in']:
            tier = 'inside' if d > EDGE_M else 'at the edge'
            notes = []
            if ap: notes.append('approximate outline: check the official map')
            if tier == 'at the edge': notes.append('at the edge: check the official map')
            if rounded_pt and d < 500: notes.append('rounded point (3 decimals): the edge answer is unreliable')
            row = dict(base, m_inside=round(d), tier=tier, notes=notes, outline=lab)
            res['inside'].setdefault(ref, []).append(row)
            if tier == 'at the edge': checks.append(f"point {round(d)} m inside the edge of {parks[ref]['n']} -> 'at the edge: check the official map'")
            if ap: checks.append(f"inside an approximate (OpenStreetMap) outline of {parks[ref]['n']}: check the official map")
            if r['park'] and r['park'] != ref and r['park'] in parks and not any(x[0] == r['park'] for x in r['_in']):
                res['disagree'].append({'id': r['id'], 'name': r['name'], 'list_says': r['park'], 'outline_says': ref})
        if rounded_pt: checks.append('rounded point (3 decimals, RIDB): any near-edge answer on it is unreliable')
        for o in r.get('other_points') or []:
            mine = sorted(p['id'] for p in r['_both']); mine_in = sorted(x[0] for x in r['_in'])
            if sorted(o['both']) != mine or sorted(o.get('inside') or []) != mine_in:
                checks.append(f"two records for one campground: {r['name']} ({r['list']}) and {o['name']} ({o['list']}) are {o['apart_m']} m apart and give different answers "
                              f"(2-fer: {mine} vs {sorted(o['both'])}; inside: {mine_in} vs {sorted(o.get('inside') or [])}): needs one agency-map point")
        for p in r['_both']:
            refs = p['refs']; names = p['names'] if isinstance(p['names'], dict) else {}
            hunt = ''
            for ref in refs:
                if re.search(r'wildlife management area|\bwma\b|hunting', parks.get(ref, {}).get('n', '') + ' ' + parks.get(ref, {}).get('t', ''), re.I):
                    hunt = f"on a hunt area ({parks[ref]['n']}): apply the hunt closure dates (Sheet D) before showing (CA-5)"
            now = next((hunt_now(HC.get(ref) or []) for ref in refs if hunt_now(HC.get(ref) or [])), None)
            row = dict(base, parks=refs, park_names=[names.get(x) or parks.get(x, {}).get('n', x) for x in refs], patch_id=p['id'], patch_acres=p['acres'], patch_tier=p['tier'],
                       patch_kind=p['kind'], label=p['label'], hunt_note=hunt, notice=NOTICE_2FER, show=not now)
            if now: row['hidden_for'] = f"hunt closure: {now['label']} ({now.get('from') or '?'} to {now.get('expires') or '?'})"
            if any('two records' in c for c in checks): row['show'] = False; row['check_first'] = 'two points disagree'
            res['both'].append(row)
            if hunt and not now: checks.append(hunt)
        for ref, d, public in r['_line']:
            row = dict(base, park=ref, park_name=O.lines[ref]['n'], m_from_line=round(d), public_land=public, line_src=O.lines[ref]['src'])
            if public: res['line'].append(row)
            else: checks.append(f"within 100 ft of the {O.lines[ref]['n']} but not on a known public outline: check the land owner")
        for ref, d, note in r['_near']:
            res['nearby'].setdefault(ref, []).append(dict({'id': r['id'], 'name': r['name'], 'kind': KIND.get(r['kind'], r['kind']), 'miles': round(d / 1609.344, 1)}, **({'note': note} if note else {})))
        if checks: res['check_first'].append({'id': r['id'], 'name': r['name'], 'why': checks})
    for ref in res['nearby']: res['nearby'][ref].sort(key=lambda x: x['miles'])
    for ref in res['inside']: res['inside'][ref].sort(key=lambda x: -x['m_inside'])
    for d in day:
        host = next((ref for ref, pk in parks.items() if pk['pieces'] and any(near_box(d['lat'], d['lon'], bb, 0) and point_in(d['lat'], d['lon'], g) for g, bb, l, a in pk['pieces'])), None) if d.get('lat') is not None else None
        res['dayuse'].append({'id': d['id'], 'name': d['name'], 'kind': KIND['s'], 'agency': d.get('agency'), 'park': host, 'booking': d.get('booking')})
    with_outline = sum(1 for pk in parks.values() if pk['pieces'])
    res['counts'] = {'campgrounds': len(rows), 'placed': len(placed), 'no_point': len(res['no_point']), 'inside': len({x['id'] for v in res['inside'].values() for x in v}), 'inside_rows': sum(len(v) for v in res['inside'].values()),
                     'parks_with_inside': len(res['inside']), 'both': len(res['both']), 'line': len(res['line']), 'check_first': len(res['check_first']),
                     'parks_with_nearby': len(res['nearby']), 'dayuse': len(res['dayuse']), 'dispersed': len(res['dispersed']), 'merged_pairs': len(merged),
                     'parks': len(parks), 'parks_with_outline': with_outline, 'line_parks': len(O.lines), 'patches': len(P), 'disagree': len(res['disagree'])}
    res['park_names'] = {ref: {'n': pk['n'], 'src': pk['src'], 'notes': pk['notes']} for ref, pk in parks.items() if ref in res['inside'] or ref in res['nearby'] or ref in res['dispersed']}
    save(OUT / f'{area}.json', res)
    state['areas'][area] = {'status': 'done', 'when': TODAY, 'counts': res['counts']}
    notice(f'{area}: {json.dumps(res["counts"])}')
    return res


# ---------------- the Kentucky known-answer check ----------------
def desk_answers():
    """Chat 8's desk file -> {counts, both names, per-park inside lists {ref: {name: metres}}}."""
    t = DESK.read_text(encoding='utf-8') if DESK.exists() else ''
    want = {'counts': {}, 'both': [], 'inside': {}, 'inside_names': {}}
    m = re.search(r'Counts: (\d+) campgrounds.*?(\d+) placed with a point, (\d+) have NO point.*?(\d+) campgrounds sit inside a POTA park \((\d+) parks\); (\d+) are CAMP HERE, ACTIVATE BOTH; (\d+) line-park rows; (\d+) go to CHECK FIRST', t, re.S)
    if m: want['counts'] = dict(zip(['campgrounds', 'placed', 'no_point', 'inside', 'parks_with_inside', 'both', 'line', 'check_first'], map(int, m.groups())))
    sec = re.search(r'## 2\..*?\n(.*?)\n## 3', t, re.S)
    if sec: want['both'] = re.findall(r'^- \*\*(.+?)\*\*', sec.group(1), re.M)
    sec = re.search(r'## 3\..*?\n(.*?)\n## 4', t, re.S)
    if sec:
        for ln in sec.group(1).splitlines():
            mm = re.match(r'- (.+?) \((US-\d+)\): (.*)$', ln.strip())
            if not mm: continue
            ref = mm.group(2); items = re.findall(r'(.+?)(?: \[CHECK FIRST\])? \((\d+) m in\)(?:, |$)', mm.group(3))
            want['inside'][ref] = {nm.strip(): int(d) for nm, d in items}
            want['inside_names'][ref] = mm.group(1)
    want['zilpo_check'] = 'Zilpo' in re.search(r'## 4\..*?(?=## 5)', t, re.S).group(0) if re.search(r'## 4\..*?(?=## 5)', t, re.S) else True
    return want


def ky_test(res, state):
    """GATE=PASS only when chat 8's counts, both names, Zilpo = check first and every per-park inside list match; every
    difference is printed and written (never hidden)."""
    W = desk_answers(); diffs = []; info = []
    if not W['counts']: diffs.append(f'desk file not found or unreadable: {DESK}')
    C = res['counts']
    for k, v in W['counts'].items():
        if C.get(k) != v: diffs.append(f'count {k}: ours {C.get(k)} vs chat 8 {v}')
    ours_both = sorted(norm_name(b['name']) for b in res['both']); want_both = sorted(norm_name(x) for x in W['both'])
    if ours_both != want_both: diffs.append(f'activate both: ours {[b["name"] for b in res["both"]]} vs chat 8 {W["both"]}')
    zil = [c for c in res['check_first'] if 'zilpo' in c['name'].lower()]
    if W.get('zilpo_check') and not zil: diffs.append('Zilpo is not in CHECK FIRST (chat 8: two points 1.4 km apart)')
    for ref, want in W['inside'].items():
        ours = {r['name']: r['m_inside'] for r in res['inside'].get(ref, [])}
        wn = {norm_name(n): (n, d) for n, d in want.items()}; on = {norm_name(n): (n, d) for n, d in ours.items()}
        miss = [wn[k][0] for k in wn if k not in on]; extra = [on[k][0] for k in on if k not in wn]
        if miss or extra: diffs.append(f"{ref} {W['inside_names'].get(ref, '')}: missing {miss} extra {extra}")
        for k in wn:
            if k in on and abs(wn[k][1] - on[k][1]) > max(20, 0.15 * wn[k][1]): info.append(f'{ref} {wn[k][0]}: {on[k][1]} m in (chat 8: {wn[k][1]} m)')
    for ref in res['inside']:
        if ref not in W['inside']: diffs.append(f"{ref} {res['park_names'].get(ref, {}).get('n', '')}: extra park with inside rows {[r['name'] for r in res['inside'][ref]]}")
    ok = not diffs
    state['test'] = {'when': TODAY, 'result': 'PASS' if ok else 'FAIL', 'why': ' · '.join(diffs)[:2000] or 'all of chat 8\'s Kentucky answers matched', 'distance_notes': info[:40],
                     'rows': [{'ref': 'counts', 'ok': not any(d.startswith('count') for d in diffs)}, {'ref': 'both', 'ok': not any(d.startswith('activate both') for d in diffs)},
                              {'ref': 'zilpo', 'ok': bool(zil)}, {'ref': 'inside lists', 'ok': not any(re.match(r'US-\d+', d) for d in diffs)}]}
    notice(f"KENTUCKY TEST {'PASS' if ok else 'FAIL'}: {state['test']['why'][:700]}")
    print('TEST=' + ('PASS' if ok else 'FAIL')); print('GATE=' + ('PASS' if ok else 'FAIL'))
    return diffs, info


# ---------------- review.md (Sheet E rule 5 wording) ----------------
def review(state, results):
    L = ['# Camp & activate: which campground is in which park (review list; nothing posts)', '',
         f'Last checked {TODAY}. Rules: RULE SHEET E + rulings CA-1..CA-6 (KPC-Links .claude/notes/mapping.md). Points first (CA-1); every kind shown with its kind (CA-2); '
         "'nearby' = 5 miles straight line from the park edge (CA-3); dispersed camping = a park note (CA-4); during hunt dates no 'activate both' (CA-5); lists per state (CA-6).", '',
         NOTICE_INFO, '', '2-fer rows (POTA only): ' + NOTICE_2FER, '']
    t = state.get('test') or {}
    if t.get('when') == TODAY:
        L += [f"## Kentucky known-answer check: GATE={t.get('result')}", '', f"Chat 8's desk run (KPC_CampActivate_KY_desk.md) vs this run: {t.get('why')}", '']
        if t.get('distance_notes'): L += ['Distances that differ from chat 8 by more than 15% / 20 m (names and parks still match; not a gate item):'] + [f'- {x}' for x in t['distance_notes']] + ['']
    for area, res in results.items():
        L += [f'## {area}', '']
        if res.get('stub'): L += [f"- {res['stub']}", '']; continue
        C = res['counts']; pn = res.get('park_names') or {}
        L += [f"Read: {'; '.join(res['read']['inputs'])}. Outline source: {res['read']['outline_source']}. Patches: {res['read']['patches']}.",
              f"Counts: {C['campgrounds']} campgrounds ({C['merged_pairs']} same-name pairs merged), {C['placed']} with a point, {C['no_point']} with no point; {C['inside']} inside a park ({C['inside_rows']} rows, {C['parks_with_inside']} parks); "
              f"{C['both']} camp here, activate both; {C['line']} line-park rows; {C['check_first']} check first; {C['parks_with_nearby']} parks with a campground nearby; {C['dayuse']} day-use places.", '']
        L += ['### ⛺ Camp here, activate both (we think)', '']
        for b in res['both']:
            L.append(f"- ⛺ Camp here, activate both: {b['name']} ({b['kind']}) — inside the {' × '.join(b['park_names'])} overlap (we think; patch {b['patch_acres']} ac, {b['patch_tier']}"
                     + (f"; {b['label']}" if b['label'] else '') + f"). Booking: {b['booking'] or 'see the agency page'}. {NOTICE_2FER}"
                     + (f" HIDDEN NOW: {b['hidden_for']}" if b.get('hidden_for') else '') + (f" CHECK FIRST: {b['check_first']}" if b.get('check_first') else '') + (f" Note: {b['hunt_note']}" if b['hunt_note'] else ''))
        if not res['both']: L.append('- none')
        L += ['', '### ⛺ Campgrounds in the park', '']
        for ref in sorted(res['inside'], key=lambda r: pn.get(r, {}).get('n', r)):
            p = pn.get(ref, {}); rows = res['inside'][ref]
            L.append(f"- **{p.get('n', ref)}** ({ref}; outline: {p.get('src') or 'official'}" + (f"; {'; '.join(p.get('notes') or [])}" if p.get('notes') else '') + '): '
                     + '; '.join(f"⛺ {r['name']} ({r['kind']}, {r['agency']}" + (f", {r['sites']} sites" if r.get('sites') else '') + (f", {r['booking']}" if r['booking'] else '') + f"; {r['m_inside']} m in"
                                 + (f"; {'; '.join(r['notes'])}" if r['notes'] else '') + ')' for r in rows))
            if ref in res['dispersed']: L.append(f"  - camping info: {res['dispersed'][ref]}")
        for ref, note in res['dispersed'].items():
            if ref not in res['inside']: L.append(f"- **{pn.get(ref, {}).get('n', ref)}** ({ref}): camping info: {note}")
        L += ['', '### ⛺ Within 100 ft of a line park (public land)', '']
        for r in res['line']: L.append(f"- ⛺ {r['name']}: within 100 ft of the {r['park_name']} ({r['m_from_line']} m; public land; {r['line_src']})")
        if not res['line']: L.append('- none')
        L += ['', '### 🔎 Check first (members only)', '']
        for c in res['check_first']: L.append(f"- {c['name']}: " + ' · '.join(c['why']))
        if res['no_point']: L.append(f"- NO POINT ({len(res['no_point'])}): " + '; '.join(f"{x['name']} ({pn.get(x['park'], {}).get('n') or x['park'] or 'no park'})" for x in res['no_point']))
        if res['disagree']: L.append('- list vs outline disagreements: ' + '; '.join(f"{d['name']}: list says {d['list_says']}, outline says {d['outline_says']}" for d in res['disagree']))
        if res['merged']: L.append('- merged same-name pairs within 1 mile: ' + '; '.join(f"{m['kept']} + {m['merged']} ({m['apart_m']} m)" for m in res['merged']))
        L += ['', '### 📍 Nearby (outside the park, within 5 miles straight line; never counts toward an activation; nearest 4 shown)', '']
        for ref in sorted(res['nearby'], key=lambda r: pn.get(r, {}).get('n', r)):
            rows = res['nearby'][ref][:4]
            L.append(f"- {pn.get(ref, {}).get('n', ref)}: " + '; '.join(f"📍 Nearby (outside the park): {r['name']}, {r['miles']} mi" + (f" ({r['note']})" if r.get('note') else '') for r in rows))
        L += ['', '### 🧺 Day-use info (shelters / picnic areas: good info, not camping rows)', '']
        for d in res['dayuse']: L.append(f"- {d['name']} ({d['agency']}" + (f"; in {pn.get(d['park'], {}).get('n', d['park'])}" if d.get('park') else '; not inside a park outline') + ')')
        if not res['dayuse']: L.append('- none')
        L.append('')
    L += [NOTICE_INFO, '']
    (OUT / 'review.md').write_text('\n'.join(L), encoding='utf-8')


def status_lines(area, res, state):
    """kpc_status.py grade-me / gate / board after a batch (same calls as kpc_workshop.py). STATUS=1 only (the workflow)."""
    if os.environ.get('STATUS') != '1': return
    me = '.github/scripts/kpc_status.py'; name = 'camp and activate bot'; t = state.get('test') or {}
    st = (state['areas'].get(area) or {}).get('status')
    if t.get('result') == 'FAIL' and t.get('when') == TODAY and area == 'US-KY':
        subprocess.run([sys.executable, me, 'gate', name, area, 'FAIL', str(t.get('why'))[:380]])
    else:
        subprocess.run([sys.executable, me, 'grade-me', name, area, f'{OUT}/{area}.json (+ review.md)', f"{st}; gate {t.get('result', 'none') if t.get('when') == TODAY else 'none'}; {json.dumps(res['counts'])[:140]}"])
    subprocess.run([sys.executable, me, 'board', name, 'green', f"{area}: {st}; {json.dumps(res['counts'])[:200]}", 'chat 8 grades review.md; Brandon GO before the Lounge tab / cards', ''])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    state = load(OUT / 'state.json', {'areas': {}})
    want = (os.environ.get('AREAS') or '').upper().split()
    chunks = int(os.environ.get('CHUNKS') or 6)   # areas per job when AREAS is blank
    areas = want or [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') not in ('done', 'stub')][:chunks] or ['US-KY']
    test = os.environ.get('TEST') == '1'
    results = {}
    for area in areas:
        try: results[area] = run_area(area, state, test)
        except Exception as e:  # noqa: BLE001
            import traceback; traceback.print_exc()
            notice(f'{area}: error {e}'); state['areas'][area] = {'status': 'error', 'when': TODAY, 'why': str(e)[:300]}
    if test and 'US-KY' in results and not results['US-KY'].get('stub'):
        diffs, info = ky_test(results['US-KY'], state)
        for d in diffs: print('DIFF: ' + d)
        for d in info: print('DIST: ' + d)
        if not diffs: state['proven'] = TODAY
    state['last'] = {'when': TODAY, 'areas': areas, 'ver': VER}
    save(OUT / 'state.json', state)
    review(state, results)
    for area, res in results.items(): status_lines(area, res, state)
    left = [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') not in ('done', 'stub')]
    print(f'LEFT={len(left)}')
    notice('done: ' + ', '.join(f"{a} {(state['areas'].get(a) or {}).get('status')}" for a in areas) + f' · areas left in the queue: {len(left)}')


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc(); notice(f'bot error: {e}')
    sys.exit(0)
