#!/usr/bin/env python3
"""Nov 9 PM (Brandon t905u/t906u; run 42649544758): the 2-fer bot runs AREA by AREA, a time-out shows red, and two workflow breakages.
Offline: reads files, runs the area planner and the waiting room's divert with no files. Nothing is started or pushed."""
import json, os, pathlib, re, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
Y = (ROOT / '.github/workflows/kpc-fers.yml').read_text(encoding='utf-8')
fails = []


def check(c, msg):
    print(('PASS ' if c else 'FAIL ') + msg)
    if not c: fails.append(msg)


# 1 areas: every US state + Canadian province in exactly one area (Kentucky is its own run)
A = json.load(open(ROOT / '.github/fers-areas.json'))['areas']
sts = [s for v in A.values() for s in v.split()]
check(len(sts) == len(set(sts)), 'no state is in two areas')
us = {'US-' + x for x in 'AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split()}
check(us <= set(sts) and 'US-KY' not in sts, 'every US state except Kentucky (its own run) is in an area')
check({'CA-' + x for x in 'AB BC MB NB NL NS NT NU ON PE QC SK YT'.split()} <= set(sts), 'every Canadian province / territory is in an area')
env = dict(os.environ, REGION='southeast canadaeast nope', STATES='')
r = subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_fers_areas.py'), 'plan'], capture_output=True, text=True, env=env)
L = json.loads(r.stdout.split('list=', 1)[1])
check([x['name'] for x in L] == ['southeast', 'canadaeast'] and all(x['region'] == 'na' and x['tag'] == x['name'] for x in L) and 'nope' in r.stderr,
      'plan: one job per named area (REGION na, its own tag); an unknown name is skipped with a warning')
for reg, want in (('na', [('na', 'na', 'US-OH')]), ('both', [('na', 'na', 'US-OH'), ('world', 'world', 'US-OH')]), ('ky', [('ky', 'ky', '')])):
    r = subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_fers_areas.py'), 'plan'], capture_output=True, text=True, env=dict(os.environ, REGION=reg, STATES='US-OH'))
    L = json.loads(r.stdout.split('list=', 1)[1])
    check([(x['name'], x['region'], x['states']) for x in L] == want, f'plan: the old value {reg!r} works as before')
r = subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_fers_areas.py'), 'plan'], capture_output=True, text=True, env=dict(os.environ, REGION='areas'))
check(len(json.loads(r.stdout.split('list=', 1)[1])) == len(A), "plan: 'areas' = every area, one job each")

# 2 the workflow: matrix from the plan, own budget, 3 at a time, area files saved, no cron
check('needs: plan' in Y and 'fromJSON(needs.plan.outputs.list)' in Y and 'max-parallel: 3' in Y, 'one job per area from the plan, at most 3 at once')
check('STATES: ${{ matrix.r.states }}' in Y and 'RUN_TAG: ${{ matrix.r.tag }}' in Y and 'inputs.states' not in Y.split('  fers:', 1)[1], 'each job uses its own area (states + tag), not the dispatch box')
check('data/fers/*-"$TAG".json' in Y, "an area job saves its own report / looked / missing files")
# Nov 9 evening: Brandon's t911u/t912u ('once a month') allow exactly ONE monthly cron (test_fers_rolling_nov9eve.py)
check(re.findall(r"cron: '([^']+)'", Y.split('on:', 1)[1].split('permissions:', 1)[0]) == ['23 8 5 * *'], 'exactly one cron, the monthly one Brandon asked for')
check("success() && steps.kept_green_3.outcome == 'success'" in Y, 'Save still needs a finished Look step (an out-of-time area keeps its previous file)')
# 3 a time-out is red, never green
check('KPC_HARD_END' in Y and '335 * 60 - 300' in Y, 'the bot gets the step\'s hard end and stops 5 minutes before it')
check("(s.get('kept_green_3') or {}).get('outcome') in ('failure', 'cancelled')" in Y and Y.count('sys.exit(1)') >= 2, "a 'Look for shared ground' time-out makes the job red")
check("KPC_FERS_PARK_S: '600'" in Y, 'one park / pair / map request: 10 minutes at most')

# 4 the scoreboard divert with 0 approved parks is a clean no-op (run 42666223956), and divert with no files touches nothing
SB = (ROOT / '.github/workflows/kpc-scoreboard.yml').read_text(encoding='utf-8')
check('[ -n "$F" ] && python3 .github/scripts/kpc_waiting_room.py divert' not in SB and 'if [ -n "$F" ]; then python3 .github/scripts/kpc_waiting_room.py divert $F' in SB,
      'scoreboard: 0 approved parks = nothing to divert, no error')
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['git', 'init', '-q', t]); pathlib.Path(t, 'x.json').write_text('{}')
    r = subprocess.run([sys.executable, str(ROOT / '.github/scripts/kpc_waiting_room.py'), 'divert'], capture_output=True, text=True, cwd=t)
    check(r.returncode == 0 and 'nothing to divert' in r.stdout, 'kpc_waiting_room.py divert with no files: exit 0, nothing moved')

# 5 Playwright jobs run on ubuntu-24.04 (Playwright has no build for 26.04: KPC Guide PDFs run 42637107981)
bad = []
for f in sorted((ROOT / '.github/workflows').glob('*.yml')):
    s = f.read_text(encoding='utf-8')
    if not re.search(r'playwright install', s, re.I): continue
    jobs = re.split(r'\n(?=  [A-Za-z0-9_-]+:\s*\n)', s.split('\njobs:', 1)[1])
    for j in jobs:
        if re.search(r'playwright install', j, re.I) and 'runs-on: ubuntu-24.04' not in j: bad.append(f.name)
check(not bad, f'every job that installs Playwright runs on ubuntu-24.04 ({bad})')
print('ALL PASS' if not fails else f'{len(fails)} FAILED'); sys.exit(1 if fails else 0)
