"""Import the Mapping agent's master workbook (KPC_All_GIS_Sources_plus_mapping-nov1.xlsx) into registry/master_nov1.json.

READ ONLY: the workbook is opened with openpyxl read_only=True and never saved, copied over or merged (do not run
world_keys/merge.py or the trails round-1 merge). Every row is deduped against the engine's own registry; a duplicate keeps
OUR entry and gets the workbook's status / notes attached (annotations). New rows are added with the workbook's status / notes.
Source policy: never-use rows are refused; WDPA / Protected Planet rows (incl. HDX copies) go to the W-10 last-resort list
(approx only); 'Token Required' / sign-in rows are refused as 'needs sign-in'.

  python3 registry/import_master.py /path/to/KPC_All_GIS_Sources_plus_mapping-nov1.xlsx [--out registry/master_nov1.json]
"""
import argparse, collections, datetime, hashlib, json, os, pathlib, re, sys, urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from core import rules                                    # noqa: E402
from core.registry import Registry, norm_url              # noqa: E402

US = set('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR VI GU AS MP'.split())
CA = set('AB BC MB NB NL NS NT NU ON PE QC SK YT'.split())
HDX = re.compile(r'data\.humdata\.org|\bhdx\b', re.I)
SIGNIN = re.compile(r'token required|sign[- ]?in|login required|requires (a )?log ?in|subscription', re.I)
SHEET_USE = {'US boundaries': 'outline', 'Canada boundaries': 'outline', 'World boundaries': 'outline', 'Trail lines': 'trail',
             'Parking + access': 'parking', 'Camping (outside agent)': 'camping', 'Acres (outside agent)': 'acres'}


def area_of(raw, sheet):
    a = str(raw or '').strip()
    if not a: return ''
    if a.startswith('CA (all)') or a == 'CA (all)': return 'CA'
    if a.startswith('US (all)'): return 'US'
    if re.match(r'^(US|CA)-[A-Z]{2}$', a): return a
    if sheet in ('Parking + access', 'Trail lines', 'Campground sources', 'Open-data portals') and len(a) == 2:
        if a in CA and a not in US: return f'CA-{a}'
        if a in US: return f'US-{a}'
    return a.split()[0][:6]


def kind_of(u):
    lu = u.lower()
    if 'service=wfs' in lu or '/wfs' in lu.split('?')[0]: return 'wfs'
    if '/rest/services/' in lu:
        return 'arcgis' if re.search(r'/(mapserver|featureserver)/\d+/?$', lu.split('?')[0]) else 'arcgis-service'
    if '/collections/' in lu or '/ogc/features' in lu: return 'ogcapi'
    if re.search(r'\.(zip|geojson|gpkg|kmz|kml|shp)(\?|$)', lu): return 'download'
    return 'page'


def wfs_parts(u):
    base, _, q = u.partition('?')
    qs = {k.lower(): v for k, v in urllib.parse.parse_qsl(q)}
    layer = qs.get('typenames') or qs.get('typename')
    srs = re.search(r'(\d{4,5})$', qs.get('srsname', '') or '')
    return base, layer, (int(srs.group(1)) if srs else None), qs.get('version')


def key_of(u):
    if kind_of(u) == 'wfs':
        b, l, _, _ = wfs_parts(u); return f'{norm_url(b)}|{(l or "").lower()}'
    return norm_url(u.split('?')[0] if '/rest/services/' in u else u)


def first_url(row):
    for i, v in enumerate(row):
        if isinstance(v, str) and v.strip().lower().startswith('http'): return i, v.strip()
    return None, None


def read(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)          # read only: never saved
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = [(n, r) for n, r in enumerate(ws.iter_rows(values_only=True), start=1)]
    wb.close()
    return out


def ours():
    """Our registry keys (all files, rejected too, so nothing comes back in by the side door) + our yes rows."""
    from core import registry as _r
    R = Registry(files=[_r.HERE / x for x in _r.FILES])   # ours only: never dedupe against a previous import
    keys = {}
    for s in R.sources + R.rejected + getattr(R, 'last_resort', []):
        u = s.get('url') or ''
        k = f"{norm_url(u)}|{(s.get('layer') or '').lower()}" if s.get('kind') == 'wfs' else norm_url(u)
        keys[k] = s.get('id') or u
    yes = {(ref, norm_url(r[0])) for ref, v in R.yes_rows.items() for r in v if r}
    return R, keys, yes


def policy(text):
    """-> ('ok' | 'last_resort' | 'refused', why)."""
    if re.search(rules.WDPA, text, re.I) or HDX.search(text) and re.search(r'wdpa|protected', text, re.I):
        return ('last_resort', 'WDPA / Protected Planet copy (incl. HDX): W-10 last resort only') if rules.wdpa_last_resort_ok() else ('refused', 'WDPA (W-10 last resort switched off)')
    bad = rules.forbidden(text)
    if bad: return 'refused', f'never-use source ({bad})'
    if SIGNIN.search(text): return 'refused', 'needs sign-in (Token Required / login): never used'
    return 'ok', ''


def run(path, out):
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    st = os.stat(path)
    S = read(path)
    R, keys, yes = ours()
    res = {'about': 'Imported READ-ONLY from the Mapping agent\'s master workbook (never saved or merged). New rows keep the '
                    'workbook\'s status / notes (wb_status, wb_notes); duplicates of our own entries are listed under '
                    '"annotations" and attached to our entry at load time. Leads only: chat 11 decides.',
           'workbook': {'path': str(path), 'sha256': sha, 'mtime': datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds'),
                        'read': datetime.datetime.now().isoformat(timespec='seconds')},
           'sources': [], 'annotations': {}, 'yes_rows': {}, 'park_leads': {}, 'pages': [], 'portals': [], 'picture_maps': [],
           'failed_hosts': {}, 'last_resort': [], 'refused': [], 'counts': {}}
    C = collections.defaultdict(collections.Counter)
    seen = {}
    for sheet, use in SHEET_USE.items():
        for n, row in S.get(sheet, [])[1:]:
            i, u = first_url(row)
            if not u: continue
            vals = [str(v) if v is not None else '' for v in row]
            text = ' '.join(vals)
            pol, why = policy(text)
            if pol == 'refused':
                res['refused'].append({'sheet': sheet, 'row': n, 'url': u, 'why': why}); C[sheet]['refused'] += 1; continue
            k = key_of(u)
            if sheet == 'Trail lines':                          # some rows are shifted one column: find the area by shape
                area = next((area_of(v, sheet) for v in vals if re.fullmatch(r'[A-Z]{2}|(US|CA)-[A-Z]{2}', v.strip())), '')
                name_field = vals[i + 1] if i + 1 < len(vals) and vals[i + 1] and len(vals[i + 1]) < 40 and ' ' not in vals[i + 1] else None
                agency = next((v for j, v in enumerate(vals) if j != i and len(v) > 8 and not v.startswith('http') and 'Added by' not in v), '')
                status = next((v for v in vals if 'Added by' in v or 'approved' in v.lower()), vals[-1])
                notes = ''
            else:
                area = area_of(row[0], sheet)
                agency, name_field = vals[1], (vals[3] or None)
                status, notes = vals[5] if sheet in ('US boundaries', 'Canada boundaries', 'World boundaries', 'Parking + access') else vals[8] if len(vals) > 8 else '', ''
                if sheet in ('Camping (outside agent)', 'Acres (outside agent)'):
                    name_field = vals[4] or None; notes = ' | '.join(x for x in (vals[3], vals[6], vals[7]) if x)
                if sheet == 'Parking + access': notes = vals[4]
                if sheet == 'World boundaries': notes = f'parks approved on it: {vals[4]}' if vals[4] else ''
            if area in ('US', 'CA'):                             # a state / provincial host listed under the whole country
                host = urllib.parse.urlparse(u).netloc.lower()
                m = re.search(r'(?:^|\.)([a-z]{2})\.(?:gov|us)$', host) if area == 'US' else re.search(r'\.gov\.([a-z]{2})\.ca$|(?:^|\.)([a-z]{2})\.ca$', host)
                code = next((g for g in (m.groups() if m else ()) if g), '').upper()
                if code and code in (US if area == 'US' else CA): notes = (notes + ' | ' if notes else '') + f'area set to {area}-{code} from the host (workbook said {area})'; area = f'{area}-{code}'
            wb = {'sheet': sheet, 'row': n, 'status': status, 'notes': notes}
            if pol == 'last_resort':
                res['last_resort'].append({**wb, 'url': u, 'area': area, 'why': why}); C[sheet]['last_resort'] += 1; continue
            if k in keys:
                res['annotations'].setdefault(keys[k], []).append(wb); C[sheet]['duplicate (ours)'] += 1; continue
            if (k, use) in seen:
                seen[(k, use)].setdefault('wb_also', []).append(wb); C[sheet]['duplicate (in workbook)'] += 1; continue
            kd = kind_of(u)
            s = {'id': f'WB-{sheet.split()[0][:5].upper()}-{n}', 'area': area, 'cc': area.split('-')[0], 'use': use, 'kind': kd, 'url': u,
                 'name_field': name_field, 'agency': agency, 'grade': 'official', 'wb_status': status, 'wb_notes': notes,
                 'wb_sheet': sheet, 'wb_row': n, 'from': 'master workbook (Mapping agent, nov1)',
                 'verified': {'status': 'imported' if kd in ('arcgis', 'wfs', 'ogcapi', 'download') else 'imported-not-queryable',
                              'why': 'imported from the master workbook; the workbook status is kept in wb_status', 'date': datetime.date.today().isoformat()}}
            if 'approved by chat 11' in status.lower(): s['verified']['status'] = 'club'
            if kd == 'wfs':
                b, l, srs, ver = wfs_parts(u); s.update(url=b, layer=l)
                if srs: s['srs'] = srs
                if ver: s['version'] = ver
                if not l: s['verified']['status'] = 'imported-not-queryable'
            if use == 'acres': s['acres_field'] = vals[5] or None
            if area in ('US', 'CA') or area.startswith(('US-', 'CA-')): pass
            res['sources'].append(s); seen[(k, use)] = s; C[sheet]['new'] += 1
    # per-park YES rows (chat 11) and the outside agent's per-park matches
    for n, row in S.get('Approved per park (US+CA)', [])[1:]:
        if not row or not row[0] or not row[3]: continue
        ref, u = str(row[0]).strip(), str(row[3]).strip()
        if (ref, norm_url(u)) in yes: C['Approved per park (US+CA)']['duplicate (ours)'] += 1; continue
        if policy(' '.join(str(x or '') for x in row))[0] != 'ok': C['Approved per park (US+CA)']['refused'] += 1; continue
        res['yes_rows'].setdefault(ref, []).append([u, row[5], row[2]]); C['Approved per park (US+CA)']['new'] += 1
    help_rows = S.get('Outside agent help', [])
    for n, row in help_rows[2:]:
        if not row or not row[0] or not row[2]: continue
        ref, u = str(row[0]).strip(), str(row[2]).strip()
        txt = ' '.join(str(x or '') for x in row)
        pol, why = policy(txt)
        if pol != 'ok':
            (res['last_resort'] if pol == 'last_resort' else res['refused']).append({'sheet': 'Outside agent help', 'row': n, 'url': u, 'ref': ref, 'why': why})
            C['Outside agent help'][pol if pol == 'refused' else 'last_resort'] += 1; continue
        if (ref, norm_url(u)) in yes: C['Outside agent help']['duplicate (ours)'] += 1; continue
        meth = str(row[5] or '')
        lead = {'url': u, 'name_field': row[3], 'record': row[4], 'method': meth, 'notes': row[6], 'row': n,
                'check': 'name only: no location check (a person must check)' if ('location' not in meth and 'researcher' not in meth) else ''}
        L = res['park_leads'].setdefault(ref, [])
        if any(norm_url(x['url']) == norm_url(u) for x in L): C['Outside agent help']['duplicate (in workbook)'] += 1; continue
        L.append(lead); C['Outside agent help']['new'] += 1
    for n, row in S.get('Campground sources', [])[1:]:
        if row and row[2]:
            if policy(' '.join(str(x or '') for x in row))[0] != 'ok': C['Campground sources']['refused'] += 1; continue
            res['pages'].append({'area': area_of(row[0], 'Campground sources'), 'host': row[1], 'url': row[2], 'what': 'camping / reservation page', 'row': n}); C['Campground sources']['new'] += 1
    for n, row in S.get('Open-data portals', [])[1:]:
        if row and row[2]:
            res['portals'].append({'area': area_of(row[0], 'Open-data portals'), 'name': row[1], 'url': row[2], 'row': n}); C['Open-data portals']['new'] += 1
    for n, row in S.get('Picture maps (world)', [])[1:]:
        if row and row[2]:
            res['picture_maps'].append({'cc': row[0], 'country': row[1], 'url': row[2], 'publisher': row[3], 'year': row[4], 'shows': row[5],
                                        'pages': row[6], 'licence': row[7], 'notes': row[8], 'row': n,
                                        'note': 'picture map: for the picture-map saver, never traced by the engine'}); C['Picture maps (world)']['new'] += 1
    ours_failed = set(R.failed_hosts)
    for n, row in S.get('Failed + blocked hosts', [])[1:]:
        if row and row[0]:
            h = str(row[0]).strip()
            res['failed_hosts'][h] = {'count': row[1], 'why': row[2], 'from': 'master workbook', 'row': n}
            C['Failed + blocked hosts']['duplicate (ours)' if h in ours_failed else 'new'] += 1
    res['counts'] = {k: dict(v) for k, v in C.items()}
    res['counts']['_total'] = dict(sum(C.values(), collections.Counter()))
    json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False, default=str)
    after = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    assert after == sha, 'the workbook changed while it was read: re-run the import'
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('workbook'); ap.add_argument('--out', default=str(HERE / 'master_nov1.json'))
    a = ap.parse_args()
    r = run(a.workbook, a.out)
    print(json.dumps(r['counts'], indent=1))
