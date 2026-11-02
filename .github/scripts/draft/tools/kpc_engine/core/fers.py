"""The club's 2-fer / 3-fer rules (round 4, Nov 1 2026). NEVER automatic: everything here only builds suggestions for the
waiting room (fers-waiting-room.json, checked by chat 8 + chat 11). Our label is "Overlapping boundaries", never "shared".

  * A trail with no land boundary of its own counts within 100 ft of its line (water trails: 100 ft of the water's edge).
  * A wild / scenic river corridor uses its own boundary; the 100 ft rule does not apply.
  * Parks that only touch do not overlap (zero-area contact is not an overlap).
  * A trail inside two parks that overlap is fine; it can make a 3-fer when a spot within 100 ft of the trail sits inside the
    overlap patch (all three share one patch).
  * The overlap patch must hold a spot at least 50 yards across (club 2-fer bar)."""
import math
from core import geo

FT100_M = geo.FT100_M          # 30.48 m
YD50_M = geo.YD50_M            # 45.72 m
LABEL = 'Overlapping boundaries'
TOUCH_M2 = 1.0                 # below this the parks only touch (edge / corner contact, slivers from digitising)


def _ft100():
    from core import rules
    return rules.num('fer_line_ft') * 0.3048


def zone(g, kind, lat, lon, water=None):
    """The area that counts as the park, in local metres around (lat, lon).
    kind: 'land' (its own polygon), 'wsr' (wild / scenic river corridor: own boundary, no 100 ft rule),
          'trail' (no land boundary: line + 100 ft), 'water_trail' (100 ft of the water's edge; the line + 100 ft when no water polygon)."""
    if not geo.HAVE or g is None: return None
    t = geo._local(lat, lon)
    G = geo._tf(t.transform, g)
    if kind in ('land', 'wsr'): return G
    if kind == 'water_trail' and water is not None: return geo._tf(t.transform, water).buffer(_ft100())
    return G.buffer(_ft100())


def overlap_patch(A, B):
    """The overlap patch of two zones (local metres), or None when they only touch / do not meet."""
    if A is None or B is None: return None
    ov = A.intersection(B)
    if ov.is_empty or ov.area < TOUCH_M2: return None
    return ov


def widest_m(p):
    if p is None: return 0.0
    try:
        from shapely import maximum_inscribed_circle
        parts = p.geoms if hasattr(p, 'geoms') else [p]
        return max((2 * maximum_inscribed_circle(q, tolerance=0.5).length for q in parts if q.geom_type == 'Polygon' and q.area > 1), default=0.0)
    except Exception:  # noqa: BLE001
        return 2 * math.sqrt(p.area / math.pi)


def two_fer(A, B):
    """-> {'relation': 'overlap'|'touching only'|'apart', 'widest_m', 'suggest'}. suggest is a waiting-room suggestion only."""
    if A is None or B is None: return {'relation': 'unknown', 'widest_m': None, 'suggest': False}
    p = overlap_patch(A, B)
    if p is None: return {'relation': 'touching only' if A.intersects(B) else 'apart', 'widest_m': 0.0, 'suggest': False}
    w = widest_m(p)
    return {'relation': 'overlap', 'widest_m': round(w, 1), 'suggest': w >= YD50_M}


def three_fer(trail_zone, A, B):
    """A trail (its 100 ft zone, or a WSR's own corridor) + two overlapping parks: a 3-fer suggestion when the trail zone reaches
    into the A∩B patch."""
    p = overlap_patch(A, B)
    if p is None or trail_zone is None: return {'relation': 'no overlap patch', 'suggest': False}
    spot = overlap_patch(trail_zone, p)
    return {'relation': 'trail reaches the overlap patch' if spot is not None else 'trail misses the overlap patch',
            'suggest': spot is not None, 'spot_m2': round(spot.area, 1) if spot is not None else 0.0}


def suggestion(refs, why, evidence=None):
    """A waiting-room row. Never written to the club's 2-fer list by the engine."""
    return {'refs': sorted(refs), 'label': LABEL, 'kind': '3-fer' if len(refs) >= 3 else '2-fer', 'why': why,
            'evidence': evidence or {}, 'auto': False, 'goes_to': 'waiting room: chat 8 + chat 11 check by hand',
            'answer': '', 'checked_by': ''}


def from_trail_rows(rows):
    """Trail features filed under 2+ parks: label them "Overlapping boundaries" (not a failure) and return waiting-room rows."""
    from core import rule_g
    out = []
    got = [r for r in rows if r and r.get('status') in ('found', 'candidate')]
    for key, refs in rule_g.same_points(got).items():
        names_ = {}
        for r in got:
            for f in r.get('features') or []:
                if (round(f['lat'], 5), round(f['lon'], 5)) == key:
                    f['overlap'] = LABEL; f['overlap_refs'] = [x for x in refs if x != r['ref']]
                    names_[r['ref']] = r.get('park')
        out.append(suggestion(refs, 'one official trail feature sits in two or more parks (Overlapping boundaries); '
                              'check the overlap patch and the 100 ft trail rule by hand', {'point': list(key), 'parks': names_}))
    seen, uniq = set(), []
    for s in out:
        k = tuple(s['refs'])
        if k in seen: continue
        seen.add(k); uniq.append(s)
    return uniq
