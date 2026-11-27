#!/usr/bin/env python3
"""Tests for the 26 Nov 2026 page-reader fixes (A site rule, B names, C sizes, D re-read kept pages, E status page,
G saving correctly, H doing less). No network: every socket is shut and urlopen is a dictionary (kpc_fake_web.py).

  python test_page_reader_fixes.py        -> one line: ALL PASS, or the FAIL lines
"""
import gzip, json, os, pathlib, shutil, sys, tempfile, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpc_fake_web as FW  # noqa: E402  (shuts the network first)
import kpc_net_rule as NR  # noqa: E402
import kpc_manners as KM  # noqa: E402
import kpc_park_pages as P  # noqa: E402
import kpc_park_pages_rules as R  # noqa: E402
import kpc_page_status as ST  # noqa: E402

TESTS = []


def test(f):
    TESTS.append(f)
    return f


def web(pages):
    KM.MAX_CRAWL_DELAY = 120
    return FW.FakeWeb(pages).install(KM, P)


def ua_manners():
    M = KM.Manners('test reader')
    M.say = None   # 27 Nov 2026: the waiting lines stay off the test screen (one line per test file)
    return M


ROBOTS_OK = (200, 'User-agent: *\nDisallow: /private\n', {'Content-Type': 'text/plain'})
PAGE = '<html><head><title>Rib Mountain State Park | Wisconsin DNR</title></head><body><h1>Rib Mountain State Park</h1>' + ('<p>words</p>' * 120) + '</body></html>'


# ------------------------------------------------------------------------------------------------ A: the site rule
@test
def a_table_every_robots_line():
    cases = [((200, b'User-agent: *\nDisallow: /x\n'), 'rules'), ((404, b''), 'no-rules'), ((410, b''), 'no-rules'),
             ((401, b''), 'no-rules'), ((403, b''), 'no-rules'), ((418, b''), 'no-rules'), ((429, b''), 'busy'),
             ((500, b''), 'busy'), ((503, b''), 'busy'), ((None, b''), 'busy'), ((200, b''), 'no-rules'),
             ((200, b'x' * 600_000), 'rules')]
    for (st, body), want in cases:
        assert NR.robots_verdict(st, body)[0] == want, (st, want, NR.robots_verdict(st, body))
    assert NR.robots_verdict(200, b'<html>hi</html>', looks_like_page=True)[0] == 'no-rules'
    assert NR.robots_verdict(200, b'<html>hi</html>', redirected_off_site=True, looks_like_page=True)[0] == 'no-rules'
    for st, want in ((401, 'skip-page'), (403, 'skip-page'), (429, 'stop-site'), (503, 'busy'), (404, 'dead'), (200, 'read')):
        assert NR.page_verdict(st)[0] == want, st
    assert NR.is_block('disallow') and not any(NR.is_block(c) for c, _ in NR.REASONS if c != 'disallow')


@test
def a_robots_answers_that_are_not_a_no():
    for name, ans in [('403', (403, '', {})), ('401', (401, '', {})), ('web page', (200, '<html><body>Welcome</body></html>', {})),
                      ('sign-in page', (200, '<html><form action="/login"><input type="password"></form></html>', {})),
                      ('empty', (200, '', {})), ('redirected', (200, '<html>x</html>', {'X-Final-Url': 'https://other.example/robots.txt'})),
                      ('NUL byte', (200, 'User-agent: *\nDisallow: /a\x00b\n', {})),
                      ('600 KB', (200, 'User-agent: *\nDisallow: /private\n' + '#' * 600_000, {}))]:
        w = web({'https://s.example/robots.txt': ans, 'https://s.example/parks/one': (200, PAGE, {'Content-Type': 'text/html'})})
        st = ua_manners().get('https://s.example/parks/one')[0]
        assert st == 200, (name, st)
        assert w.asked('/parks/one'), name


@test
def a_real_disallow_is_the_only_no_and_its_line_is_kept():
    web({'https://s.example/robots.txt': ROBOTS_OK, 'https://s.example/private/p': (200, PAGE, {})})
    M = ua_manners()
    assert M.get('https://s.example/private/p')[0] == 'robots'
    assert 'Disallow: /private' in M.disallow_line('https://s.example/private/p')
    w = web({'https://s.example/robots.txt': (200, 'User-agent: *\nAllow: /p\nDisallow: /p\n', {}), 'https://s.example/p/1': (200, PAGE, {})})
    assert ua_manners().get('https://s.example/p/1')[0] == 200, 'a tie: Allow wins (RFC 9309)'


@test
def a_busy_robots_is_not_this_run_and_asked_next_run():
    for ans in [(503, '', {}), (429, '', {}), TimeoutError('timed out')]:
        w = web({'https://b.example/robots.txt': ans, 'https://b.example/x': (200, PAGE, {})})
        M = ua_manners()
        assert M.get('https://b.example/x')[0] == 'robots-unreadable'
        assert M.get('https://b.example/y')[0] == 'robots-unreadable'
        assert not w.asked('/x') and len(w.asked('robots.txt')) == 1, 'robots.txt once per host per run, no page asked'
        M2 = ua_manners()                       # the next run
        M2.get('https://b.example/x')
        assert len(w.asked('robots.txt')) == 2, 'asked again next run'


@test
def a_page_401_403_is_that_page_only_and_the_site_carries_on():
    """Owner 27 Nov 4:15 AM ("sure we are just polite"): a 401 / 403 is that page only. No retry, the next page is asked."""
    for code in (401, 403):
        w = web({'https://p.example/robots.txt': ROBOTS_OK, 'https://p.example/a': (code, '', {}), 'https://p.example/b': (200, PAGE, {})})
        M = ua_manners()
        assert M.get('https://p.example/a')[0] == code
        assert len(w.asked('/a')) == 1, f'{code}: no retry of the refused page'
        assert M.get('https://p.example/b')[0] == 200 and len(w.asked('/b')) == 1, f'{code}: the site carries on'
        assert M.stopped == {} and M.resting() == {}, 'nothing stopped, nothing saved for the next run'


@test
def a_five_refused_pages_in_a_row_stop_the_site_this_run_only():
    assert NR.REFUSALS_IN_A_ROW == 5
    pages = {'https://q.example/robots.txt': ROBOTS_OK, 'https://q.example/ok': (200, PAGE, {})}
    pages.update({f'https://q.example/n{i}': (403, '', {}) for i in range(8)})
    w = web(pages)
    M = ua_manners()
    for i in range(4):
        assert M.get(f'https://q.example/n{i}')[0] == 403
    assert M.get('https://q.example/ok')[0] == 200, 'four in a row: still asked'
    for i in range(4):
        assert M.get(f'https://q.example/n{i}')[0] == 403, 'a page that read set the count back to 0'
    assert 'q.example' not in M.stopped
    assert M.get('https://q.example/n4')[0] == 403 and 'q.example' in M.stopped, 'the fifth in a row stops the site'
    n = len(w.asked('/'))
    assert M.get('https://q.example/n5')[0] == 'stopped' and M.get('https://q.example/ok')[0] == 'stopped' and len(w.asked('/')) == n, \
        'no more requests to it this run'
    assert M.resting() == {}, 'nothing saved for the next run'
    assert ua_manners().get('https://q.example/ok')[0] == 200, 'the next run asks again'


@test
def a_page_429_stops_the_site_this_run_only():
    w = web({'https://p.example/robots.txt': ROBOTS_OK, 'https://p.example/a': (429, '', {}), 'https://p.example/b': (200, PAGE, {})})
    M = ua_manners()
    assert M.get('https://p.example/a')[0] == 429 and len(w.asked('/a')) == 1, 'no retry'
    assert M.get('https://p.example/b')[0] == 'stopped' and not w.asked('/b'), '429 = the site says slow down: stopped for this run'
    assert M.resting() == {} and ua_manners().get('https://p.example/b')[0] == 200, 'the next run asks again'


@test
def a_walls_in_a_row_count_even_though_each_answers_200():
    M = ua_manners()
    web({'https://w.example/robots.txt': ROBOTS_OK, 'https://w.example/a': (200, PAGE, {})})
    for i in range(4):
        assert M.get('https://w.example/a')[0] == 200
        assert M.refuse_host('w.example', 'wall', wall=True) is False
    assert M.refused_row['w.example'] == 4
    M.get('https://w.example/a')
    assert M.refuse_host('w.example', 'wall', wall=True) is True and 'w.example' in M.stopped, 'five walls in a row stop the site'
    M2 = ua_manners()
    M2.get('https://w.example/a'); M2.refuse_host('w.example', 'wall', wall=True); M2.get('https://w.example/a')
    M2.get('https://w.example/a')
    assert M2.refuse_host('w.example', 'wall', wall=True) is False and M2.refused_row['w.example'] == 1, 'a real page between ends the run of walls'
    assert M2.refuse_host('w.example', 'HTTP 403') is False and M2.refused_row['w.example'] == 1, 'a page get() already counted is not counted twice'


@test
def a_old_saved_rests_are_ignored():
    web({'https://r.example/robots.txt': ROBOTS_OK, 'https://r.example/a': (200, PAGE, {})})
    M = KM.Manners('t', {'r.example': time.time() + 86400})
    assert M.get('https://r.example/a')[0] == 200


@test
def a_crawl_delay_waits_for_the_slow_pass_never_skipped():
    robots = (200, 'User-agent: *\nCrawl-delay: 1000\n', {})
    w = web({'https://slow.example/robots.txt': robots, 'https://slow.example/a': (200, PAGE, {}), 'https://slow.example/b': (200, PAGE, {})})
    assert ua_manners().get('https://slow.example/a')[0] == 'crawl-delay' and not w.asked('/a')
    assert NR.reason_of('crawl-delay', 'resting') == 'slow' and not NR.is_block('slow')
    KM.MAX_CRAWL_DELAY = float('inf')            # what KPC_SLOW_PASS=1 sets
    KM.SLOW_BUDGET = 5000
    try:
        M = ua_manners()
        assert M.get('https://slow.example/a')[0] == 200
        assert M.get('https://slow.example/b')[0] == 200
        assert max(w.sleeps) >= 999, f'the 1000 s delay is obeyed in full (slept {max(w.sleeps)})'
    finally:
        KM.MAX_CRAWL_DELAY, KM.SLOW_BUDGET = 120, 10


@test
def a_redirect_to_another_host_obeys_that_hosts_robots():
    import urllib.request
    web({'https://two.example/robots.txt': (200, 'User-agent: *\nDisallow: /\n', {})})
    M = ua_manners()
    KM._HOP.manners = M
    req = urllib.request.Request('https://one.example/x')
    try:
        urllib.request.HTTPRedirectHandler().redirect_request(req, None, 302, 'Found', {}, 'https://two.example/y')
        raise AssertionError('the hop should be refused')
    except KM.RobotsHopRefused as e:
        assert e.status == 'robots' and 'Disallow: /' in e.why
    finally:
        KM._HOP.manners = None


@test
def a_bare_host_try_keeps_only_a_real_page():
    w = web({'https://www.dec.example/robots.txt': TimeoutError('x'), 'https://dec.example/robots.txt': (404, '', {}),
             'https://dec.example/lands/a': (404, '', {})})
    assert ua_manners().get('https://www.dec.example/lands/a')[0] == 'robots-unreadable', 'a 404 on the bare host is not saved as dead'
    w = web({'https://www.dec.example/robots.txt': TimeoutError('x'), 'https://dec.example/robots.txt': (404, '', {}),
             'https://dec.example/lands/a': (200, PAGE, {})})
    assert ua_manners().get('https://www.dec.example/lands/a')[0] == 200


@test
def a_docs_bot_robots_uses_the_same_table():
    import kpc_docs_bot as D
    for ans, want in [((200, '<html>page</html>', {}), None), ((200, 'User-agent: *\nDisallow: /x\n' + '#' * 600_000, {}), 'rules'),
                      ((503, '', {}), False), ((403, '', {}), None)]:
        web({'https://d.example/robots.txt': ans})
        D.ROBOTS.clear()
        D._load_docs_robots('https://d.example/a', 'https://d.example')
        got = D.ROBOTS['https://d.example']
        assert (got is None and want is None) or (got is False and want is False) or (want == 'rules' and got and not KM.robots_allowed(got, D.UA, 'https://d.example/x/1')), (ans[0], got)


def make_area(t, parks):
    (t / 'parkinfo').mkdir(parents=True, exist_ok=True)
    (t / 'parkinfo' / 'US-ZZ.json').write_text(json.dumps({'parks': {ref: [name, url, kind, '', '', 40.0, -80.0, 0, 0, 1]
                                                                      for ref, (name, url, kind) in parks.items()}}))
    return P.load_data(t)


@test
def a_the_one_test_only_disallow_lines_are_saved_as_blocked():
    """After a run over sites answering every way, the only pages recorded as blocked carry their Disallow line."""
    pages = {'https://ok.example/robots.txt': ROBOTS_OK, 'https://ok.example/parks/a': (200, PAGE, {}),
             'https://ok.example/private/b': (200, PAGE, {}),
             'https://f.example/robots.txt': (403, '', {}), 'https://f.example/c': (403, '', {}), 'https://f.example/d': (200, PAGE, {}),
             'https://busy.example/robots.txt': (503, '', {}), 'https://busy.example/e': (200, PAGE, {}),
             'https://web.example/robots.txt': (200, '<html><body>a page</body></html>', {}), 'https://web.example/f': (200, PAGE, {}),
             'https://slow.example/robots.txt': (200, 'User-agent: *\nCrawl-delay: 600\n', {}), 'https://slow.example/g': (200, PAGE, {}),
             'https://lim.example/robots.txt': ROBOTS_OK, 'https://lim.example/h': (429, '', {})}
    web(pages)
    parks = {f'US-{9000 + i}': (f'Rib Mountain {c} State Park', u, 'State Park') for i, (c, u) in enumerate(
        [('A', 'https://ok.example/parks/a'), ('B', 'https://ok.example/private/b'), ('C', 'https://f.example/c'),
         ('D', 'https://f.example/d'), ('E', 'https://busy.example/e'), ('F', 'https://web.example/f'), ('G', 'https://slow.example/g'),
         ('H', 'https://lim.example/h')])}
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t, parks)
        state = {}
        facts, _ = P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-26', refs=sorted(parks), quiet=True,
                                out_dir=str(t / 'out'))
        assert P.write_disallow_list(t / 'out') == 1
        rows = (t / 'out' / 'robots-disallow-hand-look.csv').read_text().splitlines()
        assert len(rows) == 2 and 'US-9001' in rows[1] and 'Disallow: /private' in rows[1]
        blocked = {r: f for r, f in facts['US-ZZ'].items() if (f.get('page') or {}).get('kind') == 'refused'}
        assert set(blocked) == {'US-9001'}, sorted(blocked)
        assert 'Disallow: /private' in blocked['US-9001']['page']['not_read']['line']
        reasons = {r: (f['page'].get('not_read') or {}).get('reason', 'read') for r, f in facts['US-ZZ'].items()}
        # US-9003 shares a site with US-9002, whose page answered 403: since 27 Nov that is one page, and the site carries on
        assert reasons == {'US-9000': 'read', 'US-9001': 'disallow', 'US-9002': 'stopped', 'US-9003': 'read', 'US-9004': 'busy',
                           'US-9005': 'read', 'US-9006': 'slow', 'US-9007': 'stopped'}, reasons
        assert state['hosts'] == {} and state['refused'] == {}, 'nothing carried into the next run'


class BrowserGetter(P.LiveGetter):
    """The live getter with a stand-in page browser (no Playwright): returns `built` for every address it is asked."""
    def __init__(self, state, built):
        super().__init__(state)
        self.built, self.browser_calls = built, []

    def browser_html(self, url):
        self.browser_calls.append(url)
        if self.M.dead.get(self.M.host(url), 0) > time.time():   # the page browser keeps the same manners
            return ''
        return self.built


def _p2_run(code, built):
    pages = {'https://p2.example/robots.txt': ROBOTS_OK, 'https://p2.example/a': (code, '', {}), 'https://p2.example/b': (200, PAGE, {})}
    w = web(pages)
    os.environ['BROWSER'] = '1'
    try:
        with tempfile.TemporaryDirectory() as td:
            areas, wb, docs, truth = make_area(pathlib.Path(td), {'US-1': ('Rib Mountain State Park', 'https://p2.example/a', 'State Park'),
                                                                   'US-2': ('Rib Mountain State Park', 'https://p2.example/b', 'State Park')})
            state = {}
            g = BrowserGetter(state, built)
            facts, _ = P.read_parks(areas, wb, docs, truth, g, state, '2026-11-26', refs=['US-1', 'US-2'], quiet=True)
    finally:
        os.environ.pop('BROWSER', None)
    return w, g, facts['US-ZZ']


@test
def a_p2_one_browser_try_after_401_403_then_the_site_carries_on():
    for code in (401, 403):
        w, g, f = _p2_run(code, PAGE)
        assert g.browser_calls == ['https://p2.example/a'] and f['US-1']['page']['kind'] == 'html', (code, 'P-2: the browser got the page')
        assert len(w.asked('/a')) == 1 and f['US-2']['page']['kind'] == 'html', (code, 'the site is not stopped when the browser got it')
        w, g, f = _p2_run(code, '')
        assert g.browser_calls == ['https://p2.example/a'], (code, 'exactly one browser try')
        assert f['US-1']['page']['not_read']['reason'] == 'stopped' and f['US-2']['page']['kind'] == 'html' and len(w.asked('/b')) == 1, \
            (code, 'the browser failed too: that page waits for the next run, the site carries on (27 Nov)')
        assert g.M.refused_row.get('p2.example', 0) == 0 and g.M._row_before.get('p2.example') == 1, (code, 'the refused page was counted once')
    w, g, f = _p2_run(429, PAGE)
    assert g.browser_calls == [] and f['US-2']['page']['status'] == 'stopped' and not w.asked('/b'), '429: no browser try, stopped at once'


@test
def a_site_that_did_not_answer_is_read_through_the_browser_first_next_time():
    """27 Nov (the other builder's fix, kept in the merge): a site that answers the plain reader with a server error goes on
    the browser list; a site on that list is read through the page browser first, and the plain reader is not asked."""
    pages = {'https://bh.example/robots.txt': ROBOTS_OK, 'https://bh.example/a': (503, '', {}), 'https://bh.example/b': (200, PAGE, {})}
    os.environ['BROWSER'] = '1'
    try:
        with tempfile.TemporaryDirectory() as td:
            areas, wb, docs, truth = make_area(pathlib.Path(td), {'US-1': ('Rib Mountain State Park', 'https://bh.example/a', 'State Park')})
            w = web(pages)
            state = {'browser_hosts': {}}
            g = BrowserGetter(state, PAGE)
            P.read_parks(areas, wb, docs, truth, g, state, '2026-11-27', refs=['US-1'], quiet=True)
            assert 'bh.example' in state['browser_hosts'], 'a 503 puts the site on the browser list'
            w = web(pages)
            g = BrowserGetter(state, PAGE)
            facts, _ = P.read_parks(areas, wb, docs, truth, g, state, '2026-11-28', refs=['US-1'], quiet=True)
            assert g.browser_calls == ['https://bh.example/a'] and not w.asked('/a'), 'next run: the browser first, the plain reader not asked'
            assert facts['US-ZZ']['US-1']['page']['kind'] == 'html'
    finally:
        os.environ.pop('BROWSER', None)


@test
def a_decisions_are_one_value_each():
    src = open(os.path.join(HERE, 'kpc_net_rule.py'), encoding='utf-8').read()
    assert src.count("'robots_challenge_page': 'no-rules'") == 1 and src.count("'robots_other_site_page': 'no-rules'") == 1
    assert src.count("'wall_max_chars': 3000") == 1 and src.count("'refusals_in_a_row': 5") == 1
    import importlib.util
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / 'nr_flipped.py'
        f.write_text(src.replace("'robots_challenge_page': 'no-rules'", "'robots_challenge_page': 'busy'"), encoding='utf-8')
        spec = importlib.util.spec_from_file_location('nr_flipped', f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert m.robots_verdict(200, b'<html>x</html>', looks_like_page=True, challenge=True)[0] == 'busy', 'flipping the one value flips the verdict'
    assert m.robots_verdict(200, b'<html>x</html>', looks_like_page=True)[0] == 'no-rules', 'a plain web page is untouched'
    web({'https://c.example/robots.txt': (200, '<html><body>Please verify you are human</body></html>', {})})
    M = ua_manners()
    M.robots_ok('https://c.example/x')
    assert M.robots_note['c.example'][0] == 'challenge'
    long_wall = '<html><body>' + 'captcha mentioned in a long real page. ' * 200 + '</body></html>'
    assert P._kind_of_status(200, R.visible_of(long_wall.encode(), {}, 'https://x/p')['text'], 'https://x/p') == 'html'
    assert P._kind_of_status(200, 'Just a moment... captcha', 'https://x/p') == 'resting'


@test
def g_kept_pages_list_survives_a_killed_run():
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td) / 'kept'
        k = P.PageKeeper(root, '2026-11-26')
        for i in range(3):
            k.keep(f'https://a/p{i}', f'https://a/p{i}', 200, {}, PAGE.encode(), kind='html')
        # the run is killed here: save() never runs
        with open(root / 'manifest.journal', 'a', encoding='utf-8') as fh:
            fh.write('{"url": "https://a/p9", "rec": {"fi')      # a line cut off mid-write
        k2 = P.PageKeeper(root, '2026-11-27')
        assert sorted(k2.man['pages']) == ['https://a/p0', 'https://a/p1', 'https://a/p2']
        assert sorted(P.kept_manifest(root / 'manifest.json')['pages']) == sorted(k2.man['pages']), 'the re-read sees them too'
        k2.keep('https://a/p3', 'https://a/p3', 200, {}, PAGE.encode(), kind='html')
        k2.save()
        assert not (root / 'manifest.journal').exists() and len(json.loads((root / 'manifest.json').read_text())['pages']) == 4
    # and a re-read of the kept pages after the killed run asks no website at all
    w = web({})
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        url = 'https://dnr.example.gov/parks/rib'
        make_area(t / 'data', {'US-1': ('Rib Mountain State Park', url, 'State Park')})
        k = P.PageKeeper(t / 'pages-kept', '2026-11-26')
        k.keep(url, url, 200, {'content-type': 'text/html'}, PAGE.encode(), kind='html')     # killed: no save()
        P.main(['read', '--data', str(t / 'data'), '--out', str(t / 'out'), '--reextract', '--quiet', '--status-file', str(t / 'S.txt')])
        assert w.calls == [] and json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']['US-1']['name']['best'] == 'Rib Mountain State Park'


# ------------------------------------------------------------------------------------------------------- B: names
@test
def b_junk_table_every_row():
    for row in R.JUNK['patterns']:
        for c in row['catch']:
            assert R.junk_why(c), ('not caught', c)
        for k in row['keep']:
            assert not R.junk_why(k), ('wrongly caught', k)
    for c in ['STATE WILDLIFE MANAGEMENT AREA', 'Conservation Areas', 'Provincial Park Reserves', 'National Wildlife Refuge',
              'Wildlife Habitat Management Areas | Wyoming Game & Fish Department', 'State Forest']:
        assert R.junk_why(c), c
    for k in ['Rib Mountain State Park', 'Alaksen National Wildlife Area', 'Allagash Wilderness Waterway', 'Taj Mahal']:
        assert not R.junk_why(k), k


def facts_for(html, name, ptype='State Park', area_parks=None, url='https://dnr.example.gov/parks/x'):
    pg = {'kind': 'html', 'status': 200, 'final': url, 'url': url}
    vis = R.visible_of(html.encode(), {'content-type': 'text/html'}, url)
    pg.update(vis)
    return R.build_facts('US-1', 'US-ZZ', {'name': name, 'type': ptype, 'pin': [40, -80]}, area_parks or {'US-1': {'name': name}},
                         {'url': url}, [pg], '2026-11-26', [], 'own', 'own page')


@test
def b_headings_that_are_not_names_are_set_aside():
    html = ('<html><head><title>Morning Glory Farm - Historic Places</title></head><body><h2>Other Name(s)</h2>'
            + '<p>text</p>' * 120 + '</body></html>')
    f = facts_for(html, 'Morning Glory National Historic Site')
    assert f['name']['heading'] != 'Other Name(s)' and f['name']['best'] != 'Other Name(s)', f['name']
    assert any(x['name'] == 'Other Name(s)' for x in f['name'].get('set_aside') or [])
    html = '<html><head><title>Main navigation</title></head><body><h1>Main navigation</h1>' + '<p>t</p>' * 120 + '</body></html>'
    f = facts_for(html, 'Rib Mountain State Park')
    assert not f['name']['best'] and not f['name']['heading'] and 'TITLE_NOT_A_NAME' in {q['code'] for q in f['questions']}
    f = facts_for(PAGE, 'Rib Mountain State Park')
    assert f['name']['best'] == 'Rib Mountain State Park' and not f['name'].get('set_aside')
    offered = {x['from']: x for x in f['name']['offered']}
    assert offered['title']['name'].startswith('Rib Mountain') and offered['h1']['set_aside'] == ''


@test
def b_a_neighbours_name_is_never_this_parks_name():
    html = '<html><head><title>Duclos Point Provincial Park</title></head><body><h1>Duclos Point Provincial Park</h1>' + '<p>t</p>' * 120 + '</body></html>'
    f = facts_for(html, 'Morning Glory Provincial Park', 'Provincial Park',
                  {'US-1': {'name': 'Morning Glory Provincial Park'}, 'US-2': {'name': 'Duclos Point Provincial Park'}})
    assert not f['name']['best'] and any('another park' in x['why'] for x in f['name']['set_aside'])


@test
def b_a_name_shared_by_many_parks_of_one_site_is_set_aside():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        parks = {}
        for i in range(4):
            parks[f'US-{i}'] = {'ref': f'US-{i}', 'pota': {'name': f'Park {i} Wildlife Area'}, 'page': {'host': 'myfwp.example', 'kind': 'html'},
                                'name': {'heading': 'Montana Outdoors Hub', 'title': '', 'best': 'Montana Outdoors Hub', 'vs_pota': 'differs'}}
        parks['US-9'] = {'ref': 'US-9', 'pota': {'name': 'Montana Outdoors Hub'}, 'page': {'host': 'myfwp.example', 'kind': 'html'},
                         'name': {'heading': 'Montana Outdoors Hub', 'title': '', 'best': 'Montana Outdoors Hub', 'vs_pota': 'same'}}
        P.save_json(out / 'facts' / 'US-ZZ.json', {'area': 'US-ZZ', 'parks': parks})
        assert P.set_aside_shared_names(out) == 4
        assert P.set_aside_shared_names(out) == 0, 'idempotent'
        got = json.loads((out / 'facts' / 'US-ZZ.json').read_text())['parks']
        assert not got['US-0']['name']['best'] and got['US-0']['name']['set_aside'][0]['rule'] == 'shared'
        assert got['US-9']['name']['best'] == 'Montana Outdoors Hub', "the park whose own name it is keeps it"


# ------------------------------------------------------------------------------------------------------- C: sizes
@test
def c_two_totals_that_disagree_are_not_clean():
    html = ('<html><head><title>Big Creek Park</title></head><body><h1>Big Creek Park</h1><p>Big Creek Park covers 608 hectares.</p>'
            '<p>Big Creek Park protects 162 hectares of land.</p>' + '<p>t</p>' * 120 + '</body></html>')
    rows = R.check_sizes([{'acres': 1502.4, 'as': '608 ha', 'total': True, 'clean': True}, {'acres': 400.3, 'as': '162 ha', 'total': True, 'clean': True}])
    assert not any(r['clean'] for r in rows) and all(r['disagrees_with'] for r in rows)
    rows = R.check_sizes([{'acres': 862.4, 'as': '349 ha', 'total': True, 'clean': True}, {'acres': 862.0, 'as': '862 acres', 'total': True, 'clean': True}])
    assert all(r['clean'] for r in rows), 'the same size in two units agrees'
    f = facts_for(html, 'Big Creek Park', 'Park')
    if len([s for s in f['sizes'] if s.get('total')]) >= 2 and any(s.get('disagrees_with') for s in f['sizes']):
        assert 'SIZES_DISAGREE' in {q['code'] for q in f['questions']}


@test
def c_number_and_unit_as_written_and_the_french_comma():
    r = R.size_detail({'acres': 3049.3, 'as': '1,234 ha'}, 'Le parc couvre 1,234 ha de forêt.', 'fr')
    assert r['number'] == '1,234' and r['unit'] == 'hectares' and r['written'].startswith('1,234')
    assert r.get('ambiguous') and r['clean'] is False, 'a French page: 1,234 can be 1.234'
    r = R.size_detail({'acres': 3049.3, 'as': '1,234 ha', 'clean': True}, 'The park covers 1,234 ha.', 'en')
    assert not r.get('ambiguous') and r['clean'] is True
    r = R.size_detail({'acres': 58171.5, 'as': '23,540 hectares'}, 'Le parc couvre 23 540 hectares.', 'fr')
    assert r['written'] == '23 540 hectares', r['written']
    assert R.page_language('<html lang="fr-CA">', '') == 'fr' and R.page_language('', 'https://x.ca/fr/parc') == 'fr'


# ------------------------------------------------------------------------- D: re-read the kept pages, nothing downloaded
@test
def d_reread_kept_pages_fixes_names_with_no_web():
    w = web({})
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        url = 'https://dnr.example.gov/parks/rib'
        areas, wb, docs, truth = make_area(t / 'data', {'US-1': ('Rib Mountain State Park', url, 'State Park')})
        keeper = P.PageKeeper(t / 'pages-kept', '2026-11-20')
        junk = '<html><head><title>Main navigation</title></head><body><h2>Main navigation</h2><h1>Rib Mountain State Park</h1>' + '<p>words on the page</p>' * 120 + '</body></html>'
        keeper.keep(url, url, 200, {'content-type': 'text/html'}, junk.encode(), kind='html')
        keeper.save()
        rc = P.main(['read', '--data', str(t / 'data'), '--out', str(t / 'out'), '--reextract', '--quiet', '--status-file', str(t / 'S.txt')])
        assert rc == 0 and w.calls == [], 'nothing asked of any site'
        f = json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']['US-1']
        assert f['name']['best'] == 'Rib Mountain State Park', f['name']
        assert (t / 'S.txt').is_file()


# --------------------------------------------------------------------------------------------------- E: status page
@test
def e_status_page_one_screen_fixed_reasons():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / 'out'
        parks = {
            'US-1': {'page': {'kind': 'html', 'status': 200, 'host': 'a.gov'}, 'name': {'best': 'X Park'}, 'sizes': [{'total': True, 'clean': True}]},
            'US-2': {'page': {'kind': 'refused', 'status': 'robots', 'host': 'pa.gov', 'not_read': {'reason': 'disallow', 'line': 'User-agent: * | Disallow: /'}}},
            'US-3': {'page': {'kind': 'resting', 'status': 'rest', 'host': 'blm.gov'}},
            'US-4': {'page': {'kind': 'resting', 'status': 403, 'host': 'nh.gov'}},
            'US-5': {'page': {'kind': 'resting', 'status': 'crawl-delay', 'host': 'parks.ny.gov'}},
            'US-6': {'page': {'kind': 'none', 'status': None}, 'own_page': {'is': ''}},
            'US-7': {'page': {'kind': 'dead', 'status': 404, 'host': 'x.gov'}},
            'US-8': {'page': {'kind': 'html', 'status': 200, 'host': 'a.gov'}, 'name': {'best': None, 'set_aside': [{'name': 'Main navigation'}]}},
        }
        P.save_json(out / 'facts' / 'US-ZZ.json', {'area': 'US-ZZ', 'parks': parks})
        P.save_json(out / 'facts' / 'CA-BC.json', {'area': 'CA-BC', 'parks': {'CA-1': {'page': {'kind': 'pdf', 'status': 200}, 'name': {'best': 'Y'}}}})
        text = ST.render(out, kept_pages=500)
        lines = text.splitlines()
        assert len(lines) <= 40, len(lines)
        assert 'Parks with their page read: 3 of 9' in text
        for code, words in NR.REASONS[:7]:
            assert words in text, words
        assert '1 had only a heading, menu or site name, set aside' in text
        assert 'choice 2' in text and 'choice 3' in text
        assert text.index('choice 2') < text.index('choice 3'), 're-reading the kept pages comes first'


# -------------------------------------------------------------------------------------------------- G: saving correctly
@test
def g_a_failed_read_never_overwrites_good_facts():
    w = web({'https://ok.example/robots.txt': ROBOTS_OK, 'https://ok.example/p': (200, PAGE, {})})
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t / 'data', {'US-1': ('Rib Mountain State Park', 'https://ok.example/p', 'State Park')})
        state = {}
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-20', refs=['US-1'], out_dir=str(t / 'out'), quiet=True)
        good = json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']['US-1']
        assert good['name']['best'] == 'Rib Mountain State Park'
        for bad in [(403, '', {}), (503, '', {}), (404, '', {}), (200, '<html><body>Just a moment... captcha</body></html>', {})]:
            w.pages['https://ok.example/p'] = bad
            state['read']['US-1']['date'] = '2025-01-01'      # make it due
            P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-26', refs=['US-1'], out_dir=str(t / 'out'),
                         quiet=True, refresh_days=30)
            now = json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']['US-1']
            assert now['name']['best'] == 'Rib Mountain State Park', (bad[0], now.get('name'))
            assert now['page']['kind'] == 'html' and now['page']['last_try']['date'] == '2026-11-26', bad[0]


@test
def g_save_reads_back_and_keeps_the_old_file_on_a_bad_write():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / 'f.json'
        P.save_json(p, {'parks': {'A': 1}})
        real = pathlib.Path.read_text
        def broken(self, *a, **k):
            return '{"parks": {}}' if self.name.endswith('.tmp') else real(self, *a, **k)
        pathlib.Path.read_text = broken
        try:
            try:
                P.save_json(p, {'parks': {'A': 1, 'B': 2}})
                raise AssertionError('a bad write must be refused')
            except P.SaveFailed:
                pass
        finally:
            pathlib.Path.read_text = real
        assert json.loads(p.read_text()) == {'parks': {'A': 1}}


@test
def g_an_unreadable_facts_file_is_copied_aside_not_wiped():
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td)
        f = out / 'facts' / 'US-ZZ.json'
        f.parent.mkdir(parents=True)
        f.write_text('{"parks": {"US-1": {"ref": "US-1"}, ')      # cut off
        P.write_facts(out, {'US-ZZ': {'US-2': {'ref': 'US-2'}}})
        aside = list(f.parent.glob('US-ZZ.json.unreadable-*'))
        assert aside and aside[0].read_text().startswith('{"parks": {"US-1"')


@test
def g_keeper_never_replaces_a_good_copy_with_a_wall_and_writes_whole():
    with tempfile.TemporaryDirectory() as td:
        k = P.PageKeeper(pathlib.Path(td) / 'kept', '2026-11-26')
        k.keep('https://a/p', 'https://a/p', 200, {}, PAGE.encode(), kind='html')
        k.keep('https://a/p', 'https://a/p', 200, {}, b'<html>Just a moment</html>', kind='resting')
        assert gzip.decompress((k.root / k.man['pages']['https://a/p']['file']).read_bytes()) == PAGE.encode()
        assert not list(k.root.rglob('*.tmp'))


@test
def g_a_run_stopped_half_way_loses_nothing_and_carries_on():
    pages = {'https://ok.example/robots.txt': ROBOTS_OK}
    parks = {}
    for i in range(6):
        u = f'https://ok.example/p{i}'
        pages[u] = (200, PAGE.replace('Rib Mountain', f'Rib Mountain {i}'), {})
        parks[f'US-{i}'] = (f'Rib Mountain {i} State Park', u, 'State Park')
    w = web(pages)
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t / 'data', parks)
        state = {}
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-26', refs=sorted(parks), out_dir=str(t / 'out'),
                     quiet=True, max_requests=3)
        saved = json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']
        assert len(saved) == 3 and state['stopped'] == 'requests' and len(state['left']) == 3
        n = len(w.asked('/p'))
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-26', refs=sorted(parks), out_dir=str(t / 'out'), quiet=True)
        saved = json.loads((t / 'out' / 'facts' / 'US-ZZ.json').read_text())['parks']
        assert len(saved) == 6 and len(w.asked('/p')) - n == 3, 'only the three left are asked'


@test
def g_upload_pack_is_checked_before_it_gets_its_name():
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(HERE, 'pc'))   # the same file in KPC-Data (.github/scripts/pc)
    import kpc_upload_pack as U
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        (t / 'facts').mkdir()
        (t / 'pi').mkdir()
        (t / 'facts' / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'parks': {'US-1': {'ref': 'US-1'}}}))
        (t / 'pi' / 'US-ZZ.json').write_text(json.dumps({'parks': {'US-1': []}}))
        zp, counts, why = U.make_pack(t / 'send', t / 'facts', None, None, None, None, parkinfo=t / 'pi')
        assert zp and zp.is_file() and not list((t / 'send').glob('*.part'))


# ---------------------------------------------------------------------------------------------------- H: doing less
@test
def h_one_robots_read_per_host_and_one_request_per_shared_page():
    pages = {'https://ok.example/robots.txt': ROBOTS_OK, 'https://ok.example/list': (200, PAGE, {})}
    parks = {f'US-{i}': (f'Rib Mountain State Park', 'https://ok.example/list', 'State Park') for i in range(5)}
    w = web(pages)
    with tempfile.TemporaryDirectory() as td:
        areas, wb, docs, truth = make_area(pathlib.Path(td), parks)
        state = {}
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-26', refs=sorted(parks), quiet=True)
    assert len(w.asked('robots.txt')) == 1 and len(w.asked('/list')) == 1, (w.asked('robots.txt'), w.asked('/list'))


@test
def h_a_page_already_read_is_not_read_again_unless_asked():
    w = web({'https://ok.example/robots.txt': ROBOTS_OK, 'https://ok.example/p': (200, PAGE, {'ETag': '"v1"'})})
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t, {'US-1': ('Rib Mountain State Park', 'https://ok.example/p', 'State Park')})
        state = {}
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-01', refs=['US-1'], quiet=True, out_dir=str(t / 'out'))
        n = len(w.asked('/p'))
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2027-03-01', refs=['US-1'], quiet=True, out_dir=str(t / 'out'),
                     refresh_days=P.NEVER_DAYS)
        assert len(w.asked('/p')) == n, 'months later, no new request (the default)'
        assert state['read']['US-1'].get('validators', {}).get('etag') == '"v1"'


# ------------------------------------------------------------------------- I: never silent, never stuck (27 Nov 2026)
class FakeClock:
    """A made-up clock: time.time() is a number, and time.sleep() moves it on at once (nothing really waits)."""
    def __init__(self, t=1_800_000_000.0):
        self.t, self.sleeps = t, []

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += max(0.0, s)

    def __enter__(self):
        self._old = (time.time, time.sleep)
        time.time, time.sleep = (lambda: self.t), self.sleep
        return self

    def __exit__(self, *a):
        time.time, time.sleep = self._old


@test
def i_a_robots_txt_that_redirects_to_another_site_never_hangs():
    """The owner's PC, 27 Nov: a robots.txt that redirected to another host waited forever on the robots lock."""
    import threading, urllib.request

    def robots_moved(req):
        # what urllib does with a 301 for robots.txt: it asks the redirect check before following
        urllib.request.HTTPRedirectHandler().redirect_request(req, None, 301, 'Moved', {}, 'https://www.moved.example/robots.txt')
        return ROBOTS_OK
    web({'https://moved.example/robots.txt': robots_moved, 'https://moved.example/a': (200, PAGE, {})})
    M = ua_manners()
    got = []
    t = threading.Thread(target=lambda: got.append(M.get('https://moved.example/a')), daemon=True)
    t.start()
    t.join(5)
    assert not t.is_alive(), 'the read is stuck (the robots lock waits on itself)'
    assert got[0][0] == 200 and KM._HOP.manners is None
    # a robots.txt read in the middle of a page's redirect puts the page's own hop check back afterwards
    web({'https://two.example/robots.txt': ROBOTS_OK})
    KM._HOP.manners = M
    try:
        urllib.request.HTTPRedirectHandler().redirect_request(urllib.request.Request('https://one.example/x'), None, 302, 'Found', {},
                                                             'https://two.example/y')
        assert KM._HOP.manners is M, 'the hop check is still on for the later hops'
    finally:
        KM._HOP.manners = None


@test
def i_a_long_wait_says_what_it_waits_for_first():
    said = []
    web({'https://cd.example/robots.txt': (200, 'User-agent: *\nCrawl-delay: 100\n', {}),
         'https://cd.example/a': (200, PAGE, {}), 'https://cd.example/b': (200, PAGE, {}),
         'https://busy.example/robots.txt': ROBOTS_OK, 'https://busy.example/c': (503, '', {'Retry-After': '60'})})
    with FakeClock() as c:
        M = ua_manners()
        M.say = said.append
        assert M.get('https://cd.example/a', max_time=90)[0] == 200
        assert M.get('https://busy.example/c', max_time=90)[0] == 503
    waits = [s for s in c.sleeps if s > KM.SAY_WAIT_OVER]
    assert waits and len(said) == len(waits), (said, c.sleeps)
    assert 'Waiting 2 min before asking cd.example again: the site asks for 100 s between requests.' in said[0], said
    assert any('Waiting 60 s before asking busy.example again: it answered 503 (busy) and asked us to wait.' in x for x in said), said
    assert not any(0 < s <= KM.SAY_WAIT_OVER for s in waits)


@test
def i_the_download_clock_starts_after_the_polite_wait():
    """Before 27 Nov the 90 s download cap ran during the Crawl-delay wait: a site asking 300 s was waited for, then never asked."""
    web({'https://slow.example/robots.txt': (200, 'User-agent: *\nCrawl-delay: 300\n', {}),
         'https://slow.example/a': (200, PAGE, {}), 'https://slow.example/b': (200, PAGE, {})})
    KM.MAX_CRAWL_DELAY, KM.SLOW_BUDGET = float('inf'), 5000   # what KPC_SLOW_PASS=1 sets
    try:
        with FakeClock() as c:
            M = ua_manners()
            assert M.get('https://slow.example/a', max_time=90)[0] == 200
            assert M.get('https://slow.example/b', max_time=90)[0] == 200
        assert sum(1 for s in c.sleeps if s >= 300) == 2, f'both 300 s waits obeyed in full ({c.sleeps})'
    finally:
        KM.MAX_CRAWL_DELAY, KM.SLOW_BUDGET = 120, 10


@test
def i_a_park_past_its_time_limit_is_noted_and_the_next_park_is_read():
    import contextlib, io
    clock = FakeClock()

    def stuck_page(req):
        clock.t += 400   # this one page takes 400 s
        return (200, PAGE, {})
    pages = {'https://hang.example/robots.txt': ROBOTS_OK, 'https://hang.example/a': stuck_page,
             'https://ok.example/robots.txt': ROBOTS_OK, 'https://ok.example/b': (200, PAGE, {})}
    parks = {'US-1': ('Rib Mountain State Park', 'https://hang.example/a', 'State Park'),
             'US-2': ('Rib Mountain State Park', 'https://ok.example/b', 'State Park')}
    w = web(pages)
    screen = io.StringIO()
    with tempfile.TemporaryDirectory() as td, clock, contextlib.redirect_stdout(screen):
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t / 'data', parks)
        state = {}
        facts, _ = P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-27', refs=['US-1', 'US-2'],
                                out_dir=str(t / 'out'))
        disallow = P.write_disallow_list(t / 'out')
    f1, f2 = facts['US-ZZ']['US-1'], facts['US-ZZ']['US-2']
    nr = f1['page'].get('not_read') or {}
    assert nr.get('reason') == 'busy' and 'not this run (took too long: hang.example)' in nr.get('why', ''), f1['page']
    assert 'Park US-1: not this run (took too long: hang.example). It is tried again next run.' in screen.getvalue()
    assert f2['page']['kind'] == 'html' and len(w.asked('/b')) == 1, 'the next park is read'
    assert state['read']['US-1']['kind'] == 'resting' and disallow == 0 and state['hosts'] == {}, 'never saved as blocked'
    assert NR.reason_of('took-too-long', 'resting') == 'busy' and not NR.is_block('busy')
    # the next run asks it again
    w = web(pages)
    with tempfile.TemporaryDirectory() as td, FakeClock():
        t = pathlib.Path(td)
        areas, wb, docs, truth = make_area(t / 'data', parks)
        P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-28', refs=['US-1'], quiet=True)
    assert len(w.asked('hang.example/a')) == 1, 'tried again next run'


@test
def i_a_crawl_delay_longer_than_the_park_limit_waits_for_the_slow_pass():
    import kpc_park_pages_slow as SL
    pages = {'https://cd.example/robots.txt': (200, 'User-agent: *\nCrawl-delay: 100\n', {}), 'https://cd.example/a': (200, PAGE, {})}
    parks = {'US-1': ('Rib Mountain State Park', 'https://cd.example/a', 'State Park')}
    old = P.PARK_MAX_SECONDS
    P.PARK_MAX_SECONDS = 60   # shorter than the site's 100 s
    try:
        with tempfile.TemporaryDirectory() as td:
            t = pathlib.Path(td)
            areas, wb, docs, truth = make_area(t / 'data', parks)
            state = {}
            w = web(pages)
            with FakeClock() as c:
                facts, _ = P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-27', refs=['US-1'], quiet=True,
                                        out_dir=str(t / 'out'))
            assert not w.asked('/a') and not [s for s in c.sleeps if s > 0], 'the site is not asked, and no wait was cut short'
            assert facts['US-ZZ']['US-1']['page']['not_read']['reason'] == 'slow'
            assert SL.waiting(str(t / 'out' / 'facts'))[0] == ['US-1'], 'on the slow pass list'
            KM.MAX_CRAWL_DELAY, KM.SLOW_BUDGET = float('inf'), 5000   # the slow pass (KPC_SLOW_PASS=1)
            w = FW.FakeWeb(pages).install(KM, P)
            with FakeClock() as c:
                facts, _ = P.read_parks(areas, wb, docs, truth, P.LiveGetter(state), state, '2026-11-27', refs=['US-1'], quiet=True,
                                        out_dir=str(t / 'out'))
            assert facts['US-ZZ']['US-1']['page']['kind'] == 'html' and len(w.asked('/a')) == 1
            assert any(abs(s - 100) < 1e-6 for s in c.sleeps), f'the 100 s delay obeyed in full ({c.sleeps})'
    finally:
        P.PARK_MAX_SECONDS = old
        KM.MAX_CRAWL_DELAY, KM.SLOW_BUDGET = 120, 10


@test
def i_a_long_read_says_still_on_about_once_a_minute():
    watch = {'host': 'www.fs.usda.gov', 'ref': 'US-3660', 'since': 1000.0, 'said': 0}
    lines = [P._still_line(watch, now) for now in (1030, 1065, 1070, 1125, 1190)]
    assert lines == [None, '    still on www.fs.usda.gov, 1 min (park US-3660)', None, '    still on www.fs.usda.gov, 2 min (park US-3660)',
                     '    still on www.fs.usda.gov, 3 min (park US-3660)'], lines
    assert P._still_line({'since': None}, 5000) is None


def main():
    fails = []
    for f in TESTS:
        try:
            f()
        except Exception as e:  # noqa: BLE001
            fails.append(f'FAIL {f.__name__}: {type(e).__name__}: {e}'[:300])
            if os.environ.get('KPC_TEST_TRACE'):
                traceback.print_exc()
    if fails:
        print('\n'.join(fails))
        return 1
    print(f'test_page_reader_fixes.py: ALL PASS ({len(TESTS)} tests)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
