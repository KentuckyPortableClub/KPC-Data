#!/usr/bin/env python3
"""2-FER CHAIN PLAN (Nov 4 2026; the chain: per Brandon via Super Head Bot (relayed), 4:55 AM CST Nov 4, his words: "I think it is done set up for this but if not make sure once mapping new pr with 2fer fixes is pushed that the 2fer line will start automatically running the new system that way next time we can evaluate both new systems"; what Mapping built from it: after the merge the whole
chain runs by itself, no new cron: US key build -> post-key check (links-01) -> 2-fer pre-line check -> 2-fer line -> 2-fer post-line
check; the pre- and post-line bots: Brandon, directly (Mapping chat), 4:52 AM CST Nov 4: "2fer line review? Plan and install any
pre and post line bots for the 2fer system."). The 2-fers stay HELD until a person grades them. Run by kpc-fers-chain.yml
(workflow_run on the hourly copy). Decides which 2-fer areas get a line on a NEW key build. Starts nothing itself, releases nothing:
it prints the area list for the workflow's matrix.

An area of a key runs once per key build, when ALL hold:
  * KPC-Links' build of that key is a FULL build on the CURRENT rules (index 'rules' == kpc_key_freeze.rules_hash: links-04)
  * the links-01 post-key check ran on that build (KPC-Links data/status/key-check/last-<us|ca>.json names it)
  * the build has come over to KPC-Data (data/waiting/in/data/<key>/index.json or data/<key>/index.json carries its id)
  * nobody graded the build NO / FAIL / WITHDRAWN (kpc_key_freeze.graded_no: a person, Quality or old chat 11; a NO only holds)
  * the CHAIN GATE = the repo variable KPC_FERS_CHAIN_GATE when set BY HAND (always wins: Brandon's off), else 'on' once it turned
    on by itself (data/status/fers-chain/gate.json, kpc_fers_chain_gate.py: the first Brandon / KZ4CP sign-off that a 2-fer run
    is good, or 3 clean post-key + 2-fer post-line checks in a row; then it stays on), else GATE_DEFAULT below = 'off' (per Brandon
    via Super Head Bot (relayed), 5:48 AM CST Nov 4: "Map gate audit off by default for testing purposes once we see the system
    is working it goes back on automatically."):
      on       every state of the area has a CLEAN MAP AUDIT (audit_clean below): data/status/audited.json lists it (a stamp
               from the Nov 2 fixes on) and none of its map-audit rows is open, answered NO or only by a pattern, or source down.
               FINAL-v2 (Quality, NOT YET on data-05): this is the map audit ONLY. It no longer reads fers-ready.json, whose
               'waiting for key' is set exactly while the key build that just finished sits HELD in data/waiting/in - the moment
               the chain runs - so the chain could never start. The key itself is checked by the four points above.
      off      the map audit is not checked (the four key checks above still apply)
      PENDING  a repo variable that is neither on nor off (a typo): the plan works out BOTH answers and reports them, and STARTS
               NOTHING (the safe direction). ('audit' = the old name for 'on'.)
    Either way the 2-fer output stays HELD in the waiting room until a person grades it; the gate only decides what STARTS.
At most MAX (3) areas per start; the rest come on the next hourly copy. Kentucky (its own key) is never in the chain.
CA and world finishing later: each key's 2-fers wait for THAT key's own new build (the US areas do not wait for Canada); inside a
line the other keys are the live (last good) ones. Nov 8: the world key has its own areas (worldwest/north/east, W-* countries).
Remembered in data/status/fers-chain/seen.json {key: {build, ran: [tags], waiting: {tag: why}}}; while PENDING both answers are
printed as notices in the run log (nothing is saved: nothing started). The gate state: data/status/fers-chain/gate.json.
env  DATA=. LINKS=links GATE=<repo variable: on|off|empty> MAX=3 GITHUB_OUTPUT (writes run, areas, gate_changed)"""
import json, os, pathlib, re, sys, time

R = {'southeast': 'US-TN US-NC US-VA US-WV US-GA US-AL US-SC US-FL US-MS', 'midwest': 'US-IN US-IL US-MO US-WI US-MN US-IA US-ND US-SD',
     'northeast': 'US-PA US-NY US-NJ US-CT US-RI US-MA US-VT US-NH US-ME US-MD US-DE US-DC', 'southcentral': 'US-AR US-LA US-OK US-TX US-KS US-NE',
     'mountain': 'US-CO US-WY US-ID US-MT US-NV US-AZ US-NM', 'pacific': 'US-CA US-OR US-WA US-AK US-HI',
     'oh': 'US-OH', 'mi': 'US-MI', 'ut': 'US-UT',
     'canadaeast': 'CA-ON CA-QC CA-NB CA-NS CA-PE CA-NL', 'canadawest': 'CA-MB CA-SK CA-AB CA-BC CA-YT CA-NT CA-NU',   # = kpc-fers-pending.yml's areas
     # Nov 8 (Brandon: 'if quality approves something it is good to run'): the world key's 2-fer areas (the W-* countries in data/fers)
     'worldwest': 'W-GB W-IE W-FR W-ES W-PT W-BE W-NL W-LU W-DE W-CH',
     'worldnorth': 'W-AT W-IT W-DK W-NO W-SE W-FI W-EE W-LV W-LT W-PL',
     'worldeast': 'W-CZ W-SK W-HU W-SI W-HR W-RO W-AU W-JP'}
KEYS = {'us-key': 'us', 'ca-key': 'ca', 'world-key': 'world'}
KIND_OF = lambda sts: 'ca-key' if sts.startswith('CA-') else 'world-key' if sts.startswith('W-') else 'us-key'   # an area's key
GATE_DEFAULT = 'off'   # <-- THE GATE DEFAULT (per Brandon via Super Head Bot (relayed), 5:48 AM CST Nov 4: off for testing; it turns on by itself: kpc_fers_chain_gate.py)


def load(p, d=None):
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from kpc_json_any import load_json_any
        return load_json_any(p)
    except Exception: return d  # noqa: BLE001


def _gate():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # this repo's own kpc_fers_chain_gate.py (the auto re-enable)
    import kpc_fers_chain_gate as CG
    return CG


def gate_mode(v, data=None):
    """the repo variable -> 'on' | 'off' | 'PENDING' (anything unknown = PENDING: starts nothing). Empty = gate.json 'on' when the
    gate turned on by itself (data given), else GATE_DEFAULT."""
    if data is None:
        v = str(v or '').strip() or GATE_DEFAULT
        v = v.lower()
        return 'on' if v in ('on', 'audit', 'yes', 'true') else 'off' if v in ('off', 'no', 'false') else 'PENDING'
    return _gate().effective(v, data, GATE_DEFAULT)[0]


def audit_clean(data):
    """{area: why-not} for every area whose map audit is NOT clean (missing = clean). Uses kpc_fers_gate's own row rules
    (row_clean / clean_answer, source-down rows) and its audited.json stamps; never the 'waiting for key' status."""
    data = pathlib.Path(data)
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # this repo's own kpc_fers_gate.py (its row rules)
    import kpc_fers_gate as G
    A = load(data / 'data/status/audited.json', {}) or {}
    Q = (load(data / 'data/waiting/questions/map-audit.json', {}) or {}).get('questions') or []
    down = {}
    for r in (load(data / 'data/waiting/questions/map-audit-auto.json', {}) or {}).get('rows') or []:
        if str(r.get('auto') or '').startswith('source down'): down[r.get('area')] = down.get(r.get('area'), 0) + 1
    bad = {}
    areas = {x for v in R.values() for x in v.split()}
    for a in areas:
        mine = [r for r in Q if r.get('area') == a]
        op = sum(1 for r in mine if not G.row_clean(r))
        if not isinstance(A.get(a), dict): bad[a] = 'not audited in this pass'
        elif op or down.get(a): bad[a] = f'{op} audit row(s) not clean' + (f', {down[a]} source down' if down.get(a) else '')
    return bad


def plan(data='.', links='links', gate='', mx=3, now=None):
    data, links = pathlib.Path(data), pathlib.Path(links)
    sys.path.insert(0, str(links / '.github/scripts'))
    try:
        import kpc_key_freeze as KF
        KF.rules_hash
    except Exception as e:  # noqa: BLE001
        return [], {}, [f'KPC-Links has no rules hash (links-04 not merged: {str(e)[:80]}): the chain waits']
    seen_f = data / 'data/status/fers-chain/seen.json'; seen = load(seen_f, {}) or {}
    gsrc = _gate().effective(gate, data, GATE_DEFAULT)[1]
    gate = gate_mode(gate, data)
    notclean = audit_clean(data) if gate != 'off' else {}
    run, notes = [], []
    would = {'on': [], 'off': []}   # PENDING: what each answer would start now (reported, not started)
    notes.append(f'map-audit gate {gate} ({gsrc}); the 2-fers stay held either way')
    if gate == 'PENDING': notes.append(f"KPC_FERS_CHAIN_GATE is PENDING ({gsrc}): the plan is reported, NOTHING starts")
    for kind, short in KEYS.items():
        li = load(links / f'data/{kind}/index.json', {}) or {}; bid = str(li.get('build') or '')
        cur = KF.rules_hash(kind, links)
        if not bid: notes.append(f'{kind}: no build stamp in KPC-Links'); continue
        if str(li.get('rules') or '') != cur: notes.append(f'{kind}: build {bid} is not a full build on the current rules ({li.get("rules") or "none"} vs {cur}): waits for the rebuild'); continue
        last = load(links / f'data/status/key-check/last-{short}.json', {}) or {}
        if str(last.get('build') or '') != bid: notes.append(f'{kind}: the post-key check (links-01) has not run on {bid} yet'); continue
        here = {str((load(data / f'data/waiting/in/data/{kind}/index.json', {}) or {}).get('build') or ''), str((load(data / f'data/{kind}/index.json', {}) or {}).get('build') or '')}
        if bid not in here: notes.append(f'{kind}: build {bid} has not come over to KPC-Data yet'); continue
        items = (load(data / 'data/waiting/approved.json', {}) or {}).get('items')
        gno = getattr(KF, 'graded_no', None)
        if gno: v = gno(kind, bid, items, links)
        else:   # links-04 from before FINAL-v2: its verdict() + the NO words
            v = KF.verdict(kind, bid, items, links); v = v if v and re.match(r'\W*(KEY\s+)?(NO|FAIL|WITHDRAWN)', v[0].upper()) else None
        if v: notes.append(f'{kind}: build {bid} was graded {v[0][:20]} by {v[1]}: no 2-fers on it'); continue
        s = seen.get(kind) or {}
        if s.get('build') != bid: s = {'build': bid, 'ran': [], 'waiting': {}, 'first_seen': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}
        s['waiting'] = {}
        for tag, sts in R.items():
            if KIND_OF(sts) != kind or tag in s['ran']: continue
            nr = [f'{x} ({notclean[x]})' for x in sts.split() if x in notclean]
            if gate == 'PENDING':
                (would['off'] if len(would['off']) < mx else []).append(tag)
                if not nr and len(would['on']) < mx: would['on'].append(tag)
                s['waiting'][tag] = 'KPC_FERS_CHAIN_GATE is PENDING (not on / off): nothing starts' + (f"; map audit not clean: {'; '.join(nr[:4])}" if nr else '; map audit clean'); continue
            if gate == 'on' and nr: s['waiting'][tag] = f"map audit not clean: {'; '.join(nr[:6])}"; continue
            if len(run) >= mx: s['waiting'][tag] = 'next start (at most 3 areas at a time)'; continue
            run.append({'states': sts, 'tag': tag, 'key': kind, 'build': bid}); s['ran'].append(tag)
        seen[kind] = s
        notes.append(f"{kind}: build {bid}: gate {gate}: {len([r for r in run if r['key'] == kind])} area(s) start now; waiting: {len(s['waiting'])}"
                     + (f"; if 'on': {' '.join(would['on']) or 'none'}; if 'off': {' '.join(would['off']) or 'none'}" if gate == 'PENDING' else ''))
        would = {'on': [], 'off': []}
    return run, seen, notes


def main(env=os.environ):
    try: _gs, gch = _gate().update(env.get('DATA') or '.', env.get('LINKS') or 'links')   # the auto re-enable (a person's GOOD / 3 clean in a row)
    except Exception as e: gch = False; print(f'::warning title=2-fer chain gate::gate state not updated ({str(e)[:150]}): it stays as it was')  # noqa: BLE001
    run, seen, notes = plan(env.get('DATA') or '.', env.get('LINKS') or 'links', env.get('GATE') or '', int(env.get('MAX') or 3))
    for n in notes: print(f'::notice title=2-fer chain::{n}')
    if seen:
        f = pathlib.Path(env.get('DATA') or '.') / 'data/status/fers-chain/seen.json'; f.parent.mkdir(parents=True, exist_ok=True)
        json.dump(seen, open(f, 'w', encoding='utf-8'), indent=1)
    if env.get('GITHUB_OUTPUT'):
        with open(env['GITHUB_OUTPUT'], 'a') as o: o.write(f"run={'yes' if run else 'no'}\nareas={json.dumps(run, separators=(',', ':'))}\ngate_changed={'yes' if gch else 'no'}\n")
    return run, seen, notes


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        print(f'::warning title=2-fer chain::plan stopped ({str(e)[:200]}): nothing starts')
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as o: o.write('run=no\nareas=[]\ngate_changed=no\n')
    sys.exit(0)
