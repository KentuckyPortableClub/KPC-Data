#!/usr/bin/env python3
"""FLOW BOARD (chat 10, Nov 1 2026; Brandon 2:01 PM: 'stuff seems to get dropped a lot ... where you can see for example 900
layers in x bot and a date so you all know it has not moved to the right place and a list of waiting on approvals ... it all gets
done at some point').

Every pile of work in the line, with its count, who it waits on and the date it LAST MOVED:
  finders -> layer list (queue) -> intake check -> engine -> collector -> questions (YES / NO) -> waiting room -> live.
A pile with work in it that has not moved for STUCK_DAYS is STUCK and goes to the top. 'Moved' = its count changed (work came in
or went out) since the last look; the date is kept in data/status/flow.json between runs.
Writes data/status/flow.json (counts + history) and data/status/flow.md (STUCK first, then per chat, then the whole line).
Every chat sees its lines at the start: .claude/build/inbox_now.py (KPC-Links) prints them. Reads only; decides nothing.
  python3 .github/scripts/kpc_flow.py            (from the KPC-Data root; git branches tools-out / intake-files / engine-registry
                                                   are read with git show, nothing is checked out)"""
import datetime as dt, glob, json, os, pathlib, re, subprocess
sys_path = str(pathlib.Path(__file__).resolve().parent)
import sys
if sys_path not in sys.path: sys.path.insert(0, sys_path)
from kpc_json_any import glob_json_any, load_json_any  # noqa: E402

TODAY = dt.date.today()
STUCK_DAYS = 2
OUT_J, OUT_M = pathlib.Path('data/status/flow.json'), pathlib.Path('data/status/flow.md')


def load(p, d=None):
    try: return load_json_any(p)
    except (OSError, ValueError): return d


def git(*a):
    try: return subprocess.run(['git', *a], capture_output=True, text=True, timeout=120).stdout
    except Exception: return ''  # noqa: BLE001


def changed(path, ref=''):                            # date of the last commit that touched a file (main, or a branch)
    p = str(path)
    gz, plain = (p, p[:-3]) if p.endswith('.gz') else (p + '.gz', p)
    cands = [c for c in (gz, plain) if os.path.exists(c)] or [p]
    for c in cands:
        s = git('log', '-1', '--format=%cs', *([ref] if ref else []), '--', c).strip()
        if s: return s
    return None


def show(ref, path):
    try: return json.loads(git('show', f'{ref}:{path}') or 'null')
    except ValueError: return None



def main():
    for b in ('tools-out', 'intake-files', 'engine-registry'):
        git('fetch', '-q', '--depth=50', 'origin', f'+refs/heads/{b}:refs/remotes/origin/{b}')   # recent history is enough for 'last changed'

    P = []   # piles: {id, stage, what, n, owner, note, date (when its file last changed)}


    def pile(id_, stage, what, n, owner, note='', date=None):
        P.append({'id': id_, 'stage': stage, 'what': what, 'n': int(n or 0), 'owner': owner, 'note': note, 'date': date})


    def lead_key(u): return re.sub(r'/(featureserver|mapserver)(/\d+)?/?$', '', (u or '').split('?')[0].lower().rstrip('/'))


    # ---- 1. FINDERS: what they made that has not reached the layer list yet
    queue = (load('data/intake/queue.json', {}) or {}).get('rows') or []
    inq = {lead_key(r.get('url')) for r in queue}
    n = 0
    for f in glob.glob('data/harvest/leads-*.json'):
        L = (load(f, {}) or {}).get('leads') or {}
        n += sum(1 for k, v in (L.items() if isinstance(L, dict) else []) if isinstance(v, dict) and v.get('band') == 'A' and v.get('url') and lead_key(v['url']) not in inq)
    pile('harvest-to-queue', '1 finders', 'world harvester A leads not in the layer list yet', n, 'intake bot (daily 8:41 UTC)', '', changed('data/harvest'))
    dl = [v for v in ((load('data/discovery/new-a-leads.json', {}) or {}).get('leads') or []) if isinstance(v, dict)
          and re.search(r'/rest/services/|wfs|\.(geojson|kml|kmz|zip)(\?|$)', v.get('url') or '', re.I) and lead_key(v['url']) not in inq]
    pile('discovery-to-queue', '1 finders', 'discovery bot map-layer leads not in the layer list yet', len(dl), 'intake bot (daily 8:41 UTC)', '', changed('data/discovery'))
    reg = show('origin/engine-registry', 'registry/us_ca_discovered.json') or load('.github/scripts/draft/tools/kpc_engine/registry/us_ca_discovered.json', {}) or {}
    pile('engine-crawler', '1 finders', 'engine crawler layers (US + Canada) the engine tries at the pins', len(reg.get('found') or []), 'park-info engine (every run)',
         'information: these wait on nothing', changed('registry/us_ca_discovered.json', 'origin/engine-registry'))

    # ---- 2. OUTSIDE FILES on branch intake-files that no reader has taken yet
    board = (load('data/status/board.json', {}) or {}).get('bots') or {}
    read = {k.split(':', 1)[1].strip() for k in board if k.startswith('Intake:')}
    read |= {f for v in ((load('data/intake/intake-seen.json', {}) or {}).values()) if isinstance(v, dict) for f in v}   # the reader's own seen list
    KINDS = ('camping', 'parking', 'docs', 'convert', 'external-sources', 'world-sources', 'questions', 'hours', 'acres', 'portals', 'hardlook')
    files = [f for f in git('ls-tree', '--name-only', 'origin/intake-files').split() if f.endswith(('.json', '.xlsx', '.csv')) and f.startswith(KINDS)]
    unread = [f for f in files if f not in read and not (f.endswith('.xlsx') and f[:-5] + '.json' in files)]
    # the readers run inside other bots that do not always save the seen list: a file is also read when its bot ran AFTER the file came
    USES = {'camping': ['kpc-camp-layers', 'kpc-workshop'], 'parking': ['kpc-us-access'], 'docs': ['kpc-docs-merge'], 'convert': ['kpc-convert-layers'],
            'external-sources': ['kpc-collector'], 'world-sources': ['kpc-collector', 'kpc-convert-layers'], 'questions': ['kpc-waiting-room'],
            'hours': ['kpc-waiting-room'], 'acres': ['kpc-tool-trial'], 'portals': ['kpc-collector'], 'hardlook': ['kpc-hardlook']}
    _last = {}


    def last_ok(wf):                                       # the newest successful run of a bot (gh api; '' when unknown)
        if wf not in _last:
            try: _last[wf] = subprocess.run(['gh', 'api', f'repos/KentuckyPortableClub/KPC-Data/actions/workflows/{wf}.yml/runs?status=success&per_page=1',
                                             '--jq', '.workflow_runs[0].run_started_at // ""'], capture_output=True, text=True, timeout=60).stdout.strip()
            except Exception: _last[wf] = ''  # noqa: BLE001
        return _last[wf]


    still = []
    for f in unread:
        came = git('log', '-1', '--format=%cI', 'origin/intake-files', '--', f).strip()
        kind = next((k for k in USES if f.startswith(k)), None)
        runs = [last_ok(w) for w in USES.get(kind, [])]
        wait_d = {'acres': 7}.get(kind, 0)   # Nov 2: the acres reader runs weekly (tool trial, Sundays): a file younger than that is on time, not unread
        if wait_d and came and (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(came.strip())).days < wait_d: continue
        if not (came and any(r and r > came[:19].replace('+00:00', '') for r in runs)): still.append(f)
    unread = still   # an .xlsx twin of a .json is the same data
    pile('intake-unread', '2 outside files', 'files on branch intake-files no reader has taken yet', len(unread), 'chat 10 (the reader of that kind)',
         ', '.join(unread[:12]) + (' …' if len(unread) > 12 else ''), changed('.', 'origin/intake-files'))

    # ---- 3. LAYER LIST -> intake check (open terms / publisher)
    ready = {lead_key(r.get('url')) for r in ((load('data/intake/ready.json', {}) or {}).get('rows') or []) if isinstance(r, dict)}
    unprobed = [r for r in queue if r.get('url') and lead_key(r['url']) not in ready]
    old = min((r.get('added') or '9999') for r in unprobed) if unprobed else ''
    pile('queue-unchecked', '3 layer list', 'layers in the list the intake bot has not checked yet', len(unprobed), 'intake bot (daily, 40 a night)',
         f'oldest added {old}' if old else '', changed('data/intake/queue.json'))

    # ---- 4. ENGINE: did its last runs save, and what did it hand to the collector
    eng_saved = changed('engine', 'origin/tools-out')
    hb = show('origin/intake-files', 'external-sources-engine.json') or {}
    hbn = len(hb.get('pairs') or hb.get('rows') or hb.get('sources') or []) if isinstance(hb, dict) else len(hb or [])
    pile('engine-finds', '4 engine', 'engine finds handed to the collector (last hand-back)', hbn, 'layer collector (every 2 h)',
         f'engine results last saved {eng_saved}', changed('external-sources-engine.json', 'origin/intake-files'))
    P[-1]['engine_saved'] = eng_saved

    # ---- 5. COLLECTOR: outside-research pairs still to pin-test
    er = (load('data/intake/external-results.json', {}) or {}).get('summary') or {}
    pile('collector-left', '5 collector', 'outside-research layer x park pairs not pin-tested yet', er.get('pairs left') or 0, 'layer collector (every 2 h)', '',
         changed('data/intake/external-results.json'))

    # ---- 6. QUESTIONS: everything waiting on a YES / NO
    for f in glob_json_any('data/waiting/questions/*.json'):
        d = load(f)
        if d is None: continue
        name = pathlib.Path(f).stem
        about = d.get('about', '') if isinstance(d, dict) else ''
        owner = 'chat 9' if 'chat9' in name else (re.search(r'\b(chat \d+) (?:answers|fills|grades)', about) or [None, 'chat 11'])[1]
        rows = d if isinstance(d, list) else (d.get('questions') or d.get('rows') or (d.get('open') if isinstance(d.get('open'), list) else []) or [])
        rows = [r[1] if isinstance(r, list) and len(r) == 2 else r for r in (rows.values() if isinstance(rows, dict) else rows)]
        if any(isinstance(r, dict) and 'answer' in r for r in rows):   # count the rows themselves: a file's own 'open' number can be stale (chat 11 Nov 1)
            n = sum(1 for r in rows if isinstance(r, dict) and not str(r.get('answer') or '').strip())
        elif isinstance(d, dict) and str(d.get('open', '')).isdigit(): n = int(d['open'])
        elif 'for-chat' in name: n = len(rows)
        else: continue   # information only (no answer box)
        pile(f'q-{name}', '6 questions', f'questions/{name}.json waiting for an answer', n, owner, (about[:90] + '…') if len(about) > 90 else about, changed(f))

    # ---- 7. WAITING ROOM: held files (a check failed) and files waiting for a grader
    held = load('data/waiting/held-since.json', {}) or {}
    grp = {}
    for path, since in held.items(): grp.setdefault(path.split('/')[1] if path.count('/') > 1 else path, []).append((since, path))
    for kind, L in sorted(grp.items()):
        L.sort(); names = ', '.join(pathlib.Path(x[1]).name.split('.')[0] for x in L)
        pile(f'held-{kind}', '7 waiting room', f'HELD {kind} files (a check failed; data/waiting/today.md says why)', len(L), 'chat 2 (fix) + chat 11',
             names[:160] + (' …' if len(names) > 160 else ''), L[0][0])
        P[-1]['since'] = L[0][0]                          # held: the age runs from the oldest held date, not from our first look
    gq = open('data/status/grade-queue.md').read() if os.path.exists('data/status/grade-queue.md') else ''
    gn = len(re.findall(r'^- \*\*', gq, re.M))
    pile('grade-queue', '7 waiting room', 'files waiting for a grader (data/status/grade-queue.md)', gn, 'chat 11', '', changed('data/status/grade-queue.md'))

    # ---- 8. BOTS: red, or not run for a week
    for k, v in sorted(board.items()):
        if k.startswith('Intake:'): continue
        lr = v.get('last_run') or ''
        try: age = (TODAY - dt.date.fromisoformat(lr[:10])).days
        except ValueError: age = 99
        res = v.get('result')
        if res in ('red', 'amber') or age > 7:
            wo = v.get('waiting_on') or ''
            if res == 'amber':                             # the bot works; it found work for a chat (owner from its own line)
                owner = ' + '.join(dict.fromkeys(re.findall(r'chat \d+|HQ|Brandon', wo))) or 'HQ'
                what = f'{k}: found work'
            else:
                owner, what = 'chat 10', f"{k}: {'RED (the bot is broken)' if res == 'red' else 'not run for ' + str(age) + ' days'}"
            pile(f'bot-{k}', '8 bots', what, 1, owner, (v.get('made') or '')[:100] + (' · ' + wo[:90] if wo else ''), lr[:10] or None)

    # ---- moved / stuck (history kept between runs)
    prev = {p['id']: p for p in ((load(OUT_J, {}) or {}).get('piles') or [])}
    for p in P:
        o = prev.get(p['id'])
        p['first_seen'] = (o or {}).get('first_seen') or TODAY.isoformat()
        if p.get('since'): p['moved'] = p['since']                             # held files: their own held date
        elif o is None: p['moved'] = p['date'] or TODAY.isoformat()            # first look: the date its file last changed
        elif o.get('n') != p['n']: p['moved'] = TODAY.isoformat()              # work came in or went out
        else: p['moved'] = o.get('moved') or TODAY.isoformat()                 # same count: a rewritten file is not a move
        still = (TODAY - dt.date.fromisoformat(p['moved'])).days
        p['still_days'] = still
        p['stuck'] = p['n'] > 0 and still >= STUCK_DAYS and 'information' not in p['note']
        if p['id'] == 'engine-finds' and p.get('engine_saved') and (TODAY - dt.date.fromisoformat(p['engine_saved'])).days >= 1: p['stuck'] = True
    json.dump({'about': __doc__.split('\n')[0], 'built': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'), 'stuck_days': STUCK_DAYS, 'piles': P},
              open(OUT_J, 'w'), indent=1, ensure_ascii=False)

    # ---- flow.md
    L = [f"# Flow board ({dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ')}, kpc_flow.py)",
         f"Every pile of work, who it waits on and when it last moved. STUCK = work in it and no move for {STUCK_DAYS}+ days. Fix the STUCK ones first.", '']
    st = [p for p in P if p['stuck']]
    L += [f'## STUCK ({len(st)})'] + ([f"- STUCK {p['still_days']} d · **{p['n']:,}** · {p['what']} · waits on **{p['owner']}**" + (f" · {p['note']}" if p['note'] else '')
                                         for p in sorted(st, key=lambda p: -p['still_days'])] or ['- nothing stuck']) + ['']
    L += ['## Waiting on each chat (open work, oldest first)']
    by = {}
    for p in P:
        if p['n'] > 0 and 'information' not in p['note']:
            for c in re.findall(r'chat \d+', p['owner']) or ['bots']: by.setdefault(c, []).append(p)
    for c in sorted(by, key=lambda c: (c == 'bots', int(re.sub(r'\D', '', c) or 99))):
        L.append(f'### {c}')
        L += [f"- {'STUCK ' if p['stuck'] else ''}{p['n']:,} · {p['what']} · since {p['moved']}" for p in sorted(by[c], key=lambda p: p['moved'])]
    L += ['', '## The whole line', '| stage | pile | count | waits on | last moved |', '|---|---|---|---|---|']
    L += [f"| {p['stage']} | {p['what']} | {p['n']:,} | {p['owner']} | {p['moved']}{' **STUCK**' if p['stuck'] else ''} |" for p in sorted(P, key=lambda p: p['stage'])]
    OUT_M.write_text('\n'.join(L) + '\n')
    print(f"::notice title=Flow board::{len(P)} piles, {len(st)} stuck: " + '; '.join(f"{p['n']} {p['what'][:40]} ({p['owner']})" for p in st[:5]))


if __name__ == "__main__":
    main()
