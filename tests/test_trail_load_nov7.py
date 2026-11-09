#!/usr/bin/env python3
"""Nov 7 2026 (Brandon 9 PM CST: 'build the rest of it so that dont get forgot about'). Fails if any of the 243 trail parks has no
trail status in the outline-source ledger, if any wired park is not loaded (ArcGIS rows handed to the trail bot; file-based extracts
present as data/trails/<ref>.json plus the intake geojson), or if the trail matcher would fetch our own intake file over the web.
Also covers newly accepted Research wires. Offline."""
import csv, gzip, json, os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILS = []


def check(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: FAILS.append(m)


O = ROOT / 'data/waiting/outline-sources'
rows = json.loads(gzip.open(O / 'ledger.json.gz').read())['rows']
parks = list(csv.DictReader(open(ROOT / '.github/scripts/draft/tools/kpc_layers_nov7/inputs/kpc-pota-trail-parks-no-outline-nov7.csv', encoding='utf-8')))
st = {}
for p in parks:
    s = [(v.get('trail') or {}).get('status') for k, v in rows.items() if k == p['ref'] or k.startswith(p['ref'] + '|')]
    st[p['ref']] = next((x for x in s if x), None)
KNOWN = {'trail line wired', 'blocked host (robots)', 'nothing found', 'rejected', 'conditional', 'kept current line', 'open (point only)', 'check'}
check(len(parks) == 243 and all(st.values()), f'all {len(parks)} trail parks have a trail status (missing {[r for r, s in st.items() if not s][:5]})')
check(set(st.values()) <= KNOWN, f'statuses are known {sorted(set(map(str, st.values())))}')
wired_rows = list(csv.DictReader(open(O / 'trail-lines-wired-nov7.csv', encoding='utf-8')))
wired = {w['ref'] for w in wired_rows}
led_wired = {r for r, s in st.items() if s == 'trail line wired'}
# Nov 8: ledger trail status is keyed to the Nov 7 243-park list; later wires may sit only in the CSV.
check(led_wired <= wired, f'every 243-list park marked trail line wired is in the wired CSV ({len(led_wired)} / {len(wired)})')

ORIG12 = {'US-11953', 'US-8316', 'US-9163', 'US-10880', 'US-10884', 'US-10929',
          'US-10423', 'US-10714', 'US-10862', 'US-10900', 'CA-5506', 'CA-5993'}
check(ORIG12 <= wired, f'original 12 wired parks stay loaded (missing {sorted(ORIG12 - wired)})')

# Newly accepted Research wires that must stay loaded (ArDOT + USGS/FS/municipal file extracts).
RESEARCH = {'US-9681', 'US-10426', 'US-13622', 'US-5749', 'US-7973', 'US-10398', 'US-13626',
            'US-11815', 'US-13206', 'US-13214', 'US-9203', 'US-5841', 'US-11004', 'US-11176',
            'US-10508', 'US-13623', 'US-11730', 'US-0877', 'US-0887', 'US-0892', 'US-3382',
            'US-11852', 'US-10430', 'US-0642'}
# US-0642 Natchez is wired only after the MS/AL extract lands; the test accepts either wired or a reviewed note so a later
# follow-up cannot silently drop a completed wire.
check(RESEARCH <= wired, f'Research accepted wires are loaded (missing {sorted(RESEARCH - wired)})')

def is_arcgis(w):
    u = (w.get('layer_url') or '').rstrip('/')
    return u.startswith('https://') and u.rsplit('/', 1)[-1].isdigit()

def is_file(w):
    return (w.get('layer_url') or '').startswith('file:')

arc = [w for w in wired_rows if is_arcgis(w)]
fil = [w for w in wired_rows if is_file(w)]
check(all(is_arcgis(w) or is_file(w) for w in wired_rows), 'every wired row is an ArcGIS layer or a file: extract')

with tempfile.TemporaryDirectory() as d:
    out = pathlib.Path(d) / 'x.json'
    subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_wired_trails.py'), str(out)], env={**os.environ, 'DATA': str(ROOT)}, check=False)
    got = {x['ref']: x for x in json.load(open(out))}
check({w['ref'] for w in arc} <= set(got), f'every ArcGIS wired park goes to the trail bot (missing {sorted({w["ref"] for w in arc} - set(got))})')
check(all(x.get('where', '').count("'") >= 2 and x.get('url', '').startswith('https://') and isinstance(x.get('layer'), int) for x in got.values()),
      'each trail bot row names its layer and the exact feature')
# Nov 8: CA national-trail bot path may be file-based now; require they stay wired, not that the US-shaped bot emits them.
check({'CA-5506', 'CA-5993'} <= wired, 'Canada parks CA-5506 and CA-5993 stay on the wired list (file or ArcGIS)')

missing_files = []
for w in fil:
    ref = w['ref']
    tj = ROOT / f'data/trails/{ref}.json'
    intake = ROOT / w['layer_url'][5:]
    if not tj.exists():
        missing_files.append(ref + ':trails-json')
    if not intake.exists():
        missing_files.append(ref + ':intake')
    else:
        try:
            doc = json.loads(gzip.open(intake).read() if str(intake).endswith('.gz') else intake.read_bytes())
            feats = doc.get('features') if doc.get('type') == 'FeatureCollection' else [doc]
            ok = any(((f.get('geometry') or {}).get('coordinates')) for f in feats or [])
            if not ok: missing_files.append(ref + ':empty')
        except Exception as e:  # noqa: BLE001
            missing_files.append(ref + f':read {e}')
check(not missing_files, f'every file-based wired park has intake + data/trails JSON (missing {missing_files[:8]})')

y = (ROOT / '.github/workflows/kpc-us-trails.yml').read_text()
check('kpc_wired_trails.py /tmp/finds-lines.json' in y and y.index('kpc_wired_trails.py') < y.index('python3 .github/scripts/kpc_us_trails.py'),
      'the trail workflow adds the wired ArcGIS lines before the trail bot runs')
check('--install-files' in y and y.index('python3 .github/scripts/kpc_us_trails.py') < y.index('--install-files'),
      'the trail workflow re-installs file-based extracts after the trail bot rewrites index.json')
mt = (ROOT / '.github/scripts/draft/tools/kpc_layers_nov7/match_trails.py').read_text()
check('def own_file' in mt and 'polite_get(L["url"]).content' not in mt, 'own intake file is read from git, not raw.githubusercontent.com')
check('intake-files' in (ROOT / '.github/workflows/kpc-match-trails-nov7.yml').read_text(), 'matcher workflow fetches the intake-files branch')
# Canada parks are listed, not forgotten
check({'CA-5506', 'CA-5993'} <= wired, 'CA-5506 and CA-5993 stay in the wired list')
sys.exit(1 if FAILS else 0)
