#!/usr/bin/env python3
"""Nov 11 (data-quality review): the waiting room's campinfo check (c_campinfo) had no look at facts the LIVE file has and the NEW file lost.
A day of blocked reads that emptied the records still passed. F-I6 holds a file whose count of campgrounds with source-lined facts fell
by more than 30% (same rule and floor as the other drop checks). Offline: plain dicts, nothing is read from disk or the network."""
import importlib.util, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-wr-ci-'))
os.environ['DATA'] = str(tmp); os.environ['LINKS'] = str(tmp / 'nolinks')
sys.path.insert(0, str(HERE / '.github/scripts'))
spec = importlib.util.spec_from_file_location('wr_campinfo', HERE / '.github/scripts/kpc_waiting_room.py')
WR = importlib.util.module_from_spec(spec); spec.loader.exec_module(WR)


def camp(i, facts=True):
    c = {'name': f'Camp {i}', 'agency': f'agency{i % 5}', 'sites': {'total': 10 + i}, 'facts_src': {}}
    if facts: c['facts_src'] = {'sites.total': {'url': 'https://example.test/' + str(i), 'date': '2026-11-01', 'line': 'x sites'}}
    return c


def file_of(n_facts, n_total=20):
    return {'camps': {f'c{i}': camp(i, i < n_facts) for i in range(n_total)}}


live = file_of(20)
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(20), live, {})
check(not [h for h in holds if h.startswith('F-I6')], 'same number of camps with facts: no F-I6')
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(15), live, {})
check(not [h for h in holds if h.startswith('F-I6')], '15 of 20 kept (25% lost): no F-I6')
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(5), live, {})
h6 = [h for h in holds if h.startswith('F-I6')]
check(len(h6) == 1 and '20 -> 5' in h6[0], f'20 -> 5: held with F-I6 ({h6})')
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(0), live, {})
check(any(h.startswith('F-I6') for h in holds), 'every record emptied: held')
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(0), None, {})
check(not [h for h in holds if h.startswith('F-I6')], 'no live copy (first publish): no F-I6')
small_live = file_of(5, 8)
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(0, 8), small_live, {})
check(not [h for h in holds if h.startswith('F-I6')], 'a live file under the 10-camp floor is too small to judge: no F-I6')
holds, _ = WR.c_campinfo('data/campinfo/US-TN.json', file_of(5), {'camps': ['not', 'a', 'dict']}, {})
check(not [h for h in holds if h.startswith('F-I6')], 'a live file of the wrong shape counts as empty and does not crash')
# the whole judge: a HOLD verdict for the emptied file, PASS for the same file
res = WR.judge('data/campinfo/US-TN.json', file_of(5), live)
check(res['verdict'] == 'HOLD' and any('F-I6' in w for w in res['why']), f"judge(): HOLD with F-I6 ({res['verdict']})")
res = WR.judge('data/campinfo/US-TN.json', file_of(20), live)
check(res['verdict'] == 'PASS', f"judge(): the unchanged file passes ({res['verdict']} {res['why']})")
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
