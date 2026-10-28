#!/usr/bin/env python3
"""STATUS HELPER (Fable, chat 10 'bot workshop', Oct 28 2026; HQ's AUTOMATION item). Two small things every bot can call after
a batch lands, so people do not have to look:
  grade-me  appends ONE line per batch to KPC-Data data/status/inbox-chat-8.md (chat 8's bot inbox; never KPC-Links, because
            a push there rebuilds the site): '- FROM BOT <bot> (<date>): grade me: <areas> <file>'. Duplicate lines (same bot,
            areas and file on the same day) are not written twice.
  board     updates data/status/board.json: per bot its last run (date + run link), green / red, what it made, what is waiting
            on whom; the members-only status page (later) reads this file.
Both never fail (exit 0 always) and write nothing when nothing changed; the calling workflow's normal save step pushes
data/status with the rest (add data/status to its kpc_push_data.sh paths).

  python3 kpc_status.py grade-me <bot> "<areas>" "<file or folder>" ["<note>"]
  python3 kpc_status.py board <bot> <green|red> "<what it made>" "<waiting on whom>" ["<areas done / left>"]
  python3 kpc_status.py sample <bot> <area> <file> [n]      -> prints the sample file path (random 12, seeded by date + area)
  python3 kpc_status.py gate <bot> <area> FAIL "<why>"       -> the FAILED line (self-grading gates, HQ item A)
"""
import json, os, pathlib, sys, time

STATUS = pathlib.Path(os.environ.get('STATUS_DIR') or 'data/status')
INBOX = STATUS / 'inbox-checkers.md'   # Oct 28 (HQ A): chat 11 grades bot output now; chat 8 keeps 2-fers / rules
BOARD = STATUS / 'board.json'
TODAY = time.strftime('%Y-%m-%d')
HEAD = ('# BOT INBOX FOR THE CHECKERS (KPC-Data; written by the bots, read by chat 11 (bot output) and chat 8 (2-fers, rules); HQ tidies)\n'
        'Bots append one line per batch: "grade me" = a passed self-gate + a 10-12 record random sample to grade (data/status/samples/); '
        '"FAILED its gate" = the batch is marked failed, never queued onward, with the reasons. The checker writes fixes to the owning chat\'s inbox in KPC-Links (.claude/inbox/chat-N.md). Lines are never deleted by bots; strike them through when graded.\n\n')


def run_link():
    rep = os.environ.get('GITHUB_REPOSITORY'); rid = os.environ.get('GITHUB_RUN_ID')
    return f'https://github.com/{rep}/actions/runs/{rid}' if rep and rid else ''


def grade_me(bot, areas, file, note=''):
    STATUS.mkdir(parents=True, exist_ok=True)
    old = INBOX.read_text(encoding='utf-8') if INBOX.exists() else HEAD
    line = f"- FROM BOT {bot} ({TODAY}): grade me: {areas} {file}" + (f" — {note}" if note else '') + (f" · [run]({run_link()})" if run_link() else '')
    key = line.split(' · [run]')[0]
    if key in old: print('status: grade-me line already there'); return
    INBOX.write_text(old.rstrip('\n') + '\n' + line + '\n', encoding='utf-8')
    print('status: grade-me line added')


def sample(bot, area, file, n=12):
    """A random 10-12 record sample of an area file (seeded by date + area, so a checker and the bot see the same rows) ->
    data/status/samples/<bot>-<area>-<date>.md; returns its path or ''."""
    import random
    try: d = json.load(open(file, encoding='utf-8'))
    except Exception: return ''  # noqa: BLE001
    recs = d.get('parks') or d.get('camps') or d.get('records') or {}
    if isinstance(recs, dict): items = [(k, v) for k, v in recs.items() if isinstance(v, dict) and ((v.get('verdict') not in (None, 'no outline', 'not read', 'no official page on file')) or v.get('status') == 'ok' or v.get('hours') or v.get('fees') or v.get('permits') or v.get('sites'))]
    else: items = [(str(i), v) for i, v in enumerate(recs)]
    if not items: return ''
    rnd = random.Random(f'{TODAY}{area}{bot}'); rnd.shuffle(items)
    picks = items[:n]
    out = STATUS / 'samples' / f"{bot.replace(' ', '-')}-{area}-{TODAY}.md"; out.parent.mkdir(parents=True, exist_ok=True)
    L = [f'# {bot}: {area} random sample of {len(picks)} ({TODAY}; seed = date + area, same rows for everyone)', '', f'Source file: `{file}`', '']
    for k, v in picks:
        short = {kk: vv for kk, vv in v.items() if kk not in ('pages', 'sizes', 'score_parts', 'facts_src', 'ver')}
        L.append(f'## {k} {v.get("n") or v.get("name") or ""}'); L.append('```json'); L.append(json.dumps(short, ensure_ascii=False, indent=1)[:2500]); L.append('```'); L.append('')
    out.write_text('\n'.join(L), encoding='utf-8')
    return str(out)


def gate(bot, area, result, why):
    """A batch that FAILED its self-gate: one line with the reasons (never queued onward: the driver marks the area 'failed')."""
    STATUS.mkdir(parents=True, exist_ok=True)
    old = INBOX.read_text(encoding='utf-8') if INBOX.exists() else HEAD
    line = f"- FROM BOT {bot} ({TODAY}): FAILED its gate: {area} — {why[:400]}" + (f" · [run]({run_link()})" if run_link() else '')
    if line.split(' · [run]')[0] in old: return
    INBOX.write_text(old.rstrip('\n') + '\n' + line + '\n', encoding='utf-8'); print('status: gate FAIL line added')


def board(bot, result, made, waiting, areas=''):
    STATUS.mkdir(parents=True, exist_ok=True)
    try: b = json.load(open(BOARD, encoding='utf-8'))
    except Exception: b = {'about': 'KPC bot status board: per bot the last run, green / red, what it made, what is waiting on whom. Written by kpc_status.py from each workflow; a members-only page reads it later.', 'bots': {}}  # noqa: BLE001
    b['bots'][bot] = {'last_run': TODAY, 'run': run_link(), 'result': 'green' if result.lower().startswith('g') else 'red', 'made': made[:300], 'waiting_on': waiting[:200], 'areas': areas[:300]}
    b['updated'] = TODAY
    BOARD.write_text(json.dumps(b, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(f'status: board updated for {bot}')


if __name__ == '__main__':
    try:
        a = sys.argv[1:]
        if a and a[0] == 'grade-me' and len(a) >= 4: grade_me(a[1], a[2], a[3], a[4] if len(a) > 4 else '')
        elif a and a[0] == 'board' and len(a) >= 5: board(a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else '')
        elif a and a[0] == 'sample' and len(a) >= 4: print(sample(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 12))
        elif a and a[0] == 'gate' and len(a) >= 5: gate(a[1], a[2], a[3], a[4])
        else: print('usage: kpc_status.py grade-me <bot> <areas> <file> [note] | board <bot> <green|red> <made> <waiting> [areas]')
    except Exception as e:  # noqa: BLE001
        print('status helper: ' + str(e)[:200])
    sys.exit(0)
