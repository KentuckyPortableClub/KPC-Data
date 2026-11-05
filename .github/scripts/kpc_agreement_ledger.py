#!/usr/bin/env python3
"""Agreement ledger (Nov 6 2026; Brandon rulings 4:07 PM and 4:17 PM CST Nov 5, relayed via Super).

A generic row holds two agreements from DIFFERENT agents:
  park, kind (pile-exit | location-fix | join), proposed_by, proposal, source,
  confirmed_by, confirmed_at, decided_by = 'Brandon rule 2026-11-05 two-agreements'

Kinds:
  pile-exit       park leaves the review pile (outside-agent correction + checker/Quality)
  location-fix   corrected location for a 0,0 / impossible POTA pin (never edits POTA's pin;
                  stores agreed_lat / agreed_lon as a separate labelled field; original 0,0 kept)
  join            join proposal (reserved; not auto-applied)

The same agent cannot both propose and confirm (enforced). auto=false in state.json: Brandon
turns it on only after he checks a full run. No bot flips auto.
"""
import csv, datetime, json, os, pathlib, sys

DECIDED_BY = 'Brandon rule 2026-11-05 two-agreements'
KINDS = ('pile-exit', 'location-fix', 'join')
LEDGER = pathlib.Path('data/agreement-ledger/ledger.csv')
STATE = pathlib.Path('data/agreement-ledger/state.json')
FIELDS = ['park', 'kind', 'proposed_by', 'proposal', 'source', 'confirmed_by', 'confirmed_at', 'decided_by',
          'agreed_lat', 'agreed_lon', 'pota_lat', 'pota_lon', 'notes']


def load_rows(path=LEDGER):
    if not pathlib.Path(path).exists(): return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_rows(rows, path=LEDGER):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        for r in rows: w.writerow({k: r.get(k, '') for k in FIELDS})


def load_state(path=STATE):
    try: s = json.load(open(path, encoding='utf-8'))
    except Exception: s = {}  # noqa: BLE001
    s.setdefault('auto', False)
    s.setdefault('auto_note', "Brandon turns auto on by hand after he checks a full run. No bot flips it. (Brandon 4:07 PM CST Nov 5, relayed)")
    s.setdefault('decided_by', DECIDED_BY)
    return s


def save_state(s, path=STATE):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    json.dump(s, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def propose(park, kind, proposed_by, proposal, source='', pota_lat='', pota_lon='', notes='', rows=None):
    """Add a proposal row. confirmed_by stays empty until a different agent confirms."""
    if kind not in KINDS: raise ValueError(f'kind must be one of {KINDS}')
    if not park or not proposed_by or not proposal: raise ValueError('park, proposed_by, proposal required')
    rows = list(rows if rows is not None else load_rows())
    rows.append({'park': park, 'kind': kind, 'proposed_by': proposed_by, 'proposal': proposal, 'source': source,
                 'confirmed_by': '', 'confirmed_at': '', 'decided_by': '',
                 'agreed_lat': '', 'agreed_lon': '', 'pota_lat': pota_lat, 'pota_lon': pota_lon, 'notes': notes})
    return rows


def confirm(park, kind, confirmed_by, proposal_match=None, agreed_lat='', agreed_lon='', rows=None, now=None):
    """Confirm an open proposal. Same agent cannot propose and confirm."""
    rows = list(rows if rows is not None else load_rows())
    now = now or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    hit = None
    for r in rows:
        if r.get('park') == park and r.get('kind') == kind and not r.get('confirmed_by'):
            if proposal_match and r.get('proposal') != proposal_match: continue
            hit = r; break
    if hit is None: raise ValueError(f'no open {kind} proposal for {park}')
    if (hit.get('proposed_by') or '').strip().casefold() == (confirmed_by or '').strip().casefold():
        raise ValueError(f'same agent cannot propose and confirm ({confirmed_by})')
    hit['confirmed_by'] = confirmed_by
    hit['confirmed_at'] = now
    hit['decided_by'] = DECIDED_BY
    if kind == 'location-fix':
        if agreed_lat == '' or agreed_lon == '': raise ValueError('location-fix confirm needs agreed_lat and agreed_lon')
        hit['agreed_lat'] = str(agreed_lat); hit['agreed_lon'] = str(agreed_lon)
        # Never edit POTA source pins: agreed_* is a separate labelled field; pota_* stays as recorded at propose time.
    return rows


def ready(kind=None, rows=None):
    """Rows with both agreements (proposed_by and confirmed_by set, different agents)."""
    rows = rows if rows is not None else load_rows()
    out = []
    for r in rows:
        if kind and r.get('kind') != kind: continue
        if r.get('proposed_by') and r.get('confirmed_by') and r.get('decided_by') == DECIDED_BY:
            if r['proposed_by'].strip().casefold() != r['confirmed_by'].strip().casefold():
                out.append(r)
    return out


def exit_candidates(rows=None, auto=None):
    """Parks that would leave the pile under the two-agreements rule right now. Honours state.auto (default false)."""
    st = load_state(); a = st['auto'] if auto is None else auto
    ready_exit = ready('pile-exit', rows)
    return {'auto': a, 'would_exit': ready_exit if a else [], 'ready_but_auto_false': ready_exit if not a else [],
            'count_ready': len(ready_exit), 'decided_by': DECIDED_BY}


def location_fixes(rows=None):
    """Agreed corrected locations (never written back to POTA)."""
    return [{**r, 'note': 'agreed_lat/lon is a separate labelled field; POTA source pin unchanged'}
            for r in ready('location-fix', rows)]


def report_00(rows=None):
    """How many 0,0 parks currently have a proposal, a confirmation, or both."""
    rows = rows if rows is not None else load_rows()
    loc = [r for r in rows if r.get('kind') == 'location-fix']
    prop = [r for r in loc if r.get('proposed_by') and not r.get('confirmed_by')]
    both = [r for r in loc if r.get('proposed_by') and r.get('confirmed_by')]
    conf_only = [r for r in loc if r.get('confirmed_by') and not r.get('proposed_by')]  # shouldn't happen
    return {'proposals_only': len(prop), 'confirmations_both': len(both), 'confirm_without_proposal': len(conf_only),
            'total_location_fix_rows': len(loc),
            'parks_proposal_only': [r['park'] for r in prop],
            'parks_both': [r['park'] for r in both]}


def main(argv=None):
    argv = list(argv or sys.argv[1:])
    cmd = argv[0] if argv else 'report'
    if cmd == 'init':
        save_rows([]); save_state(load_state()); print('initialized', LEDGER, STATE); return 0
    if cmd == 'report':
        rows = load_rows(); st = load_state(); ex = exit_candidates(rows); loc = report_00(rows)
        print(json.dumps({'state': st, 'pile_exit': ex, 'location_fix_00': loc,
                          'ready_join': len(ready('join', rows))}, indent=1)); return 0
    if cmd == 'propose':
        # propose <park> <kind> <by> <proposal> [source]
        rows = propose(argv[1], argv[2], argv[3], argv[4], source=argv[5] if len(argv) > 5 else '')
        save_rows(rows); print('proposed', argv[1], argv[2]); return 0
    if cmd == 'confirm':
        rows = confirm(argv[1], argv[2], argv[3], agreed_lat=argv[4] if len(argv) > 4 else '',
                       agreed_lon=argv[5] if len(argv) > 5 else '')
        save_rows(rows); print('confirmed', argv[1], argv[2]); return 0
    print('usage: init|report|propose|confirm', file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
