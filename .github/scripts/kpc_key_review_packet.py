#!/usr/bin/env python3
"""The key review packet. Compare two built US key folders and write one small report.

A person starts the workflow by hand. This script does the comparing and the writing.
It joins nothing and changes no park. Standard library only.

  python3 .github/scripts/kpc_key_review_packet.py --selftest
  python3 .github/scripts/kpc_key_review_packet.py scope --old OLD.json --new NEW.json [--states "AK ID"] --json-out FILE
  python3 .github/scripts/kpc_key_review_packet.py judge --state AK --old-exit 0 --new-exit 0 --old-log A --new-log B --out status.json
  python3 .github/scripts/kpc_key_review_packet.py packet --out DIR --states AK,ID --builds DIR [--fact-old DIR] [--fact-new DIR]
          [--gold-old FILE] [--gold-new FILE] [--meta FILE] [--assets FILE]
"""
import argparse, csv, json, pathlib, re, shutil, sys

# The same fixed settings the scorecard uses for both builds (GEO_CACHE and the build date are set by the workflow).
FIXED_BUILD_ENV = {
    'KPC_KEY_REMATCH_IDS': '1', 'KPC_KEY_OFFLINE': '1', 'KPC_MASTER_OWNS': '1',
    'GEO_CACHE_MODE': 'only', 'GEO_DETAIL': '0.001', 'GEO_PAGE': '200',
    'KPC_ANSWER_SHEET': 'off', 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1', 'MINUTES': '600',
}
HARD_FLAGS = ('PIN_FAR', 'SIZE_BIG', 'BIG_PIECE', 'SHARED', 'OTHER_PARK')
NO_ENTRY = 'this PR adds no scope entry'
DONE_LINE = re.compile(r'(?m)^([A-Z]{2}): (\d+) parks, ')
NOTICE_LINE = re.compile(r'::notice title=US key ([A-Z]{2})::(.*)$')
PARK_COLS = ['area', 'ref', 'name', 'record lost', 'record name', 'record acres',
             'outline acres old', 'outline acres new', 'class old -> new',
             'record gained', 'gained name', 'gained acres']
FACT_COLS = ['area', 'ref', 'name', 'class old', 'class new', 'flags old', 'flags new',
             'pin_km old', 'pin_km new', 'why']


def state_code(raw):
    """'US-AK' or 'ak' -> 'AK'. KY is not this builder. Anything else -> ''."""
    s = str(raw or '').strip().upper()
    if s.startswith('US-'): s = s[3:]
    if s == 'KY' or not re.fullmatch(r'[A-Z]{2}', s): return ''
    return s


def parse_state_list(text):
    """A hand-typed list ('AK ID' or 'US-AK,US-ID') into state codes, in order. KY is left out."""
    out, saw_ky = [], False
    for part in re.split(r'[\s,]+', str(text or '').strip()):
        if not part: continue
        raw = part.strip().upper()
        bare = raw[3:] if raw.startswith('US-') else raw
        if bare == 'KY':
            saw_ky = True
            continue
        code = state_code(part)
        if code and code not in out: out.append(code)
    return out, saw_ky


def states_named(scope):
    """State codes from one scope entry, or None when the entry has no state list."""
    if isinstance(scope, dict) and isinstance(scope.get('states'), list):
        out = []
        for raw in scope['states']:
            bare = str(raw or '').strip().upper()
            bare = bare[3:] if bare.startswith('US-') else bare
            code = state_code(raw)
            if code and code not in out: out.append(code)
        return out
    return None


def _entries(doc):
    if not isinstance(doc, dict): return []
    return [e for e in (doc.get('changes') or []) if isinstance(e, dict) and e.get('id')]


def scope_from_docs(old_doc, new_doc, states_text=''):
    """Which states this pull request builds. A states list typed by hand wins."""
    notes = []
    asked, saw_ky = parse_state_list(states_text)
    if saw_ky: notes.append('KY is not built by this tool, so it was left out')
    if not isinstance(old_doc, dict) or not isinstance(new_doc, dict):
        return {'states': [], 'entries': [], 'message': 'the scope file could not be read', 'notes': notes, 'states_from': ''}
    old_ids = {e['id'] for e in _entries(old_doc)}
    entries, states, unnamed = [], [], []
    for e in _entries(new_doc):
        if e['id'] in old_ids: continue
        entries.append(e['id'])
        named = states_named(e.get('scope'))
        if named is None:
            unnamed.append(e['id'])
            continue
        for code in named:
            if code not in states: states.append(code)
    if asked:
        return {'states': asked, 'entries': entries, 'message': '', 'notes': notes, 'states_from': 'input'}
    if not entries:
        return {'states': [], 'entries': [], 'message': NO_ENTRY, 'notes': notes, 'states_from': ''}
    if unnamed:
        notes.append('these new entries name no state list: ' + ', '.join(unnamed))
    if not states:
        who = ', '.join(unnamed or entries)
        return {'states': [], 'entries': entries,
                'message': f'this PR adds a scope entry but it names no states ({who}). Pass the states input, for example AK ID.',
                'notes': notes, 'states_from': ''}
    return {'states': states, 'entries': entries, 'message': '', 'notes': notes, 'states_from': 'scope'}


def _read(path):
    p = pathlib.Path(path)
    if not path or not p.is_file(): return ''
    return p.read_text(encoding='utf-8', errors='replace')


def _load(path):
    p = pathlib.Path(path)
    if not path or not p.is_file(): return None
    try: return json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError): return None


def side_result(state, exit_code, log_text, key_doc=None, key_given=False):
    """One side of a build. ok means a clean finish and a readable key."""
    try: code = int(exit_code)
    except (TypeError, ValueError): code = 1
    finished = any(m.group(1) == state for m in DONE_LINE.finditer(log_text or ''))
    key_good = (not key_given) or (isinstance(key_doc, dict) and isinstance(key_doc.get('parks'), dict))
    ok = code == 0 and finished and key_good
    if code == 124: why = 'timed out'
    elif code == 89: why = 'it tried to use the network, so this side is not used'
    elif code != 0: why = f'exit {code}'
    elif not finished: why = 'no finished line for this state'
    elif not key_good: why = 'the key file was not written'
    else: why = ''
    return {'exit': code, 'ok': ok, 'why': why}


def judge_build(state, old_exit, new_exit, old_text, new_text, old_key=None, new_key=None, keys_given=False):
    old = side_result(state, old_exit, old_text, old_key, keys_given)
    new = side_result(state, new_exit, new_text, new_key, keys_given)
    if old['ok'] and new['ok']: result = 'ok'
    elif old['exit'] == 124 or new['exit'] == 124: result = 'timed out'
    else: result = 'failed'
    return {'state': state, 'result': result, 'old': old, 'new': new}


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)): return None
    return float(v)


def _num_text(v):
    """A number as a person would write it, keeping the fact check's own rounding."""
    n = _num(v)
    if n is None: return ''
    if float(n).is_integer(): return str(int(n))
    return f'{n:.4f}'.rstrip('0').rstrip('.')


def _rows(park):
    out = []
    for raw in (park or {}).get('m') or []:
        if not isinstance(raw, (list, tuple)) or not raw: continue
        out.append({'id': str(raw[0]), 'name': '' if len(raw) < 2 or raw[1] is None else str(raw[1]), 'acres': raw[2] if len(raw) > 2 else None})
    return out


def _acres(rows):
    total, any_n = 0.0, False
    for row in rows:
        n = _num(row.get('acres'))
        if n is None: continue
        total += n
        any_n = True
    return int(round(total)) if any_n else ''


def _sig(rows):
    return sorted((r['id'], r['name'], r['acres']) for r in rows)


def diff_parks(old_key, new_key):
    """Parks whose joined records differ. The check list is not a joined record."""
    old_parks = (old_key or {}).get('parks') or {}
    new_parks = (new_key or {}).get('parks') or {}
    found = []
    for ref in sorted(set(old_parks) | set(new_parks)):
        op = old_parks.get(ref) if isinstance(old_parks.get(ref), dict) else {}
        np = new_parks.get(ref) if isinstance(new_parks.get(ref), dict) else {}
        old_rows, new_rows = _rows(op), _rows(np)
        if _sig(old_rows) == _sig(new_rows): continue
        old_by, new_by = {}, {}
        for r in old_rows: old_by.setdefault(r['id'], []).append(r)
        for r in new_rows: new_by.setdefault(r['id'], []).append(r)
        lost, gained, changed = [], [], []
        for rid in sorted(set(old_by) | set(new_by)):
            a, b = old_by.get(rid) or [], new_by.get(rid) or []
            if a and not b: lost.extend(a)
            elif b and not a: gained.extend(b)
            elif _sig(a) != _sig(b): changed.append((a[0], b[0]))
        name = (np.get('n') if np.get('n') else None) or op.get('n') or ''
        found.append({'ref': ref, 'name': name, 'old_acres': _acres(old_rows), 'new_acres': _acres(new_rows),
                      'lost': lost, 'gained': gained, 'changed': changed})
    return found


def _decode_notice(text):
    """Undo the escapes a ::notice line uses, so the two logs compare as a person would read them."""
    placeholder = '\u0000'
    text = text.replace('%25', placeholder).replace('%0A', '\n').replace('%0D', '').replace(placeholder, '%')
    return text.strip()


def notice_lines(log_text, state):
    out = []
    for line in (log_text or '').splitlines():
        m = NOTICE_LINE.search(line.strip())
        if m and m.group(1) == state: out.append(_decode_notice(m.group(2)))
    return out


def _only(old_lines, new_lines):
    """Lines of the new log that the old log does not have, and the other way, keeping order."""
    from collections import Counter
    oc, nc = Counter(old_lines), Counter(new_lines)
    only_new, only_old = [], []
    seen_n, seen_o = Counter(), Counter()
    for line in new_lines:
        seen_n[line] += 1
        if seen_n[line] > oc[line]: only_new.append(line)
    for line in old_lines:
        seen_o[line] += 1
        if seen_o[line] > nc[line]: only_old.append(line)
    return only_new, only_old


def _flags(entry):
    out = []
    for f in (entry or {}).get('flags') or []:
        if isinstance(f, (list, tuple)) and f: out.append(str(f[0]))
    return out


def _flag_text(flags):
    return ' '.join(flags)


def class_phrase(old_e, new_e):
    co = (old_e or {}).get('class') or ''
    cn = (new_e or {}).get('class') or ''
    if not co and not cn: return ''
    text = f'{co or "none"} -> {cn or "none"}'
    if cn == 'flagged' and cn != co:
        old_set = {tuple(f) for f in (old_e or {}).get('flags') or [] if isinstance(f, (list, tuple)) and f}
        details = []
        for f in (new_e or {}).get('flags') or []:
            if isinstance(f, (list, tuple)) and f and f[0] in HARD_FLAGS and tuple(f) not in old_set and len(f) > 1:
                details.append(str(f[1]))
        if details: text += ' (' + '; '.join(details) + ')'
    return text


def _hard_count(doc):
    counts = (doc or {}).get('counts') or {}
    return sum(int(counts.get(k) or 0) for k in HARD_FLAGS)


def _count(doc, key):
    counts = (doc or {}).get('counts') or {}
    if key not in counts: return None
    try: return int(counts[key])
    except (TypeError, ValueError): return None


def _joined(key, ref):
    park = ((key or {}).get('parks') or {}).get(ref)
    return bool(isinstance(park, dict) and park.get('m'))


def _outline_count(key):
    return sum(1 for ref in ((key or {}).get('parks') or {}) if _joined(key, ref))


def _pin(entry):
    if not isinstance(entry, dict) or 'pin_km' not in entry: return ''
    return _num_text(entry.get('pin_km'))


def _why(old_e, new_e, changed, old_joined, new_joined):
    old_class = (old_e or {}).get('class') or ''
    new_class = (new_e or {}).get('class') or ''
    if old_class == 'verified' and not new_joined: return 'verified outline lost'
    if old_class == 'verified' and new_class and new_class != 'verified' and new_joined: return 'verified got worse'
    if changed: return 'joined records changed'
    if old_class != new_class or _flags(old_e) != _flags(new_e) or _pin(old_e) != _pin(new_e): return 'class or flags differ'
    return ''


def _gold_head(text):
    return [ln.strip() for ln in (text or '').splitlines() if ln.startswith('TUNE:') or ln.startswith('SEALED:')]


def _cell(v):
    return '' if v is None else str(v)


def _arrow(a, b):
    if a is None and b is None: return ''
    return f'{_cell(a)} -> {_cell(b)}'


def _build_phrase(status):
    if not status: return 'build failed or timed out'
    result = status.get('result')
    if result == 'ok': return ''
    if result == 'timed out': return 'build timed out'
    if result == 'failed': return 'build failed'
    return 'build failed or timed out'


def _park_lines(diff, area, phrase):
    """One csv row per record that was lost, gained, or changed."""
    rows = []
    base = {'area': area, 'ref': diff['ref'], 'name': diff['name'],
            'outline acres old': _cell(diff['old_acres']), 'outline acres new': _cell(diff['new_acres']),
            'class old -> new': phrase}
    for row in diff['lost']:
        item = dict(base)
        item.update({'record lost': row['id'], 'record name': row['name'], 'record acres': _num_text(row['acres']),
                     'record gained': '', 'gained name': '', 'gained acres': ''})
        rows.append(item)
    for row in diff['gained']:
        item = dict(base)
        item.update({'record lost': '', 'record name': '', 'record acres': '',
                     'record gained': row['id'], 'gained name': row['name'], 'gained acres': _num_text(row['acres'])})
        rows.append(item)
    for old_row, new_row in diff['changed']:
        item = dict(base)
        item.update({'record lost': old_row['id'], 'record name': old_row['name'], 'record acres': _num_text(old_row['acres']),
                     'record gained': new_row['id'], 'gained name': new_row['name'], 'gained acres': _num_text(new_row['acres'])})
        rows.append(item)
    if not rows:
        item = dict(base)
        item.update({'record lost': '', 'record name': '', 'record acres': '', 'record gained': '', 'gained name': '', 'gained acres': ''})
        rows.append(item)
    return rows


def _plain_change(diff):
    bits = []
    for row in diff['lost']:
        acres = _num_text(row['acres'])
        bits.append(f"lost {row['id']} {row['name']}" + (f" ({acres} acres)" if acres else ''))
    for row in diff['gained']:
        acres = _num_text(row['acres'])
        bits.append(f"gained {row['id']} {row['name']}" + (f" ({acres} acres)" if acres else ''))
    for old_row, new_row in diff['changed']:
        bits.append(f"record {old_row['id']} changed ({_num_text(old_row['acres'])} acres to {_num_text(new_row['acres'])} acres)")
    acres = f" Outline acres {diff['old_acres']} -> {diff['new_acres']}." if diff['old_acres'] != '' or diff['new_acres'] != '' else ''
    return f"{diff['ref']} {diff['name']}: " + '; '.join(bits) + '.' + acres


def _table(headers, rows):
    cells = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in cells:
        for i, c in enumerate(row): widths[i] = max(widths[i], len(c))
    def fmt(row): return '| ' + ' | '.join(c.ljust(widths[i]) for i, c in enumerate(row)) + ' |'
    line = '| ' + ' | '.join('-' * widths[i] for i in range(len(headers))) + ' |'
    return '\n'.join([fmt(headers), line] + [fmt(r) for r in cells])


def _state_dirs(builds, states):
    """{state: folder} from builds/key-AK or builds/AK."""
    found = {}
    root = pathlib.Path(builds) if builds else None
    if root is None or not root.is_dir(): return found
    for path in sorted(root.iterdir()):
        if not path.is_dir(): continue
        name = path.name[4:] if path.name.startswith('key-') else path.name
        if name in states and name not in found: found[name] = path
    return found


def _shape_index(assets):
    out = {}
    for item in assets or []:
        if not isinstance(item, dict): continue
        name = str(item.get('name') or '')
        if re.fullmatch(r'US-[A-Z]{2}\.json\.gz', name) or name.startswith('hand-US-'):
            out[name] = {'date': item.get('created_at') or item.get('createdAt') or item.get('updated_at') or item.get('updatedAt') or '', 'size': item.get('size')}
    return out


def write_packet(out_dir, states, builds=None, fact_old=None, fact_new=None, gold_old=None, gold_new=None, meta=None, assets=None):
    """Write the packet folder. Returns the summary text. Never writes outside out_dir."""
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    out = out.resolve()
    meta = meta or {}
    folders = _state_dirs(builds, states)
    park_rows, fact_rows = [], []
    only_new, only_old = [], []
    table_rows = []
    lost_refs, worse_refs = [], []
    changed_lines, gap_lines = [], []
    per_state = {}
    for state in states:
        area = f'US-{state}'
        folder = folders.get(state)
        status = _load(folder / 'status.json') if folder else None
        phrase = _build_phrase(status)
        old_key = _load(folder / f'US-{state}-old.json') if folder else None
        new_key = _load(folder / f'US-{state}-new.json') if folder else None
        old_fact = _load(pathlib.Path(fact_old) / f'factcheck-{area}.json') if fact_old else None
        new_fact = _load(pathlib.Path(fact_new) / f'factcheck-{area}.json') if fact_new else None
        if phrase:
            why = ''
            if status:
                bits = [x['why'] for x in (status.get('old'), status.get('new')) if isinstance(x, dict) and x.get('why')]
                why = '; '.join(f'{side} {txt}' for side, txt in zip(('old', 'new'), bits) if txt)
            gap_lines.append(f'{state}: the {phrase}' + (f' ({why})' if why else '') + '. This row is not a result.')
            table_rows.append([state, phrase, '—', '—', '—', '—', '—', '—'])
            per_state[state] = {'result': phrase}
            continue
        diffs = diff_parks(old_key, new_key)
        changed_refs = {d['ref'] for d in diffs}
        old_parks = (old_fact or {}).get('parks') or {}
        new_parks = (new_fact or {}).get('parks') or {}
        lost_n = worse_n = 0
        for ref in sorted(set(old_parks) | set(new_parks) | changed_refs):
            old_e, new_e = old_parks.get(ref), new_parks.get(ref)
            old_joined = _joined(old_key, ref) if old_key else bool((old_e or {}).get('rows'))
            new_joined = _joined(new_key, ref) if new_key else bool((new_e or {}).get('rows'))
            reason = _why(old_e, new_e, ref in changed_refs, old_joined, new_joined)
            if (old_e or {}).get('class') == 'verified' and not new_joined:
                lost_n += 1
                lost_refs.append(f'{area} {ref}')
            elif (old_e or {}).get('class') == 'verified' and (new_e or {}).get('class') not in ('', 'verified') and new_joined:
                worse_n += 1
                worse_refs.append(f'{area} {ref} ({class_phrase(old_e, new_e)})')
            if not reason: continue
            name = (new_e or {}).get('n') or (old_e or {}).get('n') or ''
            if not name:
                for key in (new_key, old_key):
                    park = ((key or {}).get('parks') or {}).get(ref)
                    if isinstance(park, dict) and park.get('n'):
                        name = park['n']
                        break
            fact_rows.append({'area': area, 'ref': ref, 'name': name, 'class old': (old_e or {}).get('class') or '',
                              'class new': (new_e or {}).get('class') or '', 'flags old': _flag_text(_flags(old_e)),
                              'flags new': _flag_text(_flags(new_e)), 'pin_km old': _pin(old_e), 'pin_km new': _pin(new_e),
                              'why': reason})
        by_ref = {d['ref']: class_phrase(old_parks.get(d['ref']), new_parks.get(d['ref'])) for d in diffs}
        for diff in diffs:
            park_rows.extend(_park_lines(diff, area, by_ref.get(diff['ref']) or ''))
            changed_lines.append(f'{area} ' + _plain_change(diff))
        new_notes, old_notes = [], []
        if folder:
            new_notes, old_notes = _only(notice_lines(_read(folder / 'old.log'), state), notice_lines(_read(folder / 'new.log'), state))
        for line in new_notes: only_new.append(f'{area} {line}')
        for line in old_notes: only_old.append(f'{area} {line}')
        outlines = _arrow(_count(old_fact, 'with_outline') if old_fact else _outline_count(old_key),
                          _count(new_fact, 'with_outline') if new_fact else _outline_count(new_key))
        verified = _arrow(_count(old_fact, 'verified'), _count(new_fact, 'verified')) if old_fact or new_fact else 'not checked'
        hard = _arrow(_hard_count(old_fact) if old_fact else None, _hard_count(new_fact) if new_fact else None) if old_fact or new_fact else 'not checked'
        if not old_fact and not new_fact:
            lost_cell, worse_cell = 'not checked', 'not checked'
        else:
            lost_cell, worse_cell = str(lost_n), str(worse_n)
        table_rows.append([state, str(len(diffs)), outlines or '0 -> 0', verified, lost_cell, worse_cell, hard, str(len(new_notes))])
        per_state[state] = {'result': 'ok', 'parks_changed': len(diffs), 'notices_only_new': len(new_notes),
                            'verified_outlines_lost': lost_n, 'verified_got_worse': worse_n}
    gold_old_text = _read(gold_old)
    gold_new_text = _read(gold_new)
    if not gold_old_text and not gold_new_text:
        gold_sentence = 'Gold score: not run.'
    elif not gold_old_text or not gold_new_text:
        gold_sentence = 'Gold score: one side did not finish. Read the gold file that is here.'
    elif _gold_head(gold_old_text) == _gold_head(gold_new_text):
        gold_sentence = 'Gold score: the TUNE line and the SEALED line are the same on both sides.'
    else:
        gold_sentence = 'Gold score: the TUNE line or the SEALED line differs. Read gold-old.txt and gold-new.txt.'
    head = str(meta.get('head') or '')
    old_sha = str(meta.get('old') or '')
    pr = str(meta.get('pr') or '')
    title = f"Review packet for KPC-Links pull request {pr}" if pr else 'Review packet'
    intro = [f'# {title}', '']
    if head or old_sha:
        intro.append(f"New side: commit {head[:12] or '?'}. Old side: commit {old_sha[:12] or '?'} (the shared starting point, so later unrelated edits stay out).")
    entries = meta.get('entries') or []
    if entries: intro.append('New scope entries: ' + ', '.join(str(x) for x in entries) + '.')
    if meta.get('states_from') == 'input': intro.append('The states were typed in by hand.')
    elif states: intro.append('States: ' + ' '.join(states) + '.')
    intro.append('This report only compares. It does not change a park.')
    intro.append('')
    headers = ['state', 'parks changed', 'outlines old -> new', 'verified old -> new', 'verified outlines lost',
               'verified got worse', 'hard flags old -> new', 'notice lines only in NEW']
    body = [_table(headers, table_rows) if table_rows else 'No states were asked for.', '']
    if changed_lines:
        shown = changed_lines[:30]
        body.append(f'Parks whose joined records changed ({len(changed_lines)}):')
        body.extend('- ' + line for line in shown)
        if len(changed_lines) > 30: body.append(f'- and {len(changed_lines) - 30} more in parks-changed.csv')
        body.append('')
    else:
        body.append('No park had a joined-record change in a state that finished.')
        body.append('')
    body.append('Verified outlines lost: ' + (', '.join(lost_refs) if lost_refs else 'none'))
    body.append('Verified got worse: ' + (', '.join(worse_refs) if worse_refs else 'none'))
    body.append('')
    if only_new:
        body.append('Notice lines only in the new build:')
        body.extend('- ' + line for line in only_new[:20])
        if len(only_new) > 20: body.append(f'- and {len(only_new) - 20} more in notices-only-new.txt')
        body.append('')
    if only_old:
        body.append(f'Notice lines only in the old build: {len(only_old)} (see notices-only-old.txt).')
        body.append('')
    if gap_lines:
        body.append('States that did not finish:')
        body.extend('- ' + line for line in gap_lines)
        body.append('')
    body.append(gold_sentence)
    body.append('')
    body.append('Files here: parks-changed.csv, factcheck-diff.csv, notices-only-new.txt, notices-only-old.txt, gold-old.txt, gold-new.txt, inputs.json.')
    summary = '\n'.join(intro + body).rstrip() + '\n'

    def place(name, text=None, src=None):
        dest = (out / name).resolve()
        if out != dest and out not in dest.parents: raise SystemExit(f'refusing to write outside the packet folder: {name}')
        if src and pathlib.Path(src).is_file():
            shutil.copyfile(src, dest)
        else:
            dest.write_text('' if text is None else text, encoding='utf-8')

    place('summary.md', summary)
    with (out / 'parks-changed.csv').open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, PARK_COLS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(park_rows)
    with (out / 'factcheck-diff.csv').open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, FACT_COLS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(fact_rows)
    place('notices-only-new.txt', ('\n'.join(only_new) + '\n') if only_new else '')
    place('notices-only-old.txt', ('\n'.join(only_old) + '\n') if only_old else '')
    place('gold-old.txt', gold_old_text if gold_old_text else 'not run\n', gold_old if gold_old_text else None)
    place('gold-new.txt', gold_new_text if gold_new_text else 'not run\n', gold_new if gold_new_text else None)
    inputs = {
        'about': 'Frozen inputs for this review packet. Both sides used the same park data, the same saved shapes, and the same build date.',
        'pr': pr, 'head': head, 'old': old_sha, 'data_commit': meta.get('data_commit') or '',
        'build_date': meta.get('build_date') or '', 'states': states, 'states_from': meta.get('states_from') or '',
        'entries': entries, 'fixed_build_settings': FIXED_BUILD_ENV,
        'shapes': _shape_index(assets), 'gold_file': meta.get('gold_file') or '', 'gold_commit': meta.get('gold_commit') or '',
        'states_ran': per_state,
        'note': 'Shapely is for the fact check step. The two builds do not install it, so a build cannot change its answers by finding that library.',
    }
    place('inputs.json', json.dumps(inputs, indent=1, ensure_ascii=False) + '\n')
    return summary


def _cmd_scope(args):
    try:
        old_doc = json.loads(pathlib.Path(args.old).read_text(encoding='utf-8'))
        new_doc = json.loads(pathlib.Path(args.new).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        result = {'states': [], 'entries': [], 'message': 'the scope file could not be read', 'notes': [], 'states_from': ''}
    else:
        result = scope_from_docs(old_doc, new_doc, args.states or '')
    text = json.dumps(result)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(text + '\n', encoding='utf-8')
    print(text)
    if result.get('message'): print(result['message'], file=sys.stderr)
    for note in result.get('notes') or []: print(note, file=sys.stderr)
    return 0 if result.get('states') else 2


def _cmd_judge(args):
    keys = bool(args.old_key or args.new_key)
    result = judge_build(args.state.upper(), args.old_exit, args.new_exit, _read(args.old_log), _read(args.new_log),
                         _load(args.old_key) if args.old_key else None, _load(args.new_key) if args.new_key else None, keys)
    pathlib.Path(args.out).write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(result['result'])
    return 0 if result['result'] == 'ok' else 1


def _cmd_packet(args):
    states, _ky = parse_state_list(args.states or '')
    meta = _load(args.meta) if args.meta else {}
    if not isinstance(meta, dict): meta = {}
    assets = _load(args.assets) if args.assets else None
    if isinstance(assets, dict): assets = assets.get('assets') or assets.get('items') or []
    summary = write_packet(args.out, states, args.builds, args.fact_old, args.fact_new, args.gold_old, args.gold_new, meta, assets)
    print(summary)
    return 0


def selftest():
    """Tiny made-up parks. No network."""
    old_scope = {'changes': [{'id': 'older', 'scope': {'states': ['US-ZZ']}}]}
    new_scope = {'changes': [{'id': 'older', 'scope': {'states': ['US-ZZ']}},
                             {'id': 'sample-rule', 'scope': {'states': ['US-ZZ', 'US-KY', 'US-QQ']}}]}
    got = scope_from_docs(old_scope, new_scope, '')
    assert got['states'] == ['ZZ', 'QQ'] and got['entries'] == ['sample-rule'], got
    assert scope_from_docs(old_scope, old_scope, '')['message'] == NO_ENTRY
    assert scope_from_docs(old_scope, old_scope, 'QQ ZZ')['states'] == ['QQ', 'ZZ']
    assert scope_from_docs(old_scope, {'changes': [{'id': 'wide', 'scope': 'all'}]}, '')['states'] == []
    old_key = {'parks': {
        'US-9001': {'n': 'North Sample Park', 'm': [[1001, 'North Sample Preserve', 30, 'name'], [1002, 'North Sample Park', 70, 'name']], 'c': []},
        'US-9002': {'n': 'East Sample Park', 'm': [[1003, 'East Sample Park', 10, 'name']],
                    'c': [[1004, 'East Sample Preserve', 5, 'check (sample): a made-up reason']]},
    }}
    new_key = {'parks': {
        'US-9001': {'n': 'North Sample Park', 'm': [[1002, 'North Sample Park', 70, 'name']], 'c': []},
        'US-9002': {'n': 'East Sample Park', 'm': [[1003, 'East Sample Park', 10, 'name']],
                    'c': [[1004, 'East Sample Preserve', 5, 'check (other): the reason text changed']]},
    }}
    diffs = diff_parks(old_key, new_key)
    assert [d['ref'] for d in diffs] == ['US-9001'], diffs
    assert diffs[0]['old_acres'] == 100 and diffs[0]['new_acres'] == 70 and diffs[0]['lost'][0]['id'] == '1001'
    old_log = '::notice title=US key ZZ::kept 1 record\n::notice title=US key ZZ::sample rule: 1 record to check: US-9001 North Sample Preserve\n'
    new_log = '::notice title=US key ZZ::kept 1 record\nZZ: 2 parks, 1 joined, 1 to check, 0 nothing found, 0 places with no park, 3 s\n'
    only_new, only_old = _only(notice_lines(old_log, 'ZZ'), notice_lines(new_log, 'ZZ'))
    assert only_new == [] and only_old == ['sample rule: 1 record to check: US-9001 North Sample Preserve']
    judged = judge_build('ZZ', 0, 124, 'ZZ: 2 parks, 1 joined,\n', '', None, None, False)
    assert judged['result'] == 'timed out'
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        b = root / 'builds' / 'key-ZZ'
        b.mkdir(parents=True)
        (b / 'status.json').write_text(json.dumps({'state': 'ZZ', 'result': 'ok', 'old': {'ok': True, 'why': ''}, 'new': {'ok': True, 'why': ''}}))
        (b / 'US-ZZ-old.json').write_text(json.dumps(old_key))
        (b / 'US-ZZ-new.json').write_text(json.dumps(new_key))
        (b / 'old.log').write_text(old_log)
        (b / 'new.log').write_text(new_log + '::notice title=US key ZZ::sample rule: 1 record to check: US-9001 North Sample Preserve\n')
        # the new log above was replaced: give the new side its own extra line
        (b / 'new.log').write_text('::notice title=US key ZZ::kept 1 record\n::notice title=US key ZZ::sample rule: 2 records to check\nZZ: 2 parks, 1 joined, 1 to check, 0 nothing found, 0 places with no park, 3 s\n')
        fact = root / 'fact'
        fact.mkdir()
        old_f = {'area': 'US-ZZ', 'counts': {'parks': 2, 'with_outline': 2, 'verified': 2, 'PIN_FAR': 0},
                 'parks': {'US-9001': {'n': 'North Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 0, 'rows': 2},
                           'US-9002': {'n': 'East Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 0, 'rows': 1}}}
        new_f = {'area': 'US-ZZ', 'counts': {'parks': 2, 'with_outline': 2, 'verified': 1, 'PIN_FAR': 1},
                 'parks': {'US-9001': {'n': 'North Sample Park', 'class': 'flagged', 'flags': [['PIN_FAR', 'the pin is 4.0 km outside the nearest piece']], 'pin_km': 4.0, 'rows': 1},
                           'US-9002': {'n': 'East Sample Park', 'class': 'verified', 'flags': [], 'pin_km': 0, 'rows': 1}}}
        (fact / 'old').mkdir()
        (fact / 'new').mkdir()
        (fact / 'old' / 'factcheck-US-ZZ.json').write_text(json.dumps(old_f))
        (fact / 'new' / 'factcheck-US-ZZ.json').write_text(json.dumps(new_f))
        (root / 'gold-old.txt').write_text('TUNE: 1 gold parks in these keys | wrong land 0 of 1\nSEALED: 1 gold parks in these keys | wrong land 0 of 1\n')
        (root / 'gold-new.txt').write_text('TUNE: 1 gold parks in these keys | wrong land 0 of 1\nSEALED: 1 gold parks in these keys | wrong land 0 of 1\n    hidden detail\n')
        packet = root / 'packet'
        text = write_packet(packet, ['ZZ', 'YY'], b.parent, fact / 'old', fact / 'new', root / 'gold-old.txt', root / 'gold-new.txt',
                            {'pr': '1', 'head': 'abc1234def', 'old': 'fff0000111', 'entries': ['sample-rule'], 'states_from': 'scope'}, [])
        assert 'North Sample Park' in text and 'US-9001' in text
        assert 'verified got worse' in text.lower() or 'Verified got worse' in text
        assert 'US-9002' not in (packet / 'parks-changed.csv').read_text()
        assert 'the TUNE line and the SEALED line are the same' in text
        assert 'build failed or timed out' in text  # YY had no folder
        assert 'sample rule: 2 records to check' in (packet / 'notices-only-new.txt').read_text()
        for name in ('summary.md', 'parks-changed.csv', 'factcheck-diff.csv', 'notices-only-new.txt', 'notices-only-old.txt', 'gold-old.txt', 'gold-new.txt', 'inputs.json'):
            assert (packet / name).is_file(), name
        # a check-list-only change must not become a joined-record change
        assert 'US-9002' not in text.split('Parks whose joined records changed')[1].split('Verified outlines lost')[0]
    print('selftest: ok')
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (['--selftest'], ['selftest']): return selftest()
    ap = argparse.ArgumentParser(description='Compare two built keys and write a review packet.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sc = sub.add_parser('scope')
    sc.add_argument('--old', required=True)
    sc.add_argument('--new', required=True)
    sc.add_argument('--states', default='')
    sc.add_argument('--json-out')
    ju = sub.add_parser('judge')
    ju.add_argument('--state', required=True)
    ju.add_argument('--old-exit', required=True)
    ju.add_argument('--new-exit', required=True)
    ju.add_argument('--old-log', required=True)
    ju.add_argument('--new-log', required=True)
    ju.add_argument('--old-key')
    ju.add_argument('--new-key')
    ju.add_argument('--out', required=True)
    pk = sub.add_parser('packet')
    pk.add_argument('--out', required=True)
    pk.add_argument('--states', required=True)
    pk.add_argument('--builds')
    pk.add_argument('--fact-old')
    pk.add_argument('--fact-new')
    pk.add_argument('--gold-old')
    pk.add_argument('--gold-new')
    pk.add_argument('--meta')
    pk.add_argument('--assets')
    args = ap.parse_args(argv)
    if args.cmd == 'scope': return _cmd_scope(args)
    if args.cmd == 'judge': return _cmd_judge(args)
    return _cmd_packet(args)


if __name__ == '__main__':
    sys.exit(main())
