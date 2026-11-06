#!/usr/bin/env python3
"""CELL COVERAGE AT THE PARK (chat 10, Oct 31 2026; HQ 9:00 PM, Brandon 8:59 PM 'ok releasing cell coverage for a test').
Rule sheet: KPC-Links .claude/notes/ideas.md 'CELL COVERAGE RULE SHEET'. Source = the FCC National Broadband Map (Broadband Data
Collection) public data API ONLY: the carriers' own reported mobile coverage as H3 hexagons (resolution 9). FCC developer page: the
APIs are 'free for use by anyone', 'indicate the source on your page' -> every file says 'FCC National Broadband Map (carrier-reported)'.
Per park: the best technology each carrier claims (5G / 4G / none) at the POTA pin and at the park's main parking point;
'no FCC data' when the FCC file for that state could not be read. Outdoor stationary first (in-vehicle kept apart when the file says).
Key: GitHub secrets FCC_BDC_USERNAME / FCC_BDC_TOKEN (sent as the API's 'username' / 'hash_value' headers; never printed or saved).
Refresh only when the FCC publishes a new as-of date (data/cell/state.json). Polite: one request every 2 s. Never fails.
  python3 kpc_cell_bot.py [--states KY] [--test]   (out: data/cell/US-KY.json + data/cell/test-parks.json; work files: $OUT_WORK)"""
import csv, datetime as dt, io, json, os, pathlib, re, sys, time, zipfile
import requests

API = 'https://broadbandmap.fcc.gov/api/public'
UA = 'KPC-cell-bot (Kentucky Portable Club ham radio club; https://github.com/KentuckyPortableClub)'
OUT = pathlib.Path('data/cell'); WORK = pathlib.Path(os.environ.get('OUT_WORK') or '../out/cell')
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
SRC = 'FCC National Broadband Map (carrier-reported coverage)'
TEST = {'US-0561': 'VA', 'US-7494': 'NV'}   # a coastal NWR (Chincoteague) + a western BLM site (Red Rock Canyon NCA); the KY three are in KY's file
TECH = {'300': '3G', '400': '4G', '500': '5G'}
RANK = {'none': 0, '3G': 1, '4G': 2, '5G': 3}
FIPS = {'KY': '21', 'VA': '51', 'NV': '32'}
LAST = [0.0]


def note(m): print('::notice title=Cell coverage::' + str(m)[:900], flush=True)


def get(path, **kw):
    w = 2 - (time.time() - LAST[0])
    if w > 0: time.sleep(w)
    LAST[0] = time.time()
    h = {'username': os.environ.get('FCC_BDC_USERNAME', ''), 'hash_value': os.environ.get('FCC_BDC_TOKEN', ''), 'user-agent': UA}
    return requests.get(API + path, headers=h, timeout=300, **kw)


def pins_ky():
    D = json.load(open(LINKS / 'kpc-ky-data.json'))
    out = {}
    for p in D.get('parks') or []:
        if p.get('c') and p.get('la') is not None:
            ap = (p.get('ap') or [None])[0]
            out[p['c']] = {'n': p.get('n'), 'pin': [p['la'], p['lo']], 'park': [ap[0], ap[1]] if ap else None}
    return out


def pins_other(refs_by_st):
    out = {}
    for st, refs in refs_by_st.items():
        P = (json.load(open(f'data/parkinfo/US-{st}.json')).get('parks') or {})
        try: A = json.load(open(f'data/access/US-{st}.json')).get('parks') or {}
        except Exception: A = {}  # noqa: BLE001
        for r in refs:
            a = P.get(r)
            if not a: continue
            ap = (A.get(r) or [None])[0]
            out[r] = {'n': a[0], 'pin': [a[5], a[6]], 'park': [ap[0], ap[1]] if ap else None, 'st': st}
    return out


def _hex_file(x):
    t = json.dumps(x).lower()
    return 'hex' in t or '_h3_' in t or 'h3' in str(x.get('subcategory') or '').lower()


def _fmt_rank(x):
    ft = (str(x.get('file_type') or '') + ' ' + str(x.get('file_name') or '')).lower()
    return 0 if 'gpkg' in ft or 'geopackage' in ft else 1 if 'shp' in ft or 'shape' in ft else 2 if 'csv' in ft else 3


def files_for(date, fips, log):
    """Nov 6 fix (carrier field): the STATE files are all carriers together (no provider in them) and come as Shapefile / GeoPackage,
    not CSV, so the old read found nothing and the carrier came out 'None'. Now: the PROVIDER files first (one per carrier and
    technology: bdc_{fips}_{providerid}_{tech}_mobile_broadband_h3_..., fields providerid / brandname / technology / environmnt /
    h3_res9_id), one format per carrier+technology (GeoPackage, else Shapefile, else CSV). Only when the FCC lists no provider file
    for the state: the state file, labelled 'All carriers (FCC combined)'."""
    out = []
    for cat in ('Provider', 'State'):
        r = get(f'/map/downloads/listAvailabilityData/{date}', params={'category': cat, 'technology_type': 'Mobile Broadband'})
        rows = (r.json() or {}).get('data') or [] if r.ok else []
        if not rows:   # the filters differ from what we expect: take the whole list and filter here
            r = get(f'/map/downloads/listAvailabilityData/{date}'); rows = (r.json() or {}).get('data') or [] if r.ok else []
            rows = [x for x in rows if str(x.get('category') or '').lower() == cat.lower()]
        mine = [x for x in rows if str(x.get('state_fips') or '').zfill(2) == fips and 'mobile broadband' in str(x.get('technology_type') or '').lower()]
        mine = [x for x in mine if _hex_file(x)] or mine
        pick = {}
        for x in sorted(mine, key=_fmt_rank):
            k = (str(x.get('provider_id') or ''), str(x.get('technology_code') or x.get('technology_code_desc') or ''))
            pick.setdefault(k, x)
        log.append({'state': fips, 'category': cat, 'listed': len(rows), 'mobile_files': len(mine), 'picked': len(pick), 'sample': mine[:3]})
        for x in pick.values(): x['_cat'] = cat
        out = list(pick.values())
        if out: break
    return out


ALL = 'All carriers (FCC combined)'


def _col(cols, *names, part=None):
    low = {c.lower(): c for c in cols}
    for n in names:
        if n in low: return low[n]
    return next((c for c in cols if part and part in c.lower()), None) if part else None


def _rows_gpkg(path):
    import sqlite3
    con = sqlite3.connect(path)
    try:
        tabs = [t for (t,) in con.execute("select table_name from gpkg_contents where data_type in ('features','attributes')")] or \
               [t for (t,) in con.execute("select name from sqlite_master where type='table' and name not like 'gpkg%' and name not like 'rtree%' and name not like 'sqlite%'")]
        for t in tabs:
            cur = con.execute(f'select * from "{t}"')
            cols = [d[0] for d in cur.description]
            keep = [i for i, c in enumerate(cols) if c.lower() not in ('geom', 'geometry', 'shape')]
            yield [cols[i] for i in keep], None
            for row in cur: yield None, {cols[i]: row[i] for i in keep}
    finally: con.close()


def _rows_dbf(fh):
    """A plain dBASE III reader (the Shapefile's attribute table); no extra packages."""
    import struct
    head = fh.read(32); n, hl, rl = struct.unpack('<IHH', head[4:12])
    rest, fields = fh.read(hl - 32), []
    for k in range(0, len(rest) - 31, 32):
        d = rest[k:k + 32]
        if d[0] == 0x0D: break
        fields.append((d[:11].split(b'\0')[0].decode('latin-1'), chr(d[11]), d[16]))
    yield [f[0] for f in fields], None
    for _ in range(n):
        rec = fh.read(rl)
        if not rec or len(rec) < rl: break
        if rec[:1] == b'*': continue
        o, pos = {}, 1
        for nm, _t, ln in fields:
            o[nm] = rec[pos:pos + ln].decode('latin-1', 'replace').strip(); pos += ln
        yield None, o


def _rows_csv(fh):
    rd = csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace'))
    yield rd.fieldnames or [], None
    for x in rd: yield None, x


def parse_zip(blob, want, row, log):
    """{h3: [(tech, env, carrier)]} for the hexes we want, from one FCC zip (GeoPackage, Shapefile .dbf or CSV inside)."""
    import tempfile
    got = {}
    z = zipfile.ZipFile(io.BytesIO(blob))
    for nm in z.namelist():
        ext = nm.lower().rsplit('.', 1)[-1]
        if ext not in ('gpkg', 'dbf', 'csv'): continue
        if ext == 'gpkg':
            tf = tempfile.NamedTemporaryFile(suffix='.gpkg', delete=False); tf.write(z.read(nm)); tf.close()
            it = _rows_gpkg(tf.name)
        else:
            it = (_rows_dbf if ext == 'dbf' else _rows_csv)(z.open(nm))
        cols, hc = [], None
        for c, x in it:
            if c is not None:
                cols = c
                hc = _col(cols, 'h3_res9_id', 'h3_hex', part='h3')
                tc = _col(cols, 'technology', 'technology_code', 'tech_code', 'tech')
                ec = _col(cols, 'environmnt', 'environment', 'env', part='environ')
                bc = _col(cols, 'brandname', 'brand_name', 'provider_name')
                pc = _col(cols, 'providerid', 'provider_id')
                log.append({'file': row.get('file_id'), 'member': nm, 'cols': cols[:20]})
                continue
            if not hc: break
            h = x.get(hc)
            if h not in want: continue
            code = str((x.get(tc) if tc else None) or row.get('technology_code') or '').split('.')[0]
            t = TECH.get(code, TECH.get(str(row.get('technology_code') or ''), str(row.get('technology_code_desc') or code)))
            car = str((x.get(bc) if bc else '') or row.get('provider_name') or row.get('brand_name') or (x.get(pc) if pc else '') or row.get('provider_id') or '').strip()
            if not car or car == 'None' or row.get('_cat') == 'State': car = ALL
            got.setdefault(h, []).append((t, str(x.get(ec) if ec else ''), car))
        if ext == 'gpkg':
            try: os.unlink(tf.name)
            except OSError: pass
    return got


def read_file(date, row, want, log):
    """Download one coverage file; return {h3: [(tech, env, carrier)]} for the hexes we want."""
    fid = row.get('file_id')
    r = get(f'/map/downloads/downloadFile/availability/{fid}')
    if not r.ok: log.append({'file': fid, 'http': r.status_code}); return None
    try: return parse_zip(r.content, want, row, log)
    except Exception as e:  # noqa: BLE001
        log.append({'file': fid, 'error': f'{type(e).__name__}: {e}'[:200]}); return None


def best(lst):
    """Best technology claimed at the point. Both FCC environment codes include outdoor stationary (0 = outdoor stationary only,
    1 = in-vehicle AND outdoor stationary), so every row counts for an operator standing at the park."""
    out = 'none'
    for t, env in lst:
        if t in RANK and RANK[t] > RANK[out]: out = t
    return out


def main():
    a = sys.argv[1:]
    sts = (a[a.index('--states') + 1] if '--states' in a else 'KY').split(',')
    test = '--test' in a or os.environ.get('TEST') == '1'
    WORK.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    if not (os.environ.get('FCC_BDC_USERNAME') and os.environ.get('FCC_BDC_TOKEN')):
        note('FCC key not set (GitHub secrets FCC_BDC_USERNAME / FCC_BDC_TOKEN): nothing read'); return
    try:
        t = requests.get('https://www.fcc.gov/general/api-terms-service', headers={'user-agent': UA}, timeout=60)
        (WORK / 'fcc-terms.html').write_text(t.text[:400000])
    except Exception: pass  # noqa: BLE001
    r = get('/map/listAsOfDates')
    if not r.ok: note(f'FCC list of dates: HTTP {r.status_code} (key refused or site down): nothing changed'); return
    dates = sorted({x.get('as_of_date', '')[:10] for x in (r.json() or {}).get('data') or [] if 'availability' in str(x.get('data_type'))})
    if not dates: note('FCC gave no availability dates'); return
    date = dates[-1]
    state_f = OUT / 'state.json'
    try: S = json.load(open(state_f))
    except Exception: S = {}  # noqa: BLE001
    jobs = {}
    if 'KY' in sts:
        if S.get('KY') == date and (OUT / 'US-KY.json').exists() and not test: note(f'KY: FCC as-of {date} already read: nothing to do')
        else: jobs['KY'] = pins_ky()
    if test:
        by = {}
        for ref, st in TEST.items(): by.setdefault(st, []).append(ref)
        for st, P in ((st, pins_other({st: refs})) for st, refs in by.items()): jobs[st] = P
    import h3
    log, summ = [], []
    for st, P in jobs.items():
        cell = lambda p: h3.latlng_to_cell(p[0], p[1], 9) if p else None
        want = {c for v in P.values() for c in (cell(v['pin']), cell(v['park'])) if c}
        files = files_for(date, FIPS[st], log)
        res, readok = {}, 0
        for row in files:
            g = read_file(date, row, want, log)
            if g is None: continue
            readok += 1
            for h, lst in g.items():
                for t, env, car in lst: res.setdefault(h, {}).setdefault(car, []).append((t, env))
        # Nov 6: the carriers are the names IN the files (brandname), else the FCC list's provider name; never 'None'
        carriers = sorted({c for v in res.values() for c in v} | {str(r_.get('provider_name') or '').strip() for r_ in files if r_.get('_cat') == 'Provider' and str(r_.get('provider_name') or '').strip() not in ('', 'None')})
        if not carriers and readok: carriers = [ALL]
        rows = {}
        for ref, v in P.items():
            e = {'n': v['n']}
            for k in ('pin', 'park'):
                c = cell(v[k])
                if not c: continue
                e[k] = 'no FCC data' if not readok else {cr: best(res.get(c, {}).get(cr, [])) for cr in carriers}
                e[k + '_at'] = [round(v[k][0], 5), round(v[k][1], 5)]
            rows[ref] = e
        doc = {'src': SRC, 'as_of': date, 'read': dt.date.today().isoformat(), 'how': 'best technology each carrier reports at the point (H3 hexagon, resolution 9); none = that carrier reports no coverage there',
               'carriers': carriers, 'files_read': f'{readok} of {len(files)}', 'parks': rows}
        f = OUT / ('US-KY.json' if st == 'KY' else f'test-{st}.json')
        json.dump(doc, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
        if st == 'KY' and readok: S['KY'] = date
        summ.append(f'{st}: {len(rows)} parks, {readok}/{len(files)} FCC files, {len(carriers)} carriers')
    json.dump(log, open(WORK / 'work-log.json', 'w'), indent=1, default=str)
    json.dump(S, open(state_f, 'w'), indent=1)
    note(f'FCC as-of {date}; ' + ('; '.join(summ) or 'nothing read'))


def selftest():
    """Offline: one GeoPackage zip, one Shapefile (.dbf) zip and one State (all carriers) CSV zip, built here; no FCC key, no network."""
    import sqlite3, struct, tempfile
    H1, H2 = '892aa8458c7ffff', '892aa8458cbffff'
    d = tempfile.mkdtemp(); g = os.path.join(d, 'x.gpkg'); con = sqlite3.connect(g)
    con.execute("create table gpkg_contents (table_name text, data_type text)"); con.execute("insert into gpkg_contents values ('cov','features')")
    con.execute('create table cov (fid integer, geom blob, frn text, providerid integer, brandname text, technology integer, mindown real, minup real, minsignal integer, environmnt integer, h3_res9_id text)')
    con.execute("insert into cov values (1, x'00', '0001', 130077, 'Verizon', 500, 7.0, 1.0, -110, 0, ?)", (H1,))
    con.execute("insert into cov values (2, x'00', '0001', 130077, 'Verizon', 500, 7.0, 1.0, -110, 1, '89ffffffffffff1')"); con.commit(); con.close()
    b = io.BytesIO(); zipfile.ZipFile(b, 'w').write(g, 'bdc_21_130077_500_mobile_broadband_h3_J24_01apr2025.gpkg')
    log = []
    r1 = parse_zip(b.getvalue(), {H1, H2}, {'file_id': 1, '_cat': 'Provider', 'technology_code': 500}, log)
    assert r1 == {H1: [('5G', '0', 'Verizon')]}, r1
    flds = [('providerid', 'N', 10), ('brandname', 'C', 20), ('technology', 'N', 3), ('environmnt', 'N', 1), ('h3_res9_id', 'C', 15)]
    hdr = struct.pack('<BBBBIHH20x', 3, 125, 1, 1, 1, 32 + 32 * len(flds) + 1, 1 + sum(f[2] for f in flds))
    for nm, t, ln in flds: hdr += nm.encode().ljust(11, b'\0') + t.encode() + b'\0' * 4 + bytes([ln, 0]) + b'\0' * 14
    rec = b' ' + b'130403'.rjust(10) + b'AT&T'.ljust(20) + b'400' + b'1' + H2.encode()
    b = io.BytesIO(); z = zipfile.ZipFile(b, 'w'); z.writestr('bdc_21_130403_400_mobile_broadband_h3.dbf', hdr + b'\r' + rec + b'\x1a'); z.close()
    r2 = parse_zip(b.getvalue(), {H1, H2}, {'file_id': 2, '_cat': 'Provider'}, log)
    assert r2 == {H2: [('4G', '1', 'AT&T')]}, r2
    b = io.BytesIO(); z = zipfile.ZipFile(b, 'w'); z.writestr('bdc_21_400_mobile_broadband_h3.csv', f'technology,mindown,minup,environmnt,h3_res9_id\n400,5,1,0,{H1}\n'); z.close()
    r3 = parse_zip(b.getvalue(), {H1}, {'file_id': 3, '_cat': 'State', 'provider_name': None}, log)
    assert r3 == {H1: [('4G', '0', ALL)]}, r3
    assert best([('4G', '0'), ('5G', '1')]) == '5G' and best([]) == 'none'
    print('kpc_cell_bot selftest OK: GeoPackage, Shapefile .dbf and State CSV read; carriers', sorted({c for r in (r1, r2, r3) for v in r.values() for *_, c in v}))


if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest(); sys.exit(0)
    try: main()
    except Exception as e: note(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
