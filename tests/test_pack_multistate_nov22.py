#!/usr/bin/env python3
"""22 Nov 2026: a park POTA lists in two areas (a trail through two states) is saved once, in ONE area's page-facts file. The
PC upload packer called the other area "not read whole" and left it out (236 such parks kept 43 areas out of the owner's pack).
Now a park read under another area counts as read. An area with a park read nowhere is still left out. Invented parks.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import datetime, json, pathlib, sys, tempfile, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/pc'))
import kpc_upload_pack as K  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def w(p, o):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o), encoding='utf-8')


fact = lambda r, a: {'ref': r, 'area': a, 'page': {'kind': 'html'}}
with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    w(t / 'pi' / 'US-ZZ.json', {'parks': {'US-9001': {}, 'US-9900': {}}})          # US-9900 = a trail in both areas
    w(t / 'pi' / 'US-YY.json', {'parks': {'US-9101': {}, 'US-9900': {}}})
    w(t / 'pi' / 'US-XX.json', {'parks': {'US-9201': {}, 'US-9999': {}}})          # US-9999 read nowhere
    w(t / 'facts' / 'US-ZZ.json', {'area': 'US-ZZ', 'parks': {'US-9001': fact('US-9001', 'US-ZZ'), 'US-9900': fact('US-9900', 'US-ZZ')}})
    w(t / 'facts' / 'US-YY.json', {'area': 'US-YY', 'parks': {'US-9101': fact('US-9101', 'US-YY')}})
    w(t / 'facts' / 'US-XX.json', {'area': 'US-XX', 'parks': {'US-9201': fact('US-9201', 'US-XX')}})
    zp, c, why = K.make_pack(t / 'out', t / 'facts', '', '', '', None, parkinfo=t / 'pi', now=datetime.datetime(2026, 11, 22, 18, 40))
    names = zipfile.ZipFile(zp).namelist() if zp else []
    check('an area whose two-state park was saved under the other area is packed', 'pages/US-YY.json' in names)
    check('the area holding that park is packed too', 'pages/US-ZZ.json' in names)
    check('an area with a park read nowhere is still left out', 'pages/US-XX.json' not in names)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
