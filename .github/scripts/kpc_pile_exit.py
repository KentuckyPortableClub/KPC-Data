#!/usr/bin/env python3
"""Pile-exit path (Nov 6): applies the two-agreements rule from the agreement ledger.

Does NOT write fake per-park overrides. When state.auto is true AND a park has two agreements
of kind pile-exit, it records a RELEASE proposal in data/agreement-ledger/exits.jsonl with
decided_by 'Brandon rule 2026-11-05 two-agreements'. auto defaults false.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_agreement_ledger as AL

OUT = pathlib.Path('data/agreement-ledger/exits.jsonl')


def run():
    rows = AL.load_rows(); st = AL.load_state(); ex = AL.exit_candidates(rows)
    report = {'auto': st['auto'], 'count_ready': ex['count_ready'],
              'ready_parks': [r['park'] for r in ex['ready_but_auto_false'] or ex['would_exit']],
              'would_exit_now': [r['park'] for r in ex['would_exit']],
              'decided_by': AL.DECIDED_BY,
              'note': 'auto=false: nothing exits until Brandon turns auto on after a full-run check'}
    if st['auto'] and ex['would_exit']:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT, 'a', encoding='utf-8') as f:
            for r in ex['would_exit']:
                f.write(json.dumps({'park': r['park'], 'kind': 'pile-exit', 'decided_by': AL.DECIDED_BY,
                                    'proposed_by': r['proposed_by'], 'confirmed_by': r['confirmed_by'],
                                    'proposal': r['proposal'], 'source': r.get('source', '')}, ensure_ascii=False) + '\n')
        report['written'] = len(ex['would_exit'])
    print(json.dumps(report, indent=1)); return report


if __name__ == '__main__':
    run()
