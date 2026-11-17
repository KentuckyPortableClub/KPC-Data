#!/usr/bin/env python3
"""Trace hold (KPC owner, 2026-11-17; Handoff 3 proof 4). Offline, on a made-up world in a temp folder (a fake KPC-Data, a fake
KPC-Links with data/fers-approx-outlines.json and a key, a fake store folder, stored tracer outputs):
  1. the chain order: card first (an official record lead stops it, even with a DRAWN trace stored), then a stored trace (held),
     then a picture map waiting for the tracer, then a parcel-tracer input, then the PDF finder - and each park stops at its first answer
  2. stored copy first: stored tracer outputs are held without running a tracer; the finder answers from the docs bot's stored link;
     the whole run makes 0 requests
  3. the hold: held traces sit ONLY in the traces folder in the store's hand-file format (GeoJSON + .kpc-source.json with kind traced,
     tracer, source URL, page, terms; official false, use_for_2fer false); every other file in the world (fers-approx-outlines.json,
     the key, the store folder, KPC-Data) is byte-identical after the run; the guard refuses store / key / 2-fer / site paths and a
     traces folder inside KPC-Links; a do-not-share source is "private input, not saved here"; WDPA is never a source
  4. the receipt: written, parks tried = cards made = parks asked, held / found / stored / requests / POTA request count (0)
  5. prune: a park that gets an official outline loses its held trace
  6. the workflow: by hand only (no schedule, no workflow_run, never starts another run), never pushes main, never writes KPC-Links,
     red without a receipt; the existing kpc-picture-trace.yml is unchanged against main
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import csv, hashlib, json, os, pathlib, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
FX = ROOT / 'tests/fixtures/trace-hold-nov17'
sys.path.insert(0, str(S))
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k): raise OSError('test: no network')
socket.socket.connect = _no_net

import kpc_trace_hold as H  # noqa: E402


def sq(lon, lat, d=0.01):
    return {'type': 'Polygon', 'coordinates': [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]]}


def snapshot(root, skip):
    out = {}
    for p in sorted(pathlib.Path(root).rglob('*')):
        if p.is_file() and not any(str(p).startswith(str(s)) for s in skip): out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def build_world(w):
    w = pathlib.Path(w)
    pins = {f'US-90{i:02d}': [37.0 + i / 10, -85.0 - i / 10] for i in range(10)}
    names = {'US-9000': 'Alder Pond Park', 'US-9001': 'Birch Ridge Natural Area', 'US-9002': 'Cedar Bend Park', 'US-9003': 'Dogwood Lake Park',
             'US-9004': 'Elm Creek Wildlife Area', 'US-9005': 'Fir Hollow Park', 'US-9006': 'Gum Swamp Park', 'US-9007': 'Hickory Knob Park',
             'US-9008': 'Ivy Glen Park', 'US-9009': 'Juniper Flat Park'}
    data = w / 'kpcdata'; (data / 'data/parkinfo').mkdir(parents=True); (data / 'data/docs').mkdir(parents=True); (data / '.github').mkdir()
    (data / 'data/parkinfo/US-ZZ.json').write_text(json.dumps({'parks': {r: [names[r], f'https://parks.example.gov/{r.lower()}', 'State Park', '', '', pins[r][0], pins[r][1]] for r in pins}}))
    (data / 'data/docs/US-ZZ.json').write_text(json.dumps({'parks': {'US-9007': {'page': 'https://parks.example.gov/us-9007', 'agency': 'Example Parks',
                                                                                  'map': {'url': 'https://parks.example.gov/maps/hickory-knob-map.pdf'}}}}))
    links = w / 'links'; (links / 'data/us-key').mkdir(parents=True); (links / '.github/scripts').mkdir(parents=True)
    (links / '.github/scripts/kpc_fers.py').write_text('# stub\n')
    (links / 'data/fers-approx-outlines.json').write_text(json.dumps({'outlines': [{'ref': 'US-1234', 'grade': 'approximate (picture map)'}]}, indent=1) + '\n')
    (links / 'data/us-key/US-ZZ.json').write_text(json.dumps({'parks': {'US-0001': {'g': 'official'}}}))
    (links / 'data/us-key/why-not.json').write_text(json.dumps({'parks': {r: {'st': 'ZZ', 'tag': 'no-layer'} for r in pins}}))
    store = w / 'store/store-data/gis-list'; store.mkdir(parents=True); (store / 'TODO.csv').write_text('ref\nUS-9001\n')
    pic = w / 'pictraced'; (pic / 'debug').mkdir(parents=True)
    rows = []
    for r, st, src in (('US-9000', 'DRAWN', 'https://parks.example.gov/maps/alder.pdf'), ('US-9001', 'DRAWN', 'https://parks.example.gov/maps/birch.pdf'),
                       ('US-9002', 'NO FIT', 'https://parks.example.gov/maps/cedar.pdf'), ('US-9008', 'DRAWN', 'https://www.protectedplanet.net/x.pdf')):
        rows.append({'ref': r, 'status': st, 'source_url': src, 'page': '1', 'acres_traced': '250.0'})
        if st == 'DRAWN':
            (pic / f'{r}.json').write_text(json.dumps({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': sq(pins[r][1], pins[r][0]),
                'properties': {'ref': r, 'source_url': src, 'page': 1, 'area_acres': 250.0, 'tool': 'kpc_trace_picture.py 0.2.0', 'fit_m': 21.0,
                               'method': 'boundary by Lab k-means; control points: LSD junctions matched', 'use_for_2fer': False, 'official': False}}]}))
    with open(pic / 'report.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['ref', 'status', 'source_url', 'page', 'acres_traced']); wr.writeheader(); wr.writerows(rows)
    (pic / 'debug/US-9001_1_boundary.jpg').write_bytes(b'\xff\xd8\xff\xe0' + b'0' * 200)
    par = w / 'parcel/parcels'; par.mkdir(parents=True)
    feats = [{'type': 'Feature', 'geometry': sq(pins[r][1], pins[r][0], 0.005), 'properties': {'ref': r, 'acres': 60.0, 'pin_dist_m': 0,
              'layer_url': 'https://gis.example.gov/arcgis/rest/services/Parcels/MapServer/0', **({'terms': 'do not share: licensed to the club only'} if r == 'US-9006' else {})}}
             for r in ('US-9005', 'US-9006')]
    (par / 'US-ZZ.json').write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}))
    with open(par / 'report.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['ref', 'status', 'acres']); wr.writeheader()
        wr.writerows([{'ref': 'US-9005', 'status': 'DRAWN', 'acres': '60'}, {'ref': 'US-9006', 'status': 'DRAWN', 'acres': '60'}])
    pm = w / 'pm'; pm.mkdir()
    (pm / 'index.json').write_text(json.dumps({'maps': [{'ref': 'US-9003', 'source_url': 'https://parks.example.gov/maps/dogwood.pdf', 'page': [1], 'agency': 'Example Parks'},
                                                         {'ref': 'US-9001', 'source_url': 'https://parks.example.gov/maps/birch.pdf', 'page': [1], 'agency': 'Example Parks'}]}))
    (w / 'parcel-parks.json').write_text(json.dumps([{'ref': 'US-9004'}]))
    (w / 'extra.csv').write_text('ref,name,checked,cand_name,cand_km,cand_acres,official_acres\nUS-9000,Alder Pond Park,2026-11-10,Alder Pond Park,0,100,104\n')
    (w / 'asks.json').write_text(json.dumps({'made': '2026-11-17', 'parks': [{'ref': r, 'area': 'US-ZZ', 'name': names[r], 'ask': 'no official record'} for r in sorted(pins)]}))
    return w


def args(w, **kw):
    import argparse
    a = argparse.Namespace(asks=str(w / 'asks.json'), areas='', data=str(w / 'kpcdata'), links=str(w / 'links'), extra=str(w / 'extra.csv'),
                           picture_maps=str(w / 'pm'), picture_traced=str(w / 'pictraced'), parcel_traced=str(w / 'parcel'),
                           parcel_input=str(w / 'parcel-parks.json'), traces=str(w / 'traces'), receipt=str(w / 'receipt.json'),
                           today='2026-11-17', checked_default='2026-11-11', finder='yes', finder_queue=str(w / 'queue'),
                           settings=str(FX / 'fetch-settings.json'), blocked=str(FX / 'extra-blocked-hosts.txt'), disallowed=str(FX / 'robots-disallowed-layers.csv'),
                           saved=None, dry_run=False, park_max=6)
    for k, v in kw.items(): setattr(a, k, v)
    return a


with tempfile.TemporaryDirectory() as td:
    w = build_world(td)
    before = snapshot(w, [w / 'traces', w / 'queue', w / 'receipt.json'])
    os.environ['KPC_FINDER_SEARCH_URL'] = ''
    import kpc_pdf_finder as PF

    class NoNet:   # the finder's door: any live request would be recorded here
        stat = {'requests': 0}; calls = []
        def get(self, u, **k): NoNet.calls.append(u); return 'err:test', {}, b'', u
        def robots_ok(self, u): NoNet.calls.append('robots ' + u); return True
        def resting(self): return {}
    a = args(w)
    F = PF.Finder(PF.load_settings(a.settings), PF.load_blocked_hosts(a.blocked), PF.load_disallowed_layers(a.disallowed), PF.SavedCopies(None),
                  manners=NoNet(), portals={}, search_url='', picture_maps=H.picture_maps_index(a.picture_maps), docs_dir=os.path.join(a.data, 'data/docs'), today=a.today)
    R = H.Run(a); rec = R.run(F); F.write(a.finder_queue)
    open(a.receipt, 'w').write(H.jdump(rec))
    P = R.paths
    print('chain paths: ' + json.dumps(P))
    check('1. US-9000: card first - an official record lead (PROPOSE JOIN) stops the chain; its stored DRAWN trace is NOT held',
          P['US-9000'] == ['card', 'official record lead'] and not (w / 'traces/US-ZZ/US-9000.geojson').exists())
    check('1. US-9001: stored picture trace -> held', P['US-9001'] == ['card', 'stored trace', 'held'])
    check('1. US-9003: picture map on picture-maps, no trace yet -> to the picture tracer (the finder is not asked)', P['US-9003'] == ['card', 'picture map to trace'])
    check('1. US-9004: parcel-tracer input -> to the parcel tracer', P['US-9004'] == ['card', 'parcel input to trace'])
    check('1. US-9005: stored parcel trace -> held', P['US-9005'] == ['card', 'stored trace', 'held'])
    check('1. US-9007: nothing stored -> the PDF finder last (queued from the stored docs link)', P['US-9007'] == ['card', 'finder', 'queued'])
    check('1. US-9002: a stored NO FIT does not stop the chain; it goes on to the finder', P['US-9002'][-2:] == ['finder', 'nothing'] and 'stored trace (not drawn' in P['US-9002'][1])
    pages = sorted(c for c in NoNet.calls if not c.startswith('robots '))
    check(f'2. stored copy first: parks with a stored answer never reach the door; only the two with nothing stored do ({pages}); no tracer was run',
          pages == ['https://parks.example.gov/us-9002', 'https://parks.example.gov/us-9009'] and rec['requests_made'] == 0)
    check(f"2. served from stored copies: {rec['served_from_stored_copy']} (4 stored DRAWN traces + 1 stored NO FIT + 1 picture map + 1 docs-bot map link)",
          rec['served_from_stored_copy'] == 7)
    q = json.load(open(w / 'queue/queue.json'))
    check('2. the finder queued the stored docs-bot link with its park ref', [x['url'] for x in q] == ['https://parks.example.gov/maps/hickory-knob-map.pdf'] and q[0]['found_by'] == 'stored')
    after = snapshot(w, [w / 'traces', w / 'queue', w / 'receipt.json'])
    check(f'3. every file outside the traces folder is byte-identical after the run ({len(before)} files: fers-approx-outlines.json, the key, the store folder, KPC-Data)',
          before == after and 'links/data/fers-approx-outlines.json' in after and 'store/store-data/gis-list/TODO.csv' in after)
    held = sorted(str(p.relative_to(w / 'traces')) for p in (w / 'traces').rglob('*') if p.is_file())
    check(f'3. held files ({held})', held == ['US-ZZ/US-9001.geojson', 'US-ZZ/US-9001.jpg', 'US-ZZ/US-9001.kpc-source.json',
                                              'US-ZZ/US-9005.geojson', 'US-ZZ/US-9005.kpc-source.json', 'US-ZZ/US-9005.svg', 'index.json'])
    note = json.load(open(w / 'traces/US-ZZ/US-9001.kpc-source.json'))
    check(f"3. .kpc-source.json: kind traced, tracer, source URL, page, terms ({note['kind']}, {note['tracer']}, {note['source_url']}, page {note['page']})",
          note['kind'] == 'traced' and note['tracer'].startswith('kpc_trace_picture.py') and note['source_url'].endswith('birch.pdf') and note['page'] == 1
          and note['terms'] and note['official'] is False and note['use_for_2fer'] is False and note['held'] is True)
    gj = json.load(open(w / 'traces/US-ZZ/US-9005.geojson'))['features'][0]['properties']
    check('3. the held GeoJSON says approximate, held, official false, use_for_2fer false', gj['held'] and gj['official'] is False and gj['use_for_2fer'] is False and 'approximate' in gj['grade'])
    idx = {r['ref']: r for r in json.load(open(w / 'traces/index.json'))['rows']}
    need = {'source_map', 'page', 'method', 'traced_acres', 'official_acres', 'pin_inside', 'picture', 'review'}
    check(f"3. review rows carry the reviewer's fields ({sorted(idx['US-9001'])})", set(idx) == {'US-9001', 'US-9005'} and need <= set(idx['US-9001'])
          and idx['US-9001']['pin_inside'] is True and idx['US-9005']['method'] == 'parcel trace' and idx['US-9001']['traced_acres'] == 250.0)
    nh = {x['ref']: x['why'] for x in rec['not_held']}
    check(f"3. a do-not-share source: 'private input, not saved here' ({nh.get('US-9006')})", 'private input, not saved here' in nh.get('US-9006', '') and rec['private_not_saved'] == 1
          and not (w / 'traces/US-ZZ/US-9006.geojson').exists())
    check(f"3. WDPA is never a source ({nh.get('US-9008')})", 'WDPA' in nh.get('US-9008', '') and not (w / 'traces/US-ZZ/US-9008.geojson').exists())
    for bad in ('data/fers-approx-outlines.json', 'US-ZZ/../../links/data/fers-approx-outlines.json', 'data/us-key/US-ZZ.json', 'store-data/gis-list/TODO.csv',
                'index.html', 'locations-pota.json', 'tracer-inputs.csv', 'data/waiting/in/x.json'):
        try: R.W.write(bad, '{}'); check(f'3. the guard refuses {bad}', False)
        except H.HoldRefused: check(f'3. the guard refuses {bad}', True)
    for root in (w / 'links' / 'held', w / 'kpcdata' / 'held'):
        try: H.HoldWriter(root); check(f'3. a traces folder inside {root.parent.name} is refused', False)
        except H.HoldRefused: check(f'3. a traces folder inside {root.parent.name} is refused', True)
    r2 = json.load(open(a.receipt))
    check(f"4. receipt: asked {r2['parks_asked']}, tried {r2['parks_tried']}, cards {r2['cards_made']}, found {r2['outlines_found']}, held {r2['outlines_held']}, "
          f"requests {r2['requests_made']}, stored {r2['served_from_stored_copy']}, POTA requests {r2['pota_requests']}",
          r2['parks_asked'] == r2['parks_tried'] == r2['cards_made'] == 10 and r2['outlines_found'] == 4 and r2['outlines_held'] == 2
          and r2['pota_requests'] == 0 and 'pota_requests' in r2['finder'] and r2['held_by_method'] == {'picture trace': 1, 'parcel trace': 1})
    check('4. the receipt names the list it ran on', r2['list_source'])
    # receipt through the command line, dry run, into a scratch folder
    r = subprocess.run([sys.executable, '-B', str(S / 'kpc_trace_hold.py'), 'run', '--asks', a.asks, '--data', a.data, '--links', a.links,
                        '--picture-maps', a.picture_maps, '--picture-traced', a.picture_traced, '--parcel-traced', a.parcel_traced,
                        '--traces', str(w / 'dry'), '--receipt', str(w / 'dry-receipt.json'), '--dry-run', '--today', '2026-11-17'], capture_output=True, text=True)
    dr = json.load(open(w / 'dry-receipt.json')) if (w / 'dry-receipt.json').exists() else {}
    check(f"4. the command line writes the receipt (exit {r.returncode}; {r.stdout.strip()[-120:]})", r.returncode == 0 and dr.get('dry_run') is True and dr.get('parks_tried') == 10
          and dr.get('requests_made') == 0 and dr.get('pota_requests') == 0)
    # 5. prune
    (w / 'links/data/us-key/US-ZZ.json').write_text(json.dumps({'parks': {'US-9001': {'g': 'official'}}}))
    gone = H.prune(w / 'traces', w / 'links')
    idx2 = {x['ref'] for x in json.load(open(w / 'traces/index.json'))['rows']}
    check(f'5. prune: US-9001 got an official outline, its held trace is deleted ({gone})', gone == ['US-9001'] and idx2 == {'US-9005'}
          and not (w / 'traces/US-ZZ/US-9001.geojson').exists() and not (w / 'traces/US-ZZ/US-9001.jpg').exists())

# 6. the workflow
wf = (ROOT / '.github/workflows/kpc-trace-hold.yml').read_text(encoding='utf-8')
on = wf.split('\non:', 1)[1].split('\npermissions:', 1)[0]
check('6. kpc-trace-hold.yml is by hand only: workflow_dispatch, no schedule, no workflow_run, no push trigger',
      'workflow_dispatch' in on and 'schedule' not in on and 'workflow_run' not in on and 'push:' not in on and 'cron' not in wf)
check('6. it never starts another run (no gh workflow run, no dispatches API)', 'gh workflow run' not in wf and 'dispatches' not in wf and 'gh api' not in wf)
check('6. it never pushes main and never writes KPC-Links (KPC-Links checked out read-only, no fers-approx-outlines.json in it)',
      'push_retry.sh main' not in wf and 'HEAD:main' not in wf and 'persist-credentials: false' in wf
      and not __import__('re').search(r'cd (\.\./)?links|-C (\.\./)?links|>\s*(\.\./)?links/', wf))
check('6. it saves only to the traces, intake-files and picture-maps branches', set(__import__('re').findall(r'kpc_push_retry\.sh (\S+)', wf)) == {'traces', 'intake-files', 'picture-maps'})
check('6. no receipt = red', 'no receipt: red' in wf and 'exit 1' in wf)
check('6. the default is a dry run', "dry_run:\n        description: 'yes = no request at all and nothing saved (counts and a receipt only)'\n        default: 'yes'" in wf)
try:
    d = subprocess.run(['git', 'diff', '--name-only', 'origin/main', '--', '.github/workflows/kpc-picture-trace.yml', 'data/'], cwd=ROOT, capture_output=True, text=True, timeout=60)
    if d.returncode == 0: check(f'6. kpc-picture-trace.yml (and its schedule) and data/** unchanged against main ({d.stdout.strip() or "no diff"})', not d.stdout.strip())
    else: print('NOTE: no origin/main here; compared in the PR')
except Exception as e:  # noqa: BLE001
    print(f'NOTE: git not available ({e})')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
