#!/usr/bin/env python3
"""The pile solver's name score is the active Tool Box matcher (kpc-maprep-logic.js).

Node scores the shared 1,600 name pairs. Python must return the same score for every pair.
Sourced round-3 abbreviations (SHS, HP, SPA) rank. from_memory rows are not on the list.
'game' stays a distinguishing word. Offline. Does not write this repo.
"""
import csv, json, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ.setdefault('LINKS', '/tmp/kpc-links')
os.environ['KPC_RESEARCH_SOURCES'] = 'report'
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_research_sources as RS

PAIRS = ROOT / 'tests' / 'fixtures' / 'pile_solver' / 'name-score-pairs.json'
JS = pathlib.Path(os.environ['LINKS']) / 'kpc-maprep-logic.js'

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


def main():
    RS.reset_matcher()
    pairs = json.loads(PAIRS.read_text(encoding='utf-8'))
    check(len(pairs) == 1600, f'shared fixture has 1,600 name pairs ({len(pairs)})')
    rows_path = pathlib.Path('/tmp/kpc-name-score-rows.json')
    rows_path.write_text(json.dumps(RS.table_rows()), encoding='utf-8')
    node = (
        "const fs = require('fs');\n"
        f"const L = require({json.dumps(str(JS))});\n"
        f"const rows = JSON.parse(fs.readFileSync({json.dumps(str(rows_path))}, 'utf8'));\n"
        "L.loadRows(rows);\n"
        f"const pairs = JSON.parse(fs.readFileSync({json.dumps(str(PAIRS))}, 'utf8'));\n"
        "process.stdout.write(JSON.stringify(pairs.map(p => L.nameScore(p[0], p[1]))));\n"
    )
    proc = subprocess.run(['node', '-e', node], capture_output=True, text=True, timeout=60)
    check(proc.returncode == 0 and proc.stdout.startswith('['),
          'node scored the pairs with kpc-maprep-logic.js' + ('' if proc.returncode == 0 else ': ' + (proc.stderr or '?')[:180]))
    if proc.returncode != 0:
        print('SOME FAILED')
        return 1
    js = json.loads(proc.stdout)
    py = [RS.name_score(a, b, report=True) for a, b in pairs]
    agree = sum(1 for a, b in zip(py, js) if a == b)
    print(f'JS-PYTHON AGREE {agree}/{len(pairs)}')
    check(agree == len(pairs) == 1600, f'Python and the Tool Box matcher agree on every pair ({agree}/{len(pairs)})')
    want = {
        ('Seney NWR', 'Seney National Wildlife Refuge'): 96,
        ('Cabin Creek WMA (Lewis County)', 'Cabin Creek WMA'): 88,
        ('Croatan NF', 'Croatan National Forest'): 96,
    }
    for (a, b), score in want.items():
        got = RS.name_score(a, b, report=True)
        check(got == score, f'{a} vs {b}: {got} (Tool Box {score})')
    game = RS.name_score('Allegan State Game Area', 'Allegan State Recreation Area', report=True)
    check('game' in RS.canon('Allegan State Game Area')[1] and game < 84,
          f"'game' still distinguishes a game area from a recreation area ({game})")
    sourced = [
        ('Marksville SHS', 'Marksville State Historic Site', 'Marksville Creek'),
        ('Bald Rock HP', 'Bald Rock Heritage Preserve', 'Bald Rock Creek'),
        ('Cypremort Point SPA', 'Cypremort Point State Preservation Area', 'Cypremort Point Creek'),
    ]
    for query, good, bad in sourced:
        gs, bs = RS.name_score(query, good, report=True), RS.name_score(query, bad, report=True)
        check(gs == 96 and gs > bs, f'{query} ranks {good} above {bad} ({gs} vs {bs})')
    listed = list(csv.DictReader((ROOT / 'data/research-sources/abbreviations.csv').open(encoding='utf-8')))
    check(len(listed) == 30 and {r['origin'] for r in listed} == {'sourced'},
          f'the abbreviation list is the 30 sourced rows only ({len(listed)} origins {sorted({r["origin"] for r in listed})})')
    # SRA is from_memory only (not sourced, not in the toolbox table), so it must not expand.
    sra = RS.name_score('Foo SRA', 'Foo State Recreation Area', report=True)
    check(sra < 84, f'a from_memory code is not applied ({sra})')
    os.environ.pop('KPC_RESEARCH_SOURCES', None)
    check(RS.rank_outlines('Marksville SHS', [{'id': '1', 'name': 'Marksville State Historic Site'}]) == [],
          'flag off: ranking still returns nothing')
    print('ALL PASS' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
