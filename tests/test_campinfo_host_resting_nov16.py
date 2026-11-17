#!/usr/bin/env python3
"""Nov 16: when a host is struck out or robots-blocked, the campground bot used to write 'host resting'
or 'robots.txt says no' over the earlier record and blank the facts. Brandon: leave those camps as they
were (the live / earlier record), and do not fetch what robots disallows. Offline: the page read is
replaced by a stub, nothing is fetched, and nothing in the repo is written."""
import json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TMP = tempfile.mkdtemp(prefix='kpc-camp-rest-out-')
os.environ['OUT'] = TMP
os.environ.pop('LIVE_CAMPINFO', None)
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_campinfo_bot as C   # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


ROW = {'name': 'Pine Camp', 'lat': 36.1, 'lon': -85.2, 'park': 'Pine SP', 'agency': 'state', 'kind': 'campground',
       'page': 'https://example.test/pine', 'reserve': 'https://example.test/reserve/pine', 'src': 'campstate', 'id': 'pine'}


def good():
    r = C.blank_record(ROW)
    C.apply_facts(r, {'sites.total': C.fact(42, 'https://example.test/pine', 'The campground has 42 sites'),
                      'dump_station': C.fact(True, 'https://example.test/pine', 'dump station on site')})
    r['status'] = 'ok'
    r['checked'] = '2026-09-01'
    return r


def booking_only():
    """A live record whose only stored fact is a booking link (has_facts() is false)."""
    r = C.blank_record(ROW)
    r['booking'] = {'url': 'https://example.test/reserve/pine', 'how': 'online: example.test'}
    r['facts_src'] = {'booking.url': {'url': 'https://example.test/pine', 'date': '2026-09-01',
                                      'line': 'Reserve a site'}}
    r['status'] = 'ok'
    r['checked'] = '2026-09-01'
    return r


def failed(status):
    r = C.blank_record(ROW)
    r['status'] = status
    r['checked'] = '2026-11-16'
    r['ver'] = C.VER
    return r


# --- keep_known: struck-out / robots-blocked host leaves the camp as it was
old = good()
for st in ('host resting', 'robots.txt says no',
           'host resting (robots.txt could not be read: next run)',
           'host resting (deferred: slow host, next run)'):
    k = C.keep_known(old, failed(st))
    check(k['sites']['total'] == 42 and k['dump_station'] is True and k['status'] == 'ok',
          f'{st!r}: the earlier facts and status stay (not replaced with the resting/robots status)')
    check(k['checked'] == '2026-09-01' and k['last_read_status'] == st,
          f'{st!r}: the old checked date stays; the failed re-read is noted')
check('last_read_failed' not in old, 'the earlier record object is not changed')

book = booking_only()
check(not C.has_facts(book), 'fixture: a booking-only record is not has_facts()')
k = C.keep_known(book, failed('host resting'))
check(k['status'] == 'ok' and (k.get('booking') or {}).get('url') == 'https://example.test/reserve/pine',
      'a booking-only earlier record is left as it was when the host is resting')
k = C.keep_known(book, failed('robots.txt says no'))
check(k['status'] == 'ok' and (k.get('booking') or {}).get('url') == 'https://example.test/reserve/pine',
      'a booking-only earlier record is left as it was when robots.txt says no')

# a page-level 403 on a booking-only record is unchanged (still not kept)
k = C.keep_known(book, failed('HTTP 403 -> needs browser'))
check(k['status'] == 'HTTP 403 -> needs browser', 'a page-level 403 on a booking-only record is still the failed read')

# no earlier record: the failed status stands
check(C.keep_known(None, failed('host resting'))['status'] == 'host resting',
      'no earlier record: host resting is the record, as before')

# --- run_area: published live file is found even when OUT is a work folder and LIVE_CAMPINFO is unset
# (main only looked at git HEAD when OUT was cwd/data/campinfo, so a held working copy in another folder
# lost the live facts). Nothing is fetched. A tiny throwaway git repo holds the published file.
GIT = pathlib.Path(tempfile.mkdtemp(prefix='kpc-camp-rest-git-'))
(GIT / 'data' / 'campinfo').mkdir(parents=True)
pub = {'area': 'US-ZZ', 'camps': {'pine': good()}}
(GIT / 'data' / 'campinfo' / 'US-ZZ.json').write_text(json.dumps(pub), encoding='utf-8')
subprocess.run(['git', 'init', '-q'], cwd=GIT, check=True)
subprocess.run(['git', '-C', str(GIT), 'config', 'user.name', 'KPC test'], check=True)
subprocess.run(['git', '-C', str(GIT), 'config', 'user.email', 'test@example.test'], check=True)
subprocess.run(['git', '-C', str(GIT), 'add', 'data/campinfo/US-ZZ.json'], check=True)
subprocess.run(['git', '-C', str(GIT), 'commit', '-q', '-m', 'published live'], check=True)

C.repo_root = lambda: GIT
C.OUT = pathlib.Path(TMP)
os.environ.pop('LIVE_CAMPINFO', None)
C.camp_rows = lambda area: {'pine': ROW}
C.one_camp = lambda area, r, state: failed('host resting')
C.merge_duplicates = lambda D: None

pathlib.Path(TMP, 'US-ZZ.json').write_text(json.dumps({
    'area': 'US-ZZ',
    'camps': {'pine': dict(failed('host resting'), ver=C.VER)},
}), encoding='utf-8')
C.run_area('US-ZZ', {'areas': {}})
rec = json.loads(pathlib.Path(TMP, 'US-ZZ.json').read_text(encoding='utf-8'))['camps']['pine']
check(rec['sites']['total'] == 42 and rec['dump_station'] is True and rec['status'] == 'ok',
      'run_area keeps the live facts and status when OUT is not data/campinfo and LIVE_CAMPINFO is unset')
check(rec.get('last_read_status') == 'host resting' and rec.get('checked') == '2026-09-01',
      'the struck-out re-read is noted; the live checked date stays')
check(pathlib.Path(GIT, 'data/campinfo/US-ZZ.json').read_text(encoding='utf-8') == json.dumps(pub),
      'the published live file in the throwaway repo is not written')

# robots-blocked re-read, same setup
C.one_camp = lambda area, r, state: failed('robots.txt says no')
pathlib.Path(TMP, 'US-ZZ.json').write_text(json.dumps({
    'area': 'US-ZZ',
    'camps': {'pine': dict(failed('robots.txt says no'), ver=C.VER)},
}), encoding='utf-8')
C.run_area('US-ZZ', {'areas': {}})
rec = json.loads(pathlib.Path(TMP, 'US-ZZ.json').read_text(encoding='utf-8'))['camps']['pine']
check(rec['sites']['total'] == 42 and rec['status'] == 'ok' and rec.get('last_read_status') == 'robots.txt says no',
      'run_area also keeps the live record when robots.txt says no')


# booking-only live record, emptied host-resting working copy, no LIVE_CAMPINFO
C.one_camp = lambda area, r, state: failed('host resting')
book_pub = {'area': 'US-ZZ', 'camps': {'pine': booking_only()}}
(GIT / 'data' / 'campinfo' / 'US-ZZ.json').write_text(json.dumps(book_pub), encoding='utf-8')
subprocess.run(['git', '-C', str(GIT), 'add', 'data/campinfo/US-ZZ.json'], check=True)
subprocess.run(['git', '-C', str(GIT), 'commit', '-q', '-m', 'booking-only live'], check=True)
pathlib.Path(TMP, 'US-ZZ.json').write_text(json.dumps({
    'area': 'US-ZZ',
    'camps': {'pine': dict(failed('host resting'), ver=C.VER)},
}), encoding='utf-8')
C.run_area('US-ZZ', {'areas': {}})
rec = json.loads(pathlib.Path(TMP, 'US-ZZ.json').read_text(encoding='utf-8'))['camps']['pine']
check(rec['status'] == 'ok' and (rec.get('booking') or {}).get('url') == 'https://example.test/reserve/pine',
      'run_area leaves a booking-only live record as it was when the working copy was emptied by host resting')


# a live bot-error with no facts is not treated as "how the camp was"
err = failed("bot error: URL can't contain control characters")
err['checked'] = '2026-10-01'
check(C.earlier_record(failed('host resting'), err)['status'] == 'host resting',
      'a live bot-error with no facts is not preferred over a resting working copy')

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
