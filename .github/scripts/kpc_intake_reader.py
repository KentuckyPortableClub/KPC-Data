#!/usr/bin/env python3
"""ONE INTAKE READER FOR EVERY BOT (chat 10, Oct 31 2026; HQ 7:55 PM, Brandon 'set the bot to pull it up': automation first, no
hand-feeding). HQ drops outside-research files on the KPC-Data branch `intake-files`; each bot, at the start of its run, calls

    python3 .github/scripts/kpc_intake_reader.py <kind> [--all]

which fetches the branch, picks the files of ITS kind, converts a workbook (.xlsx) to the same JSON when needed, and writes them to
data/intake/_in/<kind>/ (a working folder: never committed, BRANCH FIRST). A seen list (data/intake/intake-seen.json:
kind -> {file: git blob id}) makes each NEW or RE-SENT file count as new once; the bot reads every file of its kind every run
anyway (resume-safe), so --all is the default. One status-board line per new file. Prints NEW=<files> and FILES=<files>. Never fails.

Kinds (file name patterns on intake-files):
  camping    camping-*.json                         -> campground info bot (sources)
  parking    parking-hunt-*.json                    -> access bot (point layers)
  docs       docs-found-*.json / docs-found-*.xlsx  -> documents merge (an .xlsx is converted unless its .json twin exists)
  convert    world-sources-*.json, leads-*.json     -> map-format converter ('other' / 'other_layer' leads)
  layers     external-sources-*.json, world-sources-*.json -> layer collector ('rest' + Parks|/Trail| rows)
  questions  pins-check-*.json, ca-name-mismatch-*.json -> data/intake/_in/questions/ for chat 2 / chat 11 (listed on the board)
  hours      hours-fees-*.json                      -> saved only (Kentucky-only scope)
  acres      acres-*.json                           -> the acres bot (official sizes by agency)
  portals    portals-*.json                         -> the GIS finders' portal search + state-gis.json
"""
import datetime as dt, json, os, pathlib, re, subprocess, sys

KINDS = {
    'camping': [r'^camping-.*\.json$'],
    'parking': [r'^parking-hunt-.*\.json$'],
    'docs': [r'^docs-found-.*\.(json|xlsx)$', r'^docs-pagefix-.*\.csv$'],
    'convert': [r'^world-sources-.*\.json$', r'^leads-.*\.json$'],
    'layers': [r'^external-sources-.*\.json$', r'^world-sources-.*\.json$'],
    'questions': [r'^pins-check-.*\.json$', r'^ca-name-mismatch-.*\.json$'],
    'hours': [r'^hours-fees-.*\.(json|xlsx)$', r'^hours-fees-blocked-.*\.csv$'],   # Nov 1: the outside hours / fees workbooks -> the outside-KY trial (kpc_hours_bot.py HOURS_WB)
    'acres': [r'^acres-.*\.json$'],        # Oct 31 9:40 PM: official acres by agency -> the acres bot (data/acres.json, waiting room)
    'portals': [r'^portals-.*\.json$'],
    'files': [r'^file-.*\.(geojson|json|zip|geojson\.gz)$'],   # Nov 1: boundary files a person downloaded by hand -> the layer collector (handfiles)
    'hardlook': [r'^hardlook-.*\.(json|xlsx)$'],   # Nov 1: Brandon's Canada Hard Look rows -> kpc_hardlook.py (questions for chat 11)    # Oct 31 9:30 PM: open-data portals -> the GIS finders + data/state-gis.json (waiting room)
}
SEEN = pathlib.Path('data/intake/intake-seen.json')



def _openpyxl():
    """Nov 2: GitHub's runners have no openpyxl, so every workbook (the whole US Hard Look, Canada Nov 1, the mapping rounds,
    hours) was silently skipped. Installed on first use."""
    try:
        import openpyxl
    except ImportError:
        import importlib, site
        for cmd in ([sys.executable, '-m', 'pip', 'install', '-q', 'openpyxl'], [sys.executable, '-m', 'pip', 'install', '-q', '--user', '--break-system-packages', 'openpyxl'],
                    ['sudo', 'apt-get', 'install', '-y', '-qq', 'python3-openpyxl']):
            try:
                if subprocess.run(cmd, capture_output=True, timeout=300).returncode == 0: break
            except Exception: pass  # noqa: BLE001
        for d in [site.getusersitepackages(), '/usr/lib/python3/dist-packages']:   # a --user / apt install is not on this run's path yet
            if d not in sys.path: sys.path.append(d)
        importlib.invalidate_caches()
        import openpyxl
    return openpyxl

def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout


def xlsx_to_docs(path):
    """The documents workbook (sheet 'Parks') -> docs-found JSON {ref: {st, page, map, map_page, kind, date, agency, notes}}."""
    openpyxl = _openpyxl()
    ws = openpyxl.load_workbook(path, read_only=True)['Parks']; it = ws.iter_rows(values_only=True); H = next(it); ix = {h: i for i, h in enumerate(H)}
    col = lambda r, n: r[ix[n]] if n in ix else None
    out = {}
    for r in it:
        ref = col(r, 'Park number')
        if not ref: continue
        page, m = str(col(r, 'Official park page') or ''), str(col(r, 'Official map URL') or '')
        page, m = (page if page.startswith('http') else ''), (m if m.startswith('http') else '')
        if not (page or m): continue
        out[ref] = {'st': col(r, 'State / prov'), 'page': page, 'map': m, 'map_page': col(r, 'Map page #') or 1, 'kind': col(r, 'Map kind (PDF / IMAGE / MAP PAGE)') or '',
                    'date': col(r, 'Map date'), 'agency': col(r, 'Agency') or '', 'notes': str(col(r, 'Notes') or '')[:300]}
    return out


def xlsx_to_hours(path):
    """The hours / fees workbook (sheet 'Parks', yellow columns H-P filled by outside research) -> {ref: {st, page, hours_page,
    hours, season, fees_page, fees, pass, closures_page, status, notes}}. Values stay as the researcher wrote them: the hours bot
    reads the PAGES itself; the words ride along for chat 11 to compare (Nov 1, chat 10)."""
    openpyxl = _openpyxl()
    ws = openpyxl.load_workbook(path, read_only=True)['Parks']; it = ws.iter_rows(values_only=True); H = next(it)
    ix = {str(h or '').strip(): i for i, h in enumerate(H)}
    def col(r, *names):
        for n in names:
            for h, i in ix.items():
                if h.lower().startswith(n.lower()) and i < len(r): return r[i]
        return None
    url = lambda v: (str(v) if str(v or '').startswith('http') else '')
    txt = lambda v: '' if v is None or str(v).strip().lower() in ('none', 'not stated on the agency page') else str(v)[:400]
    out = {}
    for r in it:
        ref = col(r, 'Park number')
        if not ref: continue
        row = {'st': col(r, 'State / prov'), 'page': url(col(r, 'Official park page')), 'hours_page': url(col(r, 'HOURS page')),
               'hours': txt(col(r, 'Hours (as')), 'season': txt(col(r, 'Open season')), 'fees_page': url(col(r, 'FEES page')), 'fees': txt(col(r, 'Fees (as')),
               'pass': txt(col(r, 'Pass accepted')), 'closures_page': url(col(r, 'CLOSURES')), 'status': str(col(r, 'Status') or ''), 'notes': txt(col(r, 'Notes'))[:300]}
        if any(row[k] for k in ('page', 'hours_page', 'fees_page', 'hours', 'fees', 'closures_page')): out[str(ref)] = row
    return out


def xlsx_to_hardlook(path):
    """A Hard Look workbook (every sheet with a 'Park number' column; US = 4 tabs, Canada = 'Parks') -> {about, rows: {ref: {...}}}."""
    openpyxl = _openpyxl()
    wb = openpyxl.load_workbook(path, read_only=True); rows = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True); H = next(it, None) or ()
        if 'Park number' not in H: continue
        ix = {h: i for i, h in enumerate(H) if h}
        col = lambda r, pre: next((r[i] for h, i in ix.items() if str(h).startswith(pre) and i < len(r)), None)
        for r in it:
            ref = str(col(r, 'Park number') or '').strip()
            if not re.match(r'^[A-Z]{2}-\d+', ref): continue
            g = lambda pre: '' if col(r, pre) is None else str(col(r, pre)).strip()
            rows[ref] = {'st': g('State / prov'), 'name': g('Name'), 'lat': col(r, 'Pin lat'), 'lon': col(r, 'Pin lon'), 'status': g('Status'), 'kind': g('Kind'),
                         'url': g('NEW official layer'), 'field': g('Name field'), 'record': g('Record id / name'), 'notes': g('Notes')[:1500], 'agency': g('Agency'),
                         'page': g('Official park page'), 'tab': ws.title}
    return {'about': 'Hard Look workbook rows (outside research), converted by the intake reader', 'rows': rows}


def pagefix_to_docs(csv_blob, n, files):
    """docs-pagefix-<x>.csv (outside research: dead / moved / wrong official pages with the correct URL) -> docs-found-pagefix-<x>.json
    {ref: {st, page, old_page, replace_page: true, notes}}. The US csv names the row of hours-fees-<x>.xlsx (sheet Parks); Canada names the ref."""
    import csv, io
    sfx = n[len('docs-pagefix-'):-4]; R = list(csv.DictReader(io.StringIO(csv_blob.decode('utf-8-sig', 'replace'))))
    byrow = {}
    if R and not any('POTA ref' in k for k in R[0]):
        hf = f'hours-fees-{sfx}.xlsx'
        if hf in files:
            import openpyxl, tempfile
            t = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False); t.write(subprocess.run(['git', 'cat-file', 'blob', files[hf]], capture_output=True).stdout); t.close()
            ws = openpyxl.load_workbook(t.name, read_only=True)['Parks']
            for i, r in enumerate(ws.iter_rows(values_only=True), 1): byrow[str(i)] = (str(r[1] or ''), str(r[0] or ''))
    try: CA = {k: v[10] for k, v in (json.load(open('data/parkinfo/CA.json')).get('parks') or {}).items() if isinstance(v, list) and len(v) > 10}
    except Exception: CA = {}  # noqa: BLE001
    out = {}
    for r in R:
        ref = r.get('POTA ref') or byrow.get(str(r.get('row')), ('', ''))[0]
        st = byrow.get(str(r.get('row')), ('', ''))[1] or CA.get(ref, '')
        new = (r.get('correct official URL (if found)') or r.get('correct URL') or '').strip()
        if not ref or not new.startswith('http') or re.search(r'wikipedia\.org|tripadvisor|alltrails|google\.', new, re.I): continue
        out[ref] = {'st': st or '', 'page': new, 'old_page': r.get('column F URL') or r.get('old F URL') or '', 'replace_page': True,
                    'notes': ('page fix: ' + (r.get('issue') or r.get('why column F was replaced') or '') + ' ' + (r.get('note') or '')).strip()[:300]}
    return out


def parking_layers(cfg_path):
    """The access bot's helper: every parking-hunt file's agency-wide point layers -> extra entries in the (working, uncommitted)
    data/access-layers.json, one per state / province the file says the layer covers (by place only + the layer's type field)."""
    import collections, glob as G
    cfg = json.load(open(cfg_path)); L = cfg['layers']; have = {(x['url'].rstrip('/'), x['st']) for x in L}; n = 0
    for f in sorted(G.glob('data/intake/_in/parking/parking-hunt-*.json')):
        H = json.load(open(f)); sts = collections.defaultdict(set)
        for v in (H.get('rows') or {}).values():
            u = str(v.get('Parking / access layer URL') or '').rstrip('/'); s_ = str(v.get('State / province') or '')
            if u and s_: sts[u].add(s_[3:] if s_.startswith('US-') else s_)
        for u, meta in (H.get('layers') or {}).items():
            u = u.rstrip('/')
            if not re.search(r'/(MapServer|FeatureServer)/\d+$', u): continue
            m = re.match(r'\s*([A-Za-z0-9_]+)', str(meta.get('field') or ''))
            for st in sorted(sts.get(u, ())):
                if (u, st) in have: continue
                L.append({'prog': 'parking hunt (' + pathlib.Path(f).stem + ')', 'st': st, 'url': u, 'what': 'points: parking / access / facility (agency-wide)',
                          'typef': m.group(1) if m else 'none (layer = type)', 'vals': str(meta.get('field') or '')[:200], 'area': 'none (location only)',
                          'count': str(meta.get('parks') or ''), 'tested': 'outside research (the bot\'s own place test decides)', 'licence': 'see the agency',
                          'agency': str(meta.get('agency') or '')[:150]})
                have.add((u, st)); n += 1
    json.dump(cfg, open(cfg_path, 'w'), indent=1, ensure_ascii=False)
    print(f'::notice title=Intake reader (parking)::{n} layer-by-state entries added for this run')


def main():
    a = sys.argv[1:]
    if a[:1] == ['parking-layers']: parking_layers(a[1]); return
    kind = a[0] if a else ''
    if kind not in KINDS: print(f'usage: kpc_intake_reader.py <{"|".join(KINDS)}>'); return
    git('fetch', '-q', 'origin', '+refs/heads/intake-files:refs/remotes/origin/intake-files')
    lst = [l.split('\t') for l in git('ls-tree', 'origin/intake-files').splitlines() if '\t' in l]
    files = {name: meta.split()[2] for meta, name in lst}
    pick = sorted(n for n in files if any(re.match(p, n) for p in KINDS[kind]))
    if kind in ('docs', 'hardlook', 'hours'):   # an .xlsx whose .json twin is there is skipped (the JSON was made from it)
        pick = [n for n in pick if not (n.endswith('.xlsx') and n[:-5] + '.json' in files)]
    out = pathlib.Path('data/intake/_in') / kind; out.mkdir(parents=True, exist_ok=True)
    try: seen = json.load(open(SEEN))
    except Exception: seen = {}  # noqa: BLE001
    S = seen.setdefault(kind, {}); new = []
    for n in pick:
        blob = subprocess.run(['git', 'cat-file', 'blob', files[n]], capture_output=True).stdout
        if n.endswith('.xlsx'):
            tmp = out / n; tmp.write_bytes(blob)
            try: json.dump({'hardlook': xlsx_to_hardlook, 'hours': xlsx_to_hours}.get(kind, xlsx_to_docs)(tmp), open(out / (n[:-5] + '.json'), 'w'), ensure_ascii=False)
            except Exception as e: print(f'::warning title=Intake reader::{n}: workbook not read ({type(e).__name__}: {e})')  # noqa: BLE001
            tmp.unlink(missing_ok=True)
        elif kind == 'files' and n.endswith('.zip'):
            tmp = out / n; tmp.write_bytes(blob)
            try:
                sys.path.insert(0, str(pathlib.Path(__file__).parent)); import kpc_handfile_convert as HC   # pure Python: no outside libraries
                m_ = re.match(r'^file-((?:US|CA)-[A-Z]{2}|[A-Z]{2})-(.+)\.zip$', n)
                print(f'::notice title=Intake reader::{n}: ' + ', '.join(f'{a} ({b} areas)' for a, b, _ in HC.convert(tmp, m_.group(1), out, m_.group(2))))
            except Exception as e: print(f'::notice title=Intake reader::{n}: zip not converted ({type(e).__name__}: {e})')  # noqa: BLE001
            tmp.unlink(missing_ok=True)
        elif n.startswith('docs-pagefix-'):
            try: json.dump(pagefix_to_docs(blob, n, files), open(out / ('docs-found-pagefix-' + n[len('docs-pagefix-'):-4] + '.json'), 'w'), ensure_ascii=False)
            except Exception as e: print(f'::notice title=Intake reader::{n}: page fixes not read ({type(e).__name__}: {e})')  # noqa: BLE001
        else:
            (out / n).write_bytes(blob)
        if S.get(n) != files[n]:
            new.append(n); S[n] = files[n]
            try: subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', f'Intake: {n}', 'green', f'read by the {kind} bot ({dt.date.today()})', 'the bot sends what it finds through the waiting room'], capture_output=True, timeout=60)
            except Exception: pass  # noqa: BLE001
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    json.dump(seen, open(SEEN, 'w'), indent=1)
    print(f'::notice title=Intake reader ({kind})::{len(pick)} file(s) on intake-files, {len(new)} new: {" ".join(new) or "-"}')
    print('NEW=' + ' '.join(new)); print('FILES=' + ' '.join(sorted(p.name for p in out.iterdir())))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Intake reader::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
