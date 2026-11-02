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


AUTOQ = pathlib.Path('data/waiting/questions/map-audit-auto.json')
HEALTH = {'SELF-INTERSECTION', 'TINY HOLES', 'SLIVERS', 'INVALID'}


def flags_of_row(r):
    """the row's flags: its 'flags' list (audits from Nov 2 6 PM on), else read from its note 'score N: T5 SLIVERS, T3 MISMATCH'"""
    if r.get('flags') is not None: return list(r['flags'])
    n = str(r.get('note') or '')
    return [x.strip().split(' ', 1)[1] for x in n.split(':', 1)[1].split(',') if ' ' in x.strip()] if ':' in n else []


def pattern_of(r):
    """HQ 5:55 PM: one kind of problem = one pattern; chats 11 / 12 answer a pattern after a sample of 10"""
    w = str(r.get('why') or '')
    if w.startswith('SOURCE DOWN'): return 'SOURCE DOWN'
    f = w.split(':', 1)[0].strip()
    lw = w.lower()
    if f == 'OFF': return 'OFF smaller' if 'smaller' in lw else 'OFF bigger'
    if f == 'WAY OFF': return 'WAY OFF smaller' if 'smaller' in lw else 'WAY OFF bigger'
    if f == 'CONFLICT':
        for k in ('lake', 'wma', 'forest', 'river', 'trail', 'state park', 'refuge', 'recreation'):
            if k in lw: return f'CONFLICT {k}'
        return 'CONFLICT other'
    return f or 'OTHER'


def auto_of(r):
    """-> what a bot does instead of asking a person, or None (HQ 5:55 PM pile-down A)"""
    fl = set(flags_of_row(r))
    if str(r.get('why') or '').startswith('SOURCE DOWN') or r.get('down'): return 'source down: the audit reads it again next run (not a question)'
    if fl and fl <= HEALTH | {'STALE CHECK'} and (r.get('repaired') or (r.get('flags') is None and fl & HEALTH)):
        return 'shape repaired by the audit (repairs/<area>.json on tools-out audit/: make_valid, holes < 100 m2 and pieces < 10 m dropped, land kept within 1 %)' if r.get('repaired') else 'shape repair: the next audit run repairs it (a row from before the repair step)'
    if fl == {'STALE CHECK'}: return 'stale source: a note, not a question'
    return None


def apply_patterns(Q):
    """a pattern answer (map-audit.json 'patterns': {pattern: {answer, by, sample: [10 refs], date, note}}) answers every OPEN row of it"""
    P = Q.get('patterns') or {}
    n = 0
    for r in Q.get('questions') or []:
        r['pattern'] = pattern_of(r)
        a = P.get(r['pattern'])
        if a and a.get('answer') and not r.get('answer'):
            r.update(answer=a['answer'], checked_by=a.get('by'), how=f"pattern answer '{r['pattern']}' ({a.get('date', '')}, sample {', '.join((a.get('sample') or [])[:10])})"); n += 1
    return n


def split_auto(Q):
    """open rows a bot handles leave the person's list for map-audit-auto.json (kept, counted on the board)"""
    keep, auto = [], []
    for r in Q.get('questions') or []:
        a = None if r.get('answer') else auto_of(r)
        if a: auto.append({**r, 'auto': a})
        else: keep.append(r)
    Q['questions'] = keep
    A = load(AUTOQ, {}) or {}
    old = {(x.get('area'), x.get('ref'), x.get('record')): x for x in A.get('rows') or []}
    for x in auto: old[(x.get('area'), x.get('ref'), x.get('record'))] = x
    A.update(about="Map-audit rows a BOT handles (HQ Nov 2 5:55 PM pile-down): shape repairs, sources that were down (read again next run), stale-source notes. Not asked of a person.", rows=list(old.values()), built=TODAY)
    json.dump(A, open(AUTOQ, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return len(auto)


def tidy(Q):
    """pile-down: auto rows out, pattern answers in, open recounted (runs after every audit job and every gate)"""
    na = split_auto(Q); npat = apply_patterns(Q)
    Q['open'] = sum(1 for r in Q.get('questions') or [] if not r.get('answer'))
    c = {}
    for r in Q.get('questions') or []:
        if not r.get('answer'): c[r['pattern']] = c.get(r['pattern'], 0) + 1
    Q['open_by_pattern'] = dict(sorted(c.items(), key=lambda kv: -kv[1]))
    Q.setdefault('patterns', {})
    Q['how_to_answer_a_pattern'] = "Read 10 random open rows of one pattern. If all 10 agree, write patterns[<pattern>] = {answer: YES|NO|PIN, by: 'chat 11', sample: [the 10 refs], date, note}; it answers every open row of that pattern. Any disagreeing row: answer it by hand and say so in the note."
    return na, npat


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
    Q['questions'] = keep; Q['built'] = TODAY
    na, npat = tidy(Q)
    QF.parent.mkdir(parents=True, exist_ok=True)
    json.dump(Q, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    A = load(AUD, {}) or {}
    for a in done_areas: A[a] = TODAY
    AUD.parent.mkdir(parents=True, exist_ok=True)
    json.dump(A, open(AUD, 'w'), indent=1, sort_keys=True)
    print(f"::notice title=Map audit questions::{len(rows)} worst rows from {len(fresh_areas)} areas -> map-audit.json ({Q['open']} open for a person; {na} to the bots' list; {npat} answered by a pattern); {len(A)} areas audited so far", flush=True)


def gh(*a):
    r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True)
    return r.returncode, r.stdout


def gate():
    areas = sorted({pathlib.Path(f).stem for f in glob.glob('data/parkinfo/US-*.json')} | {pathlib.Path(f).stem for f in glob.glob('data/ca-key/CA-??.json')} | {'US-KY'})   # KY has no parkinfo file (HQ 5:40 PM: it was missing from the board)
    A = load(AUD, {}) or {}
    QQ = load(QF, {}) or {}
    if QQ.get('questions'):
        na, npat = tidy(QQ); json.dump(QQ, open(QF, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        if na or npat: print(f'::notice title=Map audit pile::{na} rows to the bots\' list, {npat} answered by a pattern; {QQ["open"]} open for a person', flush=True)
    Q = QQ.get('questions') or []
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
