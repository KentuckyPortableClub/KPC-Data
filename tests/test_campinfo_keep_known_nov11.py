#!/usr/bin/env python3
"""Nov 11 (data-quality review): the campground info bot rebuilds each record blank on every re-read, so a blocked page (403, robots,
host resting, soft 404, a script-built page, a bot error) used to REPLACE a record that had facts and source lines with an empty one.
keep_known() keeps the earlier record and says why the re-read failed. Offline: the page read is replaced by a stub, nothing is fetched."""
import json, os, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TMP = tempfile.mkdtemp(prefix='kpc-campinfo-keep-')
os.environ['OUT'] = TMP
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_campinfo_bot as C   # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


ROW = {'name': 'Pine Camp', 'lat': 36.1, 'lon': -85.2, 'park': 'Pine SP', 'agency': 'state', 'kind': 'campground', 'page': 'https://example.test/pine',
       'reserve': '', 'src': 'campstate', 'id': 'pine'}


def good():
    r = C.blank_record(ROW)
    C.apply_facts(r, {'sites.total': C.fact(42, 'https://example.test/pine', 'The campground has 42 sites'),
                      'dump_station': C.fact(True, 'https://example.test/pine', 'dump station on site')})
    r['status'] = 'ok'; r['checked'] = '2026-09-01'
    return r


def failed(status):
    r = C.blank_record(ROW); r['status'] = status
    return r


old = good()
check(C.has_facts(old), 'fixture: the earlier record has facts')
for st in ('HTTP 403 -> needs browser', 'robots.txt says no', 'host resting', 'soft 404', 'bot error: boom',
           'ok, no campground facts in the page text: needs browser?', 'needs RIDB_API_KEY secret in KPC-Data'):
    k = C.keep_known(old, failed(st))
    check(k['sites']['total'] == 42 and k['dump_station'] is True and k['facts_src']['sites.total']['line'] == 'The campground has 42 sites',
          f'{st!r}: the earlier facts and their source lines stay')
    check(k['last_read_failed'] == C.TODAY and k['last_read_status'] == st, f'{st!r}: the failed re-read is written on the record')
    check(k['checked'] == '2026-09-01', f'{st!r}: the old checked date stays, so the next run tries again')
check('last_read_failed' not in old, 'the earlier record object is not changed')

fresh = good(); fresh['sites']['total'] = 40; fresh['status'] = 'ok'
check(C.keep_known(old, fresh) is fresh, 'a re-read that found facts replaces the record (a changed value is a real change)')
check(C.keep_known(None, failed('HTTP 403 -> needs browser'))['status'] == 'HTTP 403 -> needs browser', 'no earlier record: the failed read is the record, as before')
only_elev = C.blank_record(ROW); only_elev['elevation_ft'] = {'value': 900, 'src': 'x'}; only_elev['status'] = 'ok'
check(C.keep_known(only_elev, failed('host resting'))['status'] == 'host resting', 'an earlier record with no campground facts is not kept')

# the whole area loop: stub the list and the page read; no network
C.camp_rows = lambda area: {'pine': ROW}
calls = []
def stub_one(area, r, state): calls.append(r['id']); return failed('HTTP 403 -> needs browser')
C.one_camp = stub_one
C.merge_duplicates = lambda D: None
D0 = {'area': 'US-TN', 'camps': {'pine': dict(old, ver=C.VER)}}
pathlib.Path(TMP, 'US-TN.json').write_text(json.dumps(D0), encoding='utf-8')
state = {'areas': {}}
C.run_area('US-TN', state)
D1 = json.loads(pathlib.Path(TMP, 'US-TN.json').read_text(encoding='utf-8'))
rec = D1['camps']['pine']
check(calls == ['pine'], 'the stale record was re-read once')
check(rec['sites']['total'] == 42 and rec['last_read_status'] == 'HTTP 403 -> needs browser', 'run_area keeps the facts after a blocked re-read')
check(D1['counts'].get('kept_after_failed_read') == 1, f"counts say one record was kept after a failed read ({D1['counts'].get('kept_after_failed_read')})")
check(D1['counts'].get('with_facts') == 1, 'the kept record still counts as having facts')
# a bot error inside the read
def boom(area, r, state): raise RuntimeError('boom')
C.one_camp = boom
pathlib.Path(TMP, 'US-TN.json').write_text(json.dumps(D0), encoding='utf-8')
C.run_area('US-TN', {'areas': {}})
rec = json.loads(pathlib.Path(TMP, 'US-TN.json').read_text(encoding='utf-8'))['camps']['pine']
check(rec['sites']['total'] == 42 and rec['last_read_status'].startswith('bot error'), 'a bot error also keeps the earlier facts')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
