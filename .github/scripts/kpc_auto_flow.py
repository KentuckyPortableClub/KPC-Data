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

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
QDIR = pathlib.Path('data/waiting/questions')
TODAY = time.strftime('%Y-%m-%d')
LANDCLASS = re.compile(r'sssi|\bsac\b|\bspa\b|ramsar|special (?:area|protection)|scientific interest|zone|parcel|cadastr|census|imagery|aerial|'
                       r'photo|coverage|index|grid|land use|planning|electoral|watershed|catchment', re.I)
SMALL = T.SMALL_KIND


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
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


def _recheck(f, world):
    D = load(f, {}) or {}
    qs = D.get('questions') or []
    if not qs: notice(f'recheck: no questions in {f.name}'); return
    L = T.Learned(QDIR / 'gis-hunter.json', QDIR / 'world-finder.json', QDIR / 'key-pieces.json')
    no_any = {(str(q.get('record')), q.get('layer')) for q in qs if str(q.get('answer') or '').upper().startswith('NO')}
    no_ref = {q.get('ref') for q in qs if str(q.get('answer') or '').upper().startswith('NO') and not q.get('auto')}   # a person already said NO on this park
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
    json.dump(D, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    notice(f"AUTO-1{'W' if world else ''} recheck ({f.name}): {yes} SURE rows passed (bot YES; the key joins them at its next rebuild), {held} stay open (check named on the row)")


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
    json.dump(D, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    notice(f'AUTO-2 layers: {n} READY layers approved by the rule (chat 9 spot-checks Mondays)')


# ------------------------------------------------------------------------------------------------ AUTO-3
def maps():
    root = pathlib.Path(os.environ.get('LOOKUP_ROOT') or 'lk')
    if not (root / 'requests').exists(): notice('AUTO-3 maps: no lookup branch checkout: skipped'); return
    have = {p.stem for p in (root / 'requests').glob('*.json')} | {p.stem for p in (root / 'answers').glob('*.json')} if (root / 'answers').exists() else {p.stem for p in (root / 'requests').glob('*.json')}
    done = set()
    try: done = {r.get('ref') for r in (json.load(open(os.environ.get('PIC_INDEX') or '/tmp/pic-index.json')).get('maps') or [])}
    except Exception: pass  # noqa: BLE001
    off = set()
    for f in glob.glob(str(LINKS / 'data' / 'us-key' / 'US-*.json')):
        off |= {r for r, v in ((load(f, {}) or {}).get('parks') or {}).items() if isinstance(v, dict) and v.get('g') == 'official'}
    n = 0
    for f in sorted(glob.glob('data/docs/US-*.json')):
        if f.endswith('US-KY.json'): continue
        for r, v in ((load(f, {}) or {}).get('parks') or {}).items():
            if n >= 25: break
            m = v.get('map') or {}
            u = str(m.get('url') or '')
            if r in off or r in done or m.get('status') != 'ok' or not m.get('names_park'): continue
            if not (m.get('kind') in ('pdf', 'image') or re.search(r'\.(pdf|jpe?g|png|gif)(?:$|[?#])', u, re.I)): continue
            if re.search(r'widen\.net|widencdn\.net', u, re.I): continue
            rid = f'10-auto-{r}'
            if rid in have: continue
            json.dump({'chat': 10, 'kind': 'save-map', 'ref': r, 'name': v.get('n') or '', 'agency': v.get('agency') or '', 'url': u, 'pages': 1,
                       'report': 'AUTO-3: documents-bot map for a park with no official outline'}, open(root / 'requests' / f'{rid}.json', 'w'), indent=1)
            n += 1
    notice(f'AUTO-3 maps: {n} save-map requests filed (25 a night at most)')


if __name__ == '__main__':
    for mode in sys.argv[1:] or ['recheck', 'layers']:
        try: {'recheck': recheck, 'layers': layers, 'maps': maps}[mode]()
        except Exception as e: notice(f'{mode} stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
