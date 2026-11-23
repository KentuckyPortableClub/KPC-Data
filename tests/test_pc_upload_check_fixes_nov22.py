#!/usr/bin/env python3
"""22 Nov 2026: the owner's first real PC upload pack (52 areas, 18,975 parks) was refused by the GitHub check for three reasons
that were the check's, not the pack's: a park POTA lists in two areas is saved under one area only; Kentucky has no
data/parkinfo file (it comes from POTA's saved list); and a park page about the 'Private John Allen' fish hatchery read as a
private file. Each is fixed; a real private-file name and a park read nowhere are still refused. Invented parks.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import gzip, json, pathlib, sys, tempfile, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_pc_upload as U  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def pack(t, pages, name='p.zip'):
    zp = t / name
    with zipfile.ZipFile(zp, 'w') as z:
        z.writestr('manifest.json', json.dumps({'kind': 'kpc-pc-upload-pack', 'format': 1, 'made': '2026-11-22T18:40:00'}))
        for area, parks in pages.items():
            z.writestr(f'pages/{area}.json', json.dumps({'area': area, 'parks': {r: dict({'ref': r}, **v) for r, v in parks.items()}}))
    return zp


with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    pi = t / 'data' / 'parkinfo'; pi.mkdir(parents=True)
    (pi / 'US-ZZ.json').write_text(json.dumps({'parks': {'US-9001': {}, 'US-9900': {}}}))
    (pi / 'US-YY.json').write_text(json.dumps({'parks': {'US-9101': {}, 'US-9900': {}}}))
    sv = t / 'data' / 'pota' / 'saved' / 'parks'; sv.mkdir(parents=True)
    (sv / 'US-KK.json.gz').write_bytes(gzip.compress(json.dumps({'data': [{'reference': 'US-9301'}]}).encode()))
    good = {'US-ZZ': {'US-9001': {}, 'US-9900': {}}, 'US-YY': {'US-9101': {}},
            'US-KK': {'US-9301': {'asked': {'url': 'https://www.fws.gov/southeast/private-john-allen/'}}}}
    P, probs = U.read_pack(pack(t, good), str(pi))
    check('a two-area park saved under one area counts for both', not [x for x in probs if 'US-YY' in x])
    check("Kentucky is checked against POTA's saved list", not [x for x in probs if 'US-KK' in x and 'POTA list' in x])
    check("a park page about the 'Private John Allen' hatchery is not a private file", not [x for x in probs if 'private file' in x])
    check('so the whole pack is taken', P is not None and not probs)
    P, probs = U.read_pack(pack(t, {'US-ZZ': {'US-9001': {'note': 'see PRIVATE-crosswalk-do-not-share.csv'}, 'US-9900': {}}}, 'q.zip'), str(pi))
    check('a real private file name is still refused', any('private file' in x for x in probs))
    P, probs = U.read_pack(pack(t, {'US-YY': {'US-9101': {}}}, 'r.zip'), str(pi))
    check('an area with a park read nowhere is still refused', any('US-YY' in x and 'read whole' in x for x in probs))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
