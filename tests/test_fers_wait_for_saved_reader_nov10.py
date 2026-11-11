"""Owner decision, 2026-11-10: until the 2-fer finder in KPC-Links has its saved-copy reader (the text held_saved_missing in
kpc_fers.py), every workflow that runs the finder checks for it right after the KPC-Links checkout and, if it is missing,
tests no pairs and saves/commits/pushes/dispatches nothing. Static, no network. Run: python3 -B tests/test_fers_wait_for_saved_reader_nov10.py"""
import pathlib, re, sys
import yaml
W = pathlib.Path(__file__).resolve().parents[1] / '.github/workflows'
ok = True
def check(c, m):
    global ok
    print(('ok   ' if c else 'FAIL ') + m); ok = ok and bool(c)
def s(x): return x if isinstance(x, str) else ''
RUNS = re.compile(r'(^|[\s;&|(])python3?\s+[^\n;&|]*\bkpc_fers\.py\b', re.M)
# a step that writes, saves, commits, pushes or starts something
ACTS = re.compile(r'kpc_push_data|kpc_archive\.sh put|gh release (create|upload)|gh workflow run|/dispatches|git push|git commit|kpc_waiting_room\.py (divert|resume)|kpc_fers_(known|expected)\.py|kpc_pota_pairs|kpc_water_bulk|kpc_map_observations|kpc_fers_key_gate')
names = []
for f in sorted(W.glob('*.yml')):
    y = yaml.safe_load(f.read_text(encoding='utf-8'))
    jobs = y.get('jobs') or {}
    runners = [j for j, d in jobs.items() if any(RUNS.search(s(st.get('run'))) for st in d.get('steps') or [])]
    if not runners: continue
    names.append(f.name)
    # the job that has the wait step: it comes first in its job, after the KPC-Links checkout
    holders = [j for j, d in jobs.items() if any(st.get('id') == 'wait' for st in d.get('steps') or [])]
    check(len(holders) == 1, f'{f.name}: exactly one job has the wait step ({holders})')
    h = holders[0]; hs = jobs[h]['steps']
    wi = next(i for i, st in enumerate(hs) if st.get('id') == 'wait')
    w = hs[wi]
    check('held_saved_missing' in s(w.get('run')) and '.github/scripts/kpc_fers.py' in s(w.get('run')), f'{f.name}: wait step looks for held_saved_missing in kpc_fers.py')
    check('::notice title=2-fers waiting::' in s(w.get('run')) and 'wait=1' in s(w.get('run')), f'{f.name}: wait step prints the notice and sets wait=1')
    check(any('KPC-Links' in s((st.get('with') or {}).get('repository')) for st in hs[:wi]), f'{f.name}: the KPC-Links checkout comes before the wait step')
    first = min(i for i, st in enumerate(hs) if RUNS.search(s(st.get('run')))) if h in runners else len(hs)
    check(wi < first, f'{f.name}: wait step comes before the first finder step')
    check(h in runners or 'wait' in (jobs[h].get('outputs') or {}), f'{f.name}: {h} exposes wait as a job output')
    gate = lambda e: "steps.wait.outputs.wait != '1'" in s(e)
    for i, st in enumerate(hs):
        if i <= wi or st.get('uses') or s(st.get('name')).startswith('Report hidden failures'): continue
        if RUNS.search(s(st.get('run'))) or ACTS.search(s(st.get('run'))):
            check(gate(st.get('if')), f"{f.name}: {h}: step '{st.get('name')}' is gated on the wait")
    if h not in runners:   # fetcher -> worker -> checker: the later jobs are gated on the first job's output
        for j, d in jobs.items():
            if j == h or j not in runners and not any(ACTS.search(s(st.get('run'))) for st in d.get('steps') or []): continue
            if h in (d.get('needs') if isinstance(d.get('needs'), list) else [d.get('needs')]):
                check(f"needs.{h}.outputs.wait != '1'" in s(d.get('if')), f'{f.name}: job {j} is gated on needs.{h}.outputs.wait')
            else:
                # reached only through the jobs it needs (a skipped job skips it)
                check(any(n in jobs and f"needs.{h}.outputs.wait" in s(jobs[n].get('if')) for n in (d.get('needs') if isinstance(d.get('needs'), list) else [d.get('needs')]) if n), f'{f.name}: job {j} only runs after a gated job')
check(set(names) == {'kpc-fers.yml', 'kpc-fers-line.yml'}, f'the workflows that run the finder are the two that are gated ({names})')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
