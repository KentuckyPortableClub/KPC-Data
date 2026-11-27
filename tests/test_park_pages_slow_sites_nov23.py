#!/usr/bin/env python3
"""Job 10, 23 Nov 2026: parks waiting on SLOW sites (a long Crawl-delay: New York State Parks 196, Utah State Parks 24) are
listed for the PC's 2g step, which alone may wait up to 15 minutes a page (KPC_MAX_CRAWL_DELAY, never more than 900 s; the
nightly walk keeps 120 s). Invented parks; no request. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_park_pages_slow as SLOW  # noqa: E402
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


with tempfile.TemporaryDirectory() as d:
    t = pathlib.Path(d); (t / 'facts').mkdir()
    (t / 'facts' / 'US-ZZ.json').write_text(json.dumps({'parks': {
        'US-9801': {'asked': {'url': 'https://parks.zz.invented.gov/parks/1'}, 'page': {'kind': 'resting', 'status': 'crawl-delay'}},
        'US-9802': {'asked': {'url': 'https://stateparks.zz.invented.gov/p/2'}, 'page': {'kind': 'resting', 'status': 'deferred'}},
        'US-9803': {'asked': {'url': 'https://blm.zz.invented.gov/p/3'}, 'page': {'kind': 'resting', 'status': 'rest'}},
        'US-9804': {'asked': {'url': 'https://parks.zz.invented.gov/parks/4'}, 'page': {'kind': 'html', 'status': 200}}}}))
    refs, hosts = SLOW.waiting(str(t / 'facts'))
    check('only the parks waiting on a long Crawl-delay or a slow site\'s nightly share are listed', refs == ['US-9801', 'US-9802'])
    check('counted by site', hosts['parks.zz.invented.gov'] == 1 and hosts['stateparks.zz.invented.gov'] == 1)
    r = subprocess.run([sys.executable, '-B', str(ROOT / '.github/scripts/kpc_park_pages_slow.py'), '--out', str(t)], capture_output=True, text=True)
    check('the lister writes slow-refs.json and prints the count', r.returncode == 0 and json.loads((t / 'slow-refs.json').read_text()) == refs
          and '2 parks wait on slow sites.' in r.stdout)
code = 'import kpc_park_pages, kpc_manners as M; print(M.MAX_CRAWL_DELAY)'
env = dict(os.environ, PYTHONPATH=str(ROOT / '.github/scripts'))
get = lambda v: subprocess.run([sys.executable, '-B', '-c', code], env=dict(env, KPC_MAX_CRAWL_DELAY=v) if v is not None else env,
                               capture_output=True, text=True).stdout.strip()
env.pop('KPC_MAX_CRAWL_DELAY', None)
check('the nightly walk keeps 120 s', get(None) == '120')
check('the 2g step may wait 900 s', get('900') == '900.0')
# 26 Nov 2026 (owner's site rule: 'obey it by going slow, however long; never skip because it is long'): the 900 s cap is gone
check('no upper cap (5000 s is obeyed), never less than 120 s, a bad value changes nothing', get('5000') == '5000.0' and get('30') == '120' and get('x') == '120')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
