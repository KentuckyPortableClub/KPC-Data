#!/usr/bin/env python3
"""Nov 8 (Brandon t802u / Quality after W-AU wipe): refuse a 2-fer bot job when the answer key for this region is stale
or when STATES asks for a country/state listed as failed on the key.

Root cause: run 42451234481 measured W-AU on an older world build while a newer rebuild was coming. Do not measure
2-fers on a key whose rules_of_run is behind the current freeze hash.

A partial world build (failed=['LK','RW'], rules kept from the prior full stamp) is still GO for other countries when
rules_of_run matches the current freeze — only the failed countries are refused.

  REGION=na|world|ky  STATES='W-AU US-MI …' (optional)
Exit 0 = GO; exit 1 = refuse.
"""
import json, os, pathlib, subprocess, sys

ROOT = pathlib.Path('.')


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
        if not cur:
            print(f'::warning title=2-fer key gate::{kind}: could not compute current freeze hash; skipping stale check')
        elif rules == cur:
            print(f'::notice title=2-fer key gate::{kind}: full build on current rules')
        elif rules_of_run == cur:
            print(f'::notice title=2-fer key gate::{kind}: this run used current rules (rules_of_run={rules_of_run}); '
                  f'index.rules={rules or "none"} kept from prior full stamp — OK for countries that built')
        else:
            bad.append(f'{kind} build {build} is stale: rules_of_run={rules_of_run or "none"}, rules={rules or "none"}, '
                       f'current freeze={cur}. Rebuild the key on current rules before 2-fers.')
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
