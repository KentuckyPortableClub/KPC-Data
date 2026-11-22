#!/usr/bin/env python3
"""Park page reader, 21 Nov 2026: a page is read in its own character set (Content-Type charset, else <meta charset>, else
UTF-8 when valid, else Windows-1252). Before, every page was read as UTF-8 and a Latin-1 page's 'Réserve écologique' came
out with replacement marks, so its name never matched. Invented pages. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_rules as R  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


WANT = 'Réserve écologique des Invented-Arbres'
page = lambda meta: (f'<html><head>{meta}<title>{WANT}</title></head><body><h1>{WANT}</h1><p>' + 'Words. ' * 80 + '</p></body></html>')
lat = page('<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">').encode('latin-1')
check('a Latin-1 page named in its <meta> reads right', R.visible_of(lat, {'content-type': 'text/html'}, 'https://x.example/a')['title'] == WANT)
check('a Latin-1 page named in the Content-Type header reads right',
      R.visible_of(page('').encode('latin-1'), {'content-type': 'text/html; charset=ISO-8859-1'}, 'https://x.example/a')['title'] == WANT)
check('a page with no charset that is not UTF-8 reads as Windows-1252',
      R.visible_of(page('').encode('cp1252'), {'content-type': 'text/html'}, 'https://x.example/a')['title'] == WANT)
check('a UTF-8 page still reads right', R.visible_of(page('<meta charset="utf-8">').encode('utf-8'), {}, 'https://x.example/a')['title'] == WANT)
check('an unknown charset name falls back safely', R.visible_of(page('').encode('utf-8'), {'content-type': 'text/html; charset=no-such-set'},
                                                               'https://x.example/a')['title'] == WANT)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
