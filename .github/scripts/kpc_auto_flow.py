#!/usr/bin/env python3
"""WORK THE BOTS DO THEMSELVES: AUTO-1..AUTO-3 (chat 10, Oct 30 2026; Brandon 6:17 AM '1-4 go'; rule sheet KPC-Links
.claude/notes/mapping.md 'AUTO-1..AUTO-4'). Runs in the nightly waiting-room job (before the morning list). A person's later
answer always wins. Never fails.

  recheck  AUTO-1: SURE hunter rows (US + Canada) with no answer -> the bot's YES when the five checks pass; else the failed check
           is written on the row and it stays OPEN for chat 11. 1 in 10 bot YES rows is marked sample_for_chat11.
  layers   AUTO-2: intake READY layers -> approved: true when the publisher passed, the licence is open, it is not a land-class /
           coverage layer and 3+ of the parks it closes are SURE by the name tiers.
  maps     AUTO-3: documents-bot map PDFs / pictures for parks with no OFFICIAL outline -> save-map requests (25 a night), written
           to $LOOKUP_ROOT/requests/ (a checkout of the lookup branch).
  python3 kpc_auto_flow.py recheck layers [maps]          env LINKS (KPC-Links checkout), LOOKUP_ROOT"""
import collections, glob, hashlib, json, os, pathlib, re, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_tiers as T  # noqa: E402
from kpc_json_any import glob_json_any, load_json_any, save_json_gz  # noqa: E402

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
QDIR = pathlib.Path('data/waiting/questions')
TODAY = time.strftime('%Y-%m-%d')
LANDCLASS = re.compile(r'sssi|\bsac\b|\bspa\b|ramsar|special (?:area|protection)|scientific interest|zone|parcel|cadastr|census|imagery|aerial|'
                       r'photo|coverage|index|grid|land use|planning|electoral|watershed|catchment|'
                       r'natura|habitat|designated|protected (?:area|site|land)s?|land ?cover|easement|surface management|aonb|outstanding natural beauty|'
                       r'biosphere|heritage|discomap\.eea|cdda|wdpa|schutzgebiet', re.I)   # Oct 31 (Fable review #19)
SMALL = T.SMALL_KIND


def load(p, d=None):
    try: return load_json_any(p)
    except Exception: return d  # noqa: BLE001


def notice(m): print('::notice title=Auto flow::' + str(m)[:900], flush=True)


def norm_url(u): return re.sub(r'/query.*$', '', str(u or '').strip().lower().rstrip('/'))


# ------------------------------------------------------------------------------------------------ AUTO-1
def key_reads():
    """Layer URLs (normalised) the US / Canada keys read, + PAD-US / FWS / CPCAD / Parks Canada."""
    s = set()
    for v in (load(LINKS / 'data' / 'us-key' / 'layers.json', {}) or {}).values():
        if isinstance(v, list) and v and isinstance(v[0], str): s.add(norm_url(v[0]))
    for v in (load(LINKS / 'data' / 'ca-key' / 'layers.json', {}) or {}).values():
        for u in v if isinstance(v, list) else []: s.add(norm_url(u))
    s = s | {u.replace('/featureserver', '/mapserver') for u in s} | {u.replace('/mapserver', '/featureserver') for u in s}
    return s


NATIONAL = re.compile(r'pad-us|pad_us|fwsinterest|cpcad|parks ?canada|wcomu5is7ydsypnx', re.I)


def outlines_in_key():
    """record name (normalised) + rough acres -> the refs whose OFFICIAL outline already uses it (a record used twice = suspect)."""
    used = collections.defaultdict(set)
    for f in glob.glob(str(LINKS / 'data' / 'us-key' / 'US-*.json')) + glob.glob(str(LINKS / 'data' / 'ca-key' / 'CA-*.json')):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if not isinstance(v, dict) or v.get('g') != 'official': continue
            for m in v.get('m') or []:
                if isinstance(m, list) and len(m) >= 2: used[(' '.join(T.norm(m[1])), round(float(m[2] or 0), -1) if len(m) > 2 and isinstance(m[2], (int, float)) else None)].add(r)
    return used


def recheck():
    _recheck(QDIR / 'gis-hunter.json', world=False)
    _recheck(QDIR / 'world-finder.json', world=True)   # AUTO-1W (Brandon Oct 30 10:44 AM 'All 3'): world SURE rows too
    collector_trusted(QDIR / 'layers.json')   # AUTO-1C (Brandon Nov 1 2:23 PM ruling; replaces AUTO-1L)
    # AUTO-1L (Brandon Oct 31 8:10 PM 'we need more automation'): layer-collector SURE rows on a layer chat 11 already said YES to 3+ times (1 in 10 still sampled)


def _recheck(f, world):
    D = load(f, {}) or {}
    qs = D.get('questions') or []
    if not qs: notice(f'recheck: no questions in {f.name}'); return
    L = T.Learned(QDIR / 'gis-hunter.json', QDIR / 'world-finder.json', QDIR / 'key-pieces.json')
    no_any = {(str(q.get('record')), q.get('layer')) for q in qs if re.match(r'NO\b(?! *SURE)', str(q.get('answer') or '').upper().strip())}
    no_ref = {q.get('ref') for q in qs if re.match(r'NO\b(?! *SURE)', str(q.get('answer') or '').upper().strip()) and not q.get('auto')}   # a person already said NO on this park
    under = collections.Counter((str(q.get('record')), q.get('layer')) for q in qs)
    reads, used = key_reads(), outlines_in_key()
    # Oct 30 12:05 PM (Brandon): a layer chat 11 said YES to 3+ times by hand = trusted (the key reads it once the first YES joins)
    trusted = {l for l, c in collections.Counter(q.get('layer') for q in qs if str(q.get('answer') or '').upper().startswith('YES') and not q.get('auto')).items() if c >= 3 and l}
    if world:
        WL = load(LINKS / 'data' / 'world-key' / 'layers.json', {}) or {}
        reads |= {norm_url(u) for u in WL.values() if isinstance(u, str)} | {str(k).lower() for k in WL}   # world rows name the layer by its label
        for wf in glob.glob(str(LINKS / 'data' / 'world-key' / '*.json')):
            for r, v in ((load(wf, {}) or {}).get('parks') or {}).items():
                for m in (v or {}).get('m') or [] if isinstance(v, dict) else []:
                    if isinstance(m, list) and len(m) >= 2: used[(' '.join(T.norm(m[1])), round(float(m[2] or 0), -1) if len(m) > 2 and isinstance(m[2], (int, float)) else None)].add(r)
    yes = held = 0
    for q in qs:
        if q.get('tier') != 'SURE' or q.get('answer'): continue
        fails = []
        if under[(str(q.get('record')), q.get('layer'))] > 1: fails.append('the record is offered to more than one park')
        k = (' '.join(T.norm(q.get('record_name'))), round(float(q.get('acres_approx') or 0), -1))
        if used.get(k) and q['ref'] not in used[k]: fails.append(f"already the outline of {', '.join(sorted(used[k]))[:40]}")
        ac = q.get('acres_approx')
        if isinstance(ac, (int, float)) and ac > 50_000 and SMALL.search(q.get('park') or '') and not re.search(r'national park|national forest|provincial park|wilderness|state forest', q.get('park') or '', re.I):
            fails.append(f'{ac:,.0f} ac is too big for this kind of place')
        u = norm_url(q.get('layer'))
        if world and re.search(r'\beea\b|natura ?2000|cdda|discomap\.eea', str(q.get('layer') or ''), re.I):
            fails.append('an EU compilation layer (W-2 stays off: never an official outline)')
        if not (u in reads or NATIONAL.search(u) or (world and q.get('layer') in trusted)): fails.append('a layer the ' + ('world ' if world else '') + 'key does not read yet')
        if L.demoted(q.get('layer')): fails.append('a demoted layer (under 10% YES)')   # T-5: only the LAYER rule applies to SURE rows (an area's LIKELY rate never demotes SURE)
        if (str(q.get('record')), q.get('layer')) in no_any: fails.append('chat 11 said NO to this record before')
        if q['ref'] in no_ref: fails.append('chat 11 already said NO to another record for this park')
        kp, kr = T.kinds(q.get('park')), T.kinds(q.get('record_name'))
        same_name = bool(T.proper(q.get('park'))) and T.proper(q.get('park')) == T.proper(q.get('record_name'))
        if kp - kr and not (world and same_name): fails.append(f"the park is a {' '.join(sorted(kp - kr))} kind the record does not name")
        if fails:
            q['auto_recheck'] = 'NOT PASSED: ' + '; '.join(fails); held += 1; continue
        q.update({'answer': 'YES', 'checked_by': 'auto recheck (AUTO-1W)' if world else 'auto recheck (AUTO-1)', 'auto': True,
                  'how': 'AUTO-1: pin inside the record; record under this park only and not another park\'s outline; size sane; a layer the key reads; no NO before on this record or park; kinds agree',
                  'sample_for_chat11': int(hashlib.md5(f"{q['ref']}{q.get('record')}".encode()).hexdigest(), 16) % 10 == 0})
        yes += 1
    D['open'] = sum(1 for q in qs if not q.get('answer'))
    D['auto_yes'] = sum(1 for q in qs if q.get('auto'))
    save_json_gz(f, D, indent=1, ensure_ascii=False)
    notice(f"AUTO-1{'W' if world else ''} recheck ({f.name}): {yes} SURE rows passed (bot YES; the key joins them at its next rebuild), {held} stay open (check named on the row)")


# ------------------------------------------------------------------------------------------------ AUTO-1C
TRAILP = re.compile(r'\b(trail|trace|greenway|rail[- ]trail|byway|parkway|route|path|scenic river|water ?trail)\b', re.I)
PAUSE_F = pathlib.Path('data/waiting/auto-paused.json')


def official_acres():
    """{ref: acres} for the size check: data/acres.json (the acres bot, chat 11 YES) first, else the key's PAD-US / CPCAD records."""
    A = {}
    for f in glob.glob(str(LINKS / 'data' / 'us-key' / 'US-*.json')) + glob.glob(str(LINKS / 'data' / 'ca-key' / 'CA-*.json')) + glob.glob('data/us-key/US-*.json') + glob.glob('data/ca-key/CA-*.json'):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(v, dict) and re.search(r'pad-us|cpcad', ' '.join(map(str, v.get('src') or [])), re.I):
                a = sum(float(m[2]) for m in v.get('m') or [] if isinstance(m, list) and len(m) > 2 and isinstance(m[2], (int, float)))
                if a > 0: A.setdefault(r, a)
    for r, v in ((load('data/acres.json', {}) or {}).get('parks') or {}).items():
        a = v.get('acres') if isinstance(v, dict) else v
        if isinstance(a, (int, float)) and a > 0: A[r] = a
    return A


def official_outline():
    """refs that already have an OFFICIAL outline in a key (a new record could replace it)."""
    s = set()
    for f in glob.glob(str(LINKS / 'data' / '*-key' / '*.json')) + glob.glob('data/*-key/*.json'):
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if isinstance(v, dict) and v.get('g') == 'official': s.add(r)
    return s


def collector_trusted(f):
    """AUTO-1C, Brandon's ruling Nov 1 2:23 PM (HQ 2:25 PM): a layer-collector match graded SURE goes on the map by itself (the bot's
    YES: the key joins it, the key file goes through the waiting room). 1 in 10 is marked sample_for_chat11. ALWAYS to chat 11
    (the row stays open, the reason written on it): every LIKELY; the same record offered to several parks; a trail matched to an
    area or an area to a line; a pin more than 100 m outside the outline (or a line whose distance was not measured); a record
    more than 10 times the park's official size; a park that already has an official outline. Also kept (older rules): a record or
    park chat 11 said NO to, an EU compilation layer, kinds that disagree. SAFETY SWITCH: a chat-11 NO on a sample pauses the whole
    layer (data/waiting/auto-paused.json) until chat 11 writes 'cleared' for it there. Never 2-fers, never other bots' files."""
    D = load(f, {}) or {}
    qs = D.get('questions') or []
    if not qs: notice(f'AUTO-1C: no questions in {f.name}'); return
    P = load(PAUSE_F, {'about': 'AUTO-1C safety switch: layers whose auto-release is PAUSED because chat 11 said NO on a sample. Chat 11 clears one by setting its "cleared" to a date.', 'layers': {}})
    for q in qs:   # a person's NO on a row the bot had released = a NO on a sample -> pause that layer
        if q.get('sample_for_chat11') and re.match(r'NO\b(?! *SURE)', str(q.get('answer') or '').upper().strip()) and 'auto' not in str(q.get('checked_by') or ''):
            P['layers'].setdefault(q.get('layer'), {'paused': TODAY, 'why': f"chat 11 NO on {q.get('ref')} record {q.get('record')}", 'cleared': None})
    paused = {l for l, v in P['layers'].items() if not v.get('cleared')}
    no_any = {(str(q.get('record')), q.get('layer')) for q in qs if re.match(r'NO\b(?! *SURE)', str(q.get('answer') or '').upper().strip())}
    no_ref = {q.get('ref') for q in qs if re.match(r'NO\b(?! *SURE)', str(q.get('answer') or '').upper().strip()) and not q.get('auto')}
    under = collections.Counter((str(q.get('record')), q.get('layer')) for q in qs)
    AC, OFF = official_acres(), official_outline()
    yes = held = 0; why_n = collections.Counter()
    for q in qs:
        if q.get('tier') != 'SURE' or q.get('answer'): continue
        fails, why = [], str(q.get('why') or '')
        if q.get('layer') in paused: fails.append('auto-release paused for this layer (chat 11 NO on a sample)')
        if under[(str(q.get('record')), q.get('layer'))] > 1: fails.append('the record is offered to more than one park')
        is_line = 'a line' in why
        trail_park = q.get('kind') == 'trail' or bool(TRAILP.search(q.get('park') or ''))
        if is_line and not trail_park: fails.append('an area park matched to a line record')
        if trail_park and not is_line: fails.append('a trail matched to an area record')
        m = re.search(r'pin (\d+) m outside|line (\d+) m from the pin', why)
        dist = int(m.group(1) or m.group(2)) if m else (None if is_line else 0)
        if dist is None: fails.append('a line within 200 m: distance not measured')
        elif dist > 100: fails.append(f'the pin is {dist} m outside the record')
        ac, oa = q.get('acres_approx'), AC.get(q.get('ref'))
        if isinstance(ac, (int, float)) and oa and ac > 10 * oa: fails.append(f'record {ac:,.0f} ac = more than 10x the official {oa:,.0f} ac')
        elif isinstance(ac, (int, float)) and not oa and ac > 50_000 and SMALL.search(q.get('park') or '') and not re.search(r'national park|national forest|provincial park|wilderness|state forest', q.get('park') or '', re.I):
            fails.append(f'{ac:,.0f} ac is too big for this kind of place (no official size on file)')
        if q.get('ref') in OFF: fails.append('the park already has an official outline (this could replace it)')
        if (str(q.get('record')), q.get('layer')) in no_any: fails.append('chat 11 said NO to this record before')
        if q.get('ref') in no_ref: fails.append('chat 11 already said NO to another record for this park')
        if re.search(r'\beea\b|natura ?2000|cdda|discomap\.eea', str(q.get('layer') or ''), re.I): fails.append('an EU compilation layer (W-2: never an official outline)')
        kp, kr = T.kinds(q.get('park')), T.kinds(q.get('record_name'))
        same = bool(T.proper(q.get('park'))) and T.proper(q.get('park')) == T.proper(q.get('record_name'))
        if kp - kr and (not same or SMALL.search(' '.join(kp - kr)) or re.search(r'memorial|dam\b', ' '.join(kp - kr))): fails.append(f"the park is a {' '.join(sorted(kp - kr))} kind the record does not name")   # Fort Sill NHS vs bare 'Fort Sill' = chat 11
        if kr - kp: fails.append(f"the record is a {' '.join(sorted(kr - kp))} (another kind of place than the park)")   # Narcisse Provincial Park vs Narcisse WMA
        if fails:
            q['auto_recheck'] = 'TO CHAT 11: ' + '; '.join(fails); held += 1; why_n.update(x.split(' (')[0][:50] for x in fails); continue
        q.update({'answer': 'YES', 'checked_by': 'auto (AUTO-1C, trusted collector)', 'auto': True, 'auto_recheck': None,
                  'how': 'AUTO-1C (Brandon Nov 1 2:23 PM): SURE name match, pin inside (or within 100 m), record under this park only, size within 10x the official size, no outline replaced, no NO before',
                  'sample_for_chat11': int(hashlib.md5(f"{q['ref']}{q.get('record')}".encode()).hexdigest(), 16) % 10 == 0})
        yes += 1
    D['open'] = sum(1 for q in qs if not q.get('answer'))
    D['auto_yes'] = sum(1 for q in qs if q.get('auto'))
    D['auto_1c'] = {'date': TODAY, 'released': yes, 'sampled': sum(1 for q in qs if q.get('auto') and q.get('sample_for_chat11') and q.get('checked_by', '').startswith('auto (AUTO-1C')),
                    'to_chat11': held, 'likely_open': sum(1 for q in qs if q.get('tier') == 'LIKELY' and not q.get('answer')), 'paused_layers': len(paused), 'why': dict(why_n.most_common(12))}
    save_json_gz(f, D, indent=1, ensure_ascii=False)
    PAUSE_F.parent.mkdir(parents=True, exist_ok=True); json.dump(P, open(PAUSE_F, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    notice(f"AUTO-1C trusted collector ({f.name}): {yes} SURE released (bot YES, the key joins them), {D['auto_1c']['sampled']} of all bot YES marked for chat 11's 1-in-10, {held} SURE sent to chat 11 ({dict(why_n.most_common(4))}), {len(paused)} layers paused")


# ------------------------------------------------------------------------------------------------ AUTO-2
def layers():
    f = pathlib.Path('data/intake/ready.json')
    D = load(f, {}) or {}
    n = 0
    for r in D.get('rows') or []:
        if r.get('verdict') != 'READY' or r.get('approved') is not None: continue
        if LANDCLASS.search(' '.join(str(r.get(k) or '') for k in ('title', 'url', 'name'))): r['auto_note'] = 'AUTO-2: a land-class / coverage layer: chat 9 decides'; continue
        pt = str(r.get('publisher_test') or '')
        if re.search(r'\b(no|fail|not)\b', pt, re.I) and not re.search(r'pass|ok|official', pt, re.I): r['auto_note'] = 'AUTO-2: publisher test not passed'; continue
        if re.search(r'ask|closed|by request|sign-?in|internal', str(r.get('terms') or ''), re.I): r['auto_note'] = 'AUTO-2: licence not open'; continue
        parks = ((r.get('closes') or {}).get('parks') or []) if isinstance(r.get('closes'), dict) else []
        sure = [p for p in parks if isinstance(p, list) and len(p) >= 3 and T.tier(p[1], p[2])[0] == 'SURE']
        if len(sure) < 3: r['auto_note'] = f'AUTO-2: {len(sure)} SURE park names (needs 3): chat 9 decides'; continue
        r.update({'approved': True, 'approved_by': 'auto (AUTO-2)', 'approved_note': f'{len(sure)} SURE names, e.g. ' + '; '.join(f'{p[0]} {p[1][:30]}' for p in sure[:3]), 'approved_on': TODAY})
        n += 1
    save_json_gz(f, D, indent=1, ensure_ascii=False)
    notice(f'AUTO-2 layers: {n} READY layers approved by the rule (chat 9 spot-checks Mondays)')


# ------------------------------------------------------------------------------------------------ AUTO-3
CAP_MAPS = int(os.environ.get('CAP_MAPS') or 150)


def maps():
    root = pathlib.Path(os.environ.get('LOOKUP_ROOT') or 'lk')
    if not (root / 'requests').exists(): notice('AUTO-3 maps: no lookup branch checkout: skipped'); return
    have = {p.stem for p in (root / 'requests').glob('*.json')} | {p.stem for p in (root / 'answers').glob('*.json')} if (root / 'answers').exists() else {p.stem for p in (root / 'requests').glob('*.json')}
    done = set()
    try: done = {r.get('ref') for r in (json.load(open(os.environ.get('PIC_INDEX') or '/tmp/pic-index.json')).get('maps') or [])}
    except Exception: pass  # noqa: BLE001
    off = set()
    for f in glob.glob(str(LINKS / 'data' / 'us-key' / 'US-*.json')) + glob.glob(str(LINKS / 'data' / 'ca-key' / 'CA-*.json')):
        off |= {r for r, v in ((load(f, {}) or {}).get('parks') or {}).items() if isinstance(v, dict) and v.get('g') == 'official'}
    n = 0
    # Oct 30 1:25 PM (Brandon 'can it be turned up?'): 150 a night (was 25), the main map AND the extra maps, US first then Canada
    for f in glob.glob(str(LINKS / 'data' / 'world-key' / '[A-Z][A-Z].json')):
        off |= {r for r, v in ((load(f, {}) or {}).get('parks') or {}).items() if isinstance(v, dict) and v.get('g') == 'official'}
    import kpc_order as O
    files = sorted(glob.glob('data/docs/US-*.json')) + sorted(glob.glob('data/docs/CA-*.json')) + sorted(glob.glob('data/docs/W-*.json'), key=lambda f: (O.rank(pathlib.Path(f).stem), f))
    for f in files:
        if f.endswith('US-KY.json'): continue
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if n >= CAP_MAPS: break
            if r in off or r in done: continue
            for j, m in enumerate([v.get('map') or {}] + list(v.get('map_also') or [])):
                u = str((m or {}).get('url') or '')
                if m.get('status') != 'ok' or not m.get('names_park'): continue
                if not (m.get('kind') in ('pdf', 'image') or re.search(r'\.(pdf|jpe?g|png|gif)(?:$|[?#])', u, re.I)): continue
                if re.search(r'widen\.net|widencdn\.net', u, re.I): continue
                rid = f'10-auto-{r}' + (f'-{j}' if j else '')
                if rid in have: continue
                json.dump({'chat': 10, 'kind': 'save-map', 'ref': r, 'name': v.get('n') or '', 'agency': v.get('agency') or '', 'url': u, 'pages': 1,
                           'report': 'AUTO-3: documents-bot map for a park with no official outline'}, open(root / 'requests' / f'{rid}.json', 'w'), indent=1)
                n += 1
                break   # one map per park a night; the next one if this one is not a boundary map
    notice(f'AUTO-3 maps: {n} save-map requests filed ({CAP_MAPS} a night at most)')


# ------------------------------------------------------------------------------------------------ AUTO-T1 (Brandon Oct 31 8:31 PM 'wire them')
def match():
    """The map-match second opinion (outside tool T1, run nightly to tools-out map-match/map_match.json): an OPEN question whose
    band is STRONG (pin inside, name score >= 0.85, acres within x2, no better record nearby; 100% right on 200 answered rows) gets
    a bot YES, 1 in 10 marked for chat 11's sample. Never an EU-compilation layer; WEAK / CONFLICT stay with chat 11 (the band
    and its reason are written on the row to help them)."""
    f = pathlib.Path(os.environ.get('MATCH_FILE') or '../out/map-match/map_match.json')
    M = load(f, {}) or {}
    if not M: notice('AUTO-T1: no map_match.json (the T1 run has not written one yet)'); return
    def qkey(q):
        if q.get('record') not in (None, ''): return f"{q['ref']}|{q['record']}"
        parts = str(q.get('layer') or q.get('url') or '').rstrip('/').split('/')
        tail = f"{parts[-3]}/{parts[-1]}" if len(parts) >= 3 else str(q.get('layer'))
        return f"{q['ref']}|name:{q.get('record_name', '')}@{tail}"
    tot = 0
    for qf in glob_json_any(str(QDIR / '*.json')):
        qf = pathlib.Path(qf)
        D = load(qf, {}) or {}
        qs = D.get('questions') if isinstance(D, dict) else None
        if not isinstance(qs, list): continue
        n = 0
        for q in qs:
            if not isinstance(q, dict) or q.get('answer'): continue
            r = M.get(qkey(q))
            if not r: continue
            q['t1_band'] = r.get('band'); q['t1_why'] = str(r.get('why') or '')[:200]
            if r.get('band') != 'STRONG': continue
            if re.search(r'\beea\b|natura ?2000|cdda|discomap\.eea', str(q.get('layer') or ''), re.I): continue
            q.update({'answer': 'YES', 'checked_by': 'auto (T1 map-match STRONG)', 'auto': True,
                      'how': 'T1: pin inside the record, names match (>= 0.85), acres within x2, no better record nearby',
                      'sample_for_chat11': int(hashlib.md5(f"{q['ref']}{q.get('record')}".encode()).hexdigest(), 16) % 10 == 0})
            n += 1
        if n or any(isinstance(q, dict) and q.get('t1_band') for q in qs):
            save_json_gz(qf, D, indent=1, ensure_ascii=False)
        tot += n
    notice(f'AUTO-T1 map-match: {tot} STRONG open questions got a bot YES (1 in 10 sampled for chat 11); bands written on the rest')


if __name__ == '__main__':
    for mode in sys.argv[1:] or ['recheck', 'layers']:
        try: {'recheck': recheck, 'layers': layers, 'maps': maps, 'match': match}[mode]()
        except Exception as e: notice(f'{mode} stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
