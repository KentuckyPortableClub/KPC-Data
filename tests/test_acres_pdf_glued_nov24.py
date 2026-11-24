#!/usr/bin/env python3
"""24 Nov 2026: the acreage bot's PDF reader gets the FWS lands report's text with cells run together
('831,847.24406,081.28'): the 22 Nov run read 0 rows (716 lines not read). A run-together token is split ONLY when there is
exactly one way to split it into two-decimal acre numbers and $ amounts; the table's own sums still check every row kept.
Offline. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_acres'))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


U = A.unglue
check('two acre numbers run together are split', U('831,847.24406,081.28') == ['831,847.24', '406,081.28'])
check('a $ amount run into an acre number is split', U('$149,7000.00') == ['$149,700', '0.00'])
check('0.00 then 125.68', U('0.00125.68') == ['0.00', '125.68'])
check('a token with no two-decimal split is left alone (not read)', U('1234.00') is None and U('12.3') is None)
check('a single number is not "split"', U('12.34') is None)
check('a name word is never touched', A.split_pdf_row('Area 51 Refuge 0.00 12.00') is None or A.split_pdf_row('Area 51 Refuge 0.00 12.00')[0] != '')

import types  # noqa: E402
_src = (ROOT / 'tests/test_acres_pdf_table_nov20.py').read_text(encoding='utf-8')
T = types.SimpleNamespace()
_ns = {'A': A, '__name__': 'rows'}
exec(compile(_src[_src.index('TITLE = '):_src.index('# ---- 1.')], 'rows', 'exec'), _ns)   # its REAL rows only, not its checks
T.__dict__.update(_ns)
num = re.compile(r'^\$?\d[\d,]*\.\d{2}$|^\$\d[\d,]*$')


def glue(line):
    """Run together every pair of neighbouring cells that are two-decimal numbers or $ amounts (as pypdf gives them)."""
    out = []
    for t in line.split(' '):
        if out and num.match(t) and num.match(re.split(r'(?<=\d)(?=\$)', out[-1])[-1]) and not re.fullmatch(r'\d{1,5}', out[-1]):
            out[-1] += t
        else:
            out.append(t)
    return ' '.join(out)


glued = [glue(l) for l in T.ALABAMA]
check('the test really glues the rows', any(re.search(r'\.\d{2}\d', l) for l in glued))
plain, _ = A.read_pdf_table(['\n'.join(T.HEAD + T.ALABAMA)], T.cfg('US-AL'))
got, info = A.read_pdf_table(['\n'.join(T.HEAD + glued)], T.cfg('US-AL'))
check('the glued Alabama block reads the same rows and sizes as the plain one',
      plain and sorted((r['name'], r['size']) for r in got) == sorted((r['name'], r['size']) for r in plain))
check('and still adds up to its printed total', info['blocks_ok'] == 1 and not info['blocks_bad'])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
