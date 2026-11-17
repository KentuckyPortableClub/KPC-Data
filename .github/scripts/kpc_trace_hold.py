#!/usr/bin/env python3
"""TRACE HOLD (KPC owner, 2026-11-17; Handoff 3 "tracers and the PDF finder"). Wires the existing tracers to the keeper's list of
parks with no official record and HOLDS every result. Nothing here installs anything: no trace reaches the store, KPC-Links
data/fers-approx-outlines.json, a key, the public map or the 2-fer line. There is no scoring step (the owner and Fable review the
held traces after a few days, Fable adjusts the tracers, and it runs again).

Per park on the list, in this order (the chain), stopping at the first step that gives an answer:
  card     the evidence card from stored files (kpc_evidence_card.py); PROPOSE JOIN / EASY FIX = an official record lead: no trace
  a. a stored trace: the picture tracer's output (<ref>.json DRAWN) or the parcel tracer's (parcels/<area>.json DRAWN) -> HELD
  b. a picture map already on branch picture-maps, not traced yet -> "to trace (picture)": the picture tracer takes it next run
  c. a parcel-tracer input row (kpc_trace_prep.py parks.json) -> "to trace (parcel)"
  d. the PDF finder (kpc_pdf_finder.py, find only): portal -> agency page Maps -> web search; a found PDF is queued for picture-maps
HELD = the store's hand-file format on the orphan branch `traces`, one folder per area:
  <area>/<ref>.geojson          the outline (approximate, official false, use_for_2fer false, held true)
  <area>/<ref>.kpc-source.json  kind traced, the tracer's name, the source file's URL, the page used, the source's terms
  <area>/<ref>.jpg | .svg       a small picture of the trace over the map it came from (the parcel tracer has no map: outline + pin)
  index.json                    one review row per trace: source map link, page, method, traced acres, official acres, pin inside
A do-not-share source or a general parcel file is never saved (logged "private input, not saved here"); WDPA is never a source.
A trace is deleted from `traces` the day its park gets an official outline (prune), the same way a picture map is.

  python3 kpc_trace_hold.py asks-from-why-not --links <KPC-Links> --data <KPC-Data> --areas US-AR,CA-ON --out asks.json   (SUBSTITUTE list)
  python3 kpc_trace_hold.py limit-index --asks asks.json --pic-base <picture-maps checkout>    (the tracer traces listed parks only)
  python3 kpc_trace_hold.py limit-parks --asks asks.json --parks parks.json                   (the same for the parcel tracer)
  python3 kpc_trace_hold.py run --asks asks.json --data . --links ../links --picture-maps ../pm --picture-traced ../pm/traced \
        --parcel-traced ../parcel-out --traces ../traces --receipt ../traces/receipts/<date>.json [--finder-queue DIR ...] [--dry-run]
  python3 kpc_trace_hold.py prune --traces ../traces --links ../links
  python3 kpc_trace_hold.py --selftest"""
import csv, datetime as _dt, json, os, pathlib, re, shutil, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kpc_evidence_card as EC  # noqa: E402

FORBIDDEN = re.compile(r'(^|/)(fers-approx-outlines\.json|outlines/|(us|ca|world)-key/|kpc-ky-data\.json|locations-[a-z]+\.json|'
                       r'index\.html|store-data/|gis-list/|tracer-inputs(-found)?\.csv|waiting/)', re.I)
PRIVATE_TERMS = re.compile(r'do[- ]not[- ]share|not for (re)?distribution|internal use|confidential|private|licen[cs]ed to the club only|no redistribution', re.I)
WDPA = re.compile(r'protectedplanet|\bwdpa\b|wdpa[_-]', re.I)
MAX_FILE = 900_000      # under the 1 MB per file rule
GRADE = 'approximate (traced, held for review)'


class HoldRefused(Exception):
    """A write the hold guard refuses: the run stops (red), nothing is written there."""


class HoldWriter:
    """The ONLY way this job writes a trace. Every path must sit inside the traces root, never name a store / key / 2-fer / site
    file, and the root must not be (inside) a KPC-Links checkout or a KPC-Data main checkout."""

    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        for p in [self.root, *self.root.parents]:
            if (p / '.github/scripts/kpc_fers.py').exists() or (p / 'data/fers-approx-outlines.json').exists():
                raise HoldRefused(f'{self.root} is inside a KPC-Links checkout: traces are never written there')
            if (p / 'data/parkinfo').is_dir() and (p / '.github').is_dir():
                raise HoldRefused(f'{self.root} is inside a KPC-Data main checkout: traces live on the orphan branch traces')
        if (self.root / '.git').exists():
            b = subprocess.run(['git', '-C', str(self.root), 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True).stdout.strip()
            if b != 'traces': raise HoldRefused(f'{self.root} is a git checkout of {b!r}, not the traces branch')
        self.written = []

    def path(self, rel):
        rel = str(rel).replace('\\', '/')
        if rel.startswith('/') or '..' in rel.split('/') or FORBIDDEN.search(rel):
            raise HoldRefused(f'{rel}: not a held-trace path (store / key / 2-fer / site files are never written)')
        p = (self.root / rel).resolve()
        if self.root not in p.parents and p != self.root: raise HoldRefused(f'{rel}: outside the traces folder')
        return p

    def write(self, rel, data):
        p = self.path(rel)
        b = data.encode('utf-8') if isinstance(data, str) else data
        if len(b) > MAX_FILE: raise HoldRefused(f'{rel}: {len(b)} bytes is over the 1 MB rule')
        if isinstance(data, str) and '\r' in data: raise HoldRefused(f'{rel}: CR line ending (LF only)')
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b); self.written.append(rel)
        return p

    def remove(self, rel):
        p = self.path(rel)
        if p.exists(): p.unlink(); self.written.append('-' + rel)


def jdump(o): return json.dumps(o, indent=1, ensure_ascii=False) + '\n'


def _load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


# ---------------- geometry (no outside library) ----------------
def _rings(g):
    t = (g or {}).get('type')
    if t == 'Polygon': return [g['coordinates']]
    if t == 'MultiPolygon': return list(g['coordinates'])
    return []


def _in_ring(x, y, ring):
    inside = False
    for i in range(len(ring)):
        x1, y1 = ring[i][:2]; x2, y2 = ring[i - 1][:2]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-15) + x1: inside = not inside
    return inside


def pin_inside(geom, lat, lon):
    """True / False for an area; None for a line (a route has no inside) or no pin."""
    if lat is None or lon is None: return None
    polys = _rings(geom)
    if not polys: return None
    return any(_in_ring(lon, lat, p[0]) and not any(_in_ring(lon, lat, h) for h in p[1:]) for p in polys if p)


def svg_picture(geom, lat, lon, title):
    pts = [c for p in _rings(geom) for r in p for c in r] or ([c for c in geom.get('coordinates') or []] if (geom or {}).get('type') == 'LineString' else [])
    if lat is not None: pts = pts + [[lon, lat]]
    if not pts: return ''
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); s = 380 / max(x1 - x0, y1 - y0, 1e-9)
    f = lambda c: f'{10 + (c[0] - x0) * s:.1f},{10 + (y1 - c[1]) * s:.1f}'
    body = ''.join(f'<polygon points="{" ".join(f(c) for c in r)}" fill="#ffd70055" stroke="#c00" stroke-width="1.5"/>' for p in _rings(geom) for r in p[:1])
    if (geom or {}).get('type') == 'LineString': body += f'<polyline points="{" ".join(f(c) for c in geom["coordinates"])}" fill="none" stroke="#c00" stroke-width="2"/>'
    if lat is not None: body += f'<circle cx="{f([lon, lat]).split(",")[0]}" cy="{f([lon, lat]).split(",")[1]}" r="4" fill="#06c"/>'
    t = re.sub(r'[<>&"]', '', title)[:90]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="420" viewBox="0 0 400 420"><rect width="400" height="420" fill="#fff"/>'
            f'{body}<text x="10" y="414" font-size="11" font-family="sans-serif">{t} (held trace; blue = POTA pin)</text></svg>\n')


def small_jpeg(src, max_px=640):
    """A small copy of the tracer's own picture of the boundary over the map (debug/<ref>_1_boundary.jpg)."""
    try:
        from PIL import Image
        import io
        im = Image.open(src); im.thumbnail((max_px, max_px)); b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=60, optimize=True)
        return b.getvalue()
    except Exception:  # noqa: BLE001  (no Pillow: the tracer's picture as it is, when it is small enough)
        b = pathlib.Path(src).read_bytes()
        return b if len(b) <= 300_000 else None


# ---------------- the keeper's list ----------------
def asks_from_why_not(links, data, areas, made=None):
    """SUBSTITUTE for the keeper's list (KPC-Store gis-list/TODO.csv is private and not readable here): every park the PUBLIC key
    lists with no outline (KPC-Links data/us-key|ca-key/why-not.json). Only refs, POTA names, area codes and the ask word."""
    st = EC.Stores(data, links)
    want = {a for a in (areas or '').split(',') if a}
    parks = []
    for ref, w in sorted(st.why.items()):
        area = f"{ref.split('-')[0]}-{w.get('st') or ''}"
        if want and area not in want: continue
        pi = st.pinfo.get(ref) or []
        parks.append({'ref': ref, 'area': area, 'name': pi[0] if pi else '', 'ask': 'no official record', 'since': ''})
    return {'made': made or _dt.date.today().isoformat(), 'keeper_run': '',
            'source': 'SUBSTITUTE: the public key view (KPC-Links why-not.json), not the keeper\'s own list', 'parks': parks}


# ---------------- stored tracer results ----------------
def picture_results(d):
    d = pathlib.Path(d) if d else None
    out = {}
    if not d or not (d / 'report.csv').exists(): return out
    for row in csv.DictReader(open(d / 'report.csv', encoding='utf-8')):
        out[row['ref']] = {'row': row, 'file': d / f"{re.sub(r'[^A-Za-z0-9_-]', '_', row['ref'])}.json", 'debug': d / 'debug' / f"{row['ref']}_1_boundary.jpg"}
    return out


def parcel_results(d):
    d = pathlib.Path(d) if d else None
    out = {}
    if not d: return out
    rep = d / 'parcels' / 'report.csv'
    rows = {r['ref']: r for r in csv.DictReader(open(rep, encoding='utf-8'))} if rep.exists() else {}
    feats = {}
    for f in sorted((d / 'parcels').glob('*.json')) if (d / 'parcels').exists() else []:
        for ft in (_load(f, {}) or {}).get('features') or []:
            r = (ft.get('properties') or {}).get('ref')
            if r: feats[r] = ft
    for r, row in rows.items(): out[r] = {'row': row, 'feature': feats.get(r)}
    return out


def picture_maps_index(d):
    idx = _load(pathlib.Path(d) / 'index.json', {}) if d else {}
    rows = idx.get('maps') if isinstance(idx, dict) and 'maps' in idx else (list(idx.values()) if isinstance(idx, dict) else idx)
    out = {}
    for m in rows or []:
        if isinstance(m, dict) and m.get('ref'): out.setdefault(m['ref'], m)
    return out


# ---------------- the run ----------------
class Run:
    def __init__(self, a):
        self.a = a
        self.today = a.today or _dt.date.today().isoformat()
        self.stores = EC.Stores(a.data, a.links, a.extra, checked_default=a.checked_default or '')
        self.pic = picture_results(a.picture_traced)
        self.par = parcel_results(a.parcel_traced)
        self.pm = picture_maps_index(a.picture_maps)
        self.pin_ok = {p.get('ref') for p in (_load(a.parcel_input, []) if a.parcel_input else [])}
        self.W = HoldWriter(a.traces)
        old = _load(self.W.root / 'index.json', {}) or {}
        self.index = {r['ref']: r for r in old.get('rows') or [] if isinstance(r, dict) and r.get('ref')}
        self.finder_terms = {}   # terms the finder queued with each map address (an earlier run's queue.json), for the hand file
        for q in (_load(os.path.join(a.finder_queue, 'queue.json'), []) if a.finder_queue else []) or []:
            if isinstance(q, dict) and q.get('url') and q.get('terms'): self.finder_terms[q['url']] = q['terms']
        self.R = {'made': self.today, 'dry_run': bool(a.dry_run), 'list_source': '', 'areas': [], 'parks_asked': 0, 'parks_tried': 0,
                  'cards_made': 0, 'sorts': {}, 'chain': {k: 0 for k in ('official record lead (card)', 'stored trace held', 'stored trace not drawn',
                  'already held', 'picture map to trace', 'parcel input to trace', 'finder queued', 'finder nothing', 'finder off')},
                  'outlines_found': 0, 'outlines_held': 0, 'held_by_method': {}, 'private_not_saved': 0, 'not_held': [],
                  'requests_made': 0, 'served_from_stored_copy': 0, 'stored_files_read_for_cards': 0, 'requests_planned_dry_run': 0,
                  'refused': {}, 'pota_requests': 0, 'finder': None, 'minutes': 0, 'guard': 'ok', 'writes': 0}
        self.paths = {}

    def hold_one(self, ref, area, kind, src, card):
        """Write one held trace in the store's hand-file format. -> (held: bool, why)."""
        pin = (card.get('pota') or {}).get('pin') or [None, None]
        lat, lon = (pin + [None, None])[:2] if pin else (None, None)
        if kind == 'picture':
            row, fc = src['row'], _load(src['file'], None)
            ft = ((fc or {}).get('features') or [None])[0]
            if not ft: return False, 'tracer said DRAWN but its outline file is missing'
            pr = ft.get('properties') or {}
            m = self.pm.get(ref) or {}
            source_url = pr.get('source_url') or row.get('source_url') or m.get('source_url') or ''
            mpg = m.get('page')
            page = pr.get('page') or row.get('page') or (mpg[0] if isinstance(mpg, list) and mpg else mpg) or ''
            meth = str(pr.get('method') or '')
            method = 'geopdf' if 'placed by' in meth and 'control points' not in meth else 'picture trace'
            tracer = pr.get('tool') or 'kpc_trace_picture.py'
            terms = self.finder_terms.get(source_url) or m.get('terms') or (f"the agency's own published park map ({m.get('agency') or pr.get('agency') or 'agency'}; "
                                                                              "picture-maps row); terms not recorded by the tracer: check before release")
            acres = pr.get('area_acres') or _num(row.get('acres_traced'))
            off = _num(row.get('acres_known')) or card.get('official_acres')
            pdist = _num(row.get('pin_dist_m'))
            pic_bytes = small_jpeg(src['debug']) if src['debug'].exists() else None
            geom, fit = ft.get('geometry'), pr.get('fit_m') or row.get('fit_m')
            general = False
        else:
            row, ft = src['row'], src['feature']
            if not ft: return False, 'tracer said DRAWN but its outline is missing'
            pr = ft.get('properties') or {}
            source_url = pr.get('layer_url') or pr.get('source_url') or row.get('layer_url') or ''
            page, method, tracer = '', 'parcel trace', 'kpc_parcel_trace.py'
            terms = pr.get('terms') or f'agency parcel layer {source_url}; terms not recorded by the tracer: check before release'
            general = bool(pr.get('general_parcel_file')) or str(pr.get('source_kind') or '').lower() == 'general parcel file'
            acres, off = pr.get('acres') or _num(row.get('acres')), pr.get('known_acres') or _num(row.get('known_acres')) or card.get('official_acres')
            pdist = _num(pr.get('pin_dist_m') if pr.get('pin_dist_m') is not None else row.get('pin_dist_m'))
            pic_bytes, geom, fit = None, ft.get('geometry'), ''
        if WDPA.search(source_url) or WDPA.search(terms): return False, 'WDPA / Protected Planet is never a source'
        if general or PRIVATE_TERMS.search(terms):
            self.R['private_not_saved'] += 1
            return False, 'private input, not saved here (do-not-share source or a general parcel file)'
        inside = pin_inside(geom, lat, lon)
        props = {'ref': ref, 'name': card.get('name') or pr.get('name') or '', 'grade': GRADE, 'held': True, 'official': False,
                 'use_for_2fer': False, 'method': method, 'tracer': tracer, 'made': self.today}
        gj = jdump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': props, 'geometry': geom}]})
        if len(gj.encode()) > MAX_FILE: return False, 'outline over the 1 MB rule: not held, for a person'
        note = {'kind': 'traced', 'tracer': tracer, 'source_url': source_url, 'page': page, 'terms': terms, 'ref': ref, 'area': area,
                'method': method, 'made': self.today, 'held': True, 'official': False, 'use_for_2fer': False,
                'status': 'held for review (the owner and Fable); not in the store, not in fers-approx-outlines.json, not on the map, not a 2-fer'}
        base = f'{area}/{ref}'
        self.W.write(base + '.geojson', gj)
        self.W.write(base + '.kpc-source.json', jdump(note))
        pic = ''
        if pic_bytes: self.W.write(base + '.jpg', pic_bytes); pic = base + '.jpg'; self.W.remove(base + '.svg')
        else:
            s = svg_picture(geom, lat, lon, f'{ref} {props["name"]}')
            if s: self.W.write(base + '.svg', s); pic = base + '.svg'; self.W.remove(base + '.jpg')
        self.index[ref] = {'ref': ref, 'area': area, 'name': props['name'], 'method': method, 'source_map': source_url, 'page': page,
                           'traced_acres': _round(acres), 'official_acres': _round(off), 'pin_inside': inside,
                           'pin_dist_m': pdist, 'fit_m': _num(fit), 'picture': pic, 'geojson': base + '.geojson', 'source_note': base + '.kpc-source.json',
                           'tracer': tracer, 'card_sort': card.get('sort'), 'made': self.today, 'review': ''}
        self.R['outlines_held'] += 1
        self.R['held_by_method'][method] = self.R['held_by_method'].get(method, 0) + 1
        return True, 'held'

    def run(self, finder=None):
        t0 = time.time()
        asks = _load(self.a.asks, {}) or {}
        want = {x for x in (self.a.areas or '').split(',') if x}
        parks = [p for p in asks.get('parks') or [] if not want or p.get('area') in want]
        self.R['list_source'] = asks.get('source') or "the keeper's list (data/keeper-asks)"
        self.R['areas'] = sorted({p.get('area') for p in parks})
        self.R['parks_asked'] = len(parks)
        to_find = []
        for p in parks:
            ref, area = p['ref'], p.get('area') or ''
            card = EC.build_card(ref, self.stores, area, p.get('name') or '', p.get('since') or '', today=_dt.date.fromisoformat(self.today))
            self.R['cards_made'] += 1; self.R['parks_tried'] += 1
            self.R['sorts'][card['sort']] = self.R['sorts'].get(card['sort'], 0) + 1
            path = ['card']
            if card['sort'] in ('PROPOSE JOIN', 'EASY FIX'):
                self.R['chain']['official record lead (card)'] += 1; path.append('official record lead'); self.paths[ref] = path; continue
            pr, pa = self.pic.get(ref), self.par.get(ref)
            drawn = [(k, s) for k, s in (('picture', pr), ('parcel', pa)) if s and str(s['row'].get('status') or '').upper() == 'DRAWN']
            if drawn:
                self.R['outlines_found'] += 1
                self.R['served_from_stored_copy'] += 1
                path.append('stored trace')
                ok, why = self.hold_one(ref, area, drawn[0][0], drawn[0][1], card)
                if ok: self.R['chain']['stored trace held'] += 1; path.append('held')
                else: self.R['not_held'].append({'ref': ref, 'why': why}); path.append('not held')
                self.paths[ref] = path; continue
            if pr or pa:
                self.R['chain']['stored trace not drawn'] += 1
                self.R['served_from_stored_copy'] += 1
                path.append('stored trace (not drawn: ' + ', '.join(f"{k} {s['row'].get('status')}" for k, s in (('picture', pr), ('parcel', pa)) if s) + ')')
            if ref in self.index:
                self.R['chain']['already held'] += 1; path.append('already held'); self.paths[ref] = path; continue
            if ref in self.pm and not pr:
                self.R['chain']['picture map to trace'] += 1; self.R['served_from_stored_copy'] += 1; path.append('picture map to trace'); self.paths[ref] = path; continue
            if ref in self.pin_ok and not pa:
                self.R['chain']['parcel input to trace'] += 1; path.append('parcel input to trace'); self.paths[ref] = path; continue
            path.append('finder'); self.paths[ref] = path
            to_find.append({'ref': ref, 'name': card['name'], 'area': area, 'website': (card.get('pota') or {}).get('website') or '',
                            'agency': (card.get('official_page') or {}).get('agency') or ''})
        if finder is None:
            self.R['chain']['finder off'] += len(to_find)
        else:
            for q in to_find:
                row = finder.find(q)
                k = 'finder queued' if row.get('queued') else 'finder nothing'
                self.R['chain'][k] += 1; self.paths[q['ref']].append(k.split(' ', 1)[1])
            fr = finder.receipt()
            self.R['finder'] = fr
            self.R['requests_made'] += fr['requests_made']; self.R['served_from_stored_copy'] += fr['served_from_stored_copy']
            self.R['requests_planned_dry_run'] += fr['planned_dry_run']; self.R['pota_requests'] += fr['pota_requests']
            self.R['refused'] = {k: v for k, v in fr['refused'].items() if v}
            for qq in finder.queue: self.finder_terms[qq['url']] = qq['terms']
        self.R['stored_files_read_for_cards'] = self.stores.reads
        rows = sorted(self.index.values(), key=lambda r: (r.get('area') or '', r['ref']))
        self.W.write('index.json', jdump({'about': 'Held traces (KPC owner, 2026-11-17; Handoff 3): approximate, held for review by the owner and Fable. '
                                                   'Never in the store, never in fers-approx-outlines.json, never on the map, never a 2-fer. Deleted when the park gets an official outline.',
                                          'updated': self.today, 'count': len(rows), 'rows': rows}))
        self.R['minutes'] = round((time.time() - t0) / 60, 2)
        self.R['writes'] = len(self.W.written)
        return self.R


def _num(v):
    try: return float(v) if v not in (None, '') else None
    except (TypeError, ValueError): return None


def _round(v):
    v = _num(v)
    return round(v, 1) if v is not None else None


def prune(traces, links):
    """Delete every held trace whose park now has an OFFICIAL outline in KPC-Links data/us-key or data/ca-key (g == 'official')."""
    W = HoldWriter(traces); L = pathlib.Path(links); off = set()
    for f in list((L / 'data/us-key').glob('US-*.json')) + list((L / 'data/ca-key').glob('CA-*.json')):
        off |= {r for r, v in ((_load(f, {}) or {}).get('parks') or {}).items() if isinstance(v, dict) and v.get('g') == 'official'}
    if not off: print('::notice title=Trace hold::no key read: nothing deleted'); return []
    idx = _load(W.root / 'index.json', {}) or {}
    gone = [r for r in idx.get('rows') or [] if r.get('ref') in off]
    for r in gone:
        for ext in ('.geojson', '.kpc-source.json', '.jpg', '.svg'): W.remove(f"{r['area']}/{r['ref']}{ext}")
    if gone:
        idx['rows'] = [r for r in idx['rows'] if r.get('ref') not in off]; idx['count'] = len(idx['rows'])
        W.write('index.json', jdump(idx))
    print(f"::notice title=Trace hold::prune: {len(gone)} held trace(s) deleted (park now has an official outline)")
    return [r['ref'] for r in gone]


def limit_index(asks, base):
    keep = {p['ref'] for p in (_load(asks, {}) or {}).get('parks') or []}
    b = pathlib.Path(base)
    idx = _load(b / 'index.json', {}) or {}
    pins = _load(b / 'pins.json', {}) or {}
    idx = {r: v for r, v in idx.items() if r in keep} if isinstance(idx, dict) else [v for v in idx if v.get('ref') in keep]
    json.dump(idx, open(b / 'index.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump({r: v for r, v in pins.items() if r in keep}, open(b / 'pins.json', 'w'), indent=0)
    print(f'::notice title=Trace hold::picture tracer limited to {len(idx)} listed park(s)')


def limit_parks(asks, parks):
    keep = {p['ref'] for p in (_load(asks, {}) or {}).get('parks') or []}
    rows = [r for r in _load(parks, []) or [] if r.get('ref') in keep]
    json.dump(rows, open(parks, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    print(f'::notice title=Trace hold::parcel tracer limited to {len(rows)} listed park(s)')


def make_finder(a):
    import kpc_pdf_finder as PF
    S = PF.load_settings(a.settings); B = PF.load_blocked_hosts(a.blocked); D = PF.load_disallowed_layers(a.disallowed)
    pmi = picture_maps_index(a.picture_maps)
    return PF.Finder(S, B, D, PF.SavedCopies(a.saved), dry_run=a.dry_run, park_max=a.park_max, picture_maps=pmi,
                     docs_dir=os.path.join(a.data, 'data/docs') if a.data else None, today=a.today)


def _selftest():
    import tempfile
    ok = True
    def chk(c, w):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + w)
    with tempfile.TemporaryDirectory() as td:
        W = HoldWriter(pathlib.Path(td) / 'traces')
        for bad in ('data/fers-approx-outlines.json', '../x.geojson', 'data/us-key/US-KY.json', 'index.html', 'store-data/a.json'):
            try: W.write(bad, '{}'); chk(False, f'guard refuses {bad}')
            except HoldRefused: chk(True, f'guard refuses {bad}')
        links = pathlib.Path(td) / 'links'; (links / 'data').mkdir(parents=True); (links / 'data/fers-approx-outlines.json').write_text('{}')
        try: HoldWriter(links / 'held'); chk(False, 'guard refuses a traces root inside KPC-Links')
        except HoldRefused: chk(True, 'guard refuses a traces root inside KPC-Links')
    sq = {'type': 'Polygon', 'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
    chk(pin_inside(sq, 0.5, 0.5) is True and pin_inside(sq, 2, 2) is False, 'pin inside / outside')
    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['asks-from-why-not', 'limit-index', 'limit-parks', 'run', 'prune'])
    for k in ('asks', 'areas', 'data', 'links', 'extra', 'picture-maps', 'picture-traced', 'parcel-traced', 'parcel-input', 'traces', 'receipt',
              'out', 'pic-base', 'parks', 'today', 'checked-default', 'finder-queue', 'settings', 'blocked', 'disallowed', 'saved'):
        ap.add_argument('--' + k, default=None)
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--finder', default='no'); ap.add_argument('--park-max', type=int, default=6)
    a = ap.parse_args(argv)
    if a.cmd == 'asks-from-why-not':
        o = asks_from_why_not(a.links, a.data, a.areas, a.today)
        open(a.out, 'w', encoding='utf-8', newline='\n').write(jdump(o)); print(f"{len(o['parks'])} parks (SUBSTITUTE list) -> {a.out}"); return 0
    if a.cmd == 'limit-index': limit_index(a.asks, a.pic_base); return 0
    if a.cmd == 'limit-parks': limit_parks(a.asks, a.parks); return 0
    if a.cmd == 'prune': prune(a.traces, a.links); return 0
    try:
        F = make_finder(a) if a.finder == 'yes' else None
        R = Run(a)
        rec = R.run(F)
        if F is not None and a.finder_queue: F.write(a.finder_queue)
    except HoldRefused as e:
        print(f'::error title=Trace hold::guard stopped the run: {e}'); return 1
    except Exception as e:  # noqa: BLE001
        print(f'::error title=Trace hold::{type(e).__name__}: {e}'); return 1
    txt = jdump(rec)
    if a.receipt:
        pathlib.Path(a.receipt).parent.mkdir(parents=True, exist_ok=True)
        open(a.receipt, 'w', encoding='utf-8', newline='\n').write(txt)
    print(f"::notice title=Trace hold::{rec['parks_tried']} parks tried, {rec['cards_made']} cards, {rec['outlines_held']} traces held, "
          f"{rec['requests_made']} requests, {rec['served_from_stored_copy']} from stored copies, POTA requests {rec['pota_requests']}"
          f"{' (dry run)' if rec['dry_run'] else ''}")
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]: sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
