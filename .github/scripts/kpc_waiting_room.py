#!/usr/bin/env python3
"""THE WAITING ROOM checker (RULE SHEET F, KPC-Links .claude/notes/mapping.md). Built Oct 28 2026 night (Opus, chat 10) from
chat 11's KPC_WaitingRoom_Checks_desk.md + HQ's 12:38 PM item. NOT SWITCHED ON: no bot writes to data/waiting/in/ yet and the
workflow has no schedule. Brandon's GO switches it on, bot by bot.

WHAT IT DOES. A bot that saves a CHANGED data file puts it in data/waiting/in/<live path>. This checker compares that NEW file with
the LIVE one (and with other bots' data + the permanent known answers in data/waiting/known/), and per file says:
  PASS          -> it goes live at once (the replaced live copy is kept in data/waiting/previous/<path> for UNDO)
  HOLD          -> the new file waits in data/waiting/in/, the live file stays as it was, ONE 'please look' line for chat 11
  LIVE-FILTERED -> closures only (they NEVER wait, F-3): the file goes live with the rows that break a reject rule taken out
BUILT RIGHT (Brandon): (a) INDEPENDENT: imports no bot code and never reads a bot's own gate / READY / 'test' fields; (b) a check
that cannot run, an unknown kind of file, or any error = HOLD, never pass; (c) the REPLAY TEST (data/waiting/replay.json: the real
bad outputs from git history + 3 good outputs) must come back 100% right before it is switched on; (e) a held file never blocks
another file; (f) its own failure = nothing is promoted (everything waits) + one line to chat 11; no email (the workflow only goes
red when the checker has not run successfully for a whole day).

Use:  kpc_waiting_room.py check   [--promote]        every file under data/waiting/in/ (promote only when WAITING_ON=1)
      kpc_waiting_room.py replay                     the replay test; prints REPLAY=PASS|FAIL and writes data/waiting/replay.md
      kpc_waiting_room.py undo    <live path>        put back the previous good copy of one file (one bot / one state)
      kpc_waiting_room.py undo-bot <bot> [<area>]    every file of one bot (optionally one area, e.g. US-KY)
      kpc_waiting_room.py release <live path>        a person approved a held file: it goes live (previous copy kept)
Env: DATA (KPC-Data checkout, default .) · LINKS (KPC-Links checkout, default ../links) · NET=1 (link re-tests may use the
     network) · WAITING_ON=1 (promotion allowed; unset = report only)."""
import copy, datetime as dt, glob, json, math, os, pathlib, random, re, shutil, subprocess, sys, time, urllib.parse, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kpc_json_any import append_jsonl_gz  # noqa: E402
import kpc_archive as KA  # noqa: E402  (Nov 7: undo copies older than 14 days live on KPC-Archive; data/archive-manifest.json lists them)

DATA = pathlib.Path(os.environ.get('DATA') or '.')
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
W = DATA / 'data' / 'waiting'
TODAY = dt.date.today()
NET = os.environ.get('NET') == '1'
UA = 'KPC waiting-room checker (https://kentuckyportableclub.github.io/KPC-Links/; ham radio club; 1 request per 2 s per host)'
LINE_RX = re.compile(r'trail|river|parkway|byway|scenic|greenway|canal|route|corridor', re.I)   # F-2: line parks (POTA's 100-ft rule)
TOLLFREE = re.compile(r'^\D*1?\D*8(00|33|44|55|66|77|88)\D')
STATE_NAMES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
               'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
               'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
               'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
               'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
               'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
               'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia',
               'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}


class Unsure(Exception):
    """A check that could not run: the file HOLDS (F-4: unsure = hold)."""


# Nov 2 review: list guards. A part of a file with the wrong shape (a list where a checker expects an object, or the other way)
# crashed the checker ("'list' object has no attribute 'get'"); now it is a plain-words Unsure = HOLD, never a crash. (bug fix)
def want_dict(x, what):
    if x is None: return {}
    if not isinstance(x, dict): raise Unsure(f'{what} should be a JSON object, got a {type(x).__name__}')
    return x


def want_list(x, what):
    if x is None: return []
    if not isinstance(x, list): raise Unsure(f'{what} should be a list, got a {type(x).__name__}')
    return x


def live_dict(x, what):   # the LIVE side is never trusted to be right either: a wrong-shape live part counts as empty
    return x if isinstance(x, dict) else {}


# ------------------------------------------------------------------------------------------------ small helpers
def load(p, d=None):
    try:
        p = pathlib.Path(p)
        if str(p).endswith('.gz'):
            import gzip
            with gzip.open(p, 'rt', encoding='utf-8') as fh: return json.load(fh)
        return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def km(a, b, c, d):
    r = math.radians
    x = math.sin(r(c - a) / 2) ** 2 + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, x)))


def known(kind): return load(W / 'known' / f'{kind}.json', {}) or {}


def st_of(path):
    m = re.search(r'(?:US-)?([A-Z]{2})\.json', pathlib.Path(path).name)
    return m.group(1) if m else ''


_PARKS = {}
def parks(st):
    """POTA park pins for a state: [name, ?, type, ..., lat, lon] rows from data/parkinfo (the shared park list, not a bot's own)."""
    if st not in _PARKS and st.startswith('CA-'):   # Canada: POTA's own list (data/canada.json), same row shape as parkinfo
        _PARKS[st] = {r[1]: [r[2], '', '', None, None, r[3], r[4]] for r in (load(DATA / 'data' / 'canada.json', {}) or {}).get('rows') or [] if r[0] == 'POTA' and (r[3], r[4]) != (0, 0)}
    if st not in _PARKS:
        _PARKS[st] = (load(DATA / 'data' / 'parkinfo' / f'US-{st}.json', {}) or load(LINKS / 'data' / 'parkinfo' / f'US-{st}.json', {}) or {}).get('parks')
        if not _PARKS[st] and st == 'KY':   # Kentucky's pins live in the site's own park data (KPC-Links kpc-ky-data.json)
            _PARKS[st] = {x['c']: [x.get('n', ''), x.get('web') or '', x.get('t', ''), None, None, x.get('la'), x.get('lo')] for x in (load(LINKS / 'kpc-ky-data.json', {}) or {}).get('parks', []) if x.get('c')}
    if not _PARKS[st]: raise Unsure(f'no park list for {st} (data/parkinfo/US-{st}.json)')
    return _PARKS[st]


_ALLPINS = None
def pin_of(ref):
    """A park's pin from any state's park list (same-land pairs can cross a state line). -> (lat, lon) or None."""
    global _ALLPINS
    if _ALLPINS is None:
        _ALLPINS = {}
        for f in glob.glob(str(DATA / 'data' / 'parkinfo' / 'US-*.json')) + glob.glob(str(LINKS / 'data' / 'parkinfo' / 'US-*.json')):
            st_f = pathlib.Path(f).stem
            for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
                if len(v) > 6 and v[5] is not None and (v[5], v[6]) != (0, 0):
                    if r in _ALLPINS and _ALLPINS[r][3] != st_f: _ALLPINS[r] = (*_ALLPINS[r][:2], _ALLPINS[r][2], 'multi')
                    else: _ALLPINS.setdefault(r, (v[5], v[6], f'{v[0]} {v[2] or ""}', st_f))
        for x in (load(LINKS / 'kpc-ky-data.json', {}) or {}).get('parks', []):
            if x.get('c') and x.get('la') is not None: _ALLPINS.setdefault(x['c'], (x['la'], x['lo'], f"{x.get('n', '')} {x.get('t', '')}", 'US-KY'))
        for row in (load(DATA / 'data' / 'canada.json', {}) or {}).get('rows') or []:   # chat 8 B2: Canada's POTA pins (the shared park list)
            if len(row) > 4 and row[0] == 'POTA' and row[3] is not None and (row[3], row[4]) != (0, 0): _ALLPINS.setdefault(row[1], (row[3], row[4], row[2], 'CA'))   # 0,0 = no pin
    return _ALLPINS.get(ref)


SMALLK = re.compile(r'memorial|historic|site\b|monument|hatchery|museum|battlefield|cemetery|lighthouse|landing|access', re.I)   # never 'huge': a 100,000-acre memorial is a wrong join
_ACRES = None
def park_acres(ref):
    """A park's outline size in acres from the keys (US / Canada / world: the 'm' records), or None. Chat 2 Nov 1: F-S3 skips 100,000+ acres."""
    global _ACRES
    if _ACRES is None:
        _ACRES = {}
        for f in glob.glob(str(DATA / 'data' / '*-key' / '*.json')) + glob.glob(str(LINKS / 'data' / '*-key' / '*.json')):
            for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
                if isinstance(v, dict):
                    a = sum(float(m[2]) for m in v.get('m') or [] if isinstance(m, list) and len(m) > 2 and isinstance(m[2], (int, float)))
                    if a > 0: _ACRES[r] = max(a, _ACRES.get(r, 0))
    return _ACRES.get(ref)


BIG_RX = re.compile(r'national forest|national grassland|wilderness|national recreation area|national park\b|national monument|national preserve|national conservation area|maritime|islands? national wildlife refuge|' + LINE_RX.pattern, re.I)   # NOT state forests (NY's sister-name forests are small)
SISTER = re.compile(r'^\s*(.+?)\s*\(([^)]*)\)')


_SHAPES = None
def inside(x, y, ring):
    c = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]; xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi: c = not c
        j = i
    return c


def in_state(st, la, lo, slack=.05):
    global _SHAPES
    if _SHAPES is None:
        _SHAPES = {b['a']: [pl[0] for pl in b['p']] for b in (load(LINKS / 'kpc-us-states.json', []) or [])}
    rings = _SHAPES.get(st)
    if not rings: raise Unsure(f'no state outline for {st} (KPC-Links kpc-us-states.json)')
    return any(inside(lo + dx, la + dy, r) for dx, dy in ((0, 0), (slack, 0), (-slack, 0), (0, slack), (0, -slack)) for r in rings)


def drop(old_n, new_n, frac, floor=10):
    """True when new_n fell below frac of old_n (and the old file was big enough to judge)."""
    return old_n >= floor and new_n < frac * old_n


def share(urls, n_parks, cap=20, pct=.10):
    """URLs used by more than `cap` parks, or more than pct of a state's parks (when it has 30+): one page for many parks."""
    from collections import Counter
    c = Counter(u for u in urls if u)
    lim = min(cap, max(3, int(pct * n_parks))) if n_parks >= 30 else cap
    return [(u, k) for u, k in c.most_common() if k > lim]


# ------------------------------------------------------------------------------------------------ the checks, one per kind of file
# each: (path, new, live, ctx) -> (holds [reasons], notes [info]); raise Unsure when it cannot judge. ctx['set'] = {path: new} of the batch.

def c_access(path, new, live, ctx):
    ca = area_of(path).startswith('CA-')
    st = st_of(path); P = parks('CA-' if ca else st); K = known('access')
    holds, notes = [], []
    far, outside, unknown, n_new = [], 0, 0, 0
    for ref, pts in (new.get('parks') or {}).items():
        v = P.get(ref)
        if not v: unknown += len(pts); continue
        line = bool(LINE_RX.search(f'{v[0]} {v[2] or ""}'))
        for q in pts:
            n_new += 1
            if abs(q[0]) < .01 and abs(q[1]) < .01: outside += 1; continue
            if v[5] is not None and not line and km(v[5], v[6], q[0], q[1]) > K.get('far_km', 100): far.append((ref, round(km(v[5], v[6], q[0], q[1]))))
            elif not ca and not (v[5] is not None and km(v[5], v[6], q[0], q[1]) <= 5) and not ((pin_of(ref) or (0, 0, '', ''))[3] == 'multi') and not in_state(st, q[0], q[1], .3): outside += 1   # Canada: no province outlines; tune Oct 29: a point within 5 km of its own park pin, or on a multi-state park, is never 'outside'
    n_old = sum(len(v) for v in ((live or {}).get('parks') or {}).values())
    if far: holds.append(f'F-A1 {len(far)} points over {K.get("far_km", 100)} km from their park pin (not a line park), e.g. ' + ', '.join(f'{r} {k} km' for r, k in far[:3]))
    if drop(n_old, n_new, .6, 20): holds.append(f'F-A2 points {n_old} -> {n_new} (more than 40% gone)')
    if n_new and outside / n_new > .01: holds.append(f'F-A3 {outside} of {n_new} points at 0,0 or outside the state')
    if n_new and unknown / max(1, n_new) > .02: holds.append(f'F-A4 {unknown} points on park numbers not in the park list')
    for ref, mn in ((K.get('keep') or {}).get(pathlib.Path(path).name) or {}).items():
        if len((new.get('parks') or {}).get(ref) or []) < mn: holds.append(f'F-K known answer: {ref} must keep {mn}+ points')
    return holds, notes


def c_campfed(path, new, live, ctx, state_file=True):
    st = st_of(path); holds, notes = [], []
    camps = new.get('camps') or []
    old = (live or {}).get('camps') or []
    if drop(len(old), len(camps), .7): holds.append(f'F-C1 campgrounds {len(old)} -> {len(camps)} (more than 30% gone)')
    out = [c for c in camps if c[2] is not None and not in_state(st, c[2], c[3])]
    if camps and len(out) / len(camps) > .01: holds.append(f'F-C2 {len(out)} of {len(camps)} pins outside {st}, e.g. {out[0][1]}')
    if state_file:   # F-C3: one campground, one state file: the batch's files + every other live file of the same folder
        folder = pathlib.Path(path).parent
        others = {}
        for f in glob.glob(str(LINKS / folder / 'US-*.json')) + glob.glob(str(DATA / folder / 'US-*.json')):   # KPC-Links first: campfed / campstate are written there
            nm = pathlib.Path(f).name
            if nm == pathlib.Path(path).name or nm in others: continue
            others[nm] = {c[0] for c in ((ctx['set'].get(str(folder / nm)) or load(f, {}) or {}).get('camps') or [])}
        mine = {c[0] for c in camps}
        dup = {nm: len(mine & ids) for nm, ids in others.items() if mine & ids}
        if dup: holds.append(f'F-C3 {sum(dup.values())} campground ids are also in another state file: ' + ', '.join(f'{k} {v}' for k, v in sorted(dup.items())[:5]))
    ids = [c[0] for c in camps]
    if len(ids) != len(set(ids)): holds.append(f'F-C4 {len(ids) - len(set(ids))} campground ids twice in the file')
    if st == 'KY' and folder_is(path, 'campfed'):   # F-K: the hand-checked Kentucky Recreation.gov camps (KPC-Links kpc-campgrounds.json)
        hand = [g for p in (load(LINKS / 'kpc-campgrounds.json', {}) or {}).get('parks', []) for g in p.get('campgrounds', [])
                if 'recreation.gov' in (g.get('reserve', '') + g.get('source', '')) and g.get('la') and g.get('lo')]
        if not hand: raise Unsure('no Kentucky hand camps to compare (KPC-Links kpc-campgrounds.json)')
        pool = list(camps)   # Kentucky's hand camps can sit just over a line (Wilderness Road CG at Cumberland Gap = a Virginia pin): the neighbour states' files count too
        for nb in ('TN', 'VA', 'WV', 'OH', 'IN', 'IL', 'MO'):
            pool += ((ctx['set'].get(f'data/campfed/US-{nb}.json') or load(LINKS / f'data/campfed/US-{nb}.json', {}) or load(DATA / f'data/campfed/US-{nb}.json', {}) or {}).get('camps') or [])
        miss = sorted({g['name'] for g in hand if not any(km(g['la'], g['lo'], c[2], c[3]) <= 2 for c in pool if c[2] is not None)})
        if miss: holds.append('F-K known Kentucky federal camps missing within 2 km: ' + ', '.join(miss[:5]))
    return holds, notes


def folder_is(path, name): return f'/{name}/' in '/' + str(path).replace('\\', '/')


def c_campstate(path, new, live, ctx): return c_campfed(path, new, live, ctx, state_file=False)


def c_campinfo(path, new, live, ctx):
    from collections import Counter
    holds, notes = [], []
    camps = list((new.get('camps') or {}).values())
    rv = [(c.get('name'), c.get('rv_max_ft')) for c in camps if isinstance(c.get('rv_max_ft'), (int, float)) and not 10 <= c['rv_max_ft'] <= 100]
    if rv: holds.append(f'F-I1 {len(rv)} RV lengths outside 10-100 ft, e.g. {rv[0][0]} {rv[0][1]} ft')
    tot = Counter()
    for c in camps:
        s = c.get('sites'); t = s.get('total') if isinstance(s, dict) else s
        if isinstance(t, (int, float)):
            if not 1 <= t <= 1000: holds.append(f"F-I2 {c.get('name')} {t} sites (outside 1-1,000)")
            tot[(c.get('agency'), t)] += 1
    same = [(k, n) for k, n in tot.items() if n > 3]
    if same: holds.append(f'F-I3 the same site count on {same[0][1]} camps of one agency ({same[0][0][0]}: {same[0][0][1]}): copied from a shared page?')
    ph = [c.get('name') for c in camps if c.get('phone') and TOLLFREE.match(str(c['phone']))]
    if ph: holds.append(f'F-I4 {len(ph)} toll-free reservation numbers kept as a camp phone, e.g. {ph[0]}')
    fee = [c.get('name') for c in camps if re.search(r'million|renovat|\bgrant\b', json.dumps(c.get('fees') or ''), re.I)]
    if fee: holds.append(f'F-I5 {len(fee)} fees that read like news / money totals, e.g. {fee[0]}')
    return holds, notes


def coords(g):
    if not g: return []
    t, c = g.get('type'), g.get('coordinates') or []
    if t == 'LineString': return c
    if t == 'MultiLineString': return [p for l in c for p in l]
    if t == 'GeometryCollection': return [p for gg in g.get('geometries') or [] for p in coords(gg)]
    return []


def length_km(g):
    t, c = (g or {}).get('type'), (g or {}).get('coordinates') or []
    lines = [c] if t == 'LineString' else c if t == 'MultiLineString' else []
    return sum(km(a[1], a[0], b[1], b[0]) for l in lines for a, b in zip(l, l[1:]))


def c_wwff(path, new, live, ctx):
    """WWFF directory, one file per prefix (chat 2 8:20 PM: ready to wire). Wrong = empty, a read that half-answered (under 80% of the
    saved rows), or the same reference twice."""
    holds = []
    rows = new if isinstance(new, list) else (new or {}).get('refs') or []
    old = live if isinstance(live, list) else (live or {}).get('refs') or []
    if not rows: holds.append('F-W1 the directory file is empty')
    if old and len(rows) < .8 * len(old): holds.append(f'F-W2 rows {len(old)} -> {len(rows)} (under 80% of the saved list)')
    refs = [r[0] if isinstance(r, list) and r else (r.get('reference') or r.get('ref')) if isinstance(r, dict) else None for r in rows]
    d = len(refs) - len(set(refs))
    if d: holds.append(f'F-W3 {d} references listed twice')
    return holds, []


def c_trails(path, new, live, ctx):
    holds, notes = [], []
    if isinstance(new, list):   # data/trails/index.json = the list of trail lines (Nov 2: was a checker error)
        old = live if isinstance(live, list) else []
        if not new: holds.append('F-T1 the trail index is empty')
        if old and len(new) < .8 * len(old): holds.append(f'F-T4 trail index {len(old)} -> {len(new)} lines (under 80% of the saved list)')
        refs = [r.get('ref') for r in new if isinstance(r, dict)]
        if len(refs) != len(set(refs)): holds.append(f'F-T5 {len(refs) - len(set(refs))} trails listed twice in the index')
        return holds, notes
    nl = not_line(path)
    if nl: return [f"F-T7 not a trail line: {nl.get('why') or 'a report with no geometry'}; its home is {nl.get('home') or 'data/status/'} (never released into data/trails)"], notes
    pn, po = coords(new.get('geometry')), coords((live or {}).get('geometry'))
    if not pn: holds.append('F-T1 the line has no points')
    if po and len(pn) < .5 * len(po): holds.append(f'F-T2 points {len(po)} -> {len(pn)} (under half the saved line)')
    ln, lo = length_km(new.get('geometry')), length_km((live or {}).get('geometry'))
    if lo > 1 and not (.75 * lo <= ln <= 1.5 * lo): holds.append(f'F-T3 length {lo:.0f} -> {ln:.0f} km (outside -25% / +50%)')
    kl = keep_line(path)
    if kl and (ln < .98 * float(kl.get('km') or 0) or len(pn) < int(kl.get('points') or 0)):
        holds.append(f"F-T6 REJECTED ({kl.get('by') or 'a person'}): keep the saved official line ({kl.get('km')} km, {kl.get('points')} points); "
                     f"this new line is {ln:.1f} km, {len(pn)} points. Never released while data/waiting/known/trails.json keeps it; {kl.get('review') or 'on the review pile'}")
    return holds, notes


def keep_line(path):
    """Nov 4 (per Brandon via Super Head Bot (relayed), 4:35 AM CST: 'Agree keep the official line'; Brandon, directly (Mapping chat), 4:36 AM CST: 'No keep the full length ones we had'): data/waiting/known/trails.json 'keep_lines'
    = parks whose saved official line a person chose to keep. A new line for one of them that is shorter or has fewer points is
    REJECTED (F-T6), and mode_release refuses it, so no chat 11 YES, per-park release or trusted-kind auto-release can put it live.
    To lift it, a person removes the park from keep_lines."""
    m = re.match(r'^data/trails/([^/]+)\.json(\.gz)?$', str(path).replace('\\', '/'))
    return (known('trails').get('keep_lines') or {}).get(m.group(1)) if m else None


def not_line(path):
    """Nov 4 (Quality; per Brandon via Super Head Bot (relayed), 4:35 AM CST): files under data/trails/ that are NOT trail lines (a status report with no
    geometry), from data/waiting/known/trails.json 'not_lines': held as F-T7, never released into data/trails, never taken back as a
    bot's working copy (mode_resume), so a stale held copy stops coming round every run."""
    return (known('trails').get('not_lines') or {}).get(re.sub(r'\.gz$', '', str(path).replace('\\', '/')))


def retest(urls, n=20):
    """Re-test up to n kept links (GET, 2 s per host). -> (tested, dead [url]). No network = Unsure (hold)."""
    if not NET: raise Unsure('link re-test needs the network (NET=1): not run, so the file waits')
    urls = sorted(set(u for u in urls if u and u.startswith('http')))
    random.Random(str(TODAY)).shuffle(urls)
    last, dead, tested = {}, [], 0
    for u in urls[:n]:
        h = u.split('/')[2]
        w = 2 - (time.time() - last.get(h, 0))
        if w > 0: time.sleep(w)
        last[h] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=30) as r: ok = r.status < 400
        except Exception as e:  # noqa: BLE001
            ok = getattr(e, 'code', 0) in (401, 403, 405, 429)   # alive, just not for bots
        tested += 1
        if not ok: dead.append(u)
    return tested, dead


def c_docs(path, new, live, ctx):
    holds, notes = [], []
    P = new.get('parks') or {}
    banned = re.compile(known('docs').get('banned_hosts') or r'inciweb|google\.[a-z.]+/maps|maps\.app\.goo\.gl|goo\.gl/maps|facebook\.com', re.I)
    for kind in ('map', 'rules'):
        urls = [((r.get(kind) or {}).get('url')) for r in P.values()]
        agency = lambda d: (d or {}).get('rules_scope') == 'agency' or 'agency-wide' in str((d or {}).get('how') or '') or 'agency-wide' in str((d or {}).get('status_note') or '')
        shared = [((r.get(kind) or {}).get('url')) for r in P.values() if not (kind == 'rules' and agency(r.get(kind)))]   # tune Oct 29: an agency-wide rules page LABELLED so (docs v6 rule) is allowed on many parks
        for u, k in share(shared, len(P)): holds.append(f'F-D1 one {kind} page on {k} of {len(P)} parks: {u[:80]}')
        bad = [u for u in urls if u and banned.search(u)]
        if bad: holds.append(f'F-D2 {len(bad)} {kind} links on a banned host (fire news / map pins / social), e.g. {bad[0][:70]}')
    kept = [(r.get(k) or {}).get('url') for r in P.values() for k in ('map', 'rules')]
    try:
        tested, dead = retest(kept)
        if tested and (len(dead) / tested > .03 and len(dead) >= 2): holds.append(f'F-D3 {len(dead)} of {tested} re-tested links dead, e.g. {dead[0][:70]}')
    except Unsure as e: holds.append(f'F-4 unsure: {e}')   # keep the other reasons too
    return holds, notes


def c_hours(path, new, live, ctx):
    from collections import Counter
    holds, notes = [], []
    P = new.get('parks') or {}
    for kind in ('fees', 'hours', 'permits'):
        lines = [re.sub(r'\W+', ' ', (x.get('line') or '')).strip().lower() for r in P.values() for x in (r.get(kind) or [])]
        per = Counter()
        for r in P.values():
            for t in {re.sub(r'\W+', ' ', (x.get('line') or '')).strip().lower() for x in (r.get(kind) or [])}: per[t] += 1
        lim = min(20, max(3, int(.1 * len(P)))) if len(P) >= 30 else 20
        wide = [(t, n) for t, n in per.items() if n > lim]
        if wide: holds.append(f'F-H1 the same {kind} line on {wide[0][1]} parks (statewide / agency-wide text?): "{wide[0][0][:70]}"')
        if kind == 'fees':
            big = [l for l in lines if re.search(r'million', l) or any(float(m.replace(',', '')) > 500 for m in re.findall(r'\$\s?(\d[\d,]*(?:\.\d+)?)', l) if m.replace(',', '').replace('.', '').isdigit())]
            if big: holds.append(f'F-H2 {len(big)} fee lines over $500 or in millions, e.g. "{big[0][:70]}"')
        if kind == 'hours':
            notime = [l for l in lines if not re.search(r'\d\s*(?:a\.?m|p\.?m)|\b\d{1,2}(:\d\d)?\s*(?:-|to|–)\s*\d|sunrise|sunset|dawn|dusk|24 hours|24/7|closed', l)]
            if lines and len(notime) / len(lines) > .2: holds.append(f'F-H3 {len(notime)} of {len(lines)} hours lines have no time, e.g. "{notime[0][:60]}"')
        heads = [l for r in P.values() for x in (r.get(kind) or []) for l in [x.get('line') or ''] if l.strip().endswith(':')]
        if heads: holds.append(f'F-H4 {len(heads)} {kind} lines are headings ending ":"')
    for key, rule in (known('hours').get(st_of(path)) or {}).items():
        ref = rule.get('ref') or key   # Oct 28 (Fable): a key may carry a suffix so one park can have several rules; 'ref' names the park
        txt = json.dumps((P.get(ref) or {}).get(rule['field']) or '')
        if rule.get('never') and re.search(rule['never'], txt, re.I): holds.append(f"F-K known answer: {ref} {rule['field']} must never match '{rule['never']}'")
        if rule.get('must') and not re.search(rule['must'], txt, re.I): holds.append(f"F-K known answer: {ref} {rule['field']} must still carry '{rule['must']}' ({rule.get('what', '')[:50]})")
    return holds, notes


def c_truth(path, new, live, ctx):
    from collections import Counter
    holds, notes = [], []
    P = new.get('parks') or {}
    offs = [(ref, r) for ref, r in P.items() if r.get('verdict') == 'off' and r.get('official')]
    byn = Counter((r['official'].get('acres'), r['official'].get('url')) for _, r in offs)
    sh = [(k, n) for k, n in byn.items() if n >= 3]
    if sh: holds.append(f'F-R1 {sh[0][1]} parks OFF on one number from one page ({sh[0][0][0]:,} ac, {str(sh[0][0][1])[:60]})')
    byv = Counter(r['official'].get('acres') for _, r in offs)
    shv = [(a, n) for a, n in byv.items() if n >= 5]
    if shv: holds.append(f'F-R2 {shv[0][1]} OFF rows share the size {shv[0][0]:,} ac')
    K = known('truth')
    for a in (K.get('never_acres') or {}).get(st_of(path), []):
        hit = [ref for ref, r in offs if r['official'].get('acres') == a]
        if hit: holds.append(f'F-K known answer: {a:,} ac is never one park\'s size ({len(hit)} rows)')
    for ref, rule in (K.get('rows') or {}).get(st_of(path), {}).items():
        r = P.get(ref) or {}; o = r.get('official') or {}
        ok = True
        if rule.get('verdict') and r.get('verdict') != rule['verdict']: ok = False
        if rule.get('acres_near') and not (o.get('acres') and abs(o['acres'] - rule['acres_near']) <= rule.get('tol', 60)): ok = False
        if rule.get('acres_not') is not None and o.get('acres') == rule['acres_not']: ok = False
        if not ok: holds.append(f"F-K known answer {ref}: {rule.get('what')} (now verdict {r.get('verdict')}, {o.get('acres')} ac)")
    n_size = sum(1 for r in P.values() if r.get('verdict') in ('off', 'agree'))
    if n_size >= 20 and len(offs) / n_size > .5: holds.append(f'F-R3 {len(offs)} of {n_size} sized parks are OFF (over half: a reading problem?)')
    return holds, notes


def c_leads(path, new, live, ctx):
    n, o = len(new.get('leads') or []), len((live or {}).get('leads') or [])
    holds = []
    if o and (n == 0 or n < .5 * o): holds.append(f'F-L1 leads {o} -> {n} (wiped or under half)')
    return holds, []


def has_outline(r): return bool((r or {}).get('m') or (r or {}).get('c'))


NAME_STOP = set('state park parks national forest wildlife management area wma the of and nature preserve recreation lake river natural historic '
                'site county city regional reserve conservation memorial trail wilderness refuge nwr sp sf creek fish game public lands land unit at on in '
                'de la le du des provincial'.split())
def name_words(s):
    """Nov 2 (chat 12, Cameroon / Paraguay): accents stripped first ('Bénoué' = 'Benoue', 'Lobéké' = 'Lobeke'; the old compare split
    'Bénoué' into 'b' + 'nou'), any apostrophe dropped ('Ma’an' = "Ma'an")."""
    import unicodedata
    t = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r"['’`´]", '', t)
    return {w for w in re.findall(r'[a-z0-9]+', t) if len(w) > 2 and w not in NAME_STOP}


PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0/query'
def padus_boxes(ids):
    """{OBJECTID: (minlon, minlat, maxlon, maxlat)} read from PAD-US (generalised geometry, 100 ids per request, 2 s apart)."""
    out = {}
    for i in range(0, len(ids), 100):
        q = urllib.parse.urlencode({'objectIds': ','.join(map(str, ids[i:i + 100])), 'outFields': 'OBJECTID', 'returnGeometry': 'true', 'outSR': 4326, 'maxAllowableOffset': .005, 'f': 'json'})
        try:
            with urllib.request.urlopen(urllib.request.Request(PADUS + '?' + q, headers={'User-Agent': UA}), timeout=90) as r: d = json.load(r)
        except Exception as e: raise Unsure(f'PAD-US did not answer the shape test ({type(e).__name__})')  # noqa: BLE001
        for f in d.get('features') or []:
            pts = [pt for ring in (f.get('geometry') or {}).get('rings') or [] for pt in ring]
            if pts: out[(f.get('attributes') or {}).get('OBJECTID')] = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        time.sleep(2)
    return out


def c_key(path, new, live, ctx):
    holds, notes = [], []
    retired = set(((load(LINKS / 'data' / 'retired-refs.json', {}) or {}).get('refs') or {}) if isinstance((load(LINKS / 'data' / 'retired-refs.json', {}) or {}).get('refs'), (dict, list)) else [])
    retired |= set(known('key').get('never_outlined') or [])
    if pathlib.Path(path).name == 'refs.json':
        txt = json.dumps(new)
        bad = sorted(r for r in retired if f'"{r}"' in txt)
        if bad: holds.append(f'F-O3 retired parks still in the outline index: {", ".join(bad[:5])}')
        return holds, notes
    P, O = want_dict(new.get('parks'), 'the key\'s "parks"'), live_dict((live or {}).get('parks'), 'live parks')
    P = {k: (v if isinstance(v, dict) else {}) for k, v in P.items()}; O = {k: (v if isinstance(v, dict) else {}) for k, v in O.items()}
    n_new, n_old = sum(has_outline(r) for r in P.values()), sum(has_outline(r) for r in O.values())
    if n_old >= 20 and n_new < .99 * n_old: holds.append(f'F-O1 outlines {n_old} -> {n_new} (more than 1% lost)')
    bad = sorted(r for r in P if r in retired and has_outline(P[r]))
    if bad: holds.append(f'F-O3 retired parks still outlined: {", ".join(bad[:5])}')
    # chat 8 attack 2 (an outline swapped to another park, the NS label / NY same-name bugs): the outline's own layer names must share a
    # word with the park's name. Live keys miss on 0-4% (spelling: 'DeSoto', 'Norfork'); a shuffled key misses on nearly all.
    def miss_rate(PP):
        n = bad = 0
        for r in PP.values():
            mw = set().union(*[name_words(m[1]) for m in (r.get('m') or []) if isinstance(m, list) and len(m) > 1]) if r.get('m') else set()
            nw = name_words(r.get('n'))
            if not (mw and nw): continue
            n += 1; bad += not (mw & nw)
        return n, bad
    nn, nb = miss_rate(P); on, ob = miss_rate(O)
    if nn >= 20:
        lim = max(.05, (ob / on + .02) if on >= 20 else .10)
        if nb / nn > lim: holds.append(f'F-O2 {nb} of {nn} outlines carry a layer name that shares no word with the park ({nb / nn:.0%}; live {ob}/{on or 0}): outlines swapped to other parks?')
    # chat 8 retest 2 (A2d): the park's NAME must still be POTA's name (the shared park list), so a bot cannot rename a park to fit a swapped layer
    try: plist = parks(st_of(path)) if area_of(path).startswith('US') else {r[1]: [r[2]] for r in (load(DATA / 'data' / 'canada.json', {}) or {}).get('rows') or [] if r[0] == 'POTA' and r[1].startswith(area_of(path)[:2])}
    except Unsure: plist = {}
    ren = [ref for ref, r in P.items() if ref in plist and r.get('n') and name_words(r['n']) and name_words(plist[ref][0]) and not (name_words(r['n']) & name_words(plist[ref][0]))]
    if len(ren) > max(2, .01 * max(len(P), 1)): holds.append(f'F-O2 {len(ren)} parks carry a name that is not POTA\'s (renamed to fit a layer?), e.g. ' + ', '.join(f"{q} '{P[q]['n'][:30]}'" for q in ren[:3]))
    # chat 8 retest 2: the SHAPE test by a different path: outlines that changed since the live file (or 60 at random in a first file) are read
    # straight from PAD-US (ArcGIS REST, the one robots exception), and the park's POTA pin must be inside the outline's box or within 5 km of it
    if NET:
        oldm = {ref: sorted(str(m[0]) for m in (r.get('m') or [])) for ref, r in O.items()}
        cand = [ref for ref, r in P.items() if r.get('m') and any(isinstance(m[0], int) for m in r['m']) and (not O or sorted(str(m[0]) for m in r['m']) != oldm.get(ref))]
        random.Random(str(TODAY) + str(path)).shuffle(cand); cand = cand[:60]
        if cand:
            boxes = padus_boxes(sorted({m[0] for ref in cand for m in P[ref]['m'] if isinstance(m[0], int)}))
            off = []
            for ref in cand:
                pin = pin_of(ref); bx = [boxes[m[0]] for m in P[ref]['m'] if m[0] in boxes]
                if not pin or not bx: continue
                if not any(b[1] - .05 <= pin[0] <= b[3] + .05 and b[0] - .07 <= pin[1] <= b[2] + .07 for b in bx): off.append(ref)
            notes.append(f'F-O4 shape test: {len(cand)} changed outlines read from PAD-US, {len(off)} far from the park pin')
            if len(off) > max(1, .05 * len(cand)): holds.append(f'F-O4 {len(off)} of {len(cand)} changed outlines sit 5+ km from the park\'s pin (read from PAD-US itself), e.g. ' + ', '.join(off[:3]))
    for name in known('key').get('keep_names') or []:
        hit = [r for r in P.values() if name.lower() in str(r.get('n', '')).lower()]
        if hit and not any(has_outline(r) for r in hit): holds.append(f'F-K known answer: {name} must keep its outline')
    return holds, notes


def c_intake(path, new, live, ctx):
    holds = []
    K = known('intake')
    rows = want_list(new.get('rows'), 'the intake "rows"')
    if any(not isinstance(r, dict) for r in rows): raise Unsure(f'{sum(not isinstance(r, dict) for r in rows)} intake row(s) are not objects')
    for r in rows:
        v = str(r.get('verdict') or r.get('status') or '').upper(); why = str(r.get('why') or '').lower(); t = (r.get('title') or r.get('url') or '')[:40]
        if v == 'REJECT' and re.search(r'did not open|error|timed? ?out|invalid url', why): holds.append(f'F-N1 "{t}": a read error must be RETRY, never REJECT')
        if v == 'READY' and re.search(r'credit|copyright', why) and not re.search(r'licen[cs]e|open data|cc[- ]by|public domain|ogl', why): holds.append(f'F-N2 "{t}": READY on a credit / copyright line only')
        for k in K.get('never_ready') or []:
            if v == 'READY' and re.search(k['rx'], json.dumps(r), re.I): holds.append(f'F-K known answer: "{t}" is {k["why"]}, never READY')
    return holds, []


def c_fers(path, new, live, ctx):
    holds, notes = [], []
    S = [s for s in want_list(new.get('spots'), 'the 2-fer "spots"') if isinstance(s, dict)]
    _ol = (live or {}).get('spots') if isinstance(live, dict) else None
    O = [s for s in (_ol if isinstance(_ol, list) else []) if isinstance(s, dict)]
    if any('id' not in s for s in S): raise Unsure(f'{sum("id" not in s for s in S)} 2-fer spot(s) have no id')
    O = [s for s in O if "id" in s]
    cand = {s['id'] for s in S if str(s.get('status', '')).startswith('candidate')}
    oc = {s['id'] for s in O if str(s.get('status', '')).startswith('candidate')}
    if len(oc) >= 10 and abs(len(cand) - len(oc)) / len(oc) > .3: holds.append(f'F-2 candidates {len(oc)} -> {len(cand)} (over 30% change)')
    ns = sum(1 for s in S if str(s.get('status', '')).startswith('not sure')); ons = sum(1 for s in O if str(s.get('status', '')).startswith('not sure'))
    if ons >= 5 and abs(ns - ons) / ons > .3: holds.append(f'F-2 NOT SURE {ons} -> {ns} (over 30% change)')
    for p in ('pass1', 'pass2', 'pass3'):
        if not new.get(p): holds.append(f'F-2 {p} missing: the 2-fer passes did not all run')
        elif not re.match(r'^20\d\d-\d\d-\d\d', str(new.get(p))): holds.append(f'F-2 {p} is not a run date ({str(new.get(p))[:20]}): the bot\'s own field, not trusted')
    if S and not all(isinstance(s.get('passes'), list) and len(s['passes']) >= 3 for s in S):   # chat 8 attack 7: every row must show what each pass did (independent of the pass1-3 flags)
        holds.append(f"F-2 {sum(1 for s in S if not (isinstance(s.get('passes'), list) and len(s['passes']) >= 3))} rows without a passes record: the passes did not all look at them")
    # chat 8 attack 1 + 4: WHICH pairs, not how many. A pair = its park numbers (stable when an outline moves).
    LIVE_ST = ('candidate', 'very tight', 'water only', 'merged into')
    op = {frozenset(s.get('refs') or []) for s in O if str(s.get('status', '')).startswith('candidate')}
    np_ = {frozenset(s.get('refs') or []) for s in S if str(s.get('status', '')).startswith('candidate')}   # like for like: the rows shown as 2-fers
    if len(op) >= 3 and len(op & np_) < .8 * len(op): holds.append(f'F-2 only {len(op & np_)} of {len(op)} live candidate pairs are still there (under 80%): a person looks (a rule change is released by hand)')
    elif 1 <= len(op) <= 2 and not (op & np_): holds.append(f'F-2 small area: all {len(op)} live candidate pair(s) gone')
    if len(op) >= 3 and len(np_ - op) > max(2, .10 * len(op)):   # chat 8 retest 1: near-miss swaps (a partner moved to a park 20 km away) add NEW pairs
        holds.append(f'F-2 {len(np_ - op)} new candidate pairs since the live file (over 10% of {len(op)}): a person looks at them first, e.g. ' + ', '.join('+'.join(sorted(q)) for q in sorted(np_ - op, key=sorted)[:3]))
    if O and not S: holds.append(f'F-2 every row gone (live had {len(O)})')
    # chat 8 attack 3: a far-apart pair is a wrong join for EVERY kind (area / trail / river too), not only 'same land'
    far2 = []
    for s in S:
        if s.get('kind') == 'same land' or not str(s.get('status', '')).startswith(LIVE_ST): continue
        pins = [pin_of(r) for r in (s.get('refs') or [])]
        if any(pp is None for pp in pins): continue
        d = max((km(a[0], a[1], b[0], b[1]) for i, a in enumerate(pins) for b in pins[i + 1:]), default=0)
        if d > 100 and not any(pp[3] == 'multi' or BIG_RX.search(pp[2]) for pp in pins) and s.get('kind') not in ('trail', 'river', 'line', 'water') \
                and not any((park_acres(r) or 0) > 100_000 and not SMALLK.search(str((pin_of(r) or ('', '', ''))[2])) for r in (s.get('refs') or [])): far2.append(f"{'+'.join(s.get('refs') or [])} {d:.0f} km")
    if far2: holds.append(f'F-S3 {len(far2)} live rows whose two park pins are 100+ km apart (wrong joins), e.g. ' + ', '.join(sorted(set(far2))[:3]))
    # F-S2 (Fable review): a LIVE 'same land, two park numbers' row whose two pins are 30+ km apart is a wrong join; a missing pin = hold (fail closed)
    far, nopin = [], []
    for s in S:
        if s.get('kind') != 'same land' or not str(s.get('status', '')).startswith(('candidate', 'merged into')): continue
        pins = [pin_of(r) for r in (s.get('refs') or [])]
        if any(pp is None for pp in pins): nopin.append(s.get('id')); continue
        d = max((km(a[0], a[1], b[0], b[1]) for i, a in enumerate(pins) for b in pins[i + 1:]), default=0)
        sis = [SISTER.match(pp[2]) for pp in pins]
        sister = all(sis) and len({m.group(1).lower() for m in sis}) == 1 and len({m.group(2).lower() for m in sis}) > 1   # 'Lost Nation (St. Lawrence County)' + '(Allegany County)'
        big = any(pp[3] == 'multi' or BIG_RX.search(pp[2]) for pp in pins)   # one pin for a huge / multi-state / line park (GW & Jefferson NF)
        if d > 30 and (sister or not big or d > 300): far.append(f"{'+'.join(s.get('refs') or [])} {d:.0f} km" + (' (sister names)' if sister else ''))
    if far: holds.append(f'F-S2 {len(far)} same-land rows with pins 30+ km apart (wrong joins), e.g. ' + ', '.join(far[:3]))
    if nopin: holds.append(f'F-4 unsure: {len(nopin)} same-land rows with a park pin missing, e.g. {nopin[0]}')
    # first file for an area: a near-empty file must not pass just because there is nothing to compare with
    if live is None:
        st = st_of(path); ok_n = ((load(DATA / 'data' / ('ca-key' if area_of(path).startswith('CA') else 'us-key') / f'{area_of(path)}.json', {}) or {}).get('counts') or {}).get('matched') or 0
        if ok_n >= 50 and len(S) < ok_n / 50: holds.append(f'F-2 near-empty first file: {len(S)} rows for a state with {ok_n} outlined parks')
    # F-K by a STABLE key (Fable note c): the PAIR of park numbers (never the spot id, which changes when an outline changes). Live =
    # candidate / very tight / water only / merged into another row. Pairs come from the hand files, never from the 2-fer bot's own gate.
    live_rows = [set(s.get('refs') or []) for s in S if str(s.get('status', '')).startswith(('candidate', 'very tight', 'water only', 'merged into'))]
    keys_live = {spot_key(s) for s in S if str(s.get('status', '')).startswith(('candidate', 'very tight', 'water only', 'merged into'))}
    ids_live = {s.get('id') for s in S if str(s.get('status', '')).startswith(('candidate', 'very tight', 'water only', 'merged into'))}
    for k in (known('fers').get(area_of(path)) or {}).get('keys') or []:   # G2 (Brandon Oct 29 6:50 AM)
        if k.get('key') not in keys_live and not (set(k.get('alias_ids') or []) & ids_live): holds.append(f"F-K known 2-fer missing: {k.get('key')}")
    for pair, line in known_pairs(area_of(path)):
        ok = any(set(pair) <= rs for rs in live_rows)
        if not ok and line and len(pair) > 2:   # a 3-park entry also passes when each trail x park pair is live (Fort Donelson + Fort Heiman = one shore)
            ok = all(any({line, o} <= rs for rs in live_rows) for o in pair if o != line)
        if not ok: holds.append(f"F-K known 2-fer missing: {' + '.join(pair)}")
    return holds, notes


def spot_key(s):
    """G2 (Brandon Oct 29 6:50 AM): a 2-fer's STABLE key = its park numbers (sorted) + kind + center rounded to 0.01 degree (~1 km);
    the bot's spot id changes when an outline changes, so the old id is kept only as an alias."""
    c = s.get('center') or [None, None]
    loc = f'{round(c[0], 2):.2f},{round(c[1], 2):.2f}' if c[0] is not None else '?'
    return '+'.join(sorted(s.get('refs') or [])) + '@' + str(s.get('kind') or '') + '@' + loc


def area_of(path):
    m = re.search(r'\b((?:US|CA)-[A-Z]{2})\.json', pathlib.Path(path).name)
    return m.group(1) if m else ''


def known_pairs(st):
    K = known('fers').get(st if '-' in st else f'US-{st}') or {}
    pairs = [(list(p), None) for p in (K.get('pairs') or [])]
    if K.get('from_trail_file'):   # KPC-Links ky-trail-parks.json: the hand-checked river-bank / trail-inside pairs (the same rule chat 2 uses)
        tp = load(LINKS / 'ky-trail-parks.json', {}) or {}
        for key in ('lewis', 'tears'):
            t = tp.get(key) or {}
            for pk in t.get('parks') or []:
                if re.search(r'within 100 ft of the water|of (the )?(trail|route).*inside|mi of trail inside', pk.get('how') or '', re.I):
                    pairs.append((sorted(set([t.get('ref')] + (pk.get('refs') or []))), t.get('ref')))
    return [(p, l) for p, l in pairs if all(p)]


def c_pota(path, new, live, ctx):
    def count(x, side):
        if isinstance(x, bool): raise Unsure(f'{side} "parks" is true/false, not a count')
        if isinstance(x, (int, float)): return x
        if isinstance(x, (dict, list)): return len(x)   # a park table instead of a count: its length
        if x in (None, ''): return 0
        raise Unsure(f'{side} "parks" is a {type(x).__name__}, not a count')
    n = count(new.get('parks'), 'new'); o = count((live or {}).get('parks') if isinstance(live, dict) else None, 'live')
    holds = []
    if o and (o - n > max(5, .01 * o)): holds.append(f'F-P1 POTA parks {o:,} -> {n:,} (more than 1% or 5 gone): needs a second read')
    return holds, []


def c_status(path, new, live, ctx):
    """Any file with a READY status must have no 'not checked / no answer' rows (Michigan water lesson)."""
    txt = json.dumps(new).lower()
    if not isinstance(new, dict): return [], []   # a plain list (the WWFF directories, the trails index) has no status line (Nov 2: was a checker error on 9 files)
    st = str(new.get('status') or new.get('verdict') or new.get('state') or '').upper()   # chat 8 retest 6: 'state' too
    n = len(re.findall(r'store not read|not checked', txt)); r = len(re.findall(r'no answer|unanswered|did not answer|map not answered', txt))
    ready = 'READY' in st and 'STOPPED' not in st   # chat 8 attack 6: the real words are 'READY FOR CHAT 8' / 'PART READY FOR CHAT 8'
    holds = [f'F-S1 status {st[:30]} with {n} rows STORE NOT READ / not checked (must be STOPPED)'] if ready and n else []
    notes = [f'F-S1 {r} rows where a map did not answer: review, not a stop (aligned with the 2-fer line checker, Fable note d)'] if ready and r else []
    return holds, notes


# ---- closures: NEVER WAIT (F-3): rows that break a reject rule are taken out; an empty / garbled file holds (old one stays, 'as of')
RES_ROW = re.compile(r'\|\s*(?:\d+(?:\.\d+)?\s*%|1\s*:\s*\d)|(?:\|\s*(?:\d+(?:\.\d+)?|-|NA)\s*){3}')
def closures_filter(path, new, live):
    st = st_of(path); items = new.get('items')
    if not isinstance(items, list): return None, ['F-3 garbled closures file (no items list): the old one stays, stamped "as of"']
    _bad = [it for it in items if not isinstance(it, dict)]   # Nov 2 review: a row that is not an object is taken out, never a crash
    items = [it for it in items if isinstance(it, dict)]
    if _bad and not items: return None, [f'F-3 garbled closures file ({len(_bad)} rows, none an object): the old one stays, stamped "as of"']
    if not isinstance(live, dict): live = {}
    if not items and len((live or {}).get('items') or []) >= 5: return None, [f'F-3 empty closures file (live had {len((live or {}).get("items"))}): the old one stays, stamped "as of"']
    keep, gone, seen = [], [], set()
    try: own = set(parks(st)) if st else None
    except Unsure: own = None
    for it in items:
        d = str(it.get('details') or ''); low = d.lower(); why = ''
        if it.get('to') and str(it['to']) < TODAY.isoformat(): why = 'ended'
        elif RES_ROW.search(d): why = 'a results table row'
        elif re.search(r'\bfree\b|no permit needed|federal holidays|prohibitions\b', low) and not it.get('from'): why = 'a fee / hours / standing note'
        elif re.search(r'\b(?:is|are) prohibited\b|in violation of', low) and not it.get('from') and not it.get('to') and it.get('class') in ('note', None): why = 'a standing rule'
        elif it.get('ref') and own is not None:   # chat 8 B1: the row's park number decides (the shared park list), never words in the text
            if it['ref'] not in own: why = f"another state (park {it['ref']} is not on the US-{st} park list)"
        else:   # no park number: the word test, with a state name only in a place role ('Indiana bat', 'Washington County', 'state line' are not)
            pl = re.sub(r'\b(?:indiana|virginia|townsend\'?s|gray|grey|northern long-eared) bats?\b|\b[a-z]+(?: [a-z]+)? (?:county|parish|counties)\b|\b[a-z]+(?: [a-z]+)? (?:state )?(?:line|border)\b|\b[a-z]+(?: [a-z]+)? (?:hunters|residents|license|licence)s?\b', ' ', low)
            for ab, nm in STATE_NAMES.items():
                if ab != st and (re.search(rf'\b(?:County|Co\.|City|Parish),?\s+{ab}\b|,\s*{ab}\s*\)', d) or (nm.lower() in pl and not (nm == 'Virginia' and 'west virginia' in pl and st == 'WV'))):
                    if STATE_NAMES.get(st, '').lower() not in pl: why = f'another state ({ab})'; break
        k = (it.get('ref'), re.sub(r'\W+', ' ', low).strip())
        if not why and k in seen: why = 'a duplicate'
        if why: gone.append(f'{it.get("ref")}: {why}: {d[:60]}'); continue
        seen.add(k); keep.append(it)
    gone += [f'?: not a row object: {str(b)[:60]}' for b in _bad]
    items = items + _bad
    if items and len(gone) > len(items) / 3:   # G4 (Brandon Oct 29 6:50 AM): many bad rows = something is wrong with the read: hold the whole file
        return None, [f'F-3 {len(gone)} of {len(items)} closure rows break a reject rule (over a third): the whole file is held, the old one stays, stamped "as of"'] + gone[:5]
    out = dict(new); out['items'] = keep
    return out, gone


# ------------------------------------------------------------------------------------------------ routing (unknown kind = HOLD)
def c_acres(path, new, live, ctx):
    """Official acres list (kpc_acres; chat 10 Oct 31): every row a positive number of acres, a source and how it matched."""
    bad = []
    rows = new if isinstance(new, dict) else {}
    rows = next((rows[k] for k in ('parks', 'rows', 'acres') if isinstance(rows.get(k), dict)), rows)
    rows = {k: v for k, v in rows.items() if isinstance(v, dict)}
    if not rows: bad.append('no rows')
    odd = [r for r, v in rows.items() if not (isinstance(v.get('acres'), (int, float)) and v['acres'] > 0 and v.get('source_url'))]
    if odd: bad.append(f'{len(odd)} rows without acres or a source (e.g. {odd[0]})')
    fl = sum(1 for v in rows.values() if v.get('flags'))
    return bad, [f'{len(rows)} parks sized, {fl} flagged for a look']


def c_cell(path, new, live, ctx):
    """Cell coverage (chat 10 Oct 31; HQ 9:00 PM rule sheet): FCC source named, an as-of date, every point = 'no FCC data' or carrier -> 5G / 4G / 3G / none."""
    bad, notes = [], []
    if 'FCC' not in str((new or {}).get('src')): bad.append('the source is not the FCC National Broadband Map')
    if not (new or {}).get('as_of'): bad.append('no FCC as-of date')
    P = (new or {}).get('parks') or {}
    if not P: bad.append('no parks')
    odd = [r for r, v in P.items() for k in ('pin', 'park') if k in v and v[k] != 'no FCC data' and not (isinstance(v[k], dict) and all(t in ('5G', '4G', '3G', 'none') for t in v[k].values()))]
    if odd: bad.append(f'{len(odd)} points with an unknown value (e.g. {odd[0]})')
    nod = sum(1 for v in P.values() if v.get('pin') == 'no FCC data')
    notes.append(f'{len(P)} parks, {nod} with no FCC data at the pin, FCC as-of {(new or {}).get("as_of")}')
    return bad, notes


PILE_VERDICTS = {'SOLVED-JOIN': 'YES', 'SOLVED-PIN': 'PIN', 'NEEDS-PERSON': 'NOT SURE', 'UNTOUCHED': ''}
PILE_BAD_SRC = re.compile(r'openstreetmap|\bosm\b|wdpa|protectedplanet|google\.|alltrails|wikipedia|wikidata', re.I)


def c_pile_solver(path, new, live, ctx):
    """Review pile solver proposals (Nov 4 handoff, section 8): one known verdict per park with its answer word; every SOLVED-JOIN has
    an official evidence URL, a record id, a distance and no rule-18 note, and a pin more than 100 m out carries 'POTA pin may be off';
    every NEEDS-PERSON says what is missing; no row claims a person's approval. Independent of the solver's code (F: imports none)."""
    bad = []
    P = want_dict(want_dict(new, 'the file').get('parks'), 'parks')
    if not P: bad.append('no parks')
    cnt = {}
    for ref, r in P.items():
        r = want_dict(r, ref); v = r.get('verdict'); cnt[v] = cnt.get(v, 0) + 1
        if v not in PILE_VERDICTS: bad.append(f'{ref}: unknown verdict {v!r}'); continue
        if (r.get('answer_word') or '') != PILE_VERDICTS[v]: bad.append(f"{ref}: verdict {v} with answer word {r.get('answer_word')!r}")
        if r.get('approved_by'): bad.append(f'{ref}: a bot row may not name an approver')
        if v == 'SOLVED-JOIN':
            ev = str(r.get('evidence_urls') or '')
            if not ev or PILE_BAD_SRC.search(ev): bad.append(f'{ref}: SOLVED-JOIN without an official evidence URL')
            if not r.get('record_id'): bad.append(f'{ref}: SOLVED-JOIN without a record id')
            try: d = float(r.get('distance_m'))
            except (TypeError, ValueError): bad.append(f'{ref}: SOLVED-JOIN without a distance'); continue
            if r.get('rule18_note'): bad.append(f'{ref}: SOLVED-JOIN with a rule-18 note')
            if d > 100 and r.get('pin_flag') != 'POTA pin may be off': bad.append(f'{ref}: pin {d:g} m out without the POTA pin flag')
        if v == 'NEEDS-PERSON' and not str(r.get('whats_missing') or '').strip(): bad.append(f'{ref}: NEEDS-PERSON without what is missing')
    return bad[:20], [f'{len(P)} parks: ' + ', '.join(f'{k} {n}' for k, n in sorted(cnt.items()))]


ROUTES = [
    (r'^data/pile-solver/(?:US-[A-Z]{2}|CA-[A-Z]{2}|[A-Z]{2})\.json$', 'pilesolver', c_pile_solver),   # Nov 4: review pile solver proposals
    (r'^data/access/index\.json$', 'info', lambda path, new, live, ctx: ([], ['the access index: passes when it reads as JSON'])),
    (r'^data/access/[^/]+\.json$', 'access', c_access),
    (r'^data/campfed/US-[A-Z]{2}\.json$', 'campfed', c_campfed),
    (r'^data/campstate/US-[A-Z]{2}\.json$', 'campstate', c_campstate),
    (r'^data/campinfo/US-[A-Z]{2}\.json$', 'campinfo', c_campinfo),
    (r'^data/trails/[^/]+\.json$', 'trails', c_trails),
    (r'^data/docs/US-[A-Z]{2}\.json$', 'docs', c_docs),
    (r'^data/hours/US-[A-Z]{2}\.json$', 'hours', c_hours),
    (r'^data/truth/US-[A-Z]{2}\.json$', 'truth', c_truth),
    (r'^data/access-leads/[^/]+\.json$', 'leads', c_leads),
    # Nov 2 review: switch WAITING_KEY_NAMES_ONLY=1 routes only the state / province key files (US-KY.json, CA-ON.json) to the key
    # checker; index.json, layers.json, zip-*.json then fall to the 'info' rule below them (or HOLD as unknown). Default 0 = today.
    ((r'^data/(?:us|ca)-key/(?:US|CA)-[A-Z]+\.json$' if os.environ.get('WAITING_KEY_NAMES_ONLY') == '1' else r'^data/(?:us|ca)-key/[^/]+\.json$'), 'key', c_key),
    (r'^data/world-key/[A-Z]{2}\.json$', 'key', c_key),   # Oct 30 5:55 AM (chat 2; Brandon 'world boundaries a go'): the world key is held + checked like the US / Canada keys
    (r'^data/intake/ready\.json$', 'intake', c_intake),
    (r'^data/wwff/[^/]+\.json$', 'wwff', c_wwff),   # Oct 29 10:55 PM (chat 2 8:20 PM)
    (r'^data/fers/(?:US|CA)-[A-Z]{2}\.json$', 'fers', c_fers),   # chat 8 B2: Canada too (Canada's POTA pins from data/canada.json)
    (r'^data/fers/(?:line|missing|same-outline|expected|looked)-[a-z]+\.json$', 'info', lambda path, new, live, ctx: ([], ['an info file: passes when it reads as JSON (chat 8 B2)'])),
    (r'^data/pota/index\.json$', 'pota', c_pota),
    (r'^data/closures/(?:US|CA)-[A-Z]{2}\.json$', 'closures', None),
    (r'^data/review/[^/]+\.json$', 'status', c_status),
    (r'^data/cell/(?:US-[A-Z]{2}|test-[A-Z]{2})\.json$', 'cell', c_cell),
    (r'^data/acres\.json$', 'acres', c_acres),
]
NEVER_AUTO = {'pilesolver'}   # Nov 4 review: the pile solver's proposals never go live by themselves (no PROMOTE_KINDS, no trust run): a person releases them
NEVER_WAIT = {'closures'}   # F-3 (+ spots, weather, band alerts and a NEW park's pin + name, which never pass through here)


def kind_of(path):
    p = re.sub(r'\.gz$', '', str(path).replace('\\', '/'))   # a gzipped bot file is judged like its .json
    for rx, k, fn in ROUTES:
        if re.match(rx, p): return k, fn
    return None, None


def live_of(rel, twin=None):
    """chat 8 attack 5: x.json and x.json.gz are ONE file. -> (live, twin_note): the live copy under either name; both live = hold."""
    rel = str(rel); base = re.sub(r'\.gz$', '', rel); names = [base, base + '.gz']
    have = [n for n in names if (DATA / n).exists()] if twin is None else twin
    if len(have) == 2: return load(DATA / rel) or load(DATA / [n for n in names if n != rel][0]), 'both'
    if have and have[0] != rel: return load(DATA / have[0]), have[0]
    return (load(DATA / rel) if have else None), None


def rows_in(d):
    for k in ('spots', 'parks', 'items', 'camps', 'leads', 'rows'):
        v = (d or {}).get(k)
        if isinstance(v, (list, dict)): return len(v)
    return 0


BIG_CHANGE = re.compile(r'over 30% change|live candidate pairs are still there|new candidate pairs since|more than 40% gone|more than 1% lost|under half|over 10% fewer|more than 1% or 5 gone')


def apply_stamp(path, kind, holds):
    """G5 (Brandon Oct 29 7:26 AM 'Yes'): after an INTENDED rule change, one narrow stamp (by Brandon, or chat 8 for him) naming the rule
    and the areas waives ONLY the 'big change' alarms for those files, for 7 days; every other check still runs. Stamps live in
    data/waiting/known/stamps.json: {"stamps": [{"rule": "NS label fix", "kind": "fers", "areas": ["CA-NS"], "by": "Brandon", "date": "2026-10-29"}]}."""
    area = area_of(path) or ('US-' + st_of(path) if st_of(path) else '')
    keep, waived = [], []
    for h in holds:
        s = next((s for s in (known('stamps').get('stamps') or []) if BIG_CHANGE.search(h) and s.get('kind') in (kind, '*') and area in (s.get('areas') or [])
                  and s.get('by') and str(s.get('date', '')) <= TODAY.isoformat() <= str(s.get('until') or (dt.date.fromisoformat(str(s['date'])) + dt.timedelta(days=7)).isoformat())), None)
        if s: waived.append(f"G5 stamp '{s.get('rule')}' ({s.get('by')}, {s.get('date')}) waived: {h}")
        else: keep.append(h)
    return keep, waived


LIST_OK = {'wwff', 'trails', 'status'}   # kinds whose checker handles a list (c_wwff, c_trails, c_status since Nov 2)


def judge(path, new, live, twin=None, ctx=None):
    """-> {'path','kind','verdict': PASS|HOLD|LIVE-FILTERED,'why': [..],'notes': [..], 'out': file to publish (closures)}"""
    ctx = ctx or {}
    kind, fn = kind_of(path)
    res = {'path': str(path), 'kind': kind or 'unknown', 'why': [], 'notes': []}
    try:
        if new is None: raise Unsure('the new file does not read as JSON')
        if kind is None: raise Unsure('no check written for this kind of file (fail closed)')
        if twin == 'both': res.update(verdict='HOLD', why=[f'F-4 both {re.sub(r".gz$", "", str(path))} and its .gz are live: two copies, the page reads one (chat 8 attack 5)']); return res
        if twin and rows_in(live) and rows_in(new) < .9 * rows_in(live):
            res.update(verdict='HOLD', why=[f'F-4 {path} replaces live {twin} (other format) with {rows_in(new)} rows for {rows_in(live)} (over 10% fewer)']); return res
        if twin: res['notes'].append(f'replaces live {twin} (same file, other format): promotion removes the old name')
        if kind == 'closures':
            out, gone = closures_filter(path, new, live)
            if out is None: res.update(verdict='HOLD', why=gone); return res
            res.update(verdict='LIVE-FILTERED' if gone else 'PASS', notes=gone, out=out if gone else None); return res
        if live is None: res['notes'].append('no live copy: first time this file is published')
        # Nov 2 review: list-shaped files (wwff, trails index, ...) crashed dict checkers with "'list' object has no attribute 'get'"
        if kind not in LIST_OK and not isinstance(new, dict): raise Unsure(f'expected a JSON object for a {kind} file, got a {type(new).__name__} (wrong shape)')
        if kind not in LIST_OK and live is not None and not isinstance(live, dict): live = None; res['notes'].append('live copy is not a JSON object: compared as a first publish')
        holds, notes = fn(path, new, live, ctx)
        h2, _ = c_status(path, new, live, ctx) if kind != 'status' else ([], [])
        holds += h2
        holds, waived = apply_stamp(path, kind, holds)
        res.update(verdict='HOLD' if holds else 'PASS', why=holds, notes=res['notes'] + notes + waived)
    except Unsure as e: res.update(verdict='HOLD', why=[f'F-4 unsure: {e}'])
    except Exception as e:  # noqa: BLE001  (own error = hold, fail closed)
        res.update(verdict='HOLD', why=[f'F-4 checker error: {type(e).__name__}: {str(e)[:160]}'])
    return res


# ------------------------------------------------------------------------------------------------ modes
def look_line(r): return f"- FROM WAITING ROOM ({TODAY}): {r['kind']} {r['path']} held: {' · '.join(r['why'])[:600]}"


def mode_divert(paths):
    """Brandon Oct 29 7:55 PM ('fire them up if you trust them to run and put stuff in waiting room'): a bot's CHANGED files of a kind
    the waiting room checks are moved into data/waiting/in/ and the live file is put back as it was (git HEAD), so nothing new goes
    live; then every waiting file is judged (verdicts written, NOTHING promoted). State / review files stay with the bot."""
    out = subprocess.run(['git', '-C', str(DATA), 'status', '--porcelain', '--', *paths], capture_output=True, text=True).stdout.splitlines()
    moved = []
    for ln in out:
        rel = ln[3:].strip().strip('"')
        if ' -> ' in rel: rel = rel.split(' -> ')[1]
        if not re.search(r'\.json(\.gz)?$', rel) or kind_of(rel)[0] in (None, 'info'): continue
        src = DATA / rel
        if not src.exists():   # Nov 1 (storage, 1 MB gzip): a bot that swapped x.json for x.json.gz deleted the live x.json: put it back (live stays as it was)
            if not ln.startswith('??'): subprocess.run(['git', '-C', str(DATA), 'checkout', '-q', 'HEAD', '--', rel])
            continue
        dst = W / 'in' / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
        _tw = W / 'in' / (rel[:-3] if rel.endswith('.gz') else rel + '.gz')   # Nov 1: the newer held copy replaces an older held twin
        if _tw.exists(): _tw.unlink()
        if ln.startswith('??'): src.unlink()
        else: subprocess.run(['git', '-C', str(DATA), 'checkout', '-q', 'HEAD', '--', rel])
        moved.append(rel)
    print(f'::notice title=Waiting room (hold)::{len(moved)} changed files held for checks, live files unchanged' + (f': {", ".join(moved[:8])}' if moved else ''))
    if moved: mode_check(False)


def mode_resume(paths):
    """Before a held bot runs again: its waiting files become its working copy, so it continues from what it held (not from live)."""
    n, skipped = 0, []
    for pth in paths:
        for f in (W / 'in' / pth).rglob('*') if (W / 'in' / pth).exists() else []:
            if not f.is_file(): continue
            rel = f.relative_to(W / 'in')
            if not_line(rel.as_posix()): skipped.append(rel.as_posix()); continue   # Nov 4: a held status report is not a bot's working copy
            (DATA / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, DATA / rel); n += 1
    print(f'::notice title=Waiting room (hold)::{n} held files taken as the working copy' + (f'; not taken (not a trail line, see known/trails.json): {", ".join(skipped)}' if skipped else ''))


def row_map(d):
    """{row key: row json} for a bot file: dict-of-ref files by ref, list rows by their id / first cell / whole row."""
    if isinstance(d, list): d = {'rows': d}
    if not isinstance(d, dict): return {}
    for k in ('spots', 'parks', 'items', 'camps', 'leads', 'rows', 'states', 'provinces', 'countries'):   # Nov 2 review (Quality 6a): key index files
        v = (d or {}).get(k)
        if isinstance(v, dict): return {str(r): json.dumps(x, sort_keys=True, ensure_ascii=False) for r, x in v.items()}
        if isinstance(v, list):
            out = {}
            for x in v:
                key = (x.get('id') or x.get('key') or '|'.join(str(x.get(f) or '') for f in ('a', 'b', 'refs', 'ref'))) if isinstance(x, dict) else (x[0] if isinstance(x, list) and x else x)
                out[str(key) if key not in (None, '', '|||') else json.dumps(x, sort_keys=True)[:200]] = json.dumps(x, sort_keys=True, ensure_ascii=False)
            return out
    return {}


def grade_queue(out):
    """Brandon Oct 31 10:00 PM ('I agree to all'): ONE list of what waits for a grader, written by the bot (no chat relays 'ready to check'),
    and ONLY the rows that changed since the live (last graded) copy: same rows keep their old YES, graders look at new / changed only."""
    who = {'fers': 'chat 8 + chat 11', 'key': 'chat 11 (+ chat 2 G-4)'}
    lines = [f"# Waiting for a grader ({dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ')}, written by the waiting room)",
             'Rows the same as the live (already graded) copy keep their old YES: check only the NEW + CHANGED rows listed. Held = a check failed: fix first.', '']
    # Nov 2 review (Quality 6b): rule 22 ties a key YES to the held build id, so every key file shows it
    builds = {}
    def held_build(path):
        m = re.match(r'data/(us-key|ca-key|world-key)/', path)
        if not m: return None
        if m.group(1) not in builds: builds[m.group(1)] = str((load(W / 'in' / 'data' / m.group(1) / 'index.json') or {}).get('build') or '')
        return builds[m.group(1)] or 'NONE (no build stamp: a YES cannot name a build yet)'
    # Nov 2 review (Quality 6c): 2-fer grading is paused (Nov 2 10:07 AM ruling) except areas the gate marked ready or restarted
    try: FR = (load(DATA / 'data/status/fers-ready.json') or {}).get('areas') or {}
    except Exception: FR = {}  # noqa: BLE001
    def fers_paused(path):
        if not path.startswith('data/fers/'): return False
        a = FR.get(pathlib.Path(path).name.split('.')[0]) or {}
        return not (a.get('status') == 'ready for 2-fers' or a.get('fers_started'))
    paused = []
    for r in sorted(out, key=lambda r: (r['verdict'] != 'PASS', r['path'])):
        if fers_paused(r['path']): paused.append(r['path']); continue
        new = load(W / 'in' / r['path']); live = live_of(r['path'])[0]
        a, b = row_map(new), row_map(live) if live else {}
        nw = [k for k in a if k not in b]; ch = [k for k in a if k in b and a[k] != b[k]]; gone = [k for k in b if k not in a]
        same = len(a) - len(nw) - len(ch)
        if not a and not b:   # Nov 2 review (Quality 6a): no rows this list can read: say whether the file changed at all
            counts = ('new file (no live copy), no rows to list' if live is None else 'same as the live copy' if new == live
                      else 'whole file changed, no rows to list: look at the whole file')
        else: counts = f"{len(nw)} new, {len(ch)} changed, {len(gone)} gone, {same} same (carried)"
        hb = held_build(r['path'])
        lines.append(f"- **{r['path']}** ({r['kind']}, {r['verdict']}; grader {who.get(r['kind'], 'chat 11')}"
                     + (f"; held build {hb}" if hb else '') + f"): {counts}"
                     + (f"; check: {', '.join((nw + ch)[:25])}{' ...' if len(nw) + len(ch) > 25 else ''}" if nw or ch else '')
                     + (f"; why held: {'; '.join(r.get('why') or [])[:300]}" if r['verdict'] == 'HOLD' else ''))
    if paused:
        lines += ['', f'## Paused, not for grading ({len(paused)} 2-fer file(s): 2-fer grading is paused since Nov 2 10:07 AM until the gate marks the area ready)',
                  '', ', '.join(paused)]
    pathlib.Path(DATA / 'data/status').mkdir(parents=True, exist_ok=True)
    (DATA / 'data/status/grade-queue.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def mode_tidy():
    """Nov 2 review (storage). Switch WAITING_TIDY (default 1 = ON since Nov 2, Brandon OK'd; WAITING_TIDY=0 = nothing is cleaned). A held copy that a newer build made the
    same as live (the live file already has it: released, or the bot came back to it) has nothing left to wait for: it is removed.
    WAITING_KEEP_GENS=N (default 2 since Nov 2; 0 = keep all) also removes 'previous-<g>' copies older than N generations. Returns what went."""
    if os.environ.get('WAITING_TIDY', '1') != '1': return []   # Nov 2: ON (Brandon OK'd the review; storage alarm); WAITING_TIDY=0 = off
    gone = []
    for p in sorted((W / 'in').rglob('*')) if (W / 'in').exists() else []:
        if not p.is_file(): continue
        rel = str(p.relative_to(W / 'in')); lv = DATA / rel
        same = lv.exists() and lv.read_bytes() == p.read_bytes()
        if not same and lv.exists():
            try: same = load(lv) == load(p) and load(p) is not None
            except Exception: same = False  # noqa: BLE001
        if same: p.unlink(); gone.append(rel)
    keep = int(os.environ.get('WAITING_KEEP_GENS') or 2)   # Nov 2: the two newest undo generations are kept
    if keep > 0:
        for d in sorted(W.glob('previous-*')):
            try: g = int(d.name.split('-')[1])
            except ValueError: continue
            if g > keep: shutil.rmtree(d); gone.append(d.name + '/')
    if gone: log_action('tidy', f'{len(gone)} held copies / old generations removed'); print(f'::notice title=Waiting room tidy::{len(gone)} removed: {", ".join(gone[:8])}')
    return gone


def mode_check(promote):
    try: mode_tidy()
    except Exception as e: print(f'::error title=Waiting room tidy::stopped ({type(e).__name__}: {e}); nothing else changed')  # noqa: BLE001
    on = promote and os.environ.get('WAITING_ON') == '1'
    files = sorted(p for p in (W / 'in').rglob('*') if p.is_file() and re.search(r'\.json(\.gz)?$', p.name)) if (W / 'in').exists() else []   # Fable b: .json.gz too (never a silent stall)
    batch = {str(p.relative_to(W / 'in')): load(p) for p in files}
    ctx = {'set': batch}
    out = []
    for rel, new in batch.items():
        r = judge(rel, new, *live_of(rel), ctx=ctx); out.append(r)
        allowed = [k for k in (os.environ.get('PROMOTE_KINDS') or '').split(',') if k]   # only the bots Brandon switched on promote; held bots wait for chat 11
        if on and r['verdict'] in ('PASS', 'LIVE-FILTERED') and allowed and r['kind'] in allowed and r['kind'] not in NEVER_AUTO:
            promote_file(rel, r.get('out'), raw=(W / 'in' / rel))
            (W / 'in' / rel).unlink()
            tw = live_of(rel)[1]
            if tw and tw not in ('both', rel) and (DATA / tw).exists(): keep_generation(tw); (DATA / tw).unlink()   # one name only (chat 8 attack 5)
    held = [r for r in out if r['verdict'] == 'HOLD']
    rep = {'checked': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'switched_on': on, 'results': [{k: v for k, v in r.items() if k != 'out'} for r in out]}
    W.mkdir(parents=True, exist_ok=True)
    json.dump(rep, open(W / 'verdicts.json', 'w'), indent=1, ensure_ascii=False)
    try: grade_queue([r for r in out if (W / 'in' / r['path']).exists()])
    except Exception as e: print(f'::notice title=Waiting room::grade list skipped ({type(e).__name__}: {e})')  # noqa: BLE001
    lastv = load(W / 'verdicts-last.json', {}) or {}   # Nov 2 (storage): the log took 135,000 lines in 4 days, mostly the same PASS every 2 h
    for r in out:   # Fable note b: one line per verdict CHANGE, kept, so thresholds can be tuned from a month of data
        row = {'kind': r['kind'], 'path': r['path'], 'verdict': r['verdict'], 'why': r['why'][:4], 'notes': r['notes'][:3]}
        sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if lastv.get(r['path']) == sig: continue
        lastv[r['path']] = sig
        append_jsonl_gz(W / 'verdicts.jsonl', {'date': rep['checked'], **row})
    json.dump(lastv, open(W / 'verdicts-last.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'ok': rep['checked']}, open(W / 'heartbeat.json', 'w'))
    since = load(W / 'held-since.json', {}) or {}
    since = {k: v for k, v in since.items() if any(r['path'] == k for r in held)}   # a file no longer held drops out
    for r in held: since.setdefault(r['path'], TODAY.isoformat())
    json.dump(since, open(W / 'held-since.json', 'w'), indent=1)
    inbox = DATA / 'data' / 'status' / 'inbox-checkers.md'
    old = inbox.read_text(encoding='utf-8').splitlines() if inbox.exists() else []
    if held or any(l.startswith('- FROM WAITING ROOM') for l in old):   # chat 8 C2 + C4: ONE line per held file (replaced, never repeated), with its age
        keep = [l for l in old if not l.startswith('- FROM WAITING ROOM')]
        for r in held:
            days = (TODAY - dt.date.fromisoformat(since[r['path']])).days
            keep.append(look_line(r).replace(f'({TODAY})', f"(held since {since[r['path']]}" + (f', {days} days' if days else '') + ')'))
        inbox.parent.mkdir(parents=True, exist_ok=True); inbox.write_text('\n'.join(keep) + '\n', encoding='utf-8')
    print(f'::notice title=Waiting room::{len(out)} files: {sum(r["verdict"] != "HOLD" for r in out)} pass, {len(held)} held' + ('' if on else ' (NOT switched on: nothing promoted)'))


def keep_newer_overrides(live_d, new_d):
    """Nov 9 2026 weekly batch (lost Nov 8 edits): an overrides.json release must not wipe hand edits made on this copy that the
    incoming copy (built from KPC-Links) never saw. Release f2a68a32 (Nov 8, 2:06 PM CST) dropped 14 WSR corridor joins this way.
    Per park: missing from the incoming copy -> this copy's entry is carried; this copy's 'when' is NEWER -> its join/no/fp/nofp
    are merged in (the incoming copy wins on a clash; an id the incoming copy has on the opposite list is not brought back).
    A park the incoming copy changed later (its 'when' is the same or newer) is taken as is, so a real removal still lands.
    Returns (merged, [refs carried]); never blocks, only adds back."""
    lp = (live_d or {}).get('parks') or {}; npk = (new_d or {}).get('parks')
    if not isinstance(npk, dict): return new_d, []
    kept = []
    for ref, le in lp.items():
        if not isinstance(le, dict): continue
        ne = npk.get(ref)
        if ne is None: npk[ref] = le; kept.append(ref); continue
        if not isinstance(ne, dict) or str(le.get('when') or '') <= str(ne.get('when') or ''): continue
        moved = False
        for key, opp in (('join', 'no'), ('no', 'join')):
            for i in le.get(key) or []:
                if i in (ne.get(key) or []) or i in (ne.get(opp) or []): continue
                ne.setdefault(key, []).append(i); moved = True
                fk = 'fp' if key == 'join' else 'nofp'
                if i in (le.get(fk) or {}): ne.setdefault(fk, {}).setdefault(i, le[fk][i])
        if moved: ne['when'] = le['when']; ne['why'] = ((ne.get('why') or '') + ' | kept from the KPC-Data copy: ' + (le.get('why') or ''))[:2000]; kept.append(ref)
    return new_d, kept


def promote_file(rel, content=None, raw=None):
    """Fable c: the file goes live EXACTLY as the bot wrote it (its own bytes: indent, gzip), so git sees only real changes. Only a
    closures file with rows taken out is rewritten (indented, like the bot writes it)."""
    live = DATA / rel
    if str(rel).endswith('overrides.json') and live.exists():   # Nov 9: never lose a newer hand edit (see keep_newer_overrides)
        try:
            new_d = content if content is not None else json.load(open(raw, encoding='utf-8'))
            merged, kept = keep_newer_overrides(json.load(open(live, encoding='utf-8')), new_d)
            if kept:
                print(f'::warning title=Overrides kept::{rel}: {len(kept)} park(s) had newer edits here than the incoming copy and were '
                      f'kept: {", ".join(kept[:40])}{" ..." if len(kept) > 40 else ""}. Copy them into KPC-Links data/us-key/overrides.json.')
                content, raw = merged, None
        except Exception as e:  # noqa: BLE001  (a broken file is promoted as before; the check is reported, never blocks)
            print(f'::warning title=Overrides kept::check skipped for {rel}: {e}')
    if live.exists(): keep_generation(rel)
    live.parent.mkdir(parents=True, exist_ok=True)
    _tw = DATA / (str(rel)[:-3] if str(rel).endswith('.gz') else str(rel) + '.gz')   # Nov 1 (storage, 1 MB gzip): the other name goes, so x.json + x.json.gz are never both live
    if _tw.exists():
        try: keep_generation(str(_tw.relative_to(DATA)))
        except Exception: pass  # noqa: BLE001
        _tw.unlink()
    if content is None and raw is not None: shutil.copy2(raw, live); return
    if str(rel).endswith('.gz'):
        import gzip
        with gzip.open(live, 'wt', encoding='utf-8') as fh: json.dump(content, fh, indent=1, ensure_ascii=False)
    else: json.dump(content, open(live, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


GENS = 1   # Nov 1 storage fix (HQ 12:10 PM, Brandon GO): ONE undo copy on main; older copies stay in git history + the history bundle (was 3; chat 8 C1: keep the last 3 live copies (previous = 1, previous-2, previous-3), so undo can step past a bad copy that slipped through


def gen_dir(g): return W / ('previous' if g == 1 else f'previous-{g}')


def keep_generation(rel):
    for g in range(GENS, 1, -1):
        src, dst = gen_dir(g - 1) / rel, gen_dir(g) / rel
        if src.exists(): dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    p1 = gen_dir(1) / rel; p1.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(DATA / rel, p1)


def mode_undo(rel, gen=1):
    rel, _, g = str(rel).partition('@'); gen = int(g or gen)   # 'data/access/US-NY.json@2' = two copies back
    live, prev = DATA / rel, gen_dir(gen) / rel
    got = None
    if not prev.exists():   # Nov 7 (archive split): the undo copy may have moved to KPC-Archive; the manifest says so, and its sha256 is checked
        got = KA.fetch(prev.relative_to(DATA).as_posix(), DATA)
        if got is None: print(f'::notice title=Waiting room undo::no copy {gen} back of {rel}'); return False
    tmp = live.read_bytes() if live.exists() else None
    if got is None: shutil.copy2(prev, live)
    else: live.parent.mkdir(parents=True, exist_ok=True); live.write_bytes(got)
    if tmp is not None and gen == 1: prev.parent.mkdir(parents=True, exist_ok=True); prev.write_bytes(tmp)     # the copy we replaced becomes 'previous' (undo of the undo)
    log_action('undo', f'{rel}@{gen}')
    print(f'::notice title=Waiting room undo::{rel} put back to the copy {gen} back'); return True


def log_action(what, rel):
    W.mkdir(parents=True, exist_ok=True)
    append_jsonl_gz(W / 'verdicts.jsonl', {'date': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'kind': what, 'path': rel, 'verdict': what.upper(), 'by': os.environ.get('GITHUB_ACTOR') or 'local'})   # chat 8 C3: who / when for every undo and release


BOT_FOLDERS = {'access': 'data/access', 'campfed': 'data/campfed', 'campstate': 'data/campstate', 'campinfo': 'data/campinfo', 'trails': 'data/trails',
               'docs': 'data/docs', 'hours': 'data/hours', 'truth': 'data/truth', 'leads': 'data/access-leads', 'us-key': 'data/us-key', 'ca-key': 'data/ca-key',
               'intake': 'data/intake', 'fers': 'data/fers', 'pota': 'data/pota', 'closures': 'data/closures', 'wwff': 'data/wwff', 'cell': 'data/cell'}


def mode_undo_bot(bot, area=''):
    folder = BOT_FOLDERS.get(bot)
    if not folder: print(f'::notice title=Waiting room undo::unknown bot {bot} (one of {", ".join(BOT_FOLDERS)})'); return
    n = 0
    local = [str(p.relative_to(W / 'previous')) for p in sorted((W / 'previous' / folder).rglob('*.json'))] if (W / 'previous' / folder).exists() else []
    pre = (W / 'previous').relative_to(DATA).as_posix() + '/'   # Nov 7: copies that moved to KPC-Archive are listed by the manifest (no network for the list)
    moved = [a[len(pre):] for a in KA.listing(f'{pre}{folder}/', DATA) if a.endswith('.json')]
    for rel in sorted(set(local) | set(moved)):
        if area and area not in pathlib.Path(rel).name: continue
        n += mode_undo(rel)
    print(f'::notice title=Waiting room undo::{bot} {area or "all areas"}: {n} files put back')


def mode_release(rel):
    if '..' in str(rel) or str(rel).startswith('/') or not str(rel).startswith('data/'): print(f'::notice title=Waiting room release::refused: {rel} is not a data/ path'); return
    src = W / 'in' / rel
    if not src.exists(): print(f'::notice title=Waiting room release::nothing held at {rel}'); return
    if load(src) is None: print(f'::notice title=Waiting room release::refused: {rel} does not read as JSON'); return   # chat 8 retest 5
    kl, nl = keep_line(rel), not_line(rel)   # Nov 4: a person's keep (Brandon, directly (Mapping chat), 4:36 AM CST Nov 4) beats any YES or trusted-kind release
    if nl: print(f'::notice title=Waiting room release::refused: {rel} is not a trail line (data/waiting/known/trails.json not_lines); its home is {nl.get("home")}'); return
    if kl:
        g = (load(src) or {}).get('geometry') if isinstance(load(src), dict) else None
        if length_km(g) < .98 * float(kl.get('km') or 0) or len(coords(g)) < int(kl.get('points') or 0):
            print(f"::notice title=Waiting room release::refused: {rel} is shorter than the official line a person chose to keep ({kl.get('by')}); see data/waiting/known/trails.json"); return
    promote_file(rel, None, raw=src); src.unlink(); log_action('release', rel)
    print(f'::notice title=Waiting room release::{rel} released by a person (previous copy kept for undo)')


# ---- the REPLAY TEST (F-6): real bad outputs from git history must ALL hold; the good outputs must ALL pass
def git_json(repo, sha, path):
    base = DATA if repo == 'data' else LINKS
    if sha in ('live', 'HEAD', None):   # Nov 2: a live file gzipped in the storage fix (x.json -> x.json.gz) is read from its twin
        if not (base / path).exists() and (base / (str(path) + '.gz')).exists():
            import gzip
            return json.loads(gzip.decompress((base / (str(path) + '.gz')).read_bytes()).decode('utf-8'))
        return load(base / path)
    p = subprocess.run(['git', '-C', str(base), 'show', f'{sha}:{path}'], capture_output=True)
    if p.returncode != 0 and repo == 'data':   # Nov 2: history restart; the case files live on branch replay-files (<commit>/<path>)
        rf = pathlib.Path(os.environ.get('REPLAY_FILES') or '../replay-files') / sha / path
        if rf.exists(): p = subprocess.CompletedProcess([], 0, rf.read_bytes(), b'')
    if p.returncode != 0: raise Unsure(f'{repo} {sha}:{path} not in the git history (needs fetch-depth 0) nor on branch replay-files')
    try: return json.loads(p.stdout.decode('utf-8'))
    except Exception: import gzip; return json.loads(gzip.decompress(p.stdout).decode('utf-8'))  # noqa: E401


def transform(d, how):
    d = copy.deepcopy(d)
    op, _, arg = how.partition(':')
    if op == 'shrink':
        f = float(arg)
        for k in ('parks', 'camps', 'leads', 'items', 'spots'):
            v = d.get(k)
            if isinstance(v, dict): d[k] = dict(list(v.items())[:int(len(v) * f)])
            elif isinstance(v, list): d[k] = v[:int(len(v) * f)]
    elif op == 'count':                 # pota index: 'count:0.97'
        d['parks'] = int((d.get('parks') or 0) * float(arg))
    elif op == 'spread_fee':            # copy one park's fee line onto N parks (statewide price lesson)
        P = d['parks']; src = next(r['fees'][0] for r in P.values() if r.get('fees'))
        for r in list(P.values())[:int(arg)]: r['fees'] = [dict(src)]
    elif op == 'drop_spot':             # 'drop_spot:US-0050+US-10105': every 2-fer row holding both parks removed
        want = set(arg.split('+'))
        d['spots'] = [s for s in d.get('spots') or [] if not (isinstance(s, dict) and want <= set(s.get('refs') or []))]
    elif op == 'set':                   # 'set:{"status":"READY","rows":[...]}'
        d = json.loads(arg)
    # ---- chat 8's attacks (Oct 29), kept as permanent replay cases
    elif op == 'rotate_refs':           # A1: every candidate pair wrong, same count, new ids
        C = [s for s in d.get('spots') or [] if isinstance(s, dict) and str(s.get('status', '')).startswith('candidate')]
        refs = [s['refs'][0] for s in C]
        for i, s in enumerate(C):
            s['refs'] = [refs[i], refs[(i + 7) % len(refs)]] if len(refs) > 7 else s['refs'][::-1] + ['US-99999']; s['id'] = 'X' + str(i)
    elif op == 'shuffle_outlines':      # A2: every outline moved to another park, same count
        P = [r for r in (d.get('parks') or {}).values() if r.get('m')]
        ms = [r['m'] for r in P]
        for i, r in enumerate(P): r['m'] = ms[(i + 11) % len(ms)]
    elif op == 'fake_area':             # A3: 20% fake 'area' rows between far-apart parks
        S = [s for s in d.get('spots') or [] if isinstance(s, dict)]
        refs = sorted({r for s in S for r in s.get('refs') or []})
        add = []
        for i in range(int(len(S) * float(arg))):
            a, b = refs[i % len(refs)], refs[(i * 37 + len(refs) // 2) % len(refs)]
            pa, pb = pin_of(a), pin_of(b)
            if a != b and pa and pb and km(pa[0], pa[1], pb[0], pb[1]) > 150:
                add.append({'id': f'FAKE{i}', 'kind': 'area', 'refs': [a, b], 'status': 'candidate', 'passes': [1, 1, 1], 'center': [pa[0], pa[1]]})
        d['spots'] = S + add
    elif op == 'near_swap':             # chat 8 retest 1: a share of candidate pairs get a partner moved to another park within 20 km
        C = [s for s in d.get('spots') or [] if isinstance(s, dict) and str(s.get('status', '')).startswith('candidate')]
        allr = sorted({r for s in d.get('spots') or [] if isinstance(s, dict) for r in s.get('refs') or []} | set(parks(st_of(d.get('st') or 'US-OH.json') or 'OH')))
        n = 0
        for s in C:
            if n >= max(1, int(len(C) * float(arg))): break
            a, b = s['refs'][0], s['refs'][-1]; pa = pin_of(b)
            if not pa: continue
            near = [r for r in allr if r not in s['refs'] and pin_of(r) and km(pa[0], pa[1], *pin_of(r)[:2]) < 20]
            if near: s['refs'] = [a, near[0]]; s['id'] = 'NEAR' + str(n); n += 1
    elif op == 'shuffle_rename':        # chat 8 retest 2 (A2d): outlines swapped AND the park renamed to the swapped layer's name
        P = [r for r in (d.get('parks') or {}).values() if r.get('m')]
        ms = [r['m'] for r in P]
        for i, r in enumerate(P[:int(len(P) * float(arg or 1))]):
            r['m'] = ms[(i + 11) % len(ms)]; r['n'] = r['m'][0][1]
    elif op == 'status_unchecked':      # A6: a real status word with unchecked rows
        d['status'] = arg
        for s in (d.get('spots') or [])[:40]:
            if isinstance(s, dict): s['water'] = 'not checked'
    elif op == 'fake_passes':           # A7: truthy pass flags, no pass record on the rows
        for k in ('pass1', 'pass2', 'pass3'): d[k] = True
        for s in d.get('spots') or []:
            if isinstance(s, dict): s.pop('passes', None)
    return d


def mode_replay():
    cases = (load(W / 'replay.json', {}) or {}).get('cases') or []
    if not cases: print('REPLAY=FAIL (no cases)'); return False
    rows, ok_all = [], True
    for c in cases:
        if c.get('retired'): rows.append(f"| retired | {c['name']} | {c['expect']} | {c['retired']} |"); continue
        try:
            batch, live = {}, {}
            for f in c['files']:
                new = git_json(c['repo'], f['new'], f.get('src_path') or f['path'])
                if f.get('transform'): new = transform(new, f['transform'])
                batch[f['path']] = new
                lp = f.get('live_path') or f['path']   # chat 8 attack 5: the live copy may sit under the other name (.json vs .json.gz)
                live[f['path']] = (git_json(c['repo'], f.get('live', 'live'), lp) if f.get('live') != 'none' else None, None if lp == f['path'] else ('both' if f.get('both') else lp))
            ctx = {'set': batch}
            res = [judge(p, n, *live[p], ctx=ctx) for p, n in batch.items()]
        except Exception as e:  # noqa: BLE001
            res = [{'path': '?', 'verdict': 'HOLD', 'why': [f'case could not load: {e}'], 'notes': []}]
        caught = any(r['verdict'] in ('HOLD', 'LIVE-FILTERED') and (not c.get('catch') or re.search(c['catch'], ' '.join(r['why'] + r['notes']), re.I)) for r in res)
        passed = all(r['verdict'] == 'PASS' for r in res)
        good = caught if c['expect'] == 'HOLD' else passed
        ok_all &= good
        rows.append(f"| {'ok' if good else '**MISS**'} | {c['name']} | {c['expect']} | " + ' / '.join(f"{r['verdict']}: {('; '.join(r['why'] + r['notes']))[:160]}" for r in res) + ' |')
    md = ['# Waiting room REPLAY TEST', f'Run {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%MZ}: **{"PASS" if ok_all else "FAIL"}** ({sum(r.startswith("| ok") for r in rows)} of {sum(not r.startswith("| retired") for r in rows)} cases right). '
          'Every real bad output must be HELD (or, closures, have its bad rows taken out); every good output must PASS.', '',
          '| result | case | expect | what the checker said |', '|---|---|---|---|'] + rows
    W.mkdir(parents=True, exist_ok=True)
    (W / 'replay.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('\n'.join(rows)); print('REPLAY=' + ('PASS' if ok_all else 'FAIL'))
    print(f'::notice title=Waiting room replay::{"PASS" if ok_all else "FAIL"}: {sum(r.startswith("| ok") for r in rows)} of {sum(not r.startswith("| retired") for r in rows)} cases right ({sum(r.startswith("| retired") for r in rows)} retired)')
    return ok_all


if __name__ == '__main__':
    a = sys.argv[1:] or ['check']
    try:
        if a[0] == 'check': mode_check('--promote' in a)
        elif a[0] == 'replay': mode_replay()
        elif a[0] == 'undo': mode_undo(a[1])
        elif a[0] == 'undo-bot': mode_undo_bot(a[1], a[2] if len(a) > 2 else '')
        elif a[0] == 'release': mode_release(a[1])
        elif a[0] == 'divert': mode_divert(a[1:])
        elif a[0] == 'resume': mode_resume(a[1:])
        else: print(__doc__)
    except Exception as e:  # noqa: BLE001  (fail closed: nothing was promoted; one line for chat 11)
        print(f'::notice title=Waiting room::checker stopped ({type(e).__name__}: {str(e)[:200]}): nothing promoted, everything waits')
    sys.exit(0)
