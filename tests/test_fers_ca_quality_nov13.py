#!/usr/bin/env python3
"""Nov 13 (Quality, CA 2-fer chain 43332473942 + per-area fers promote + 0-pair guard).

B1  A live pair that vanishes gets a dropped or not-sure row (never a silent gone).
    Named CA pairs: CA-1182+3063, CA-2956+2957, CA-2957+2958, CA-0109+0691.
    Post-line fails the job when any gone pair is unexplained.
B2  A US trail line must not stay live on Canadian ground (CA-0110+US-4558).
B3  A hidden file with 0 pairs must never replace live; canadaeast (CA-SI / CA-SP
    live there; casp is not its own area) keeps live if it has not run.
B5  The POTA-pairs check reads parkinfo/CA.json when there is no CA-XX.json, or
    reports 'not checked' — never 0.
Water checks and the canadaeast line are not blocked in code.
Per-area 2-fer release: one area at a time; a held area does not block the others;
world 2-fers and US-42797939226 are never public; WDPA is denied on the site.
Nothing is started.
"""
import json, os, pathlib, sys, tempfile, textwrap
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_fers_annotate as A
import kpc_fers_postline_gate as G
import kpc_pota_pairs_run as P
import kpc_waiting_room as W
import kpc_fers_release_areas as R
import kpc_fers_states as FS
import yaml

ok = True
def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg)
    ok = ok and bool(c)

def spot(refs, status='candidate', **kw):
    s = {'id': '+'.join(sorted(refs)) + '@t', 'refs': list(refs), 'status': status, 'passes': [1, 1, 1], 'kind': kw.pop('kind', 'area')}
    s.update(kw)
    return s

def doc(*spots, **kw):
    d = {'spots': list(spots), 'pass1': '2026-11-13', 'pass2': '2026-11-13', 'pass3': '2026-11-13'}
    d.update(kw)
    return d

# ---- B1 annotate: named CA gone pairs get a row
live = doc(
    spot(['CA-1182', 'CA-3063']),
    spot(['CA-2956', 'CA-2957']),
    spot(['CA-2957', 'CA-2958']),
    spot(['CA-0109', 'CA-0691']),
    spot(['CA-0001', 'CA-0002']),  # an ordinary live pair that also vanished
    spot(['CA-1111', 'CA-2222']),  # still live in the new file
)
new = doc(spot(['CA-1111', 'CA-2222']))
r = A.annotate_doc(new, live, 'CA-AB')
keys = {A.pair_key(s['refs']): s for s in new['spots']}
check(r['added'] == 5 and r['gone_left'] == 0, f'B1: five vanished live pairs each got a row (added={r["added"]}, gone_left={r["gone_left"]})')
check(str(keys['CA-1182+CA-3063']['status']).startswith('not sure') and 'same-land' in keys['CA-1182+CA-3063']['status'],
      'B1: CA-1182+CA-3063 is not-sure (same-land, vanished)')
check(str(keys['CA-2956+CA-2957']['status']).startswith('not sure') and str(keys['CA-2957+CA-2958']['status']).startswith('not sure'),
      'B1: CA-2956+2957 and CA-2957+2958 are not-sure (same-land, vanished)')
check(str(keys['CA-0109+CA-0691']['status']).startswith('dropped') and 'pin' in keys['CA-0109+CA-0691']['status'].lower(),
      'B1: CA-0109+CA-0691 is dropped (CA-0109 is a pin)')
check(str(keys['CA-0001+CA-0002']['status']).startswith('dropped') and keys['CA-0001+CA-0002'].get('reason'),
      'B1: an unnamed vanished pair still gets a dropped row with a reason')
check(str(keys['CA-1111+CA-2222']['status']).startswith('candidate'), 'B1: a pair still live is left alone')

# already explained: do not add a second row
new2 = doc(spot(['CA-1182', 'CA-3063'], status='not sure: already written'))
r2 = A.annotate_doc(new2, doc(spot(['CA-1182', 'CA-3063'])), 'CA-AB')
check(r2['added'] == 0 and len(new2['spots']) == 1, 'B1: a vanished pair that already has a not-sure row is not written again')

# ---- B2 US trail on Canadian ground
cdt = spot(['CA-0110', 'US-4558'], kind='trail', name='Continental Divide Trail', center=[49.05, -113.91])
keep = spot(['US-0001', 'US-0002'], kind='trail', name='some US trail', center=[35.0, -80.0])
cross_ok = spot(['CA-0110', 'US-4558'], kind='area', name='Waterton-Glacier land', center=[48.5, -113.9])  # not a trail, south of 49
new3 = doc(cdt, keep)
r3 = A.annotate_doc(new3, doc(), 'CA-AB')
st = {A.pair_key(s['refs']): s['status'] for s in new3['spots']}
check(r3['demoted'] == 1 and str(st['CA-0110+US-4558']).startswith('not sure') and 'Canadian' in st['CA-0110+US-4558'],
      'B2: CA-0110+US-4558 (Waterton + CDT, on Canadian ground) is marked not sure')
check(str(st['US-0001+US-0002']).startswith('candidate'), 'B2: a US trail on US ground stays live')
# already-demoted is not demoted again; ground=canada also trips it
g = spot(['CA-1000', 'US-2000'], kind='path', ground='canada', center=[45.0, -75.0], status='candidate')
new4 = doc(g)
r4 = A.annotate_doc(new4, doc(), 'CA-QC')
check(r4['demoted'] == 1 and 'Canadian' in new4['spots'][0]['status'],
      'B2: a US/CA trail with ground=canada is demoted even south of 49')

# ---- B1 post-line gate
def tree(td, hidden, live_doc):
    h = pathlib.Path(td, 'data/waiting/in/data/fers'); h.mkdir(parents=True)
    lv = pathlib.Path(td, 'data/fers'); lv.mkdir(parents=True)
    (h / 'CA-AB.json').write_text(json.dumps(hidden) + '\n')
    (lv / 'CA-AB.json').write_text(json.dumps(live_doc) + '\n')

with tempfile.TemporaryDirectory() as t:
    tree(t, doc(), doc(spot(['CA-1182', 'CA-3063'])))  # vanished, no row
    rc = G.main.__wrapped__ if hasattr(G.main, '__wrapped__') else None
    # call main with argv
    import io
    from contextlib import redirect_stdout
    argv = sys.argv
    sys.argv = ['kpc_fers_postline_gate.py', '--data', t]
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = G.main()
    sys.argv = argv
    check(rc == 1 and 'CA-1182+CA-3063' in buf.getvalue() and '(gone)' in buf.getvalue(),
          f'B1 gate: a silent gone pair fails the post-line (rc={rc})')

with tempfile.TemporaryDirectory() as t:
    tree(t, doc(spot(['CA-1182', 'CA-3063'], status='not sure: same-land pair vanished')), doc(spot(['CA-1182', 'CA-3063'])))
    argv = sys.argv
    sys.argv = ['kpc_fers_postline_gate.py', '--data', t]
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = G.main()
    sys.argv = argv
    check(rc == 0 and 'no silent gone' in buf.getvalue(), f'B1 gate: an explained row is clean (rc={rc})')

# workflow: the gate step has no continue-on-error; it is called from post-line
Y = yaml.safe_load((ROOT / '.github/workflows/kpc-fers-postline.yml').read_text())
# PyYAML may turn 'on' into True; jobs stay under 'jobs'
steps = Y['jobs']['postline']['steps']
gate = next(s for s in steps if 'kpc_fers_postline_gate.py' in s.get('run', ''))
check(not gate.get('continue-on-error') and 'kpc_fers_postline_gate.py' in (ROOT / '.github/workflows/kpc-fers-postline.yml').read_text(),
      'B1: kpc-fers-postline.yml runs the gate with no continue-on-error')
line_src = (ROOT / '.github/workflows/kpc-fers-line.yml').read_text()
bot_src = (ROOT / '.github/workflows/kpc-fers.yml').read_text()
check('kpc_fers_annotate.py' in line_src and line_src.find('kpc_fers_annotate.py') < line_src.find('kpc_waiting_room.py divert data/fers'),
      'B1/B2: the line annotates vanished / US-trail-on-Canada pairs before the waiting-room divert')
check('kpc_fers_annotate.py' in bot_src, 'B1/B2: the monthly 2-fer bot also annotates before save')

# ---- B3 0-pair must never replace live; canadaeast / casp
live_ab = doc(spot(['CA-0001', 'CA-0002']), spot(['CA-0003', 'CA-0004']))
empty = doc()  # 0 live pairs
why = W.refuse_fers_promote('data/fers/CA-AB.json', new=empty, live=live_ab)
check('0 pairs' in why and 'never replace live' in why,
      f'B3: refuse_fers_promote blocks 0-pair over live ({why!r})')
check(W.refuse_fers_promote('data/fers/CA-AB.json', new=live_ab, live=live_ab) == '',
      'B3: a hidden file that still has pairs is not refused for this reason')
check(W.refuse_fers_promote('data/fers/W-GB.json', new=live_ab, live=None) == 'world 2-fers are never public',
      'B3/release: a world 2-fer file is never promoted')
# c_fers also holds
holds, _ = W.c_fers('data/fers/CA-QC.json', empty, live_ab, {})
check(any('0 pairs' in h and 'never replace live' in h for h in holds),
      f'B3: c_fers holds a 0-pair hidden file ({holds})')

areas = json.loads((ROOT / '.github/fers-areas.json').read_text())['areas']
check(areas.get('canadaeast') == 'CA-QC CA-NB CA-NS CA-PE CA-NL CA-SI CA-SP',
      'B3: CA-SI and CA-SP live under canadaeast')
check('casp' not in areas, 'B3: casp is not a separate area (it is not run on its own)')
check('canadaeast' in FS.areas() and set(areas['canadaeast'].split()) <= set(sum((v.split() for k, v in FS.areas().items() if k.startswith('canada')), [])),
      'B3: canadaeast is still on the area list the chain and the bot use')

# per-area release: held area does not block a green neighbour; 0-pair / world / blocked build
# patch R to a temp tree
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    (t / 'data/waiting/in/data/fers').mkdir(parents=True)
    (t / 'data/fers/stamps').mkdir(parents=True)
    (t / 'data/fers/CA-AB.json').write_text(json.dumps(live_ab) + '\n')
    (t / 'data/fers/CA-SK.json').write_text(json.dumps(doc(spot(['CA-0100', 'CA-0101']))) + '\n')
    # hidden: AB is 0-pair (must keep live); SK is green and has pairs
    (t / 'data/waiting/in/data/fers/CA-AB.json').write_text(json.dumps(empty) + '\n')
    sk_new = doc(spot(['CA-0100', 'CA-0101']), spot(['CA-0102', 'CA-0103']))
    (t / 'data/waiting/in/data/fers/CA-SK.json').write_text(json.dumps(sk_new) + '\n')
    (t / 'data/fers/stamps/CA-SK.json').write_text(json.dumps({'run': 'CA-43332473942', 'rules': 'x', 'built_sha': 'abc'}) + '\n')
    grade = {'RELEASE-READY': 'YES', 'areas': {
        'CA-AB': {'RELEASE-READY': 'YES'},
        'CA-SK': {'RELEASE-READY': 'YES', 'no_worse_than_live': True},
    }}
    (t / 'grade.json').write_text(json.dumps(grade) + '\n')
    old_data, old_w, old_live = W.DATA, W.W, R.LIVE_FILE
    W.DATA = t; W.W = t / 'data/waiting'; R.LIVE_FILE = t / 'data/fers/LIVE.json'
    try:
        check(R.why_not('CA-AB', grade).startswith('hidden file has 0 pairs'),
              f"B3/release: CA-AB 0-pair is kept ({R.why_not('CA-AB', grade)!r})")
        check(R.why_not('CA-SK', grade) == '', f"per-area: CA-SK is promotable ({R.why_not('CA-SK', grade)!r})")
        check(R.why_not('W-GB', grade) == 'world 2-fers are never public', 'per-area: world 2-fers are never public')
        blocked = dict(grade, build='US-42797939226')
        check('never released' in R.why_not('CA-SK', blocked), 'per-area: US-42797939226 is never released')
        # SK promotes, AB is kept, live AB bytes unchanged
        sys_argv = sys.argv
        sys.argv = ['kpc_fers_release_areas.py', '--areas', 'CA-AB CA-SK', '--grade', str(t / 'grade.json')]
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        sys.argv = sys_argv
        live_ab_after = json.loads((t / 'data/fers/CA-AB.json').read_text())
        live_sk_after = json.loads((t / 'data/fers/CA-SK.json').read_text())
        ledger = json.loads((t / 'data/fers/LIVE.json').read_text())
        check(rc == 0 and 'CA-SK promoted' in buf.getvalue() and 'CA-AB kept live' in buf.getvalue(),
              f'per-area: SK is promoted and AB is kept (rc={rc}; {buf.getvalue().strip()[:200]})')
        check(W.live_pairs(live_ab_after) if False else A.pairs_of(live_ab_after, live_only=True).keys() == {'CA-0001+CA-0002', 'CA-0003+CA-0004'},
              'per-area: CA-AB live pairs are unchanged')
        check('CA-0102+CA-0103' in A.pairs_of(live_sk_after, live_only=True),
              'per-area: CA-SK live file is the promoted hidden copy')
        check(ledger.get('areas', {}).get('CA-SK', {}).get('build') == 'CA-43332473942' and 'CA-AB' not in ledger.get('areas', {}),
              'per-area: LIVE.json records the build only for the promoted area')
    finally:
        W.DATA, W.W, R.LIVE_FILE = old_data, old_w, old_live

# W-* in --areas is refused before any promote
try:
    R.parse_areas('US-KY W-GB')
    check(False, 'parse_areas should refuse a world area')
except SystemExit as e:
    check('world 2-fer' in str(e), f'parse_areas refuses W-GB ({e})')

# waiting-room workflow wires release-areas, owner-run dispatch, no cron
WR = yaml.safe_load((ROOT / '.github/workflows/kpc-waiting-room.yml').read_text())
on = WR.get('on') or WR.get(True)
wd = on['workflow_dispatch']['inputs']
check('release-areas' in wd['mode']['description'] and 'areas' in wd and 'grade' in wd,
      'waiting-room: release-areas is a dispatch mode (areas + grade inputs; existing crons unchanged)')
wr_src = (ROOT / '.github/workflows/kpc-waiting-room.yml').read_text()
check('kpc_fers_release_areas.py' in wr_src and "release-areas)" in wr_src,
      'waiting-room: release-areas runs kpc_fers_release_areas.py')

# site allow-list denies WDPA and world 2-fers
allow = (ROOT / '.github/site-allow-list.txt').read_text()
check('!data/fers/W-*' in allow and '!**/wdpa*' in allow.lower() or '!**/wdpa*' in allow,
      'site allow-list denies world 2-fer files and WDPA paths')
check('!**/*WDPA*' in allow, 'site allow-list denies *WDPA* paths')

# ---- B5 POTA pairs: CA.json fallback, or not checked — never 0
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    cwd = os.getcwd()
    os.chdir(t)
    try:
        # no parkinfo at all -> not checked, marker, never a 0 count
        os.environ['STATES'] = 'CA-AB'
        os.environ['DATA'] = str(t)
        os.environ['LINKS'] = str(t)
        # reload module constants? resolve uses DATA via HERE at import. Call resolve after patching.
        P.HERE = t
        P.LINKS = t
        P.SCRIPT = t / '.github/scripts/kpc_pota_pairs.py'
        P.OUT = t / 'data/fers'
        refs, how = P.resolve('CA-AB')
        check(refs is None and how == 'not checked', f"B5: no CA.json and no CA-AB.json -> not checked ({how!r})")
        P.write_marker('CA-AB', how)
        m = json.loads((t / 'data/fers/pota-pairs-CA-AB.json').read_text())
        check(m.get('not_checked') is True and m.get('parks_read') is None and m.get('pairs') == {},
              'B5: the marker says not checked (never a 0-pairs confirmation)')
        # CA.json + province key -> filtered list
        (t / 'data/parkinfo').mkdir(parents=True)
        (t / 'data/ca-key').mkdir(parents=True)
        (t / 'data/parkinfo/CA.json').write_text(json.dumps({'parks': {'CA-0001': {}, 'CA-0002': {}, 'CA-9999': {}}}) + '\n')
        (t / 'data/ca-key/CA-AB.json').write_text(json.dumps({'parks': {'CA-0001': {}, 'CA-0002': {}}}) + '\n')
        refs, how = P.resolve('CA-AB')
        check(refs == ['CA-0001', 'CA-0002'] and 'CA.json' in how,
              f'B5: with no CA-AB.json in parkinfo, parkinfo/CA.json is filtered by the CA-AB key ({refs}, {how})')
        # direct CA-AB.json still wins
        (t / 'data/parkinfo/CA-AB.json').write_text(json.dumps({'parks': {'CA-0001': {}}}) + '\n')
        refs, how = P.resolve('CA-AB')
        check(refs == ['CA-0001'] and 'CA-AB.json' in how, f'B5: a direct parkinfo/CA-AB.json is used when present ({how})')
        # CA.json but no province key and no CA-XX.json -> not checked (do not invent a 5,901-park request)
        refs, how = P.resolve('CA-SK')
        check(refs is None and how == 'not checked', f'B5: CA.json with no province filter is not checked ({how})')
    finally:
        os.chdir(cwd)
        os.environ.pop('STATES', None)

check('kpc_pota_pairs_run.py' in line_src and 'kpc_pota_pairs_run.py' in bot_src,
      'B5: the line and the monthly bot run kpc_pota_pairs_run.py (not a bare skip that looks like 0)')

# Water / canadaeast are not blocked in code
water = (ROOT / '.github/workflows/kpc-fers-water.yml').read_text()
check('kpc-fers-water.yml' and 'workflow_dispatch' in water and 'canadaeast' not in [l for l in water.splitlines() if l.strip().startswith('#') and 'skip' in l.lower() or 'block' in l.lower()],
      'water: kpc-fers-water.yml is still a dispatchable workflow')
# no code sets canadaeast or casp to skip / 0-replace
block_hit = []
for pth in (ROOT / '.github/scripts').glob('kpc_fers*.py'):
    txt = pth.read_text()
    if 'canadaeast' in txt and ('skip canadaeast' in txt.lower() or "areas.pop('canadaeast')" in txt):
        block_hit.append(pth.name)
check(not block_hit, f'nothing in fers scripts removes or skips canadaeast ({block_hit})')


# ---- end to end (Brandon, 5:10 AM CT Nov 13): one held or broken 2-fer area never blocks the others
def _fers_tree(t, live, hidden):
    (t / 'data/waiting/in/data/fers').mkdir(parents=True)
    (t / 'data/fers/stamps').mkdir(parents=True)
    for name, doc_ in live.items():
        (t / 'data/fers' / f'{name}.json').write_text(json.dumps(doc_) + '\n')
    for name, raw in hidden.items():
        path = t / 'data/waiting/in/data/fers' / f'{name}.json'
        if isinstance(raw, (bytes, bytearray)):
            path.write_bytes(raw)
        else:
            path.write_text(json.dumps(raw) + '\n')

with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    ab_live = doc(spot(['CA-0100', 'CA-0101']))
    qc_live = doc(spot(['CA-0200', 'CA-0201']), spot(['CA-0202', 'CA-0203']))
    ab_new = doc(spot(['CA-0100', 'CA-0101']), spot(['CA-0102', 'CA-0103']))
    qc_new = doc(spot(['CA-0200', 'CA-0201']))  # fewer, but we will hold QC by grade, not by 0-pair
    _fers_tree(t, {'CA-AB': ab_live, 'CA-QC': qc_live}, {'CA-AB': ab_new, 'CA-QC': qc_new})
    (t / 'data/fers/stamps/CA-AB.json').write_text(json.dumps({'run': 'CA-43332473942', 'rules': 'x', 'built_sha': 'ab'}) + '\n')
    (t / 'data/fers/stamps/CA-QC.json').write_text(json.dumps({'run': 'CA-43332473942', 'rules': 'x', 'built_sha': 'qc'}) + '\n')
    grade = {'RELEASE-READY': 'PARTIAL', 'areas': {
        'CA-AB': {'RELEASE-READY': 'YES', 'no_worse_than_live': True},
        'CA-QC': {'RELEASE-READY': 'NO'},
    }}
    (t / 'grade.json').write_text(json.dumps(grade) + '\n')
    old_data, old_w, old_live, old_dry, old_argv = W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv
    W.DATA = t; W.W = t / 'data/waiting'; R.LIVE_FILE = t / 'data/fers/LIVE.json'; R.DRY = False
    try:
        sys.argv = ['kpc_fers_release_areas.py', '--areas', 'CA-AB CA-QC', '--grade', str(t / 'grade.json')]
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        ab_after = json.loads((t / 'data/fers/CA-AB.json').read_text())
        qc_after = json.loads((t / 'data/fers/CA-QC.json').read_text())
        check(rc == 0 and 'CA-AB promoted' in out and 'CA-QC kept live' in out,
              f'2-fer e2e CLI: held CA-QC does not block CA-AB (rc={rc}; {out.strip()[:240]})')
        check('CA-0102+CA-0103' in A.pairs_of(ab_after, live_only=True),
              '2-fer e2e: CA-AB live is the promoted hidden copy')
        check(A.pairs_of(qc_after, live_only=True).keys() == {'CA-0200+CA-0201', 'CA-0202+CA-0203'},
              '2-fer e2e: held CA-QC keeps its live pairs')
        check((t / 'data/waiting/in/data/fers/CA-QC.json').is_file()
              and not (t / 'data/waiting/in/data/fers/CA-AB.json').is_file(),
              '2-fer e2e: only the held area stays in the waiting room (only that area still needs a later promote / rebuild)')
        ledger = json.loads((t / 'data/fers/LIVE.json').read_text())
        check(ledger.get('areas', {}).get('CA-AB', {}).get('build') == 'CA-43332473942' and 'CA-QC' not in ledger.get('areas', {}),
              '2-fer e2e: LIVE.json records only the promoted area')
    finally:
        W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv = old_data, old_w, old_live, old_dry, old_argv

# a broken hidden file for one area does not abort a green neighbour
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    ab_live = doc(spot(['CA-0100', 'CA-0101']))
    qc_live = doc(spot(['CA-0200', 'CA-0201']))
    ab_new = doc(spot(['CA-0100', 'CA-0101']), spot(['CA-0102', 'CA-0103']))
    _fers_tree(t, {'CA-AB': ab_live, 'CA-QC': qc_live},
               {'CA-AB': ab_new, 'CA-QC': b'NOT-JSON{{{'})
    (t / 'data/fers/stamps/CA-AB.json').write_text(json.dumps({'run': 'CA-9', 'rules': 'x', 'built_sha': 'ab'}) + '\n')
    grade = {'RELEASE-READY': 'YES', 'areas': {
        'CA-AB': {'RELEASE-READY': 'YES', 'no_worse_than_live': True},
        'CA-QC': {'RELEASE-READY': 'YES'},
    }}
    (t / 'grade.json').write_text(json.dumps(grade) + '\n')
    old_data, old_w, old_live, old_dry, old_argv = W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv
    W.DATA = t; W.W = t / 'data/waiting'; R.LIVE_FILE = t / 'data/fers/LIVE.json'; R.DRY = False
    try:
        sys.argv = ['kpc_fers_release_areas.py', '--areas', 'CA-QC CA-AB', '--grade', str(t / 'grade.json')]
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        qc_after = json.loads((t / 'data/fers/CA-QC.json').read_text())
        ab_after = json.loads((t / 'data/fers/CA-AB.json').read_text())
        check(rc == 0 and 'CA-AB promoted' in out and 'CA-QC kept live' in out,
              f'2-fer e2e: a broken hidden file for CA-QC does not block CA-AB (rc={rc}; {out.strip()[:240]})')
        check(A.pairs_of(qc_after, live_only=True).keys() == {'CA-0200+CA-0201'},
              '2-fer e2e: CA-QC live bytes stay when its hidden file is unreadable')
        check('CA-0102+CA-0103' in A.pairs_of(ab_after, live_only=True),
              '2-fer e2e: CA-AB still promotes after a broken neighbour')
    finally:
        W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv = old_data, old_w, old_live, old_dry, old_argv


# R5: a 2-fer area releases only if both key areas are released and current (cross-border needs both)
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data, links = t / 'data-root', t / 'links'
    ab_live = doc(spot(['CA-0100', 'CA-0101']))
    ab_new = doc(spot(['CA-0100', 'CA-0101']), spot(['CA-0102', 'CA-0103']))
    # cross-border pair in the hidden file
    ab_xb = doc(spot(['CA-0110', 'US-4558']))
    _fers_tree(data, {'CA-AB': ab_live}, {'CA-AB': ab_new})
    (data / 'data/fers/stamps/CA-AB.json').write_text(json.dumps({'run': 'CA-9', 'rules': 'x', 'built_sha': 'ab'}) + '\n')
    grade = {'RELEASE-READY': 'YES', 'areas': {'CA-AB': {'RELEASE-READY': 'YES', 'no_worse_than_live': True}}}
    (data / 'grade.json').write_text(json.dumps(grade) + '\n')
    # Links tree with no released key
    (links / 'data/ca-key').mkdir(parents=True)
    (links / 'data/ca-key/CA-AB.json').write_text(json.dumps({'parks': {'CA-0100': {}, 'CA-0101': {}, 'CA-0102': {}, 'CA-0103': {}}}) + '\n')
    old_data, old_w, old_live, old_dry, old_argv, old_links = W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv, os.environ.get('LINKS')
    W.DATA = data; W.W = data / 'data/waiting'; R.LIVE_FILE = data / 'data/fers/LIVE.json'; R.DRY = False
    os.environ['LINKS'] = str(links)
    try:
        sys.argv = ['kpc_fers_release_areas.py', '--areas', 'CA-AB', '--grade', str(data / 'grade.json')]
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        check(rc == 1 and 'CA-AB kept live' in out and 'not released' in out,
              f'R5: CA-AB 2-fer stays live when the CA-AB key is not released (rc={rc}; {out.strip()[:200]})')
        # now release the key
        dest = links / 'data/released/ca-key'; dest.mkdir(parents=True)
        (dest / 'CA-AB.json').write_text(json.dumps({'parks': {'CA-0100': {}}}) + '\n')
        (links / 'data/released/RELEASED.json').write_text(json.dumps({'live': {'CA-AB': {'build': 'CA-9', 'sha': 'ab'}}}) + '\n')
        # hidden still waiting (previous promote did not happen)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        check(rc == 0 and 'CA-AB promoted' in out,
              f'R5: CA-AB 2-fer promotes once its key is released and current (rc={rc}; {out.strip()[:200]})')
    finally:
        W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv = old_data, old_w, old_live, old_dry, old_argv
        if old_links is None: os.environ.pop('LINKS', None)
        else: os.environ['LINKS'] = old_links

# cross-border: CA-AB hidden has CA-0110+US-4558; both keys required
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    data, links = t / 'data-root', t / 'links'
    live = doc(spot(['CA-0100', 'CA-0101']))
    hidden = doc(spot(['CA-0110', 'US-4558']))
    _fers_tree(data, {'CA-AB': live}, {'CA-AB': hidden})
    (data / 'data/fers/stamps/CA-AB.json').write_text(json.dumps({'run': 'CA-9', 'rules': 'x', 'built_sha': 'ab'}) + '\n')
    (data / 'grade.json').write_text(json.dumps({'RELEASE-READY': 'YES', 'areas': {'CA-AB': {'RELEASE-READY': 'YES', 'no_worse_than_live': True}}}) + '\n')
    (links / 'data/ca-key').mkdir(parents=True)
    (links / 'data/us-key').mkdir(parents=True)
    (links / 'data/ca-key/CA-AB.json').write_text(json.dumps({'parks': {'CA-0110': {}, 'CA-0100': {}, 'CA-0101': {}}}) + '\n')
    (links / 'data/us-key/US-MT.json').write_text(json.dumps({'parks': {'US-4558': {}}}) + '\n')
    (links / 'data/released/ca-key').mkdir(parents=True)
    (links / 'data/released/ca-key/CA-AB.json').write_text(json.dumps({'parks': {'CA-0110': {}}}) + '\n')
    (links / 'data/released/RELEASED.json').write_text(json.dumps({'live': {'CA-AB': {'build': 'CA-9', 'sha': 'ab'}}}) + '\n')
    old_data, old_w, old_live, old_dry, old_argv, old_links = W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv, os.environ.get('LINKS')
    W.DATA = data; W.W = data / 'data/waiting'; R.LIVE_FILE = data / 'data/fers/LIVE.json'; R.DRY = False
    os.environ['LINKS'] = str(links)
    try:
        sys.argv = ['kpc_fers_release_areas.py', '--areas', 'CA-AB', '--grade', str(data / 'grade.json')]
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        check(rc == 1 and 'US-MT key is not released' in out,
              f'R5: cross-border CA-0110+US-4558 stays live until the US-MT key is also released ({out.strip()[:240]})')
        (links / 'data/released/us-key').mkdir(parents=True)
        (links / 'data/released/us-key/US-MT.json').write_text(json.dumps({'parks': {'US-4558': {}}}) + '\n')
        idx = json.loads((links / 'data/released/RELEASED.json').read_text())
        idx.setdefault('live', {})['US-MT'] = {'build': 'US-9', 'sha': 'mt'}
        (links / 'data/released/RELEASED.json').write_text(json.dumps(idx) + '\n')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.main()
        out = buf.getvalue()
        check(rc == 0 and 'CA-AB promoted' in out,
              f'R5: cross-border promotes once both key areas are released ({out.strip()[:200]})')
    finally:
        W.DATA, W.W, R.LIVE_FILE, R.DRY, sys.argv = old_data, old_w, old_live, old_dry, old_argv
        if old_links is None: os.environ.pop('LINKS', None)
        else: os.environ['LINKS'] = old_links

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
