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
# 24 Nov (the 10:06 AM run): pypdf gives the FWS report with its columns OUT OF ORDER and note letters run into the name.
# These three lines are copied from that run's report. The total is the one number equal to the sum of the others.
REAL = ['Bon Secour 575.000.000.00 0.00 $0678.2132.340.00 6,415.33 $23,478,154 7,700.880.000.00',
        'Cahaba River 0.000.000.00 0.00 $00.000.000.00 4,853.63 $9,536,218 4,853.630.000.00',
        'EChoctaw 0.000.000.00 0.00 $00.000.000.00 0.00 $0 4,218.004,218.000.00']
got = []
for l in REAL:
    nm, nums = A.split_pdf_row(l)
    got.append((nm, nums[A.self_total(nums)]))
check('out-of-order rows: the self-checking total is found and the note letter is taken off the name',
      got == [('Bon Secour', '7,700.88'), ('Cahaba River', '4,853.63'), ('Choctaw', '4,218.00')])
check('no leading zeros: "$0678.21" is $0 + 678.21 (one way only)', A.unglue('$0678.2132.340.00') == ['$0', '678.21', '32.34', '0.00'])
check('a row of zeros has no total', A.self_total(['0.00', '0.00', '0.00']) is None)
import random as _r  # noqa: E402
_rng = _r.Random(7)


def scramble(line):
    toks = line.split(' ')
    i = next(k for k, t in enumerate(toks) if num.match(t) or t[:1] == '$' or t[:1].isdigit())
    if toks[0] in ('State',):   # the total row keeps its unit count first
        i += 2
    cells = [c for c in toks[i:] if not A.PDF_NOTE.match(c)]   # pypdf puts the note letters by the name, not among the cells
    _rng.shuffle(cells)
    return ' '.join(toks[:i] + cells)


mixed = [T.ALABAMA[0]] + [scramble(l) for l in T.ALABAMA[1:]]
got2, info2 = A.read_pdf_table(['\n'.join(T.HEAD + mixed)], T.cfg('US-AL'))
check('the whole Alabama block with every row\'s columns shuffled reads the same sizes as the plain block',
      sorted((r['name'], r['size']) for r in got2) == sorted((r['name'], r['size']) for r in plain))
check('and its total row still checks it', info2['blocks_ok'] == 1 and not info2['blocks_bad'])
# 24 Nov: the research file's hand copies name their page under "Source page"; that column was never read, so every hand
# copy looked like "page not given" (and a hand copy with no page never counts as a witness).
import json as _j, tempfile as _t  # noqa: E402
with _t.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as _f:
    _j.dump({'Acres not downloadable': [{'Park name (as the agency writes it)': 'Invented Marsh', 'Size': 10, 'Unit': 'acres',
                                         'Agency': 'Invented DNR', 'Source page': 'https://dnr.invented.gov/marsh'}]}, _f)
_h = A.load_research(_f.name)[1]
check('a hand copy keeps its "Source page" link', _h and _h[0].get('_page') == 'https://dnr.invented.gov/marsh')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
