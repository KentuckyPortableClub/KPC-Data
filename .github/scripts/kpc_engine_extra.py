#!/usr/bin/env python3
"""ENGINE EXTRA SOURCES (chat 10, Nov 1 2026; Brandon 1:20 PM 'are they not tied into the engine?').
Ties the club's finders into the park-info engine: writes <engine>/registry/club_extra.json = {'sources': [...]} from
  (1) the engine's own crawler finds (registry/us_ca_discovered.json + us_ca_trails_discovered.json, key 'found'), which the
      engine never loaded (its registry list left them out), and
  (2) every layer in data/intake/queue.json and its split files queue-*.json, never a *hold* file (GIS hunter, world harvester, discovery bot, outside research, chats 8 + 9).
The engine still decides nothing: these are places to LOOK; what it finds goes through the waiting room to chat 11.
Rows chat 11 said NO to stay out (the engine's own no_rows / deny lists still apply on top).
  python3 .github/scripts/kpc_engine_extra.py <engine dir> [queue.json]"""
import json, pathlib, re, sys

E = pathlib.Path(sys.argv[1]); R = E / 'registry'
Q = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'data/intake/queue.json')


def load(p, d):
    try: return json.load(open(p))
    except (OSError, ValueError): return d


def key(u): return re.sub(r'^https?://', '', re.sub(r'/query/?$', '', (u or '').split('?')[0].strip().rstrip('/'), flags=re.I), flags=re.I).lower()   # same as the engine's norm_url: one layer = one row


out, seen = [], set()
for f in ('us_ca_discovered.json', 'us_ca_trails_discovered.json'):
    for s in load(R / f, {}).get('found') or []:
        if s.get('url') and key(s['url']) not in seen:
            g = s.get('geometry'); pt = s.get('ptype')   # same 'use' rule as registry/_seed_usca.py (a trail line is never an outline)
            use = s.get('use') or {'polygon': 'outline', 'line': 'trail'}.get(g) or (pt if pt in ('parking', 'camping') else 'parking')
            seen.add(key(s['url'])); out.append(dict(s, use=use, from_list=f))
n_disc = len(out)
AREA = {}                                            # park ref -> its areas (US / CA park files; world refs = their country prefix)
for f in pathlib.Path('data/parkinfo').glob('US-*.json'):
    for ref in (load(f, {}).get('parks') or {}): AREA.setdefault(ref, []).append(f.stem)
for ref, v in (load('data/parkinfo/CA.json', {}).get('parks') or {}).items():
    if isinstance(v, list) and len(v) > 10 and v[10]: AREA.setdefault(ref, []).append('CA-' + v[10])
import kpc_queue_files as QF   # Nov 12: queue.json is at the 1 MB cap, so rows also live in data/intake/queue-*.json (a *hold* file is never read)
QROWS = QF.rows(Q.parent) if Q.name == 'queue.json' else (load(Q, {}).get('rows') or [])   # queue.json first, so the Q-<n> ids of its rows do not move
for i, r in enumerate(QROWS):
    u = r.get('url') or ''
    if not u.startswith('http') or key(u) in seen: continue
    if str(r.get('status') or r.get('verdict') or '').upper().startswith(('NO', 'REJECT', 'DEAD')): continue
    areas = [r.get('area') or r.get('cc')] if (r.get('area') or r.get('cc')) else []
    for ref in r.get('closes') or []:                # a lead for named parks: the areas of those parks
        areas += AREA.get(ref) or ([] if ref[:2] in ('US', 'CA') else [ref.split('-')[0]])
    areas = list(dict.fromkeys(a for a in areas if a))
    if not areas: continue
    area = areas[0]
    rest = '/rest/services/' in u.lower()
    seen.add(key(u))
    out.append({'id': f'Q-{i}', 'area': area, 'cc': area.split('-')[0], 'region': area.split('-')[1] if '-' in area else '',
                'use': 'outline', 'kind': 'arcgis' if rest else 'other', 'url': u, 'layer_name': r.get('title') or '',
                'agency': r.get('publisher') or '', 'geometry': 'polygon',
                'official_basis': f"club layer queue (from {r.get('from') or '?'}, added {r.get('added') or '?'}); not graded yet",
                'areas': areas, 'closes': r.get('closes') or [], 'from_list': 'intake-queue'})
json.dump({'about': __doc__.split('\n')[0], 'sources': out}, open(R / 'club_extra.json', 'w'), ensure_ascii=False)
print(f'::notice title=Engine extra sources::{n_disc} from its own crawler + {len(out) - n_disc} from the club layer queue')
