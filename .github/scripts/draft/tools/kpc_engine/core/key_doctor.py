"""KEY DOCTOR (v0.5.0, Nov 2 2026). One read-only check-up of the answer-key line, run by hand or by a bot:

  python3 kpc_engine.py doctor --links L --data D --out OUT [--tasks nos,release,approvals,fers-ids,line,stuck,storage]

It READS the KPC-Links and KPC-Data checkouts (or local copies with the same folders) and writes ONLY to <out>/key-doctor/.
It never pushes, never edits a checkout, never emails. Switches live in config/rules.json 'key_doctor' (see TUNING.md).

  nos        chat 11's NO answers (data/waiting/questions/*.json in KPC-Data) -> are they in data/us-key/overrides.json (KPC-Links)?
             Missing ones are re-applied to a COPY (overrides.fixed.json, the same rules as BOT A with the Nov 2 fixes: a YES
             clears a sole NO, a NO keeps its name + acres in 'nofp'). Also: NOs the built key ignored (the ruled-out record is
             still joined in data/us-key/US-XX.json) = 'came back'.
  release    the per-park release check, LIVE-FILTERED style: each held key file (data/waiting/in/data/us-key/US-XX.json) is
             split into passing parks (they go) and failing parks (held: the live version stays, or a pin when there is no live
             version). Failing = named in the latest KEY NO, a NO that came back, or a self-check failure. Writes the filtered
             files to <out>/key-doctor/release/ ONLY when key_doctor.per_park_release is on (default OFF: a report only).
  approvals  approved.json items: a YES with no chat 2 recheck (key_doctor.require_chat2) or no folder path (require_path).
  fers-ids   2-fer spot ids that survive a rebuild: id = sorted refs + kind + centre rounded to 0.01 deg; an old spot with the same
             refs + kind within key_doctor.fer_carry_km (or overlapping boxes) passes its id on (carry-forward map).
  line       the assembly line per area, in the club order: build, check, grade, save, release, fers, review. A build being graded
             is frozen with its hash; 'done' means the live file IS the build (same hash).
  stuck      the daily stuck list (stuck-YYYY-MM-DD.md): areas on one stage for key_doctor.stuck_days or more, with the owner.
  storage    the size guard: any data file over key_doctor.size_warn_mib (80 MiB) warns, over size_red_mib (95 MiB) goes red
             (GitHub refuses a file over 100 MiB). Also lists held copies a newer build already replaced (cleanup candidates).
"""
import datetime as dt, fnmatch, glob, gzip, hashlib, json, math, os, pathlib, re, sys, unicodedata

from core import rules

TASKS = ['nos', 'release', 'approvals', 'fers-ids', 'line', 'stuck', 'storage']
STAGES = ['build', 'check', 'grade', 'save', 'release', 'fers', 'review']
OWNERS = {'build': 'chat 10 (key bots)', 'check': 'chat 2 (waiting-room checks)', 'grade': 'chat 11 (grader)',
          'save': 'chat 10 (save step)', 'release': 'Brandon OK + chat 10', 'fers': 'chat 2 / chat 8 (2-fers)', 'review': 'HQ'}
MIB = 1024 * 1024
PAD = 'edits.nationalmap.gov/arcgis/rest/services/pad-us/pad_us/mapserver/0'
FWS = 'fwsinterest_simplified_authoritative/featureserver/0'


# ------------------------------------------------------------------ small helpers
def load(p, d=None):
    p = pathlib.Path(p)
    try:
        if not str(p).endswith('.gz'):
            gz = pathlib.Path(str(p) + '.gz')
            if gz.is_file(): p = gz
        if str(p).endswith('.gz'): return json.loads(gzip.decompress(p.read_bytes()))
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:  # noqa: BLE001
        return d


def sha(p):
    p = pathlib.Path(p)
    if not p.exists(): return None
    b = p.read_bytes()
    if p.suffix == '.gz':
        try: b = gzip.decompress(b)
        except OSError: pass
    return hashlib.sha1(b).hexdigest()


def nf(t): return unicodedata.normalize('NFC', str(t or '')).strip().casefold()


def today(): return dt.date.today()


def _date(s):
    m = re.search(r'(20\d\d)-(\d\d)-(\d\d)', str(s or ''))
    return dt.date(int(m[1]), int(m[2]), int(m[3])) if m else None


def first_word(ans):
    a = re.sub(r'^[^A-Za-z]+', '', str(ans or '')).upper()
    if a.startswith('NOT'): return ''
    m = re.match(r'(?:KEY\s+)?(YES|NO|PASS)\b', a)
    return {'PASS': 'YES'}.get(m.group(1), m.group(1)) if m else ''


def write(out, name, obj):
    p = pathlib.Path(out) / name; p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, str): p.write_text(obj, encoding='utf-8')
    else: p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return p


# ------------------------------------------------------------------ chat 11's NOs
def norm_url(u):
    u = str(u or '').strip().lower().split('?')[0].rstrip('/')
    return re.sub(r'^https?://', '', re.sub(r'/query$', '', u))


def layer_map(layers):
    m = {}
    for pre, v in (layers or {}).items():
        if isinstance(v, list) and v and isinstance(v[0], str) and not v[0].startswith('file:'):
            u = norm_url(v[0]); m[u] = pre
            m[u.replace('/featureserver/', '/mapserver/')] = pre; m[u.replace('/mapserver/', '/featureserver/')] = pre
    return m


def key_id(row, lmap):
    """Same mapping as BOT A (kpc_key_answers.key_id)."""
    rec = str(row.get('record')).strip(); lay = row.get('layer')
    if not lay: return rec
    u = norm_url(lay)
    if PAD in u: return rec
    if FWS in u: return rec if rec.startswith('fws') else 'fws' + rec
    pre = lmap.get(u)
    if not pre: return None
    return rec if rec.startswith(pre) else pre + rec


def question_rows(data_dir):
    out = []
    base = pathlib.Path(data_dir) / 'data/waiting/questions'
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from kpc_json_any import glob_json_any
    for f in glob_json_any(str(base / '*.json')):
        j = load(f, {}) or {}
        q = j.get('questions') if isinstance(j, dict) else j
        if isinstance(q, dict): q = list(q.values())
        for r in q or []:
            if isinstance(r, dict) and r.get('ref') and r.get('record') is not None: out.append((pathlib.Path(f).stem, r))
    return out


def latest_answers(rows, lmap):
    """{(ref, kid): (answer, row, file)}: the last plain YES / NO per park + piece (NOT SURE changes nothing)."""
    got = {}
    for f, r in rows:
        kid = key_id(r, lmap)
        a = first_word(r.get('answer'))
        if not kid or a not in ('YES', 'NO'): continue
        got[(str(r['ref']), str(kid))] = (a, r, f)
    return got


def apply_answer(v, kid, ans, row):
    """BOT A's rule with the Nov 2 fixes, on one overrides entry (changed in place)."""
    nm = str(row.get('record_name') or '').strip()
    ac = row.get('acres') if row.get('acres') is not None else row.get('acres_approx')
    try: ac = round(float(ac))
    except (TypeError, ValueError): ac = 0
    if ans == 'YES':
        v['no'] = [x for x in v.get('no', []) if str(x) != kid]
        if not v['no']: v.pop('no')
        if kid in (v.get('nofp') or {}): v['nofp'].pop(kid)
        if 'nofp' in v and not v['nofp']: v.pop('nofp')
        v.setdefault('join', [])
        if kid not in [str(x) for x in v['join']]: v['join'].append(kid)
        v.setdefault('fp', {})[kid] = [nm, ac]
    else:
        v['join'] = [x for x in v.get('join', []) if str(x) != kid]
        if not v['join']: v.pop('join')
        if kid in (v.get('fp') or {}): v['fp'].pop(kid)
        if 'fp' in v and not v['fp']: v.pop('fp')
        v.setdefault('no', [])
        if kid not in [str(x) for x in v['no']]: v['no'].append(kid)
        if nm: v.setdefault('nofp', {})[kid] = [nm, ac]


def ruled_out(ov, oid, name):
    ov = ov or {}
    if str(oid) in {str(x) for x in ov.get('no') or []}: return True
    n = nf(name)
    return bool(n) and (n in {nf(x) for x in ov.get('no') or []} or any(v and nf(v[0]) == n for v in (ov.get('nofp') or {}).values()))


def key_files(key_dir):
    return sorted(p for p in pathlib.Path(key_dir).glob('*.json*') if re.match(r'^(US|CA)-[A-Z]+\.json(\.gz)?$', p.name))


def came_back(key, ovr_parks):
    """[(ref, id, name)] joined in this key although a person ruled them out."""
    out = []
    for ref, p in ((key or {}).get('parks') or {}).items():
        ov = ovr_parks.get(ref)
        if not ov or not isinstance(p, dict): continue
        for x in p.get('m') or []:
            if isinstance(x, (list, tuple)) and len(x) > 1 and ruled_out(ov, x[0], x[1]): out.append((ref, str(x[0]), str(x[1])))
    return out


def overrides_whole(links):
    """Nov 12 2026 (KPC owner; KPC-Links #151 split): KPC-Links' US overrides read WHOLE (manifest + parts) through KPC-Data's
    kpc_overrides_whole, in the single-file shape ('parts' dropped). A missing / bad part raises: never a partial set."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    import kpc_overrides_whole as OVW
    d = dict(OVW.load_whole(pathlib.Path(links) / 'data/us-key/overrides.json', missing_ok=True, links=links))
    d.pop('parts', None)
    return d


def task_nos(links, data, out):
    key = pathlib.Path(links) / 'data/us-key'
    ovr = overrides_whole(links) or {'parks': {}}
    P = ovr.setdefault('parks', {})
    lmap = layer_map(load(key / 'layers.json', {}) or {})
    ans = latest_answers(question_rows(data), lmap) if data else {}
    missing, ok = [], 0
    for (ref, kid), (a, row, f) in sorted(ans.items()):
        if a != 'NO': continue
        v = P.get(ref) or {}
        if kid in {str(x) for x in v.get('no') or []} and kid not in {str(x) for x in v.get('join') or []}: ok += 1; continue
        missing.append({'ref': ref, 'id': kid, 'name': row.get('record_name'), 'file': f, 'checked_by': row.get('checked_by')})
    fixed = None
    if missing and rules.on('key_doctor.reapply_nos'):
        import copy
        fixed = copy.deepcopy(ovr)
        for mm in missing:
            a, row, _ = ans[(mm['ref'], mm['id'])]
            apply_answer(fixed['parks'].setdefault(mm['ref'], {}), mm['id'], 'NO', row)
        write(out, 'overrides.fixed.json', fixed)
    back = []
    for p in key_files(key):
        for ref, oid, nm in came_back(load(p, {}), P): back.append({'file': p.name, 'ref': ref, 'id': oid, 'name': nm})
    res = {'nos_in_questions': ok + len(missing), 'landed': ok, 'missing': missing, 'reapplied_copy': 'overrides.fixed.json' if fixed else None,
           'came_back': back, 'verdict': 'OK' if not missing and not back else 'FIX'}
    write(out, 'nos.json', res)
    return res


# ------------------------------------------------------------------ per-park release (LIVE-FILTERED)
REF_RX = re.compile(r'\b(?:US|CA)-\d{1,6}\b')


def latest_item(items, what):
    xs = [it for it in items or [] if isinstance(it, dict) and it.get('what') == what]
    xs.sort(key=lambda it: (_date(it.get('date')) or dt.date.min, _date(it.get('chat11')) or dt.date.min))
    return xs[-1] if xs else None


def key_no_refs(approved, what='us-key'):
    """Refs named in the LATEST verdict for this key when that verdict is a NO (a YES clears them)."""
    it = latest_item((approved or {}).get('items'), what)
    if not it or first_word(it.get('chat11')) != 'NO': return set(), it
    return set(REF_RX.findall(str(it.get('chat11')))), it


def park_checks(ref, p):
    bad = []
    if not isinstance(p, dict): return ['not a park object']
    for k in ('n', 'm', 'c'):
        if k not in p: bad.append(f'missing field {k}')
    for x in p.get('m') or []:
        if not isinstance(x, (list, tuple)) or len(x) < 4: bad.append('joined row is not [id, name, acres, how]'); break
    if p.get('far') == 'well outside': bad.append('pin well outside the joined land')
    return bad


def release_split(new, live, fail_refs, ovr_parks):
    """-> (filtered key, {ref: why held}). Passing parks go as built; failing parks keep the live version (or a pin)."""
    import copy
    out = copy.deepcopy(new); live_p = ((live or {}).get('parks') or {}) if isinstance(live, dict) else {}
    held = {}
    back = {r for r, _, _ in came_back(new, ovr_parks)}
    for ref, p in (new.get('parks') or {}).items():
        why = []
        if ref in fail_refs: why.append('named in the latest KEY NO')
        if ref in back: why.append("a person's NO came back")
        why += park_checks(ref, p)
        if not why: continue
        held[ref] = why
        if ref in live_p: out['parks'][ref] = live_p[ref]
        else:
            q = {k: v for k, v in (p if isinstance(p, dict) else {}).items() if k in ('n', 't', 'la', 'lo')}
            q.update(m=[], c=[], held='per-park release: no live version, shown as a pin until chat 11 says YES'); out['parks'][ref] = q
    out.setdefault('counts', {})
    if isinstance(out['counts'], dict):
        out['counts']['held_parks'] = len(held)
        out['counts']['matched'] = sum(1 for p in out['parks'].values() if isinstance(p, dict) and p.get('m'))
    out['release'] = {'mode': 'LIVE-FILTERED (per park)', 'held': len(held), 'when': today().isoformat()}
    return out, held


def task_release(links, data, out):
    data = pathlib.Path(data); held_dir = data / 'data/waiting/in/data/us-key'
    approved = load(data / 'data/waiting/approved.json', {}) or {}
    fail, item = key_no_refs(approved, 'us-key')
    ovr_parks = (overrides_whole(links).get('parks') or {}) if links else {}
    if links:   # chat 11's NO answers that never reached overrides.json count too (BOT A's lost saves)
        lmap = layer_map(load(pathlib.Path(links) / 'data/us-key/layers.json', {}) or {})
        import copy
        ovr_parks = copy.deepcopy(ovr_parks)
        for (ref, kid), (a, row, _) in latest_answers(question_rows(data), lmap).items():
            if a == 'NO': apply_answer(ovr_parks.setdefault(ref, {}), kid, 'NO', row)
    write_on = rules.on('key_doctor.per_park_release')
    files = []
    for p in key_files(held_dir) if held_dir.exists() else []:
        new = load(p, None)
        if not isinstance(new, dict) or not isinstance(new.get('parks'), dict):
            files.append({'file': p.name, 'verdict': 'HOLD', 'why': 'not a key file (wrong shape)'}); continue
        live = load(data / 'data/us-key' / p.name, None)
        filt, held = release_split(new, live, fail, ovr_parks)
        n = len(new['parks'])
        files.append({'file': p.name, 'parks': n, 'pass': n - len(held), 'held': len(held),
                      'verdict': 'PASS' if not held else 'LIVE-FILTERED', 'held_parks': {r: w for r, w in sorted(held.items())[:50]}})
        if write_on and held is not None: write(out, f'release/data/us-key/{p.name.replace(".gz", "")}', filt)
    res = {'switch_per_park_release': write_on, 'latest_verdict': (item or {}).get('chat11', '')[:200], 'refs_in_key_no': sorted(fail),
           'files': files, 'note': 'report only (key_doctor.per_park_release is OFF; Brandon must OK it)' if not write_on
           else 'filtered files written to key-doctor/release/ (copy them into the release only after a test build)'}
    write(out, 'release.json', res)
    return res


# ------------------------------------------------------------------ approvals missing fields
def _matches(what, pats): return any(fnmatch.fnmatchcase(str(what), p) for p in pats or [])


def task_approvals(data, out):
    approved = load(pathlib.Path(data) / 'data/waiting/approved.json', {}) or {}
    items = [it for it in approved.get('items') or [] if isinstance(it, dict)]
    flags = []
    for what in sorted({it.get('what') for it in items if it.get('what')}):
        it = latest_item(items, what)
        if first_word(it.get('chat11')) != 'YES': continue
        miss = []
        if _matches(what, rules.value('key_doctor.require_chat2')) and not str(it.get('chat2') or '').strip(): miss.append('chat2 (chat 2 recheck, G-4)')
        if _matches(what, rules.value('key_doctor.require_path')) and not str(it.get('path') or '').strip(): miss.append('path (the folder it releases)')
        if miss: flags.append({'what': what, 'date': it.get('date'), 'missing': miss, 'verdict': str(it.get('chat11'))[:120]})
    res = {'items': len(items), 'flags': flags, 'verdict': 'OK' if not flags else 'FIX'}
    write(out, 'approvals.json', res)
    return res


# ------------------------------------------------------------------ 2-fer ids that survive a rebuild
def stable_id(s):
    c = s.get('center') or [None, None]
    loc = f'{round(c[0], 2):.2f},{round(c[1], 2):.2f}' if c and c[0] is not None else '?'
    return '+'.join(sorted(str(r) for r in s.get('refs') or [])) + '@' + str(s.get('kind') or '') + '@' + loc


def _km(a, b):
    if not a or not b or a[0] is None or b[0] is None: return 1e9
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, h)))


def _box_overlap(a, b):
    try: return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
    except (TypeError, IndexError): return False


def carry_ids(old_spots, new_spots, km=None):
    """-> {new stable id: old id}. Same refs + kind, nearest old spot within km (or overlapping 'bbox'), each old id used once."""
    km = float(rules.value('key_doctor.fer_carry_km')) if km is None else km
    pool = {}
    for s in old_spots or []:
        if isinstance(s, dict): pool.setdefault(('+'.join(sorted(map(str, s.get('refs') or []))), str(s.get('kind') or '')), []).append(s)
    used, out = set(), {}
    for s in new_spots or []:
        if not isinstance(s, dict): continue
        nid = stable_id(s)
        cands = [o for o in pool.get(('+'.join(sorted(map(str, s.get('refs') or []))), str(s.get('kind') or '')), []) if id(o) not in used]
        best = min(cands, key=lambda o: _km(o.get('center'), s.get('center')), default=None)
        if best is None: continue
        if _km(best.get('center'), s.get('center')) <= km or _box_overlap(best.get('bbox'), s.get('bbox')):
            used.add(id(best)); out[nid] = best.get('id') or stable_id(best)
    return out


def task_fers_ids(data, out):
    data = pathlib.Path(data); res = {'files': []}
    for p in sorted((data / 'data/waiting/in/data/fers').glob('*.json*')) if (data / 'data/waiting/in/data/fers').exists() else []:
        new = load(p, {}) or {}
        live = load(data / 'data/fers' / p.name, None) or load(data / 'data/fers' / (p.name[:-3] if p.name.endswith('.gz') else p.name + '.gz'), {}) or {}
        ns = [s for s in (new.get('spots') or []) if isinstance(s, dict)] if isinstance(new, dict) else []
        os_ = [s for s in (live.get('spots') or []) if isinstance(s, dict)] if isinstance(live, dict) else []
        cm = carry_ids(os_, ns)
        changed = sum(1 for s in ns if s.get('id') and cm.get(stable_id(s)) and cm[stable_id(s)] != s.get('id'))
        res['files'].append({'file': p.name, 'new_spots': len(ns), 'carried': len(cm), 'ids_that_would_change_without_carry': changed})
        write(out, f'fers-ids/{p.name.replace(".gz", "")}', {'carry': cm})
    write(out, 'fers-ids.json', res)
    return res


# ------------------------------------------------------------------ assembly line + stuck list
def club_order(areas):
    try:
        from core import adapters
        return adapters.order_areas(areas)
    except Exception:  # noqa: BLE001
        return sorted(set(areas), key=lambda a: (a != 'US-KY', a))


def _area(name):
    m = re.match(r'^((?:US|CA)-[A-Z]+|[A-Z]{2})\.json', name)
    return m.group(1) if m else None


def area_state(area, links, data, approved, verdicts, frozen):
    """-> (stage, detail, hashes). The first stage not yet done."""
    links, data = pathlib.Path(links), pathlib.Path(data)
    folder = 'us-key' if area.startswith('US-') else 'ca-key' if area.startswith('CA-') else 'world-key'
    rel = f'data/{folder}/{area}.json'
    find = lambda base, r: next((base / x for x in (r, r + '.gz') if (base / x).exists()), None)
    built, held, live = find(links, rel), find(data / 'data/waiting/in', rel), find(data, rel)
    hb, hh, hl = sha(built) if built else None, sha(held) if held else None, sha(live) if live else None
    h = {'build': hb, 'held': hh, 'live': hl}
    if not hb: return 'build', 'no key file built yet', h
    if hl == hb:
        fers = find(data, f'data/fers/{area}.json')
        kd = (load(live, {}) or {}).get('updated') if live else None
        fd = (load(fers, {}) or {}).get('updated') if fers else None
        if not fers: return 'fers', 'key is live, no 2-fer file for it yet', h
        if kd and fd and str(fd)[:10] < str(kd)[:10]: return 'fers', f'2-fers ({fd}) older than the live key ({kd})', h
        return 'review', 'live and 2-fers current: done (HQ review only)', h
    if not hh: return 'save', 'built but not copied to KPC-Data (no held copy, live differs)', h
    v = next((r for r in verdicts if r.get('path') == rel or r.get('path') == rel + '.gz'), None)
    if not v: return 'check', 'held, the waiting room has not judged it yet', h
    if v.get('verdict') == 'HOLD': return 'check', 'HOLD: ' + '; '.join(v.get('why') or [])[:160], h
    it = latest_item((approved or {}).get('items'), folder)
    fz = frozen.get(rel)
    if fz and fz.get('sha') != hh: return 'grade', f"the held copy CHANGED while chat 11 was grading it (frozen {fz.get('since')}): grade again", h
    if not it or first_word(it.get('chat11')) != 'YES' or (_date(it.get('date')) or dt.date.min) < (_date((fz or {}).get('since')) or dt.date.min):
        return 'grade', 'waiting for chat 11' + (f" (latest verdict: {first_word(it.get('chat11')) or '?'} {it.get('date')})" if it else ''), h
    return 'release', 'chat 11 YES: waiting for the release (live is not the build yet)', h


def task_line(links, data, out):
    data = pathlib.Path(data); links = pathlib.Path(links)
    approved = load(data / 'data/waiting/approved.json', {}) or {}
    verdicts = (load(data / 'data/waiting/verdicts.json', {}) or {}).get('results') or []
    prev = load(pathlib.Path(out) / 'line.json', {}) or {}
    frozen = prev.get('frozen') or {}
    areas = set()
    for base in (links, data, data / 'data/waiting/in'):
        for f in ('us-key', 'ca-key'):
            for p in (base / 'data' / f).glob('*.json*') if (base / 'data' / f).exists() else []:
                if _area(p.name): areas.add(_area(p.name))
    rows, t = [], today().isoformat()
    for a in club_order(areas):
        st, why, h = area_state(a, links, data, approved, verdicts, frozen)
        folder = 'us-key' if a.startswith('US-') else 'ca-key'
        rel = f'data/{folder}/{a}.json'
        if rules.on('key_doctor.freeze_while_graded'):
            if st == 'grade' and h['held'] and rel not in frozen: frozen[rel] = {'sha': h['held'], 'since': t}
            if st != 'grade' and rel in frozen and not why.startswith('the held copy CHANGED'): frozen.pop(rel)
        old = next((r for r in prev.get('areas') or [] if r.get('area') == a), None)
        since = old['since'] if old and old.get('stage') == st else t
        rows.append({'area': a, 'stage': st, 'why': why, 'since': since, 'owner': OWNERS[st], 'done': st == 'review',
                     'freeze': frozen.get(rel), 'hashes': {k: (v or '')[:12] for k, v in h.items()}})
    res = {'when': t, 'stages': STAGES, 'areas': rows, 'frozen': frozen,
           'counts': {s: sum(1 for r in rows if r['stage'] == s) for s in STAGES}}
    write(out, 'line.json', res)
    return res


def task_stuck(line, out):
    days = int(rules.value('key_doctor.stuck_days')); t = today()
    stuck = []
    for r in line.get('areas') or []:
        if r.get('done'): continue
        d = (t - (_date(r.get('since')) or t)).days
        if d >= days: stuck.append(dict(r, days=d))
    stuck.sort(key=lambda r: (-r['days'], STAGES.index(r['stage'])))
    L = [f'# Stuck list {t.isoformat()} (key doctor)', '', f'Areas on the same stage for {days}+ days, longest first. Owner = who moves it next.', '']
    L += [f"- **{r['area']}** at **{r['stage']}** for {r['days']} days (owner: {r['owner']}): {r['why']}" for r in stuck] or ['- nothing stuck']
    write(out, f'stuck-{t.isoformat()}.md', '\n'.join(L) + '\n')
    return {'stuck': stuck, 'file': f'stuck-{t.isoformat()}.md'}


# ------------------------------------------------------------------ storage
def size_level(n_bytes):
    if n_bytes >= float(rules.value('key_doctor.size_red_mib')) * MIB: return 'RED'
    if n_bytes >= float(rules.value('key_doctor.size_warn_mib')) * MIB: return 'WARN'
    return 'OK'


def task_storage(roots, data, out):
    big, scanned = [], 0
    for root in [pathlib.Path(r) for r in roots if r]:
        for p in root.rglob('*'):
            if '.git' in p.parts or not p.is_file(): continue
            scanned += 1; n = p.stat().st_size; lv = size_level(n)
            if lv != 'OK': big.append({'file': str(p.relative_to(root)), 'root': root.name, 'bytes': n, 'mib': round(n / MIB, 1), 'level': lv,
                                        'headroom_to_100mib_mb': round((100 * MIB - n) / 1e6, 2)})
    big.sort(key=lambda r: -r['bytes'])
    superseded = []
    if data and rules.on('key_doctor.list_superseded_held'):
        w = pathlib.Path(data) / 'data/waiting/in'
        for p in w.rglob('*') if w.exists() else []:
            if not p.is_file(): continue
            lv = pathlib.Path(data) / p.relative_to(w)
            if lv.exists() and sha(lv) == sha(p): superseded.append({'held': str(p.relative_to(w)), 'why': 'live already has this exact build', 'bytes': p.stat().st_size})
    res = {'scanned': scanned, 'warn_mib': rules.value('key_doctor.size_warn_mib'), 'red_mib': rules.value('key_doctor.size_red_mib'),
           'files': big, 'red': [r for r in big if r['level'] == 'RED'], 'superseded_held': superseded,
           'verdict': 'RED' if any(r['level'] == 'RED' for r in big) else 'WARN' if big else 'OK'}
    write(out, 'storage.json', res)
    return res


# ------------------------------------------------------------------ the command
def run(links, data, out, tasks=None):
    tasks = tasks or TASKS
    bad = [t for t in tasks if t not in TASKS]
    if bad: raise ValueError(f'unknown doctor task(s): {", ".join(bad)} (known: {", ".join(TASKS)})')
    out = pathlib.Path(out) / 'key-doctor'; out.mkdir(parents=True, exist_ok=True)
    res = {}
    if 'nos' in tasks and links: res['nos'] = task_nos(links, data, out)
    if 'release' in tasks and data: res['release'] = task_release(links, data, out)
    if 'approvals' in tasks and data: res['approvals'] = task_approvals(data, out)
    if 'fers-ids' in tasks and data: res['fers-ids'] = task_fers_ids(data, out)
    if ('line' in tasks or 'stuck' in tasks) and links and data: res['line'] = task_line(links, data, out)
    if 'stuck' in tasks and 'line' in res: res['stuck'] = task_stuck(res['line'], out)
    if 'storage' in tasks and rules.on('key_doctor.size_guard'): res['storage'] = task_storage([links, data], data, out)
    write(out, 'summary.json', {k: (v.get('verdict') if isinstance(v, dict) and 'verdict' in v else 'done') for k, v in res.items()})
    return res


def lines(res):
    """Plain-words lines for the console (GitHub annotations when run in Actions)."""
    L = []
    n = res.get('nos')
    if n: L.append(('::error' if n['missing'] or n['came_back'] else '::notice') + f" title=Key doctor NOs::{n['landed']} of {n['nos_in_questions']} NOs landed; "
                   f"{len(n['missing'])} missing" + (' (re-applied to overrides.fixed.json)' if n['reapplied_copy'] else '') + f"; {len(n['came_back'])} came back in the key")
    r = res.get('release')
    if r: L.append(f"::notice title=Key doctor release::{sum(f.get('pass', 0) for f in r['files'])} parks pass, {sum(f.get('held', 0) for f in r['files'])} held, "
                   f"{len(r['files'])} files; per-park release {'ON' if r['switch_per_park_release'] else 'OFF (report only)'}")
    a = res.get('approvals')
    if a: L += [f"::warning title=Key doctor approvals::{f['what']} {f['date']}: YES is missing {', '.join(f['missing'])}" for f in a['flags']]
    s = res.get('stuck')
    if s: L.append(f"::notice title=Key doctor stuck::{len(s['stuck'])} area(s) stuck; see {s['file']}")
    st = res.get('storage')
    if st:
        for f in st['files']:
            L.append(('::error' if f['level'] == 'RED' else '::warning') + f" title=Key doctor size::{f['root']}/{f['file']} is {f['mib']} MiB ({f['level']}; "
                     f"{f['headroom_to_100mib_mb']} MB under GitHub's 100 MiB limit)")
        if st['superseded_held']: L.append(f"::notice title=Key doctor storage::{len(st['superseded_held'])} held copies already live (cleanup candidates)")
    return L


def exit_code(res):
    """1 when something is red: a NO missing / came back, or a file over the red size."""
    n, st = res.get('nos') or {}, res.get('storage') or {}
    return 1 if (n.get('missing') or n.get('came_back') or st.get('red')) else 0
