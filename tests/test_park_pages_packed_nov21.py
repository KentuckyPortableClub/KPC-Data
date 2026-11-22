#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026: a page a server sends gzip- or deflate-packed (unasked) is unpacked before it is read, and a
PDF whose words cannot be read is never read as its own packed bytes. Before, both gave the park a gibberish 'name' (153 parks
on the PC run of 21 Nov) and a false 'name differs' question. Invented pages. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import gzip, pathlib, sys, zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


WANT = 'Invented Lake State Park'
html = (f'<html><head><title>{WANT}</title></head><body><h1>{WANT}</h1><p>' + 'Words about the park. ' * 60 + '</p></body></html>').encode('utf-8')
U = 'https://parks.example.gov/park/invented-lake'
check('a gzip page with its header is unpacked and read', R.visible_of(gzip.compress(html), {'content-encoding': 'gzip', 'content-type': 'text/html'}, U)['title'] == WANT)
check('a gzip page WITHOUT the header (known by its first bytes) is unpacked and read', R.visible_of(gzip.compress(html), {'content-type': 'text/html'}, U)['title'] == WANT)
check('a deflate page is unpacked and read', R.visible_of(zlib.compress(html), {'content-encoding': 'deflate'}, U)['title'] == WANT)
c = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS); raw_deflate = c.compress(html) + c.flush()
check('a raw-deflate page is unpacked and read', R.visible_of(raw_deflate, {'content-encoding': 'deflate'}, U)['title'] == WANT)
cut = gzip.compress(html)[:-40]
v = R.visible_of(cut, {'content-encoding': 'gzip'}, U)
check('a gzip page cut off by the size cap unpacks as far as it goes', v['title'] == WANT)
v = R.visible_of(b'\x1b\x00\xf8\x07garbled-brotli-bytes\x00\x91', {'content-encoding': 'br'}, U)
check('a brotli page gives no text and says why (never gibberish)', v['text'] == '' and v['title'] == '' and 'br' in v.get('note', ''))
check('a plain page is unchanged', R.visible_of(html, {'content-type': 'text/html'}, U)['title'] == WANT)
pdf = b'%PDF-1.5\n1 0 obj<</Filter/FlateDecode/Length 99>>stream\n' + zlib.compress(b'BT (hidden) Tj ET' * 50) + b'\nendstream\nendobj\n%%EOF'
v = R.visible_of(pdf, {'content-type': 'application/pdf'}, 'https://parks.example.gov/map.pdf')
check('a PDF with no readable words gives no text, not its packed bytes', v['pdf'] and v['text'] == '')
v = R.visible_of(b'Invented Lake State Park map\nThe map is being updated.\n', {'content-type': 'application/pdf'}, 'https://parks.example.gov/map.pdf')
check('a PDF address that answered plain words still reads them', 'Invented Lake State Park' in v['text'])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
