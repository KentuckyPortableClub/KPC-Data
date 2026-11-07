"""Nov 4 PM fix bundle item 7: 'keep green' errors are visible. Every '|| echo "::error|warning title=..."' a step uses to swallow
a failure also writes a line to $RUNNER_TEMP/kpc-hidden.txt, and every job that does so has the G8 'Report hidden failures'
step (if: always()), which lists those lines in the run's summary ($GITHUB_STEP_SUMMARY) next to the kept-green steps.
Run: python3 -B tests/test_fixbundle_hidden_failures_nov4.py"""
import glob, os, pathlib, re, subprocess, sys, tempfile
import yaml
R = pathlib.Path(__file__).resolve().parents[1]; W = R / '.github/workflows'
ok = True
def check(what, got, want):
    global ok
    good = got == want; ok &= good
    print(('PASS ' if good else 'FAIL ') + f'{what}: got {got!r}' + ('' if good else f', want {want!r}'))
SWALLOW = re.compile(r'\|\| echo "::(error|warning) title=')
PAUSED = re.compile(r'PAUSED Nov 4|Paused bot')
# the chain starts of the 9 paused bots are left alone here: the PAUSE patch rewrites exactly those lines (so the two patches never
# touch the same line); with PAUSE they print a visible '::warning title=Paused bot::'; see NOTES.md for after the pause is undone
PAUSE_SITE = re.compile(r'(gh workflow run |workflows/)kpc-(wdpa-phonebook|collector|intake|docs|docs-merge|gis-hunter|world-finder|discovery|engine-discover)\.yml')
left, nog8, bad_sh, rec, skipped = [], [], [], 0, []
for f in sorted(W.glob('*.yml')):
    d = yaml.safe_load(open(f))
    for jn, j in (d.get('jobs') or {}).items():
        st = j.get('steps') or []
        runs = [x.get('run', '') for x in st]
        for r in runs:
            for line in r.split('\n'):
                if SWALLOW.search(line) and not line.lstrip().startswith('#'):
                    if PAUSE_SITE.search(line): skipped.append(f'{f.name}:{jn}'); continue
                    left.append(f'{f.name}:{jn}: {line.strip()[:90]}')
            rec += r.count('kpc-hidden.txt')
        if any('kpc-hidden.txt' in r for r in runs):
            g8 = [x for x in st if 'hidden failures' in str(x.get('name', '')).lower()]
            if not (g8 and g8[-1].get('if') == 'always()' and 'kpc-hidden.txt' in g8[-1].get('run', '') and st.index(g8[-1]) == len(st) - 1): nog8.append(f'{f.name}:{jn}')
        for i, r in enumerate(runs):   # every changed shell script still parses (bash -n), with ${{ }} filled in
            if 'kpc-hidden.txt' not in r: continue
            t = re.sub(r'\$\{\{.*?\}\}', 'X', r)
            p = subprocess.run(['bash', '-n'], input=t, capture_output=True, text=True)
            if p.returncode: bad_sh.append(f'{f.name}:{jn}:{i}: {p.stderr.strip()[:120]}')
check('no swallowed error is left without the kpc-hidden.txt line', left[:5], [])
paused = any('PAUSED Nov 4' in open(f).read() for f in W.glob('*.yml'))   # with the PAUSE patch on top those lines are its warnings
check('the chain starts left to the PAUSE patch (12 of its 14 sites swallow an error this way; 0 once PAUSE is applied)', len(skipped), 0 if paused else 12)
check('every job that records them ends with the G8 report (if: always(), reads kpc-hidden.txt)', nog8, [])
check('every changed shell script parses (bash -n)', bad_sh[:5], [])
check('the recorded sites are many (the 4 from the health check among them)', rec > 300, True)
for n, s in (('kpc-world-finder.yml', 'kpc_world_finder.py'), ('kpc-discovery.yml', 'kpc_discovery.py'), ('kpc-engine-discover.yml', 'Save'), ('kpc-gis-hunter.yml', 'kpc_push_data.sh')):
    t = open(W / n).read()
    check(f'{n}: the {s} failure is recorded', re.search(r'echo "' + re.escape(s) + r' - [^"]*" >> "\$RUNNER_TEMP/kpc-hidden.txt"', t) is not None, True)
# the report itself: run the G8 python with a fake hidden file and a fake summary
g8 = next(x for x in yaml.safe_load(open(W / 'kpc-discovery.yml'))['jobs']['discover']['steps'] if 'hidden failures' in x.get('name', '').lower())
py = g8['run'].split("<<'PY'\n", 1)[1].rsplit('PY', 1)[0]
with tempfile.TemporaryDirectory() as td:
    open(os.path.join(td, 'kpc-hidden.txt'), 'w').write('kpc_discovery.py - stopped with an error (exit 1), see the log above\n')
    env = dict(os.environ, RUNNER_TEMP=td, GITHUB_STEP_SUMMARY=os.path.join(td, 'sum.md'), KPC_STEPS='{"a": {"outcome": "failure", "conclusion": "success"}}')
    p = subprocess.run([sys.executable, '-B', '-c', py], env=env, capture_output=True, text=True)
    summ = open(os.path.join(td, 'sum.md')).read()
check('the G8 report lists the caught error in the summary', ('Errors caught inside steps and kept green (1)' in summ, 'kpc_discovery.py - stopped with an error (exit 1)' in summ, 'Steps that failed but were kept green:** a' in summ, p.returncode), (True, True, True, 0))
# Crons Brandon OK'd himself (the only way a new cron gets in): Brandon, 7:11 AM CST Nov 6 2026 (relayed by the parent agent, his
# words): "Yes, put the Quality sample on a weekly schedule" -> kpc-quality-sample.yml Mondays 7:41 AM CST.
# Nov 7 2026 2:19 PM CST (Brandon, own words: "release fcc ridb"): the cell coverage bot's pre-PR1 monthly cron is back.
BRANDON_OK_CRONS = {('kpc-quality-sample.yml', '41 13 * * 1'), ('kpc-cell.yml', '16 9 3 * *')}
crons = lambda t: re.findall(r"^\s*-\s*cron:.*$", t, re.M)
base = subprocess.run(['git', '-C', str(R), 'cat-file', '-e', 'a569c9b35'], capture_output=True).returncode == 0
if base:
    diff = subprocess.run(['git', '-C', str(R), 'diff', 'a569c9b35', '--', '.github/workflows'], capture_output=True, text=True).stdout
    check('no cron line added' + ('' if paused else ' or changed'), [l for l in diff.split('\n') if re.match(r'^[+]\s*-\s*cron:' if paused else r'^[+-]\s*-\s*cron:', l) and not any(c in l for _f, c in BRANDON_OK_CRONS)], [])
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
