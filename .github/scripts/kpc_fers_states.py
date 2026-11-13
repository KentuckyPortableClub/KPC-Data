#!/usr/bin/env python3
"""2-FERS PER STATE / PROVINCE (KPC owner, 2026-11-12: KISS, fix only the affected areas; the 2-fer half of the shared per-area design,
same units, stamps and reason codes as the key half in KPC-Links).

THE UNIT is the US state / Canadian province: data/fers/<ST>.json (and its waiting-room copy data/waiting/in/data/fers/<ST>.json).
The 14 areas of .github/fers-areas.json stay only as a way to GROUP states into jobs. One area list for every 2-fer workflow:
.github/fers-areas.json (the bot, the chain, the lines, the small batches, the water tiles); the chain's old list R is retired.

  pick      after a 2-fer job (kpc-fers.yml Save / break save, kpc-fers-line.yml checker Save): decide PER STATE what is saved.
            env STATES='US-FL US-GA' KPCDATA=kpcdata [BASE_REF=<KPC-Data commit the job started from>] [PLAN_STATES=...] [RUN_ID, JOB]
            [ONLY_FINISHED=1: only states whose file finished every pass today (the break save)]
            A green state's new file is copied into KPCDATA/data/fers (the waiting-room divert then holds it, as before) and stamped.
            A state is KEPT (its previous saved file byte for byte, no stamp, listed red) when:
              not-built   the job made no file for it, or the file does not read
              failed      the file says incomplete (stopped for time) and a saved file exists; or the saved copy changed on main
                          since this job started ('stale base': another run saved it; never overwritten)
              reused      nothing it reads changed and the saved file has more passes done than the new one
              join-refused  two states of this job hold the same pair after the owner rule: NOTHING of this job is saved
            Prints the run table (state | verdict | saved or kept | hash stamped | why) and writes it to GITHUB_STEP_SUMMARY.
            Exit 0 = something saved or nothing to save, 2 = join-refused (nothing saved), 3 = every state kept.
            The red list goes to $RUNNER_TEMP/kpc-fers-red.txt (the job turns red after its save).
  hash      env STATES=... [LINKS=.] [KPCDATA=kpcdata]: the per-state 2-fer hash and its parts (JSON)
  plan      env STATES='' (all) [LINKS=links] [KPCDATA=.]: the run table a per-state plan WOULD make (shadow) and, only with
            KPC_AREA_HASH=reuse (default OFF until the owner signs D1-D9), the states it would leave out. FORCE=full = every state.
  neighbours  the pair-neighbours of each state, from the saved 2-fer results (JSON)

Owner rule for a pair that crosses a state line: the pair (its sorted park refs + kind) belongs to ONE state, the alphabetically
first state among its parks that lie in one state (US-FL + US-GA -> US-FL; CA-NB + US-ME -> CA-NB); a park POTA lists in several
states (a national trail) does not decide, and a row with no one-state park stays in its file. A job drops a row it does not own only
when the owner's file (new in this job, or saved) already holds that pair; otherwise it keeps it (a row is never lost). Two files
of one job holding one pair = join-refused (fail closed). KPC_FERS_PAIR_OWNER=off turns the drop off (the check stays).

Per-state 2-fer hash (composition ah1 of the shared scheme): sha256 over '<part>\\0<sha256 hex>\\n' of the sorted parts, 12 hex:
  version            sha256('ah1' NUL + the fers value of .github/key-rules-version.json)
  code               the fers CODE hash: KPC-Links kpc_area_hash.code_hash(repo, 'fers') (the key half) when that module exists,
                     else kpc_key_freeze.rules_hash('fers') (the same value): a code edit moves every state, unless the key half's
                     D4 reader (kpc_area_hash.proof_valid) accepts a 'no result change' proof (plan only, reuse on only)
  up:key:<ST>        the state's key file, canonical JSON of {st, parks without the per-park 'read' date}
  up:key:<N>         the same for every neighbour N the state's 2-fers ACTUALLY pair with (saved results; a park listed in several
                     states counts all of them, fail closed); a state with no saved result pairs with every state of its key
  up:outline:<ST|N>  the state's outline files in data/outlines (KPC-Links), all parts, decompressed; missing = 'none'
  data:<file>        the rows of the hand files 2-fers read (approximate outlines / traces, point circles, overrides) for the
                     parks of the state and of its pair neighbours
  pins               data/parkinfo (KPC-Data) of the state, first 7 fields of each park
NOT covered (so reuse stays OFF): the boundary-cache saved copies kpc_fers.py reads (not in git; no copy manifest yet), live reads,
host verdicts. That is why KPC_AREA_HASH is off by default and the monthly full run stays."""
import gzip, hashlib, json, os, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
COMPOSITION = 'ah1'
STATE_RX = re.compile(r'^(US|CA)-[A-Z]{2}$')
REF_RX = re.compile(r'^[A-Z0-9]{1,4}-\d{3,6}$')
HEADER = {'about', 'note', 'notes', 'updated', 'when', 'date', 'from', 'format'}
REASONS = ('built', 'reused', 'failed', 'not-built', 'not-planned', 'cancelled', 'join-refused')   # the shared scheme's codes


# ------------------------------------------------------------------ areas (the ONE list)

def key_builds(links):
    """Quality D1 (KPC owner, 2026-11-13): the real key build ids this 2-fer was made from, per kind (US and CA, so a
    cross-border pair can check both). Read from the Links key indexes; a kind with no readable build is left out."""
    out = {}
    for kind, rel in (('US', 'data/us-key/index.json'), ('CA', 'data/ca-key/index.json')):
        try:
            b = str((json.loads((pathlib.Path(links) / rel).read_text(encoding='utf-8')) or {}).get('build') or '')
        except (OSError, ValueError, TypeError, AttributeError):
            b = ''
        if b: out[kind] = b
    return out

def areas(root=ROOT):
    return json.load(open(pathlib.Path(root) / '.github/fers-areas.json', encoding='utf-8'))['areas']


def area_of_state(root=ROOT):
    return {s: a for a, v in areas(root).items() for s in v.split()}


def state_tag(st):
    """the tag of a one-state job: US-FL -> fl, CA-ON -> caon (the old own-state line tags: ky, oh, mi, ut)"""
    return st.lower().replace('us-', '').replace('-', '')


# ------------------------------------------------------------------ small helpers
def canon(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else str(b).encode()).hexdigest()


def load(p, d=None):
    p = pathlib.Path(p)
    try:
        b = p.read_bytes()
        return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
    except Exception:  # noqa: BLE001
        return d


def state_file(base, st):
    """(path, data) of data/fers/<st>.json or .json.gz under base, or (None, None)"""
    for n in (f'{st}.json', f'{st}.json.gz'):
        p = pathlib.Path(base) / n
        if p.exists(): return p, load(p)
    return None, None


def saved_copy(kpcdata, st):
    """the previous SAVED file of a state: its waiting-room copy when one is held, else the live one. -> (relpath, path, data)"""
    k = pathlib.Path(kpcdata)
    for d in ('data/waiting/in/data/fers', 'data/fers'):
        p, j = state_file(k / d, st)
        if p: return str(p.relative_to(k)), p, j
    return None, None, None


def passes(d):
    return {k: d.get(k) for k in ('pass1', 'pass2', 'pass3', 'pass5') if isinstance(d, dict) and d.get(k)}


def n_passes(d):
    return len(passes(d))


# ------------------------------------------------------------------ park -> state, owner rule, neighbours
def park_states(kpcdata):
    """ref -> frozenset of states from KPC-Data data/parkinfo (US-XX.json, CA.json: province at index 10). A park POTA lists in
    several states (the Appalachian Trail, the Trail of Tears, ...) has all of them."""
    out = {}
    pi = pathlib.Path(kpcdata) / 'data/parkinfo'
    for f in sorted(pi.glob('US-??.json')):
        for r in ((load(f, {}) or {}).get('parks') or {}): out.setdefault(r, set()).add(f.stem)
    for r, v in ((load(pi / 'CA.json', {}) or {}).get('parks') or {}).items():
        if isinstance(v, list) and len(v) > 10 and v[10]: out.setdefault(r, set()).add('CA-' + str(v[10]))
    return {r: frozenset(v) for r, v in out.items()}


def _sts(st_of, r):
    v = st_of.get(r)
    return set(v) if isinstance(v, (set, frozenset)) else ({v} if v else set())


def pair_key(s):
    return '+'.join(sorted(s.get('refs') or [])) + '@' + str(s.get('kind'))


def owner(s, st_of, fallback):
    """the alphabetically first state among the parks of the row that lie in ONE state; a park listed in several states (a national
    trail) does not decide; no one-state park = the file's own state (the row stays where it is)"""
    one = sorted({next(iter(_sts(st_of, r))) for r in s.get('refs') or [] if len(_sts(st_of, r)) == 1})
    return one[0] if one else fallback


def neighbours(kpcdata, st_of=None):
    """{state: set(neighbour states)} from every saved 2-fer state file (held and live): N is a neighbour of S when a saved row of
    S or N joins a park of S with a park of N. A state with no saved file is not in the result (= unknown: fail closed)."""
    st_of = st_of if st_of is not None else park_states(kpcdata)
    nb = {}
    for d in ('data/waiting/in/data/fers', 'data/fers'):
        for f in sorted((pathlib.Path(kpcdata) / d).glob('*-??.json*')):
            st = re.sub(r'\.json(\.gz)?$', '', f.name)
            if not STATE_RX.match(st): continue
            nb.setdefault(st, set())
            for s in (load(f, {}) or {}).get('spots') or []:
                sts = set().union(*[_sts(st_of, r) for r in s.get('refs') or []]) if s.get('refs') else set()   # a multi-state park: every state it is in (fail closed)
                for a in sts | {st}:
                    for b in sts | {st}:
                        if a != b: nb.setdefault(a, set()).add(b)
    return nb


# ------------------------------------------------------------------ the per-state hash
def _key_part(links, st):
    kind = 'ca-key' if st.startswith('CA-') else 'us-key'
    k = load(pathlib.Path(links) / f'data/{kind}/{st}.json')
    if not isinstance(k, dict): return 'missing'
    parks = {r: {a: b for a, b in v.items() if a != 'read'} if isinstance(v, dict) else v for r, v in (k.get('parks') or {}).items()}
    return sha(canon({'st': st, 'parks': parks}))


def _outline_part(links, st):
    fs = sorted((pathlib.Path(links) / 'data/outlines').glob(f'{st}*.geojson*'))
    if not fs: return 'none'
    h = hashlib.sha256()
    for f in fs:
        b = f.read_bytes()
        h.update(f.name.encode() + b'\0' + (gzip.decompress(b) if f.suffix == '.gz' else b))
    return h.hexdigest()


def _ref_rows(obj):
    """the dict of ref -> row inside a hand file (top level, or under 'parks' / 'refs' / 'items')"""
    if not isinstance(obj, dict): return {}
    for k in ('parks', 'refs', 'items', 'rows'):
        if isinstance(obj.get(k), dict): return obj[k]
    return {k: v for k, v in obj.items() if REF_RX.match(str(k))}


HAND = ('data/fers-approx-outlines.json', 'data/point-circles.json', 'data/us-key/overrides.json', 'data/ca-key/overrides.json')
UNREADABLE = '!unreadable'


def hand_rows(links):
    """{hand file: its ref rows}. Nov 12 2026 (KPC owner; KPC-Links #151 split): an overrides.json is read WHOLE (manifest + its parts,
    kpc_overrides_whole), so a state's 'data:' part is the same in both layouts and an edit in a part file still moves it. A set that
    cannot be read whole gives {UNREADABLE: why}: state_hash then stamps a value no readable set has (every state differs; never a
    partial slice that looks current)."""
    out = {}
    for f in HAND:
        if f.endswith('/overrides.json'):
            sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
            import kpc_overrides_whole as OVW
            try: out[f] = _ref_rows(OVW.load_whole(pathlib.Path(links) / f, missing_ok=True, links=links))
            except OVW.OverridesError as e:
                print(f'::warning title=2-fer hash::{f} cannot be read whole ({str(e)[:200]}): its part of every state hash is marked unreadable', file=sys.stderr)
                out[f] = {UNREADABLE: str(e)}
        else: out[f] = _ref_rows(load(pathlib.Path(links) / f))
    return out


def _mod(links, name):
    """KPC-Links' own copy of a module, loaded from that tree by path (never a cached module of another tree)"""
    import importlib.util
    f = pathlib.Path(links) / '.github/scripts' / f'{name}.py'
    if not f.exists(): return None
    sp = importlib.util.spec_from_file_location(f'_kpc_{name}_{abs(hash(str(f)))}', f)
    m = importlib.util.module_from_spec(sp)
    sys.path.insert(0, str(f.parent))
    try: sp.loader.exec_module(m)
    finally: sys.path.remove(str(f.parent))
    return m


def code_hash(links):
    """the shared 2-fer code hash = the fers CODE hash of the key half (KPC-Links kpc_area_hash.code_hash(repo, 'fers'), the same
    value as kpc_key_freeze.rules_hash('fers')): one code hash, never two"""
    try:
        AH = _mod(links, 'kpc_area_hash')
        if AH is not None and hasattr(AH, 'code_hash'): return 'rules:' + str(AH.code_hash(str(links), 'fers'))
    except Exception:  # noqa: BLE001
        pass
    r = fers_rules(links)
    return 'rules:' + r if r else 'unknown'


def fers_rules(links):
    try:
        KF = _mod(links, 'kpc_key_freeze')
        return KF.rules_hash('fers', str(links)) if KF is not None else ''
    except Exception:  # noqa: BLE001
        return ''


def version_part(links):
    """the shared scheme's version part: sha256('ah1' + NUL + str(the fers value of .github/key-rules-version.json))"""
    v = load(pathlib.Path(links) / '.github/key-rules-version.json', None)
    return sha(COMPOSITION + '\0' + str(v.get('fers') if isinstance(v, dict) else None))


def state_hash(st, links, kpcdata, nb=None, st_of=None, code=None, hand=None):
    """-> (hash12, parts {name: sha256 hex}, neighbours used)"""
    links, kpcdata = pathlib.Path(links), pathlib.Path(kpcdata)
    st_of = st_of if st_of is not None else park_states(kpcdata)
    nb = nb if nb is not None else neighbours(kpcdata, st_of)
    mine = nb.get(st)
    if mine is None:   # no saved result for this state: every state of the same key counts (fail closed)
        mine = {s for v in st_of.values() for s in _sts({0: v}, 0) if s[:3] == st[:3] and s != st}
    used = sorted(mine)
    parts = {'version': version_part(links), 'code': sha(code if code is not None else code_hash(links))}
    for s in [st] + used:
        parts[f'up:key:{s}'] = _key_part(links, s)
        parts[f'up:outline:{s}'] = _outline_part(links, s)
    refs = {r for r in st_of if _sts(st_of, r) & ({st} | set(mine))}
    hand = hand if hand is not None else hand_rows(links)
    for f, rows in hand.items():
        if UNREADABLE in rows: parts[f'data:{f}'] = sha(UNREADABLE); continue
        parts[f'data:{f}'] = sha(canon({r: {k: v for k, v in rows[r].items() if k not in HEADER} if isinstance(rows[r], dict) else rows[r]
                                       for r in sorted(refs & set(rows))}))
    pf = kpcdata / ('data/parkinfo/CA.json' if st.startswith('CA-') else f'data/parkinfo/{st}.json')
    pk = (load(pf, {}) or {}).get('parks') or {}
    parts['pins'] = sha(canon({r: (v[:7] if isinstance(v, list) else v) for r, v in sorted(pk.items()) if st in _sts(st_of, r)}))
    h = hashlib.sha256(''.join(f'{k}\0{v}\n' for k, v in sorted(parts.items())).encode()).hexdigest()[:12]
    return h, parts, used


def stamp_path(kpcdata, st):
    return pathlib.Path(kpcdata) / f'data/fers/stamps/{st}.json'


# ------------------------------------------------------------------ pick (the per-state save)
def _git(kpcdata, *a):
    return subprocess.run(['git', '-C', str(kpcdata), *a], capture_output=True, text=True)


def changed_since(kpcdata, base, paths):
    """the paths whose blob on the newest main differs from `base` (another run saved them since this job started).
    None = main could not be read (fail closed: the caller keeps the saved file)."""
    if _git(kpcdata, 'fetch', '-q', 'origin', 'main').returncode: return None
    out = []
    for p in paths:
        a = _git(kpcdata, 'rev-parse', '-q', '--verify', f'{base}:{p}').stdout.strip()
        b = _git(kpcdata, 'rev-parse', '-q', '--verify', f'FETCH_HEAD:{p}').stdout.strip()
        if a != b: out.append(p)
    return out


def own_filter(st, new, mine_new, saved_keys, st_of, on=True):
    """drop the rows of `new` (state st) whose pair belongs to another state that already holds the pair (new in this job, or saved).
    -> (rows kept, keys dropped)"""
    keep, dropped = [], set()
    for s in new.get('spots') or []:
        k = pair_key(s); o = owner(s, st_of, st)
        if on and o != st and (k in mine_new.get(o, set()) or k in saved_keys.get(o, set())): dropped.add(k); continue
        keep.append(s)
    return keep, dropped


def pick(env=os.environ, out=sys.stdout):
    kpcdata = pathlib.Path(env.get('KPCDATA') or 'kpcdata'); links = pathlib.Path(env.get('LINKS') or '.')
    work = pathlib.Path(env.get('WORK') or 'data/fers')
    states = [s for s in (env.get('STATES') or '').split() if STATE_RX.match(s)]
    if (env.get('REGION') == 'ky') or 'US-KY' in (env.get('STATES') or '').split(): states = sorted(set(states) | {'US-KY'})
    base = env.get('BASE_REF') or 'HEAD'
    today = env.get('TODAY') or time.strftime('%Y-%m-%d')
    only_finished = env.get('ONLY_FINISHED') == '1'
    st_of = park_states(kpcdata)
    nb = neighbours(kpcdata, st_of)
    code = code_hash(links); rules = fers_rules(links)
    hand = hand_rows(links)
    rows, new_files = {}, {}
    # 1 read every new file and its saved copy
    for st in states:
        p, d = state_file(work, st)
        rel, sp, sd = saved_copy(kpcdata, st)
        rows[st] = {'st': st, 'new': d, 'path': p, 'saved_rel': rel, 'saved': sd}
        if p is None or not isinstance(d, dict): rows[st].update(verdict='not-built', why='the job made no readable file for this state'); continue
        if only_finished and not (str(d.get('pass5') or '') == today and not d.get('incomplete')):
            rows[st].update(verdict='not-built', why='the run broke before this state finished every pass'); continue
        if d.get('incomplete') and sd is not None:
            rows[st].update(verdict='failed', why=f"short: {str(d.get('incomplete'))[:80]}"); continue
        new_files[st] = d
    # 2 stale base: the saved copy changed on main since the job started -> never overwritten
    cand = [st for st in new_files]
    paths = sorted({f'data/waiting/in/data/fers/{st}{x}' for st in cand for x in ('.json', '.json.gz')} | {f'data/fers/{st}{x}' for st in cand for x in ('.json', '.json.gz')})
    moved = changed_since(kpcdata, base, paths) if cand and env.get('KPC_FERS_NO_BASE_CHECK') != '1' else []
    for st in cand:
        mv = None if moved is None else [p for p in moved if f'/{st}.json' in p]
        if mv is None: rows[st].update(verdict='failed', why='main could not be read to check the saved copy (fail closed): kept'); new_files.pop(st)
        elif mv: rows[st].update(verdict='failed', why=f'stale base: {mv[0]} was saved by another run since this job started: kept, run this state again'); new_files.pop(st)
    # 3 hashes; reused when nothing changed and the saved file is further along
    for st in list(new_files):
        h, parts, used = state_hash(st, links, kpcdata, nb, st_of, code, hand)
        rows[st].update(area_hash=h, area_parts={k: v[:12] for k, v in parts.items()}, nb=used)
        old = load(stamp_path(kpcdata, st), {}) or {}
        sd = rows[st]['saved']
        if old.get('area_hash') == h and sd is not None and n_passes(sd) > n_passes(new_files[st]) and not sd.get('incomplete'):
            rows[st].update(verdict='reused', why=f'nothing it reads changed and the saved file has {n_passes(sd)} passes (new: {n_passes(new_files[st])}): kept'); new_files.pop(st)
    # 4 the owner rule, then the in-job double-write check
    on = (env.get('KPC_FERS_PAIR_OWNER') or 'on').lower() not in ('off', '0', 'no')
    mine_new = {st: {pair_key(s) for s in d.get('spots') or []} for st, d in new_files.items()}
    saved_keys = {}
    for d in ('data/waiting/in/data/fers', 'data/fers'):
        for f in (kpcdata / d).glob('*-??.json*'):
            s_ = re.sub(r'\.json(\.gz)?$', '', f.name)
            if STATE_RX.match(s_) and s_ not in saved_keys and s_ not in new_files: saved_keys[s_] = {pair_key(x) for x in (load(f, {}) or {}).get('spots') or []}
    final = {}
    for st in sorted(new_files):
        keep, dropped = own_filter(st, new_files[st], mine_new, saved_keys, st_of, on)
        if dropped:
            new_files[st] = dict(new_files[st], spots=keep); rows[st]['dropped'] = len(dropped)
        final[st] = {pair_key(s) for s in keep}
    seen, clash = {}, []
    for st, ks in final.items():
        for k in ks:
            if k in seen: clash.append((k, seen[k], st))
            seen.setdefault(k, st)
    if clash:
        for st in rows:
            if st in new_files: rows[st].update(verdict='join-refused', why=f'{len(clash)} pair(s) in two files of this job, e.g. {clash[0][0]} in {clash[0][1]} and {clash[0][2]}: NOTHING saved')
        new_files = {}
    # 5 copy the green states into KPC-Data and stamp them (only what was rebuilt is stamped)
    for st, d in new_files.items():
        src = rows[st]['path']
        dst_dir = kpcdata / 'data/fers'; dst_dir.mkdir(parents=True, exist_ok=True)
        if rows[st].get('dropped'):
            b = json.dumps(d, ensure_ascii=False).encode()
            if src.suffix == '.gz': b = gzip.compress(b, 9, mtime=0)
        else: b = src.read_bytes()
        dst = dst_dir / src.name; twin = dst_dir / (src.name[:-3] if src.name.endswith('.gz') else src.name + '.gz')
        if not (dst.exists() and dst.read_bytes() == b): dst.write_bytes(b)
        if twin.exists(): twin.unlink()   # the new copy replaces the other name (.json vs .json.gz), so a stale twin never wins
        stp = stamp_path(kpcdata, st); stp.parent.mkdir(parents=True, exist_ok=True)
        rec = {'format': 1, 'st': st, 'composition': COMPOSITION, 'rules': rules, 'area_hash': rows[st]['area_hash'], 'area_parts': rows[st]['area_parts'],
               'neighbours': rows[st]['nb'], 'out_sha': sha(b), 'built_sha': _git(links, 'rev-parse', 'HEAD').stdout.strip() or env.get('BUILT_SHA', ''),
               'data_sha': base if base != 'HEAD' else _git(kpcdata, 'rev-parse', 'HEAD').stdout.strip(), 'passes': passes(d),
               'run': env.get('GITHUB_RUN_ID', ''), 'job': env.get('JOB') or '', 'key_source': env.get('KEY_SOURCE') or 'live', 'key_builds': key_builds(links), 'why': 'built'}
        stp.write_text(json.dumps(rec, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        rows[st].update(verdict='built', why='rebuilt and saved (held in the waiting room)' + (f"; {rows[st]['dropped']} pair(s) left to their owner state" if rows[st].get('dropped') else ''))
    # 6 the run table
    red = [st for st, r in rows.items() if r['verdict'] not in ('built', 'reused')]   # reused = nothing changed, nothing lost: not red
    lines = ['| state | built? | verdict | saved or kept from main | hash stamped | why |', '|---|---|---|---|---|---|']
    for st in states:
        r = rows[st]; b = r['verdict'] == 'built'
        lines.append(f"| {st} | {'yes' if b else 'no'} | {r['verdict']} | {'saved' if b else 'kept from main'} | {r.get('area_hash', '-') if b else '-'} | {r['verdict']}: {r['why']} |")
    print('\n'.join(lines), file=out)
    if env.get('GITHUB_STEP_SUMMARY'):
        with open(env['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as o: o.write('**2-fers per state** (only what was rebuilt is stamped)\n\n' + '\n'.join(lines) + '\n')
    for st in red:
        print(f"::error title=2-fers {st}::{rows[st]['verdict']}: {rows[st]['why']}", file=out)
    rf = pathlib.Path(env.get('RUNNER_TEMP') or '/tmp') / 'kpc-fers-red.txt'
    with open(rf, 'a', encoding='utf-8') as o:
        for st in red: o.write(f"{st} {rows[st]['verdict']}: {rows[st]['why']}\n")
    code_ = 2 if clash else (3 if states and not new_files and red and len(red) == len(states) else 0)
    return code_, rows


# ------------------------------------------------------------------ plan (shadow table; reuse only behind the switch)
def proof(links, frm, to):
    """(valid, id or why): the D4 'no result change' proof, read ONLY by the key half's reader (KPC-Links kpc_area_hash.proof_valid).
    No reader there = no proof (fail closed: a shared-code change rebuilds every state)."""
    try:
        AH = _mod(links, 'kpc_area_hash')
        if AH is not None and hasattr(AH, 'proof_valid'): return AH.proof_valid(str(links), 'fers', frm, to)
    except Exception as e:  # noqa: BLE001
        return False, f'proof reader failed ({type(e).__name__})'
    return False, 'no proof reader in KPC-Links (kpc_area_hash.proof_valid)'



def plan(env=os.environ, out=sys.stdout):
    links = pathlib.Path(env.get('LINKS') or 'links'); kpcdata = pathlib.Path(env.get('KPCDATA') or '.')
    st_of = park_states(kpcdata); nb = neighbours(kpcdata, st_of); code = code_hash(links); cur = fers_rules(links)
    hand = hand_rows(links)
    want = [s for s in (env.get('STATES') or '').split() if STATE_RX.match(s)] or sorted(area_of_state(kpcdata if (kpcdata / '.github/fers-areas.json').exists() else ROOT))
    mode = (env.get('KPC_AREA_HASH') or 'shadow').strip().lower()   # the shared switch: shadow (default) | add | reuse
    reuse = mode == 'reuse' and (env.get('FORCE') or '').lower() != 'full'
    rows, build = [], []
    for st in want:
        h, parts, used = state_hash(st, links, kpcdata, nb, st_of, code, hand)
        old = load(stamp_path(kpcdata, st), {}) or {}
        _, sp, sd = saved_copy(kpcdata, st)
        moved = sorted(k for k, v in parts.items() if (old.get('area_parts') or {}).get(k) != v[:12]) if old else ['(no stamp)']
        file_ok = bool(old) and sd is not None and old.get('out_sha') == sha(sp.read_bytes()) and not sd.get('incomplete')
        same = file_ok and old.get('area_hash') == h and old.get('rules') == cur
        why = 'inputs and code unchanged' if same else ''
        if file_ok and not same and old.get('rules') and old.get('rules') != cur and set(moved) <= {'code', 'version'} and 'version' not in moved:
            # only the shared code moved: reuse only with a VALID 'no result change' proof (D4), read by the key half's reader
            pv, pid = proof(links, old.get('rules'), cur)
            same, why = (True, f'only shared code moved, proven no result change ({pid})') if pv else (False, f'shared code only; no valid proof: {pid}')
        act = 'reuse' if same and reuse else 'rebuild'
        if act == 'rebuild': build.append(st)
        rows.append({'state': st, 'old': old.get('area_hash') or '-', 'new': h, 'moved': moved[:6], 'would': 'reuse' if same else 'rebuild', 'action': act, 'neighbours': used, 'why': why})
    print('| state | old hash | new hash | moved parts | would | action |\n|---|---|---|---|---|---|', file=out)
    for r in rows: print(f"| {r['state']} | {r['old']} | {r['new']} | {' '.join(r['moved']) or '-'} | {r['would']} | {r['action']} |", file=out)
    print(f"reuse {'ON' if reuse else 'OFF (shadow only: KPC_AREA_HASH is not reuse, or FORCE=full)'}: {len(build)} of {len(rows)} states to build", file=out)
    return build, rows


if __name__ == '__main__':
    a = sys.argv[1:] or ['help']
    if a[0] == 'pick':
        c, _ = pick(); sys.exit(c)
    elif a[0] == 'hash':
        e = os.environ
        st_of = park_states(e.get('KPCDATA') or 'kpcdata')
        print(json.dumps({st: dict(zip(('hash', 'parts', 'neighbours'), state_hash(st, e.get('LINKS') or '.', e.get('KPCDATA') or 'kpcdata', st_of=st_of)))
                          for st in (e.get('STATES') or '').split()}, indent=1))
    elif a[0] == 'plan':
        b, _ = plan()
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as o: o.write('states=' + ' '.join(b) + '\n')
    elif a[0] == 'neighbours':
        print(json.dumps({k: sorted(v) for k, v in sorted(neighbours(os.environ.get('KPCDATA') or '.').items())}, indent=1))
    else: print(__doc__)
