"""Nov 10: the ONE pre-request host check for every KPC-Data fetch, no robots exemption, a robots 403 = a Disallow, the ONE
needs-download list, and the engine's time budget. Nothing here contacts any server (urlopen is replaced by a trap)."""
import importlib, json, os, pathlib, sys, time, urllib.error, urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
ENG = S / 'draft/tools/kpc_engine'
sys.path.insert(0, str(S))
import kpc_host_rules as HR  # noqa: E402
import kpc_needs_download as ND  # noqa: E402

BLOCKED = ['https://services-eu1.arcgis.com/abc/arcgis/rest/services/X/FeatureServer/0', 'https://services-ap1.arcgis.com/a/arcgis/rest/services/Y/MapServer/1',
           'https://services.arcgis.com/abc/arcgis/rest/services/X/FeatureServer/0', 'https://services7.arcgis.com/abc/arcgis/rest/services/X/FeatureServer/0',
           'https://services-eu1.arcgis.com/robots.txt', 'https://apps.fs.usda.gov/arcx/rest/services/EDW/X/MapServer/0',
           'https://ncnhde.natureserve.org/arcgis/rest/services/X/MapServer/0', 'https://ncnhde.natureserve.org/robots.txt',
           'https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest/services/Parcels/FeatureServer/0', 'svc:https://services-eu1.arcgis.com/a/arcgis/rest/services/B/FeatureServer|x']
ALLOWED = ['https://www.arcgis.com/sharing/rest/search?q=x', 'https://hub.arcgis.com/search?q=x', 'https://gis.blm.gov/arcgis/rest/services/x/MapServer/0',
           'https://api.pota.app/park/US-0001', 'https://servicesx.arcgis.com.example.org/x']


@pytest.fixture
def no_net(monkeypatch):
    calls = []
    def trap(*a, **k): calls.append(a[0] if a else k); raise AssertionError('a network request was made')
    monkeypatch.setattr(urllib.request, 'urlopen', trap)
    return calls


@pytest.mark.parametrize('u', BLOCKED)
def test_host_rules_block(u): assert not HR.host_ok(u)[0]


@pytest.mark.parametrize('u', ALLOWED)
def test_host_rules_allow(u): assert HR.host_ok(u)[0]


def test_who_for():
    assert HR.who_for(BLOCKED[8])[0] == 'never' and HR.who_for(BLOCKED[6])[0] == 'never'
    assert HR.who_for(BLOCKED[0])[0] == 'person' and HR.who_for(BLOCKED[5])[0] == 'person'
    assert HR.who_for(ALLOWED[2], lambda u: False)[0] == 'person' and HR.who_for(ALLOWED[2], lambda u: True)[0] == 'bot'


def test_manners_host_rule_before_any_request(no_net, monkeypatch, tmp_path):
    monkeypatch.setenv('KPC_ARCGIS_ROBOTS_EXEMPT', '1')   # the old switch does nothing any more
    import kpc_manners as K; K = importlib.reload(K)
    assert not hasattr(K, 'ARCGIS_EXEMPT') and not hasattr(K, 'ARCGIS_API')
    M = K.Manners('test')
    for u in BLOCKED:
        st = M.get(u)[0]
        assert st == 'host-rule' and K.robots_block(st) and not K.next_run(st)
        assert M.robots_ok(u) is False
    assert not no_net and not M.robots          # no robots.txt read, no request
    M.area = 'US-NC'
    M.get('https://ncnhde.natureserve.org/arcgis/rest/services/NHP/MapServer/0/query?where=1=1')
    f = tmp_path / 'n.json'
    K.write_needs(str(f))
    rows = {r['id']: r for r in json.load(open(f))['rows']}
    assert all(set(r) == set(ND.FIELDS) for r in rows.values())
    nc = [r for r in rows.values() if r['area'] == 'US-NC']
    assert nc and nc[0]['who'] == 'never' and nc[0]['url'].endswith('/MapServer/0')
    assert any(r['who'] == 'person' and r['host'] == 'services-eu1.arcgis.com' for r in rows.values())
    assert any(r['page'].startswith('https://hub.arcgis.com/search?q=') for r in rows.values())


def test_manners_robots_403_is_disallow(monkeypatch):
    import kpc_manners as K; K = importlib.reload(K)
    def r403(*a, **k): raise urllib.error.HTTPError('https://gis.example.gov/robots.txt', 403, 'no', {}, None)
    monkeypatch.setattr(urllib.request, 'urlopen', r403)
    M = K.Manners('test'); M._pace = lambda *a, **k: None
    st = M.get('https://gis.example.gov/arcgis/rest/services/x/MapServer/0?f=json')[0]
    assert st == 'robots' and not K.next_run(st)
    assert M.needs and M.needs[0][2] == 'robots'
    def r503(*a, **k): raise urllib.error.HTTPError('https://gis2.example.gov/robots.txt', 503, 'busy', {}, None)
    monkeypatch.setattr(urllib.request, 'urlopen', r503)
    assert M.get('https://gis2.example.gov/arcgis/rest/services/x/MapServer/0')[0] == 'robots-unreadable'


def test_world_harvest_no_exemption_and_host_rule(no_net):
    import kpc_world_harvest as H
    assert not hasattr(H, 'ROBOTS_API') and not hasattr(H, 'ROBOTS_API_PATH')
    for u in BLOCKED: assert H.robots_ok(u) is False
    assert not no_net
    with pytest.raises(RuntimeError): H.get('https://services-eu1.arcgis.com/a/arcgis/rest/services/X/FeatureServer/0')
    assert any(n[1].startswith('https://services-eu1.arcgis.com/') for n in H.NEEDS)
    src = (S / 'kpc_world_harvest.py').read_text(encoding='utf-8')
    assert 'robots_exempt' not in src and "rp.can_fetch('*', u)" not in src


def test_world_harvest_robots_status(monkeypatch):
    import kpc_world_harvest as H
    for code, want in ((403, False), (401, False), (404, True), (410, True), (503, False)):
        h = f'r{code}.example.gov'
        def f(*a, _c=code, **k): raise urllib.error.HTTPError(f'https://{h}/robots.txt', _c, 'x', {}, None)
        monkeypatch.setattr(urllib.request, 'urlopen', f); H.ROBOTS.pop(h, None)
        assert H.robots_ok(f'https://{h}/arcgis/rest/services/x/MapServer/0') is want, code
    def down(*a, **k): raise urllib.error.URLError('down')
    monkeypatch.setattr(urllib.request, 'urlopen', down); H.ROBOTS.pop('down.example.gov', None)
    assert H.robots_ok('https://down.example.gov/arcgis/rest/services/x') is False   # was 'allowed' on any error


def test_needs_list_merge_and_no_noise(tmp_path):
    p = tmp_path / 'n.json'
    r = ND.row('US-AZ', 'https://apps.fs.usda.gov/arcx/rest/services/EDW/X/MapServer/0/query', 'short', 'test', date='2026-11-10')
    assert r['who'] == 'person' and set(r) == set(ND.FIELDS)
    assert ND.add([r, dict(r)], p) == (1, 0, True)
    assert ND.add([dict(r)], p)[2] is False                      # the same row again: no change, not saved
    ND.add([dict(r, status='done')], p)
    ND.add([dict(r, added='2026-11-09')], p)                    # an older open row does not reopen a done one
    assert json.load(open(p))['rows'][0]['status'] == 'done'
    assert ND.FIELDS == ('id', 'area', 'layer', 'url', 'page', 'host', 'who', 'why', 'expected', 'have', 'source', 'added', 'status', 'note', 'src', 'check')
    assert ND.FORMAT == 1   # the same format number as KPC-Links kpc_master.NEEDS_FORMAT (the release asset is merged as-is)


def test_held_row_stays_held_unless_the_change_check(tmp_path):
    p = tmp_path / 'n.json'
    r = ND.row('US-AZ', 'https://apps.fs.usda.gov/arcx/rest/services/EDW/X/MapServer/0/query', 'short', 'test', date='2026-11-10')
    ND.add([dict(r, status='held')], p)
    ND.add([dict(r, added='2026-11-11')], p)                                     # a bot's open row does not reopen a held row
    assert json.load(open(p))['rows'][0]['status'] == 'held'
    ND.add([dict(r, added='2026-11-12', source='change check', src='h010')], p)   # a changed source does
    assert json.load(open(p))['rows'][0]['status'] == 'open'


def test_seeded_list_from_the_hand_filled_sources():
    d = json.load(open(ROOT / 'data/needs-download.json'))
    rows = d['rows']
    assert sum(1 for r in rows if r.get('src')) > 150 and {r['check'] for r in rows if r.get('src')} <= {'bot', 'person'}
    blob = json.dumps(d).lower()
    for flag in ('resale', 'non-commercial', 'noncommercial', 'all rights reserved', 'wdpa', 'protected planet'):
        assert flag not in blob, flag   # terms stay off the public list (only the source page)


def test_seeded_list_schema():
    d = json.load(open(ROOT / 'data/needs-download.json'))
    assert d['rows'] and all(set(r) == set(ND.FIELDS) for r in d['rows'])
    assert all(r['who'] in ('bot', 'person', 'never') and r['status'] in ('open', 'done', 'held') for r in d['rows'])
    assert all(r['who'] == 'never' for r in d['rows'] if r['host'] == 'ncnhde.natureserve.org')


def test_engine_vendor_is_the_club_copy_and_docs_match():
    for f in ('kpc_manners.py', 'kpc_host_rules.py', 'kpc_needs_download.py'):
        assert (ENG / 'vendor' / f).read_text(encoding='utf-8') == (S / f).read_text(encoding='utf-8'), f
    for f in ('README.md', 'TUNING.md', 'AGENT_TIPS.md', 'core/polite.py'):
        t = (ENG / f).read_text(encoding='utf-8')
        assert 'ArcGIS REST exempt as' not in t and 'ArcGIS REST API paths are the documented exception' not in t and 'ArcGIS REST (/rest/services/, /sharing/rest/) exempt' not in t, f


def test_engine_time_budget(no_net, tmp_path):
    sys.path.insert(0, str(ENG))
    from core import polite, workers
    P = polite.Polite(cache_dir=str(tmp_path / 'c'), deadline=time.time() - 1)
    r = P.get('https://gis.example.gov/x')
    assert r.status == 'deadline' and r.blocked and not P.blocked and not no_net   # no request, not logged as blocked
    P2 = polite.Polite(cache_dir=str(tmp_path / 'c2'))
    assert P2.get('https://services-eu1.arcgis.com/a/arcgis/rest/services/X/FeatureServer/0').blocked.startswith('blocked (host rule')
    # a row that runs past the deadline is not kept and not marked done (redone on --resume)
    dl = time.time() + 0.2
    def fn(ag, row, i): time.sleep(0.3); return {'ref': row['ref'], 'area': row['area']}
    res, timed = workers.run([('ag', [{'area': 'US-ZZ', 'ref': 'US-1'}])], fn, tmp_path / 'w', 't', n=1, deadline=dl)
    assert timed and res == []


def test_engine_workflow_staged_and_bounded():
    w = (ROOT / '.github/workflows/kpc-engine.yml').read_text(encoding='utf-8')
    assert 'timeout-minutes: 66' in w and 'MM=$(( 40 - ' in w
    assert "timeout --signal=TERM --kill-after=60 $(( (MM + 12) * 60 )) python3 $P run" in w and '--out ../stage-engine' in w
    assert 'rm -rf ../out/engine && mv ../stage-engine ../out/engine' in w and 'this run\'s output is DISCARDED' in w
    assert 'if [ "$E" = 0 ] || [ "$E" = 3 ]; then python3 $P export' in w
    assert 'timeout-minutes: 75' in w   # the job limit itself is unchanged


@pytest.mark.parametrize('wf', ['kpc-gis-hunter.yml', 'kpc-world-finder.yml', 'kpc-world-harvest.yml', 'kpc-collector.yml', 'kpc-engine.yml'])
def test_bots_write_the_one_list(wf):
    import yaml
    w = (ROOT / '.github/workflows' / wf).read_text(encoding='utf-8')
    d = yaml.safe_load(w)
    envs = [d.get('env') or {}] + [j.get('env') or {} for j in d['jobs'].values()]
    assert any(e.get('KPC_NEEDS_FILE') == 'data/needs-download.json' for e in envs)
    assert 'data/needs-download.json' in w.split('kpc_push_data.sh', 1)[1]


def test_copy_job_merges_master_rows_without_new_cron():
    import yaml
    w = (ROOT / '.github/workflows/kpc-copy-from-links.yml').read_text(encoding='utf-8')
    d = yaml.safe_load(w); on = d.get('on') or d.get(True)
    assert 'needs-list' in d['jobs'] and len(on['schedule']) == 3
    run = ''.join(s.get('run', '') for s in d['jobs']['needs-list']['steps'])
    assert 'releases/download/boundary-cache/needs-download.json' in run and 'kpc_needs_download.py merge' in run and 'data/waiting' not in run
