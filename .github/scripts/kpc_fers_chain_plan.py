#!/usr/bin/env python3
"""2-FER CHAIN PLAN (Nov 4 2026; the chain: per Brandon via Super Head Bot (relayed), 4:55 AM CST Nov 4, his words: "I think it is done set up for this but if not make sure once mapping new pr with 2fer fixes is pushed that the 2fer line will start automatically running the new system that way next time we can evaluate both new systems"; what Mapping built from it: after the merge the whole
chain runs by itself, no new cron: US key build -> post-key check (links-01) -> 2-fer pre-line check -> 2-fer line -> 2-fer post-line
check; the pre- and post-line bots: Brandon, directly (Mapping chat), 4:52 AM CST Nov 4: "2fer line review? Plan and install any
pre and post line bots for the 2fer system."). The 2-fers stay HELD until a person grades them. Run by kpc-fers-chain.yml
(workflow_run on the hourly copy). Decides which 2-fer areas get a line on a NEW key build. Starts nothing itself, releases nothing:
it prints the area list for the workflow's matrix.

An area of a key runs once per area fingerprint (its key files + the 2-fer rules hash; done = its line wrote a READY verdict,
a line that held / failed / was cancelled may start again, at most TRIES times), when ALL hold:
  * the area is on KPC-Links' .github/fers-ready-areas.json (2-fers are US + Canada only)
  * every state of the area was built green on the CURRENT rules in that build (US: its own index 'states' row carries the
    rules hash and it is not 'failed'; keys without per-state rows: a FULL build on the current rules)
  * the links-01 post-key check ran on that build and lists no park of the area as a worse grade or outline -> pin
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
ONE LIST (KPC owner, 2026-11-12, part C of the per-area design): the chain's US / Canada areas ARE .github/fers-areas.json (the
same 14 areas the kpc-fers.yml bot runs, read by kpc_fers_states.areas()); the old hard-coded list (a 9-state southeast with VA / WV,
the old midwest / northeast, oh / mi / ut) is retired, so a chain line can never write a state set the bot does not, and a waiting-room
state file is never rewritten under a different cut. The unit that is saved, kept and stamped is the STATE (kpc_fers_states.py pick:
data/fers/stamps/<ST>.json). Retired tags still in seen.json are moved to seen[key]['retired'] (kept for the record, never planned).
A kpc-fers.yml pass that finished on the same per-state 2-fer hash counts for the chain: every pass done = the area is done (no line);
pass 1 done = the line starts with skip_pass1=yes (bot_passes below). WORLD below is the one home of the world (W-*) areas
(fers-areas.json must not hold W-* areas: a test checks it).
WORLD (Nov 11, test only, beta, hidden, members-only; nothing here publishes). THIS file (the dict R below) is the ONE list of the
chain's areas, world included; .github/fers-areas.json belongs to the older kpc-fers.yml bot and must not hold W-* areas (a test
checks it). A world area starts only when ALL hold, on top of the checks above (every unknown = wait):
  * every country of the area is on KPC-Links' .github/fers-ready-areas.json (ownership AND management wired for it). Today NO
    country is: the world key files hold no owner / manager data and kpc_fers.py's world ownership step answers 'no land register
    read for this country yet', so the world areas are skipped and this wiring is inert until a person opens a country there.
  * US and Canada are OK first (us_ca_ok below): every US / CA area of R that is on the ready list has a line that finished with a
    READY verdict on the CURRENT key files, and its report-<tag>.json records fers_rules == KPC-Links' current 2-fer rules hash
    (kpc_key_freeze.rules_hash('fers')). One unfinished, held, stale or unreadable US / CA area, or no ready US / CA area at all,
    means world waits. US / CA areas are planned before world in the same run (KEYS order) and take the 3 slots first.
Map-audit gate for world (audit_clean, the one place): while NO audit evidence exists for any country of a world area, the gate is
not applied to it (logged 'no world audit rows yet: audit gate not applied'); once any country has a row / stamp the gate applies
to the whole area exactly as for US / Canada. US / Canada areas are never passed through.
Remembered in data/status/fers-chain/seen.json {key: {build, ran: [tags], areas: {tag: {fp, planned, tries}}, waiting: {tag: why}}}; while PENDING both answers are
printed as notices in the run log (nothing is saved: nothing started). The gate state: data/status/fers-chain/gate.json.
env  DATA=. LINKS=links GATE=<repo variable: on|off|empty> MAX=3 GITHUB_OUTPUT (writes run, areas, gate_changed)"""
import hashlib, json, os, pathlib, re, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_fers_states as FS   # noqa: E402  (the one area list, the per-state hash and stamps)

# Nov 8 (Brandon: 'if quality approves something it is good to run'): the world key's 2-fer areas (the W-* countries in data/fers)
WORLD = {'worldwest': 'W-GB W-IE W-FR W-ES W-PT W-BE W-NL W-LU W-DE W-CH',
         'worldnorth': 'W-AT W-IT W-DK W-NO W-SE W-FI W-EE W-LV W-LT W-PL',
         'worldeast': 'W-CZ W-SK W-HU W-SI W-HR W-RO W-AU W-JP'}
R = {**FS.areas(), **WORLD}   # KPC owner, 2026-11-12: US / Canada = .github/fers-areas.json, the bot's own 14 areas
RETIRED = ('midwest', 'northeast', 'oh', 'mi', 'ut')   # tags of the old chain list that no longer exist (canadaeast / canadawest /
# southeast / southcentral / mountain / pacific are kept as names, with the bot's members)
KEYS = {'us-key': 'us', 'ca-key': 'ca', 'world-key': 'world'}
KEY_ORDER = tuple(KEYS)   # US first, then Canada, then world: the planning order (world is only ever planned behind US and Canada)


def kind_of(sts):
    """The key an area (or a state list) is measured on: CA-* = ca-key, W-* = world-key, anything else = us-key. The same rule as the
    BUILD_KIND line of kpc-fers-line.yml (tests/test_world_fers_line_nov11.py checks the two agree)."""
    s = str(sts or '').strip()
    return 'ca-key' if s.startswith('CA-') else 'world-key' if s.startswith('W-') else 'us-key'


KIND_OF = kind_of
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


def audit_clean(data, passed=None):
    """{area: why-not} for every area whose map audit is NOT clean (missing = clean). THE one place the audit gate decides.
    World exception (Nov 11, owner): a world (W-*) chain area with NO audit evidence at all for any of its countries (no audit
    row, no source-down row, no audited.json stamp) is passed through (its tag is appended to `passed` for the log); as soon as
    any country of it has evidence, the gate applies to the whole area exactly as for US / Canada. US / CA are never passed. Uses kpc_fers_gate's own row rules
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
    seen_codes = {r.get('area') for r in Q} | set(down) | {k for k in A}
    for tag, v in R.items():
        if kind_of(v) == 'world-key' and not (set(v.split()) & seen_codes):
            areas -= set(v.split())
            if passed is not None: passed.append(tag)
    for a in areas:
        mine = [r for r in Q if r.get('area') == a]
        op = sum(1 for r in mine if not G.row_clean(r))
        if not isinstance(A.get(a), dict): bad[a] = 'not audited in this pass'
        elif op or down.get(a): bad[a] = f'{op} audit row(s) not clean' + (f', {down[a]} source down' if down.get(a) else '')
    return bad


RETRY_H = 6      # a planned line with no result after this many hours may start again
TRIES = 2        # at most this many starts per area fingerprint; then a person looks


def states_not_green(idx, kind, sts, cur):
    """[(state, why)]: the states of an area NOT built green on the current rules in this key build (owner rule, 2026-11-10).
    US: the state's own row in index 'states' carries the rules it was built on; a state named failed, a row still marked
    not built, or no row at all never feeds 2-fers. Keys without per-state rows: the key-wide full-build 'rules'."""
    rows = idx.get('states') if isinstance(idx.get('states'), dict) and idx.get('states') else None
    failed = {str(x) for x in idx.get('failed') or []}
    out = []
    for st in sts:
        a = st.split('-', 1)[1] if '-' in st else st
        if a in failed or st in failed: out.append((st, 'failed in this build')); continue
        if rows is None:
            if str(idx.get('rules') or '') != cur: out.append((st, f"not a full build on the current rules ({idx.get('rules') or 'none'} vs {cur})"))
            continue
        r = rows.get(a)
        if not isinstance(r, dict) or r.get('_not_built'): out.append((st, 'not built in this build')); continue
        rr = r.get('rules') if 'rules' in r else (idx.get('rules') or None)
        if str(rr or '') != cur: out.append((st, f"not built on the current rules ({rr or 'none'} vs {cur})"))
    return out


def area_ready(links, sts):
    """2-fers are US + Canada only: an area runs only when every state is on KPC-Links' fers-ready-areas.json."""
    try:
        import kpc_fers_ready as FR
        rd = FR.load_ready(links)
        return all(FR.area_ready(x, rd) for x in sts)
    except Exception:  # noqa: BLE001
        return all(x.startswith(('US-', 'CA-')) for x in sts)


def area_fp(links, kind, sts, fers):
    """sha256 of the area's key files + the 2-fer rules hash: the same files and rules = the same 2-fer answer."""
    h = hashlib.sha256(str(fers).encode())
    for st in sts:
        f = pathlib.Path(links) / f"data/{kind}/{st if kind != 'world-key' else st.replace('W-', '')}.json"
        h.update(st.encode() + b'\0' + (f.read_bytes() if f.exists() else b'missing'))
    return h.hexdigest()[:16]


def line_done(data, tag, since):
    """The line's checker wrote a READY verdict (data/fers/line-<tag>.json, or its waiting-room copy) after `since`."""
    for f in ('data/fers/line-%s.json', 'data/waiting/in/data/fers/line-%s.json'):
        v = load(pathlib.Path(data) / (f % tag), {}) or {}
        if str(v.get('verdict') or '').startswith('READY') and str(v.get('date') or '') >= str(since or '~'): return True
    return False


def postcheck_parks(links, last):
    """(parks the post-key check lists as worse grade or outline -> pin for this build, why-not-read)."""
    if not last.get('report'): return set(), ''
    rep = load(pathlib.Path(links) / 'data/status/key-check' / str(last['report']))
    if not isinstance(rep, dict): return None, f"the post-key check report {last['report']} could not be read"
    ch = rep.get('changes') or {}
    return {str(r) for k in ('grade_worse', 'outline_to_pin') for r in ch.get(k) or []}, ''


def parks_of(links, kind, st):
    k = load(pathlib.Path(links) / f"data/{kind}/{st if kind != 'world-key' else st.replace('W-', '')}.json", {}) or {}
    return set((k.get('parks') or {}) if isinstance(k, dict) else ())


def _fers_file(data, name):
    """data/fers/<name> or its waiting-room copy (a line's checker diverts its output into data/waiting/in until a person releases it)."""
    for f in (f'data/fers/{name}', f'data/waiting/in/data/fers/{name}'):
        v = load(pathlib.Path(data) / f, None)
        if isinstance(v, dict): return v
    return {}


def us_ca_ok(data, links, fers, seen):
    """(True, '') when the US and Canada 2-fers are OK on the current rules, else (False, why). World waits on this. Honest and narrow:
    for EVERY US / CA area of R that is on KPC-Links' ready list (the areas the chain really runs):
      1 seen.json holds the area with the fingerprint of its CURRENT key files + the current 2-fer rules hash (so no key file changed since),
      2 its line wrote a READY verdict after that start (line_done: 'PART READY', 'STOPPED', held, missing = not OK),
      3 data/fers/report-<tag>.json (or its waiting-room copy) records fers_rules equal to the current 2-fer rules hash.
    It does not say the 2-fers are right; a person still grades them. No current rules hash, no ready US / CA area, an unreadable
    file = not OK (unknown = wait)."""
    if not fers: return False, 'the current 2-fer rules hash is unknown'
    need, bad = 0, []
    for tag, sts in R.items():
        kind = kind_of(sts)
        if kind == 'world-key' or not area_ready(links, sts.split()): continue
        need += 1
        a = ((seen.get(kind) or {}).get('areas') or {}).get(tag) or {}
        if not a.get('fp'): bad.append(f'{tag} (never started on these key files)'); continue
        if a['fp'] != area_fp(links, kind, sts.split(), fers): bad.append(f'{tag} (key files or 2-fer rules changed since its line)'); continue
        if not line_done(data, tag, a.get('planned')): bad.append(f'{tag} (line not READY yet)'); continue
        if str(_fers_file(data, f'report-{tag}.json').get('fers_rules') or '') != str(fers): bad.append(f'{tag} (its report is not on the current 2-fer rules)')
    if not need: return False, 'no US or Canada area is on the ready list'
    return (False, f'{len(bad)} of {need} US / Canada areas not OK: ' + '; '.join(bad[:8])) if bad else (True, '')


def migrate(s):
    """seen.json of one key: entries under a retired tag (the old chain list) move to s['retired'] (kept for the record, never planned)"""
    s = dict(s); ret = dict(s.get('retired') or {})
    for k in ('areas', 'waiting'):
        d = dict(s.get(k) or {})
        for t in [t for t in d if t not in R]: ret[t] = d.pop(t)
        if k in s or d: s[k] = d
    if 'ran' in s: s['ran'] = [t for t in s['ran'] if t in R]
    if ret: s['retired'] = ret
    return s


def bot_passes(data, links, sts):
    """how many passes (0-4) EVERY state of the area has finished on the inputs the chain would use now (KPC owner, 2026-11-12):
    the state's stamp (data/fers/stamps/<ST>.json, written by kpc_fers_states.py pick) has the same per-state 2-fer hash as
    computed now with LINKS' key files, its out_sha is the saved file's bytes, and the saved file is not marked incomplete.
    Anything missing or different = 0 (the line runs every pass, as before)."""
    try:
        st_of = FS.park_states(data); nb = FS.neighbours(data, st_of); code = FS.code_hash(links)
        hand = {f: FS._ref_rows(FS.load(pathlib.Path(links) / f)) for f in FS.HAND}
        n = 4
        for st in sts:
            stp = load(FS.stamp_path(data, st), {}) or {}
            _, sp, sd = FS.saved_copy(data, st)
            if not stp or sd is None or sd.get('incomplete') or stp.get('out_sha') != FS.sha(sp.read_bytes()): return 0
            if stp.get('area_hash') != FS.state_hash(st, links, data, nb, st_of, code, hand)[0]: return 0
            n = min(n, FS.n_passes(sd))
        return n
    except Exception:  # noqa: BLE001
        return 0


def area_map(data='.'):
    """The explicit, checked mapping between the chain's US / CA list (R) and the monthly bot's .github/fers-areas.json."""
    bot = json.load(open(pathlib.Path(data) / '.github/fers-areas.json', encoding='utf-8'))['areas']
    chain = {t: v for t, v in R.items() if kind_of(v) != 'world-key'}
    cm = {x: t for t, v in chain.items() for x in v.split()}; bm = {x: t for t, v in bot.items() for x in v.split()}
    return {'about': 'GENERATED by `python3 .github/scripts/kpc_fers_chain_plan.py map` from R (kpc_fers_chain_plan.py) and .github/fers-areas.json; a test fails when it is stale. KPC owner, 2026-11-12: ONE list (the chain reads fers-areas.json), so chain == bot and every difference list is empty; a test fails otherwise.',
            'chain': chain, 'bot': bot,
            'by_state': {x: {'chain': cm.get(x), 'bot': bm.get(x)} for x in sorted(set(cm) | set(bm))},
            'same_tag_same_members': sorted(t for t in chain if t in bot and chain[t].split() and set(chain[t].split()) == set(bot[t].split())),
            'same_tag_different_members': sorted(t for t in chain if t in bot and set(chain[t].split()) != set(bot[t].split())),
            'chain_only_tags': sorted(set(chain) - set(bot)), 'bot_only_tags': sorted(set(bot) - set(chain)),
            'states_only_in_bot': sorted(set(bm) - set(cm)), 'states_only_in_chain': sorted(set(cm) - set(bm))}


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
    wpass = []
    notclean = audit_clean(data, wpass) if gate != 'off' else {}
    run, notes = [], []
    would = {'on': [], 'off': []}   # PENDING: what each answer would start now (reported, not started)
    notes.append(f'map-audit gate {gate} ({gsrc}); the 2-fers stay held either way')
    if gate == 'PENDING': notes.append(f"KPC_FERS_CHAIN_GATE is PENDING ({gsrc}): the plan is reported, NOTHING starts")
    try: fers = KF.rules_hash('fers', links)
    except Exception: fers = ''  # noqa: BLE001
    stamp = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))
    wcache = []   # us_ca_ok, worked out once, and only if a world area is otherwise ready to start
    for kind in KEY_ORDER:
        short = KEYS[kind]
        li = load(links / f'data/{kind}/index.json', {}) or {}; bid = str(li.get('build') or '')
        cur = KF.rules_hash(kind, links)
        if not bid: notes.append(f'{kind}: no build stamp in KPC-Links'); continue
        mine = {tag: sts.split() for tag, sts in R.items() if KIND_OF(sts) == kind}
        green = {tag: states_not_green(li, kind, sts, cur) for tag, sts in mine.items()}
        if all(green.values()):   # owner rule, 2026-11-10: an AREA starts when each of its states is built green on the current rules
            notes.append(f'{kind}: build {bid} is not a full build on the current rules for any area ({li.get("rules") or "none"} vs {cur}): waits for the rebuild'); continue
        last = load(links / f'data/status/key-check/last-{short}.json', {}) or {}
        if str(last.get('build') or '') != bid: notes.append(f'{kind}: the post-key check (links-01) has not run on {bid} yet'); continue
        worse, pwhy = postcheck_parks(links, last)
        if worse is None: notes.append(f'{kind}: {pwhy}: no area starts'); continue
        here = {str((load(data / f'data/waiting/in/data/{kind}/index.json', {}) or {}).get('build') or ''), str((load(data / f'data/{kind}/index.json', {}) or {}).get('build') or '')}
        if bid not in here: notes.append(f'{kind}: build {bid} has not come over to KPC-Data yet'); continue
        items = (load(data / 'data/waiting/approved.json', {}) or {}).get('items')
        gno = getattr(KF, 'graded_no', None)
        if gno: v = gno(kind, bid, items, links)
        else:   # links-04 from before FINAL-v2: its verdict() + the NO words
            v = KF.verdict(kind, bid, items, links); v = v if v and re.match(r'\W*(KEY\s+)?(NO|FAIL|WITHDRAWN)', v[0].upper()) else None
        if v: notes.append(f'{kind}: build {bid} was graded {v[0][:20]} by {v[1]}: no 2-fers on it'); continue
        s = migrate(seen.get(kind) or {})
        # owner rule, 2026-11-10: an area is remembered by its fingerprint (its key files + the 2-fer rules), not by the build id,
        # and is done only when its line wrote a READY verdict; a held / failed / cancelled line may start again (at most TRIES)
        if s.get('build') != bid: s = {'build': bid, 'first_seen': stamp, 'areas': s.get('areas') or {}}
        s['areas'] = s.get('areas') or {}; s['waiting'] = {}
        s['ran'] = []; unready = []
        for tag, sts in R.items():
            if KIND_OF(sts) != kind: continue
            if not area_ready(links, sts.split()): unready.append(tag); continue   # only countries on fers-ready-areas.json (US + Canada today)
            if green.get(tag):
                s['waiting'][tag] = 'not a full build on the current rules for: ' + '; '.join(f'{x} ({w})' for x, w in green[tag][:6]); continue
            hit = sorted({x for x in sts.split() if worse & parks_of(links, kind, x)}) if worse else []
            if hit: s['waiting'][tag] = f"the post-key check lists parks with a worse grade / outline -> pin in {' '.join(hit)}: a person checks them first"; continue
            fp = area_fp(links, kind, sts.split(), fers); a = s['areas'].get(tag) or {}
            bp = bot_passes(data, links, sts.split()) if kind != 'world-key' else 0
            if bp >= 4:   # KPC owner, 2026-11-12: a kpc-fers.yml run that finished every pass on these inputs counts as done
                s['ran'].append(tag); s['waiting'][tag] = 'done by the 2-fer bot (every pass, same per-state 2-fer hash)'; continue
            if a.get('fp') == fp:
                if line_done(data, tag, a.get('planned')): s['ran'].append(tag); continue
                if int(a.get('tries') or 0) >= TRIES: s['waiting'][tag] = f"the line did not finish READY after {a.get('tries')} starts on these key files (see data/fers/line-{tag}.json): a person looks"; continue
                if a.get('planned') and time.mktime(time.strptime(a['planned'], '%Y-%m-%d %H:%M UTC')) > time.mktime(time.gmtime(now)) - RETRY_H * 3600:
                    s['ran'].append(tag); s['waiting'][tag] = f"line started {a['planned']}: waiting for its result"; continue
            if kind == 'world-key':   # behind US and Canada: world starts only when their 2-fers on the same rules are OK
                if not wcache: wcache.append(us_ca_ok(data, links, fers, seen))
                if not wcache[0][0]: s['waiting'][tag] = 'waits for US and Canada 2-fers on the same rules: ' + wcache[0][1]; continue
            nr = [f'{x} ({notclean[x]})' for x in sts.split() if x in notclean]
            if kind == 'world-key' and tag in wpass: print(f'::notice title=2-fer chain::{tag}: no world audit rows yet: audit gate not applied')
            if gate == 'PENDING':
                (would['off'] if len(would['off']) < mx else []).append(tag)
                if not nr and len(would['on']) < mx: would['on'].append(tag)
                s['waiting'][tag] = 'KPC_FERS_CHAIN_GATE is PENDING (not on / off): nothing starts' + (f"; map audit not clean: {'; '.join(nr[:4])}" if nr else '; map audit clean'); continue
            if gate == 'on' and nr: s['waiting'][tag] = f"map audit not clean: {'; '.join(nr[:6])}"; continue
            if len(run) >= mx: s['waiting'][tag] = 'next start (at most 3 areas at a time)'; continue
            run.append({'states': sts, 'tag': tag, 'key': kind, 'build': bid, 'skip_pass1': 'yes' if bp >= 1 else 'no'}); s['ran'].append(tag)
            s['areas'][tag] = {'fp': fp, 'planned': stamp, 'tries': (int(a.get('tries') or 0) if a.get('fp') == fp else 0) + 1}
        seen[kind] = s
        if unready: notes.append(f"{kind}: not on KPC-Links' fers-ready-areas.json (skipped): {' '.join(unready)}")
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
    if sys.argv[1:2] == ['map']:
        json.dump(area_map('.'), open('.github/fers-area-map.json', 'w', encoding='utf-8'), indent=1, sort_keys=True); sys.exit(0)
    try: main()
    except Exception as e:  # noqa: BLE001
        print(f'::warning title=2-fer chain::plan stopped ({str(e)[:200]}): nothing starts')
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as o: o.write('run=no\nareas=[]\ngate_changed=no\n')
    sys.exit(0)
