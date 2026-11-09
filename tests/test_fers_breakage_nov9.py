"""Nov 9 2-fer breakage fixes (Quality grade of run 42594981324): time budget, KISS ownership (no owned-land store), post-line after kpc-fers.yml."""
import os, pathlib, subprocess, tempfile
import yaml
ROOT = pathlib.Path(__file__).resolve().parents[1]
W = ROOT / '.github/workflows'


def _steps(f, job):
    return yaml.safe_load(open(W / f))['jobs'][job]['steps']


def test_kiss_ownership_no_owned_store():
    # Brandon Nov 9, 9:37 AM CST (KISS): the owner comes from the park record / agency name; the run reads no owned-land store
    st = _steps('kpc-fers.yml', 'fers')
    assert not any('KPC-Archive' in str(s.get('with', {}).get('repository', '')) for s in st)
    assert 'OWNED_STORE' not in open(W / 'kpc-fers.yml').read()


def test_no_cron_added():
    for f in ('kpc-fers.yml', 'kpc-fers-postline.yml'):
        on = yaml.safe_load(open(W / f)).get(True) or yaml.safe_load(open(W / f)).get('on')
        assert 'schedule' not in on


def test_time_budget_never_past_step_limit():
    look = next(s for s in _steps('kpc-fers.yml', 'fers') if s.get('id') == 'kept_green_3')
    run = look['run']
    # run the planning arithmetic alone: a job that started 45 minutes ago (POTA history) with MINUTES=320
    plan = run.split('for p in 1 2 3 5; do')[0].split('if [ "$PASS" = all ]; then', 1)[1]
    env = dict(os.environ, MINUTES='320', KPC_JOB_T0=str(int(__import__('time').time()) - 45 * 60))
    out = subprocess.run(['bash', '-c', plan + '\necho $TOTAL'], env=env, capture_output=True, text=True).stdout.split()
    assert int(out[-1]) <= 335 - 45 - 5 + 1
    assert 'CAP=$(( TOTAL * 2 / 5 ))' in run


def test_postline_one_step_after_the_2fer_bot():
    y = yaml.safe_load(open(W / 'kpc-fers-postline.yml'))
    on = y.get(True) or y.get('on')
    assert 'prev_ref' in on['workflow_dispatch']['inputs']
    assert 'gh workflow run kpc-fers-postline.yml' in open(W / 'kpc-fers-postline.yml').read()
    assert any('PREV_DIR' in str(s.get('run', '')) for s in y['jobs']['postline']['steps'])
