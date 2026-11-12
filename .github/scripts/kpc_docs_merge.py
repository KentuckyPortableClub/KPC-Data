#!/usr/bin/env python3
"""OUTSIDE OFFICIAL DOCUMENTS -> data/docs (chat 10, Oct 31 2026; HQ 4:10 PM + 4:55 PM, Brandon's outside research F).
Reads every data/intake/docs-found-*.json and archive/2026-10/docs-found-*.json ({ref: {st, page, map, map_page, kind, date, agency, notes}}; the US F file and the map-page
link extractor's two files use the same shape) and merges them into the documents bot's area files the way the bot's own finds go in:
  - a map we already hold with status ok is NEVER overwritten (the found page may still fill an empty 'page');
  - the link must OPEN and NAME THE PARK (the documents bot's own check_url: PDF first page / page text / file name / link id);
  - a file shared by more than 3 parks is not a park's own map (kept as a note only);
  - sign / logo / letterhead files are never maps (the link extractor's weak spot: 'Sign-with-FedDev-logo.pdf');
  - 'possible' rows (docs-found-*-possible.json) need the same checks; nothing is taken on trust.
Run inside the waiting-room pattern (resume data/docs -> this -> divert data/docs): nothing goes live without chat 11's YES.
Kentucky first, then the US by state, then Canada. Resumable (data/intake/docs-merge-done.json); MINUTES per run. Never fails.
Areas the documents bot is still reading are left for later (no two writers on one file).
Nov 11 2026 (fewer runs; 594 self-starts in a week): the last lines say LEFT=<rows still to merge> and DONE=<rows that got a final
answer this run>. A row whose link timed out / whose host rests stays LEFT but is not DONE, so a run that only met such rows
starts no other run (kpc_chain.py in the workflow: next run only when LEFT > 0 AND DONE > 0, under a cap)."""
import datetime as dt, glob, json, os, pathlib, re, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.argv = sys.argv[:1]   # the documents bot reads argv/env at import: keep it quiet
import kpc_docs_bot as B  # noqa: E402

TODAY = dt.date.today().isoformat()
LIMIT = float(os.environ.get('MINUTES') or 50) * 60
T0 = time.time()
DONE_F = pathlib.Path('data/intake/docs-merge-done.json')
NOTMAP = re.compile(r'(?:^|[\W_])(sign|signs|signage|logo|letterhead|banner|header|footer|icon|favicon|button|badge|qr)(?:[\W_]|$)', re.I)


def note(m): print('::notice title=Documents merge::' + str(m)[:900], flush=True)


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def area_of(ref, v):
    st = str(v.get('st') or '').upper()
    if ref.startswith('US-') and re.fullmatch(r'[A-Z]{2}', st): return f'US-{st}'
    if ref.startswith('CA-') and re.fullmatch(r'[A-Z]{2}', st): return f'CA-{st}'
    return None


def main():
    rows = {}
    # basename order, same as when docs-found-us-oct31.json still sat in data/intake (a later file wins). The archived
    # Oct 31 file keeps that place; _in (the intake reader's working copy of branch intake-files) stays last.
    names = sorted({os.path.basename(f) for f in glob.glob('data/intake/docs-found-*.json') + glob.glob('archive/2026-10/docs-found-*.json')})
    found_files = []
    for n in names:
        for d in ('data/intake', 'archive/2026-10'):
            p = os.path.join(d, n)
            if os.path.isfile(p):
                found_files.append(p); break
    found_files += sorted(glob.glob('data/intake/_in/docs/docs-found-*.json'))
    for f in found_files:
        possible = f.endswith('-possible.json')
        for ref, v in (load(f, {}) or {}).items():
            if isinstance(v, dict) and (v.get('map') or v.get('page')):
                old = rows.get(ref)   # a later file (v2, Canada) wins over an older one, unless it has no map and the older does
                if old is None or v.get('map') or not old.get('map'): rows[ref] = dict(v, _from=pathlib.Path(f).name, _possible=possible)
    if not rows: note('no docs-found files with rows'); print('LEFT=0'); return
    done = load(DONE_F, {}) or {}
    done0 = len(done)
    uses = {}
    for v in rows.values():
        if v.get('map'): uses[v['map']] = uses.get(v['map'], 0) + 1
    st = (load('data/docs/state.json', {}) or {}).get('areas') or {}
    busy = {a for a, x in st.items() if (x or {}).get('status') != 'done'}
    order = sorted(rows, key=lambda r: (0 if str(rows[r].get('st')).upper() == 'KY' else 1, 0 if r.startswith('US-') else 1, str(rows[r].get('st')), r))
    files, n = {}, {'map added': 0, 'page added': 0, 'kept ours': 0, 'did not open': 0, 'does not name the park': 0, 'shared file': 0,
                    'not a map (sign / logo)': 0, 'area busy (later)': 0, 'no area': 0}
    for ref in order:
        if time.time() - T0 > LIMIT: break
        v = rows[ref]; key = f"{ref}|{v.get('map') or ''}|{v.get('page') or ''}"
        if key in done: continue
        area = area_of(ref, v)
        if not area: done[key] = 'no area'; n['no area'] += 1; continue
        if area in busy: n['area busy (later)'] += 1; continue
        if area not in files: files[area] = load(f'data/docs/{area}.json', None) or {'area': area, 'parks': {}}
        D = files[area]; P = D.setdefault('parks', {}); p = P.setdefault(ref, {})
        name = p.get('n') or ''
        if not name:
            info = (load(f'data/parkinfo/{area}.json', {}) or {}).get('parks') or {} if area.startswith('US-') else {}
            name = (info.get(ref) or [''])[0] if isinstance(info.get(ref), list) else ''
            if name: p['n'] = name
        if v.get('page') and (not p.get('page') or (v.get('replace_page') and p.get('page') in (v.get('old_page'), '') )):   # Nov 1: outside page fixes replace a dead / wrong page
            if v.get('replace_page') and p.get('page'): p.setdefault('notes', []).append(f"{TODAY}: page {p['page']} replaced ({v.get('notes')})")
            p['page'] = v['page']; n['page added'] += 1
        m = v.get('map')
        if not m: done[key] = 'page only'; continue
        if (p.get('map') or {}).get('status') == 'ok': done[key] = 'kept ours'; n['kept ours'] += 1; continue
        if NOTMAP.search(B.file_words(m)): done[key] = 'not a map'; n['not a map (sign / logo)'] += 1; continue
        if uses.get(m, 0) > 3:
            p.setdefault('notes', []).append(f"{TODAY}: outside research map {m} is the same file for {uses[m]} parks: not this park's own map"); done[key] = 'shared'; n['shared file'] += 1; continue
        r = B.check_url(m, name=name)
        if r.get('status') != 'ok':
            n['did not open'] += 1
            if re.match(r'HTTP 4|robots|opened', str(r.get('status'))): done[key] = f"did not open: {r.get('status')}"[:120]   # a real answer: final
            continue   # a time-out / server error / resting host: tried again next run
        if not r.get('names_park') and r.get('kind') in ('pdf', 'page', 'image'): done[key] = 'does not name the park'; n['does not name the park'] += 1; continue
        r.pop('text', None); r.pop('links', None)
        r.update({'how': f"Brandon's outside research Oct 31 ({v.get('_from')}{', possible' if v.get('_possible') else ''}): link opened + names the park",
                  'via': 'outside research', 'agency_given': v.get('agency') or '', 'date_given': v.get('date'), 'page': v.get('page') or p.get('page') or ''})
        if v.get('map_page'): r['map_page'] = v['map_page']
        p['map'] = r; p['checked'] = TODAY
        done[key] = 'map added'; n['map added'] += 1
    for area, D in files.items():
        B.save(pathlib.Path(f'data/docs/{area}.json'), D)
    DONE_F.parent.mkdir(parents=True, exist_ok=True)
    json.dump(done, open(DONE_F, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    left = sum(1 for ref in rows if f"{ref}|{rows[ref].get('map') or ''}|{rows[ref].get('page') or ''}" not in done and area_of(ref, rows[ref]) not in busy)
    note('; '.join(f'{k} {v}' for k, v in n.items() if v) + f'; rows left {left}; done this run {len(done) - done0}')
    print(f'LEFT={left}')
    print(f'DONE={len(done) - done0}')


if __name__ == '__main__':
    try: main()
    except Exception as e: note(f'stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
