#!/usr/bin/env python3
"""WORKSHOP DRIVER (Fable, chat 10 'bot workshop', Oct 28 2026 ~5 AM). ONE job runs the workshop bots ONE AT A TIME, area by
area, so no agency host ever sees two of our bots at once (fw.ky.gov answered 403 on Oct 28 after the truth checker, the hours
bot and the campground bot read it in the same hour). Order per area: truth checker -> hours / fees / permits -> campground
info. After each bot-and-area batch: the status lines (kpc_status.py: a 'grade me' line for chat 8 + the board) and ONE save.

Env: BOTS ('truth hours campinfo'; any subset, in that order) · AREAS ('US-KY US-TN'; blank = the next unfinished areas in the
     2-fer region order, judged per bot) · MINUTES (whole job budget, default 300 = 5 chunks of 55) · CHUNK (per bot call,
     default 55) · TEST=1 (Kentucky gates: the bots' own 'TEST=' lines; prints GATE=PASS only when every gated bot passed)
     · LINKS · PUSH=0 (no saves: local tests) · the bots' own secrets pass through the environment.
Never fails (exit 0). Prints 'LEFT=<n>' (areas still unfinished for any requested bot) and 'GATE=PASS|FAIL|NONE'."""
import json, os, pathlib, subprocess, sys, time

T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 300) * 60
CHUNK = float(os.environ.get('CHUNK') or 55)
BOTS = (os.environ.get('BOTS') or 'truth hours campinfo').split()
TEST = os.environ.get('TEST') == '1'
PUSH = os.environ.get('PUSH', '1') != '0'
LINKS = os.environ.get('LINKS') or '../links'
SCRIPT = {'truth': '.github/scripts/kpc_truth_bot.py', 'hours': '.github/scripts/kpc_hours_bot.py', 'campinfo': '.github/scripts/kpc_campinfo_bot.py'}
FOLDER = {'truth': 'data/truth', 'hours': 'data/hours', 'campinfo': 'data/campinfo'}
NAME = {'truth': 'park truth checker', 'hours': 'hours fees permits bot', 'campinfo': 'campground info bot'}
GATED = {'truth', 'hours'}
sys.path.insert(0, '.github/scripts')
from kpc_truth_bot import QUEUE  # noqa: E402


def notice(m): print('::notice title=Workshop::' + str(m).replace('\n', ' ')[:900], flush=True)
def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001
def status_of(bot, area): return ((load(f'{FOLDER[bot]}/state.json', {}).get('areas') or {}).get(area) or {}).get('status')
def left_areas(): return [a for a in QUEUE if any(status_of(b, a) != 'done' for b in BOTS if b in SCRIPT)]


def run_bot(bot, area, minutes, test):
    env = dict(os.environ, AREAS=area, MINUTES=str(minutes), LINKS=LINKS, TEST='1' if test else '0')
    notice(f'{NAME[bot]}: {area} ({minutes:.0f} min)')
    p = subprocess.run([sys.executable, SCRIPT[bot]], env=env, capture_output=True, text=True)
    out = (p.stdout or '') + (p.stderr or '')
    for line in out.splitlines():
        if line.startswith('::notice'): print(line, flush=True)
    res = 'PASS' if 'TEST=PASS' in out else 'FAIL' if 'TEST=FAIL' in out else ''
    if test and bot in GATED and res == 'PASS':   # the bot's own gate passed: remember it (the weekly cron reads 'proven')
        sp = pathlib.Path(f'{FOLDER[bot]}/state.json'); s = load(sp, {}); s['proven'] = time.strftime('%Y-%m-%d'); sp.write_text(json.dumps(s, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    st = status_of(bot, area)
    counts = (((load(f'{FOLDER[bot]}/state.json', {}).get('areas') or {}).get(area) or {}).get('counts')) or {}
    subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'grade-me', NAME[bot], area, f'{FOLDER[bot]}/{area}.json + review.md', f'{st}; {json.dumps(counts)[:160]}'])
    subprocess.run([sys.executable, '.github/scripts/kpc_status.py', 'board', NAME[bot], 'green' if p.returncode == 0 else 'red', f'{area}: {st}; {json.dumps(counts)[:200]}', 'chat 8 grades the sample; Brandon GO before any card', f'left: {len(left_areas())}'])
    if PUSH:
        subprocess.run(['bash', f'{LINKS}/.github/scripts/kpc_push_data.sh', '.', f'{NAME[bot]}: {area} ({st})', FOLDER[bot], 'data/status'])
    return res


def main():
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in QUEUE] if want else left_areas()
    gates = {}
    for area in areas:
        for bot in BOTS:
            if bot not in SCRIPT: continue
            remaining = (LIMIT - (time.time() - T0)) / 60
            if remaining < 3: break
            if not want and status_of(bot, area) == 'done': continue
            while True:
                remaining = (LIMIT - (time.time() - T0)) / 60
                if remaining < 3: break
                res = run_bot(bot, area, min(CHUNK, remaining), TEST and area == 'US-KY')
                if res: gates[bot] = res
                if status_of(bot, area) == 'done' or want: break   # named areas: one pass each, no loops
    left = len(left_areas())
    gate = 'NONE' if not gates else ('PASS' if all(v == 'PASS' for b, v in gates.items() if b in GATED) else 'FAIL')
    notice(f'workshop done: gates {gates} · areas left {left}')
    print(f'LEFT={left}'); print(f'GATE={gate}')


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc(); notice(f'workshop stopped: {e}'); print('LEFT=1'); print('GATE=NONE')
    sys.exit(0)
