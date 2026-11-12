#!/usr/bin/env python3
"""Nov 11 (data-quality review): when a re-read of one park raised inside the truth checker or the hours bot, the park's earlier row (a real
verdict, hours and fees with their source lines) was REPLACED by an empty 'bot error' row. Both bots already kept the earlier row when every
page failed; a bot error now does the same (marked last_read_failed / last_read_error; 'checked' stays so it is tried again). A park with
no earlier real row still gets the 'bot error' row. Offline: one_park / the park list are stubs."""
import json, os, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TMP = tempfile.mkdtemp(prefix='kpc-workshop-err-')
os.environ['OUT'] = TMP
os.chdir(TMP)
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_truth_bot as T   # noqa: E402
os.environ['OUT'] = TMP + '/hours'
import kpc_hours_bot as H   # noqa: E402
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def boom(*a, **k): raise RuntimeError('boom')


# ---- truth checker
T.OUT = pathlib.Path(TMP)
T.park_list = lambda area: {'US-1': {'n': 'Pine SP', 't': 'State Park'}, 'US-2': {'n': 'Oak SP', 't': 'State Park'}}
T.ours_key = lambda rec: {'acres': 1000, 'pin': 'inside', 'pieces': [], 'src': 'x'}
T.news_hints = lambda *a, **k: {}
T.one_park = boom
D0 = {'area': 'US-TN', 'parks': {'US-1': {'n': 'Pine SP', 'verdict': 'agree', 'pct': 3, 'official': {'acres': 1030, 'url': 'https://example.test/p', 'line': '1,030 acres'},
                                           'checked': '2026-10-01', 'ver': 0, 'handover': [], 'score': 6}}}
pathlib.Path(TMP, 'US-TN.json').write_text(json.dumps(D0))
st = {'areas': {}, 'news': {}}
T.run_area('US-TN', st, {}, {}, {}, {}, {}, {}, {})
D1 = json.loads(pathlib.Path(TMP, 'US-TN.json').read_text())
r1, r2 = D1['parks']['US-1'], D1['parks']['US-2']
check(r1['verdict'] == 'agree' and r1['official']['acres'] == 1030 and r1['last_read_error'].startswith('bot error') and r1['checked'] == '2026-10-01',
      'truth: the earlier verdict and source line stay after a bot error, marked, and still due for a re-read')
check(r2['verdict'].startswith('bot error'), 'truth: a park with no earlier row gets the bot-error row, as before')

# ---- hours bot
H.OUT = pathlib.Path(TMP) / 'hours'
H.OUT.mkdir(exist_ok=True)
H.one_park = boom
D0 = {'area': 'US-TN', 'parks': {'US-1': {'n': 'Pine SP', 'status': 'ok', 'hours': [{'line': 'Open 8 AM - 5 PM daily', 'url': 'https://example.test/h'}], 'fees': [], 'permits': [],
                                           'checked': '2026-07-01', 'ver': 0}}}
(H.OUT / 'US-TN.json').write_text(json.dumps(D0))
st = {'areas': {}}
H.run_area('US-TN', st, {}, {}, {})
D1 = json.loads((H.OUT / 'US-TN.json').read_text())
r1, r2 = D1['parks']['US-1'], D1['parks']['US-2']
check(r1['status'] == 'ok' and r1['hours'][0]['line'].startswith('Open 8 AM') and r1['last_read_error'].startswith('bot error') and r1['checked'] == '2026-07-01',
      'hours: the earlier hours line stays after a bot error, marked')
check(r2['status'].startswith('bot error') and r2['hours'] == [], 'hours: a park with no earlier row gets the bot-error row, as before')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
