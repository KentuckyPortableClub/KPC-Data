#!/usr/bin/env python3
"""TRACER LIMITS (Nov 2 2026 review; Nov 6: parcel defaults flipped to the review values Brandon OK'd).
Small pure helpers shared by the picture-map tracer (kpc_trace_picture.py) and the parcel tracer
(tools/kpc_parcel_trace/kpc_parcel_trace.py).

Switches (env; the picture tracer also has command-line flags):
  KPC_TRACE_HONOR_IMAGE   1  the picture tracer uses the image the prep step chose (row 'map_file', else row 'image'),
                             not the first <ref>_*.jpg on disk. 0 = old first-jpg pick.
  KPC_TRACE_ACRES_FILE    '' an official acres list ({ref: acres} or {ref: {acres}}; data/acres.json) for rows with no acres.
  KPC_TRACE_CHANCE_RATIO  1.5 and KPC_TRACE_CHANCE_MARGIN 2.0: the 'better than chance' gate.
  KPC_TRACE_BAND_JUNCTIONS 1 (Nov 11, later) junctions of roads drawn as bands, and the bands' middle lines for the line agreement.
  KPC_TRACE_BOX_MASK      1  no junctions in legend / title / inset / icon boxes the park outline does not run through.
  KPC_TRACE_DARK_RING     1  a thick black boundary RING, tried only when no colour gave a boundary.
  KPC_TRACE_LINE_WEIGHT   0.25 (Nov 11) weight of the line-agreement z in the match score (kpc_trace_edges.py), real and decoy alike.
                          0 = the junction score alone (the Nov 2 behaviour).
  KPC_PARCEL_ADJ_M        30  (Nov 6 default; was 200) parcel adjacency in metres. 200 jumps roads onto the neighbour.
  KPC_PARCEL_GROW_CAP     1.25 (Nov 6 default; was 0) stop growing at this many times the official acres; 0 = no cap.
  KPC_PARCEL_SUBTRACT     1  (Nov 6 default; was 0) cut other POTA parks' official outlines out of the result.
  KPC_PARCEL_PARK_MIN     8  per-park wall-clock minutes; a hung host/statewide layer is skipped and the run continues.
  KPC_PARCEL_REQ_TIMEOUT  30 per-request HTTP timeout in seconds (Polite).
"""
import glob, json, os, re

DEFAULTS = {'KPC_TRACE_HONOR_IMAGE': '1', 'KPC_TRACE_ACRES_FILE': '', 'KPC_TRACE_CHANCE_RATIO': '1.5', 'KPC_TRACE_CHANCE_MARGIN': '2.0', 'KPC_TRACE_LINE_WEIGHT': '0.25',
            'KPC_PARCEL_ADJ_M': '30', 'KPC_PARCEL_GROW_CAP': '1.25', 'KPC_PARCEL_SUBTRACT': '1',
            'KPC_PARCEL_PARK_MIN': '8', 'KPC_PARCEL_REQ_TIMEOUT': '30',
            # Nov 11 (later): picture-tracer matcher inputs, each on by default; 0 = off (also --off on the tracer's command line)
            'KPC_TRACE_BAND_JUNCTIONS': '1', 'KPC_TRACE_BOX_MASK': '1', 'KPC_TRACE_DARK_RING': '1'}

# Picture tracer: traced acres vs known acres (Nov 6: hold back as NEEDS A PERSON, not DRAWN+flag).
PICTURE_ACRES_LO, PICTURE_ACRES_HI = 0.2, 5.0


def setting(name, env=None):
    env = os.environ if env is None else env
    v = str(env.get(name, '') or '').strip()
    return v if v else DEFAULTS.get(name, '')


def num(name, env=None):
    try: return float(setting(name, env))
    except ValueError: return float(DEFAULTS[name])


def on(name, env=None):
    return setting(name, env).lower() not in ('0', 'off', 'false', 'no', '')


# ------------------------------------------------------------------ picture tracer
def chosen_image(row):
    """The file name under maps/ the prep step chose for this row, or None. map_file wins; 'image' may carry 'maps/'."""
    row = row or {}
    if row.get('map_file'): return str(row['map_file'])
    im = str(row.get('image') or '').strip()
    if not im: return None
    return im[5:] if im.startswith('maps/') else im


def load_acres(path):
    """{ref: acres}. path = one file or several joined by ',' (Nov 6, tracer follow-up from #19: broader acres coverage).
    A file is {ref: acres | {'acres': n}} (data/acres.json) or a key tract side file ({'parks': {ref: [{'ac': n}, ...]}}, from
    KPC-Links data/us-key/tracts, data/ca-key/tracts, data/world-key/tracts, data/tracts): a park's official acres = the sum of its
    tracts' source acres, only when every tract has one; a park in two side files (two states) is summed. The first file that
    names a park wins over later files (so data/acres.json, listed first, keeps priority)."""
    out = {}
    if not path: return out
    files = [p.strip() for p in str(path).split(',') if p.strip()]
    if len(files) > 1 or os.path.isdir(files[0]):
        exp = []
        for f in files: exp += sorted(glob.glob(os.path.join(f, '*.json'))) if os.path.isdir(f) else [f]
        side = {}
        for f in exp:
            plain, sd = load_acres_one(f)
            for r, a in plain.items(): out.setdefault(r, a)
            for r, a in sd.items(): side[r] = side.get(r, 0.0) + a
        for r, a in side.items(): out.setdefault(r, a)
        return out
    plain, sd = load_acres_one(files[0])
    for r, a in sd.items(): plain.setdefault(r, a)
    return plain


def load_acres_one(path):
    out, side = {}, {}
    try: d = json.load(open(path, encoding='utf-8'))
    except Exception: return out, side  # noqa: BLE001
    d = d.get('parks', d) if isinstance(d, dict) else {}
    for r, v in (d.items() if isinstance(d, dict) else []):
        if isinstance(v, list):
            ac = [t.get('ac') for t in v if isinstance(t, dict)]
            if ac and len(ac) == len(v) and all(isinstance(a, (int, float)) and a > 0 for a in ac): side[r] = float(sum(ac))
            continue
        try: a = float(v.get('acres') if isinstance(v, dict) else v)
        except (TypeError, ValueError, AttributeError): continue
        if a > 0: out[r] = a
    return out, side


def fill_acres(index, acres):
    """index = {ref: [row, ...]}. Rows with no acres get the official acres (marked acres_src). Returns how many were filled."""
    n = 0
    for ref, rows in index.items():
        for row in rows:
            if row.get('acres') in (None, '') and acres.get(ref):
                row['acres'] = acres[ref]; row['acres_src'] = 'official acres list'; n += 1
    return n


def better_than_chance(real, decoy, ratio=1.5, margin=2.0):
    return real >= max(ratio * decoy, decoy + margin)


def acres_in_range(traced, known, lo=None, hi=None):
    """True when traced acres are inside [lo, hi] × known. Missing known/traced = True (no gate)."""
    lo = PICTURE_ACRES_LO if lo is None else lo
    hi = PICTURE_ACRES_HI if hi is None else hi
    try:
        t, k = float(traced), float(known)
    except (TypeError, ValueError):
        return True
    if k <= 0 or t < 0: return True
    return lo * k <= t <= hi * k


# ------------------------------------------------------------------ Nov 7 gates: ceilings, GeoPDF plausibility, clipped maps
# Size ceilings by POTA park type (parkinfo row[2]). They are SANITY bounds for traces with no known acres, not park sizes: a trace over its
# ceiling is held as NEEDS A PERSON, never DRAWN. First matching row wins; no match = DEFAULT_CEILING_ACRES. A tier is only as good as the
# type word: the ceilings below are a starting point for Brandon to tune (one line each), and a real park that trips one is a NEEDS A PERSON
# row for a person, which is the intended outcome. Federal giants (a national forest can be 16 M ac) only guard against country-sized errors.
TYPE_CEILING_ACRES = [
    # Brandon, Nov 7: a specific POINT-FEATURE word in the name beats the agency ("Trailhead" beats "BLM"): a trailhead with a million-acre
    # limit makes no sense. Only point-like words sit up here; "historic", "monument" and the like stay below the national tier because a
    # National Monument or National Historical Park can be large.
    (re.compile(r'trailhead|trail head|recreation site|boat (ramp|launch|access)|fishing access|day use|picnic|campground|overlook|'
                r'wayside|rest area|visitor cent', re.I), 5_000),
    (re.compile(r'\bnational (park|preserve|forest|grassland|monument|wildlife refuge|recreation area|seashore|lakeshore)|wilderness', re.I), 20_000_000),
    (re.compile(r'\bblm\b|bureau of land', re.I), 1_000_000),
    (re.compile(r'state forest|wildlife management|wildlife area|game land|conservation area|crown land|state game', re.I), 150_000),
    (re.compile(r'provincial park|territorial park|international park|state park|recreation park|recreation area|state recreation', re.I), 60_000),
    (re.compile(r'regional park|county park|conservancy|natural area|state natural', re.I), 15_000),
    (re.compile(r'nature reserve|nature preserve|preserve|historic|heritage|monument|battlefield|trailhead|recreation site|boat|fishing access|'
                r'day use|picnic|city park|municipal|urban', re.I), 5_000),
]
DEFAULT_CEILING_ACRES = 60_000
NEAR_CEILING = 0.95              # Brandon, Nov 7: a trace within 5% of its ceiling goes to a person too, not straight through
PAGE_SHARE_MAX = 0.60            # a GeoPDF trace covering more of the mapped page than this is a sheet outline, not a park
GEOPDF_RESID_MAX_M = 100.0       # /GPTS residual above this: placement not trusted
GEOPDF_RESID_MAX_PAGE = 0.02     # ... or above this share of the page's long side
GEOPDF_SCALE_RANGE = (0.05, 500.0)   # plausible metres per pixel
GEOPDF_SKEW_MAX = 0.15           # |sx - sy| / max(sx, sy)
GEOPDF_PAGE_MAX_KM2 = 50_000.0
GEOPDF_PIN_MARGIN = 0.05         # the pin may sit this share of the page outside it before 'pin off page'
EDGE_SHARE_FLAG = 0.03           # share of the outline lying on the picture frame: below = flag only, at or above = hold
LINE_LENGTH_CEILING_KM = {'trail': 400.0, 'default': 120.0}


def ceiling_acres(park_type):
    t = str(park_type or '')
    for rx, c in TYPE_CEILING_ACRES:
        if rx.search(t): return float(c)
    return float(DEFAULT_CEILING_ACRES)


def type_expected_acres(park_type):
    """Only for ranking candidate shapes, never a gate."""
    return ceiling_acres(park_type) / 30.0


def edge_share(pts_px, w, h, band=4):
    """Share (0..1) of a closed polygon's perimeter that lies within `band` px of the picture frame."""
    n = len(pts_px)
    if n < 2: return 0.0
    tot = on = 0.0
    for i in range(n):
        x0, y0 = pts_px[i]; x1, y1 = pts_px[(i + 1) % n]
        seg = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if seg <= 0: continue
        tot += seg
        for t in (0.125, 0.375, 0.625, 0.875):      # four samples per edge: a segment counts in proportion
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if x <= band or y <= band or x >= w - 1 - band or y >= h - 1 - band: on += seg / 4.0
    return on / tot if tot else 0.0


def geopdf_checks(fit_err_m, m_per_px, page_km2, pin_off_km=0.0, page_long_m=None):
    """Plausibility of a GeoPDF placement from numbers only. m_per_px = (x, y). pin_off_km = how far the pin is outside the page (0 = on it).
    Returns (ok, [why...]); the why strings start with 'geopdf residual' / 'geopdf scale' / 'geopdf skew' / 'pin off page' / 'geopdf page'."""
    why = []
    try: fe = float(fit_err_m)
    except (TypeError, ValueError): fe = None
    sx, sy = (float(m_per_px[0]), float(m_per_px[1])) if m_per_px else (None, None)
    if page_long_m is None and page_km2: page_long_m = (float(page_km2) ** 0.5) * 1000.0
    if fe is None:
        why.append('geopdf residual: the georeference has no fit error to check')
    else:
        lim = GEOPDF_RESID_MAX_M
        if page_long_m: lim = min(lim, GEOPDF_RESID_MAX_PAGE * page_long_m) if GEOPDF_RESID_MAX_PAGE * page_long_m > 1.0 else lim
        if not fe < max(lim, 1.0): why.append(f'geopdf residual: {fe:g} m is over {max(lim, 1.0):g} m (100 m, or 2% of the page)')
    if sx is None or not (GEOPDF_SCALE_RANGE[0] <= sx <= GEOPDF_SCALE_RANGE[1] and GEOPDF_SCALE_RANGE[0] <= sy <= GEOPDF_SCALE_RANGE[1]):
        why.append(f'geopdf scale: x {sx} m/px, y {sy} m/px not plausible (allowed {GEOPDF_SCALE_RANGE[0]:g}-{GEOPDF_SCALE_RANGE[1]:g})')
    elif abs(sx - sy) / max(sx, sy) > GEOPDF_SKEW_MAX:
        why.append(f'geopdf skew: x {sx:.2f} m/px vs y {sy:.2f} m/px differ by more than {GEOPDF_SKEW_MAX:.0%}')
    if pin_off_km and pin_off_km > 0:
        why.append(f'pin off page: the POTA pin falls outside this map sheet by {pin_off_km:.1f} km; wrong sheet or wrong pin')
    if page_km2 and float(page_km2) > GEOPDF_PAGE_MAX_KM2:
        why.append(f'geopdf page: the sheet maps {float(page_km2):,.0f} km2 (over {GEOPDF_PAGE_MAX_KM2:,.0f}); a statewide sheet needs a person')
    return not why, why


def geopdf_plausible(affine, w_px, h_px, fit_err_m, pin_ll):
    """Same checks from the real /GPTS affine (u, v in 0..1 of the page -> lon, lat: lon = a0 u + a1 v + a2, lat = a3 u + a4 v + a5)
    and the pin (lat, lon). Returns (ok, why list, info dict with m_per_px_x/y, page_km2, pin_off_km, pin_on_page)."""
    import math
    try:
        a = [float(x) for x in affine]
        if len(a) != 6 or not all(math.isfinite(x) for x in a): raise ValueError
        det = a[0] * a[4] - a[1] * a[3]
        if abs(det) < 1e-18: raise ValueError
    except (TypeError, ValueError):
        return False, ['geopdf scale: malformed affine'], {'malformed': True}
    lat0 = a[5] + 0.5 * (a[3] + a[4])
    kx, ky = 111320.0 * math.cos(math.radians(lat0)), 110540.0
    wx = math.hypot(a[0] * kx, a[3] * ky)            # page width in metres (u direction)
    hy = math.hypot(a[1] * kx, a[4] * ky)            # page height in metres (v direction)
    sx, sy = wx / max(float(w_px), 1.0), hy / max(float(h_px), 1.0)
    page_km2 = abs(det) * kx * ky / 1e6
    off_km, on_page = 0.0, True
    if pin_ll:
        la, lo = float(pin_ll[0]), float(pin_ll[1])
        u = (a[4] * (lo - a[2]) - a[1] * (la - a[5])) / det
        v = (-a[3] * (lo - a[2]) + a[0] * (la - a[5])) / det
        du = max(0.0, -GEOPDF_PIN_MARGIN - u, u - 1.0 - GEOPDF_PIN_MARGIN)
        dv = max(0.0, -GEOPDF_PIN_MARGIN - v, v - 1.0 - GEOPDF_PIN_MARGIN)
        on_page = du == 0 and dv == 0
        off_km = math.hypot(du * wx, dv * hy) / 1000.0
    ok, why = geopdf_checks(fit_err_m, (sx, sy), page_km2, off_km, max(wx, hy))
    # lat_down: latitude grows DOWN the page (a[4] > 0). A north-up page rendered top-down should have a[4] < 0, so this is a sign the
    # page's /GPTS-/LPTS orientation is mirrored - but it is reported as a FACT, not a verdict: it is true of pages that place correctly
    # as well (a pin near the middle of a small page barely moves when mirrored), and a mirrored page can still fit its own points
    # perfectly, so the residual does not catch it. Nov 7: US-5460 Sun Pass is a proven mirrored page; four of five sample pages carry
    # this sign. Whoever can open the PDFs should settle it in kpc_picture_geo.py.
    return ok, why, {'m_per_px_x': sx, 'm_per_px_y': sy, 'page_km2': page_km2, 'pin_off_km': off_km, 'pin_on_page': on_page,
                     'lat_down': bool(a[4] > 0)}


def size_verdict(traced_acres, known_acres, park_type, page_share=None):
    """('ok', '') or ('hold', why). Known acres: the Nov 6 0.2x-5x range, unchanged. No known acres: the type ceiling (and, on a GeoPDF, the
    page share). Never looser than before: acres_in_range is still the only test when a size is known."""
    try: t = float(traced_acres)
    except (TypeError, ValueError): return 'ok', ''
    try: k = float(known_acres) if known_acres not in (None, '') else None
    except (TypeError, ValueError): k = None
    if k and k > 0:
        if not acres_in_range(t, k):
            return 'hold', f'traced area {t:.0f} ac vs known {k:.0f} ac outside {PICTURE_ACRES_LO:g}x-{PICTURE_ACRES_HI:g}x'
        return 'ok', ''
    c = ceiling_acres(park_type)
    if t > c:
        return 'hold', (f'traced area {t:,.0f} ac is over the {c:,.0f} ac ceiling for a {park_type or "park (type unknown)"}'
                        ' and no official size is known')
    if t >= NEAR_CEILING * c:
        return 'hold', (f'traced area {t:,.0f} ac is within {1 - NEAR_CEILING:.0%} of the {c:,.0f} ac ceiling for a '
                        f'{park_type or "park (type unknown)"} and no official size is known: a person should look')
    if page_share is not None and page_share > PAGE_SHARE_MAX:
        return 'hold', f'the trace covers {page_share:.0%} of the mapped page: a sheet outline, not a park, and no official size is known'
    return 'ok', ''


def hold_reasons(*, kind='area', geopdf_why=(), pin_dist_m=None, pin_max_m=1000.0, edge=None, traced_acres=None, known_acres=None,
                 park_type=None, page_share=None, length_km=None, geopdf_residual_ok=None):
    """Every reason a picture trace must be held as NEEDS A PERSON, in the order they are reported (the first is the status line):
    GeoPDF plausibility, pin outside, clipped at the picture edge, size. [] = nothing to hold. edge = share of the outline on the frame
    (None = the outline does not touch it)."""
    out = list(geopdf_why or [])
    if pin_dist_m is not None and pin_dist_m > pin_max_m:
        if geopdf_residual_ok is True: tail = 'placement looks right (good georeference), the pin may be wrong'
        else: tail = 'placement doubtful'
        out.append(f'pin outside: the POTA pin is {pin_dist_m:.0f} m from the traced outline; {tail}')
    if kind == 'area' and edge is not None and edge >= EDGE_SHARE_FLAG:
        out.append(f'clipped: {edge:.0%} of the outline runs along the picture edge; the park continues off this sheet')
    if kind == 'area':
        st, why = size_verdict(traced_acres, known_acres, park_type, page_share)
        if st == 'hold': out.append(why)
    else:
        lim = LINE_LENGTH_CEILING_KM.get(kind, LINE_LENGTH_CEILING_KM['default'])
        try:
            if length_km is not None and float(length_km) > lim: out.append(f'line length {float(length_km):.0f} km is over the {lim:g} km ceiling for a {kind}')
        except (TypeError, ValueError): pass
    return out


# ------------------------------------------------------------------ parcel tracer
def capped_growth(candidates, area_m2, cap_m2):
    """Best-first growth under a size cap. candidates = [(key, distance_m, area_m2)] that touch the shape this round; area_m2 = the
    shape's area now; cap_m2 = the most it may reach (0/None = no cap). Returns (keys to add, capped?). Nearest first; a parcel
    that would push the shape over the cap is not added (and the growth is marked capped)."""
    if not cap_m2: return [k for k, _, _ in candidates], False
    add, tot, capped = [], area_m2, False
    for k, d, a in sorted(candidates, key=lambda x: (x[1], -x[2])):
        if tot + a > cap_m2: capped = True; continue
        add.append(k); tot += a
    return add, capped


def stitch_extra(kept_acres, candidates, known_acres, lo=0.5, hi=1.25):
    """Nov 7 (picture tracer, split-unit maps): which FURTHER shapes in the park colour may join the piece at the pin, once the 50 m
    adjacency growth has finished. candidates = [(index, distance_m, acres)] for the shapes left out. A gap wider than 50 m is only
    bridged on evidence: there must be an official size, the kept piece must be under `lo` x it, and adding the nearest pieces must land
    inside lo..hi x it. With no official size nothing is joined - the shapes are LISTED in the why for a person to judge, which is the
    honest answer when the page alone cannot say whether they are other units of this park or a neighbouring park.
    Returns (indices to add, text for the why)."""
    left = sorted(candidates or [], key=lambda t: (t[1], -t[2]))
    if not left:
        return [], ''
    def _listed(ix):
        ds = [t[1] for t in left if t[0] in ix] if ix else [t[1] for t in left]
        rng = f'{min(ds):.0f}' + (f'-{max(ds):.0f}' if max(ds) - min(ds) >= 1 else '')
        return (f'{len(ds)} more shape(s) in the park colour at {rng} m not joined; they may be other units of this park or a '
                f'neighbouring park: check by hand')
    try: k = float(known_acres) if known_acres not in (None, '') else None
    except (TypeError, ValueError): k = None
    try: tot = float(kept_acres)
    except (TypeError, ValueError): tot = None
    if not k or k <= 0 or tot is None:
        return [], _listed(None)
    if tot >= lo * k:
        return [], _listed(None)            # the piece at the pin is already the size of the park: nothing to add
    add = []
    for i, d, a in left:
        if tot + a > hi * k:
            continue
        add.append(i); tot += a
        if tot >= lo * k:
            break
    if tot < lo * k:
        return [], _listed(None)            # even all of them do not make the official size: not this park's missing units
    rest = [t[0] for t in left if t[0] not in add]
    txt = (f'{len(add)} further shape(s) joined on the official size ({tot:,.0f} ac of {k:,.0f} ac known, inside {lo:g}x-{hi:g}x)')
    if rest:
        txt += '; ' + _listed(rest)
    return add, txt


def parcel_new_holds(acres, known_acres, park_type, seed_acres=None, grow_cap=1.25):
    """Nov 7 parcel-tracer holds on top of the existing 0.2x-2x size check (which stays as it is): (1) the seed parcel ALONE is over grow_cap x the
    known size (growth capping only ever limited ADDED parcels); (2) no known size at all and the trace is over the type's ceiling (the old
    checks all needed known acres). Returns a list of 'held' reasons ([] = nothing new). Never looser than before."""
    out = []
    try: k = float(known_acres) if known_acres not in (None, '') else None
    except (TypeError, ValueError): k = None
    if k and k > 0:
        try:
            if grow_cap and seed_acres is not None and float(seed_acres) > grow_cap * k:
                out.append(f'seed parcel alone is {float(seed_acres):,.0f} ac, over {grow_cap:g}x the known {k:,.0f} ac')
        except (TypeError, ValueError): pass
        return out
    try: t = float(acres)
    except (TypeError, ValueError): return out
    c = ceiling_acres(park_type)
    if t > c:
        out.append(f'no known size and {t:,.0f} ac is over the {c:,.0f} ac ceiling for a {park_type or "park (type unknown)"}')
    elif t >= NEAR_CEILING * c:
        out.append(f'no known size and {t:,.0f} ac is within {1 - NEAR_CEILING:.0%} of the {c:,.0f} ac ceiling for a '
                   f'{park_type or "park (type unknown)"}: a person should look')
    return out


def subtract_others(g, others):
    """g minus the union of other parks' outlines (shapely). Returns (new geometry, area removed in g's units)."""
    if not others or g is None or g.is_empty: return g, 0.0
    from shapely.ops import unary_union
    u = unary_union([o for _, o in others if o is not None and not o.is_empty])
    if u.is_empty or not g.intersects(u): return g, 0.0
    out = g.difference(u)
    return out, g.area - out.area


# Statewide vs county layer preference (Nov 6). Lower score = better (prefer county).
_STATEWIDE = re.compile(
    r'(statewide|state[-_]?wide|state[-_]?parcels?|stateparcels|nc1map_parcels|massachusetts_property_tax|'
    r'state[-_]?of[-_]?|nconemap|massgis.*parcel|parcel.*statewide|/state/)', re.I)
_COUNTYISH = re.compile(
    r'(county|parish|borough|township|cadast(re|ral)|pva|assessor|appraisal|/co[unt]*[-_/]|'
    r'countygis|county-?gis)', re.I)


def layer_scope_score(url):
    """0 = looks like a county/local layer, 1 = unknown, 2 = looks statewide. Prefer lower."""
    u = str(url or '')
    if not u: return 1
    if _STATEWIDE.search(u): return 2
    if _COUNTYISH.search(u): return 0
    return 1


def prefer_county_layer(urls, known_county_url=None):
    """Pick the best parcel layer URL: county/local before statewide. urls may mix None.
    known_county_url (from parcel-layers.json for this FIPS) is always considered and preferred when present."""
    cands = []
    if known_county_url: cands.append(str(known_county_url).strip())
    for u in (urls or []):
        if u and str(u).strip() and str(u).strip() not in cands:
            cands.append(str(u).strip())
    if not cands: return None, 'no layer URL'
    best = sorted(cands, key=lambda u: (layer_scope_score(u), len(u)))[0]
    note = None
    if known_county_url and best == str(known_county_url).strip() and any(layer_scope_score(u) == 2 for u in cands):
        note = f'preferred county layer over statewide ({known_county_url})'
    elif layer_scope_score(best) == 0 and any(layer_scope_score(u) == 2 for u in cands if u != best):
        note = f'preferred county-looking layer over statewide ({best})'
    return best, note


def is_ssl_status(st):
    """True when a Polite/jget status string is an SSL failure (err:SSLError / err:SSLCertVerificationError / ...)."""
    s = str(st or '')
    return bool(re.search(r'(?i)ssl|certificate', s))


def cached_basemap_ok(d, lat, lon, half_km, version, offline=False):
    """Nov 11 (KPC owner, 2026-11-11): may the picture tracer use this cached basemap (the dict fetch_basemap saved)?
    Returns (ok, why). Same box (pin + half_km) and same tracer basemap version are always needed. A PARTIAL basemap (a source was
    robots-skipped when it was fetched) is never reused by a normal run (owner call, Nov 7: the next run asks again); with --offline
    (no web request at all, e.g. a before / after replay on the same saved basemaps) it is used as it is, and its 'skipped' list still
    goes into the map's flags exactly as on the run that fetched it. The match gates never depend on where the basemap came from."""
    if not isinstance(d, dict):
        return False, 'no cached basemap'
    try:
        same_box = abs(float(d.get('half_km', 0)) - float(half_km)) < 1e-6 and list(d.get('pin') or []) == [lat, lon]
    except (TypeError, ValueError):
        same_box = False
    if not same_box:
        return False, 'cached basemap is for another box (pin or size changed)'
    if d.get('version') != version:
        return False, f"cached basemap is version {d.get('version')}, the tracer is {version}"
    if d.get('skipped') and not offline:
        return False, 'cached basemap is partial (' + ', '.join(map(str, d['skipped'])) + ' skipped); a normal run asks again'
    return True, 'basemap from cache' + (' (partial: ' + ', '.join(map(str, d['skipped'])) + ' skipped when it was fetched)' if d.get('skipped') else '')
