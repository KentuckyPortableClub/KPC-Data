#!/usr/bin/env python3
"""THE WEEK'S NUMBERS, READY FOR THE REVIEW (chat 10, Oct 30 2026; Brandon 11:01 AM 'All 3'). Runs nightly (waiting-room job).
One daily snapshot in data/status/week-numbers.json (90 days kept) + one short page data/status/week-review.md comparing today with
the first snapshot of the week (Fable's Nov 6 review starts from it):
  outlines   official / approximate / pin per key (US, Canada, world) = parks covered
  questions  per questions file + tier: rows asked, answered YES / NO / NOT SURE, open, bot YES (AUTO-1 / 1W)
  layers     intake verdicts (READY / approved / REJECT ...), layer collector + GIS finders counts
  coverage   world finder countries done / started; GIS hunter areas + pass
Also feeds the control panel page (data/status/panel.json). Notes only. Never fails.
  LINKS=../links python3 kpc_week_numbers.py"""
import collections, datetime as dt, glob, json, os, pathlib, sys

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
S = pathlib.Path('data/status')
TODAY = dt.date.today()


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def keys():
    out = {}
    for name, pat in (('US', 'data/us-key/US-*.json'), ('Canada', 'data/ca-key/CA-*.json'), ('World', 'data/world-key/[A-Z][A-Z].json')):
        c = collections.Counter()
        for f in glob.glob(str(LINKS / pat)):
            for v in ((load(f, {}) or {}).get('parks') or {}).values():
                if not isinstance(v, dict): continue
                g = v.get('g') or ('official' if v.get('m') else 'pin')
                c[g] += 1
        out[name] = dict(c)
    return out


def questions():
    out = {}
    for f in sorted(glob.glob('data/waiting/questions/*.json')):
        d = load(f, {}) or {}
        rows = d.get('questions') if isinstance(d, dict) else d
        rows = rows if isinstance(rows, list) else []
        c = collections.Counter()
        for q in rows:
            if not isinstance(q, dict): continue
            t = q.get('tier') or '-'
            a = str(q.get('answer') or '').upper()
            k = 'bot YES' if q.get('auto') else 'YES' if a.startswith('YES') else 'NO' if a.startswith('NO') else 'NOT SURE' if a.startswith('NOT') else 'parked' if q.get('parked') else 'open' if not a else 'other'
            c[f'{t} {k}'] += 1; c['rows'] += 1
        out[pathlib.Path(f).stem] = dict(c)
    return out


def layers():
    r = (load('data/intake/ready.json', {}) or {}).get('rows') or []
    v = collections.Counter(x.get('verdict') for x in r)
    v['approved'] = sum(1 for x in r if x.get('approved') is True)
    col = collections.Counter(x.get('status') for x in (load('data/intake/collector.json', {}) or {}).values())
    return {'intake': dict(v), 'queue rows': len((load('data/intake/queue.json', {}) or {}).get('rows') or []),
            'collector': dict(col), 'finders found': len(load('data/intake/found-layers.json', {}) or {})}


def coverage():
    w = load('data/world-finder/state.json', {}) or {}
    h = load('data/gis-hunter/state.json', {}) or {}
    return {'world countries done': sum(1 for x in w.values() if (x or {}).get('stage1') == 'done'), 'world countries started': len(w),
            'world candidates': sum((x or {}).get('candidates', 0) for x in w.values()),
            'hunter areas': len(h), 'hunter last pass': collections.Counter((x or {}).get('pass') or (x or {}).get('run') for x in h.values()).most_common(1)[0][0] if h else None}


def board():
    b = load(S / 'board.json', {}) or {}
    rows = b.get('bots') if isinstance(b, dict) and isinstance(b.get('bots'), (list, dict)) else b
    return rows


def main():
    snap = {'date': TODAY.isoformat(), 'outlines': keys(), 'questions': questions(), 'layers': layers(), 'coverage': coverage()}
    H = load(S / 'week-numbers.json', {'about': 'Daily snapshots for the weekly review (chat 10); 90 days', 'days': []}) or {'days': []}
    H['days'] = ([d for d in H.get('days') or [] if d.get('date') != snap['date']] + [snap])[-90:]
    S.mkdir(parents=True, exist_ok=True)
    json.dump(H, open(S / 'week-numbers.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    week = [d for d in H['days'] if d['date'] >= (TODAY - dt.timedelta(days=7)).isoformat()]
    first = week[0] if week else snap
    L = [f'# The week in numbers ({first["date"]} -> {snap["date"]})', '', 'For the weekly review (Fable, Nov 6). Made nightly by kpc_week_numbers.py; snapshots in week-numbers.json.', '',
         '## Parks with an outline (official / approximate / pin only)', '', '| key | official | approximate | pin | official change this week |', '|---|---|---|---|---|']
    for k, v in snap['outlines'].items():
        o0 = (first['outlines'].get(k) or {}).get('official', 0)
        L.append(f"| {k} | {v.get('official', 0):,} | {v.get('approximate', 0):,} | {v.get('pin', 0):,} | {v.get('official', 0) - o0:+,} |")
    L += ['', '## Questions (per file: tier + answer)', '']
    for k, v in snap['questions'].items():
        L.append(f"- **{k}** ({v.get('rows', 0)} rows): " + ', '.join(f'{kk} {vv}' for kk, vv in sorted(v.items()) if kk != 'rows'))
    lay = snap['layers']
    L += ['', '## Layers', '', f"- intake: {', '.join(f'{k} {v}' for k, v in sorted(lay['intake'].items(), key=lambda kv: str(kv[0])))}; queue {lay['queue rows']}",
          f"- layer collector: {', '.join(f'{k} {v}' for k, v in lay['collector'].items()) or 'nothing yet'}; GIS finders found {lay['finders found']} layers",
          '', '## Coverage', ''] + [f'- {k}: {v}' for k, v in snap['coverage'].items()]
    (S / 'week-review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    panel = {'made': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), 'snap': snap, 'first': first, 'board': board(),
             'storage': ((load(S / 'storage.json', {}) or {}).get('weeks') or [None])[-1]}
    json.dump(panel, open(S / 'panel.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Week numbers::snapshot {snap['date']}: US official {snap['outlines'].get('US', {}).get('official', 0):,}; world countries done {snap['coverage']['world countries done']}")


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Week numbers::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
