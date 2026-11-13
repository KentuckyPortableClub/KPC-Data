#!/usr/bin/env python3
"""Offline test for the Nov 4 trails rules in .github/scripts/kpc_waiting_room.py (data/waiting/known/trails.json):
  * keep_lines (per Brandon via Super Head Bot (relayed), 4:35 AM CST Nov 4: 'Agree keep the official line'; Brandon, directly (Mapping chat), 4:36 AM CST Nov 4: 'No keep the full length ones we had'): a SHORTER new line for US-9905 / US-9906
    (or one with fewer points) is REJECTED (F-T6) and mode_release refuses it; the same or a longer line is not rejected; without
    the known file nothing changes
  * not_lines (per Brandon via Super Head Bot (relayed), 4:35 AM CST Nov 4): data/trails/finds-lines-report.json is held as F-T7, never released,
    and mode_resume does not bring it back as a bot's working copy; NOTHING is deleted (the held copy stays for Brandon's yes)
Uses the repo's live lines and known/trails.json, copied into a temp folder. The three held files (the shorter US-9905 / US-9906
lines and finds-lines-report.json) come from tests/fixtures/trails_keep_nov4/ (byte copies of KPC-Data main 6d8d11d6), so the test
passes with or without patch data-04-delete-dead-files, and it shows the guards still hold if those files come back. No network."""
import importlib.util, io, json, os, pathlib, shutil, sys, tempfile, contextlib

HERE = pathlib.Path(__file__).resolve().parent.parent
TOOL = HERE / '.github/scripts/kpc_waiting_room.py'
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


def load_tool(data):
    os.environ['DATA'] = str(data); os.environ['LINKS'] = str(data / 'nolinks')
    spec = importlib.util.spec_from_file_location('wr_' + data.name, TOOL); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


FIX = HERE / 'tests/fixtures/trails_keep_nov4'
HELD = 'data/waiting/in/data/trails/'


def cp(rel, root, src_rel=None):
    """Copy a repo file into the temp repo; a held trails file comes from the fixtures (data-04 may have deleted the repo copy)."""
    d = root / rel; d.parent.mkdir(parents=True, exist_ok=True)
    src = src_rel or rel
    shutil.copy2(FIX / ('held-' + src[len(HELD):]) if src.startswith(HELD) else HERE / src, d)


def quiet(f, *a):
    b = io.StringIO()
    with contextlib.redirect_stdout(b): f(*a)
    return b.getvalue()


with tempfile.TemporaryDirectory() as t:
    R = pathlib.Path(t) / 'data_repo'
    for r in ('US-9905', 'US-9906'):
        cp(f'data/trails/{r}.json', R); cp(f'data/waiting/in/data/trails/{r}.json', R)
    cp('data/waiting/in/data/trails/finds-lines-report.json', R)
    cp('data/waiting/known/trails.json', R)
    W = load_tool(R)
    for r, short_km in (('US-9905', 2.9), ('US-9906', 4.5)):
        live = W.load(R / f'data/trails/{r}.json'); new = W.load(R / f'data/waiting/in/data/trails/{r}.json')
        res = W.judge(f'data/trails/{r}.json', new, live)
        f6 = [h for h in res['why'] if h.startswith('F-T6 REJECTED')]
        check(res['verdict'] == 'HOLD' and f6 and 'Super Head Bot (relayed), 4:35 AM CST' in f6[0] and 'directly (Mapping chat), 4:36 AM CST' in f6[0], f'{r}: the shorter held line ({short_km} km) is REJECTED (F-T6, both Brandon Nov 4 lines cited)')
        same = W.judge(f'data/trails/{r}.json', live, live)
        check(not any(h.startswith('F-T6') for h in same['why']), f'{r}: the kept full-length official line itself is not rejected')
        longer = json.loads(json.dumps(live)); g = longer['geometry']
        lines = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
        lines[-1] = lines[-1] + [[p[0] + .0005, p[1] + .0005] for p in lines[-1][-5:]]
        if g['type'] == 'LineString': g['coordinates'] = lines[0]
        check(not any(h.startswith('F-T6') for h in W.judge(f'data/trails/{r}.json', longer, live)['why']), f'{r}: a longer line with more points is not rejected (normal checks only)')
        before = (R / f'data/trails/{r}.json').read_bytes()
        out = quiet(W.mode_release, f'data/trails/{r}.json')
        check('refused' in out and (R / f'data/waiting/in/data/trails/{r}.json').exists() and (R / f'data/trails/{r}.json').read_bytes() == before,
              f'{r}: mode_release refuses the shorter line (held copy kept, live line unchanged)')
    rep = W.load(R / 'data/waiting/in/data/trails/finds-lines-report.json')
    res = W.judge('data/trails/finds-lines-report.json', rep, None)
    check(res['verdict'] == 'HOLD' and any(h.startswith('F-T7') and 'data/status/finds-lines-report.json' in h for h in res['why']), 'finds-lines-report.json under data/trails is held as F-T7 (not a trail line; home data/status)')
    out = quiet(W.mode_release, 'data/trails/finds-lines-report.json')
    check('refused' in out and not (R / 'data/trails/finds-lines-report.json').exists() and (R / 'data/waiting/in/data/trails/finds-lines-report.json').exists(), 'mode_release refuses the report; it is never released into data/trails, and the held copy is NOT deleted')
    for r in ('US-9905', 'US-9906'): (R / f'data/trails/{r}.json').unlink()   # temp folder only: let resume show what it copies
    out = quiet(W.mode_resume, ['data/trails'])
    check((R / 'data/trails/US-9905.json').exists() and not (R / 'data/trails/finds-lines-report.json').exists() and 'not taken' in out,
          'mode_resume brings back held lines but not the held status report (the loop that kept re-holding it is broken)')
    check((R / 'data/waiting/in/data/trails/finds-lines-report.json').exists(), 'mode_resume deletes nothing (held report still there for Brandon)')

with tempfile.TemporaryDirectory() as t:   # without known/trails.json the checker behaves as before
    R = pathlib.Path(t) / 'data_repo'
    cp('data/trails/US-9905.json', R); cp('data/waiting/in/data/trails/US-9905.json', R); cp('data/waiting/in/data/trails/finds-lines-report.json', R)
    W = load_tool(R)
    res = W.judge('data/trails/US-9905.json', W.load(R / 'data/waiting/in/data/trails/US-9905.json'), W.load(R / 'data/trails/US-9905.json'))
    check(res['verdict'] == 'HOLD' and not any(h.startswith('F-T6') for h in res['why']) and any(h.startswith('F-T2') for h in res['why']), 'no known/trails.json: US-9905 holds on F-T2/F-T3 as before, no F-T6')
    res = W.judge('data/trails/finds-lines-report.json', W.load(R / 'data/waiting/in/data/trails/finds-lines-report.json'), None)
    check(res['verdict'] == 'HOLD' and any(h.startswith('F-T1') for h in res['why']), 'no known/trails.json: the report holds on F-T1 as before')

with tempfile.TemporaryDirectory() as t:   # end to end: a chat 11 YES in approved.json does not let the rejected line out
    import subprocess
    R = pathlib.Path(t) / 'data_repo'
    cp('data/trails/US-9905.json', R); cp('data/waiting/in/data/trails/US-9905.json', R); cp('data/waiting/known/trails.json', R)
    json.dump({'items': [{'path': 'data/waiting/in/data/trails/US-9905.json', 'chat11': 'YES', 'date': '2026-11-04', 'time': '4:40 AM', 'by': 'KPC owner'}]},
              open(R / 'data/waiting/approved.json', 'w'))
    before = (R / 'data/trails/US-9905.json').read_bytes()
    e = dict(os.environ, DATA=str(R), LINKS=str(R / 'nolinks'))
    p = subprocess.run([sys.executable, str(HERE / '.github/scripts/kpc_release_approved.py')], cwd=R, env=e, capture_output=True, text=True)
    logtxt = ''.join(f.read_text() for f in (R / 'data/waiting').glob('released*') if f.is_file())
    check((R / 'data/trails/US-9905.json').read_bytes() == before and (R / 'data/waiting/in/data/trails/US-9905.json').exists() and 'refused' in (p.stdout + logtxt),
          'kpc_release_approved.py: a chat 11 YES for the rejected US-9905 line releases nothing, and the log says it was refused')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
