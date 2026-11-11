#!/usr/bin/env python3
"""Nov 8 (Brandon t802u / Quality after W-AU wipe): refuse a 2-fer bot job when the answer key for this region is stale
or when STATES asks for a country/state listed as failed on the key.

Root cause: run 42451234481 measured W-AU on an older world build while a newer rebuild was coming. Do not measure
2-fers on a key whose rules_of_run is behind the current freeze hash.

Owner rule, 2026-11-10: every state the job measures must be built green on the current rules in this build (US: the state's own
index 'states' row carries the rules hash and is not 'failed'; keys without per-state rows: a FULL build on the current rules).
rules_of_run alone is never enough: a state that silently was not built never feeds 2-fers.

  REGION=na|world|ky  STATES='W-AU US-MI …' (optional)
Exit 0 = GO; exit 1 = refuse.
"""
import json, os, pathlib, subprocess, sys

ROOT = pathlib.Path('.')
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_fers_chain_plan as CP   # one per-state test for the chain and this gate


def load_index(kind):
    p = ROOT / 'data' / kind / 'index.json'
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        print(f'::error title=2-fer key gate::cannot read {p}: {e}')
        return None


def rules_hash(kind):
    script = ROOT / '.github' / 'scripts' / 'kpc_key_freeze.py'
    if not script.exists():
        return None
    r = subprocess.run([sys.executable, str(script), 'rules', kind], capture_output=True, text=True, timeout=60)
    out = (r.stdout or '').strip().splitlines()
    return out[-1].strip() if out else None


def main():
    region = (os.environ.get('REGION') or '').strip().lower()
    states = {x for x in (os.environ.get('STATES') or '').upper().replace(',', ' ').split() if x}
    if region == 'world':
        kinds = ['world-key']
    elif region == 'ky':
        kinds = ['us-key']
    elif region == 'na':
        kinds = ['us-key', 'ca-key']
    else:
        print(f'::warning title=2-fer key gate::unknown REGION={region!r}: no key check')
        return 0

    bad = []
    for kind in kinds:
        idx = load_index(kind)
        if idx is None:
            bad.append(f'{kind}: missing index')
            continue
        build = str(idx.get('build') or '')
        rules = str(idx.get('rules') or '')
        rules_of_run = str(idx.get('rules_of_run') or '')
        failed = [str(x) for x in (idx.get('failed') or [])]
        cur = rules_hash(kind)
        print(f'::notice title=2-fer key gate::{kind} build={build or "?"} rules={rules or "none"} '
              f'rules_of_run={rules_of_run or "none"} current_freeze={cur or "?"} failed={failed or []}')
        pre = {'us-key': 'US-', 'ca-key': 'CA-', 'world-key': 'W-'}[kind]
        mine = sorted(x for x in states if x.startswith(pre))
        if not mine:   # a whole-region run: every state row of the key (or the key-wide stamp)
            rows = idx.get('states') if isinstance(idx.get('states'), dict) else {}
            mine = [pre + a for a in sorted(rows)] or [pre + '*']
        if not cur:
            print(f'::warning title=2-fer key gate::{kind}: could not compute current freeze hash; skipping stale check')
        elif region == 'ky':   # Kentucky measures on its own key: only a key run on the current rules is asked of the US key
            if cur not in (rules, rules_of_run): bad.append(f'{kind} build {build} is stale: rules_of_run={rules_of_run or "none"}, rules={rules or "none"}, current freeze={cur}')
        else:
            off = CP.states_not_green(idx, kind, mine, cur)
            if off:
                bad.append(f'{kind} build {build}: not built green on the current rules (current freeze={cur}, rules_of_run={rules_of_run or "none"}) '
                           f'for {len(off)} state(s): ' + '; '.join(f'{st} ({w})' for st, w in off[:12]) + '. Rebuild them on current rules before 2-fers.')
            else:
                print(f'::notice title=2-fer key gate::{kind}: {len(mine)} state(s) built green on current rules')
        if kind == 'world-key' and failed and states:
            want = set()
            for s in states:
                if s.startswith('W-') and len(s) >= 4:
                    want.add(s.split('-')[1])
                elif len(s) == 2 and s.isalpha():
                    want.add(s)
            hit = sorted(want & set(failed))
            if hit:
                bad.append(f'{kind} failed={failed}: refusing STATES that need {hit} '
                           f'(source HELD / empty saved copy; previous key kept — fix the source or cache, then rebuild)')
    if bad:
        for b in bad:
            print(f'::error title=2-fer key gate::{b}')
        return 1
    print('::notice title=2-fer key gate::GO')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f'::error title=2-fer key gate::stopped: {type(e).__name__}: {e}')
        raise SystemExit(1)
