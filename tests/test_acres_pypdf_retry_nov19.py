#!/usr/bin/env python3
"""The acreage bot reads PDF lists again (owner 19 Nov 2026 9:19 PM: "Fix it and use the bots"). Offline.
pypdf is on in requirements.txt, and a --resume run reads again every item that failed only because pypdf was missing."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / '.github/scripts/draft/tools/kpc_acres'
sys.path.insert(0, str(D))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


req = (D / 'requirements.txt').read_text()
check('pypdf is installed by the tool trial (not commented out)', any(l.strip().startswith('pypdf==') for l in req.splitlines()))
try:
    import pypdf  # noqa: F401
    have = True
except ImportError:
    have = False
check('a list that failed only for want of pypdf is read again on --resume (when pypdf is here)',
      A._retry_now('failed: PDF table skipped: pypdf is not installed (pip install pypdf)') == have)
check('every other finished item stays done (read OK, robots.txt, HTTP errors)',
      not any(A._retry_now(x) for x in ('read OK (xlsx)', 'failed: blocked by robots.txt', 'failed: HTTP 404', 'skipped: page only', None)))
check("a PDF list refused only for the research's spreadsheet column name is read again",
      A._retry_now("failed: size column 'TOTAL ACRES' not found (columns: name, size, unit)"))
recs = [{'name': 'Clarks River National Wildlife Refuge', 'size': '9,000', 'unit': ''}]
cfg = {'size_col': 'TOTAL ACRES', 'name_col': 'Refuge', '_pdf': True}
try:
    rows, cols = A.extract_rows(recs, cfg)
    pdf_ok = cols.get('size') == 'size' and cols.get('name') == 'name' and len(rows) == 1
except Exception as e:  # noqa: BLE001
    pdf_ok = False; print('  ', e)
check("a PDF list's rows (name / size / unit) are read even when the research names a spreadsheet column", pdf_ok)
try:
    A.extract_rows([{'Refuge': 'x', 'acres': '5'}], {'size_col': 'TOTAL ACRES'}); still = False
except A.FetchError:
    still = True
check('a spreadsheet list with a wrong column name is still refused', still)
check('a PDF line with several numbers and no column setting is still skipped (no guessed number)',
      A.parse_pdf_line('Clarks River NWR 8,000 1,000 9,000') is None)
check('the resume loop asks _retry_now', "and not _retry_now(state['done'][it['key']])" in (D / 'kpc_acres.py').read_text())
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
