#!/usr/bin/env python3
"""Blind two-pass kits (hand-off 05, part 4).

The answer key is written beside the kits, never inside them. One pass does not
contain the other pass. No network.
"""
import json, pathlib, random, re

ASK = [
    'the name at the top of the page',
    "says '& Preserve' (or two kinds)",
    'says it is inside another named area, and that area\'s name',
    'the size on the page, the number and the words around it',
    'named tracts, if a map shows them',
    'could not tell',
]


def _core(text):
    import kpc_park_pages_rules as R
    return R.name_core(text or '')


def _num(text):
    m = re.search(r'(\d{1,3}(?:,\d{3})+|\d+)', str(text or ''))
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', ''))
    except ValueError:
        return None


def _tracts(text):
    return sorted({p.strip().lower() for p in re.split(r'[\n,;]+', str(text or '')) if p.strip()})


def open_parks(facts_by_area):
    """Questions still open: the bot asked, and no person has answered."""
    out = []
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            person = fact.get('person') or {}
            if person and not person.get('could_not_tell'):
                continue
            if not (fact.get('questions') or []):
                continue
            pota = fact.get('pota') or {}
            out.append({
                'ref': ref,
                'area': area,
                'name': pota.get('name') or '',
                'type': pota.get('type') or '',
                'link': (fact.get('asked') or {}).get('url') or pota.get('link') or '',
                'ask': list(ASK),
            })
    return out


def plant_pool(facts_by_area, known_path):
    """Parks whose answer is already known: a person's row, or a must row in known-answers."""
    plants = []
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            person = fact.get('person') or {}
            if not person or person.get('could_not_tell'):
                continue
            plants.append({
                'ref': ref, 'source': 'person',
                'name': person.get('name') or '',
                'combined': bool(person.get('combined')),
                'inside_name': person.get('inside_name') or '',
                'size': person.get('size') or '',
                'tracts': person.get('tracts') or '',
            })
    if known_path and pathlib.Path(known_path).is_file():
        doc = json.loads(pathlib.Path(known_path).read_text(encoding='utf-8'))
        groups = []
        if isinstance(doc, dict):
            for value in doc.values():
                if isinstance(value, list):
                    groups.extend(value)
        for row in groups:
            if not isinstance(row, dict) or row.get('level') != 'must' or not row.get('ref'):
                continue
            expect = row.get('expect') or {}
            plants.append({
                'ref': row['ref'], 'source': 'known-answers',
                'name': row.get('pota_name') or '',
                'combined': bool(expect.get('designation.combined')),
                'inside_name': (expect.get('inside_of[0].unit') or ''),
                'size': '',
                'tracts': '',
            })
    # one plant per ref, person wins when both exist
    by_ref = {}
    for row in plants:
        if row['source'] == 'person' or row['ref'] not in by_ref:
            by_ref[row['ref']] = row
    return list(by_ref.values())


def public_card(fact_card):
    return {k: fact_card.get(k) or '' for k in ('ref', 'name', 'type', 'link')} | {'ask': list(ASK)}


def make_kits(facts_by_area, out_dir, keys_dir, n=40, seed=1, known_path=''):
    """Two blind passes and a key that is not inside the kit folder."""
    out = pathlib.Path(out_dir)
    keys = pathlib.Path(keys_dir)
    if keys.resolve() == out.resolve() or out.resolve() in keys.resolve().parents:
        raise RuntimeError('the answer key must not sit inside the kit')
    rng = random.Random(int(seed))
    opened = open_parks(facts_by_area)
    rng.shuffle(opened)
    chosen = opened[:n]
    pool = [p for p in plant_pool(facts_by_area, known_path) if p['ref'] not in {c['ref'] for c in chosen}]
    rng.shuffle(pool)
    count = min(len(pool), 4 + (int(seed) % 5))
    if len(pool) >= 4:
        count = max(4, min(8, count))
    plants = pool[:count]
    cards = list(chosen)
    by_ref = {}
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            by_ref[ref] = fact
    for plant in plants:
        fact = by_ref.get(plant['ref']) or {}
        pota = fact.get('pota') or {}
        cards.append({
            'ref': plant['ref'],
            'area': fact.get('area') or '',
            'name': pota.get('name') or plant.get('name') or '',
            'type': pota.get('type') or '',
            'link': (fact.get('asked') or {}).get('url') or pota.get('link') or '',
            'ask': list(ASK),
        })
    passes = {}
    for label, salt in (('pass1', 0), ('pass2', 1)):
        order = list(cards)
        random.Random(int(seed) + salt + 17).shuffle(order)
        if label == 'pass2' and [c['ref'] for c in order] == [c['ref'] for c in passes.get('pass1', [])]:
            order = list(reversed(order))
        folder = out / label
        folder.mkdir(parents=True, exist_ok=True)
        public = [public_card(c) for c in order]
        (folder / 'parks.json').write_text(json.dumps(public, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        (folder / 'README.md').write_text(
            'Read each park page. Write what you see. Do not look at the other pass.\n'
            'For each park give the name at the top, whether it says two kinds, whether it sits inside another named area,\n'
            'the size and the words around it, and any named tracts. Say could not tell when you cannot.\n',
            encoding='utf-8')
        passes[label] = public
    keys.mkdir(parents=True, exist_ok=True)
    key = {'seed': int(seed), 'plants': plants}
    (keys / 'key.json').write_text(json.dumps(key, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return {'pass1': len(passes['pass1']), 'pass2': len(passes['pass2']), 'plants': len(plants)}


def _as_map(path):
    doc = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    rows = doc.get('parks') if isinstance(doc, dict) else doc
    return {r.get('ref'): r for r in rows or [] if isinstance(r, dict) and r.get('ref')}


def _same(a, b):
    return (_core(a.get('name')) == _core(b.get('name'))
            and bool(a.get('combined')) == bool(b.get('combined'))
            and _core(a.get('inside_name')) == _core(b.get('inside_name'))
            and _num(a.get('size')) == _num(b.get('size'))
            and _tracts(a.get('tracts')) == _tracts(b.get('tracts')))


def _matches_key(answer, plant):
    if _core(plant.get('name')) and _core(answer.get('name')) != _core(plant.get('name')):
        return False
    if 'combined' in plant and bool(answer.get('combined')) != bool(plant.get('combined')):
        return False
    if plant.get('inside_name') and _core(answer.get('inside_name')) != _core(plant.get('inside_name')):
        return False
    if plant.get('size') and _num(answer.get('size')) != _num(plant.get('size')):
        return False
    if plant.get('tracts') and _tracts(answer.get('tracts')) != _tracts(plant.get('tracts')):
        return False
    return True


def score(pass1, pass2, key_path):
    a = _as_map(pass1)
    b = _as_map(pass2)
    refs = sorted(set(a) & set(b))
    agreed = [ref for ref in refs if _same(a[ref], b[ref])]
    differ = [ref for ref in refs if ref not in agreed]
    key = json.loads(pathlib.Path(key_path).read_text(encoding='utf-8'))
    plants = key.get('plants') or []
    hit = 0
    for plant in plants:
        ref = plant.get('ref')
        if ref in a and ref in b and _matches_key(a[ref], plant) and _matches_key(b[ref], plant):
            hit += 1
    return {'agreed': len(agreed), 'differ': len(differ), 'plants': len(plants), 'plant_hits': hit}
