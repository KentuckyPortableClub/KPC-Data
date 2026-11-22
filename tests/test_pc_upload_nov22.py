#!/usr/bin/env python3
"""22 Nov 2026 (owner): the PC upload pack. The PC packer (.github/scripts/pc/kpc_upload_pack.py) makes it; GitHub's reader
(kpc_pc_upload.py) refuses it WHOLE on any problem (a file that does not belong, a store-only field, a WDPA word, a private
file named, an area not read whole, a bad manifest) and otherwise merges keeper-first: every park already in a facts file is
kept as it was, a park only the PC has is added and marked; a keeper's crosswalk file is kept, an agency with none gets the
PC's, built by kpc_agency_lists' own checks and builder. Offline, invented parks and agencies only.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import datetime, gzip, json, pathlib, sys, tempfile, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
sys.path.insert(0, str(ROOT / '.github/scripts/pc'))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


try:
    import kpc_pc_upload as U
    import kpc_upload_pack as K
except ImportError as e:
    check(f'the reader and the packer are here ({e})', False); print('SOME FAILED'); sys.exit(1)

SRC = 'https://gis.zz.example.gov/arcgis/rest/services/Parks/FeatureServer/0'


def w(p, o):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o)); return p


def fact(ref, **k):
    return dict({'ref': ref, 'area': 'US-ZZ', 'page': {'kind': 'html', 'read': '2026-11-21'}, 'name': {'best': f'Invented {ref}'}}, **k)


def setup(t):
    t = pathlib.Path(t)
    w(t / 'pi' / 'US-ZZ.json', {'parks': {'US-9001': [], 'US-9002': [], 'US-9003': []}})
    w(t / 'pi' / 'US-YY.json', {'parks': {'US-9101': [], 'US-9102': []}})
    w(t / 'facts' / 'US-ZZ.json', {'area': 'US-ZZ', 'reader': 'v1', 'parks': {r: fact(r) for r in ('US-9001', 'US-9002', 'US-9003')}})
    w(t / 'facts' / 'US-YY.json', {'area': 'US-YY', 'reader': 'v1', 'parks': {'US-9101': fact('US-9101')}})
    w(t / 'prop.json', {'agencies': [{'agency': 'ZZ Parks', 'link_kind': 'zz park id', 'source_url': SRC, 'licence': 'Public domain',
                                     'status': 'proposal: row tie 3 same / 0 different (invented)',
                                     'web_id': {'column': 'PARKNUM', 'regex': ''}, 'map': {'layer': 'sgzza', 'field': 'UNIT_NO', 'value': 'UNIT'}},
                                    {'agency': 'XX Lands', 'link_kind': 'xx id', 'source_url': 'https://xx.example.gov/list',
                                     'status': 'proposal: row tie 1 same / 0 different (invented)',
                                     'web_id': {'column': 'ID'}, 'map': {'layer': 'sgxxa', 'field': 'F', 'value': 'G'}}]})
    rows = [{'PARKNUM': '501', 'UNIT': 'A1'}, {'PARKNUM': '502', 'UNIT': 'A2'}, {'PARKNUM': '503', 'UNIT': 'A3'}, {'PARKNUM': '503', 'UNIT': 'A9'}]
    (t / 'lists').mkdir(exist_ok=True)
    (t / 'lists' / 'zz.json.gz').write_bytes(gzip.compress(json.dumps({'agency': 'ZZ Parks', 'read_on': '2026-11-21', 'layers': [
        {'url': SRC, 'complete': True, 'rows': rows}]}).encode()))
    (t / 'lists' / 'xx.json.gz').write_bytes(gzip.compress(json.dumps({'agency': 'XX Lands', 'layers': [{'url': 'u', 'complete': True,
                                                                                                         'rows': [{'ID': '1', 'G': 'B1'}]}]}).encode()))
    return t


def pack(t, approved=('ZZ Parks',)):
    zp, c, why = K.make_pack(t / 'out', t / 'facts', t / 'prop.json', t / 'lists', '', list(approved), parkinfo=t / 'pi',
                             now=datetime.datetime(2026, 11, 22, 1, 30))
    return zp, c


def edit(zp, name, data=None, drop=False):
    """A copy of the pack with one member changed (data = bytes / dict) or added, or dropped."""
    out = zp.with_name('edited-' + zp.name)
    with zipfile.ZipFile(zp) as a, zipfile.ZipFile(out, 'w') as b:
        for n in a.namelist():
            if n == name: continue
            b.writestr(n, a.read(n))
        if not drop: b.writestr(name, data if isinstance(data, (bytes, str)) else json.dumps(data))
    return out


with tempfile.TemporaryDirectory() as td:
    t = setup(td)
    zp, c = pack(t)
    names = zipfile.ZipFile(zp).namelist()
    check('the packer packs the whole area, leaves out the area not read whole and the agency not allowed',
          'pages/US-ZZ.json' in names and 'pages/US-YY.json' not in names and 'crosswalk/zz-parks.json' in names and 'crosswalk/xx-lands.json' not in names)
    P, probs = U.read_pack(zp, t / 'pi')
    check('a clean pack passes the check', P is not None and not probs and set(P['pages']) == {'US-ZZ'})

    bad_cases = [
        ('a file that does not belong in a pack', edit(zp, 'notes/secret.txt', b'x')),
        ('no manifest', edit(zp, 'manifest.json', drop=True)),
        ('a manifest that is not a pack', edit(zp, 'manifest.json', {'kind': 'other'})),
        ('a store-only field (shapes)', edit(zp, 'pages/US-ZZ.json', {'area': 'US-ZZ', 'parks': {r: dict(fact(r), geometry={'rings': []}) for r in ('US-9001', 'US-9002', 'US-9003')}})),
        ('a WDPA field', edit(zp, 'pages/US-ZZ.json', {'area': 'US-ZZ', 'parks': {r: dict(fact(r), WDPAID=5) for r in ('US-9001', 'US-9002', 'US-9003')}})),
        ('a WDPA word in a value', edit(zp, 'crosswalk/zz-parks.json', {'agency': 'ZZ', 'rows': [], 'source': {'url': 'https://www.protectedplanet.net/x'}})),
        ('a private file named', edit(zp, 'pages/US-ZZ.json', {'area': 'US-ZZ', 'parks': {r: dict(fact(r), note='from PRIVATE-right-records.csv') for r in ('US-9001', 'US-9002', 'US-9003')}})),
        ('an area not read whole', edit(zp, 'pages/US-ZZ.json', {'area': 'US-ZZ', 'parks': {'US-9001': fact('US-9001')}})),
        ('an area with no POTA list here', edit(zp, 'pages/US-QQ.json', {'area': 'US-QQ', 'parks': {'US-9201': fact('US-9201')}})),
        ('a file that is not JSON', edit(zp, 'pages/US-ZZ.json', b'{broken')),
        ('a park key that is not a park reference', edit(zp, 'pages/US-ZZ.json', {'area': 'US-ZZ', 'parks': dict({r: fact(r) for r in ('US-9001', 'US-9002', 'US-9003')}, **{'../x': {}})})),
    ]
    for why, bz in bad_cases:
        P2, pr = U.read_pack(bz, t / 'pi')
        check(f'refused whole: {why}', P2 is None and pr)
    rc = U.main(['merge', '--pack', str(bad_cases[3][1]), '--parkinfo', str(t / 'pi'), '--pages', str(t / 'gh-pages'), '--crosswalk', str(t / 'gh-xw')])
    check('a refused pack keeps nothing (exit 1, no file written)', rc == 1 and not (t / 'gh-pages').exists() and not (t / 'gh-xw').exists())

    # keeper-first merge
    keep = fact('US-9001', page={'kind': 'html', 'read': '2026-11-10', 'by': 'bot on GitHub'})
    gp = w(t / 'gh-pages' / 'US-ZZ.json', {'area': 'US-ZZ', 'reader': 'v1', 'parks': {'US-9001': keep, 'US-9999': fact('US-9999')}})
    w(t / 'gh-xw' / 'kept-agency.json', {'agency': 'Kept', 'made_by': 'kpc_agency_lists 2026-11-21c', 'rows': [{'web_id': '1'}]})
    before_kept = (t / 'gh-xw' / 'kept-agency.json').read_bytes()
    rc = U.main(['merge', '--pack', str(zp), '--parkinfo', str(t / 'pi'), '--pages', str(t / 'gh-pages'), '--crosswalk', str(t / 'gh-xw'),
                 '--report', str(t / 'report.md')])
    after = json.loads(gp.read_text())
    check('merge: a park already in the facts is kept exactly as it was', after['parks']['US-9001'] == keep)
    check('merge: a park only GitHub had is kept', 'US-9999' in after['parks'])
    check('merge: the parks only the PC had are added, marked with the pack date',
          all(after['parks'][r].get('from_pc_upload') == '2026-11-22' for r in ('US-9002', 'US-9003')))
    xz = json.loads((t / 'gh-xw' / 'zz-parks.json').read_text())
    check('merge: the PC crosswalk is written through the agency-list builder (a web id with two map ids left out)',
          rc == 0 and [r['web_id'] for r in xz['rows']] == ['501', '502'] and xz['left_out_not_one_to_one'] == 1 and xz['made_by'].startswith('PC upload'))
    check("merge: a keeper's crosswalk file is never touched", (t / 'gh-xw' / 'kept-agency.json').read_bytes() == before_kept)
    w(t / 'gh-xw' / 'zz-parks.json', {'agency': 'ZZ Parks', 'made_by': 'kpc_agency_lists 2026-11-21c', 'rows': []})
    U.main(['merge', '--pack', str(zp), '--parkinfo', str(t / 'pi'), '--pages', str(t / 'gh-pages'), '--crosswalk', str(t / 'gh-xw')])
    check("merge: once the keeper has its own file for an agency, the PC's never replaces it",
          json.loads((t / 'gh-xw' / 'zz-parks.json').read_text())['made_by'].startswith('kpc_agency_lists'))
    rep = (t / 'report.md').read_text()
    check('the report holds counts only (no park number)', 'US-90' not in rep and 'parks added from the PC' in rep)
    # an agency the agency-list checks refuse (a never-contact or non-https source) is not written
    pb = edit(zp, 'crosswalk/zz-parks.json', {'agency': 'ZZ Parks', 'link_kind': 'zz park id', 'source': {'url': 'http://gis.zz.example.gov/x'},
                                              'web_id': {'column': 'PARKNUM'}, 'map': {'layer': 'sgzza', 'field': 'UNIT_NO', 'value': 'UNIT'},
                                              'rows': [{'web': '501', 'map': 'A1'}]})
    (t / 'gh-xw' / 'zz-parks.json').unlink()
    U.main(['merge', '--pack', str(pb), '--parkinfo', str(t / 'pi'), '--pages', str(t / 'gh-pages'), '--crosswalk', str(t / 'gh-xw')])
    check('merge: an agency the agency-list checks refuse (not https) is not written', not (t / 'gh-xw' / 'zz-parks.json').exists())

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
