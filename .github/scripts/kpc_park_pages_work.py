#!/usr/bin/env python3
"""Worklist, list drops, and the summary for the park page reader (hand-off 05, part 2).

No network. A list is JSON only: unknown keys are ignored, and nothing in a list is run.
"""
import csv, datetime, io, json, pathlib

REFRESH_DAYS = 30
URL_KEY_RULE = 'q2'            # 23 Nov (job 10): the address key keeps the page number ('?parkId=98'): a numbered page read before is read again. q2 (2:50 PM): the Parks Canada name and Minnesota's script pages fixed too: the ~300 numbered pages read this afternoon are read once more
LIST_RULE = 1                  # 23 Nov: a page many parks share is followed to each park's own link (or its row is read)
RESTING_RETRY_DAYS = 1         # 22 Nov: a page that answered 'resting' (busy, a server error, an empty answer) is tried again the next day
CONFIRMED_REFRESH_DAYS = 365   # 21 Nov: a park already confirmed by its agency id is re-read once a year (an agency may change its page)
LIST_MAX = 5000
SUMMARY_LINES = 40
PERSON_KINDS = {'refused', 'robots', 'script-built', 'none', 'dead'}
PERSON_CODES = {'REFUSED', 'SCRIPT_BUILT', 'NO_PAGE', 'LINK_DEAD', 'AGENCY_HOME_ONLY'}


def age_days(old, today):
    try:
        return (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(old)).days
    except (TypeError, ValueError):
        return None


def load_keys(links):
    """KPC-Links data/us-key/<area>.json. Missing folder = no grades. g is official / approximate / pin."""
    out = {}
    root = pathlib.Path(links) / 'data' / 'us-key' if links else None
    if root is None or not root.is_dir():
        return out
    for f in sorted(root.glob('*.json')):
        try:
            doc = json.loads(f.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        for ref, row in (doc.get('parks') or {}).items():
            if isinstance(row, dict):
                out[ref] = {'g': row.get('g') or '', 'c': row.get('c') or [], 'n': row.get('n') or ''}
    return out


def load_lists(folder, known_refs, done_dir=None):
    """One JSON file per tool. A park number must exist. At most 5,000 rows. A finished list is marked done."""
    out = []
    path = pathlib.Path(folder) if folder else None
    if path is None or not path.is_dir():
        return out
    done_root = pathlib.Path(done_dir) if done_dir else None
    for f in sorted(path.glob('*.json')):
        try:
            doc = json.loads(f.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        parks = doc.get('parks')
        if not isinstance(parks, list) or len(parks) > LIST_MAX:
            continue
        rows = []
        for p in parks:
            if not isinstance(p, dict):
                continue
            ref = p.get('ref')
            if not isinstance(ref, str) or ref not in known_refs:
                continue
            want = p.get('want') if isinstance(p.get('want'), list) else []
            rows.append({'ref': ref, 'why': str(p.get('why') or '')[:200],
                         'want': [str(w) for w in want if isinstance(w, str)][:12]})
        done = False
        if done_root and rows:
            prev = _read(done_root / f.name)
            answered = {r.get('ref') for r in (prev.get('parks') or []) if isinstance(r, dict) and r.get('result')}
            done = all(r['ref'] in answered for r in rows)
        out.append({'name': f.name, 'made_by': str(doc.get('made_by') or '')[:80],
                    'date': str(doc.get('date') or '')[:20], 'why': str(doc.get('why') or '')[:300],
                    'parks': rows, 'done': done})
    return out


def _read(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}


def build_worklist(areas, choose, keys, lists, refs, state, today, areas_only=None, refresh_days=REFRESH_DAYS, not_sure=None,
                   priority=None, confirmed=None, confirmed_refresh_days=CONFIRMED_REFRESH_DAYS):
    """Best first, each park once. choose(ref, row) -> url or ''.
    21 Nov: priority = parks from a PRIVATE list (the likely mismatches: their pin lies outside their record) go first, before
    everything else; their reason is never written (the worklist file only says "priority list"). confirmed = parks already
    confirmed by their agency id: they leave the ordinary tiers and come LAST, read once if never read, then again only after
    confirmed_refresh_days (a yearly re-read). A not-sure row or a dropped list that names a confirmed park still wins."""
    known = {}
    for area, parks in areas.items():
        if areas_only and area not in areas_only:
            continue
        for ref, row in parks.items():
            known[ref] = (area, row)
    used = set()
    order = []

    def add(ref, tier, why):
        if ref in used or ref not in known:
            return
        used.add(ref)
        area, row = known[ref]
        order.append({'ref': ref, 'area': area, 'tier': tier, 'why': why, 'qsos': row.get('qsos') or 0})

    rank = {'wrong likely': 0, 'unsure': 1, 'incomplete': 2, 'unchecked': 3, 'fairly sure': 4}
    help_wants = {'page facts', 'official size', 'map'}
    grouped = {}
    for row in not_sure or []:
        if str(row.get('ref') or '') == '(class)' or row.get('status') != 'open':
            continue
        if not (set(row.get('wants') or []) & help_wants):
            continue
        grouped.setdefault(row['ref'], []).append(row)

    def ns_key(ref):
        best = min(rank.get(r.get('how_sure'), 9) for r in grouped[ref])
        qsos = (known.get(ref) or (None, {}))[1].get('qsos') or 0
        return (best, -qsos, ref)

    pri = [r for r in (priority or []) if isinstance(r, str)]
    for ref in pri:
        add(ref, 0, 'priority list')
    conf = {r for r in (confirmed or []) if isinstance(r, str)}

    for ref in sorted(grouped, key=ns_key):
        why = (grouped[ref][0].get('why') or 'not sure')[:80]
        add(ref, 0, f'not sure: {why}')

    for lst in lists or []:
        if lst.get('done'):
            continue
        for p in lst.get('parks') or []:
            add(p['ref'], 1, f"list {lst.get('name')}: {p.get('why') or lst.get('why') or 'dropped list'}")
    for ref in refs or []:
        if isinstance(ref, str):
            add(ref, 1, 'refs file')

    tier2, tier3, tier4, tier4r, tier4l, tier5, tier6, tier4q = [], [], [], [], [], [], [], []
    read = state.get('read') or {}
    # 23 Nov: how many parks share each page. A park on a shared page read before LIST_RULE is read once more.
    _n = lambda u: (u or '').split('#')[0].rstrip('/').lower()
    sharing = {}
    for ref, (area, row) in known.items():
        u = _n(choose(ref, row) or '')
        if u:
            sharing[u] = sharing.get(u, 0) + 1
    for ref, (area, row) in known.items():
        if ref in used:
            continue
        if ref in conf:   # 21 Nov: confirmed by its agency id: last, and only when never read or a year old
            when_c = (read.get(ref) or {}).get('date') or ''
            age_c = age_days(when_c, today) if when_c else None
            url_c = choose(ref, row) or ''
            if not when_c or (age_c is not None and age_c >= confirmed_refresh_days):
                tier6.append(ref)
            elif '?' in url_c and (read.get(ref) or {}).get('key_rule') != URL_KEY_RULE:
                tier4q.append(ref)
            continue
        key = keys.get(ref) or {}
        grade = str(key.get('g') or '')
        checks = key.get('c') or []
        url = choose(ref, row) or ''
        prev = read.get(ref) or {}
        when = prev.get('date') or ''
        age = age_days(when, today) if when else None
        if checks or grade == 'approximate':
            tier2.append(ref)
        elif grade == 'pin' and url:
            tier3.append(ref)
        elif not when:
            tier4.append(ref)
        elif '?' in url and prev.get('key_rule') != URL_KEY_RULE:
            tier4q.append(ref)   # 23 Nov 'q1': read under the old address key, which gave every numbered page of a site one page
        elif sharing.get(_n(url), 0) >= 2 and prev.get('list_rule') != LIST_RULE:
            tier4l.append(ref)   # 23 Nov: read before shared pages were followed to the park's own link
        elif prev.get('kind') == 'resting' and age is not None and age >= RESTING_RETRY_DAYS:
            tier4r.append(ref)   # 22 Nov: 'resting' means try later, not "read": it does not wait refresh_days
        elif age is not None and age >= refresh_days:
            tier5.append(ref)
    by_busy = lambda r: (-(known[r][1].get('qsos') or 0), r)
    by_old = lambda r: ((read.get(r) or {}).get('date') or '9999', r)
    for ref in sorted(tier2, key=by_busy):
        add(ref, 2, 'check rows or approximate')
    for ref in sorted(tier3, key=by_busy):
        add(ref, 3, 'pin, and a page is on file')
    for ref in sorted(tier4, key=by_busy):
        add(ref, 4, 'never read')
    for ref in sorted(tier4r, key=by_old):
        add(ref, 4, 'resting last time: tried again')
    for ref in sorted(tier4l, key=by_busy):
        add(ref, 4, 'shared page: now read on its own link')
    for ref in sorted(tier4q, key=by_busy):
        add(ref, 4, 'numbered page: read again on its own address (23 Nov key fix)')
    for ref in sorted(tier5, key=by_old):
        add(ref, 5, f'older than {refresh_days} days')
    for ref in sorted(tier6, key=by_old):
        add(ref, 6, f'confirmed by id: read once, then every {confirmed_refresh_days} days')
    return order


PRIVATE_TIERS = {'priority list': 'priority list', 'confirmed by id': 'confirmed by id'}


def public_order(order, today=''):
    """The worklist as it may be written to a public file: parks from the PRIVATE lists (the priority list, the confirmed-by-id
    list) are left out and only counted."""
    rows, counts = [], {}
    for o in order or []:
        w = str(o.get('why') or '')
        key = 'priority list' if w == 'priority list' else 'confirmed by id' if w.startswith('confirmed by id') else ''
        if key:
            counts[key] = counts.get(key, 0) + 1
        else:
            rows.append(o)
    return {'date': today, 'order': rows, 'private_list_parks': counts}


class PrivateFileError(ValueError):
    pass


def private_refs(path, repo_root=None):
    """Park refs from a PRIVATE file (CSV with a 'park' or 'ref' column, a JSON list, or {"parks": [...]}). The file must live
    OUTSIDE any git working tree (it names parks; a repo file is refused). '' -> []."""
    if not path:
        return []
    p = pathlib.Path(path).resolve()
    roots = [pathlib.Path(repo_root).resolve()] if repo_root else []
    roots += [d for d in [p.parent, *p.parents] if (d / '.git').exists()]
    for r in roots:
        try:
            p.relative_to(r)
        except ValueError:
            continue
        raise PrivateFileError(f'{p.name}: a private park list must not live inside a git repository ({r.name}); keep it on the PC')
    text = p.read_text(encoding='utf-8-sig')
    if text.lstrip().startswith(('[', '{')):
        d = json.loads(text)
        d = d.get('parks', []) if isinstance(d, dict) else d
        return [str(x.get('ref') or x.get('park') if isinstance(x, dict) else x).strip() for x in d if x]
    rows = csv.DictReader(io.StringIO(text))
    col = next((c for c in (rows.fieldnames or []) if str(c).strip().lower() in ('park', 'ref')), None)
    if not col:
        raise PrivateFileError(f'{p.name}: no "park" or "ref" column')
    out, seen = [], set()
    for r in rows:
        v = str(r.get(col) or '').strip()
        if v and v not in seen:
            seen.add(v); out.append(v)
    return out


def track(fact):
    """The facts a changed page is judged on. A changed footer is not one of them."""
    if not fact:
        return None
    return {
        'name': (fact.get('name') or {}).get('best') or '',
        'kinds': ', '.join((fact.get('designation') or {}).get('words') or []),
        'sizes': '; '.join(f"{s.get('label') or ''}:{s.get('acres')}" for s in (fact.get('sizes') or [])),
        'host': (fact.get('page') or {}).get('host') or '',
    }


def change_rows(ref, old, new, today):
    if not old or not new or new.get('unchanged'):
        return []
    a, b = track(old), track(new)
    rows = []
    for field in ('name', 'kinds', 'sizes', 'host'):
        if (a or {}).get(field) != (b or {}).get(field):
            rows.append({'ref': ref, 'field': field, 'before': (a or {}).get(field) or '',
                         'after': (b or {}).get(field) or '', 'date': today})
    return rows


def result_of(fact):
    if not fact:
        return ''
    if fact.get('unchanged'):
        return 'unchanged'
    kind = (fact.get('page') or {}).get('kind') or ''
    if kind in ('refused', 'robots'):
        return 'refused'
    if kind == 'none' or not (fact.get('asked') or {}).get('url'):
        return 'no page'
    return 'read'


def questions_of(fact):
    return [q.get('code') for q in (fact.get('questions') or []) if q.get('code')]


def for_a_person(fact):
    kind = (fact.get('page') or {}).get('kind') or ''
    codes = set(questions_of(fact))
    return kind in PERSON_KINDS or bool(codes & PERSON_CODES)


def write_tables(out_dir, facts_by_area, order, lists, today):
    """questions.csv, for-a-person.csv, changes are written by the caller, drafts and list answers here."""
    root = pathlib.Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    by_ref = {}
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            by_ref[ref] = fact
    q_path = root / 'questions.csv'
    p_path = root / 'for-a-person.csv'
    with q_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ref', 'code', 'for', 'plain', 'quote'])
        seen = []
        for item in order or []:
            fact = by_ref.get(item['ref'])
            if fact:
                seen.append(fact)
        for fact in seen:
            for q in fact.get('questions') or []:
                w.writerow([fact.get('ref'), q.get('code'), q.get('for'), q.get('plain'), q.get('quote')])
    with p_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ref', 'name', 'type', 'link', 'plain'])
        for fact in seen:
            if not for_a_person(fact):
                continue
            plain = ' '.join(q.get('plain') or '' for q in fact.get('questions') or [] if q.get('code') in PERSON_CODES)
            pota = fact.get('pota') or {}
            w.writerow([fact.get('ref'), pota.get('name') or '', pota.get('type') or '',
                        (fact.get('asked') or {}).get('url') or '', plain[:300]])
    drafts = {}
    for area, parks in facts_by_area.items():
        rows = []
        for fact in parks.values():
            rows.extend(fact.get('evidence_drafts') or [])
        if rows:
            drafts[area] = rows
            d = root / 'evidence-drafts'
            d.mkdir(parents=True, exist_ok=True)
            (d / f'{area}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    done = root / 'lists-done'
    done.mkdir(parents=True, exist_ok=True)
    for lst in lists or []:
        rows = []
        for p in lst.get('parks') or []:
            fact = by_ref.get(p['ref'])
            res = result_of(fact)
            if not res:
                continue
            rows.append({'ref': p['ref'], 'result': res, 'questions': questions_of(fact or {})})
        doc = {'made_by': lst.get('made_by') or '', 'date': lst.get('date') or today, 'why': lst.get('why') or '',
               'parks': rows}
        (done / lst['name']).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return q_path, p_path


def append_changes(path, rows):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.is_file()
    with p.open('a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['ref', 'field', 'before', 'after', 'date'])
        for r in rows:
            w.writerow([r['ref'], r['field'], r['before'], r['after'], r['date']])


def render_summary(facts_by_area, order, state, today, requests):
    """At most 40 lines. A chat reads this later, so it stands alone."""
    by_ref = {ref: fact for parks in facts_by_area.values() for ref, fact in parks.items()}
    asked = len(by_ref)
    unchanged = sum(1 for f in by_ref.values() if f.get('unchanged'))
    read = asked - unchanged
    left = len(state.get('left') or [])
    kinds = {}
    qcount = {}
    for fact in by_ref.values():
        k = (fact.get('page') or {}).get('kind') or 'none'
        kinds[k] = kinds.get(k, 0) + 1
        for code in questions_of(fact):
            qcount[code] = qcount.get(code, 0) + 1
    lines = [f'Park page reader, {today}.',
             f'Asked {asked}. Read {read}. Kept {unchanged} unchanged. {left} parks are left. The next run continues.',
             f'Requests this run: {requests}.',
             'Pictures: ' + str(sum(1 for f in by_ref.values() if f.get('picture'))) + '.',
             'Pages: ' + ', '.join(f'{k} {n}' for k, n in sorted(kinds.items())) + '.',
             'Questions: ' + (', '.join(f'{k} {n}' for k, n in sorted(qcount.items())) or 'none') + '.']
    errs = state.get('errors') or {}
    if errs:  # 19 Nov 8 PM: parks the reader stopped on are named, never silent; they are read again next run
        lines.append(f'Skipped on a reader error: {len(errs)} (read again next run): ' + '; '.join(f'{r} {e[:80]}' for r, e in sorted(errs.items())[:5]) + '.')
    lines.append('Look at these first:')
    shown = 0
    for item in order or []:
        fact = by_ref.get(item['ref'])
        if not fact:
            continue
        for q in fact.get('questions') or []:
            if shown >= 15:
                break
            lines.append(f"{item['ref']} {q.get('plain')}")
            shown += 1
        if shown >= 15:
            break
    if shown == 0:
        lines.append('None.')
    refused = sorted((state.get('refused') or {}))
    lines.append('Hosts that refused: ' + (', '.join(refused) if refused else 'none') + '.')
    why = state.get('stopped') or ''
    if why:
        lines.append(f'The run stopped on {why}. The next run continues from the parks that are left.')
    lines.append('Files: facts/, questions.csv, for-a-person.csv, evidence-drafts/, changes.csv, lists-done/, summary.md, run.json, state.json.')
    return lines[:SUMMARY_LINES]


def load_facts(out_dir):
    out = {}
    root = pathlib.Path(out_dir) / 'facts'
    if not root.is_dir():
        return out
    for f in sorted(root.glob('*.json')):
        doc = _read(f)
        area = doc.get('area') or f.stem
        out[area] = doc.get('parks') or {}
    return out
