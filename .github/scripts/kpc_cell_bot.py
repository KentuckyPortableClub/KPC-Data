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


def files_for(date, fips, log):
    r = get(f'/map/downloads/listAvailabilityData/{date}', params={'category': 'State', 'technology_type': 'Mobile Broadband'})
    rows = (r.json() or {}).get('data') or [] if r.ok else []
    if not rows:   # the filters differ from what we expect: take the whole list and filter here
        r = get(f'/map/downloads/listAvailabilityData/{date}'); rows = (r.json() or {}).get('data') or [] if r.ok else []
    mine = [x for x in rows if str(x.get('state_fips') or '').zfill(2) == fips and 'mobile broadband' in str(x.get('technology_type') or '').lower()]
    log.append({'state': fips, 'listed': len(rows), 'mobile_files': len(mine), 'sample': mine[:3]})
    hexes = [x for x in mine if 'hex' in json.dumps(x).lower()] or mine
    csvs = [x for x in hexes if str(x.get('file_type') or '').lower() == 'csv'] or hexes
    return csvs


def read_file(date, row, want, log):
    """Download one coverage file; return {h3: (tech, env)} for the hexes we want."""
    fid = row.get('file_id')
    r = get(f'/map/downloads/downloadFile/availability/{fid}')
    if not r.ok: log.append({'file': fid, 'http': r.status_code}); return None
    got = {}
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for nm in z.namelist():
            if not nm.lower().endswith('.csv'): continue
            with z.open(nm) as f:
                rd = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
                cols = rd.fieldnames or []
                hc = next((c for c in cols if 'h3' in c.lower()), None)
                tc = next((c for c in cols if c.lower() in ('technology', 'technology_code', 'tech_code')), None)
                ec = next((c for c in cols if 'environment' in c.lower() or c.lower() == 'env'), None)
                log.append({'file': fid, 'csv': nm, 'cols': cols[:20]})
                if not hc: continue
                for x in rd:
                    h = x.get(hc)
                    if h in want:
                        t = TECH.get(str(x.get(tc) or row.get('technology_code') or ''), str(x.get(tc) or row.get('technology_code_desc') or ''))
                        got.setdefault(h, []).append((t, str(x.get(ec) or '')))
    except Exception as e:  # noqa: BLE001
        log.append({'file': fid, 'error': f'{type(e).__name__}: {e}'[:200]}); return None
    return got


def best(lst):
    """Outdoor stationary first: the FCC's environment codes as read are kept in the work log; a file without an environment column
    is taken as it is. Returns the best technology."""
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
            carrier = str(row.get('provider_name') or row.get('brand_name') or row.get('provider_id'))
            for h, lst in g.items(): res.setdefault(h, {}).setdefault(carrier, []).extend(lst)
        carriers = sorted({str(r_.get('provider_name') or r_.get('provider_id')) for r_ in files})
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


if __name__ == '__main__':
    try: main()
    except Exception as e: note(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
