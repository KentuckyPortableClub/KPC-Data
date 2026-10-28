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
"""
import json, os, pathlib, sys, time

STATUS = pathlib.Path(os.environ.get('STATUS_DIR') or 'data/status')
INBOX = STATUS / 'inbox-chat-8.md'
BOARD = STATUS / 'board.json'
TODAY = time.strftime('%Y-%m-%d')
HEAD = ('# BOT INBOX FOR CHAT 8 (KPC-Data; written by the bots, read by chat 8; HQ tidies)\n'
        'Bots append one line per batch that landed: "grade me" = chat 8 grades a sample of that area/file and writes its fixes '
        'to the owning chat\'s inbox in KPC-Links (.claude/inbox/chat-N.md). Lines are never deleted by bots; chat 8 strikes them through when graded.\n\n')


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
        else: print('usage: kpc_status.py grade-me <bot> <areas> <file> [note] | board <bot> <green|red> <made> <waiting> [areas]')
    except Exception as e:  # noqa: BLE001
        print('status helper: ' + str(e)[:200])
    sys.exit(0)
