#!/usr/bin/env python3
"""HARD LOOK READER (chat 10, Nov 1 2026; Brandon 12:20 AM: the Canada Hard Look results). AUTOMATION FIRST: reads every
hardlook-*.json the intake reader copied from branch intake-files (rows: ref -> status GIS FOUND / NAME SOLVED / PARCEL / ...,
url, name field, the record id / name for THIS park, notes), asks each layer for THAT record (ArcGIS REST only), measures the POTA pin
against it, and writes one question per park for chat 11 in data/waiting/questions/hardlook.json. Decides nothing:
  GIS FOUND / NAME SOLVED -> candidate outline (grade from its source; chat 11 YES -> chat 2 joins it in the Canada key)
  PARCEL                  -> candidate APPROXIMATE (agency parcels) outline, never a 2-fer
  rules: R-G12 (record edge within 150 m of the pin = candidate 'pin N m outside'), R-G13 (PIN OFF in the notes + name/kind/size
  match = outline usable, POTA pin never moves: also listed in data/waiting/questions/pin-typos.json).
Answers already given are kept. Resumable (rows done are skipped). MINUTES (40). Never fails."""
import glob, json, math, os, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kpc_manners import Manners  # noqa: E402
from kpc_json_any import load_json_any, save_json_gz  # noqa: E402

M = Manners('KPC hard look reader (chat 10)')
QF = pathlib.Path('data/waiting/questions/hardlook.json'); PT = pathlib.Path('data/waiting/questions/pin-typos.json')
LIMIT = float(os.environ.get('MINUTES') or 40) * 60; T0 = time.time(); TODAY = time.strftime('%Y-%m-%d')
LAY = re.compile(r'^(https?://\S+?/(?:MapServer|FeatureServer))/(\d+)', re.I)
IDS = re.compile(r'\b(OBJECTID(?:_1)?|objectid|FID|OGF_ID|fid)\b\s*[#:=]?\s*((?:\d+\s*(?:\+|,|and|&)?\s*)+)')


def note(m): print('::notice title=Hard look reader::' + str(m)[:900], flush=True)


def load(p, d):
    try: return load_json_any(p)
    except Exception: return d  # noqa: BLE001


def get_json(u, params):
    try:
        st, hd, body, final = M.get(u + '?' + urllib.parse.urlencode(params), accept='application/json', timeout=60)
        if st in ('deferred', 'crawl-delay', 'rest', 'robots-unreadable'): return None, f'next run ({st})'   # A13: robots.txt not readable = next run   # Nov 3 (A4): not a failed try
        if not (isinstance(st, int) and st < 400 and body): return None, f'HTTP {st}'
        j = json.loads(body.decode('utf-8', 'replace'))
        return (None, f"error {j['error'].get('code')}: {str(j['error'].get('message'))[:80]}") if isinstance(j, dict) and j.get('error') else (j, '')
    except Exception as e: return None, f'{type(e).__name__}'  # noqa: BLE001


def where_of(rec, field):
    m = IDS.search(rec or '')
    if m:
        ids = re.findall(r'\d+', m.group(2))
        if ids: return f"{m.group(1)} IN ({','.join(ids[:20])})"
    nf = re.split(r'[\s/,;(]', (field or '').strip())[0] if field else ''
    fv = FV.search(rec or '')   # Nov 2 (chat 12): record_given = "Nom='Mont-Royal'" / "NOM='Ile-Charron, Parc de l''" / NAME="x"
    if fv:
        f_, val = fv.group(1), (fv.group(2) if fv.group(2) is not None else fv.group(3)).replace("''", "'")
        if not re.search(r'^(OBJECTID|FID|ID)$', f_, re.I): nf = f_
    else:
        q = re.search(r'"([^"]{3,120})"', rec or '')
        val = q.group(1) if q else None
        bare = re.sub(r'\s*\(.*?\)\s*', ' ', str(rec or '')).strip()
        if not val and nf and 3 <= len(bare) <= 100 and '=' not in bare and re.search(r'[A-Za-z]{3}', bare) and not re.search(r'https?:|\bOBJECTID\b', bare, re.I): val = bare   # a bare record name
    if val and nf and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', nf):
        return f"UPPER({nf}) = '{val.upper().replace(chr(39), chr(39) * 2)}'"   # Nov 2 (chat 12, AU 'TANJA Flora Reserve'): case-insensitive
    return None


FV = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{1,30})\s*=\s*(?:'((?:[^']|'')+)'|\"([^\"]+)\")")


def query(base, w):
    """Ask the layer; on a 400 'invalid query parameters' (Coillte, IE) ask again with only the plain parameters, and when
    UPPER() is refused, with plain equality. -> (json, error)."""
    full = {'where': w, 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': 0.00005, 'resultRecordCount': 20, 'f': 'json'}
    j, err = get_json(base, full)
    if j is None and re.search(r'400|Invalid', err):
        j, err = get_json(base, {'where': w, 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'f': 'json'})
    if j is None and re.search(r'400|Invalid', err) and w.startswith('UPPER('):
        m = re.match(r"UPPER\((\w+)\) = '(.*)'$", w)
        if m: j, err = get_json(base, {'where': f"{m.group(1)} = '{m.group(2)}'", 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326, 'f': 'json'})
    return j, err


def name_words_query(base, nf, name):
    """The record name in the layer can be shorter than the park's (AU 'TANJA' for 'Tanja Flora Reserve'): search the longest
    proper word, LIKE, case-insensitive."""
    import kpc_tiers as T
    words = sorted(T.proper(name or ''), key=len, reverse=True)
    if not (nf and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', nf) and words and len(words[0]) >= 4): return None, ''
    return query(base, f"UPPER({nf}) LIKE '%{words[0].upper().replace(chr(39), chr(39) * 2)}%'")


def dist_m(lat, lon, geom):
    """0 when the pin is inside a polygon ring (even-odd), else the distance to the nearest vertex / segment (m, local flat)."""
    kx = 111320 * math.cos(math.radians(lat)); ky = 110540
    rings = geom.get('rings') or geom.get('paths') or []
    inside = False; best = float('inf')
    for ring in rings:
        pts = [((x - lon) * kx, (y - lat) * ky) for x, y, *_ in ring]
        if geom.get('rings'):
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i - 1], pts[i]
                if (y1 > 0) != (y2 > 0) and x1 + (0 - y1) * (x2 - x1) / (y2 - y1) > 0: inside = not inside
        for i in range(1, len(pts)):
            (x1, y1), (x2, y2) = pts[i - 1], pts[i]
            dx, dy = x2 - x1, y2 - y1; t = max(0, min(1, -(x1 * dx + y1 * dy) / ((dx * dx + dy * dy) or 1e-12)))
            best = min(best, math.hypot(x1 + t * dx, y1 + t * dy))
    return 0 if inside else (round(best) if best < float('inf') else None)


def acres(geom, lat):
    kx = 111320 * math.cos(math.radians(lat)); a = 0
    for ring in geom.get('rings') or []:
        a += sum(ring[i - 1][0] * kx * ring[i][1] * 110540 - ring[i][0] * kx * ring[i - 1][1] * 110540 for i in range(len(ring))) / 2
    return round(abs(a) / 4046.86, 1)


def pins():
    """POTA pins: data/parkinfo/US-*.json + CA.json + world files, the data/pota/t tiles, Kentucky from KPC-Links kpc-ky-data.json."""
    out = {}
    for f in glob.glob('data/parkinfo/*.json'):
        for r, a in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(a, list) and len(a) > 6: out[r] = (a[5], a[6])
    for f in glob.glob('data/pota/t/*.json'):
        for x in load(f, []) or []:
            if isinstance(x, list) and len(x) > 3: out.setdefault(x[0], (x[2], x[3]))
    for p in (load(os.path.join(os.environ.get('LINKS') or '../links', 'kpc-ky-data.json'), {}) or {}).get('parks') or []:
        try: out[p['c']] = (float(p['la']), float(p['lo']))
        except Exception: pass  # noqa: BLE001
    return out


NAMEK = re.compile(r'name|nom|title|remarks|bez|gebiet|objekt|denom|naam|nimi|navn|label|site', re.I)
REASK = re.compile(r'^(no record id / name|record not found|layer did not answer \(error 400)')


def reask(rows, R):
    """Chat 11 (Nov 1 3 PM): rows left OPEN because no record came back ('no record id / name', 'record not found', a 400 query
    error) are asked AGAIN, once, by place and name: (1) what the layer holds at the POTA pin (within 150 m, R-G12); (2) if nothing
    there and the name field is known, a name search on the park's longest proper word. The record whose name matches the park best
    (name tiers) is written back on the row; chat 11 still answers. Answered rows are never touched."""
    import kpc_tiers as T
    n = {'asked': 0, 'found': 0, 'none': 0}
    for ref, q in sorted(R.items()):
        if time.time() - T0 > LIMIT: break
        if str(q.get('answer') or '').strip() or q.get('reasked') or not REASK.match(str(q.get('result') or '')): continue
        v = rows.get(ref) or {}
        m = LAY.match(str(q.get('url') or v.get('url') or '').strip())
        try: lat, lon = float(v.get('lat') or 0), float(v.get('lon') or 0)
        except (TypeError, ValueError): lat = lon = 0
        q['reasked'] = TODAY
        if not m or not (lat or lon): q['reask_result'] = 'not asked again: no layer address or no pin'; continue
        base = f'{m.group(1)}/{m.group(2)}/query'; n['asked'] += 1
        j, err = get_json(base, {'geometry': f'{lon},{lat}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                 'distance': 150, 'units': 'esriSRUnit_Meter', 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326,
                                 'maxAllowableOffset': 0.00005, 'resultRecordCount': 20, 'f': 'json'})
        F, how = (j or {}).get('features') or [], 'what the layer holds within 150 m of the POTA pin'
        nf = re.split(r'[\s/,;(]', str(q.get('name_field') or v.get('field') or '').strip())[0]
        words = sorted(T.proper(q.get('name') or ''), key=len, reverse=True)
        if not F and nf and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', nf) and words and len(words[0]) >= 4:
            j, err = get_json(base, {'where': f"UPPER({nf}) LIKE '%{words[0].upper()}%'", 'outFields': '*', 'returnGeometry': 'true', 'outSR': 4326,
                                     'maxAllowableOffset': 0.00005, 'resultRecordCount': 20, 'f': 'json'})
            F, how = (j or {}).get('features') or [], f"a name search: {nf} contains '{words[0]}'"
        best = None
        for f in F:
            at = f.get('attributes') or {}
            rn = str(at.get(nf) or next((x for k_, x in at.items() if x and re.search(r'name|nom|title', k_, re.I)), '') or '')
            tr, why = T.tier(q.get('name') or '', rn, None, None, 1)
            d = dist_m(lat, lon, f.get('geometry') or {})
            c = (('SURE', 'LIKELY', 'UNLIKELY').index(tr), d if d is not None else 9e9, tr, why, rn, f, at)
            if best is None or c[:2] < best[:2]: best = c
        if not best or best[2] == 'UNLIKELY':
            q['reask_result'] = f"asked again ({how}): {'no record there' if not F else 'records there, none with this park name'}" + (f' [{err}]' if err and not F else ''); n['none'] += 1; continue
        _, d, tr, why, rn, f, at = best
        oid = next((at[k_] for k_ in ('OBJECTID', 'objectid', 'FID', 'OBJECTID_1') if k_ in at), None)
        q.update(reask_result=f'record found when asked again ({how})', reask_record=f'OBJECTID {oid}: {rn}'[:200], reask_tier=tr, reask_why=why[:120],
                 pin_m=d, acres=round(acres(f.get('geometry') or {}, lat), 1) or None,
                 rule=('pin inside' if d == 0 else f'R-G12 candidate: pin {d} m outside (road / entrance)' if d is not None and d <= 150 else f'pin {d} m from the record'))
        n['found'] += 1
    return n


def keep_old(old, q):
    """Nov 2 bot fixes (Quality 4a): a row written again keeps what a person or a chat wrote on it: a non-empty answer /
    checked_by / how, and every key the reader itself does not write (notes, decisions ...)."""
    old = old or {}
    out = {**{k: v for k, v in old.items() if k not in q}, **q}
    for k in ANSWER_KEYS:
        if str(old.get(k) or '').strip() and not str(q.get(k) or '').strip() and not q.get('reread'): out[k] = old[k]
    return out


def merge_rows(mine, theirs):
    """rows {ref: row}: carry the answers and extra keys of `theirs` (main, written by the chats while this job ran) into `mine`.
    A row only on main is added. Their non-empty answer / checked_by / how wins (a person's answer beats the reader)."""
    n = 0
    for ref, t in (theirs or {}).items():
        if not isinstance(t, dict): continue
        m = mine.get(ref)
        if m is None: mine[ref] = t; n += 1; continue
        ch = False
        for k, v in t.items():
            if k in ANSWER_KEYS:
                if str(v or '').strip() and v != m.get(k): m[k] = v; ch = True
            elif k not in m: m[k] = v; ch = True
        n += ch
    return n


def _show_main(path):
    """JSON on origin/main at path or path.gz (gz preferred). None when the path is not there."""
    import gzip, subprocess
    for p in (f'{path}.gz', str(path)):
        r = subprocess.run(['git', 'show', f'origin/main:{p}'], capture_output=True)
        if r.returncode != 0: continue
        data = r.stdout
        if p.endswith('.gz'):
            try: data = gzip.decompress(data)
            except OSError: continue
        try: return json.loads(data.decode('utf-8'))
        except (UnicodeError, ValueError): continue
    return None


def merge_main():
    """kpc_hardlook.py merge-main: just before the save, read hardlook.json and pin-typos.json as they are on origin/main NOW and
    carry their answers into this job's copy (the save used to overwrite the whole file: answers written meanwhile were lost)."""
    import subprocess
    if subprocess.run(['git', 'fetch', '-q', 'origin', 'main'], capture_output=True).returncode != 0:
        note('merge-main: could not fetch main: the save may overwrite newer answers'); return 1
    tot = 0
    for f in (QF, PT):
        theirs = _show_main(f.as_posix())
        if theirs is None: continue   # not on main yet, or not JSON
        mine = load(f, None)
        if not isinstance(mine, dict): mine = theirs
        else: tot += merge_rows(mine.setdefault('rows', {}), (theirs or {}).get('rows') or {})
        save_json_gz(f, mine, indent=1, ensure_ascii=False)
    note(f'merge-main: {tot} row(s) took answers or rows from main before the save')
    return 0



ANSWER_KEYS = ('answer', 'checked_by', 'how')


def redo(q):
    """A row to read again once (Nov 2, chat 12's list): tagged REREAD, or a reader gap (no id / name parsed, record not found,
    a 400 answer, names not read) that nobody answered.
    Nov 2 bot fixes (Quality 4a): ANY answer stops a re-read (it only spared YES / NO, so NO PIN, PIN and NOT SURE answers
    were erased and the row asked again)."""
    if q.get('reread'): return False
    if any(str(q.get(k) or '').strip() for k in ANSWER_KEYS): return False
    if 'REREAD' in str(q.get('why') or ''): return True
    r = str(q.get('result') or '')
    return bool(REASK.match(r)) or (r == 'record found' and not q.get('names'))


def main():
    rows = {}
    for f in sorted(glob.glob('data/intake/_in/hardlook/hardlook-*.json')):
        for ref, v in ((load(f, {}) or {}).get('rows') or {}).items(): rows[ref] = dict(v, _file=pathlib.Path(f).name)
    if not rows: note('no hard look files'); return
    PINS = pins()   # Nov 1: bundle rows carry no pin: take POTA's own pin from our files
    for ref, v in rows.items():
        try: ok = float(v.get('lat')) and float(v.get('lon'))
        except Exception: ok = False  # noqa: BLE001
        if not ok and ref in PINS: v['lat'], v['lon'] = PINS[ref]
    Q = load(QF, {'about': 'Canada Hard Look rows (outside research) read back from the layer by chat 10\'s reader: one question per park for chat 11 (answer YES / NO / NOT SURE). GIS = candidate outline, PARCEL = candidate APPROXIMATE (agency parcels). R-G12 / R-G13 noted per row.', 'rows': {}}) or {}
    R = Q.setdefault('rows', {}); P = load(PT, {'about': 'R-G13: POTA pins that official sources show are typos (POTA pin never moved; Brandon reports to POTA if he wants).', 'rows': {}}) or {}
    n = {'asked': 0, 'record found': 0, 'record not found': 0, 'layer did not answer': 0, 'no record id / name': 0, 'skipped (status)': 0, 'next run (slow host)': 0}
    for ref in sorted(rows, key=lambda r: (rows[r].get('st') or '', r)):
        v = rows[ref]
        if time.time() - T0 > LIMIT: break
        if ref in R and R[ref].get('read') and not redo(R[ref]): continue
        if v.get('status') not in ('GIS FOUND', 'NAME SOLVED', 'PARCEL'): n['skipped (status)'] += 1; continue
        m = LAY.match(str(v.get('url') or '').strip())
        w = where_of(v.get('record'), v.get('field'))
        q = {'ref': ref, 'st': f"{ref[:2]}-{v.get('st')}" if ref[:3] in ('US-', 'CA-') else ref[:2], 'name': v.get('name'), 'status_given': v.get('status'), 'grade': 'approximate (agency parcels)' if v.get('status') == 'PARCEL' else 'outline (grade as its source)',
             'url': v.get('url'), 'name_field': v.get('field'), 'record_given': str(v.get('record'))[:300], 'agency': v.get('agency'), 'notes': str(v.get('notes'))[:600], 'from': v.get('_file'),
             'answer': (R.get(ref) or {}).get('answer', ''), 'checked_by': (R.get(ref) or {}).get('checked_by', '')}
        if ref in R and redo(R[ref]):   # Nov 2 (chat 12): a reader gap is read again ONCE; its old grade is kept as first_answer and the row is asked again
            q.update(reread=TODAY, first_answer=R[ref].get('answer'), first_result=R[ref].get('result'), answer='', checked_by='')
        if not m or not w:
            q.update(read=TODAY, result='no record id / name the reader can ask (chat 11 reads the notes)'); n['no record id / name'] += 1; R[ref] = keep_old(R.get(ref), q); continue
        n['asked'] += 1
        base = f'{m.group(1)}/{m.group(2)}/query'
        j, err = query(base, w)
        if j is not None and not (j.get('features') or []) and not w.startswith('OBJECTID'):
            j2, err2 = name_words_query(base, re.split(r'[\s/,;(]', w.replace('UPPER(', ''))[0].rstrip(')'), v.get('name'))
            if j2 and j2.get('features'): j, w = j2, w + ' (then a name-word search)'
        if j is None and err.startswith('next run'):   # Nov 3 (A4): slow host budget / Crawl-delay / host resting: asked again next run, no try counted
            n['next run (slow host)'] += 1; continue
        if j is None:
            if re.match(r'HTTP 4|error 4', err) or 'robots' in err: q.update(read=TODAY, result=f'layer did not answer ({err})'); R[ref] = keep_old(R.get(ref), q)
            tries = int((R.get(ref) or {}).get('tries') or 0) + 1   # Nov 2: 47 rows were re-asked every chained run forever
            if tries >= 3: q.update(read=TODAY, result=f'layer did not answer 3 times ({err})', tries=tries)
            else: q['tries'] = tries
            R[ref] = {**(R.get(ref) or {}), **q} if tries < 3 else keep_old(R.get(ref), q)
            n['layer did not answer'] += 1; continue   # a time-out / 5xx: tried again next run, 3 times at most
        F = j.get('features') or []
        if not F: q.update(read=TODAY, where=w, result='record not found with that id / name'); n['record not found'] += 1; R[ref] = keep_old(R.get(ref), q); continue
        lat, lon = float(v.get('lat') or 0), float(v.get('lon') or 0)
        if not (lat or lon): q.update(read=TODAY, result='record found, but no POTA pin on file to measure'); R[ref] = keep_old(R.get(ref), q); continue
        ds = [d for d in (dist_m(lat, lon, f.get('geometry') or {}) for f in F) if d is not None]
        pin = min(ds) if ds else None
        nf0 = re.split(r'[\s/,;(]', str(v.get('field') or '').strip())[0]
        names = sorted({str(x) for f in F for k_, x in (f.get('attributes') or {}).items() if x and isinstance(x, str) and (k_.lower() == nf0.lower() or NAMEK.search(k_))})[:6]   # Nov 2 (chat 12): DE / GB names were [] (field OBJEKT, SITE_NAME ...)
        q.update(read=TODAY, where=w, result='record found', features=len(F), names=names, pin_m=pin, acres=round(sum(acres(f.get('geometry') or {}, lat) for f in F), 1) or None,
                 rule=('pin inside' if pin == 0 else 'R-G12 candidate: pin %s m outside (road / entrance)' % pin if pin is not None and pin <= 150 else
                       'R-G13: PIN OFF per the notes (outline usable if name + kind + size match; POTA pin never moves)' if 'PIN OFF' in str(v.get('notes')) else
                       'pin %s m from the record: farther than 150 m and no PIN OFF evidence' % pin))
        if pin and pin > 150 and 'PIN OFF' in str(v.get('notes')):
            P['rows'][ref] = {'name': v.get('name'), 'pota_pin': [lat, lon], 'km_to_record': round(pin / 1000, 1), 'evidence': str(v.get('notes'))[:400], 'source': v.get('url'), 'date': TODAY}
        n['record found'] += 1; R[ref] = keep_old(R.get(ref), q)
    n2 = reask(rows, R)   # chat 11 (Nov 1 3 PM): the rows with no record read back are asked again by place + name
    QF.parent.mkdir(parents=True, exist_ok=True)
    save_json_gz(QF, Q, indent=1, ensure_ascii=False); save_json_gz(PT, P, indent=1, ensure_ascii=False)
    left = sum(1 for r, v in rows.items() if v.get('status') in ('GIS FOUND', 'NAME SOLVED', 'PARCEL') and not (R.get(r) or {}).get('read'))
    left += sum(1 for q in R.values() if not str(q.get('answer') or '').strip() and not q.get('reasked') and REASK.match(str(q.get('result') or '')))   # re-asks still to do keep the chain going
    note('; '.join(f'{k} {x}' for k, x in n.items() if x) + f'; re-asked by place + name: {n2}; rows left {left}; questions {len(R)}, pin typos {len(P["rows"])}')
    print(f'LEFT={left}')


if __name__ == '__main__':
    if sys.argv[1:2] == ['merge-main']:
        try: sys.exit(merge_main())
        except Exception as e: note(f'merge-main stopped ({type(e).__name__}: {e})'); sys.exit(1)  # noqa: BLE001
    try: main()
    except Exception as e: note(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
