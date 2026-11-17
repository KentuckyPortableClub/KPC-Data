#!/usr/bin/env python3
"""Nov 16: the waiting-room documents re-test must count only a definite dead
answer (404, 410, or a gone domain) as dead. Connection errors, timeouts and
5xx are 'could not check' (not a fault; one retry). A link already read OK in
the live file is not a new fault from this file. The sampled list and each
per-link result are saved on the verdict. Sample size stays 20. Offline:
synthetic records, the network is mocked, nothing in the repo is written."""
import importlib.util, io, os, pathlib, socket, sys, tempfile, urllib.error

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-wr-retest-'))
os.environ['DATA'] = str(tmp); os.environ['LINKS'] = str(tmp / 'nolinks')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
spec = importlib.util.spec_from_file_location('wr_docs_retest', HERE / '.github/scripts/kpc_waiting_room.py')
WR = importlib.util.module_from_spec(spec); spec.loader.exec_module(WR)
WR.NET = True
WR.c_status = lambda *a, **k: ([], [])


class FakeResp:
    def __init__(self, status): self.status = status
    def __enter__(self): return self
    def __exit__(self, *a): return False


def http_err(url, code):
    return urllib.error.HTTPError(url, code, 'err', {}, io.BytesIO(b''))


# scripted answers for each URL: a value, or a list of values (for a retry)
SCRIPT = {}
CALLS = {}


def mock_open(u, timeout=30):
    CALLS[u] = CALLS.get(u, 0) + 1
    ans = SCRIPT[u]
    if isinstance(ans, list):
        step = ans[min(CALLS[u] - 1, len(ans) - 1)]
    else:
        step = ans
    if isinstance(step, Exception):
        raise step
    return FakeResp(step)


WR.open_link = mock_open


def fd(holds, tag):
    return [h for h in holds if h.startswith(tag)]


def park(i, url, status='ok'):
    return {'n': f'Park {i}', 't': 'State Park', 'page': f'https://p{i}.example.test/',
            'map': {'url': url, 'how': 'on file', 'status': status, 'kind': 'pdf'},
            'rules': {'url': '', 'how': '', 'status': 'not found'}}


def area(parks):
    return {'area': 'US-XX', 'parks': parks}


def twenty(kind_of):
    """20 parks, unique hosts (no 2-second gap). kind_of(i, url) -> script value."""
    parks, live = {}, {}
    for i in range(20):
        u = f'https://p{i}.example.test/map.pdf'
        parks[f'US-{1000+i}'] = park(i, u)
        live[f'US-{1000+i}'] = park(i, u)
        SCRIPT[u] = kind_of(i, u)
    return parks, live


def run(parks, live, ctx=None):
    CALLS.clear()
    ctx = {} if ctx is None else ctx
    holds, notes = WR.c_docs('data/docs/US-XX.json', area(parks), area(live) if live is not None else None, ctx)
    return holds, notes, ctx


# (a) the hole: 3 timeouts + 17 ok. Today's check counted timeouts as dead and held (3 of 20).
SCRIPT.clear()
parks, live = twenty(lambda i, u: TimeoutError('timed out') if i < 3 else 200)
holds, notes, ctx = run(parks, live)
check(not fd(holds, 'F-D3'), f'three timeouts are could-not-check, not F-D3 ({fd(holds, "F-D3")})')
check(sum(1 for r in ctx['retest']['results'] if r['result'] == 'could not check') == 3
      and sum(1 for r in ctx['retest']['results'] if r['result'] == 'ok') == 17,
      'those three are recorded as could not check, the rest ok')
soft = [f'https://p{i}.example.test/map.pdf' for i in range(3)]
hard = [f'https://p{i}.example.test/map.pdf' for i in range(3, 20)]
check(all(CALLS[u] == 2 for u in soft) and all(CALLS[u] == 1 for u in hard),
      'a timeout is retried once; an ok link is not')

# (b) connection errors and 5xx (still 5xx after retry) are also not a fault
SCRIPT.clear(); CALLS.clear()
parks, live = twenty(lambda i, u: (
    urllib.error.URLError(ConnectionRefusedError('refused')) if i < 2 else
    http_err(u, 503) if i < 5 else 200))
holds, notes, ctx = run(parks, live)
check(not fd(holds, 'F-D3'), f'connection errors and 5xx are not F-D3 ({fd(holds, "F-D3")})')
check(sum(1 for r in ctx['retest']['results'] if r['result'] == 'could not check') == 5,
      'two connection errors and three 503s are could not check')

# (c) a 503 that succeeds on the retry is ok
SCRIPT.clear(); CALLS.clear()
parks, live = twenty(lambda i, u: [http_err(u, 503), 200] if i == 0 else 200)
holds, notes, ctx = run(parks, live)
check(not fd(holds, 'F-D3'), 'a 503 that opens on retry is not a fault')
u0 = 'https://p0.example.test/map.pdf'
check(CALLS[u0] == 2 and next(r for r in ctx['retest']['results'] if r['url'] == u0)['result'] == 'ok',
      'the retried 503 is recorded as ok')

# (d) 401/403/405/429 still count as alive (the host answered)
SCRIPT.clear()
codes = {0: 401, 1: 403, 2: 405, 3: 429}
parks, live = twenty(lambda i, u: http_err(u, codes[i]) if i in codes else 200)
holds, notes, ctx = run(parks, live)
check(not fd(holds, 'F-D3') and all(r['result'] == 'ok' for r in ctx['retest']['results']),
      '401/403/405/429 are still treated as alive')

# (e) two definite 404s among 20 are F-D3; sample size stays 20. Live does not
# already have these URLs as ok (they are new faults).
SCRIPT.clear()
parks, _ = twenty(lambda i, u: http_err(u, 404) if i < 2 else 200)
holds, notes, ctx = run(parks, None)
check(len(fd(holds, 'F-D3')) == 1 and '2 of 20' in fd(holds, 'F-D3')[0] and 'definitely dead' in fd(holds, 'F-D3')[0],
      f'two 404s that are not already ok in live are F-D3 ({fd(holds, "F-D3")})')
check(len(ctx['retest']['sample']) == 20 and len(ctx['retest']['results']) == 20,
      'the sample size stays 20')

SCRIPT.clear()
parks, _ = twenty(lambda i, u: http_err(u, 410) if i < 2 else 200)
holds, notes, ctx = run(parks, None)
check(len(fd(holds, 'F-D3')) == 1, f'two 410s are also definite dead ({fd(holds, "F-D3")})')

# (f) a gone domain is definite dead; a temporary DNS failure is not
SCRIPT.clear()
parks, _ = twenty(lambda i, u: (
    urllib.error.URLError(socket.gaierror(-2, 'Name or service not known')) if i < 2 else 200))
holds, notes, ctx = run(parks, None)
check(len(fd(holds, 'F-D3')) == 1 and all(r['detail'] == 'gone domain' for r in ctx['retest']['results'] if r['result'] == 'dead'),
      f'two gone domains are F-D3 ({fd(holds, "F-D3")})')
SCRIPT.clear()
parks, live = twenty(lambda i, u: (
    urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN, 'Temporary failure in name resolution')) if i < 3 else 200))
holds, notes, ctx = run(parks, live)
check(not fd(holds, 'F-D3') and sum(1 for r in ctx['retest']['results'] if r['result'] == 'could not check') == 3,
      'a temporary DNS failure is could not check, not dead')

# (g) a 404 already read OK in the live file is not a new fault from this file
SCRIPT.clear()
parks, live = twenty(lambda i, u: http_err(u, 404) if i < 2 else 200)
holds, notes, ctx = run(parks, live)  # live also has those URLs as status ok
check(not fd(holds, 'F-D3'), f'two 404s already ok in live are not F-D3 ({fd(holds, "F-D3")})')
check(any('already ok in live, not a new fault' in n for n in notes),
      'the verdict notes say those dead links were already ok in live')

# two 404s already ok in live PLUS two new 404s -> only the new ones are a fault
SCRIPT.clear()
parks, live_p = twenty(lambda i, u: http_err(u, 404) if i < 4 else 200)
# live is missing the last two of those four (i=2,3 are new)
for i in (2, 3):
    live_p[f'US-{1000+i}']['map']['url'] = f'https://p{i}.example.test/other.pdf'
    live_p[f'US-{1000+i}']['map']['status'] = 'ok'
holds, notes, ctx = run(parks, live_p)
check(len(fd(holds, 'F-D3')) == 1 and '2 of 20' in fd(holds, 'F-D3')[0],
      f'only the two 404s not already ok in live count ({fd(holds, "F-D3")})')

# no live copy: two 404s still count (first publish)
SCRIPT.clear()
parks, _ = twenty(lambda i, u: http_err(u, 404) if i < 2 else 200)
holds, notes, ctx = run(parks, None)
check(len(fd(holds, 'F-D3')) == 1, f'with no live file, two 404s are still F-D3 ({fd(holds, "F-D3")})')

# (h) 25 links, sample stays 20; verdict carries the sample and per-link results
SCRIPT.clear()
parks, live = {}, {}
for i in range(25):
    u = f'https://p{i}.example.test/map.pdf'
    parks[f'US-{1000+i}'] = park(i, u)
    live[f'US-{1000+i}'] = park(i, u)
    SCRIPT[u] = 200
holds, notes, ctx = run(parks, live)
check(len(ctx['retest']['sample']) == 20 and len(ctx['retest']['results']) == 20,
      'when more than 20 links exist, 20 are sampled')
check(all(r['url'] in ctx['retest']['sample'] and r['result'] in ('ok', 'dead', 'could not check') and 'detail' in r
          for r in ctx['retest']['results']),
      'each sampled link has a result and a detail on the verdict')
check(any(n.startswith('F-D3 retest 20 links:') for n in notes) and any(n.startswith('F-D3 links:') for n in notes),
      'the notes also record the sample summary and the per-link results')

# judge() writes the same retest block onto the verdict
SCRIPT.clear()
parks, live = twenty(lambda i, u: 200)
res = WR.judge('data/docs/US-XX.json', area(parks), area(live))
check(res.get('verdict') == 'PASS' and isinstance(res.get('retest'), dict)
      and len(res['retest']['sample']) == 20 and len(res['retest']['results']) == 20,
      f"judge() saves the sample and per-link results on the verdict ({res.get('verdict')})")

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
