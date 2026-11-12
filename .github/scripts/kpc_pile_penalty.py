#!/usr/bin/env python3
"""Pile solver: park-type penalty (round 3, Nov 7 2026). REPORT ONLY.

What it does
  Gives every pile-solver row a number ("score") and a penalty for park types / record kinds / name classes whose official
  outline is rarely found or joined. The numbers come from the Links US key (see build_weights). It never changes a verdict,
  never reads or writes state['auto'], and the side file says "auto": false.

Switch
  KPC_TYPE_PENALTY=report   -> kpc_pile_solver.run() writes data/pile-solver/type-penalty.json next to research-rank.json
  anything else / unset     -> nothing is computed, nothing is written (the solver's outputs stay byte for byte the same)

Weights
  data/pile-solver/type-penalty-weights.json, made by:  python3 -I .github/scripts/kpc_pile_penalty.py weights <links_dir> <out.json>
  Run it again after each US key rebuild. The solver itself never reads the Links key for weights: it stays offline and deterministic.

Sample for Quality
  python3 -I .github/scripts/kpc_pile_penalty.py sample <links_dir> <data_dir> <out_prefix>   (writes <out_prefix>.csv and .md)

Everything marked GUESS is a number nobody measured: it is a starting value Brandon can change in the weights file's "params".
"""
import csv, glob, json, os, pathlib, re, sys, collections

HERE = pathlib.Path(__file__).resolve().parent
WEIGHTS_FILE = 'data/pile-solver/type-penalty-weights.json'

PARAMS = {
    'shrink_M': 20,            # GUESS: pseudo-parks at the global rate, so a type with 3 parks cannot get a big penalty
    'points_per_rate': 60,     # GUESS: 1.00 of outline-rate deficit = 60 points (a type at 0.43 vs 0.85 = 25 = the cap)
    'cap': 25,                 # GUESS: one signal can take at most 25 points
    'type_scale': 0.5,         # GUESS: the POTA-type rate counts half (it says "outline often missing", not "join wrong")
    'type_cap': 12,
    'designation_ignored': 25, # GUESS: the key itself says the record's designation disagreed with the park's kind
    'baseline': {'SOLVED-JOIN': 80, 'SOLVED-PIN': 55, 'NEEDS-PERSON': 30},   # GUESS: the solver has no numeric score today
    'pin_off': 10, 'two_agencies': 5,                                         # GUESS
    'demote_below': 60,        # GUESS: a SOLVED-JOIN whose score falls under this is "would_demote" (reported only)
    'min_n_type': 10, 'min_n_kind': 8, 'min_n_name': 4,   # fewer parks than this = no evidence = weight 0
    # Nov 8 (Quality Nov 7 A1/A2): the type/kind/name weights are a statistical PRIOR, not a row-quality ranking; these two flags look
    # at THIS row's own match instead (they report only; auto stays false)
    'no_record': 15,           # a solved row with no record id / record name (US-9906)
    'unit_mismatch': 15,       # a unit / direction word in one name only (Salem Unit vs the whole park; Brush Mountain vs Brush Mountain East)
}
UNIT_WORDS = {'north', 'south', 'east', 'west', 'upper', 'lower', 'middle', 'unit', 'tract', 'annex', 'addition', 'northern', 'southern', 'eastern', 'western'}


def unit_words(name):
    return {w for w in re.findall(r'[a-z]+', str(name or '').lower()) if w in UNIT_WORDS}
# name classes (word boundaries; "Churchill" must not hit "church"). university is NOT here: it is the shared rule in
# kpc-maprep-candidates.js and had weight 0.
NAME_CLASSES = {
    'cemetery': r'\bcemeter', 'golf': r'\bgolf\b', 'school': r'\bschools?\b', 'easement': r'\beasement', 'mitigation': r'\bmitigation\b',
    'row_corridor': r'\b(right.of.way|corridor|greenway|rail.?trail)\b', 'airport': r'\b(airport|airstrip)\b',
    'field_office': r'\bfield office\b', 'treatment_works': r'\b(stormwater|treatment|sewage|landfill)\b',
}


def _ld(p, d=None):
    try: return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except Exception: return d if d is not None else {}   # noqa: BLE001


def load_us_key(links):
    park = {}
    for f in sorted(glob.glob(f'{links}/data/us-key/US-??.json')):
        for r, p in (_ld(f).get('parks') or {}).items(): park[r] = p
    return park


def shrunk_raw(official, n, goff, P=PARAMS):
    s = (official + P['shrink_M'] * goff) / (n + P['shrink_M'])
    return s, min(P['cap'], max(0, round((goff - s) * P['points_per_rate'])))


# ---------------------------------------------------------------- weights from the real key
def build_weights(links, today=None):
    park = load_us_key(links)
    N = len(park)
    goff = sum(p.get('g') == 'official' for p in park.values()) / max(1, N)
    P = PARAMS

    def table(keyf, min_n):
        a = collections.defaultdict(collections.Counter)
        for r, p in park.items():
            k = keyf(p)
            if not k: continue
            a[k]['n'] += 1; a[k][p.get('g') or '?'] += 1
        out = {}
        for k, c in sorted(a.items(), key=lambda kv: (-kv[1]['n'], kv[0])):
            if c['n'] < min_n: continue
            s, raw = shrunk_raw(c['official'], c['n'], goff)
            out[k] = {'n': c['n'], 'official': c['official'], 'pin': c['pin'], 'approximate': c['approximate'],
                      'rate': round(c['official'] / c['n'], 3), 'shrunk_rate': round(s, 3), 'raw': raw}
        return out
    types = table(lambda p: p.get('t'), P['min_n_type'])
    kinds = table(lambda p: (p.get('bk') or [0, 0, ''])[2] if len(p.get('bk') or []) > 2 else '', P['min_n_kind'])
    names = {}
    for cls, pat in NAME_CLASSES.items():
        c = collections.Counter(); rx = re.compile(pat, re.I)
        for r, p in park.items():
            if rx.search(p.get('n') or ''): c['n'] += 1; c[p.get('g') or '?'] += 1
        if c['n'] >= P['min_n_name']:
            s, raw = shrunk_raw(c['official'], c['n'], goff)
            names[cls] = {'n': c['n'], 'official': c['official'], 'pin': c['pin'], 'rate': round(c['official'] / c['n'], 3), 'shrunk_rate': round(s, 3), 'raw': raw}
        else:
            names[cls] = {'n': c['n'], 'official': c['official'], 'pin': c['pin'], 'raw': 0, 'note': 'fewer than %d parks: no evidence, weight 0' % P['min_n_name']}
    return {
        'auto': False,
        'about': 'Report only. A statistical type PRIOR (Quality Nov 7: not a row-quality ranking); the match part checks the row itself. Weights for the pile-solver park-type penalty, computed from the Links US key (outline rate by POTA type, by official-record '
                 'kind code and by name class). Regenerate after each US key rebuild. Nothing here changes a verdict.',
        'made': today or '', 'us_key_parks': N, 'global_official_rate': round(goff, 4),
        'how': 'rate = parks with an official outline (g=official) / parks of the group. shrunk = (official + M*global) / (n + M). '
               'raw = clamp(round((global - shrunk) * points_per_rate), 0, cap). Groups under the minimum n get no row (weight 0).',
        'params': P, 'name_patterns': NAME_CLASSES, 'types': types, 'kinds': kinds, 'names': names,
    }


# ---------------------------------------------------------------- the penalty (pure function, no I/O)
def type_penalty(row, kp, W, key_join=None):
    """row = solver output row, kp = the US key row of the park, W = weights, key_join = overrides.json parks[ref].join (list) or None.
    -> dict, or None when the row has no score (UNTOUCHED). Never raises on odd data; never touches any state."""
    P = W.get('params') or PARAMS
    verdict = row.get('verdict')
    base = (P['baseline'] or {}).get(verdict)
    if base is None: return None
    flag = str(row.get('pin_flag') or '')
    if 'pin may be off' in flag: base -= P['pin_off']
    if 'two agencies' in flag: base -= P['two_agencies']
    kp = kp or {}
    join = verdict == 'SOLVED-JOIN'
    rid = str(row.get('record_id') or '')
    bk = kp.get('bk') or [None, None, '']
    hows = [str(m[3]) for m in (kp.get('m') or []) if isinstance(m, list) and len(m) > 3 and str(m[0]) == rid] if rid else []
    parts = {'type': 0, 'kind': 0, 'name': 0, 'designation': 0, 'match': 0}
    why = []
    signed = join and ((rid and rid in [str(x) for x in (key_join or [])]) or any(h.startswith('reviewed') for h in hows))
    if signed:
        why.append('person-signed join: no penalty')
    else:
        # POTA type: not used on a join (a low outline rate says nothing about whether THIS join is right)
        t = (W.get('types') or {}).get(kp.get('t') or '')
        if t and not join:
            parts['type'] = min(P['type_cap'], round(P['type_scale'] * t['raw']))
            if parts['type']: why.append(f"type {kp.get('t')!r}: outline in {t['rate']:.0%} of {t['n']} parks")
        # record kind code: only when the key's best record IS the record the solver joined (or nothing was joined)
        code = bk[2] if len(bk) > 2 else ''
        same = bool(rid) and str(bk[0]) == rid
        if code and (same or not join):
            k = (W.get('kinds') or {}).get(code)
            if k:
                parts['kind'] = k['raw']
                if k['raw']: why.append(f"record kind {code}: outline in {k['rate']:.0%} of {k['n']} parks")
        elif join and code and not same:
            why.append(f'key kind {code} belongs to record {bk[0]}, not the joined {rid}: ignored')
        # name class
        best = 0
        for cls, pat in (W.get('name_patterns') or {}).items():
            if re.search(pat, kp.get('n') or row.get('pota_name') or '', re.I):
                w = ((W.get('names') or {}).get(cls) or {}).get('raw', 0)
                if w > best: best = w
                if w: why.append(f'name class {cls}')
        parts['name'] = best
        # the key's own statement that the joined record's designation disagreed with the park
        if join and any('designation code ignored' in h for h in hows):
            parts['designation'] = P['designation_ignored']
            why.append('the key joined this record by name only; its designation code disagreed with the park (designation code ignored)')
        # this row's own match (Quality Nov 7 A2), independent of the type prior
        rname = str(row.get('record_name') or '')
        if verdict != 'NEEDS-PERSON' and not rid and not rname:
            parts['match'] = P.get('no_record', 15); why.append('no record id or name: cannot rank as an exact match')
        elif rname:
            a, b = unit_words(row.get('pota_name') or kp.get('n')), unit_words(rname)
            if a != b:
                parts['match'] = P.get('unit_mismatch', 15); why.append(f"unit/direction words differ: park {sorted(a) or '-'} vs record {sorted(b) or '-'}")
    pen = min(P['cap'], max(parts.values()))
    after = base - pen
    return {'ref': row.get('ref'), 'park': row.get('pota_name'), 'verdict': verdict, 'score_before': base, 'penalty': pen, 'parts': parts,
            'score_after': after, 'would_demote': bool(join and after < P['demote_below']), 'why': '; '.join(why),
            'record_id': rid, 'auto': False}


def key_join_of(links_root):
    """overrides.json parks[ref].join from the Links key (person-signed joins). Nov 12 2026 (KPC owner; KPC-Links #151 split): the
    WHOLE set, manifest + parts (kpc_overrides_whole); a part that is missing or does not match raises, never a partial set."""
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    import kpc_overrides_whole as OVW
    return {r: (v or {}).get('join') or [] for r, v in OVW.parks_whole(pathlib.Path(links_root) / 'data/us-key/overrides.json', missing_ok=True, links=links_root).items()}


def report(rows, key_row_fn, W, key_join):
    out = []
    for ref in sorted(rows):
        r = rows[ref]
        if not r.get('in_pile', True): continue
        try: x = type_penalty(r, key_row_fn(r.get('area') or '', ref) if (r.get('area') or '').startswith('US-') else {}, W, key_join.get(ref))
        except Exception as e:   # noqa: BLE001  (one odd row never stops the report)
            x = {'ref': ref, 'error': f'{type(e).__name__}: {str(e)[:80]}', 'auto': False}
        if x: out.append(x)
    return out


def write_side(root, items, W):
    """data/pile-solver/type-penalty.json. 'auto' is a literal False here; this function never touches state.json."""
    side = pathlib.Path(root) / 'data' / 'pile-solver' / 'type-penalty.json'
    side.parent.mkdir(parents=True, exist_ok=True)
    side.write_text(json.dumps({'auto': False, 'about': 'Report only. Park-type penalty (round 3). No verdict was changed. auto stays false.',
                                'weights_made': W.get('made'), 'rows': items}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return str(side)


# ---------------------------------------------------------------- command line
def _sample(links, data, prefix):
    W = _ld(os.environ.get('WEIGHTS') or pathlib.Path(data) / WEIGHTS_FILE) or build_weights(links)
    park = load_us_key(links); kj = key_join_of(links)
    rows = {}
    for f in sorted(glob.glob(f'{data}/data/waiting/in/data/pile-solver/*.json')):
        if f.endswith('run-log.md'): continue
        for ref, p in (_ld(f).get('parks') or {}).items():
            if ref in park: rows[ref] = dict(p, ref=ref)
    items = []
    for ref in sorted(rows):
        x = type_penalty(rows[ref], park[ref], W, kj.get(ref))
        if x: items.append((x, rows[ref], park[ref]))
    with open(prefix + '.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['ref', 'park', 'pota_type', 'verdict', 'score_before', 'penalty', 'type', 'kind', 'name', 'designation', 'score_after', 'would_demote',
                    'why', 'record_id', 'record_name', 'quality_grade (RIGHT / WRONG / UNSURE)', 'quality_note'])
        for x, r, k in sorted(items, key=lambda t: (-t[0]['penalty'], t[0]['ref'])):
            p = x['parts']
            w.writerow([x['ref'], x['park'], k.get('t'), x['verdict'], x['score_before'], x['penalty'], p['type'], p['kind'], p['name'], p['designation'],
                        x['score_after'], 'yes' if x['would_demote'] else 'no', x['why'], x['record_id'], r.get('record_name') or '', '', ''])
    nz = [t for t in items if t[0]['penalty'] > 0]
    wd = [t for t in items if t[0]['would_demote']]
    md = [f"# Pile solver park-type penalty: sample output (report only)", '',
          f"Weights made {W.get('made') or 'now'} from {W['us_key_parks']} US key parks (global outline rate {W['global_official_rate']}). "
          f"{len(items)} scored US pile rows; {len(nz)} with a penalty above 0; {len(wd)} SOLVED-JOIN rows would be demoted (reported only; no verdict changed). auto stays false.", '',
          'Grade the CSV: `quality_grade` RIGHT (the penalty is fair), WRONG (it should be 0 or bigger) or UNSURE, plus a note. Every number is a GUESS until graded.', '',
          '| ref | park | POTA type | verdict | before | penalty (type/kind/name/desig) | after | would demote | why |', '|---|---|---|---|---|---|---|---|---|']
    for x, r, k in sorted(nz, key=lambda t: (-t[0]['penalty'], t[0]['ref'])):
        p = x['parts']
        md.append(f"| {x['ref']} | {str(x['park'])[:40]} | {k.get('t')} | {x['verdict']} | {x['score_before']} | -{x['penalty']} ({p['type']}/{p['kind']}/{p['name']}/{p['designation']}) | {x['score_after']} | {'yes' if x['would_demote'] else 'no'} | {x['why'][:110]} |")
    pathlib.Path(prefix + '.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'{len(items)} rows scored, {len(nz)} penalised, {len(wd)} would demote -> {prefix}.csv / .md')


def main(argv):
    if len(argv) >= 4 and argv[1] == 'weights':
        W = build_weights(argv[2], os.environ.get('MADE') or '')
        pathlib.Path(argv[3]).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(argv[3]).write_text(json.dumps(W, ensure_ascii=False, indent=1, sort_keys=False) + '\n', encoding='utf-8')
        print(f"wrote {argv[3]}: {len(W['types'])} types, {len(W['kinds'])} kinds, {len(W['names'])} name classes")
    elif len(argv) >= 5 and argv[1] == 'sample':
        _sample(argv[2], argv[3], argv[4])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
