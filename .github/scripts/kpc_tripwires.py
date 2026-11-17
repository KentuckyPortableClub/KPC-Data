#!/usr/bin/env python3
"""TRIPWIRES T1-T5 (KPC owner, 2026-11-17; the owner's KEY MATCHING RULINGS D1-D11 in KPC-Links .claude/notes/mapping.md).
A REPORT, NOT A RULE. This bot counts five things that must be true of every join in the answer keys and lists the parks that break
them, grouped by pattern, for a person to work. It decides nothing: no key is built or changed, nothing on the map changes, no join
is made or removed, no 2-fer is held. D2 is ON TRIAL: the slack numbers below are first guesses, and nothing binds until the owner
says so. D10 (tripwire parks not sure for 2-fers) is NOT built here: it waits for the 2-fer phase.

It reads only files (a KPC-Links checkout): the keys (data/us-key/US-XX.json, data/ca-key/CA-XX.json, data/world-key/XX.json), the
POTA pins (locations.json) and the saved outlines (data/outlines/US-XX.geojson.gz, read through KPC-Links kpc_master.load_area so
parted areas are read whole). NO NETWORK: every socket connect is refused for the whole run. It writes only into --out (the KPC-Data
side branch `tripwires`; never main of KPC-Links). No layer address is written or printed: rows carry record ids, layer prefixes
(padus, sgtne, ...) and names only, and every text written is scrubbed of web / file addresses.

  T1  one record belongs to one park, unless a person said 'same land under two numbers' (D9): the same record id in the m rows of
      two or more parks in ONE key file. Every key (US, Canada, world).
  T2  every piece of a park's land connects back to its pin (D2 leg 2): per polygon of the saved outline, 0 when the pin is inside
      (holes respected), else the distance from the pin to its outer ring, on a flat plane centred on the pin; the distances
      sorted; a gap of more than GAP_KM between two neighbours cuts the chain. US (the saved outlines are US only).
  T3  a saved row still describes its record (name + acres it was saved with, D1). This needs the key build's OWN read of the layer,
      so it is REPORTED BY THE KEY BUILD, NOT HERE. t3_hook() below is the place it plugs in: when a key build writes
      data/<kind>/review/tripwire-t3.json ({"count": n, "rows": [...]}), its count is copied into the report; until then T3 says
      'from the key build (not counted here)'.
  T4  the pin is in or at the edge of the park's land, or a person is behind the join (D2): edge slack = the larger of EDGE_MIN_M or
      EDGE_SHARE of the park's radius (the radius of a circle with the outline's area); a person = an m row starting 'reviewed' or
      'official trail'. US.
  T5  a park's land comes from a layer of its own kind. That needs D11's labels (data/state-gis.json 'what'); until a rule reads
      them, only the SIZE FORM is counted: a record joined by name only (m row 'name'), drawn in the park's saved outline, more than
      SIZE_X times the acres of the record that holds the pin (the key's bk row at 0 km), from another layer. US.

Output (--out):
  counts/latest.json        this run's counts per area and per key, the slack numbers used, binds: false, the jump from the last run
  counts/history.csv        one line per key per run day (the meter: a new bad family shows as a jump the next morning)
  waiting/<T>/<pattern>.json  the rows, grouped by pattern, for a person (the waiting room on this branch)
  README.md                 what this branch is
and, with --not-sure FILE (D10, KPC-Data main data/waiting/tripwires/not-sure.json), the small list the 2-fer bot reads: every park
on T1, T2 or T4, with its reasons, that a person has not cleared (--cleared FILE, data/waiting/tripwires/cleared.json, written by
a person only: {"parks": {"US-1234": {"by": ..., "date": ..., "why": ...}}}). A T1 record whose every join is a person's (same land
under two numbers, D9) puts no park on it. The 2-fer bot (KPC-Links kpc_fers.py, D10) treats a listed park as NOT SURE; its
outline stays on the map. No list = the 2-fer bot changes nothing.
Exit 0 on every run that could read its inputs, whatever it counts (counts never turn a run red). Exit 1 only when something is
really wrong: no KPC-Links checkout, locations.json unreadable, or no key file at all. One area that cannot be read is a warning.

  python3 kpc_tripwires.py run --links <KPC-Links checkout> --out <tripwires branch checkout> [--keys us,ca,world] [--date YYYY-MM-DD]
  python3 kpc_tripwires.py run ... --not-sure <KPC-Data>/data/waiting/tripwires/not-sure.json --cleared <KPC-Data>/data/waiting/tripwires/cleared.json
  python3 kpc_tripwires.py run ... --dry-run      (counts printed, nothing written)"""
import argparse, csv, datetime as _dt, glob, io, json, math, os, pathlib, re, socket, sys

# ---- first guesses ON TRIAL (D2): the owner tunes these before anything binds. They change counts only, never a key.
GAP_KM = 25.0          # T2: an empty gap over this many km between two pieces cuts the chain
EDGE_MIN_M = 100.0     # T4: the pin may sit this many metres outside the land ...
EDGE_SHARE = 0.10      # ... or this share of the park's radius, whichever is larger
SIZE_X = 3.0           # T5 size form: a name-only record over this many times the pin-holding record
PERSON_HOW = ('reviewed', 'official trail')   # T4 'a person is behind the join'
BINDS = False          # nothing binds until the owner says (D2 on trial)
NOV17 = {'us': {'T1': 1366, 'T2': 268, 'T4': 580, 'T5': 82}, 'ca': {'T1': 348}, 'world': {'T1': 5564}}   # the owner's census, a sanity check only
KEY_GLOB = {'us': 'data/us-key/US-??.json', 'ca': 'data/ca-key/CA-??.json', 'world': 'data/world-key/*.json'}
ADDR = re.compile(r'(?:svc:)?(?:https?|ftp|file):[^\s"\'<>|,\]\)]*', re.I)


class NoNetwork(RuntimeError):
    pass


def no_network():
    """Refuse every socket connect / name lookup for the rest of the process (this bot reads files only)."""
    def refuse(*a, **k): raise NoNetwork('kpc_tripwires is offline: no network')
    socket.socket.connect = refuse
    socket.socket.connect_ex = refuse
    socket.create_connection = refuse
    socket.getaddrinfo = refuse


def scrub(x):
    """Every text that leaves this bot, with any web / file address taken out (no layer address in a public log)."""
    if isinstance(x, str): return ADDR.sub('[address withheld]', x)
    if isinstance(x, dict): return {scrub(k): scrub(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [scrub(v) for v in x]
    return x


def say(kind, title, msg):
    print(f'::{kind} title={title}::{scrub(msg)}', flush=True)


def layer_of(rid):
    """The layer a key record id comes from: PAD-US ids are plain numbers; other layers carry a letter prefix (sgtne289 -> sgtne)."""
    m = re.match(r'^([A-Za-z]+)', str(rid))
    return m.group(1).lower() if m else 'padus'


def read_keys(links, kind):
    """{area: parks} for one key; files that are not key files (index.json, layers.json ...) are skipped; an unreadable key file is
    listed in bad (a warning, never red)."""
    out, bad = {}, []
    for f in sorted(glob.glob(str(pathlib.Path(links) / KEY_GLOB[kind]))):
        try: pk = json.load(open(f, encoding='utf-8')).get('parks')
        except Exception as e:  # noqa: BLE001
            bad.append((pathlib.Path(f).stem, type(e).__name__)); continue
        if isinstance(pk, dict): out[pathlib.Path(f).stem] = pk
    return out, bad


def read_pins(links):
    pins = {}
    for r in json.load(open(pathlib.Path(links) / 'locations.json', encoding='utf-8')):
        try: lat, lon = float(r[3]), float(r[4])
        except Exception: continue  # noqa: BLE001
        if -90 <= lat <= 90 and -180 <= lon <= 180 and not (lat == 0 and lon == 0): pins[str(r[1])] = (lat, lon)
    return pins


def read_outlines(links):
    """{ref: [(area, record)]} over every saved US area (kpc_master.load_area reads every part; a part missing = that area is
    unread, never half read)."""
    sys.path.insert(0, str(pathlib.Path(links) / '.github/scripts'))
    import kpc_master as M  # noqa: E402  (KPC-Links; imported for its file reader only, no request is made)
    out, bad = {}, []
    root = pathlib.Path(links) / 'data/outlines'
    for f in sorted(root.glob('US-??.geojson.gz')):
        area = f.name[:5]
        try: recs = M.load_area(area, root)
        except Exception as e:  # noqa: BLE001
            bad.append((area, type(e).__name__)); continue
        for ref, rec in recs.items(): out.setdefault(ref, []).append((area, rec))
    return out, bad


def person(rows):
    return any(str(m[3] if len(m) > 3 else '').startswith(PERSON_HOW) for m in rows)


# ---------------------------------------------------------------- T1
def record_of(kind, m):
    """(identity, layer label) of one m row. US / Canada: the id (a plain number = PAD-US / CPCAD; a prefixed id = that layer).
    World: the row's source + the id, so two layers' equal numbers are not one record (as kpc_fers.join_record_ids keeps them)."""
    rid = str(m[0])
    if kind == 'world':
        src = str(m[2]) if len(m) > 2 and isinstance(m[2], str) else ''
        return (src, rid), (re.sub(r'[^a-z0-9]+', '-', src.lower()).strip('-')[:40] or 'world')
    lay = layer_of(rid)
    return ('', rid), ('cpcad' if kind == 'ca' and lay == 'padus' else lay)


def how_of(m):
    h = str(m[3] if len(m) > 3 else '?')
    return 'person' if person([m]) else (re.split(r'[\s:\u00b7+]+', h.strip()) or ['?'])[0].lower() or '?'


def t1(keys, kind='us'):
    """Rows: one per (area, record) held by two or more parks of that key file. Also returns the census-method count (the plain
    record id, any layer: how the owner's 17 Nov census was counted) so the meter can be compared with it."""
    rows, census = [], 0
    for area, pk in sorted(keys.items()):
        by, plain = {}, {}
        for ref, p in pk.items():
            for m in (p.get('m') or []):
                if not m: continue
                ident, lay = record_of(kind, m)
                by.setdefault(ident, []).append((ref, m, lay))
                plain.setdefault(str(m[0]), set()).add(ref)
        census += sum(1 for v in plain.values() if len(v) > 1)
        for ident, held in sorted(by.items()):
            refs = sorted({r for r, _, _ in held})
            if len(refs) < 2: continue
            hows = sorted({how_of(m) for _, m, _ in held}); lay = held[0][2]
            rows.append({'area': area, 'record': ident[1], 'layer': lay, 'record_name': str(held[0][1][1] if len(held[0][1]) > 1 else ''),
                         'parks': refs, 'how': hows, 'all_person': all(person([m]) for _, m, _ in held),
                         'pattern': f"{lay}_{'+'.join(hows)}"})
    return rows, census


# ---------------------------------------------------------------- geometry (T2 / T4)
# Standard library only (17 Nov, sent back from review: a runner without shapely / pyproj counted no T2 / T4 and the test died on
# its sample data). Each vertex goes onto an azimuthal equidistant plane centred on the pin (spherical, mean Earth radius): the
# distance from the pin to every vertex is exact on the sphere, which is what T2 and T4 measure. Holes are respected: a pin in a
# hole is not inside, and its distance is to the outer ring.
R_EARTH_M = 6371008.8


def _plane(lat0, lon0):
    """(lon, lat) -> (x, y) metres on the azimuthal equidistant plane centred on (lat0, lon0) (sphere)."""
    p0, s0, c0 = math.radians(lat0), math.sin(math.radians(lat0)), math.cos(math.radians(lat0))
    def f(lon, lat):
        p, dl = math.radians(lat), math.radians(lon - lon0)
        sp, cp = math.sin(p), math.cos(p)
        h = math.sin((p - p0) / 2) ** 2 + c0 * cp * math.sin(dl / 2) ** 2
        c = 2 * math.asin(min(1.0, math.sqrt(max(h, 0.0))))
        if c == 0: return 0.0, 0.0
        az = math.atan2(math.sin(dl) * cp, c0 * sp - s0 * cp * math.cos(dl))
        return R_EARTH_M * c * math.sin(az), R_EARTH_M * c * math.cos(az)
    return f


def _polygons(g):
    """The polygons (lists of rings of [lon, lat]) of a GeoJSON geometry: Polygon, MultiPolygon, or a GeometryCollection of them."""
    t = (g or {}).get('type')
    if t == 'Polygon': return [g.get('coordinates') or []]
    if t == 'MultiPolygon': return list(g.get('coordinates') or [])
    if t == 'GeometryCollection': return [p for x in (g.get('geometries') or []) for p in _polygons(x)]
    return []


def _ring_xy(ring, f):
    pts = [f(float(c[0]), float(c[1])) for c in ring if c is not None and len(c) >= 2]
    if len(pts) > 1 and pts[0] == pts[-1]: pts.pop()
    return pts


def _contains_origin(pts):
    """Even-odd ray cast from (0, 0) along +x."""
    inside, n = False, len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[i - 1]
        if (y1 > 0) != (y2 > 0) and x1 + (0 - y1) * (x2 - x1) / (y2 - y1) > 0: inside = not inside
    return inside


def _dist_origin(pts):
    """Distance from (0, 0) to the closed ring pts."""
    best, n = math.inf, len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i - 1], pts[i]
        dx, dy = x2 - x1, y2 - y1; L = dx * dx + dy * dy
        t = 0.0 if L == 0 else max(0.0, min(1.0, -(x1 * dx + y1 * dy) / L))
        best = min(best, math.hypot(x1 + t * dx, y1 + t * dy))
    return best


def _area(pts):
    return abs(sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))) / 2


def pieces(recs, lat, lon):
    """[(distance m, area m2)] per polygon of a park's land (all its saved outline records), on a flat plane centred on the pin."""
    f = _plane(lat, lon); out = []
    for _area_name, rec in recs:
        for poly in _polygons(rec.get('geometry')):
            rings = [r for r in (_ring_xy(x, f) for x in poly or []) if len(r) >= 3]
            if not rings: continue
            shell, holes = rings[0], rings[1:]
            a = _area(shell) - sum(_area(h) for h in holes)
            if a <= 0: continue
            d = _dist_origin(shell)
            inside = d == 0 or (_contains_origin(shell) and not any(_contains_origin(h) and _dist_origin(h) > 0 for h in holes))
            out.append((0.0 if inside else d, a))
    return out


def t2_cut(dists, gap_m):
    """The chain: distances sorted; True (and the gap) when two neighbours are more than gap_m apart."""
    d = sorted(dists); worst = 0.0; cut_at = None
    for a, b in zip(d, d[1:]):
        if b - a > gap_m and b - a > worst: worst, cut_at = b - a, a
    n_off = sum(1 for x in d if cut_at is not None and x > cut_at)
    return worst > gap_m, worst, n_off


def edge_slack(area_m2):
    return max(EDGE_MIN_M, EDGE_SHARE * math.sqrt(max(area_m2, 0.0) / math.pi))


def band(km, edges, unit='km'):
    for lo, hi in zip(edges, edges[1:]):
        if km <= hi: return f'{lo:g}-{hi:g}{unit}'
    return f'over-{edges[-1]:g}{unit}'


def t2_t4(outl, pins, keys):
    by_ref = {}
    for area, pk in keys.items():
        for ref, p in pk.items(): by_ref.setdefault(ref, []).append((area, p))
    r2, r4, nopin = [], [], 0
    for ref, recs in sorted(outl.items()):
        if ref not in pins: nopin += 1; continue
        lat, lon = pins[ref]
        ps = pieces(recs, lat, lon)
        if not ps: continue
        areas = sorted({a for a, _ in recs}); name = next((str(r.get('name') or '') for _, r in recs), '')
        grade = next((str(r.get('g') or '') for _, r in recs), '')
        cut, gap, n_off = t2_cut([d for d, _ in ps], GAP_KM * 1000)
        if cut:
            r2.append({'ref': ref, 'name': name, 'areas': areas, 'grade': grade, 'pieces': len(ps), 'pieces_cut_off': n_off,
                       'gap_km': round(gap / 1000, 1), 'pattern': 'gap_' + band(gap / 1000, [GAP_KM, 50, 100, 500])})
        near = min(d for d, _ in ps); slack = edge_slack(sum(a for _, a in ps))
        rows_m = [m for _, p in by_ref.get(ref, []) for m in (p.get('m') or []) if m]
        if near > slack and not person(rows_m):
            r4.append({'ref': ref, 'name': name, 'areas': areas, 'grade': grade, 'pin_km_from_land': round(near / 1000, 2),
                       'slack_m': round(slack), 'pattern': f"{grade or 'nograde'}_" + band(near / 1000, [0, 1, 5, 25])})
    return r2, r4, nopin


# ---------------------------------------------------------------- T5 (size form, until D11's labels are read by a rule)
def t5_size(keys, outl):
    drawn = {}
    for ref, recs in outl.items():
        for _a, r in recs:
            drawn.setdefault(ref, set()).update(str(x) for x in (r.get('record_ids') or []))
    rows, seen = [], set()
    for area, pk in sorted(keys.items()):
        for ref, p in sorted(pk.items()):
            bk, m = p.get('bk') or [], p.get('m') or []
            if len(bk) < 2 or bk[1] != 0 or not m: continue     # the pin-holding record: the key's bk row at 0 km
            byid = {str(x[0]): x for x in m if x}
            hid = str(bk[0]); h = byid.get(hid)
            if not h or not isinstance(h[2], (int, float)) or h[2] <= 0: continue
            for x in m:
                if str(x[0]) == hid or str(x[3] if len(x) > 3 else '') != 'name' or layer_of(x[0]) == layer_of(hid): continue
                if not isinstance(x[2], (int, float)) or x[2] <= SIZE_X * h[2] or str(x[0]) not in drawn.get(ref, set()): continue
                if (ref, str(x[0])) in seen: continue
                seen.add((ref, str(x[0])))
                rows.append({'ref': ref, 'name': str(p.get('n') or ''), 'area': area, 'pin_record': hid, 'pin_record_layer': layer_of(hid),
                             'pin_record_name': str(h[1]), 'pin_record_acres': h[2], 'big_record': str(x[0]), 'big_record_layer': layer_of(x[0]),
                             'big_record_name': str(x[1]), 'big_record_acres': x[2], 'times': round(x[2] / h[2], 1),
                             'pattern': f'{layer_of(hid)}_to_{layer_of(x[0])}'})
    return rows


# ---------------------------------------------------------------- T3 (from the key build)
def t3_hook(links, kind):
    """T3 IS PRODUCED BY THE KEY BUILD, NOT BY THIS BOT (it needs the build's own read of the layer: D1). When a key build writes
    data/<kind>-key/review/tripwire-t3.json ({"count": n, "rows": [...]}), its count is carried into this report as it is. No file =
    'from the key build (not counted here)'. This bot never works T3 out itself."""
    f = pathlib.Path(links) / f'data/{kind}-key/review/tripwire-t3.json'
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: return {'T3': 'from the key build (not counted here)'}  # noqa: BLE001
    c = d.get('count') if isinstance(d, dict) else None
    return {'T3': c if isinstance(c, int) else 'from the key build (file unreadable)'}


# ---------------------------------------------------------------- report
def per_area(rows, key='area'):
    c = {}
    for r in rows:
        for a in (r.get('areas') or [r.get(key)]): c[a] = c.get(a, 0) + 1
    return c


def count_refs(rows, by='ref'):
    return len({r[by] for r in rows})


def run(a):
    no_network()
    links = pathlib.Path(a.links)
    if not (links / 'locations.json').is_file():
        say('error', 'Tripwires', f'no KPC-Links checkout at {links} (locations.json missing): nothing counted'); return 1
    try: pins = read_pins(links)
    except Exception as e:  # noqa: BLE001
        say('error', 'Tripwires', f'locations.json unreadable ({type(e).__name__}): nothing counted'); return 1
    kinds = [k.strip() for k in a.keys.split(',') if k.strip() in KEY_GLOB]
    date = a.date or _dt.date.today().isoformat()
    report = {'date': date, 'binds': BINDS, 'report_only': True,
              'about': 'Tripwires T1-T5 (owner rulings D1-D11, 17 Nov 2026). A REPORT: it changes no key, no join, no map and no 2-fer. '
                       'D2 is on trial: the slack numbers are first guesses; nothing binds until the owner says. D10 is not built.',
              'on_trial': {'T2_gap_km': GAP_KM, 'T4_edge_min_m': EDGE_MIN_M, 'T4_edge_share_of_radius': EDGE_SHARE, 'T5_size_times': SIZE_X,
                           'T4_person': list(PERSON_HOW)},
              'reference_nov17': NOV17, 'totals': {}, 'areas': {}, 'unread': [], 'not_counted': {}}
    waiting = {}
    all_keys = {}
    for kind in kinds:
        keys, bad = read_keys(links, kind)
        all_keys[kind] = keys
        for area, why in bad:
            report['unread'].append({'area': area, 'why': why}); say('warning', 'Tripwires', f'{area}: key file unreadable ({why}); left out of this run')
    if not any(all_keys.values()):
        say('error', 'Tripwires', 'no key file could be read: nothing counted'); return 1
    for kind in kinds:
        keys = all_keys[kind]
        r1, census = t1(keys, kind)
        tot = {'T1': len(r1)}
        if census != len(r1): tot['T1_census_method'] = census   # world: the plain id across layers (the 17 Nov census way)
        tot.update(t3_hook(links, kind))
        for ar, n in per_area(r1).items(): report['areas'].setdefault(ar, {})['T1'] = n
        waiting.setdefault('T1', []).extend(r1)
        if kind == 'us':
            try:
                outl, bad = read_outlines(links)
                for area, why in bad:
                    report['unread'].append({'area': area, 'why': why}); say('warning', 'Tripwires', f'{area}: saved outlines unreadable ({why}); left out')
            except Exception as e:  # noqa: BLE001
                outl = {}; report['not_counted']['us'] = f'saved outlines not read ({type(e).__name__})'
                say('warning', 'Tripwires', f'saved outlines not read ({type(e).__name__}): T2, T4 and T5 not counted this run')
            if outl:
                r2, r4, nopin = t2_t4(outl, pins, keys)
                tot['T2'], tot['T4'] = count_refs(r2), count_refs(r4)
                report['us_outlined_parks'] = len(outl); report['us_outlined_no_pin'] = nopin
                for t, rows in (('T2', r2), ('T4', r4)):
                    for ar, n in per_area(rows).items(): report['areas'].setdefault(ar, {})[t] = n
                    waiting.setdefault(t, []).extend(rows)
            if outl:
                r5 = t5_size(keys, outl)
                tot['T5'] = count_refs(r5); tot['T5_form'] = 'size form only (D11 labels not read by a rule yet)'
                for ar, n in per_area(r5).items(): report['areas'].setdefault(ar, {})['T5'] = n
                waiting.setdefault('T5', []).extend(r5)
        else:
            tot.update({'T2': 'no saved outlines for this key', 'T4': 'no saved outlines for this key', 'T5': 'no saved outlines for this key'})
        report['totals'][kind] = tot
    out = pathlib.Path(a.out) if a.out else None
    prev = None
    if out and (out / 'counts/latest.json').is_file():
        try: prev = json.load(open(out / 'counts/latest.json', encoding='utf-8'))
        except Exception: prev = None  # noqa: BLE001
    report['jump'] = jump(prev, report)
    report['patterns'] = {t: sorted({r['pattern'] for r in rows}) for t, rows in waiting.items()}
    report['new_patterns'] = new_patterns(prev, report)
    report = scrub(report)
    for kind, tot in report['totals'].items():
        ref = NOV17.get(kind, {})
        cm = f" (census way {tot['T1_census_method']}, 17 Nov: {ref['T1']})" if 'T1_census_method' in tot else ''
        say('notice', f'Tripwires {kind}', ', '.join(f"{t} {tot.get(t)}" + (cm if t == 'T1' and cm else f" (17 Nov: {ref[t]})" if t in ref else '') for t in ('T1', 'T2', 'T3', 'T4', 'T5') if t in tot))
    for kind, j in report['jump'].items():
        if j: say('notice', f'Tripwires {kind} since last run', ', '.join(f'{t} {d:+d}' for t, d in j.items()))
    if a.dry_run or not out:
        print(json.dumps({'totals': report['totals'], 'jump': report['jump']}, indent=1)); print('dry run: nothing written'); return 0
    write(out, report, waiting)
    if a.not_sure:
        ns = not_sure_list(waiting, read_cleared(a.cleared), date)
        pathlib.Path(a.not_sure).parent.mkdir(parents=True, exist_ok=True)
        txt = json.dumps(scrub(ns), ensure_ascii=False, sort_keys=True, separators=(',', ':')).replace('],"', '],\n"') + '\n'
        pathlib.Path(a.not_sure).write_text(txt, encoding='utf-8', newline='\n')
        say('notice', 'Tripwires not-sure list', f"{len(ns['parks'])} parks not sure for 2-fers until a person clears them ({ns['cleared_left_out']} cleared by a person left out)")
    return 0


def read_cleared(path):
    """Refs a PERSON cleared (data/waiting/tripwires/cleared.json, never written by a bot). Missing / unreadable = none cleared."""
    if not path: return set()
    try: d = json.load(open(path, encoding='utf-8'))
    except Exception: return set()  # noqa: BLE001
    pk = d.get('parks') if isinstance(d, dict) else None
    return {str(r) for r, v in (pk or {}).items() if isinstance(v, dict) and str(v.get('by') or '').strip()}


def not_sure_list(waiting, cleared, date):
    """D10: {ref: [reasons]} for every park on T1 (not a person's same-land record), T2 or T4, less the parks a person cleared."""
    why = {}
    for r in waiting.get('T1', []):
        if r.get('all_person'): continue
        for ref in r['parks']: why.setdefault(ref, set()).add('T1')
    for r in waiting.get('T2', []): why.setdefault(r['ref'], set()).add('T2')
    for r in waiting.get('T4', []): why.setdefault(r['ref'], set()).add('T4')
    left = sorted(set(why) & cleared)
    return {'about': 'D10 (owner, 17 Nov 2026): parks on tripwire T1, T2 or T4 are NOT SURE for 2-fers until a person clears them '
                     '(data/waiting/tripwires/cleared.json). Their outline stays on the map. Written by kpc_tripwires.py; read by KPC-Links kpc_fers.py.',
            'reasons': {'T1': 'one of its records is also joined to another park in the same key file (not a person\'s same-land record)',
                        'T2': f'a piece of its land is cut off from its pin by an empty gap over {GAP_KM:g} km',
                        'T4': f'its pin is outside its land by more than max({EDGE_MIN_M:g} m, {EDGE_SHARE:g} x its radius) and no person is behind the join'},
            'detail': 'the rows behind each reason: KPC-Data branch tripwires, waiting/T1, T2, T4',
            'date': date, 'on_trial': True, 'cleared_left_out': len(left),
            'parks': {ref: sorted(w) for ref, w in sorted(why.items()) if ref not in cleared}}


def jump(prev, now):
    out = {}
    for kind, tot in now['totals'].items():
        was = ((prev or {}).get('totals') or {}).get(kind) or {}
        out[kind] = {t: tot[t] - was[t] for t in ('T1', 'T2', 'T3', 'T4', 'T5') if isinstance(tot.get(t), int) and isinstance(was.get(t), int) and tot[t] != was[t]}
    return out


def new_patterns(prev, now):
    if not prev: return {}
    was = prev.get('patterns') or {}
    return {t: sorted(set(p) - set(was.get(t) or [])) for t, p in now['patterns'].items() if set(p) - set(was.get(t) or [])}


def write(out, report, waiting):
    (out / 'counts').mkdir(parents=True, exist_ok=True)
    wroot = out / 'waiting'
    if wroot.is_dir():   # this run's waiting room replaces the last one (the counts history keeps the meter)
        for f in wroot.glob('*/*.json'): f.unlink()
    for t, rows in waiting.items():
        groups = {}
        for r in rows: groups.setdefault(r['pattern'], []).append(r)
        for pat, rs in groups.items():
            d = wroot / t; d.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r'[^A-Za-z0-9_.+-]', '_', pat)[:80]
            body = {'tripwire': t, 'pattern': pat, 'date': report['date'], 'binds': False,
                    'for_a_person': 'report only: work these rows by hand; a fix comes with its park list and runs park-scoped (KPC_KEY_ONLY_PARKS)',
                    'rows': len(rs), 'items': rs}
            (d / f'{safe}.json').write_text(json.dumps(scrub(body), indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    (out / 'counts/latest.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    hist = out / 'counts/history.csv'; head = ['date', 'key', 'T1', 'T2', 'T3', 'T4', 'T5']
    rows = []
    if hist.is_file():
        rows = [r for r in csv.DictReader(open(hist, encoding='utf-8', newline='')) if r.get('date') != report['date']]
    for kind, tot in report['totals'].items():
        rows.append({'date': report['date'], 'key': kind, **{t: tot.get(t, '') if isinstance(tot.get(t), int) else '' for t in head[2:]}})
    rows = sorted(rows, key=lambda r: (r['date'], r['key']))[-3 * 400:]
    buf = io.StringIO(); w = csv.DictWriter(buf, head, lineterminator='\n'); w.writeheader(); w.writerows(rows)
    hist.write_text(buf.getvalue(), encoding='utf-8', newline='\n')
    (out / 'README.md').write_text(README, encoding='utf-8', newline='\n')


README = """# Tripwires T1-T5 (report only)

Written by KPC-Data `.github/scripts/kpc_tripwires.py` (workflow `KPC tripwires`, by hand until HQ turns its schedule on).
Owner rulings D1-D11, 17 Nov 2026. This branch is a REPORT: nothing here changes a key, a join, the map or a 2-fer.
D2 is on trial: the slack numbers in `counts/latest.json` (`on_trial`) are first guesses; nothing binds until the owner says.

- `counts/latest.json`: this run's counts per key and per area, and the change since the last run (`jump`).
- `counts/history.csv`: one line per key per day. A new bad family shows as a jump the next morning.
- `waiting/T1..T5/<pattern>.json`: the parks to work by hand, grouped by pattern. A fix comes with its park list and runs
  park-scoped (KPC_KEY_ONLY_PARKS), never a fifty-state rebuild.
- T3 (a saved row still describes its record) is reported by the key build, not here.
- T5 is the size form only until a rule reads the D11 layer labels.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--links', required=True); r.add_argument('--out', default='')
    r.add_argument('--keys', default='us,ca,world'); r.add_argument('--date', default='')
    r.add_argument('--not-sure', default='', help='D10: write the not-sure list here (KPC-Data data/waiting/tripwires/not-sure.json)')
    r.add_argument('--cleared', default='', help='D10: parks a person cleared (KPC-Data data/waiting/tripwires/cleared.json)')
    r.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(argv)
    try: return run(a)
    except NoNetwork as e:
        say('error', 'Tripwires', f'a network call was tried and refused ({e}): this bot must stay offline'); return 1


if __name__ == '__main__':
    sys.exit(main())
