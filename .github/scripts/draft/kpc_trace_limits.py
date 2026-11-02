#!/usr/bin/env python3
"""TRACER LIMITS (Nov 2 2026 review; a local patch, not live until Brandon OKs it). Small pure helpers shared by the picture-map
tracer (kpc_trace_picture.py) and the parcel tracer (tools/kpc_parcel_trace/kpc_parcel_trace.py). Tested on their own
(kpc_engine/patches/tests/test_trace_limits.py). Defaults = what the tracers do today, except the two bug fixes marked (fix).

Switches (env; the picture tracer also has command-line flags):
  KPC_TRACE_HONOR_IMAGE   1  (fix) the picture tracer uses the image the prep step chose (row 'map_file', else row 'image'),
                             not the first <ref>_*.jpg on disk. 0 = today.
  KPC_TRACE_ACRES_FILE    '' an official acres list ({ref: acres} or {ref: {acres}}; data/acres.json) for rows with no acres, so the
                             picture tracer's scale prior is set (without it the scale search runs 0.2-25 m/px). '' = today.
  KPC_TRACE_CHANCE_RATIO  1.5 and KPC_TRACE_CHANCE_MARGIN 2.0: the 'better than chance' gate (real score must beat
                             max(ratio x decoy, decoy + margin)). Today's values.
  KPC_PARCEL_ADJ_M        200 the parcel tracer's adjacency (m). The review suggests 30 (200 m jumps roads onto the neighbour's land).
  KPC_PARCEL_GROW_CAP     0  stop growing at this many times the official acres (the review suggests 1.25); 0 = no cap (today).
  KPC_PARCEL_SUBTRACT     0  1 = cut other POTA parks' official outlines out of the result (today: only whole parcels mostly
                             inside another park are left out).
"""
import json, os

DEFAULTS = {'KPC_TRACE_HONOR_IMAGE': '1', 'KPC_TRACE_ACRES_FILE': '', 'KPC_TRACE_CHANCE_RATIO': '1.5', 'KPC_TRACE_CHANCE_MARGIN': '2.0',
            'KPC_PARCEL_ADJ_M': '200', 'KPC_PARCEL_GROW_CAP': '0', 'KPC_PARCEL_SUBTRACT': '0'}


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
    out = {}
    if not path: return out
    try: d = json.load(open(path, encoding='utf-8'))
    except Exception: return out  # noqa: BLE001
    d = d.get('parks', d) if isinstance(d, dict) else {}
    for r, v in (d.items() if isinstance(d, dict) else []):
        try: a = float(v.get('acres') if isinstance(v, dict) else v)
        except (TypeError, ValueError, AttributeError): continue
        if a > 0: out[r] = a
    return out


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
