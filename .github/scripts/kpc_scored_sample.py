#!/usr/bin/env python3
"""Scored sample: pile-solver SOLVED-* proposals vs Quality verdicts.
Agreement % on graded SOLVED-JOIN rows informs when Brandon may flip auto
(he flips it; this script never sets auto=true). Nov 6 Part B."""
import csv, json, os, pathlib, re, sys

ROOT = pathlib.Path(os.environ.get('DATA') or '.')
SJ = ROOT / 'data/waiting/in/data/pile-solver/solved-join.csv'
NP = ROOT / 'data/waiting/in/data/pile-solver/needs-person.csv'
SHEET = ROOT / 'data/answer-sheet'
OUT_DIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/agreement-ledger'
WORD = {'SOLVED-JOIN': 'YES', 'SOLVED-PIN': 'PIN', 'NEEDS-PERSON': 'NOT SURE', 'UNTOUCHED': 'KEEP'}


def load_sheet():
    out = {}
    for f in sorted(SHEET.glob('*.csv')):
        with open(f, newline='', encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                out.setdefault(r.get('ref'), []).append(r)
    return out


def quality_label(rows):
    for r in rows or []:
        q = (r.get('quality_yes') or '').strip()
        if not q: continue
        # KEEP on OUTSIDE/NEAR patterns = Quality OK with the outline/join
        if re.search(r'\bYES\b|\bKEEP\b', q, re.I):
            return 'YES', f'LABELLED from answer-sheet quality_yes: {q[:160]}', True
        if re.search(r'\bNO\b|\bFAIL\b', q, re.I):
            return 'NO', f'LABELLED from answer-sheet quality_yes: {q[:160]}', True
        return 'OTHER', f'LABELLED: {q[:160]}', True
    return '', 'not yet graded (template)', False


def read_csv(path):
    if not path.exists(): return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    sheet = load_sheet()
    sample = []
    for r in read_csv(SJ):
        qv, qnote, graded = quality_label(sheet.get(r['ref']))
        solver = WORD.get(r.get('verdict'), r.get('answer_word') or '')
        agree = ''
        if graded:
            agree = 'AGREE' if qv == solver else 'DISAGREE'
        sample.append({
            'ref': r['ref'], 'pota_name': r.get('pota_name', ''), 'area': r.get('area', ''),
            'solver_verdict': r.get('verdict', ''), 'solver_word': solver,
            'distance_m': r.get('distance_m', ''), 'record_id': r.get('record_id', ''),
            'record_name': r.get('record_name', ''), 'reason': (r.get('reason') or '')[:180],
            'quality_verdict': qv, 'quality_note': qnote, 'agreement': agree,
            'graded': 'yes' if graded else 'no', 'cohort': 'solved-join',
        })
    # Also list NEEDS-PERSON that already have a Quality YES on the sheet (labelled, not counted in %)
    np_labelled = []
    for r in read_csv(NP):
        qv, qnote, graded = quality_label(sheet.get(r['ref']))
        if not graded: continue
        np_labelled.append({
            'ref': r['ref'], 'pota_name': r.get('pota_name', ''), 'area': r.get('area', ''),
            'solver_verdict': r.get('verdict', ''), 'solver_word': 'NOT SURE',
            'distance_m': r.get('distance_m', ''), 'record_id': r.get('record_id', ''),
            'record_name': r.get('record_name', ''), 'reason': (r.get('reason') or '')[:180],
            'quality_verdict': qv, 'quality_note': qnote + ' [sheet YES while solver NEEDS-PERSON — often offline/no-layer; not in agreement %]',
            'agreement': 'N/A-not-solver-YES', 'graded': 'yes', 'cohort': 'needs-person-labelled',
        })

    graded = [r for r in sample if r['graded'] == 'yes']
    agree_n = sum(1 for r in graded if r['agreement'] == 'AGREE')
    disagree = [r for r in graded if r['agreement'] == 'DISAGREE']
    pct = round(100.0 * agree_n / len(graded), 1) if graded else None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = sample + np_labelled
    cols = list(all_rows[0].keys()) if all_rows else ['ref']
    with open(OUT_DIR / 'scored-sample-report.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(all_rows)
    tcols = ['ref', 'pota_name', 'area', 'solver_verdict', 'solver_word', 'distance_m', 'record_id', 'record_name',
             'quality_verdict', 'quality_initials', 'quality_date', 'agree_y_n', 'notes']
    with open(OUT_DIR / 'quality-verdict-sheet-template.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=tcols); w.writeheader()
        for r in sample:  # template covers every SOLVED-JOIN proposal
            w.writerow({
                'ref': r['ref'], 'pota_name': r['pota_name'], 'area': r['area'],
                'solver_verdict': r['solver_verdict'], 'solver_word': r['solver_word'],
                'distance_m': r['distance_m'], 'record_id': r['record_id'], 'record_name': r['record_name'],
                'quality_verdict': r['quality_verdict'] if r['graded'] == 'yes' else '',
                'quality_initials': 'Quality' if r['graded'] == 'yes' else '',
                'quality_date': 'see quality_yes' if r['graded'] == 'yes' else '',
                'agree_y_n': ('Y' if r['agreement'] == 'AGREE' else ('N' if r['agreement'] == 'DISAGREE' else '')),
                'notes': ('LABELLED from answer-sheet' if r['graded'] == 'yes' else 'template: Quality to fill'),
            })
    summary = {
        'solved_join_n': len(sample), 'graded_solved_join_n': len(graded),
        'agree_n': agree_n, 'disagree_n': len(disagree), 'agreement_pct': pct,
        'disagreements': [{'ref': r['ref'], 'solver': r['solver_word'], 'quality': r['quality_verdict']} for r in disagree],
        'needs_person_with_sheet_yes_n': len(np_labelled),
        'auto': False,
        'note': 'agreement_pct is over graded SOLVED-JOIN rows only. Brandon flips auto by hand; script never sets auto=true.',
    }
    json.dump(summary, open(OUT_DIR / 'scored-sample-summary.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1)); return 0


if __name__ == '__main__':
    sys.exit(main())
