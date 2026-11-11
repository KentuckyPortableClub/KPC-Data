#!/usr/bin/env python3
"""WDPA PHONE BOOK (chat 10, Nov 1 2026; Brandon 7:30 PM: 'we just need to use them as a phone book ... yes use it like that').
WDPA (Protected Planet) as a DIRECTORY, not a map: for every park that still has no OFFICIAL outline, look up which protected area
is at the POTA pin (within about 150 m) and WHO runs it: managing authority, local-language name, designation, the data provider's
metadata id. Those are LEADS for a person (which agency's own portal to search first). No WDPA shape or coordinate is ever stored
or passed on; only the lookup facts below.

Nov 11 2026 (host rules; owner's review package A): SAVED COPY ONLY. WDPA lives on a services*.arcgis.com host, which no bot ever
contacts (no request of any kind, robots.txt included; kpc_host_rules.py). This script makes NO network request at all:
  * KPC_WDPA_SAVED  the saved WDPA copy a person downloaded (GeoJSON FeatureCollection, polygons and / or points, WGS84). It must
                    sit OUTSIDE the repo (private). Default ~/kpc-private/wdpa-saved.geojson.
  * KPC_WDPA_OUT    the phone book (JSON; a .md summary beside it). It must sit OUTSIDE the repo too: the same private-file rule as
                    KPC-Links kpc_master.private_path_ok (the master CLI's 'wdpa-lookup', "private output only, no geometry"), because
                    KPC-Data main is published whole to Pages (kpc-pages-sync.yml moves the site branch to main). Default
                    ~/kpc-private/wdpa-phonebook.json. Rows keep only the fields of kpc_master.wdpa_agency_lookup.
  No saved copy (the normal case on a GitHub runner): a visible '::warning' + the status board line 'needs the saved WDPA copy',
  zero requests, exit 0, LEFT=0. ONE job with a time budget (MINUTES, 45): it never starts another run.
  {ref: {d: date, h: [{id, name, orig, desig, auth, gov, meta, iso3}]}}   (newest look per park; a park is looked again after 90 days)
  python3 .github/scripts/kpc_wdpa_phonebook.py                env LINKS (KPC-Links checkout, for the keys), KPC_WDPA_SAVED, KPC_WDPA_OUT"""
import collections, datetime as dt, glob, json, math, os, pathlib, sys, time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
PRIVATE = pathlib.Path(os.path.expanduser('~')) / 'kpc-private'
SAVED = pathlib.Path(os.environ.get('KPC_WDPA_SAVED') or PRIVATE / 'wdpa-saved.geojson')
OUT = pathlib.Path(os.environ.get('KPC_WDPA_OUT') or PRIVATE / 'wdpa-phonebook.json')
MD = OUT.with_suffix('.md')
LIMIT = float(os.environ.get('MINUTES') or 45) * 60; T0 = time.time(); TODAY = dt.date.today()
BOT = 'WDPA phone book'
# the attribute fields kept (the same set as KPC-Links kpc_master.wdpa_agency_lookup keeps); nothing else, never geometry
WANT = {'id': ('wdpaid', 'wdpa_pid'), 'name': ('name',), 'orig': ('orig_name',), 'desig': ('desig_eng', 'desig'), 'auth': ('mang_auth',),
        'gov': ('gov_type',), 'meta': ('metadataid',), 'iso3': ('iso3',)}
NEAR = 0.00135   # about 150 m each way (R-G12)


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def private_path_ok(path, roots=None):
    """(ok, why): the path must be OUTSIDE this repo (and outside the KPC-Links checkout). KPC-Links kpc_master.private_path_ok rule."""
    p = pathlib.Path(path).expanduser().resolve()
    for r in roots if roots is not None else (REPO, LINKS):
        try: rel = p.relative_to(pathlib.Path(r).resolve())
        except ValueError: continue
        return False, f'{rel} is inside {r}: the WDPA phone book is private, so it is written outside the repo (e.g. ~/kpc-private/)'
    return True, ''


def official():
    s = set()
    for f in glob.glob('data/*-key/*.json') + glob.glob(str(LINKS / 'data' / '*-key' / '*.json')):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(v, dict) and v.get('g') == 'official': s.add(r)
    return s


def parks():
    P = {}
    for f in glob.glob('data/pota/t/*.json'):
        for row in load(f, []) or []:
            if isinstance(row, list) and len(row) >= 4 and row[2] is not None and (row[2], row[3]) != (0, 0): P[row[0]] = (row[2], row[3], row[1])
    return P


def rank(ref):
    try:
        import kpc_order as O
        cc = ref.split('-')[0]
        return (0 if ref.startswith('US-') else 1, O.rank('W-' + cc) if cc not in ('US', 'CA') else 0, ref)
    except Exception: return (9, 0, ref)  # noqa: BLE001


# ---------------------------------------------------------------- the saved copy: shapes are read in memory, never written
def _rings(g):
    t, c = (g or {}).get('type'), (g or {}).get('coordinates') or []
    if t == 'Polygon': return [c]
    if t == 'MultiPolygon': return list(c)
    return []


def _points(g):
    t, c = (g or {}).get('type'), (g or {}).get('coordinates') or []
    if t == 'Point': return [c]
    if t == 'MultiPoint': return list(c)
    return []


def _in_ring(x, y, r):
    c = False
    for i in range(len(r)):
        (x1, y1), (x2, y2) = r[i][:2], r[i - 1][:2]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-15) + x1: c = not c
    return c


def facts(props):
    low = {str(k).lower(): v for k, v in (props or {}).items()}
    out = {}
    for k, cands in WANT.items():
        v = next((low[c] for c in cands if low.get(c) not in (None, '', 'Not Reported')), None)
        if v is not None: out[k] = v
    return out


class Saved:
    """The saved WDPA copy, indexed by 1-degree cell. hits(lat, lon) -> up to 3 fact rows (no geometry)."""
    def __init__(self, doc):
        self.cell = collections.defaultdict(list); self.n = 0
        for f in (doc or {}).get('features') or []:
            g = f.get('geometry') or {}
            polys, pts = _rings(g), _points(g)
            xs = [p[0] for poly in polys for p in (poly[0] if poly else [])] + [p[0] for p in pts]
            ys = [p[1] for poly in polys for p in (poly[0] if poly else [])] + [p[1] for p in pts]
            if not xs: continue
            rec = (min(xs), min(ys), max(xs), max(ys), polys, pts, facts(f.get('properties')))
            self.n += 1
            for i in range(int(math.floor(rec[0])), int(math.floor(rec[2])) + 1):
                for j in range(int(math.floor(rec[1])), int(math.floor(rec[3])) + 1): self.cell[(i, j)].append(rec)

    def hits(self, la, lo):
        dx, dy = NEAR / max(0.2, math.cos(math.radians(la))), NEAR
        out, seen = [], set()
        for rec in self.cell.get((int(math.floor(lo)), int(math.floor(la))), []):
            x0, y0, x1, y1, polys, pts, fa = rec
            if id(rec) in seen or x1 < lo - dx or x0 > lo + dx or y1 < la - dy or y0 > la + dy: continue
            seen.add(id(rec))
            inside = any(poly and _in_ring(lo, la, poly[0]) and not any(_in_ring(lo, la, h) for h in poly[1:]) for poly in polys)
            near = any(abs(p[0] - lo) <= dx and abs(p[1] - la) <= dy for p in pts) or \
                any(abs(p[0] - lo) <= dx and abs(p[1] - la) <= dy for poly in polys for r in poly for p in r)
            if inside or near: out.append(fa)
            if len(out) >= 3: break
        return out


def note(why):
    """A visible note: a warning in the log, a line in the step summary and the status board. Nothing else is written."""
    print(f'::warning title={BOT}::{why}', flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        try: open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write(f'**{BOT}:** {why}\n')
        except Exception: pass  # noqa: BLE001
    try:
        sys.path.insert(0, str(HERE)); import kpc_status
        kpc_status.board(BOT, 'amber', why[:300], 'a person: put the saved WDPA copy at KPC_WDPA_SAVED (outside the repo) and run it on that machine')
    except Exception as e: print(f'status board not written: {str(e)[:120]}')  # noqa: BLE001


def main():
    for what, p in (('saved WDPA copy (KPC_WDPA_SAVED)', SAVED), ('phone book (KPC_WDPA_OUT)', OUT)):
        ok, why = private_path_ok(p)
        if not ok: note(f'{what}: {why}. Nothing looked up, nothing written.'); print('LEFT=0'); return 0
    if not SAVED.is_file():
        note(f'needs the saved WDPA copy: no file at KPC_WDPA_SAVED ({SAVED}). WDPA is never read live (services*.arcgis.com: no request '
             'of any kind, robots.txt included). Nothing looked up; the last phone book (if any) is kept as it is.')
        print('LEFT=0'); return 0
    doc = load(SAVED, None)
    S = Saved(doc)
    if not S.n:
        note(f'the saved WDPA copy at {SAVED} holds no readable shapes (a GeoJSON FeatureCollection is expected). Nothing looked up.')
        print('LEFT=0'); return 0
    saved_date = dt.date.fromtimestamp(SAVED.stat().st_mtime).isoformat()
    B = load(OUT, {}) or {}
    off, P = official(), parks()
    todo = sorted((r for r in P if r not in off and not (B.get(r) and (TODAY - dt.date.fromisoformat(B[r]['d'])).days < 90)), key=rank)
    n = hits = 0
    for ref in todo:
        if time.time() - T0 > LIMIT: break
        la, lo, _ = P[ref]
        h = S.hits(la, lo)
        B[ref] = {'d': TODAY.isoformat(), 'h': h, 'copy': saved_date}; n += 1; hits += bool(h)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(B, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    by = collections.defaultdict(collections.Counter)
    for r, v in B.items():
        if r in off: continue
        for x in (v.get('h') or [])[:1]:
            if x.get('auth'): by[r.split('-')[0]][x['auth']] += 1
    L = ['# WDPA phone book: who runs the parks we still miss (PRIVATE: never commit or publish)',
         f'Built {TODAY} by kpc_wdpa_phonebook.py from the saved WDPA copy of {saved_date} (directory facts only; no WDPA shapes kept).', '']
    for cc in sorted(by, key=lambda c: -sum(by[c].values())):
        L.append(f"- **{cc}** ({sum(by[cc].values())} parks): " + '; '.join(f'{a} ({c})' for a, c in by[cc].most_common(5)))
    MD.write_text('\n'.join(L) + '\n', encoding='utf-8')
    left = len(todo) - n
    print(f'::notice title={BOT}::{n} parks looked up in the saved copy of {saved_date} ({hits} inside a WDPA area), {left} left; '
          f'{len(B)} in the book (private file, outside the repo); no request made', flush=True)
    print(f'LEFT={left}')
    return 0


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::warning title={BOT}::stopped ({type(e).__name__}: {e}); nothing published')  # noqa: BLE001
    sys.exit(0)
