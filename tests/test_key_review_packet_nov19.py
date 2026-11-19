#!/usr/bin/env python3
"""Offline checks for the key review packet (19 Nov 2026). Made-up parks, no network.
Run: python3 -B tests/test_key_review_packet_nov19.py
"""
import ast, importlib.util, json, pathlib, re, subprocess, sys, tempfile
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.github/scripts/kpc_key_review_packet.py'
WF = ROOT / '.github/workflows/kpc-key-review-packet.yml'
spec = importlib.util.spec_from_file_location('kpc_key_review_packet', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ok = True

def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)

# --- the script stays on the standard library ---
tree = ast.parse(SCRIPT.read_text(encoding='utf-8'))
imported = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imported.update(a.name.split('.')[0] for a in node.names)
    elif isinstance(node, ast.ImportFrom) and node.module:
        imported.add(node.module.split('.')[0])
outside = sorted(name for name in imported if name not in sys.stdlib_module_names)
check(not outside, f'standard library only ({outside})')

# --- scope ---
old = {'changes': [{'id': 'older-rule', 'scope': {'states': ['US-AA']}}]}
new = {'changes': [
    {'id': 'older-rule', 'scope': {'states': ['US-AA']}},
    {'id': 'sample-rule', 'scope': {'states': ['US-AA', 'US-BB', 'KY', 'US-CC']}},
]}
got = mod.scope_from_docs(old, new, '')
check(got['states'] == ['AA', 'BB', 'CC'] and got['entries'] == ['sample-rule'] and got['message'] == '', 'a new scope entry gives its states, in order, without KY')
none = mod.scope_from_docs(old, old, '')
check(none['states'] == [] and none['message'] == 'this PR adds no scope entry', 'no new entry stops with the plain line')
hand = mod.scope_from_docs(old, old, 'BB, US-AA aa')
check(hand['states'] == ['BB', 'AA'] and hand['states_from'] == 'input', 'a typed state list is the one that is used')
wide = mod.scope_from_docs(old, {'changes': [{'id': 'wide', 'scope': 'all'}]}, '')
check(wide['states'] == [] and 'names no states' in wide['message'], 'a scope of "all" is not turned into every state')
ky = mod.scope_from_docs(old, old, 'KY')
check(ky['states'] == [] and any('KY' in n for n in ky['notes']), 'KY alone does not become a build')

# --- joined records, not the check list ---
old_key = {'parks': {
    'US-9001': {'n': 'North Sample Park', 'm': [[1001, 'North Sample Preserve', 30, 'name'], [1002, 'North Sample Park', 70, 'name']]},
    'US-9002': {'n': 'East Sample Park', 'm': [[1003, 'East Sample Park', 10, 'name']],
                'c': [[1004, 'East Sample Preserve', 5, 'check (sample): a made-up reason']]},
    'US-9003': {'n': 'South Sample Park', 'm': [[1005, 'South Sample Park', 13, 'name']]},
    'US-9004': {'n': 'West Sample Park', 'm': [[1007, 'West Sample Park', 8, 'name']]},
}}
new_key = {'parks': {
    'US-9001': {'n': 'North Sample Park', 'm': [[1002, 'North Sample Park', 70, 'name']]},
    'US-9002': {'n': 'East Sample Park', 'm': [[1003, 'East Sample Park', 10, 'name']],
                'c': [[1004, 'East Sample Preserve', 5, 'check (other): only the reason changed']]},
    'US-9003': {'n': 'South Sample Park', 'm': [[1005, 'South Sample Park', 13, 'name'], [1006, 'South Sample Addition', 4, 'name']]},
}}
diffs = mod.diff_parks(old_key, new_key)
check([d['ref'] for d in diffs] == ['US-9001', 'US-9003', 'US-9004'], 'a check-list change is not a joined-record change')
one = diffs[0]
check(one['old_acres'] == 100 and one['new_acres'] == 70 and one['lost'][0]['id'] == '1001' and not one['gained'], 'a lost record keeps its acres and the outline total')
check(diffs[1]['gained'][0]['id'] == '1006' and diffs[1]['new_acres'] == 17, 'a gained record is listed and the acres add up')

# --- notices ---
old_log = '::notice title=US key AA::kept 1 record\n::notice title=US key AA::sample rule: 1 record to check: US-9001 North Sample Preserve\n::notice title=Other::ignore me\n'
new_log = '::notice title=US key AA::kept 1 record\n::notice title=US key AA::sample rule: 2 records to check\n'
only_new, only_old = mod._only(mod.notice_lines(old_log, 'AA'), mod.notice_lines(new_log, 'AA'))
check(only_new == ['sample rule: 2 records to check'] and only_old == ['sample rule: 1 record to check: US-9001 North Sample Preserve'], 'only the notice lines that one side printed')
check(mod.notice_lines('::notice title=US key BB::nope\n', 'AA') == [], 'a notice for another state stays out')
check(mod._decode_notice('100%25 done%0Aline 2') == '100% done\nline 2', 'notice escapes come back as a person would read them')

# --- a build that did not finish ---
good_line = 'AA: 2 parks, 1 joined, 0 to check, 0 nothing found, 0 places, 3 s\n'
check(mod.judge_build('AA', 0, 0, good_line, good_line)['result'] == 'ok', 'a finished pair is ok')
check(mod.judge_build('AA', 0, 124, good_line, '')['result'] == 'timed out', 'a timed out side is timed out')
check(mod.judge_build('AA', 0, 89, good_line, good_line)['result'] == 'failed', 'a side that tried the network is not used')
check(mod.judge_build('AA', 0, 0, good_line, 'no finished line\n')['result'] == 'failed', 'no finished line is a failed build')
check(mod.judge_build('AA', 0, 0, good_line, good_line, {'parks': {}}, None, True)['result'] == 'failed', 'a missing key file is a failed build')

# --- the packet ---
with tempfile.TemporaryDirectory() as td:
    root = pathlib.Path(td)
    folder = root / 'builds' / 'key-AA'
    folder.mkdir(parents=True)
    (folder / 'status.json').write_text(json.dumps({'state': 'AA', 'result': 'ok', 'old': {'ok': True, 'why': ''}, 'new': {'ok': True, 'why': ''}}), encoding='utf-8')
    (folder / 'US-AA-old.json').write_text(json.dumps(old_key), encoding='utf-8')
    (folder / 'US-AA-new.json').write_text(json.dumps(new_key), encoding='utf-8')
    (folder / 'old.log').write_text(old_log, encoding='utf-8')
    (folder / 'new.log').write_text(new_log + good_line, encoding='utf-8')
    bb = root / 'builds' / 'key-BB'
    bb.mkdir()
    (bb / 'status.json').write_text(json.dumps({'state': 'BB', 'result': 'timed out', 'old': {'exit': 124, 'ok': False, 'why': 'timed out'}, 'new': {'exit': 124, 'ok': False, 'why': 'timed out'}}), encoding='utf-8')
    old_fact = {'area': 'US-AA', 'counts': {'with_outline': 3, 'verified': 2, 'PIN_FAR': 0, 'SIZE_BIG': 1},
                'parks': {
                    'US-9001': {'n': 'North Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 0, 'rows': 2},
                    'US-9002': {'n': 'East Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 1.5, 'rows': 1},
                    'US-9004': {'n': 'West Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 0, 'rows': 1},
                }}
    new_fact = {'area': 'US-AA', 'counts': {'with_outline': 3, 'verified': 1, 'PIN_FAR': 1, 'SIZE_BIG': 1},
                'parks': {
                    'US-9001': {'n': 'North Sample Park', 'class': 'flagged', 'flags': [['PIN_FAR', 'the pin is 4.0 km outside the nearest piece']], 'pin_km': 4, 'rows': 1},
                    'US-9002': {'n': 'East Sample Park', 'class': 'verified', 'flags': [['SIZE_WEAK', 'a soft flag']], 'pin_km': 1.5, 'rows': 1},
                    'US-9004': {'n': 'West Sample Park', 'class': 'pin', 'flags': [], 'rows': 0},
                }}
    (root / 'fc-old').mkdir()
    (root / 'fc-new').mkdir()
    (root / 'fc-old' / 'factcheck-US-AA.json').write_text(json.dumps(old_fact), encoding='utf-8')
    (root / 'fc-new' / 'factcheck-US-AA.json').write_text(json.dumps(new_fact), encoding='utf-8')
    (root / 'gold-old.txt').write_text('TUNE: 1 gold parks | wrong land 0 of 1\nSEALED: 1 gold parks | wrong land 0 of 1\n', encoding='utf-8')
    (root / 'gold-new.txt').write_text('TUNE: 1 gold parks | wrong land 0 of 1\nSEALED: 1 gold parks | wrong land 1 of 1\n', encoding='utf-8')
    # the new key has no US-9004, so that park lost its outline
    text = mod.write_packet(root / 'packet', ['AA', 'BB', 'CC'], root / 'builds', root / 'fc-old', root / 'fc-new',
                            root / 'gold-old.txt', root / 'gold-new.txt',
                            {'pr': '9', 'head': 'abcdef1234567890', 'old': '1234567890abcdef', 'entries': ['sample-rule'],
                             'states_from': 'scope', 'build_date': '2026-11-19', 'data_commit': 'ddd'}, 
                            [{'name': 'US-AA.json.gz', 'createdAt': '2026-11-01T00:00:00Z', 'size': 10}])
    packet = root / 'packet'
    csv_text = (packet / 'parks-changed.csv').read_text(encoding='utf-8')
    fact = (packet / 'factcheck-diff.csv').read_text(encoding='utf-8')
    check('US-9001' in csv_text and '1001' in csv_text and 'North Sample Preserve' in csv_text, 'the lost record is in the park table')
    check('US-9002' not in csv_text, 'a park whose joined records did not change is not in the park table')
    check('1006' in csv_text and 'South Sample Addition' in csv_text, 'a gained record is in the park table')
    check('verified -> flagged (the pin is 4.0 km outside the nearest piece)' in csv_text, 'a worse class keeps the flag words')
    check('US-9001' in fact and 'verified got worse' in fact and '4' in fact, 'the fact table has the pin and the worse class')
    check('verified outline lost' in fact and 'US-9004' in fact, 'a verified park with no joined record left is lost')
    check('US-9002' in fact and 'class or flags differ' in fact, 'a soft flag change is reported and is not a hard loss')
    check('build timed out' in text and 'build failed or timed out' in text, 'a timed out state and a missing state are both rows')
    check('the TUNE line or the SEALED line differs' in text, 'a gold change is said in plain words')
    check('sample rule: 2 records to check' in (packet / 'notices-only-new.txt').read_text(encoding='utf-8'), 'the new-only notice is saved')
    check('sample rule: 1 record' in (packet / 'notices-only-old.txt').read_text(encoding='utf-8'), 'the old-only notice is saved')
    inputs = json.loads((packet / 'inputs.json').read_text(encoding='utf-8'))
    check(inputs['fixed_build_settings']['GEO_DETAIL'] == '0.001' and inputs['shapes']['US-AA.json.gz']['date'].startswith('2026-11-01'), 'the frozen settings and the shape date are recorded')
    check('North Sample Park' in text and 'This report only compares' in text, 'the summary is plain words on one page')
    # same gold lines
    same_gold = root / 'same.txt'
    same_gold.write_text('TUNE: 1 gold parks | wrong land 0 of 1\nSEALED: 1 gold parks | wrong land 0 of 1\n    a detail line that is not the score\n', encoding='utf-8')
    text2 = mod.write_packet(root / 'packet2', ['AA'], root / 'builds', None, None, same_gold, same_gold, {'pr': '9', 'head': 'abcdef1234567890', 'old': '1234567890abcdef'})
    check('are the same on both sides' in text2, 'matching gold score lines are the same even when a detail line differs')

# --- the script's own check, the way the workflow runs it ---
ran = subprocess.run([sys.executable, '-B', str(SCRIPT), '--selftest'], capture_output=True, text=True)
check(ran.returncode == 0 and 'selftest: ok' in ran.stdout, 'the script selftest passes with no network')
if ran.returncode != 0:
    print(ran.stdout)
    print(ran.stderr)

# --- the workflow keeps the house rules ---
text = WF.read_text(encoding='utf-8')
doc = yaml.safe_load(text)
on = doc.get(True) or doc.get('on') or {}
check(list(on) == ['workflow_dispatch'], 'the workflow starts by hand only')
check('schedule' not in text and 'workflow_run' not in text and 'cron:' not in text, 'no timer and it starts no other workflow')
check('gh pr comment' not in text and 'issues' not in text and '/dispatches' not in text and 'gh workflow run' not in text, 'it posts nothing and starts nothing')
check('--show-sealed' not in text, 'the sealed gold half is never opened')
check('key-quality/review-packets/' in text and 'tools-out' in text, 'the packet goes to tools-out under the review-packets folder')
check(text.count('persist-credentials: false') >= 4, 'the KPC-Links checkouts do not keep a token')
check("repository: KentuckyPortableClub/KPC-Links" in text, 'the two trees are KPC-Links, read only')
check((doc.get('permissions') or {}).get('contents') == 'read' and 'actions' not in (doc.get('permissions') or {}), 'the workflow itself can only read')
check((doc['jobs']['save'].get('permissions') or {}).get('contents') == 'write', 'only the save job is allowed to write')
check(all((job.get('permissions') or {}).get('contents') != 'write' for name, job in doc['jobs'].items() if name != 'save'), 'no scoring job can write the repo')
for name, job in (doc.get('jobs') or {}).items():
    steps = job.get('steps') or []
    g8 = [s for s in steps if 'hidden failures' in str(s.get('name') or '').lower()]
    check(bool(g8) and g8[-1].get('if') == 'always()' and steps[-1] is g8[-1] and 'kpc-hidden.txt' in (g8[-1].get('run') or ''), f'{name}: the hidden-failure report is the last step')
    if name == 'build':
        check((job.get('strategy') or {}).get('fail-fast') is False, 'one state failing does not cancel the others')
    for st in steps:
        run = st.get('run') or ''
        if re.search(r'(^|\n)\s*gh ', run) or ' gh ' in run:
            check((st.get('env') or {}).get('GH_TOKEN') == '${{ github.token }}', f'{name}: a step that calls gh is signed in')
ids_run = '\n'.join((s.get('run') or '') for s in doc['jobs']['scope']['steps'])
check('head.repo' in ids_run or 'full_name' in ids_run, 'a pull request from outside KPC-Links is refused')
check('KentuckyPortableClub/KPC-Links' in ids_run, 'the allowed pull request home is named')
build_run = '\n'.join((s.get('run') or '') for s in doc['jobs']['build']['steps'])
for key, value in mod.FIXED_BUILD_ENV.items():
    check(f'{key}={value}' in build_run or f'{key}: {value}' in build_run or f"{key}={value}" in text, f'the build fixes {key}')
check('KPC_PRESERVE_APART' in build_run and 'unset' in build_run, 'a switch in the runner environment cannot override the two trees')
check('pip install' not in build_run and 'shapely' not in build_run, 'the builds do not install shapely')
packet_run = '\n'.join((s.get('run') or '') for s in doc['jobs']['packet']['steps'])
save_run = '\n'.join((s.get('run') or '') for s in doc['jobs']['save']['steps'])
check('shapely' in packet_run and 'kpc_key_factcheck.py' in packet_run and 'kpc_key_grade.py' in packet_run, 'the fact check and the gold score run from the new tree')
check('kpc_push_retry.sh' not in packet_run and 'kpc_us_key.py' not in save_run and 'kpc_key_factcheck.py' not in save_run, 'the save job runs no key code')
check('kpc_push_retry.sh' in save_run and 'key-quality/review-packets' in save_run, 'the save uses the retry helper and only the packet folder')
check('created_at' in packet_run, 'shape dates are read from the release field created_at')
dates = mod._shape_index([{'name': 'US-AA.json.gz', 'created_at': '2026-11-02T00:00:00Z', 'size': 3}])
check(dates['US-AA.json.gz']['date'].startswith('2026-11-02'), 'the packet records created_at')

class StrictLoader(yaml.SafeLoader):
    pass
def _strict_map(loader, node, deep=False):
    seen = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f'repeated key {key!r}', key_node.start_mark)
        seen[key] = loader.construct_object(value_node, deep=deep)
    return seen
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_map)
try:
    yaml.load(text, Loader=StrictLoader)
    strict_ok, strict_why = True, ''
except yaml.constructor.ConstructorError as err:
    strict_ok, strict_why = False, str(err).splitlines()[0]
check(strict_ok, 'the workflow has no repeated key' + (f' ({strict_why})' if strict_why else ''))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
