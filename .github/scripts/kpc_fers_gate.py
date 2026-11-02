#!/usr/bin/env python3
"""2-FER ROLLING RESTART GATE (chat 10, Nov 2 2026; HQ 11:00 AM, RULINGS 10:57 AM: 2-fers start over area by area, each only when its
KEY is released and its MAP AUDIT pass is clean). Two jobs, both never fail:

  questions <audit dir>   the map audit's 50 worst rows per finished area (questions.json) -> data/waiting/questions/map-audit.json
                          (rows already there keep their answer; an area's rows are replaced only when it was audited again),
                          and data/status/audited.json {area: date}
  gate                    per US state / Canadian province:
                            waiting for key    = its key file is still held in the waiting room
                            waiting for audit  = not audited yet, or audit rows with no answer (N open)
                            ready for 2-fers   = key out + audit clean
                          a READY area with no 2-fer run since its audit is started (kpc-fers-line, 2 per pass at most, never while
                          a key build is saving); written to data/status/fers-ready.json + a board line.
  python3 kpc_fers_gate.py questions ../out/audit | gate        env GH_TOKEN, GITHUB_REPOSITORY (gate starts runs)"""
import datetime as dt, glob, json, os, pathlib, subprocess, sys

QF = pathlib.Path('data/waiting/questions/map-audit.json')
AUD = pathlib.Path('data/status/audited.json')
READY = pathlib.Path('data/status/fers-ready.json')
TODAY = dt.date.today().isoformat()
REPO = os.environ.get('GITHUB_REPOSITORY') or 'KentuckyPortableClub/KPC-Data'


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def questions(adir):
    adir = pathlib.Path(adir)
    q = load(adir / 'questions.json', {}) or {}
    rows = q.get('questions') or []
    done_areas = {p.stem for p in adir.glob('*.json') if p.stem not in ('questions', 'state')}
    Q = load(QF, {'about': "KPC 10 map audit's worst outlines (50 per area): chat 2 fixes, chat 11 / 12 answer YES (right) / NO (wrong) / FIXED. An area's 2-fers start when its rows are all answered (kpc_fers_gate.py).", 'questions': []}) or {}
    old = {(r.get('area'), r.get('ref'), r.get('record')): r for r in Q.get('questions') or []}
    fresh_areas = {r.get('area') for r in rows}
    keep = [r for r in Q.get('questions') or [] if r.get('area') not in fresh_areas]
    for r in rows:
        o = old.get((r.get('area'), r.get('ref'), r.get('record')))
        if o and o.get('answer'): r = {**r, 'answer': o['answer'], 'checked_by': o.get('checked_by'), 'how': o.get('how')}
        keep.append(r)
    Q['questions'] = keep; Q['built'] = TODAY; Q['open'] = sum(1 for r in keep if not r.get('answer'))
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump(Q, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    A = load(AUD, {}) or {}
    for a in done_areas: A[a] = TODAY
    AUD.parent.mkdir(parents=True, exist_ok=True)
    json.dump(A, open(AUD, 'w'), indent=1, sort_keys=True)
    print(f"::notice title=Map audit questions::{len(rows)} worst rows from {len(fresh_areas)} areas -> map-audit.json ({Q['open']} open); {len(A)} areas audited so far", flush=True)


def gh(*a):
    r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def gate():
    areas = sorted({pathlib.Path(f).stem for f in glob.glob('data/parkinfo/US-*.json')} | {pathlib.Path(f).stem for f in glob.glob('data/ca-key/CA-??.json')} | {'US-KY'})   # KY has no parkinfo file (HQ 5:40 PM: it was missing from the board)
    A = load(AUD, {}) or {}
    Q = (load(QF, {}) or {}).get('questions') or []
    R = load(READY, {}) or {}
    st = R.setdefault('areas', {})
    rc, out = gh('repos/KentuckyPortableClub/KPC-Links/actions/runs?status=in_progress&per_page=50', '--jq', '[.workflow_runs[].name] | join("|")')
    key_saving = 'answer key' in (out or '').lower()
    started = []
    for a in areas:
        kind = 'us-key' if a.startswith('US-') else 'ca-key'
        held = any(pathlib.Path(f'data/waiting/in/data/{kind}/{a}{x}').exists() for x in ('.json', '.json.gz'))
        open_rows = sum(1 for r in Q if r.get('area') == a and not r.get('answer'))
        if held: s = 'waiting for key'
        elif a not in A: s = 'waiting for audit'
        elif open_rows: s = f'waiting for audit answers ({open_rows} open)'
        else: s = 'ready for 2-fers'
        prev = st.get(a) or ({'fers_started': '2026-11-02'} if a == 'US-KY' else {})   # Kentucky's fresh run was started by hand Nov 2 (HQ 11:00 AM)
        row = {'status': s, 'audited': A.get(a), 'fers_started': prev.get('fers_started')}
        if s == 'ready for 2-fers' and not key_saving and len(started) < 2 and (not prev.get('fers_started') or prev['fers_started'] < (A.get(a) or '')):
            tag = a.split('-')[1].lower() if a.startswith('US-') else a.lower().replace('-', '')
            rc, _ = gh('-X', 'POST', f'repos/{REPO}/actions/workflows/kpc-fers-line.yml/dispatches', '-f', 'ref=main', '-f', f'inputs[states]={a}', '-f', f'inputs[tag]={tag}', '-f', 'inputs[stage]=all')
            if rc == 0: row['fers_started'] = TODAY; started.append(a)
        st[a] = row
    R['updated'] = TODAY
    R['about'] = "2-fers start over area by area (RULINGS Nov 2 10:57 AM): an area runs when its key is out AND its map audit rows are all answered (kpc_fers_gate.py)."
    READY.parent.mkdir(parents=True, exist_ok=True)
    json.dump(R, open(READY, 'w'), indent=1, sort_keys=True)
    c = {}
    for v in st.values(): k = v['status'].split(' (')[0]; c[k] = c.get(k, 0) + 1
    msg = f'{sum(1 for r in Q if not r.get("answer"))} audit rows open in {len({r.get("area") for r in Q if not r.get("answer")})} areas; ' + ', '.join(f'{k} {n}' for k, n in sorted(c.items())) + (f'; started now: {" ".join(started)}' if started else '') + (' (a key build is saving: nothing started)' if key_saving else '')
    print(f'::notice title=2-fer gate::{msg}', flush=True)
    subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', '2-fer gate (areas ready / waiting)', 'green', msg[:300], 'chat 11 / 12 (audit answers), chat 2 (fixes)'], check=False)


if __name__ == '__main__':
    try:
        a = sys.argv[1:]
        if a[:1] == ['questions']: questions(a[1])
        elif a[:1] == ['gate']: gate()
        else: print(__doc__)
    except Exception as e: print(f'::notice title=2-fer gate::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
