#!/usr/bin/env python3
"""Test helper (not part of the checker): compare a checker run's US-KY verdicts with the club's own KY spot-check sheet
(KPC_2fer_spotcheck_KY.xlsx, sheet 'Live 2-fers', column 'Overlap on official maps?'). Matches on sorted refs + kind,
nearest spot. Needs openpyxl.  Usage: compare_ky_spotcheck.py <xlsx> <out>/US-KY.json"""
import collections, json, math, sys
import openpyxl

wb = openpyxl.load_workbook(sys.argv[1], read_only=True)
rows = list(wb['Live 2-fers'].iter_rows(values_only=True))
hdr = rows[0]; H = {h: i for i, h in enumerate(hdr)}
sheet = collections.defaultdict(list)
for r in rows[1:]:
    if r[H['State']] != 'KY' or not r[H['Parks']]:
        continue
    refs = tuple(sorted(x.strip() for x in r[H['Parks']].split('+')))
    sheet[(refs, r[H['Kind']])].append((r[H['Spot lat']], r[H['Spot lon']], r[H['Overlap on official maps?']], r[H['Why / notes']]))
doc = json.load(open(sys.argv[2]))
tab = collections.Counter(); lines = []
for rid, row in doc['rows'].items():
    refs = tuple(sorted(row['refs'])); kind = row['kind'] if row['kind'] != 'water-only' else 'area'
    lat, lon = map(float, rid.rsplit('@', 1)[1].split(','))
    c = sheet.get((refs, kind)) or sheet.get((refs, row['kind'])) or []
    if not c:
        tab[(row['verdict'], 'not in sheet')] += 1; continue
    best = min(c, key=lambda s: math.hypot((s[0] or 0) - lat, ((s[1] or 0) - lon) * 0.8))
    tab[(row['verdict'], best[2])] += 1
    if not (row['verdict'] == 'CONFIRMED') == (best[2] == 'CONFIRMED'):
        lines.append(f"{rid}\t{row['kind']}\ttool={row['verdict']}\tsheet={best[2]}\t{(best[3] or '')[:110]}")
print('tool verdict x sheet "Overlap on official maps?"')
for k, v in sorted(tab.items()):
    print(f'  {k[0]:<15} {str(k[1]):<14} {v}')
print('\nDisagreements (CONFIRMED vs not):'); print('\n'.join(sorted(lines)))
