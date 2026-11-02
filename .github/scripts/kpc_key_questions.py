#!/usr/bin/env python3
"""KEY QUESTIONS FOR A PERSON (chat 10, Oct 29 2026; chat 2's RULE SHEET G step 2 'the queue'; Brandon 12:14 + 12:18 PM rulings).
The US key HOLDS a similar-name piece it cannot place (rule G-1: more than 2 km from the pin and from every passed piece). Each held
piece becomes ONE question in the waiting room: 'is this piece part of that park on the agency's own map? YES / NO'. Chat 11
answers in the JSON (answer + checked_by + how), chat 2 rechecks and writes the result to data/us-key/overrides.json (join / no).
Parks whose POTA pin sits outside their own official outline are listed apart as INFORMATION only ('POTA pin may be wrong':
Brandon 12:14 PM 'Pins can be wrong...this is official').
Reads KPC-Links data/us-key/US-*.json (LINKS, read-only). Writes data/waiting/questions/key-pieces.json + key-pieces.md. Answers
already given are kept (matched by park + record id). Never fails.
  LINKS=../kpc-links python3 kpc_key_questions.py"""
import glob, json, os, pathlib, sys, time

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path('data/waiting/questions')
PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0/query?objectIds={}&outFields=*&returnGeometry=false&f=html'


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    old = {(q['ref'], str(q['record'])): q for q in (load(OUT / 'key-pieces.json', {}) or {}).get('questions') or []}
    qs, pins = [], []
    for f in sorted(glob.glob(str(LINKS / 'data' / 'us-key' / 'US-*.json'))):
        st = pathlib.Path(f).stem
        for ref, r in ((load(f, {}) or {}).get('parks') or {}).items():
            for c in r.get('c') or []:
                if not (isinstance(c, list) and len(c) > 3 and ('held (rule G-1)' in str(c[3]) or 'check (rule R-G8)' in str(c[3]))): continue   # Oct 29: R-G8 CHECK pieces too
                rid = c[0]
                q = {'area': st, 'ref': ref, 'park': r.get('n'), 'record': rid, 'record_name': c[1], 'acres': c[2], 'why': c[3],
                     'record_link': PADUS.format(rid) if isinstance(rid, int) else '', 'pota_link': f'https://pota.app/#/park/{ref}',
                     'question': "Is this piece part of that park on the agency's own map? YES / NO",
                     'answer': None, 'checked_by': None, 'how': None}
                prev = old.get((ref, str(rid)))
                if prev: q.update({k: prev.get(k) for k in ('answer', 'checked_by', 'how', 'rechecked_by_chat2')})
                qs.append(q)
            if r.get('pin_may_be_wrong'): pins.append({'area': st, 'ref': ref, 'park': r.get('n'), 'pota_link': f'https://pota.app/#/park/{ref}'})
    open_n = sum(1 for q in qs if not q['answer'])
    D = {'about': "RULE SHEET G step 2: held similar-name key pieces, one question each. Chat 11 fills answer (YES / NO) + checked_by + how "
                  "(the agency map it looked at); chat 2 rechecks and writes overrides.json. 'pins' = POTA pin may be wrong (information only).",
         'built': time.strftime('%Y-%m-%d %H:%MZ', time.gmtime()), 'open': open_n, 'questions': qs, 'pins': pins}
    json.dump(D, open(OUT / 'key-pieces.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    L = ['# Key pieces waiting for a person (RULE SHEET G step 2)', '',
         f'{len(qs)} held pieces, {open_n} still open. Answer in key-pieces.json (answer YES / NO, checked_by, how). Chat 2 rechecks and writes overrides.json.', '',
         '| area | park | piece (record) | acres | answer | links |', '|---|---|---|---|---|---|']
    for q in qs:
        L.append(f"| {q['area']} | {q['ref']} {q['park']} | {q['record_name']} ({q['record']}) | {q['acres']:,} | {q['answer'] or 'OPEN'} | "
                 + (f"[record]({q['record_link']}) · " if q['record_link'] else '') + f"[POTA]({q['pota_link']}) |")
    L += ['', f'## POTA pin may be wrong (information only): {len(pins)}', ''] + [f"- {p['area']} {p['ref']} {p['park']}" for p in pins]
    (OUT / 'key-pieces.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print(f'::notice title=Key questions::{len(qs)} held pieces ({open_n} open), {len(pins)} pins that may be wrong')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Key questions::stopped ({e})')  # noqa: BLE001
    sys.exit(0)
