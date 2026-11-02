#!/usr/bin/env python3
"""Inputs for the outside helper tools (chat 10, Oct 31 2026; Brandon 8:31 PM 'wire them').
  links-list OUT        dead official links in data/docs (map / page answered HTTP 404 / 410) -> T2 dead-link fixer input
  linkfix-docs IN OUT   T2's link_fix.json -> a docs-found file (only new links that open AND name the park) for the docs merge
  site-sample KEYS FERS OUT   T5 sample: 10 official / 10 approximate / 10 pin / 10 with a 2-fer (US keys, a new random set each week)
Never fails."""
import datetime as dt, glob, json, os, random, re, sys


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def links_list(out):
    rows = []
    for f in sorted(glob.glob('data/docs/*.json')):
        if not re.search(r'/(US|CA)-[A-Z]{2}\.json$', f): continue
        for ref, v in ((load(f, {}) or {}).get('parks') or {}).items():
            m = v.get('map') or {}
            if re.match(r'HTTP 4(04|10)', str(m.get('status'))) and m.get('url'):
                rows.append({'ref': ref, 'url': m['url'], 'kind': 'map', 'name': v.get('n') or '', 'page': v.get('page') or ''})
    json.dump(rows, open(out, 'w'), indent=1)
    print(f'dead official links: {len(rows)}')


def linkfix_docs(src, out):
    L = load(src, {}) or {}; D = {}
    for old, r in L.items():
        if r.get('new_url') and r.get('opens') and r.get('names_park') is True and r.get('ref'):
            D[r['ref']] = {'st': '', 'page': '', 'map': r['new_url'] if r.get('kind') == 'map' else '', 'map_page': 1, 'kind': '', 'date': None, 'agency': '',
                           'notes': f"dead-link fixer (T2) {dt.date.today()}: replaces {old} ({r.get('how')}, confidence {r.get('confidence')})"[:300]}
            if r.get('kind') == 'page': D[r['ref']]['page'] = r['new_url']
    for f in glob.glob('data/parkinfo/US-*.json'):   # the merge places a row by its state
        st = os.path.basename(f)[3:5]
        for ref in (load(f, {}) or {}).get('parks') or {}:
            if ref in D: D[ref]['st'] = st
    json.dump(D, open(out, 'w'), indent=1, ensure_ascii=False)
    print(f'fixed links for the docs merge: {len(D)}')


def site_sample(keys, fers, out):
    random.seed(dt.date.today().isocalendar()[1])   # a different set each week
    by = {'official': [], 'approximate': [], 'pin': []}
    for f in glob.glob(os.path.join(keys, 'US-*.json')):
        for ref, v in ((load(f, {}) or {}).get('parks') or {}).items():
            g = (v or {}).get('g') if isinstance(v, dict) else None
            if g in by and not (v.get('joined_in')): by[g].append(ref)
    S = [{'ref': r, 'expect': g, 'fers': []} for g, L in by.items() for r in random.sample(sorted(L), min(10, len(L)))]
    pairs = []
    for f in glob.glob(os.path.join(fers, 'US-*.json*')):
        try:
            import gzip
            d = json.load(gzip.open(f) if f.endswith('.gz') else open(f))
        except Exception: continue  # noqa: BLE001
        for r in (d.get('spots') or []) if isinstance(d, dict) else []:
            refs = r.get('refs') or []
            if len(refs) >= 2 and str(r.get('status', '')) == 'candidate' and not str(r.get('tier', '')).startswith('very tight'): pairs.append((refs[0], refs[1]))
    for a, b in random.sample(pairs, min(10, len(pairs))): S.append({'ref': a, 'expect': None, 'fers': [b]})
    json.dump(S, open(out, 'w'), indent=1)
    print(f'site sample: {len(S)} parks')


if __name__ == '__main__':
    a = sys.argv[1:]
    try: {'links-list': lambda: links_list(a[1]), 'linkfix-docs': lambda: linkfix_docs(a[1], a[2]), 'site-sample': lambda: site_sample(a[1], a[2], a[3])}[a[0]]()
    except Exception as e: print(f'helpers prep: {type(e).__name__}: {e}')  # noqa: BLE001
    sys.exit(0)
