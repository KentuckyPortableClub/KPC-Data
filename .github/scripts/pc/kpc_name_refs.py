#!/usr/bin/env python3
"""KPC page reader: the list of parks that may have a NAME mismatch (26 Nov 2026, owner 5:57 PM: 'to save on time might be handy
to just be able to do that step only for the ones that might have name mismatches').

  * the page reader's own questions (out\\questions.csv): the page calls the park another name (NAME_DIFFERS), another kind
    (DESIGNATION_DIFFERS), a page several parks share (SHARED_PAGE), a combined or bigger unit;
  * the newest key test (..\\..\\..\\5-ANSWER-KEY-TEST\\reports\\test-*\\keys\\*.json.gz): every park the key did NOT confirm
    (outlined only, or a pin).

Writes out\\name-refs.json (park numbers only) for: kpc_park_pages.py --pc read --reextract --refs-file out\\name-refs.json
Reads local files only. Usage: kpc_name_refs.py --out out"""
import argparse, csv, gzip, json, pathlib, sys

CODES = {'NAME_DIFFERS', 'DESIGNATION_DIFFERS', 'SHARED_PAGE', 'COMBINED_UNIT', 'COMBINED_BOTH_NUMBERED', 'INSIDE_BIGGER_UNIT'}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out')
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    refs, why = set(), {'page questions': 0, 'not confirmed in the newest key test': 0}
    q = out / 'questions.csv'
    if q.is_file():
        for r in csv.DictReader(open(q, encoding='utf-8', errors='replace')):
            if r.get('code') in CODES and r.get('ref'):
                if r['ref'] not in refs: why['page questions'] += 1
                refs.add(r['ref'])
    here = pathlib.Path(__file__).resolve().parents[2]   # ...\6-TOOLS
    tests = sorted((here.parent / '5-ANSWER-KEY-TEST' / 'reports').glob('test-*'))
    newest = None
    for t in reversed(tests):
        if list((t / 'keys').glob('*.json.gz')): newest = t; break
    if newest:
        for kf in (newest / 'keys').glob('*.json.gz'):
            try:
                with gzip.open(kf, 'rt', encoding='utf-8') as fh: parks = json.load(fh).get('parks') or {}
            except Exception: continue  # noqa: BLE001
            for ref, p in parks.items():
                if isinstance(p, dict) and (p.get('match') or {}).get('status') != 'confirmed':
                    if ref not in refs: why['not confirmed in the newest key test'] += 1
                    refs.add(ref)
    (out / 'name-refs.json').write_text(json.dumps({'refs': sorted(refs)}, indent=0), encoding='utf-8')
    print(f'    {len(refs)} park(s) to read again for their names: {why["page questions"]} from the page questions, '
          f'{why["not confirmed in the newest key test"]} not confirmed in the newest key test'
          + (f' ({newest.name})' if newest else ' (no key test found)') + '.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
