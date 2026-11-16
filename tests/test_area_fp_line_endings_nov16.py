#!/usr/bin/env python3
"""Nov 16 2026 (KPC owner): the per-area 2-fer fingerprint must not move with a checkout's LINE ENDINGS.

area_fp hashes the BYTES of the answer-key JSON files in the KPC-Links checkout. Git for Windows writes CRLF, so the PC saw
different bytes than the club's Linux builds and every area looked changed. (The same cause stopped the key gate on the PC
runner: KPC-Links rules_hash read CRLF rule files and called all 65 green areas stale.)

  LINKS=<KPC-Links checkout> python3 tests/test_area_fp_line_endings_nov16.py     (LINKS is optional: a made-up tree is used)
"""
import hashlib
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_fers_chain_plan as CP  # noqa: E402

FAIL = []


def ok(cond, what):
    print(('PASS ' if cond else 'FAIL ') + what)
    if not cond:
        FAIL.append(what)


def make_tree(tmp, eol=b'\n'):
    """a small stand-in for a KPC-Links checkout: one key file, one canada-bounds file, one packed outline"""
    tmp = pathlib.Path(tmp)
    for rel, text in (('data/us-key/US-RI.json', '{\n "parks": {\n  "US-1234": {"name": "a park"}\n }\n}\n'),
                      ('data/ca-key/CA-ON.json', '{\n "parks": {\n  "CA-0001": {"name": "un parc"}\n }\n}\n'),
                      ('data/canada-bounds/CA-ON.json', '{\n "bbox": [1, 2, 3, 4]\n}\n')):
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.replace('\n', eol.decode()).encode())
    ol = tmp / 'data/outlines/US-RI.geojson.gz'
    ol.parent.mkdir(parents=True, exist_ok=True)
    import gzip
    ol.write_bytes(gzip.compress(b'{"type":"FeatureCollection","features":[]}', mtime=0))
    return tmp


def main():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        lf = make_tree(pathlib.Path(td) / 'lf', b'\n')
        crlf = make_tree(pathlib.Path(td) / 'crlf', b'\r\n')
        for kind, sts in (('us-key', ['US-RI']), ('ca-key', ['CA-ON'])):
            a = CP.area_fp(lf, kind, sts, '8f5b753ce842')
            b = CP.area_fp(crlf, kind, sts, '8f5b753ce842')
            ok(a == b, f'{kind} {sts}: a CRLF checkout gives the same fingerprint ({a} vs {b})')

        # a real change to a key file still moves it
        before = CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842')
        p = lf / 'data/us-key/US-RI.json'
        p.write_bytes(p.read_bytes().replace(b'a park', b'another park'))
        ok(CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842') != before, 'a changed key file still moves the fingerprint')

        # the rules hash is still part of it
        ok(CP.area_fp(lf, 'us-key', ['US-RI'], 'other') != CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842'),
           'the 2-fer rules hash is still part of the fingerprint')

        # the packed outline is hashed as bytes: a different one moves the fingerprint
        import gzip
        before = CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842')
        (lf / 'data/outlines/US-RI.geojson.gz').write_bytes(gzip.compress(b'{"type":"FeatureCollection","features":[1]}', mtime=0))
        ok(CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842') != before, 'a changed outline file still moves the fingerprint')

        # the same files in another folder must give the same fingerprint (the PC and GitHub use different folders)
        import shutil
        other = pathlib.Path(td) / 'somewhere' / 'else' / 'KPC-Links'
        other.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(lf, other)
        ok(CP.area_fp(other, 'us-key', ['US-RI'], '8f5b753ce842') == CP.area_fp(lf, 'us-key', ['US-RI'], '8f5b753ce842'),
           'the same files in another folder give the same fingerprint')
        ok(CP.area_fp(other, 'ca-key', ['CA-ON'], '8f5b753ce842') == CP.area_fp(lf, 'ca-key', ['CA-ON'], '8f5b753ce842'),
           'ca-key too: another folder, the same fingerprint')

    ok(CP.same_lines(b'a\r\nb\rc\nd') == b'a\nb\nc\nd', 'CR LF and a lone CR both count as one line break')
    ok(CP.same_lines(b'a\nb\n') == b'a\nb\n', 'LF bytes are left exactly as they are')

    # a real checkout, when one was given: its answer-key files must already be LF, so the fingerprint is unchanged
    links = os.environ.get('LINKS')
    if links and (pathlib.Path(links) / 'data/us-key').is_dir():
        crlf_files = [p.name for p in sorted((pathlib.Path(links) / 'data/us-key').glob('US-*.json'))
                      if b'\r\n' in p.read_bytes()]
        ok(not crlf_files, f'the given checkout holds LF answer-key files ({len(crlf_files)} are CRLF)')
        f = pathlib.Path(links) / 'data/us-key/US-RI.json'
        if f.is_file():
            h = hashlib.sha256(b'x')
            h.update(b'US-RI\0' + f.read_bytes())
            h2 = hashlib.sha256(b'x')
            h2.update(b'US-RI\0' + CP.same_lines(f.read_bytes()))
            ok(h.hexdigest() == h2.hexdigest(), 'levelling changes nothing for the real US-RI key file')

    print(('ALL PASS' if not FAIL else f'{len(FAIL)} FAILED'))
    return 1 if FAIL else 0


if __name__ == '__main__':
    raise SystemExit(main())
