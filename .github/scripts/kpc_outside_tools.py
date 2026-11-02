#!/usr/bin/env python3
"""Oct 31 2026 (HQ, Brandon 'yes'): glue for the outside coder's three tools while Fable's review waits (Nov 6).
The tools stay in .github/scripts/draft/tools/ untouched; this file only feeds them the club's files and turns their
answers into REVIEW files. Nothing here edits data/fers, data/docs, a key or a card.

  prep-convert TEST OUT   data/intake/leads-oct31.json 'other_layer' ([ref, status, url]) -> OUT (list of dicts),
                          US + Canada first, then the rest by count; picture-map-only / not-found rows left out
  prep-links TEST DIR     data/intake/us-agency-maps-index.csv + data/parkinfo/US-XX.json -> DIR/agency_pages.json +
                          DIR/parks.json (each agency gets the parks of its state that have NO own map in
                          data/intake/docs-found-us-oct31.json); TEST = Tennessee rows only
  post-links OUTDIR       OUTDIR/report.csv -> data/intake/docs-found-maplinks.json (OK rows, docs-found shape, for
                          chat 10 to merge through the waiting room like the F file) + ...-possible.json
  summary                 data/intake/tools/summary.md = one short page for chats 2, 10, 11
"""
import csv, json, os, sys, collections, datetime, glob

D = 'data/intake'
TODAY = datetime.date.today().isoformat()


def prep_convert(test, out):
    L = json.load(open(f'{D}/leads-oct31.json'))['other_layer']
    keep = [x for x in L if x[1] not in ('PICTURE MAP ONLY', 'NOT FOUND')]
    cnt = collections.Counter(x[0].split('-')[0] for x in keep)
    def rank(x):
        p = x[0].split('-')[0]
        return (0 if p == 'US' else 1 if p == 'CA' else 2, -cnt[p], x[0])
    keep.sort(key=rank)
    rows = [{'ref': r, 'area': r.split('-')[0], 'url': u, 'status': s, 'agency': '', 'note': 'leads-oct31 other_layer'}
            for r, s, u in keep]
    if test:   # one of each of the first 10 hosts, US + CA first
        seen, t = set(), []
        for x in rows:
            h = x['url'].split('/')[2]
            if h not in seen:
                seen.add(h); t.append(x)
            if len(t) >= 10:
                break
        rows = t
    json.dump(rows, open(out, 'w'), indent=0)
    print(f'convert leads: {len(rows)} (of {len(L)})')


def prep_links(test, d):
    os.makedirs(d, exist_ok=True)
    found = json.load(open(f'{D}/docs-found-us-oct31.json'))
    have = {r for r, v in found.items() if isinstance(v, dict) and v.get('map')}
    parks, by_st = {}, collections.defaultdict(list)
    for f in glob.glob('data/parkinfo/US-*.json'):
        st = os.path.basename(f)[3:5]
        for ref, v in json.load(open(f)).get('parks', {}).items():
            if ref in have or not isinstance(v, list) or len(v) < 7:
                continue
            parks[ref] = {'name': v[0], 'type': v[2], 'lat': v[5], 'lon': v[6], 'alt_names': []}
            by_st[st].append(ref)
    ag = []
    for r in csv.DictReader(open(f'{D}/us-agency-maps-index.csv')):
        st = (r.get('state') or '').strip().upper()
        if test and st != 'TN':   # no KY rows in the index (KY has its own bots); Tennessee = the small test
            continue
        refs = sorted(set(by_st.get(st, [])))
        if refs and r.get('url', '').startswith('http'):
            ag.append({'agency': r['agency'], 'state_or_prov': st, 'index_url': r['url'], 'park_refs': refs})
    used = {x for a in ag for x in a['park_refs']}
    json.dump(ag, open(f'{d}/agency_pages.json', 'w'), indent=1)
    json.dump({k: v for k, v in parks.items() if k in used}, open(f'{d}/parks.json', 'w'))
    print(f'map links: {len(ag)} agency pages, {len(used)} parks with no own map yet')


def post_links(outdir):
    p = f'{outdir}/report.csv'
    if not os.path.exists(p):
        print('no report'); return
    ok, maybe = {}, {}
    for r in csv.DictReader(open(p)):
        if not r.get('map_url'):
            continue
        rec = {'st': '', 'page': r.get('page_url', ''), 'map': r['map_url'], 'map_page': 1, 'kind': r.get('kind', ''),
               'date': (r.get('map_date') or '')[:4], 'agency': r.get('agency', ''),
               'notes': f"map-page link extractor (outside tool, not yet reviewed by Fable) {TODAY}: {r.get('why', '')}"[:400]}
        (ok if r.get('status') == 'OK' else maybe if r.get('status') == 'POSSIBLE' else {})[r['ref']] = rec
    json.dump(ok, open(f'{D}/docs-found-maplinks.json', 'w'), indent=0)
    json.dump(maybe, open(f'{D}/docs-found-maplinks-possible.json', 'w'), indent=0)
    print(f'map links: {len(ok)} OK, {len(maybe)} possible')


def summary():
    os.makedirs(f'{D}/tools', exist_ok=True)
    L = [f'# Outside tools, report-only runs ({TODAY})', '',
         "Brandon Oct 31 'yes': used now as REVIEW tools until Fable fixes + wires them (Nov 6). Nothing here is live.", '']
    L.append('## 2-fer checker (data/fers-check/) -> chat 2 rechecks, chat 11 grades')
    for f in sorted(glob.glob('data/fers-check/*.json')):
        try:
            rr = json.load(open(f)).get('rows', []); rr = rr.values() if isinstance(rr, dict) else rr
            v = collections.Counter(x.get('verdict') for x in rr)
        except Exception:
            continue
        L.append(f"- {os.path.basename(f)[:-5]}: " + ', '.join(f'{k} {n}' for k, n in v.most_common()))
    L += ['', '## Map-format converter (branch tools-out, convert/) -> chat 11 grades, chat 9 turns OK ones into LAYER lines']
    p = 'out/convert/report.csv'
    if os.path.exists(p):
        c = collections.Counter(r['status'] for r in csv.DictReader(open(p)))
        L.append('- ' + ', '.join(f'{k} {n}' for k, n in c.most_common()))
    L += ['', '## Map-page link extractor -> data/intake/docs-found-maplinks.json (chat 10 merges like the F file, chat 11 grades)']
    for n in ('docs-found-maplinks.json', 'docs-found-maplinks-possible.json'):
        if os.path.exists(f'{D}/{n}'):
            L.append(f'- {n}: {len(json.load(open(f"{D}/{n}")))} parks')
    L += ['', 'Known weak spot (HQ): the link extractor can call a sign / logo PDF a map (LSRCA test: Beaver River = '
          "'Sign-with-FedDev-logo.pdf'). Chat 11: open each map before YES."]
    open(f'{D}/tools/summary.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    a = sys.argv[1:]
    {'prep-convert': lambda: prep_convert(a[1] == 'yes', a[2]), 'prep-links': lambda: prep_links(a[1] == 'yes', a[2]),
     'post-links': lambda: post_links(a[1]), 'summary': summary}[a[0]]()
