#!/usr/bin/env python3
"""24 Nov 2026: the FWS lands report, as pypdf actually gives it on run 45444158293.

All 54 state blocks showed "no total row seen", 203 glued lines were not read, and 4 unread
lines still had a note-letter prefix. The lines below are copied from the saved PDF
(2025_annual_report_of_lands_data_tables-v2.pdf) as pypdf extracts them. Expected sizes
are the last-column totals printed in the same report (checked with a spaced layout copy).

Offline. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_acres'))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


# Real pypdf lines from Table 3, Alabama, plus a few from later states.
AL = [
    'Alabama',
    'Bon Secour 575.000.000.00 0.00 $0678.2132.340.00 6,415.33 $23,478,154 7,700.880.000.00',
    'Cahaba River 0.000.000.00 0.00 $00.000.000.00 4,853.63 $9,536,218 4,853.630.000.00',
    'EChoctaw 0.000.000.00 0.00 $00.000.000.00 0.00 $0 4,218.004,218.000.00',
    'EEufaula 0.000.000.00 0.00 $00.000.000.00 24.19 $80,000 7,953.197,929.00(1) 0.00',
    'Fern Cave 0.000.000.00 0.00 $00.000.000.00 199.23 $110,000 199.230.000.00',
    'FSA Interest AL 0.000.00842.64 0.00 $00.000.000.00 0.00 $0 842.640.00*** 0.00',
    'Grand Bay 0.000.000.00 0.00 $0895.860.000.00 1,804.69 $710,613 2,700.550.00(27) 0.00',
    'Key Cave 0.000.000.00 0.00 $00.000.000.00 1,060.00 $0 1,060.000.000.00',
    'Mountain Longleaf 0.000.000.00 0.00 $01,257.007,758.680.00 0.00 $0 9,015.680.000.00',
    'Sauta Cave 0.000.000.00 0.00 $00.000.000.00 264.00 $575,000 264.000.000.00',
    'Watercress Darter 0.000.000.00 0.00 $00.000.000.00 24.52 $230,850 24.520.000.00',
    'TWheeler 0.000.000.00 0.00 $0307.388,322.980.00 125.68 $149,700 34,430.6625,674.620.00',
    '575.000.00842.64 0.00 $03,138.4516,114.000.00 14,771.27 $34,870,535 73,262.9837,821.620.0011State Total:',
]
HEAD = ['Table 3. National Wildlife Refuges - Acres by State/Territory and Unit']


def size_of(line):
    got = A.split_pdf_row(line)
    if not got:
        return None
    name, nums = got
    j = A.self_total(nums)
    return name, (nums[j] if j is not None else None), nums


nm, sz, _ = size_of(AL[4])
check('glued part-note (1) and note letter E: Eufaula 7,953.19',
      nm == 'Eufaula (1)' and sz == '7,953.19')
nm, sz, _ = size_of(AL[6])
check('glued *** summary marks: FSA Interest AL 842.64',
      nm == 'FSA Interest AL ***' and sz == '842.64')
nm, sz, _ = size_of(AL[7])
check('glued part-note (27): Grand Bay 2,700.55',
      nm == 'Grand Bay (27)' and sz == '2,700.55')
got = A.split_pdf_row(AL[-1])
cnt, acres = (got[1][0], got[1][1:]) if got and got[1] and got[1][0].isdigit() and '.' not in got[1][0] else (None, None)
j = A.self_total(acres) if acres else None
check('State Total at the end, with unit count 11 glued on: total 73,262.98',
      got and A.PDF_TOTAL_NAME.search(got[0] or '') and cnt == '11'
      and j is not None and acres[j] == '73,262.98')

# Ambiguous $ amount vs the next acre number: $22 + 971.91, not $229 + 71.91.
DALE = 'EDale Bumpers White River 56.550.000.00 253.22 $22971.9183,721.006.00 75,390.04 $7,900,627 160,444.5245.800.00'
nm, sz, _ = size_of(DALE)
check('note letter and a $22/$229 split: Dale Bumpers White River 160,444.52',
      nm == 'Dale Bumpers White River' and sz == '160,444.52')

# $3 + 10.85, not $31 + 0.85 (Big Lake, Arkansas).
BIG = 'Big Lake 0.000.000.00 0.25 $310.851,597.348,875.60 581.12 $31,855 11,065.160.000.00'
nm, sz, _ = size_of(BIG)
check('a $3/$31 split: Big Lake 11,065.16', nm == 'Big Lake' and sz == '11,065.16')

# Two note letters run into the name, plus a part-note (Havasu, Arizona).
HAV = 'RRHavasu 0.000.000.00 0.00 $00.000.0010,004.54 40.00 $8,000 30,279.829,816.98(2) 10,418.30'
nm, sz, _ = size_of(HAV)
check('two note letters RR and part-note (2): Havasu 30,279.82',
      nm == 'Havasu (2)' and sz == '30,279.82')

CIB = 'RCibola 0.000.000.00 0.00 $00.004,171.018,372.84 192.22 $382,000 13,199.34463.27(2) 0.00'
nm, sz, _ = size_of(CIB)
check('note letter R: Cibola 13,199.34', nm == 'Cibola (2)' and sz == '13,199.34')

cfg = {'pdf_table': 'Table 3. National Wildlife Refuges', 'pdf_column': 'last', 'pdf_sum': True}
recs, info = A.read_pdf_table(['\n'.join(HEAD + AL)], cfg)
by = {r['name']: r['size'] for r in recs}
check('the real Alabama block is read and adds up to the printed State Total',
      info['blocks_ok'] == 1 and not info['blocks_bad'] and info['not_read'] == 0)
check('Alabama unit sizes match the printed last-column totals',
      by.get('Bon Secour') == '7,700.88' and by.get('Eufaula') == '7,953.19'
      and by.get('Wheeler') == '34,430.66' and by.get('Choctaw') == '4,218.00'
      and by.get('Grand Bay') == '2,700.55')
check('the FSA Interest summary is not a unit, and Eufaula keeps its (1) part note',
      'FSA Interest AL' not in by and any(r.get('name') == 'Eufaula' and r.get('_part') for r in recs))

# A leftover note-letter prefix on a line that still would not parse is a miss.
# After the fix, the four real prefixed lines in the 12-sample (Eufaula, Cibola, Havasu, Dale) all parse.
prefixed = [AL[4], CIB, HAV, DALE]
check('the 4 unread note-letter-prefix lines now parse, and the prefix is off the name',
      all(size_of(l) and size_of(l)[0][0].isupper() and size_of(l)[0][0:2] not in ('EE', 'RR', 'RC', 'ED')
          and not size_of(l)[0].startswith('EEufaula') and not size_of(l)[0].startswith('RCibola')
          and not size_of(l)[0].startswith('RRHavasu') and not size_of(l)[0].startswith('EDale')
          for l in prefixed))


# Territories use "Territory Total:" (American Samoa, Guam, Puerto Rico, Virgin Islands).
TERR = '0.000.000.00 0.00 $00.001,613.000.00 0.00 $0 1,613.000.000.001Territory Total:'
got = A.split_pdf_row(TERR)
cnt, acres = (got[1][0], got[1][1:]) if got and got[1] and got[1][0].isdigit() and '.' not in got[1][0] else (None, None)
j = A.self_total(acres) if acres else None
check('Territory Total at the end, 1 unit, total 1,613.00',
      got and 'Territory' in (got[0] or '') and cnt == '1' and j is not None and acres[j] == '1,613.00')

# A note mark run into the last acre number (Montana BIA, Hawaii N, Idaho LM).
BIA = 'Ninepipe 0.000.002,021.95 2,005.73 $1,079,8000.000.000.00 0.00 $0 4,027.680.00 BIA0.00'
nm, sz, _ = size_of(BIA)
check('note mark BIA glued to the last cell: Ninepipe 4,027.68', nm == 'Ninepipe' and sz == '4,027.68')

# Arkansas State Total: $254,003.37 glued, two money splits; the one that adds up is kept.
AR_TOT = '382.280.73380.71 264.77 $254,003.37163,455.578,881.60 216,315.40 $129,723,554 394,786.651,102.220.0010State Total:'
got = A.split_pdf_row(AR_TOT)
acres = got[1][1:] if got and got[1][0] == '10' else None
j = A.self_total(acres) if acres else None
check('Arkansas State Total: unit count 10, total 394,786.65',
      got and got[1][0] == '10' and j is not None and acres[j] == '394,786.65')

# Idaho / Colorado: a two-letter note LM run into the last acre number.
LM = 'RMinidoka 0.002.4916.15 0.00 $00.001,160.001,750.49 0.00 $0 24,617.870.00 LM21,688.74'
nm, sz, _ = size_of(LM)
check('note mark LM glued to the last cell: Minidoka 24,617.87', nm == 'Minidoka' and sz == '24,617.87')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
