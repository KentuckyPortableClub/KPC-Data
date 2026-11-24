"""One KPC-Data file for settled joins and saved solver answers (IDs first).

Fingerprint: the layer's stable agency ID when it has one (LinkID, URL id,
UniqueID, or an explicit agency_id); otherwise a normalized name + acres
within 10% + map box rounded to 0.001°. The record number is a hint only.

Statuses: settled, person-yes, person-no, solver-suggested.

Reuse an answer only when the fingerprint still matches and the named
record is in the saved copy. If the named record is missing, list it
(S4); do not redo it and do not silently drop it. This module never
auto-applies a join or an override.

24 Nov 2026: design only (owner approved D). The key, the solver, and
the clean-up stage are meant to share this file later.
"""
from __future__ import annotations

import json
import pathlib

STATUSES = ('settled', 'person-yes', 'person-no', 'solver-suggested')
AGENCY_ID_FIELDS = ('agency_id', 'LinkID', 'link_id', 'UniqueID', 'unique_id', 'url_id', 'URL_ID')


def norm_name(name):
    """Lower-case, squeezed spaces. Empty names do not fingerprint."""
    return ' '.join((name or '').casefold().split())


def box_fingerprint(box):
    """Map box [minx, miny, maxx, maxy] rounded to 0.001°."""
    if not box or len(box) != 4:
        return None
    try:
        return [round(float(x), 3) for x in box]
    except (TypeError, ValueError):
        return None


def stable_agency_id(rec):
    """The layer's stable agency ID when the record carries one, else ''."""
    rec = rec or {}
    for k in AGENCY_ID_FIELDS:
        v = rec.get(k)
        if v is None or v == '':
            continue
        s = str(v).strip()
        if s:
            return s
    return ''


def fingerprint_of(rec):
    """A fingerprint dict, or None when the record has no usable land or ID."""
    rec = rec or {}
    aid = stable_agency_id(rec)
    if aid:
        return {'kind': 'agency-id', 'id': aid}
    name = norm_name(rec.get('name') or rec.get('Unit_Nm') or '')
    acres = rec.get('acres')
    if acres is None:
        acres = rec.get('GIS_Acres')
    box = box_fingerprint(rec.get('box') or rec.get('_bb'))
    try:
        acres = float(acres)
    except (TypeError, ValueError):
        acres = None
    if not name or acres is None or acres < 0 or box is None:
        return None
    return {'kind': 'name-acres-box', 'name': name, 'acres': acres, 'box': box}


def acres_within_10pct(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if a < 0 or b < 0:
        return False
    if a == 0 and b == 0:
        return True
    hi = max(a, b)
    lo = min(a, b)
    return hi <= lo * 1.10 + 1e-9


def fingerprints_match(left, right):
    """True when two fingerprints describe the same land under the agreed rule."""
    if not left or not right:
        return False
    if left.get('kind') != right.get('kind'):
        return False
    if left['kind'] == 'agency-id':
        return bool(left.get('id')) and left.get('id') == right.get('id')
    if left['kind'] == 'name-acres-box':
        if (left.get('name') or '') != (right.get('name') or ''):
            return False
        if not acres_within_10pct(left.get('acres'), right.get('acres')):
            return False
        return box_fingerprint(left.get('box')) == box_fingerprint(right.get('box'))
    return False


def decide_reuse(answer, saved_by_id, current_rec=None):
    """How to treat a saved answer against the saved copy (and optional current land).

    Returns a dict: action is reuse, missing-saved-record, or redo; never auto-applies.

    - Named record present and fingerprint still matches (current if given,
      else the saved record): reuse.
    - Named record present and the land changed: redo.
    - Named record missing from the saved copy: missing-saved-record (S4).
      The answer is listed, not redone, not dropped. If another saved record
      matches the saved fingerprint, its number is returned as maybe_new_record
      (a hint for a person; not an auto-reuse).
    """
    answer = answer or {}
    saved_by_id = saved_by_id or {}
    named = str(answer.get('record') or '').strip()
    saved_fp = answer.get('fingerprint')
    status = answer.get('status')
    out = {
        'park': answer.get('park'),
        'status': status,
        'record': named,
        'action': None,
        'maybe_new_record': None,
    }
    if status not in STATUSES:
        out['action'] = 'redo'
        out['why'] = 'unknown status'
        return out
    if named and named in saved_by_id:
        live = fingerprint_of(saved_by_id[named])
        cur = fingerprint_of(current_rec) if current_rec is not None else live
        if fingerprints_match(saved_fp, live) and fingerprints_match(saved_fp, cur):
            out['action'] = 'reuse'
            out['why'] = 'fingerprint still matches and the named record is in the saved copy'
            return out
        out['action'] = 'redo'
        out['why'] = 'named record is in the saved copy but the fingerprint no longer matches'
        return out
    # S4: named record missing (or never given)
    out['action'] = 'missing-saved-record'
    out['why'] = 'named record is not in the saved copy; listed, not redone, not dropped'
    if saved_fp:
        for rid, rec in saved_by_id.items():
            if fingerprints_match(saved_fp, fingerprint_of(rec)):
                out['maybe_new_record'] = str(rid)
                break
    return out


def load_answers(path):
    """Load the file. Rows with a park name field other than the park id are left as they are;
    writers should not put a display name on a row."""
    data = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    rows = data.get('answers') if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError('settled-answers file needs an answers list')
    for row in rows:
        if row.get('status') not in STATUSES:
            raise ValueError(f"unknown status: {row.get('status')!r}")
        if not row.get('park'):
            raise ValueError('each answer needs a park id')
        if 'name' in row:
            raise ValueError('answers are IDs first: do not store a park display name on the row')
    return data if isinstance(data, dict) else {'answers': rows}


def list_missing_saved_records(answers, saved_by_id):
    """S4 list: answers whose named record is not in the saved copy."""
    missing = []
    for a in answers:
        d = decide_reuse(a, saved_by_id)
        if d['action'] == 'missing-saved-record':
            missing.append(d)
    return missing
