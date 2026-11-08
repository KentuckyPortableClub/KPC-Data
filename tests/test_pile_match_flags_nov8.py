#!/usr/bin/env python3
"""Nov 8 2026 (Quality Nov 7 A2): rows Quality called WRONG at zero penalty now get the match flag: no record (US-9906), unit words
(US-4092 Salem Unit, US-4343 LaSage Unit), direction words (US-9940/9941 Brush Mountain / East); exact names stay 0. auto false."""
import importlib.util, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tp', ROOT / '.github/scripts/kpc_pile_penalty.py'); TP = importlib.util.module_from_spec(spec); spec.loader.exec_module(TP)
W = {'params': TP.PARAMS}
FAILS = []


def check(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: FAILS.append(m)


def pen(ref, name, verdict, rid='', rname=''):
    return TP.type_penalty({'ref': ref, 'pota_name': name, 'verdict': verdict, 'record_id': rid, 'record_name': rname}, {'n': name}, W)


check(pen('US-9906', 'Cornelius Creek National Recreation Trail', 'SOLVED-PIN')['parts']['match'] > 0, 'US-9906 no record: flagged')
check(pen('US-4092', 'Salem Unit of Apple River Canyon State Park', 'SOLVED-JOIN', 'a', 'Apple River Canyon State Park')['parts']['match'] > 0, 'US-4092 unit: flagged')
check(pen('US-4343', 'LaSage Unit of Wolf River Bottoms State Wildlife Area', 'SOLVED-JOIN', 'b', 'Wolf River Bottoms Wildlife Area')['parts']['match'] > 0, 'US-4343 unit: flagged')
check(pen('US-9940', 'Brush Mountain Wilderness Area', 'SOLVED-JOIN', 'c', 'Brush Mountain East Wilderness')['parts']['match'] > 0, 'US-9940: flagged')
check(pen('US-9941', 'Brush Mountain East Wilderness Area', 'SOLVED-JOIN', 'd', 'Brush Mountain Wilderness')['parts']['match'] > 0, 'US-9941: flagged')
x = pen('US-4868', 'Annett State Forest', 'SOLVED-JOIN', 'e', 'Annett State Forest')
check(x['parts']['match'] == 0 and x['auto'] is False, 'exact name stays 0, auto false')
sys.exit(1 if FAILS else 0)
