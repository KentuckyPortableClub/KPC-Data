"""One KPC-Data file for settled joins and saved solver answers (IDs first).

Fingerprint: the layer's stable agency ID when it has one (LinkID, URL id,
UniqueID, or an explicit agency_id), always with that layer; otherwise a
short hash of the normalised name (letters and digits, same as
kpc_store_attrs.name_key) + acres within 10% + map box. Boxes match when
they overlap, or when each side is within 0.002°. The record number is a
hint only. The file stores the name hash, never the display name.

Statuses: settled, person-yes, person-no, solver-suggested.

Reuse an answer only when the fingerprint still matches and the named
record is in the saved copy. If the named record is missing, list it
(S4); do not redo it and do not silently drop it. A person-no answer
is never redone (listed for a person; the block list still applies).
This module never auto-applies a join or an override.

24 Nov 2026: design only (owner approved D; review fix 24 Nov). The key,
the solver, and the clean-up stage are meant to share this file later.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

STATUSES = ('settled', 'person-yes', 'person-no', 'solver-suggested')
AGENCY_ID_FIELDS = ('agency_id', 'LinkID', 'link_id', 'UniqueID', 'unique_id', 'url_id', 'URL_ID')
LAYER_FIELDS = ('layer', 'Layer', 'src_layer', 'layer_id')
BOX_SIDE_DEG = 0.002
NAME_HASH_LEN = 12


def name_key(name):
    """Letters and digits only, lower-case (same rule as kpc_store_attrs.name_key)."""
    return re.sub(r'[^a-z0-9]', '', str(name or '').lower())


def name_hash(name):
    """Short sha256 of the name_key. Empty input yields ''."""
    nk = name_key(name)
    if not nk:
        return ''
    return hashlib.sha256(nk.encode('utf-8')).hexdigest()[:NAME_HASH_LEN]


def box_as_floats(box):
    if not box or len(box) != 4:
        return None
    try:
        return [float(x) for x in box]
    except (TypeError, ValueError):
        return None


def boxes_match(left, right, side_deg=BOX_SIDE_DEG):
    """True when the boxes overlap, or each side is within side_deg (default 0.002°)."""
    a, b = box_as_floats(left), box_as_floats(right)
    if not a or not b:
        return False
    # overlap: not separated on x or y
    if not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1]):
        return True
    return all(abs(a[i] - b[i]) <= side_deg + 1e-12 for i in range(4))


def layer_of(rec):
    """The layer id the agency ID belongs to (for example sgmia)."""
    rec = rec or {}
    for k in LAYER_FIELDS:
        v = rec.get(k)
        if v is None or v == '':
            continue
        s = str(v).strip()
        if s:
            return s
    return ''


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
    """A fingerprint dict, or None when the record has no usable land or ID.

    An agency-id fingerprint always includes its layer. A name fingerprint
    stores name_hash, never the display name.
    """
    rec = rec or {}
    aid = stable_agency_id(rec)
    layer = layer_of(rec)
    if aid and layer:
        return {'kind': 'agency-id', 'layer': layer, 'id': aid}
    nm = rec.get('name') or rec.get('Unit_Nm') or ''
    h = name_hash(nm)
    acres = rec.get('acres')
    if acres is None:
        acres = rec.get('GIS_Acres')
    box = box_as_floats(rec.get('box') or rec.get('_bb'))
    try:
        acres = float(acres)
    except (TypeError, ValueError):
        acres = None
    if not h or acres is None or acres < 0 or box is None:
        return None
    return {'kind': 'name-acres-box', 'name_hash': h, 'acres': acres, 'box': box}


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
        return (bool(left.get('id')) and left.get('id') == right.get('id')
                and bool(left.get('layer')) and left.get('layer') == right.get('layer'))
    if left['kind'] == 'name-acres-box':
        lh, rh = left.get('name_hash') or '', right.get('name_hash') or ''
        if not lh or lh != rh:
            return False
        if not acres_within_10pct(left.get('acres'), right.get('acres')):
            return False
        return boxes_match(left.get('box'), right.get('box'))
    return False


def _matching_saved_ids(saved_fp, saved_by_id):
    """Every saved record whose fingerprint matches. Never pick only the first of many."""
    out = []
    if not saved_fp:
        return out
    for rid, rec in saved_by_id.items():
        if fingerprints_match(saved_fp, fingerprint_of(rec)):
            out.append(str(rid))
    return out


def _hints(ids):
    """One match: return it. Several pieces sharing one ID: return all of them, and
    do not set a single maybe_new_record."""
    if not ids:
        return None, []
    if len(ids) == 1:
        return ids[0], ids
    return None, ids


def decide_reuse(answer, saved_by_id, current_rec=None):
    """How to treat a saved answer against the saved copy (and optional current land).

    Returns a dict: action is reuse, missing-saved-record, list-for-person, or redo.
    Never auto-applies. A person-no answer is never redone.
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
        'maybe_new_records': [],
    }
    if status not in STATUSES:
        out['action'] = 'redo'
        out['why'] = 'unknown status'
        return out

    def stop_person_no(why):
        ids = _matching_saved_ids(saved_fp, saved_by_id)
        one, all_ids = _hints(ids)
        out['action'] = 'list-for-person'
        out['why'] = why
        out['maybe_new_record'] = one
        out['maybe_new_records'] = all_ids
        return out

    if named and named in saved_by_id:
        live = fingerprint_of(saved_by_id[named])
        cur = fingerprint_of(current_rec) if current_rec is not None else live
        if fingerprints_match(saved_fp, live) and fingerprints_match(saved_fp, cur):
            out['action'] = 'reuse'
            out['why'] = 'fingerprint still matches and the named record is in the saved copy'
            return out
        if status == 'person-no':
            return stop_person_no('person-no is never redone; listed for a person (the block list still applies)')
        out['action'] = 'redo'
        out['why'] = 'named record is in the saved copy but the fingerprint no longer matches'
        return out
    # S4: named record missing (or never given)
    if status == 'person-no':
        return stop_person_no('person-no is never redone; named record is not in the saved copy; listed for a person')
    out['action'] = 'missing-saved-record'
    out['why'] = 'named record is not in the saved copy; listed, not redone, not dropped'
    one, all_ids = _hints(_matching_saved_ids(saved_fp, saved_by_id))
    out['maybe_new_record'] = one
    out['maybe_new_records'] = all_ids
    return out


def load_answers(path):
    """Load the file. A display name must not appear on the row or in a fingerprint."""
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
        fp = row.get('fingerprint') or {}
        if isinstance(fp, dict) and 'name' in fp:
            raise ValueError('answers are IDs first: store a name_hash, not a display name, in the fingerprint')
    return data if isinstance(data, dict) else {'answers': rows}


def list_missing_saved_records(answers, saved_by_id):
    """S4 list: answers whose named record is not in the saved copy (and person-no listed)."""
    missing = []
    for a in answers:
        d = decide_reuse(a, saved_by_id)
        if d['action'] in ('missing-saved-record', 'list-for-person'):
            missing.append(d)
    return missing
