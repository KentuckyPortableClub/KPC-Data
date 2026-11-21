#!/usr/bin/env python3
"""The acreage bot reads ONE named table out of a PDF that holds many (20 Nov 2026). Offline.

Why: the 19 Nov run read the Fish and Wildlife Service's yearly lands report 31 times and kept 16 "rows" each time, all
of them footnotes and total lines; 1,934 lines were skipped. A column number alone cannot read that file: its rows carry
dollar amounts and note letters, it holds ten tables, and a refuge in several states is printed once under each state.

The rows below marked REAL are copied from that report (Table 3, lands as of 9/30/2025, a U.S. government work). The
Alabama and Virgin Islands blocks are whole, with the totals the report prints. The other blocks are cut down to the rows
the checks need, so their total lines are made here from the rows kept (marked MADE)."""
import decimal, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / '.github/scripts/draft/tools/kpc_acres'
sys.path.insert(0, str(D))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


TITLE = 'Table 3. National Wildlife Refuges - Acres by State/Territory and Unit'
HEAD = [TITLE, 'Donated', 'TOTAL', 'ACRES Donated', 'PUBLIC LANDS AND WATERS EASEMENTS', 'State/Territory and Unit',
        'AGREEMENT', 'OR LEASE', 'Acres Cost ($)', 'Acquired by', 'Other', 'Federal', 'Agency']   # REAL page header lines
ALABAMA = [   # REAL: the whole block, 11 units + one summary row, and the total the report prints
    'Alabama',
    'Bon Secour 0.00 6,415.33 $23,478,154 0.00 32.34 0.00 678.21 0.00 0.00 $0 0.00 575.00 7,700.88',
    'Cahaba River 0.00 4,853.63 $9,536,218 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 4,853.63',
    'Choctaw 0.00 0.00 $0 0.00 0.00 E 4,218.00 0.00 0.00 0.00 $0 0.00 0.00 4,218.00',
    'Eufaula (1) 0.00 24.19 $80,000 0.00 0.00 E 7,929.00 0.00 0.00 0.00 $0 0.00 0.00 7,953.19',
    'Fern Cave 0.00 199.23 $110,000 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 199.23',
    'FSA Interest AL *** 0.00 0.00 $0 0.00 0.00 0.00 0.00 842.64 0.00 $0 0.00 0.00 842.64',
    'Grand Bay (27) 0.00 1,804.69 $710,613 0.00 0.00 0.00 895.86 0.00 0.00 $0 0.00 0.00 2,700.55',
    'Key Cave 0.00 1,060.00 $0 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 1,060.00',
    'Mountain Longleaf 0.00 0.00 $0 0.00 7,758.68 0.00 1,257.00 0.00 0.00 $0 0.00 0.00 9,015.68',
    'Sauta Cave 0.00 264.00 $575,000 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 264.00',
    'Watercress Darter 0.00 24.52 $230,850 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 24.52',
    'Wheeler 0.00 125.68 $149,700 0.00 8,322.98 T 25,674.62 307.38 0.00 0.00 $0 0.00 0.00 34,430.66',
    'State Total: 11 0.00 14,771.27 $34,870,535 0.00 16,114.00 37,821.62 3,138.45 842.64 0.00 $0 0.00 575.00 73,262.98']
VIRGIN = [   # REAL: the whole block and its printed total
    'Virgin Islands',
    'Buck Island 46.07 0.00 $0 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 46.07',
    'Green Cay 0.00 13.77 $250,000 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 13.77',
    'Sandy Point 0.00 530.31 $3,534,370 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 530.31',
    'Territory Total: 3 46.07 544.08 $3,784,370 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 590.15']
R = {   # REAL rows, by the state heading they are printed under
    'Alaska': ['Alaska Maritime 3,291,639.47 44,021.53 $8,646,537 AF,N 59,099.00 0.00 0.00 65.24 0.00 0.00 $0 26,983.86 6.59 3,421,815.69'],
    'Florida': ['Okefenokee (1) 0.00 3,648.58 $52,636 0.00 0.00 0.00 0.00 0.00 0.00 $0 46.34 0.00 3,694.92'],
    'Georgia': ['Eufaula (5)* 0.00 0.00 $0 0.00 0.00 E 3,231.00 0.00 0.00 0.00 $0 0.00 0.00 3,231.00',
                'FSA Interest GA *** 0.00 0.00 $0 0.00 886.38 0.00 0.00 4,058.14 30.00 $0 0.00 0.00 4,974.52',
                'Okefenokee (6)* 0.00 377,732.16 $5,572,635 0.00 1,860.44 0.00 23,648.66 0.00 0.00 $0 0.00 0.00 403,241.26'],
    'Illinois': ['Upper Mississippi River (9) 65.15 2,985.54 $190,620 0.00 4,057.37 E,A 26,243.73 0.00 0.00 0.19 $1 0.00 0.00 33,351.98'],
    'Iowa': ['Upper Mississippi River (13)* 333.66 20,886.39 $1,876,327 0.00 106.89 E 30,315.00 0.57 0.00 0.05 $0 0.00 0.00 51,642.56'],
    'Minnesota': ['Upper Mississippi River (18)* 241.58 19,144.68 $4,365,565 0.00 0.00 E 15,420.77 213.07 0.00 0.00 $0 0.42 92.97 35,113.49'],
    'North Dakota': ['Buffalo Lake 23.80 0.00 $0 0.00 0.00 0.00 0.00 0.00 0.00 $0 1,539.92 0.00 1,563.72'],
    'Texas': ['Buffalo Lake 0.00 0.00 $0 0.00 7,663.93 0.00 0.00 0.23 0.00 $0 0.00 0.00 7,664.16'],
    'Wisconsin': ['Upper Mississippi River (25)* 655.57 49,809.28 $5,482,531 0.00 0.00 E 40,341.00 123.43 0.00 10.84 $5,050 60.49 1,140.50 92,141.11'],
}
OTHER_TABLES = [   # REAL rows of other tables in the same PDF: they must never be read as refuge sizes
    ['Table 3A. NWRS-managed National Monument Areas and Associated National Wildlife Refuges - Acres by State/Territory and Unit',
     'Alaska Maritime NWR (AK) ** 4,950.00 0.00 $0 0.00 0.00 0.00 0.00 0.00 0.00 0.00 $0 0.00 0.00 4,950.00'],
    ['Table 9. Migratory Waterfowl Refuges on Federal Water Resource Projects (Units also included in Table 3)',
     'Alabama', 'Choctaw 4,218.00 0.00 0.00 0.00 4,218.00', 'Eufaula 7,929.00 0.00 0.00 24.19 7,953.19'],
    ['Table 8. Wilderness Areas in National Wildlife Refuges (Units also included in Table 3)',
     'Leadville* Mount Massive 2,560.00 96-560 12/22/80', 'State Total 2,560.00'],
]


def last(row):
    return decimal.Decimal(row.split(' ')[-1].replace(',', ''))


def block(state, rows, cont=False):
    """A cut-down block: the state heading, the REAL rows kept, and a total line MADE from those rows."""
    tot = sum((last(r) for r in rows), decimal.Decimal(0))
    units = sum(1 for r in rows if '***' not in r and ')*' not in r)
    return [state + (' (Continued)' if cont else '')] + rows + [f'State Total: {units} 0.00 {tot:,.2f}']


def pages(drop=None, change=None):
    """Three Table 3 pages and three pages of other tables. drop: a row left out; change: (old, new) text in one row."""
    def fix(lines):
        out = [l for l in lines if l != drop]
        return [l.replace(*change) if change and change[0] in l else l for l in out]
    cut = {st: block(st, rows) for st, rows in R.items()}   # the made totals stay those of the full cut-down blocks
    p1 = HEAD + fix(ALABAMA) + fix(cut['Alaska'])
    p2 = HEAD + fix(cut['Florida']) + fix(cut['Georgia']) + fix(cut['Illinois']) + fix(cut['Iowa']) + fix(cut['Minnesota'])
    p3 = HEAD + fix(cut['North Dakota']) + fix(cut['Texas']) + fix(VIRGIN) + fix(cut['Wisconsin']) + ['(1) Also in Georgia', '26']
    return ['\n'.join(p) for p in (p1, OTHER_TABLES[0], p2, OTHER_TABLES[1], p3, OTHER_TABLES[2])]


def cfg(area=None, **kw):
    c = {'pdf_table': 'Table 3. National Wildlife Refuges', 'pdf_column': 'last', 'pdf_sum': 'yes', 'area': area,
         'unit': 'acres', 'kind': 'nwr', 'agency': 'U.S. Fish and Wildlife Service', 'url': 'https://example.org/lands.pdf'}
    c.update(kw)
    return c


# ---- 1. one row --------------------------------------------------------------------------------------------------
name, nums = A.split_pdf_row(ALABAMA[-2])
check('a row with a dollar cell and a note letter is read: Wheeler, 11 acre numbers, the last is 34,430.66',
      name == 'Wheeler' and len(nums) == 11 and nums[-1] == '34,430.66' and '$149,700' not in nums and 'T' not in nums)
name, nums = A.split_pdf_row(R['Alaska'][0])
check('a row with two note letters (AF,N) is read: Alaska Maritime 3,421,815.69', name == 'Alaska Maritime' and nums[-1] == '3,421,815.69')
check("a line with a cell that is not a number is not read (Table 8: a law number and a date)", A.split_pdf_row(OTHER_TABLES[2][1]) is None)
check('a footnote line has no number cell: not a row', A.split_pdf_row('(1) Also in Georgia') is None)
check("state headings: full names only, '(Continued)' dropped; a stray two-letter 'OR' is never Oregon",
      A.pdf_heading('Alabama') == 'US-AL' and A.pdf_heading('Arizona (Continued)') == 'US-AZ' and A.pdf_heading('Virgin Islands') == 'US-VI'
      and A.pdf_heading('OR') is None and A.pdf_heading('Other') is None and A.pdf_heading('OR LEASE') is None)

# ---- 2. the table ------------------------------------------------------------------------------------------------
recs, info = A.read_pdf_table(pages(), cfg())
by = {}
for r in recs:
    by.setdefault(r['name'], []).append(r)


def note(r, k):
    return (r.get('_part') or {}).get(k, 'no part note')


check('only the three pages that carry the Table 3 title are read (not Table 3A, 8 or 9)', info['pages'] == 3)
check('every row read: 0 lines not read, 0 rows not adding up', info['not_read'] == 0 and info['not_adding_up'] == 0)
check("the Alabama rows add up to the State Total the report prints (73,262.98), the Virgin Islands rows to 590.15; all 11 blocks add up",
      info['adds_up'] and info['blocks_ok'] == 11 and not info['blocks_bad'])
check("the unit counts agree with the list's own (Alabama 11, Virgin Islands 3)", not info['count_notes'])
check('Bon Secour is 7,700.88 acres in Alabama', [(r['size'], r['state']) for r in by.get('Bon Secour', [])] == [('7,700.88', 'US-AL')])
check('summary rows (FSA Interest ***) and total rows are never units', not any('FSA' in n or 'Total' in n for n in by))
check('Table 9 gave nothing: Choctaw appears once, with its Table 3 size', [r['size'] for r in by.get('Choctaw', [])] == ['4,218.00'])
check('Table 3A gave nothing: no "Alaska Maritime NWR (AK)" row', 'Alaska Maritime NWR (AK)' not in by and len(by.get('Alaska Maritime', [])) == 1)
check('Eufaula is one unit printed under two states: both parts kept, marked (1) and (5)*',
      sorted((r['state'], note(r, 'note'), note(r, 'why')) for r in by.get('Eufaula', [])) == [('US-AL', '(1)', None), ('US-GA', '(5)*', None)])
check('Buffalo Lake in Texas and Buffalo Lake in North Dakota carry no note: two separate refuges',
      sorted((r['state'], r['size']) for r in by.get('Buffalo Lake', [])) == [('US-ND', '1,563.72'), ('US-TX', '7,664.16')] and not any('_part' in r for r in by['Buffalo Lake']))
check("Grand Bay (27) has its other state's row missing here: marked, with the reason, so it can get no size",
      [note(r, 'why') for r in by.get('Grand Bay', [])] == ['only one of its rows was read'])
check('24 rows are 19 units (Eufaula 2 rows, Okefenokee 2, Upper Mississippi River 4)', info['rows'] == 24 and info['units'] == 19 and info['units_in_several_places'] == 3)

# ---- 3. fail closed ----------------------------------------------------------------------------------------------
recs2, info2 = A.read_pdf_table(pages(change=('7,700.88', '7,800.88')), cfg())
check('a row whose numbers do not add up to its size is not read (Bon Secour with one digit changed)',
      info2['not_adding_up'] == 1 and not any(r['name'] == 'Bon Secour' for r in recs2))
check('... and its block then misses the printed total, so the table does not add up', not info2['adds_up'] and [b['where'] for b in info2['blocks_bad']] == ['US-AL'])
check('... and every unit printed in several places says so (no size from a table that does not add up)',
      [r for r in recs2 if '_part' in r] and all(note(r, 'why') for r in recs2 if '_part' in r))
check('the only slack in a sum is rounding: 11 printed numbers may be 6 cents from their total, not 7; a 12-row block 7 cents, not 8',
      A.pdf_adds_up('7,700.88', '7,700.94', 11) and not A.pdf_adds_up('7,700.88', '7,700.95', 11)
      and A.pdf_adds_up('73,262.98', '73,263.05', 12) and not A.pdf_adds_up('73,262.98', '73,263.06', 12))
_, info_r = A.read_pdf_table(pages(change=('0.00 575.00 7,700.88', '0.00 575.00 7,701.88')), cfg())
check('a row one acre out is not read (Bon Secour printed as 7,701.88)', info_r['not_adding_up'] == 1 and not info_r['adds_up'])
recs3, info3 = A.read_pdf_table(pages(drop=R['Wisconsin'][0]), cfg())
check("a lost part is caught: without Wisconsin's row the Wisconsin block misses its total",
      not info3['adds_up'] and [b['where'] for b in info3['blocks_bad']] == ['US-WI']
      and [note(r, 'why') for r in recs3 if r['name'] == 'Upper Mississippi River'] == ['the table did not add up to its own totals, so a part may be missing'] * 3)
gt = pages()
gt[-2] += '\nGrand Total: 19 0.00 4,132,287.54'   # MADE: the 24 unit rows and 2 summary rows of this file add to 4,132,287.54
_, info_g = A.read_pdf_table(gt, cfg())
check("a Grand Total row is read as the list's own total of everything: 19 units, and the rows add to it",
      info_g.get('grand') == {'list_total': '4132287.54', 'list_units': 19, 'rows_add_to': '4132287.54'} and info_g['adds_up'])
recs4, info4 = A.read_pdf_table(pages(), cfg(pdf_sum=None, pdf_column=None))
check('with no column named, a row with several numbers is still not read (no guessed number)', not recs4 and info4['not_read'] >= 24)
recs5, info5 = A.read_pdf_table(pages(), cfg(pdf_table='Table 99. No such table'))
check('a title no page carries reads nothing', info5['pages'] == 0 and not recs5)

# ---- 4. a research row for one state -----------------------------------------------------------------------------
ga, _ = A.read_pdf_table(pages(), cfg('US-GA'))
check("Georgia's row of the research file takes Georgia's rows and every part of the units it shares (Eufaula from Alabama, Okefenokee from Florida), nothing else",
      sorted((r['name'], r['state']) for r in ga) == [('Eufaula', 'US-AL'), ('Eufaula', 'US-GA'), ('Okefenokee', 'US-FL'), ('Okefenokee', 'US-GA')])

# ---- 5. rows -> parks --------------------------------------------------------------------------------------------
P = A.Parks()
NWR = 'National Wildlife Refuge'
for ref, nm, areas_ in (('US-0136', 'Bon Secour', ['US-AL']), ('US-0139', 'Eufaula', ['US-AL', 'US-GA']),
                        ('US-0263', 'Okefenokee', ['US-GA']),                       # the club's park file lists it in Georgia only
                        ('US-0384', 'Grand Bay', ['US-AL']), ('US-0546', 'Buffalo Lake', ['US-TX']),
                        ('US-4236', 'Upper Mississippi River', ['US-IA', 'US-IL', 'US-MN', 'US-WI'])):
    for a in areas_:
        P.add(ref, f'{nm} {NWR}', NWR, 30.0, -88.0, a)
P.add('US-7703', 'Buffalo Lake Wildlife Management Area', 'Wildlife Management Area', 47.9, -99.9, 'US-ND')
M = A.Matcher(P, None)
ALL = sorted({a for v in P.idx for a in [v]} | {'US-FL'})


def run(c, pg, areas=ALL):
    recs, info = A.read_pdf_table(pg, c)
    c = dict(c, _pdf=True, _pdf_table=info)
    rows, _ = A.extract_rows(recs, c)
    res = A.new_result('list', c['agency'], c['area'], c['url'], '2026-11-20', A.pdf_table_status(info))
    for row in rows:
        A.process_row(res, row, c.get('area'), c.get('kind'), c['url'], M, areas, None)
    A.settle_parts(res, rows, c['url'])
    return res


Z = {'acres': None, 'parts': None, 'flags': ['no size given']}
res = run(cfg(), pages())
F = A.merge([res], P)
check('Bon Secour NWR (US-0136): 7,700.88 acres, one row', F.get('US-0136', Z)['acres'] == 7700.88 and F.get('US-0136', Z)['parts'] == 1)
check('Eufaula NWR (US-0139): Alabama 7,953.19 + Georgia 3,231.00 = 11,184.19 acres, two parts',
      F.get('US-0139', Z)['acres'] == 11184.19 and F.get('US-0139', Z)['parts'] == 2 and not F.get('US-0139', Z)['flags'])
check("Okefenokee NWR (US-0263): Georgia 403,241.26 + Florida 3,694.92 = 406,936.18, though the park file lists it in Georgia only",
      F.get('US-0263', Z)['acres'] == 406936.18 and F.get('US-0263', Z)['parts'] == 2)
check('Upper Mississippi River NWR (US-4236): four states, 212,249.14 acres',
      F.get('US-4236', Z)['acres'] == 212249.14 and F.get('US-4236', Z)['parts'] == 4 and not F.get('US-4236', Z)['flags'])
check("Buffalo Lake NWR in Texas (US-0546): 7,664.16; North Dakota's Buffalo Lake is another refuge and is not added",
      F.get('US-0546', Z)['acres'] == 7664.16 and F.get('US-0546', Z)['parts'] == 1)
check('the North Dakota wildlife management area of the same name gets nothing (a refuge row never sizes a WMA)', 'US-7703' not in F)
check('Grand Bay NWR (US-0384) gets no size: one of its two rows is missing, and the reason is in the unmatched list',
      'US-0384' not in F and any('Grand Bay' in u['row_name'] and 'only one of its rows was read' in u['why'] for u in res['unmatched']))
res_bad = run(cfg(), pages(drop=R['Wisconsin'][0]))
F_bad = A.merge([res_bad], P)
check('when the table does not add up, NO unit printed in several places gets a size (Upper Mississippi, Eufaula, Okefenokee), single ones still do',
      not {'US-4236', 'US-0139', 'US-0263'} & set(F_bad) and F_bad.get('US-0136', Z)['acres'] == 7700.88)
res_ga = run(cfg('US-GA'), pages())
F_ga = A.merge([res_ga], P)
check("Georgia's research row alone gives the same whole sizes (Eufaula 11,184.19, Okefenokee 406,936.18) and nothing for other states",
      {k: v['acres'] for k, v in F_ga.items()} == {'US-0139': 11184.19, 'US-0263': 406936.18})
res_ky = run(cfg(), pages(), areas=['US-AL'])
F_ky = A.merge([res_ky], P)
check('a run limited to Alabama still gives Eufaula its whole size (the Georgia part belongs to the same unit)',
      F_ky.get('US-0139', {}).get('acres') == 11184.19 and 'US-0263' not in F_ky)
P2 = A.Parks()
P2.add('US-0139', f'Eufaula {NWR}', NWR, 31.9, -85.1, 'US-AL')
P2.add('US-9999', f'Eufaula {NWR}', NWR, 31.9, -85.1, 'US-GA')
M, keep = A.Matcher(P2, None), M
F_two = A.merge([run(cfg(), pages())], P2)
M = keep
check('parts that point to two different parks are not used at all', not F_two)
check('the status line says what was read and that the table adds up',
      res['status'].startswith('read OK (pdf table "Table 3. National Wildlife Refuges": 3 pages, 24 rows read, 0 lines not read, 0 rows not adding up; all 11 blocks add up')
      and 'DO NOT add up' in res_bad['status'] and 'US-WI' in res_bad['status'])

# ---- 6. settings and the re-read ---------------------------------------------------------------------------------
c = A.row_to_cfg({'Area': 'AL', 'Agency': 'U.S. Fish and Wildlife Service', 'Direct download (CSV / XLSX / PDF)': 'https://example.org/lands.pdf',
                  'Size column name': 'TOTAL ACRES', 'Unit (acres / hectares / km²)': 'acres', 'Status': 'FOUND',
                  'PDF table': 'Table 3. National Wildlife Refuges', 'PDF column': 'last', 'PDF sum check': 'yes',
                  'Park kind': 'national wildlife refuge'})
check('the research row carries the settings: table title, last column, sum check, kind = national wildlife refuge',
      c['pdf_table'] == 'Table 3. National Wildlife Refuges' and A.pdf_pos(c) == 'last' and A._yes(c['pdf_sum']) and c['kind'] == 'nwr' and c['area'] == 'US-AL')
old = 'read OK (pdf); 1934 PDF lines skipped as unsure'
check('a list last read the old way is read again once its research row names the table', A._reread_table(old, c))
check('read as a table, it stays done', not A._reread_table(res['status'], c))
check('a list with no table named is not read again; neither is a failed one', not A._reread_table(old, {'pdf_column': None}) and not A._reread_table('failed: HTTP 404', c))
src = (D / 'kpc_acres.py').read_text()
check('the resume loop asks both: the 19 Nov rule as it was, and the table rule',
      "and not _retry_now(state['done'][it['key']])" in src and "and not _reread_table(state['done'][it['key']], it.get('cfg'))" in src)
check('the list step settles the units printed in several places', "        settle_parts(res, rows, res['source_url'])" in src)
check('a PDF list with no table named is read exactly as before (several numbers, no column: skipped)',
      A.parse_pdf_line('Clarks River NWR 8,000 1,000 9,000') is None and A.parse_pdf_line('Blanton Forest   3,124 acres') == ('Blanton Forest', '3,124', 'acres'))

# ---- 7. through a real PDF file (only where pypdf is installed) ---------------------------------------------------
try:
    import pypdf  # noqa: F401
    have = True
except ImportError:
    have = False
if have:
    def esc(t):
        return t.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    objs, kids = ['<< /Type /Catalog /Pages 2 0 R >>', None, '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'], []
    for text in pages():
        content = 'BT /F1 7 Tf 30 760 Td 9 TL ' + ' '.join(f'({esc(t)}) Tj T*' for t in text.split('\n')) + ' ET'
        objs.append(f'<< /Length {len(content)} >>\nstream\n{content}\nendstream')
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {len(objs)} 0 R >>')
        kids.append(f'{len(objs)} 0 R')
    objs[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} >>'
    out, offs = '%PDF-1.4\n', []
    for i, o in enumerate(objs):
        offs.append(len(out))
        out += f'{i + 1} 0 obj\n{o}\nendobj\n'
    xref = len(out)
    out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n' + ''.join(f'{o:010d} 00000 n \n' for o in offs)
    out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'
    data = out.encode('latin-1')

    class Fetch:
        requests = 0

        def get(self, url):
            return data
    res_pdf = A.run_list_item(cfg(), Fetch(), M, '2026-11-20', ALL)
    F_pdf = A.merge([res_pdf], P)
    check('the same six pages as a real PDF file, read with pypdf through the whole list step, give the same sizes',
          {k: v['acres'] for k, v in F_pdf.items()} == {k: v['acres'] for k, v in F.items()} and res_pdf['status'] == res['status'])
    try:
        st = A.run_list_item(cfg(pdf_table='Table 99. No such table'), Fetch(), M, '2026-11-20', ALL)['status']
    except Exception as e:  # noqa: BLE001
        st = f'raised {e}'
    check('a title no page carries is a failed list with the reason, never a silent "read OK"', st.startswith('failed: pdf table: no page carries the title'))
    legacy = A.read_pdf_records(data, {})
    check('with no table named, the same file is read the old way (one name + one number lines only)',
          all(set(r) == {'name', 'size', 'unit'} for r in legacy) and not any(r['name'] == 'Bon Secour' for r in legacy))

    # ---- 8. a whole run, the way the bot runs: the old way first, then the settings arrive, then --resume ----------
    import argparse, json, tempfile

    def park(nm, typ=NWR):
        return [f'{nm} {typ}', '', typ, '', '', 30.0, -88.0]
    PARKINFO = {'US-AL': {'US-0136': park('Bon Secour'), 'US-0139': park('Eufaula'), 'US-0384': park('Grand Bay')},
                'US-GA': {'US-0139': park('Eufaula'), 'US-0263': park('Okefenokee')}, 'US-TX': {'US-0546': park('Buffalo Lake')},
                'US-ND': {'US-7703': park('Buffalo Lake', 'Wildlife Management Area')}}
    for st_ in ('US-IA', 'US-IL', 'US-MN', 'US-WI'):
        PARKINFO[st_] = {'US-4236': park('Upper Mississippi River')}
    SET = {'PDF table': 'Table 3. National Wildlife Refuges', 'PDF column': 'last', 'PDF sum check': 'yes',
           'Park kind': 'national wildlife refuge'}

    def research(**kw):
        return {'Agencies': [dict({'Area': a, 'Agency': 'U.S. Fish and Wildlife Service', 'Status': 'FOUND',
                                   'Direct download (CSV / XLSX / PDF)': 'https://lands.example/report.pdf',
                                   'Size column name': 'TOTAL ACRES', 'Unit (acres / hectares / km²)': 'acres'}, **kw)
                             for a in ('AL', 'GA', 'US (all)')]}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'parkinfo').mkdir()
        for a_, pk in PARKINFO.items():
            (tmp / 'parkinfo' / f'{a_}.json').write_text(json.dumps({'parks': pk}))
        rf, calls, reads = tmp / 'acres-research.json', [], []

        def transport(url, headers):
            calls.append(url)
            return (200, {}, b'User-agent: *\nDisallow:\n') if url.endswith('/robots.txt') else (200, {}, data)
        real_table = A.read_pdf_table

        def counting(pg, c):
            reads.append(c.get('area'))
            return real_table(pg, c)
        A.read_pdf_table = counting
        ns = argparse.Namespace(inp=str(rf), acres_file=None, out=str(tmp / 'out'), parkinfo=str(tmp / 'parkinfo'), keys=None,
                                areas=None, max_minutes=5, resume=False, limit=None, cache=None, answer_key=None,
                                offline=False, no_county_check=True, quiet=True)

        def go(resume):
            code = A.run(argparse.Namespace(**dict(vars(ns), resume=resume)), transport=transport, sleep=lambda s: None, gap=0.0)
            done = json.loads((tmp / 'out' / 'state.json').read_text())['done']
            return code, done, json.loads((tmp / 'out' / 'acres.json').read_text())
        rf.write_text(json.dumps(research()))
        code1, st1, ac1 = go(False)
        check('the old way (no table named): three lists "read OK (pdf); N PDF lines skipped as unsure", no refuge gets a size, the table reader is not used',
              code1 == 0 and len(st1) == 3 and all(v.startswith('read OK (pdf); ') for v in st1.values()) and not ac1 and not reads)
        rf.write_text(json.dumps(research(**SET)))
        n_calls = len(calls)
        code2, st2, ac2 = go(True)
        check('once the research rows name the table, --resume reads the three lists again, as a table',
              code2 == 0 and all(v.startswith('read OK (pdf table "Table 3. National Wildlife Refuges": 3 pages, 24 rows read') for v in st2.values())
              and sorted(map(str, reads)) == ['None', 'US-AL', 'US-GA'])
        check('... with no new download (the saved copy is read)', len(calls) == n_calls)
        want = {'US-0136': 7700.88, 'US-0139': 11184.19, 'US-0263': 406936.18, 'US-0546': 7664.16, 'US-4236': 212249.14}
        check("... and the sizes are the list's: Bon Secour 7,700.88; Eufaula 11,184.19; Okefenokee 406,936.18; Buffalo Lake (Texas) 7,664.16; "
              'Upper Mississippi River 212,249.14; nothing for Grand Bay or the North Dakota WMA',
              {k: v['acres'] for k, v in ac2.items()} == want)
        check('every size says where it came from (agency, link, the rows added)',
              all(v['agency'] == 'U.S. Fish and Wildlife Service' and v['source_url'].endswith('report.pdf') and v['why'] for v in ac2.values())
              and 'Eufaula (US-AL part) + Eufaula (US-GA part)' == ac2.get('US-0139', {}).get('record_name'))
        rep = (tmp / 'out' / 'report.md').read_text()
        check('the report shows the table once, with what was read and that all 11 blocks add up',
              rep.count('## PDF tables') == 1 and rep.count('- "Table 3. National Wildlife Refuges" | https://lands.example/report.pdf') == 1
              and "blocks that add up to the list's own total row: 11; that do not: 0" in rep and '19 units in 24 rows' in rep)
        um = (tmp / 'out' / 'unmatched.csv').read_text()
        check('the unmatched list holds no total line and no footnote any more, and says why Grand Bay got no size',
              'State Total' not in um and 'Also in' not in um and 'Grand Bay' in um and 'only one of its rows was read' in um)
        del reads[:]
        code3, st3, ac3 = go(True)
        check('a third run reads nothing again and changes nothing', code3 == 0 and not reads and st3 == st2 and ac3 == ac2 and len(calls) == n_calls)
        A.read_pdf_table = real_table
else:
    print('NOTE pypdf is not installed here: the real-PDF-file checks were skipped; the table reader was tested on page text')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
