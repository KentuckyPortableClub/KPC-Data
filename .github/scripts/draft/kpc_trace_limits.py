#!/usr/bin/env python3
"""TRACER LIMITS (Nov 2 2026 review; Nov 6: parcel defaults flipped to the review values Brandon OK'd).
Small pure helpers shared by the picture-map tracer (kpc_trace_picture.py) and the parcel tracer
(tools/kpc_parcel_trace/kpc_parcel_trace.py).

Switches (env; the picture tracer also has command-line flags):
  KPC_TRACE_HONOR_IMAGE   1  the picture tracer uses the image the prep step chose (row 'map_file', else row 'image'),
                             not the first <ref>_*.jpg on disk. 0 = old first-jpg pick.
  KPC_TRACE_ACRES_FILE    '' an official acres list ({ref: acres} or {ref: {acres}}; data/acres.json) for rows with no acres.
  KPC_TRACE_CHANCE_RATIO  1.5 and KPC_TRACE_CHANCE_MARGIN 2.0: the 'better than chance' gate.
  KPC_PARCEL_ADJ_M        30  (Nov 6 default; was 200) parcel adjacency in metres. 200 jumps roads onto the neighbour.
  KPC_PARCEL_GROW_CAP     1.25 (Nov 6 default; was 0) stop growing at this many times the official acres; 0 = no cap.
  KPC_PARCEL_SUBTRACT     1  (Nov 6 default; was 0) cut other POTA parks' official outlines out of the result.
  KPC_PARCEL_PARK_MIN     8  per-park wall-clock minutes; a hung host/statewide layer is skipped and the run continues.
  KPC_PARCEL_REQ_TIMEOUT  30 per-request HTTP timeout in seconds (Polite).
"""
import glob, json, os, re

DEFAULTS = {'KPC_TRACE_HONOR_IMAGE': '1', 'KPC_TRACE_ACRES_FILE': '', 'KPC_TRACE_CHANCE_RATIO': '1.5', 'KPC_TRACE_CHANCE_MARGIN': '2.0',
            'KPC_PARCEL_ADJ_M': '30', 'KPC_PARCEL_GROW_CAP': '1.25', 'KPC_PARCEL_SUBTRACT': '1',
            'KPC_PARCEL_PARK_MIN': '8', 'KPC_PARCEL_REQ_TIMEOUT': '30'}

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
