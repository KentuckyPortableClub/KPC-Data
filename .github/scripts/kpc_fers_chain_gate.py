#!/usr/bin/env python3
"""2-FER CHAIN MAP-AUDIT GATE: its state and the AUTOMATIC RE-ENABLE (Nov 4 2026; per Brandon via Super Head Bot (relayed), 5:48 AM
CST Nov 4: "Map gate audit off by default for testing purposes once we see the system is working it goes back on automatically.").

The gate (kpc_fers_chain_plan.py) starts OFF (GATE_DEFAULT there). It turns ON by itself, once, and then STAYS ON, after EITHER
  A) the first sign-off by a person (Brandon / KZ4CP: kpc_key_freeze.is_person; a Quality note, Super, a bot or old chat 11 text never
     counts) saying a 2-fer run is GOOD, dated on or after FLIP_SINCE; read from
       data/status/fers-chain/verdicts/*.json   {"run": "<run link or tag>", "verdict": "GOOD|YES|PASS|OK", "by": "Brandon", "date": "..."}
       data/waiting/approved.json items whose 'what' starts with 'fers-' and whose 'verdict' is such a sign-off
     (a NO / FAIL / WITHDRAWN never flips it), OR
  B) STREAK_N (3) CLEAN CHECKS IN A ROW: each new 2-fer post-line report (data/status/fers-postline/latest.json, counted once per
     run, and only when the held 2-fer output changed since the last counted check: held_fp()) is clean AND the links-01 post-key check of every key it touches (KPC-Links data/status/key-check/last-<us|ca>.json and
     its report) is clean. A report that is not clean puts the count back to 0. A report with no held area does not count.
     Why 3: one clean run can be luck (a quiet area); three in a row is the smallest count that is still a pattern, it is about one
     full chain start (at most 3 areas a start), and a single bad run sets it back to 0, so it errs on the side of a longer test.
'Clean' is spelled out in postline_clean() / POSTKEY_MUST_BE_ZERO below. Nov 6: '0,0 / impossible pins' counts only NEW / no-outline rows by default (Brandon ruling 4:17 PM CST Nov 5, relayed via Super: old POTA 0,0 pins must not block); KPC_GATE_COUNT_OLD_00=on restores old must-be-zero.
State: data/status/fers-chain/gate.json (tracked; saved by kpc-fers-chain.yml and kpc-fers-postline.yml)
  {"mode": "off"|"on", "since", "why", "streak", "need": 3, "counted": [run ids], "last_check": {...}, "history": [lines]}
On a flip one STATUS LINE is added to gate.json 'history' and to data/status/fers-chain/gate-log.md, and printed as a notice.
Once 'on' no bot ever writes 'off'. Turning it off again is BY HAND only: Brandon sets the repo variable KPC_FERS_CHAIN_GATE=off
(it always wins over this file). The gate only decides which areas START a 2-fer line; the 2-fer output stays HELD either way and
nothing here releases anything. No cron: it runs inside the workflow_run chain.
  update            (DATA=. LINKS=links) works out the state now, saves gate.json when it changed, prints changed=yes|no
  effective <var>   prints the gate mode the plan would use"""
import datetime, glob, json, os, pathlib, re, sys, time

STREAK_N = 3   # clean post-key + post-line checks in a row that turn the gate on (see 'Why 3' above)
FLIP_SINCE = datetime.datetime(2026, 11, 4, 6, 0, tzinfo=datetime.timezone.utc)   # 00:00 CST Nov 4: older sign-offs predate this chain
GOOD_RE = r'\W*(YES|GOOD|PASS|OK|APPROVED?)\b'
NO_RE = r'\W*(NO|FAIL|WITHDRAWN|NOT\s+GOOD)\b'
POSTKEY_MUST_BE_ZERO = ('0,0 / impossible pins', 'signed sheet answers not followed', 'overrides not followed, dated before the build (a real miss)',
                        'must-be-pin not yet pin')
ON_WORDS, OFF_WORDS = ('on', 'audit', 'yes', 'true'), ('off', 'no', 'false')
STATE = 'data/status/fers-chain/gate.json'
LOG = 'data/status/fers-chain/gate-log.md'


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def _kf(links):
    sys.path.insert(0, str(pathlib.Path(links) / '.github/scripts'))
    import kpc_key_freeze as KF
    return KF


def state(data):
    s = load(pathlib.Path(data) / STATE, {}) or {}
    if not isinstance(s, dict): s = {}
    s.setdefault('mode', 'off'); s.setdefault('streak', 0); s.setdefault('need', STREAK_N); s.setdefault('counted', []); s.setdefault('history', [])
    return s


def effective(var, data, default):
    """(mode, source). The repo variable set by hand always wins (Brandon's off); then gate.json 'on'; then GATE_DEFAULT."""
    v = str(var or '').strip().lower()
    if v in OFF_WORDS: return 'off', 'repo variable KPC_FERS_CHAIN_GATE (set by hand)'
    if v in ON_WORDS: return 'on', 'repo variable KPC_FERS_CHAIN_GATE (set by hand)'
    if v: return 'PENDING', f'repo variable KPC_FERS_CHAIN_GATE={v!r} is not on/off'
    if state(data).get('mode') == 'on': return 'on', f'turned on by itself ({STATE})'
    d = str(default or '').strip().lower()
    return ('on' if d in ON_WORDS else 'off' if d in OFF_WORDS else 'PENDING'), 'GATE_DEFAULT in kpc_fers_chain_plan.py'


def person_good(data, links, now=None):
    """(why) of the first person's GOOD sign-off on a 2-fer run, or ''"""
    KF = _kf(links); now = now or datetime.datetime.now(datetime.timezone.utc)
    recs = [(r, os.path.basename(f)) for f in sorted(glob.glob(str(pathlib.Path(data) / 'data/status/fers-chain/verdicts/*.json'))) for r in [load(f)] if isinstance(r, dict)]
    recs += [(it, 'approved.json ' + str(it.get('what'))) for it in (load(pathlib.Path(data) / 'data/waiting/approved.json', {}) or {}).get('items') or []
             if isinstance(it, dict) and str(it.get('what') or '').startswith('fers-')]
    for r, where in recs:
        txt = str(r.get('verdict') or '').strip().upper()
        if not txt or re.match(NO_RE, txt) or not re.match(GOOD_RE, txt): continue
        if KF.signoff_why(r, now): continue
        w = KF.signed_when(r)
        if w is None or w < FLIP_SINCE: continue
        return f"{r.get('by')} graded a 2-fer run good ({where}: {str(r.get('verdict'))[:40]}, {r.get('date') or r.get('signed') or ''})"
    return ''


def postline_clean(rep):
    """(counts, clean, why). counts=False: no new held 2-fer output in the report (not counted either way)."""
    if not isinstance(rep, dict): return False, False, 'no post-line report'
    if rep.get('error'): return True, False, f"post-line check error: {str(rep['error'])[:80]}"
    areas = rep.get('areas') or {}
    if not areas: return False, False, 'the report compared no held area'
    bad = []
    for a, r in areas.items():
        if 'error' in r: bad.append(f'{a}: could not compare'); continue
        if r.get('stale_inputs'): bad.append(f"{a}: stale inputs ({'; '.join(r['stale_inputs'])[:80]})")
        if (r.get('preline') or {}).get('verdict') != 'GO': bad.append(f"{a}: pre-line not GO")
        if r.get('touch_held'): bad.append(f"{a}: {len(r['touch_held'])} live pair(s) on held key parks")
    return True, not bad, '; '.join(bad[:4]) or 'post-line clean'


# Nov 6 (Brandon ruling 4:17 PM CST Nov 5, relayed via Super): old POTA 0,0 / impossible pins are known POTA mistakes and
# must NOT block the gate. DEFAULT counts only NEW bad pins (summary 'pins outside, new or changed this build' style), or
# ones with no outline. Flag KPC_GATE_COUNT_OLD_00=on restores the old "must be zero" behaviour.
GATE_COUNT_OLD_00 = (os.environ.get('KPC_GATE_COUNT_OLD_00') or '').strip().lower() in ('on', 'yes', 'true', '1')


def postkey_clean(links, short):
    d = pathlib.Path(links) / 'data/status/key-check'
    last = load(d / f'last-{short}.json', {}) or {}
    rep = load(d / str(last.get('report') or 'none'), None)
    if not isinstance(rep, dict): return False, f'{short}: no post-key check report'
    s = rep.get('summary') or {}
    bad = []
    for k in POSTKEY_MUST_BE_ZERO:
        n = s.get(k) or 0
        if not n: continue
        if k == '0,0 / impossible pins' and not GATE_COUNT_OLD_00:
            # Default (Brandon 4:17 PM CST Nov 5): only NEW bad pins, or ones with no outline, block.
            new_n = _new_bad_pins(rep)
            if new_n: bad.append(f'{k} {new_n} new/no-outline (of {n} standing; old POTA mistakes do not block)')
            continue
        bad.append(f'{k} {n}')
    if any('did not read as JSON' in str(n) for n in rep.get('notes') or []): bad.append('key files not readable')
    return not bad, f"{short} {rep.get('build')}: " + ('; '.join(bad) if bad else 'post-key clean')


def _new_bad_pins(rep):
    """Count of 0,0 / impossible pins that are NEW this build or have no outline.
    Standing POTA mistakes with an explicit outline='yes' (and not new/changed) do not count.
    Part A v2 (Quality): FAIL CLOSED on any error or missing data — never return 0 when we cannot
    tell standing from new (empty bad_pins but summary>0; rows without classify fields; exceptions)."""
    try:
        summary_n = int((rep.get('summary') or {}).get('0,0 / impossible pins') or 0)
        rows = rep.get('bad_pins')
        if rows is None:
            return max(summary_n, 1) if summary_n or GATE_COUNT_OLD_00 else 1  # missing list -> closed
        if not isinstance(rows, list):
            return max(summary_n, 1)
        if not rows:
            # empty list: if summary still reports pins, fail closed (cannot verify standing)
            return summary_n
        # Schema incomplete (no new/changed/outline on any row) -> cannot exempt standing; count all
        has_schema = any(isinstance(x, dict) and ('new' in x or 'changed' in x or 'outline' in x) for x in rows)
        if not has_schema:
            return len(rows)
        n = 0
        for x in rows:
            if not isinstance(x, dict):
                n += 1; continue  # malformed row -> closed
            if x.get('new') or x.get('changed'):
                n += 1; continue
            if 'outline' not in x:
                n += 1; continue  # missing outline field -> closed
            if str(x.get('outline') or '').lower() in ('no', 'none', ''):
                n += 1
            # outline='yes' and not new/changed: standing, skip
        return n
    except Exception:
        return 10 ** 9  # fail closed


def _flip(s, data, why, now):
    t = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))
    line = (f'{t}: 2-fer chain map-audit gate turned ON by itself: {why}. It stays on; only Brandon turns it off by hand '
            f'(repo variable KPC_FERS_CHAIN_GATE=off). The 2-fers stay held either way.')
    s.update(mode='on', since=t, why=why); s['history'] = (s.get('history') or []) + [line]
    f = pathlib.Path(data) / LOG; f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, 'a', encoding='utf-8') as o:
        if f.stat().st_size == 0: o.write('# 2-fer chain map-audit gate: status lines (per Brandon via Super Head Bot (relayed), 5:48 AM CST Nov 4)\n\n')
        o.write(f'- {line}\n')
    print(f'::notice title=2-fer chain gate::{line}')
    return line


def held_fp(data):
    """FINAL-v2 self-check: a fingerprint of the HELD 2-fer output (data/waiting/in/data/fers/*.json[.gz]: names + bytes), '' when none.
    The post-line check runs after EVERY chain completion (the chain runs after every hourly copy, most of them start nothing), so
    one unchanged held output is re-checked every hour under a new run link. A check counts only when the held output changed since
    the last counted one: 3 clean checks in a row = 3 different 2-fer outputs, never one output seen three times."""
    import hashlib
    h, n = hashlib.sha256(), 0
    for f in sorted(glob.glob(str(pathlib.Path(data) / 'data/waiting/in/data/fers/*.json*'))):
        try: b = open(f, 'rb').read()
        except OSError: continue
        h.update(os.path.basename(f).encode() + b'\0' + hashlib.sha256(b).digest()); n += 1
    return h.hexdigest()[:16] if n else ''


def update(data='.', links='links', now=None):
    """-> (state, changed). Never turns the gate off."""
    now = now if now is not None else time.time()
    nowdt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
    s = state(data); before = json.dumps(s, sort_keys=True)
    if s['mode'] != 'on':
        s['mode'] = 'off'
        rep = load(pathlib.Path(data) / 'data/status/fers-postline/latest.json')
        rid = str((rep or {}).get('run') or (rep or {}).get('checked') or '')
        fp = held_fp(data)
        if rid and rid not in s['counted'] and fp and fp != s.get('last_fp'):   # FINAL-v2 self-check: only a NEW held output counts
            counts, ok, why = postline_clean(rep)
            if counts:
                s['last_fp'] = fp
                keys = sorted({'ca' if a.startswith('CA-') else 'us' for a in (rep.get('areas') or {}) if a[:3] in ('US-', 'CA-')})
                pk = [postkey_clean(links, k) for k in keys] or [(False, 'no US / Canada area')]
                ok = ok and all(c for c, _ in pk)
                s['streak'] = s['streak'] + 1 if ok else 0
                s['counted'] = (s['counted'] + [rid])[-50:]
                s['last_check'] = {'run': rid, 'clean': ok, 'why': why + ' | ' + ' | '.join(w for _, w in pk),
                                   'at': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}
        s['need'] = STREAK_N
        pg = person_good(data, links, nowdt)
        if pg: _flip(s, data, pg, now)
        elif s['streak'] >= STREAK_N: _flip(s, data, f"{s['streak']} clean post-key + 2-fer post-line checks in a row (last: {s['last_check']['run']})", now)
    changed = json.dumps(s, sort_keys=True) != before
    if changed:
        f = pathlib.Path(data) / STATE; f.parent.mkdir(parents=True, exist_ok=True)
        json.dump(s, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return s, changed


if __name__ == '__main__':
    a = sys.argv[1:]
    try:
        if a[:1] == ['update']:
            s, ch = update(os.environ.get('DATA') or '.', os.environ.get('LINKS') or 'links')
            print(f"::notice title=2-fer chain gate::gate {s['mode']}; clean checks in a row {s['streak']}/{STREAK_N}" + (f"; last: {s.get('last_check', {}).get('why', '')[:200]}" if s.get('last_check') else ''))
            if os.environ.get('GITHUB_OUTPUT'):
                with open(os.environ['GITHUB_OUTPUT'], 'a') as o: o.write(f"changed={'yes' if ch else 'no'}\n")
        elif a[:1] == ['effective']:
            sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import kpc_fers_chain_plan as P
            print(*effective(a[1] if len(a) > 1 else '', os.environ.get('DATA') or '.', P.GATE_DEFAULT))
        else: print(__doc__)
    except Exception as e:  # noqa: BLE001
        print(f'::warning title=2-fer chain gate::stopped ({str(e)[:200]}): the gate stays as it was')
    sys.exit(0)
