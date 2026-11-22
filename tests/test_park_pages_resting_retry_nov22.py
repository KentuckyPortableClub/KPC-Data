#!/usr/bin/env python3
"""Page reader, 22 Nov 2026: a page that answered 'resting' (the host was busy, a server error, an empty answer) is tried again the
next day, not after the 30-day refresh. A page read fine still waits, a refused one is not asked again early, and a resting page is
not asked twice on the same day. Invented parks only. Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_work as W  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


areas = {'US-ZZ': {r: {'website': f'https://parks.invented.example/{r}', 'qsos': 1} for r in ('US-9001', 'US-9002', 'US-9003', 'US-9004')}}
choose = lambda ref, row: row['website']
state = {'read': {'US-9001': {'date': '2026-11-20', 'kind': 'resting'}, 'US-9002': {'date': '2026-11-20', 'kind': 'html'},
                  'US-9003': {'date': '2026-11-20', 'kind': 'refused'}, 'US-9004': {'date': '2026-11-22', 'kind': 'resting'}}}
order = W.build_worklist(areas, choose, {}, [], [], state, '2026-11-22')
got = {o['ref']: o['why'] for o in order}
check('a page that was resting two days ago is tried again', got.get('US-9001') == 'resting last time: tried again')
check('a page read fine two days ago still waits for the refresh', 'US-9002' not in got)
check('a refused page is not asked again early (robots.txt and refusals are kept)', 'US-9003' not in got)
check('a page that was resting today is not asked again today', 'US-9004' not in got)
order = W.build_worklist(areas, choose, {}, [], [], {'read': {'US-9002': {'date': '2026-10-01', 'kind': 'html'}, **{k: v for k, v in state['read'].items() if k != 'US-9002'}}}, '2026-11-22')
check('the retried resting page comes before the 30-day refreshes', [o['ref'] for o in order][:2] == ['US-9001', 'US-9002'])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
