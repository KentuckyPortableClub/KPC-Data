#!/usr/bin/env python3
"""QUESTION GATE + SECOND LOOK (chat 10, Nov 2 2026; Brandon 4:33 AM 'too many mistakes rejects by 11 ... we are spinning in
circles'; his GO 4:40 AM: 'Yes, gate them' + 'Yes, add map pictures').

Chat 11's own history (about 30,000 graded rows, Nov 2): a candidate whose name shares NO proper word with the park, or one
record offered to 2+ parks whose names are not equal, was NO / NOT SURE about 4,600 times and YES about 90 times (2%). So:
  gate          every OPEN question (answer blank) in data/waiting/questions/*.json that fails a gate rule is MOVED to
                data/waiting/questions/parked.json (kept, never deleted; a better source can bring it back):
                  Q0  the park's key outline already uses this record (same layer + id, or same layer + name), or the
                      same park + record is asked twice; another record for an outlined park stays, marked 'key_now'
                  Q1  no proper name word shared by the park and the record (kpc_tiers.match)
                  Q2  the same record (layer + record id) offered to 2+ parks and this park's name is not equal to it
                  Q3  world-finder LIKELY rows (names only: 799 NO / 374 NOT SURE / 30 YES) -> parked as 'map look' (they get
                      a picture, below, and come back with it)
  todo <out>    the picture list for the map-picture maker (KPC_9): every NOT SURE row (any question file) + every Q3 'map
                look' row, best-activated parks first, minus the ones that already have a picture -> a questions file
  second-look <pictures dir> <raw base>
                every picture KPC_9 made -> data/waiting/questions/second-look.json: the original row, answer blank again,
                'picture' = the picture's address, so chat 11 grades it again WITH the map (record outline + POTA pin)
Never fails; nothing is decided here (a parked row is only not asked).
  python3 .github/scripts/kpc_q_gate.py gate | todo <out.json> | second-look <pictures dir> <raw base url>"""
import collections, datetime as dt, glob, json, os, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_tiers as T  # noqa: E402

QD = pathlib.Path('data/waiting/questions')
PARKED, SECOND = QD / 'parked.json', QD / 'second-look.json'
TODAY = dt.date.today().isoformat()
SKIP = {'parked.json', 'second-look.json', 'not-sure-for-chat9.json', 'map-audit.json', 'map-audit-auto.json'}   # Nov 2 5:50 PM: the map audit ASKS about the key's own outline (Q0 parked 1,987 of its rows); never gated


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def qfiles():
    for f in sorted(QD.glob('*.json')):
        if f.name in SKIP or f.name.startswith('_'): continue
        d = load(f, None)
        qs = d.get('questions') if isinstance(d, dict) else d
        if isinstance(qs, list) and qs and isinstance(qs[0], dict) and 'ref' in qs[0]: yield f, d, qs


def key(q): return (str(q.get('layer') or q.get('url') or ''), str(q.get('record')))


def names(q):
    pw, rw = T.proper(str(q.get('park') or '')), T.proper(str(q.get('record_name') or ''))
    if not pw or not rw: return None, set(), set(), set()
    s, po, ro = T.match(pw, rw)
    return True, s, po, ro


# ---- Q0 ALREADY IN THE KEY (chat 10, Nov 2; chat 2's 'collector flood' ask, HQ GO): a row whose park's key outline already uses
# THAT record (same layer + same record id, or same layer + same name) is closed (parked 'Q0', kept); a row for a park that already
# has an outline from ANOTHER record stays, with 'key_now' saying which, so chat 11 judges 'is this one better?'. Exact duplicate
# open rows (same park + layer + record) are asked once. US / CA keys from KPC-Links, world keys from data/world-key/<CC>.json.
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
PADUS = 'pad-us/pad_us/mapserver/0'


def nurl(u): return re.sub(r'/query$', '', str(u or '').strip().lower().rstrip('/')).rstrip('/')


def nname(x): return re.sub(r'[^a-z0-9]+', ' ', str(x or '').lower()).strip()


_KEYS, _LAY = {}, {}


def key_parks(ref):
    cc = ref.split('-')[0]
    if cc in ('US', 'CA'):
        return None   # per state: found through key_area()
    if cc not in _KEYS: _KEYS[cc] = (load(f'data/world-key/{cc}.json', {}) or {}).get('parks') or {}
    return _KEYS[cc]


def key_area(q):
    ref = str(q.get('ref') or ''); cc = ref.split('-')[0]
    if cc not in ('US', 'CA'): return key_parks(ref)
    st = str(q.get('st') or q.get('area') or '').upper()
    st = st[3:] if st[:3] in ('US-', 'CA-') else st
    names = [f'{cc}-{st}'] if len(st) == 2 else []
    if not names:   # no state on the row: look in every state file of that country once (cached)
        names = sorted(p.stem for p in (LINKS / 'data' / ('us-key' if cc == 'US' else 'ca-key')).glob(f'{cc}-??.json'))
    for nm in names:
        if nm not in _KEYS: _KEYS[nm] = (load(LINKS / 'data' / ('us-key' if cc == 'US' else 'ca-key') / f'{nm}.json', {}) or {}).get('parks') or {}
        if ref in _KEYS[nm]: return _KEYS[nm]
    return {}


def layers():
    if not _LAY:
        us = load(LINKS / 'data/us-key/layers.json', {}) or {}
        _LAY['us'] = {k: nurl(v[0]) for k, v in us.items() if isinstance(v, list) and v}
        ca = load(LINKS / 'data/ca-key/layers.json', {}) or {}
        _LAY['ca'] = {k: [nurl(u) for u in (v if isinstance(v, list) else [v])] for k, v in ca.items()}
        w = load('data/world-key/layers.json', {}) or {}
        _LAY['w'] = {k: nurl(v) for k, v in w.items() if isinstance(v, str)}
    return _LAY


def m_rows(ref, p):
    """[(layer urls, record id as text, name)] of a key entry's joined records."""
    L = layers(); cc = ref.split('-')[0]; out = []
    for x in (p or {}).get('m') or []:
        if not isinstance(x, (list, tuple)) or not x: continue
        i, nm = x[0], (x[1] if len(x) > 1 else '')
        if cc not in ('US', 'CA'):
            lab = x[2] if len(x) > 2 else ''
            out.append(([L['w'].get(lab, '')], str(i), nm)); continue
        if isinstance(i, int) or str(i).isdigit():
            out.append(([PADUS, 'cpcad', 'cwa'], str(i), nm)); continue
        s = str(i)
        if cc == 'CA' and ':' in s:
            lab, rid = s.rsplit(':', 1); out.append((L['ca'].get(lab, []), rid, nm)); continue
        for pre, u in L['us'].items():
            if s.startswith(pre) and s[len(pre):].isdigit(): out.append(([u], s[len(pre):], nm)); break
        else: out.append(([], s, nm))
    return out


def in_key(q):
    """-> (same, text): same = the key already uses this record (or this layer + this name); text = what the key has now."""
    ref = str(q.get('ref') or '')
    K = key_area(q) or {}
    p = K.get(ref)
    if not isinstance(p, dict) or not p.get('m'): return False, ''
    lay, rid, rn = nurl(q.get('layer') or q.get('url')), str(q.get('record')), nname(q.get('record_name'))
    rows = m_rows(ref, p)
    for us, i, nm in rows:
        same_lay = any(u and (u == lay or (u in (PADUS, 'cpcad', 'cwa') and u in lay)) for u in us)
        if same_lay and (i == rid or (rn and nname(nm) == rn)): return True, f'the key already uses this record ({i} {nm})'
    first = rows[0]
    return False, f'the park already has an outline: record {first[1]} ({str(first[2])[:60]}){" + %d more" % (len(rows) - 1) if len(rows) > 1 else ""}; is this record BETTER?'


def gate():
    P = load(PARKED, {}) or {}; prow = P.setdefault('rows', [])
    have = {(r.get('ref'), *key(r)) for r in prow}
    share = collections.defaultdict(set)
    for f, d, qs in qfiles():
        for q in qs: share[key(q)].add(q.get('ref'))
    moved = collections.Counter(); asked = set()
    for f, d, qs in qfiles():
        keep = []
        for q in qs:
            if q.get('answer'): keep.append(q); continue
            ok, s, po, ro = names(q)
            why = None
            try: same, now = in_key(q)
            except Exception: same, now = False, ''  # noqa: BLE001
            dup = (q.get('ref'), *key(q))
            if same: why = f'Q0 {now}'
            elif dup in asked: why = 'Q0 the same park + record is already asked in another row'
            elif now and not q.get('key_now'): q['key_now'] = now
            if why: pass
            elif ok and not s: why = 'Q1 no name word shared by the park and the record'
            elif ok and len(share[key(q)]) >= 2 and (po or ro): why = f'Q2 one record offered to {len(share[key(q)])} parks; this name is not the record\'s'
            elif f.name == 'world-finder.json' and str(q.get('tier') or T.tier(q.get('park'), q.get('record_name'))[0]) == 'LIKELY':
                why = 'Q3 map look: a names-only LIKELY (world finder); comes back with a picture'
            if not why: keep.append(q); asked.add(dup); continue
            if (q.get('ref'), *key(q)) not in have:
                prow.append({**q, 'gate': why, 'parked': TODAY, 'from_file': f.name}); have.add((q.get('ref'), *key(q)))
            moved[f'{f.name} {why[:2]}'] += 1
        if len(keep) != len(qs):
            if isinstance(d, dict): d['questions'] = keep
            else: d = keep
            json.dump(d, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    P['about'] = 'Questions the gate kept away from chat 11 (kpc_q_gate.py; Brandon GO Nov 2 4:40 AM). Kept, not deleted.'
    P['updated'] = TODAY
    json.dump(P, open(PARKED, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Question gate::{sum(moved.values())} open questions parked ({dict(moved)}); {len(prow)} on the parked list', flush=True)


def activity():
    for p in ('data/pota/activity.json', '../out/pota/activity.json'):
        a = (load(p, {}) or {}).get('parks')
        if a: return a
    return {}


def _same(r):
    try: return in_key(r)[0]
    except Exception: return False  # noqa: BLE001


def todo(out):
    A = activity(); S = load(SECOND, {}) or {}
    done = {(r.get('ref'), *key(r)) for r in S.get('questions') or []}
    rows = []
    for f, d, qs in qfiles():
        for q in qs:
            if str(q.get('answer') or '').upper().startswith('NOT SURE'): rows.append({**q, 'from_file': f.name})
    for q in (load(PARKED, {}) or {}).get('rows') or []:
        if str(q.get('gate', '')).startswith('Q3'): rows.append(q)
    rows = [r for r in rows if (r.get('ref'), *key(r)) not in done and r.get('record') is not None and str(r.get('layer') or '').startswith('http') and not _same(r)]
    rows.sort(key=lambda r: (-((A.get(r.get('ref')) or [0])[0] or 0), r.get('ref')))
    json.dump({'about': 'map-picture to-do (kpc_q_gate.py todo): NOT SURE + map-look rows, most activated first', 'questions': rows},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'::notice title=Second look::{len(rows)} rows need a picture (NOT SURE + map look), most activated first', flush=True)


def second_look(pics, raw):
    pics = pathlib.Path(pics); idx = load(pics / 'index.json', None)
    items = idx.get('items') if isinstance(idx, dict) else idx
    by = {}
    for it in items or []:
        j = str((it or {}).get('job') or (it or {}).get('id') or '') if isinstance(it, dict) else ''
        if j.startswith('questions:') and it.get('file') and it.get('status') in (None, 'ok', 'done'):
            by[j] = it
    S = load(SECOND, {}) or {}; rows = S.setdefault('questions', [])
    have = {(r.get('ref'), *key(r)) for r in rows}
    src = []
    for f, d, qs in qfiles(): src += [{**q, 'from_file': f.name} for q in qs if str(q.get('answer') or '').upper().startswith('NOT SURE')]
    src += [q for q in (load(PARKED, {}) or {}).get('rows') or [] if str(q.get('gate', '')).startswith('Q3')]
    n = 0
    for q in src:
        lay = str(q.get('layer') or '')
        hit = next((it for i, it in by.items() if i.startswith(f"questions:{q.get('ref')}:{q.get('record')}:")), None)
        if not hit or (q.get('ref'), *key(q)) in have: continue
        rows.append({**q, 'first_answer': q.get('answer') or q.get('gate'), 'answer': None, 'checked_by': None, 'how': None,
                     'picture': raw.rstrip('/') + '/' + str(hit['file']).lstrip('/'), 'caption': hit.get('caption'),
                     'question': 'Second look WITH THE MAP (gold = the record, red dot = the POTA pin): is this record that park? YES / NO / NOT SURE'})
        have.add((q.get('ref'), *key(q))); n += 1
    S['about'] = 'Second look with a map picture (kpc_q_gate.py; Brandon GO Nov 2): rows that were NOT SURE or names-only, now with the record + pin drawn'
    S['updated'] = TODAY
    json.dump(S, open(SECOND, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Second look::{n} rows back for chat 11 with a picture; {sum(1 for r in rows if not r.get("answer"))} open', flush=True)


if __name__ == '__main__':
    try:
        a = sys.argv[1:]
        if a[:1] == ['gate']: gate()
        elif a[:1] == ['todo']: todo(a[1])
        elif a[:1] == ['second-look']: second_look(a[1], a[2])
        else: print(__doc__)
    except Exception as e: print(f'::notice title=Question gate::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
