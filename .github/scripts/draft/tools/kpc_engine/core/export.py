"""Hand-back export: writes the engine's finds in the club's intake shapes (HANDBACK_FORMATS.md, KPC-Data branch
`intake-files`). Reads only <out>/work/<kind>/results-*.jsonl (+ agencies.json, blocked.csv) and writes only <out>/handback/.
The engine decides nothing: every file is a list of leads for chat 11; UNLIKELY rows are never exported as layers.

Shapes follow the club's real sample files (intake_samples/samples/*.sample.json, Nov 1): external-sources-oct30,
world-sources-r15, docs-found-us-oct31-v2 (+ hardlook-ca / maplinks), parking-hunt-oct31, camping-us-oct31 and
camping-ca-nov1, acres-us-ca-oct31, portals-us-ca-oct31. tests/test_export_shapes.py checks every key against them.
docs-pagefix follows the club's round-4 samples (fixtures/handback_samples/docs-pagefix-{us,ca}.sample.csv): US keyed by the
hours-fees workbook's Parks-sheet row (no workbook / no row = the ref + a 'mapping needed' note), Canada keyed by POTA ref."""
import csv, glob, json, pathlib, re, urllib.parse

ENGINE = 'kpc engine'
CLOSEST = {}                      # every hand-back file now has a club sample (docs-pagefix since round 4)
PAGEFIX_US = ['row', 'park', 'old F URL', 'correct URL', 'why column F was replaced']
PAGEFIX_CA = ['row', 'POTA ref', 'park', 'column F URL', 'issue', 'correct official URL (if found)', 'note']
MAPPING_NEEDED = 'mapping needed: no hours-fees workbook row for this ref'
LAYER_OK = ('found', 'candidate')


def _rows(out, kind, post=True):
    """Saved rows for one kind (pass 2 overrides pass 1). post=True applies the whole-run rules (duplicate facilities,
    containers, trail bar, source-policy stamping) so the hand-back files match grades.md."""
    rows = _raw_rows(out, kind)
    if post and rows:
        import kpc_engine
        kpc_engine.postprocess(kind, rows)
    return rows


def _raw_rows(out, kind):
    by = {}
    for f in sorted(glob.glob(f'{out}/work/{kind}/results-p1-*.jsonl')) + sorted(glob.glob(f'{out}/work/{kind}/results-p2-*.jsonl')):
        for line in open(f):
            try: r = json.loads(line)
            except ValueError: continue
            by[(r.get('ref'), r.get('area'))] = r          # pass 2 overrides pass 1
    return list(by.values())


def _st(area): return area[3:] if area and area[:3] in ('US-', 'CA-') else area


def export(out, name):
    out = pathlib.Path(out); hb = out / 'handback'; hb.mkdir(parents=True, exist_ok=True)
    wrote, flags = {}, []
    ol = [r for r in _rows(out, 'outline') if r.get('status') in LAYER_OK and r.get('rule_g') != 'UNLIKELY' and r.get('service_url')]
    stat = lambda r: f"{'FOUND' if r.get('status') == 'found' and r.get('rule_g') == 'SURE' else 'POSSIBLE MATCH'} (engine {r.get('date') or ''})".replace(' )', ')')
    ext, world = {}, {'about': f'kpc engine finds ({name}): "rest" = ArcGIS layers; "other" = WFS / downloads. Leads only: nothing live without chat 11.', 'rest': {}, 'other': {}}
    for r in ol:
        if (r.get('area') or '')[:3] in ('US-', 'CA-'):
            lab = 'Trail' if r.get('park_class') in ('state_trail', 'national_trail') else 'Parks'
            ext.setdefault(f"{lab}|{r['ref']}", [])
            if r['service_url'] not in ext[f"{lab}|{r['ref']}"]: ext[f"{lab}|{r['ref']}"].append(r['service_url'])
        elif '/MapServer/' in r['service_url'] or '/FeatureServer/' in r['service_url']:
            world['rest'][r['ref']] = {'layer': r['service_url'], 'agency': r.get('agency') or '', 'field': r.get('name_field') or '', 'status': stat(r)}
        else:
            world['other'][r['ref']] = {'url': r.get('url') or r['service_url'], 'agency': r.get('agency') or '', 'status': stat(r)}
    _dump(hb / f'external-sources-{name}.json', ext); _dump(hb / f'world-sources-{name}.json', world)
    wrote['external-sources'] = len(ext); wrote['world-sources'] = len(world['rest']) + len(world['other'])

    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = 'hardlook'
    ws.append(HARDLOOK_COLS)
    for r in sorted(ol, key=lambda r: r['ref']):
        ws.append([r['ref'], r['service_url'], r.get('name_field') or '', f"{r.get('where') or r.get('record')} / {r.get('record_name') or ''}",
                   f"{r['status']} {r.get('band') or ''} {r.get('rule_g') or ''}".strip(),
                   f"{r.get('rule_g_why') or ''}; size {r.get('size_band') or 'unknown'}; {r.get('grade') or ''}; read {r.get('date')}; answer left blank for chat 11"])
    wb.save(hb / f'hardlook-{name}.xlsx'); wrote['hardlook'] = len(ol)

    docs = [r for r in _rows(out, 'docs') if r.get('status') in LAYER_OK]
    df, fix = {}, []
    for r in docs:
        m = r.get('map'); m = m if isinstance(m, dict) else ({'url': m} if m else {})
        if m.get('url') or r.get('page'):
            u = m.get('url') or ''
            kind = m.get('kind') or ('PDF' if u.lower().split('?')[0].endswith('.pdf') else 'IMAGE' if u.lower().rsplit('.', 1)[-1] in ('jpg', 'jpeg', 'png', 'gif') else 'MAP PAGE' if u else '')
            mp = m.get('page') or m.get('map_page') or 1
            df[r['ref']] = {'st': _st(r.get('area')), 'page': r.get('page') or '', 'map': u, 'map_page': int(mp) if str(mp).isdigit() else 1, 'kind': kind,
                            'date': r.get('map_date') or m.get('date'), 'agency': r.get('agency') or '',
                            'notes': f"kpc engine docs plug-in ({r.get('date')}): " + '; '.join(x for x in [r.get('why') or '', r.get('page_how') or ''] if x)[:300]}
    _dump(hb / f'docs-found-{name}.json', df); wrote['docs-found'] = len(df)
    us, ca, mapped = pagefix_rows(out)
    for tag, cols, rows_ in (('us', PAGEFIX_US, us), ('ca', PAGEFIX_CA, ca)):
        with open(hb / f'docs-pagefix-{tag}-{name}.csv', 'w', newline='') as f:
            w = csv.writer(f); w.writerow(cols); w.writerows(rows_)
        wrote[f'docs-pagefix-{tag}'] = len(rows_)
    wrote['docs-pagefix-workbooks'] = ', '.join(f'{k}: {v or "none (mapping needed)"}' for k, v in mapped.items())

    # parking-hunt-oct31 shape: {about, layers: {url: {agency, field, parks}}, rows: {ref: {State / province, Name, Type, Official agency, [Parking / access layer URL, Name / type field], Status, Notes}}}
    srcs = _src_index()
    pk = {'about': f'kpc engine parking / access finds ({name}): official agency point layers pin-tested per park. Status FOUND = points tied to '
                   'this park; NOT FOUND = no official point. Nothing live without chat 11.', 'layers': {}, 'rows': {}}
    for r in _rows(out, 'parking'):
        if r.get('status') not in ('found', 'not found', 'blocked'): continue
        feats = r.get('features') or []
        row = {'State / province': r.get('area'), 'Name': r.get('park') or '', 'Type': _ptype(r.get('park') or ''),
               'Official agency': (feats[0].get('agency') if feats else None) or r.get('agency_group') or 'managing agency not confirmed'}
        if feats:
            s0 = srcs.get(feats[0]['source'], {})
            row['Parking / access layer URL'] = s0.get('url') or feats[0].get('record_link', '').split('/query?')[0]
            row['Name / type field'] = s0.get('type_field') or s0.get('name_field') or ''
        row['Status'] = {'found': 'FOUND', 'blocked': 'BLOCKED'}.get(r['status'], 'NOT FOUND')
        row['Notes'] = ('Points: ' + '; '.join(f"{f['lat']}, {f['lon']} {f.get('type') or ''}{': ' + f['name'] if f.get('name') else ''} ({f['how']}, {f.get('record_link') or ''})" for f in feats[:12])
                        if feats else ((r.get('whynot') or {}).get('tag') or 'no official parking / access point found')) + f' [kpc engine {r.get("date")}]'
        pk['rows'][r['ref']] = row
        for f in feats:
            s0 = srcs.get(f['source'], {}); u = s0.get('url') or f.get('record_link', '').split('/query?')[0]
            L = pk['layers'].setdefault(u, {'agency': f.get('agency') or s0.get('agency') or '', 'field': s0.get('type_field') or s0.get('name_field') or '', 'parks': 0, '_refs': set()})
            L['_refs'].add(r['ref'])
    for L in pk['layers'].values(): L['parks'] = len(L.pop('_refs'))
    _dump(hb / f'parking-hunt-{name}.json', pk); wrote['parking-hunt'] = len(pk['rows'])

    # camping-us-oct31 (US) and camping-ca-nov1 (Canada) shapes: {about, rows: {ref: {...}}, layers: {url: parks}}
    cus = {'about': f'kpc engine camping finds ({name}), US: official campground points inside the park (YES) or within reach (NEARBY ONLY). '
                    'The engine never writes NO. Nothing live without chat 11.', 'rows': {}, 'layers': {}}
    cca = {'about': cus['about'].replace(', US:', ', Canada:'), 'rows': {}, 'layers': {}}
    for r in _rows(out, 'camping'):
        if r.get('status') != 'found': continue
        ca = (r.get('area') or '').startswith('CA-'); D = cca if ca else cus
        feats = r.get('features') or []
        inside = [f for f in feats if f.get('how') == 'place']
        lay = []
        for f in feats:
            s0 = srcs.get(f['source'], {}); u = s0.get('url') or (f.get('record_link') or '').split('/query?')[0]
            if u and u not in lay: lay.append(u)
        row = {('Province' if ca else 'State'): _st(r.get('area')), 'Name': r.get('park') or '', 'Type': _ptype(r.get('park') or ''),
               'Camping?': 'YES' if inside else 'NEARBY ONLY',
               'Campground name(s)': '; '.join(dict.fromkeys(f.get('name') or 'campground' for f in (inside or feats))),
               'Agency camping / reservation page': r.get('camp_page') or '',
               ('Type (tent / RV / cabins / oTENTik / backcountry)' if ca else 'Type (tent / RV / cabins / primitive)'): r.get('camp_type') or ''}
        if lay and not ca: row['Campground layer URL'] = lay[0]
        row['Notes'] = 'Source type: AGENCY LAYER. ' + '; '.join(f"{f.get('name') or 'campground'} {f['lat']}, {f['lon']} ({'inside' if f.get('how') == 'place' else str(round((f.get('m') or 0) / 1609.34, 1)) + ' mi'})" for f in feats[:10]) + f' [kpc engine {r.get("date")}]'
        if not ca: row['Checked by'] = 'kpc engine camping plug-in'
        D['rows'][r['ref']] = row
        for u in lay: D['layers'][u] = D['layers'].get(u, 0) + 1
    _dump(hb / f'camping-{name}.json', cus); wrote['camping'] = len(cus['rows'])
    if cca['rows']: _dump(hb / f'camping-ca-{name}.json', cca); wrote['camping-ca'] = len(cca['rows'])

    # acres-us-ca-oct31 shape: {about, Agencies: [...], Acres not downloadable: [...], Sources: [...]}
    ac = {'about': f'kpc engine acres ({name}): sizes computed from the official outline record (SURE matches only, approx, equal-area). '
                   'No agency list page was read, so "Agencies" is empty. Waiting room + chat 11 before use.', 'Agencies': [], 'Acres not downloadable': [], 'Sources': []}
    hosts = {}
    for r in ol:
        if r.get('acres_approx') is None or r.get('rule_g') != 'SURE' or (r.get('area') or '')[:3] not in ('US-', 'CA-'): continue
        ac['Acres not downloadable'].append({'Park number (if matched)': r['ref'], 'Park name (as the agency writes it)': r.get('record_name') or '',
                                             'Size': int(round(r['acres_approx'])), 'Unit': 'acres', 'Agency': r.get('agency') or '',
                                             'Source page': r.get('record_link') or r['service_url'],
                                             'Notes': f"computed from the official outline polygon (approx); layer {r['service_url']}; read {r.get('date')}"})
        h = urllib.parse.urlparse(r['service_url']).netloc
        H = hosts.setdefault(h, {'Host': h, 'Agency/area': r.get('agency') or None, 'Kind': 'GIS layer', 'Example URL': r['service_url'], '# times used': 0,
                                 'Status': 'OK', 'Detail': 'answered the engine (official outline layer)', 'Retry?': 'NO'})
        H['# times used'] += 1
    try:
        for b in csv.DictReader(open(out / 'blocked.csv')):
            h = b.get('domain') or ''
            if h and h not in hosts:
                hosts[h] = {'Host': h, 'Agency/area': None, 'Kind': 'GIS layer', 'Example URL': None, '# times used': 0, 'Status': 'BLOCKED',
                            'Detail': (b.get('reason') or '')[:200], 'Retry?': 'YES'}
    except OSError:
        pass
    ac['Sources'] = list(hosts.values())
    _dump(hb / f'acres-{name}.json', ac); wrote['acres'] = len(ac['Acres not downloadable'])

    _dump(hb / f'portals-{name}.json', _portals()); wrote['portals'] = len(_portals()['rows'])
    (hb / 'README.txt').write_text('Hand-back files for KPC-Data branch intake-files (HANDBACK_FORMATS.md), in the shapes of the club\'s\n'
                                   'sample files (intake_samples, Nov 1; docs-pagefix: round 4 samples). Leads only: answers are left for chat 11.\n'
                                   + ('CLOSEST shapes (no sample exists):\n' + '\n'.join(f'- {k}: {CLOSEST[k]}' for k in flags) + '\n' if flags else '')
                                   + f"docs-pagefix workbooks: {wrote['docs-pagefix-workbooks']}\n")
    return wrote, flags


HARDLOOK_COLS = ['Park number', 'NEW official layer URL', 'Name field', 'Record id / name for THIS park', 'Status', 'Notes']
PORTAL_COLS = ['Country', 'State / province', 'What we know already', 'Main open-data portal URL',
               'Portal kind (ArcGIS Hub / Socrata / CKAN / ArcGIS Online org / other)', 'Search address (tested)',
               'State GIS server (REST root)', 'Parks agency GIS server', 'Wildlife / natural resources GIS server', 'Forestry GIS server', 'Notes']


def _ptype(name):
    from core import rule_g
    k = rule_g.kind_g(name)
    return k.replace('_', ' ').title() if k else ''


def _src_index():
    from core import registry
    return {s.get('id'): s for s in registry.Registry().sources if s.get('id')}


def _root(u):
    m = re.match(r'(https?://[^?#]+?/rest/services)', u or '', re.I)
    return m.group(1) if m else None


def _portals():
    """portals-us-ca-oct31 shape, one row per US state / Canadian province, from the registry and the club's portal lists only
    (never guessed). Server roots are the REST roots of usable registry layers, sorted by agency kind."""
    from core import registry
    R = registry.Registry()
    pack = {}
    try: pack = json.load(open(pathlib.Path(__file__).resolve().parents[1] / 'registry' / 'pack_sources.json')).get('portals', {}).get('us_ca', {})
    except (OSError, ValueError): pass
    by = {}
    for s in R.sources:
        a = s.get('area') or ''
        if a[:3] not in ('US-', 'CA-') or R.status(s) not in registry.USABLE: continue
        r = _root(s.get('url'))
        if not r: continue
        ag = (s.get('agency') or '').lower()
        col = ('Parks agency GIS server' if re.search(r'park|recreation|parc', ag) else
               'Wildlife / natural resources GIS server' if re.search(r'wildlife|fish|natural resource|dnr|conservation|environment', ag) else
               'Forestry GIS server' if re.search(r'forest', ag) else 'State GIS server (REST root)')
        d = by.setdefault(a, {'n': 0})
        d['n'] += 1
        d.setdefault(col, [])
        if r not in d[col]: d[col].append(r)
    rows = []
    for a in sorted(set(by) | {('US-' if k.isupper() and len(k) == 2 else '') + k for k in pack}):
        st = a[3:]; d = by.get(a, {'n': 0}); P = pack.get(st) or []
        u = P[0][1] if P else None
        kind = 'ArcGIS Hub' if u and ('opendata.arcgis.com' in u or 'hub.arcgis.com' in u) else ('other' if u else None)
        row = {'Country': a[:2], 'State / province': st, 'What we know already': f"{d['n']} usable outline layers in the engine registry" if d['n'] else None,
               'Main open-data portal URL': u, PORTAL_COLS[4]: kind, 'Search address (tested)': None}
        for c in PORTAL_COLS[6:10]: row[c] = ' ; '.join(d.get(c, [])[:4]) or None
        row['Notes'] = ('Portal from the club source pack. ' if u else '') + 'Server roots = REST roots of registry layers that answered (kpc engine). Search address not tested by the engine.'
        rows.append(row)
    return {'about': 'kpc engine: open-data portals + GIS servers per US state / Canadian province, from the engine registry (not guessed).', 'rows': rows}


def _dump(p, d): p.write_text(json.dumps(d, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- docs-pagefix (round 4 shapes)
def _hb_cfg():
    try: return json.load(open(pathlib.Path(__file__).resolve().parent.parent / 'config' / 'handback.json'))
    except (OSError, ValueError): return {}


def find_workbook(cc, out=None):
    """-> path of the club's hours / fees workbook for 'US' or 'CA', or None. Env KPC_HF_WORKBOOK_<cc> wins."""
    import os
    e = os.environ.get(f'KPC_HF_WORKBOOK_{cc}')
    if e is not None: return e if e and os.path.exists(e) else None
    cfg, here = _hb_cfg(), pathlib.Path(__file__).resolve().parent.parent
    dirs = ([pathlib.Path(out), pathlib.Path(out).parent] if out else []) + [(here / d) for d in cfg.get('workbook_dirs', ['.'])]
    for d in dirs:
        for n in cfg.get('workbook_names', {}).get(cc, []):
            if (d / n).exists(): return str((d / n).resolve())
    return None


_WB = {}


def workbook_map(path):
    """{ref: (excel row, name, column F)} from the Parks sheet (row numbers as Excel shows them: header = row 1)."""
    if not path: return {}
    if path in _WB: return _WB[path]
    cfg = _hb_cfg()
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True)
    ws = wb[cfg.get('sheet', 'Parks')]
    it = ws.iter_rows(values_only=True)
    head = [str(h or '').strip() for h in next(it)]
    ir, inm, iF = (head.index(cfg.get(k, d)) for k, d in (('ref_column', 'Park number'), ('name_column', 'Name'), ('f_column', 'Official park page (start here)')))
    m = {}
    for n, row in enumerate(it, start=2):
        if row and len(row) > ir and row[ir]: m.setdefault(str(row[ir]).strip(), (n, row[inm] or '', row[iF] or ''))
    wb.close(); _WB[path] = m
    return m


def _split_fix(problem):
    """'link wrong/dead; correct official page: <URL>' -> ('link wrong/dead', '<URL>')."""
    m = re.match(r'(.*?);\s*correct official page:\s*(\S+)\s*$', problem or '')
    return (m.group(1).strip(), m.group(2)) if m else ((problem or '').strip(), '')


def _same_url(a, b):
    n = lambda u: re.sub(r'^https?://(www\.)?', '', (u or '').strip().rstrip('/'), flags=re.I).lower()
    return n(a) == n(b)


def pagefix_rows(out):
    """fixes.csv (dead / wrong park pages the docs plug-in proved) -> the two club shapes. Column F is never edited:
    these are leads; chat 11 replaces column F by hand. -> (us_rows, ca_rows, {cc: workbook path or None})."""
    out = pathlib.Path(out)
    fixes = []
    try: fixes = list(csv.DictReader(open(out / 'fixes.csv', newline='')))
    except OSError: pass
    paths = {cc: find_workbook(cc, out) for cc in ('US', 'CA')}
    maps = {cc: workbook_map(p) for cc, p in paths.items()}
    us, ca = [], []
    for fx in fixes:
        ref, area = fx.get('ref') or '', fx.get('area') or ''
        cc = area[:2] if area[:3] in ('US-', 'CA-') else None
        if not cc: continue
        issue, good = _split_fix(fx.get('problem'))
        hit = maps[cc].get(ref)
        tail = f"kpc engine {fx.get('date') or ''}".strip()
        if hit:
            row, nm, F = hit
            old = F or fx.get('link') or ''
            if F and not _same_url(F, fx.get('link')): tail += f"; the engine read {fx.get('link')} (column F holds another URL: check column F by hand)"
        else:
            row, nm, old = f'{ref} ({MAPPING_NEEDED})', '', fx.get('link') or ''
            tail += f'; {MAPPING_NEEDED}'
        park = fx.get('park') or nm
        if cc == 'US': us.append([row, park, old, good, f'{issue} [{tail}]'])
        else: ca.append([row, ref, park, old, issue, good, tail])
    key = lambda r: (isinstance(r[0], str), r[0] if isinstance(r[0], str) else int(r[0]))
    return sorted(us, key=key), sorted(ca, key=key), paths
