#!/usr/bin/env python3
"""Oct 31 2026 (chat 10; HQ 5:45 PM, Brandon 'let 10 wire in and let him look to fix map page link'): glue for the outside
coder's three tools, now in .github/scripts/tools/ (wired; Fable still reviews Nov 6). Replaces HQ's stop-gap kpc_outside_tools.py.
Nothing here edits data/fers, a key or a card: the 2-fer checker REPORTS, the converter's OK rows go to the layer collector
(chat 11 grades like every layer), the link extractor's finds go to data/intake/docs-found-maplinks*.json (merged by
kpc_docs_merge.py through the waiting room).
  fers-alerts             data/fers-check/*.json -> data/fers-check/alerts.md (SHRUNK / GONE / MOVED rows for chat 2 + 11)

  prep-convert TEST OUT   archive/2026-10/leads-oct31.json 'other_layer' ([ref, status, url]) -> OUT (list of dicts),
                          US + Canada first, then the rest by count; picture-map-only / not-found rows left out
  prep-links TEST DIR     data/intake/us-agency-maps-index.csv + data/parkinfo/US-XX.json -> DIR/agency_pages.json +
                          DIR/parks.json (each agency gets the parks of its state that have NO own map in
                          archive/2026-10/docs-found-us-oct31.json); TEST = Tennessee rows only
  post-links OUTDIR       OUTDIR/report.csv -> data/intake/docs-found-maplinks.json (OK rows, docs-found shape, for
                          chat 10 to merge through the waiting room like the F file) + ...-possible.json
  summary                 data/intake/tools/summary.md = one short page for chats 2, 10, 11
"""
import csv, json, os, sys, collections, datetime, glob, gzip, hashlib
from zoneinfo import ZoneInfo

D = 'data/intake'
ARCH = 'archive/2026-10'   # Oct 31 / Nov 1 intake one-offs, kept (not deleted)
CT = ZoneInfo('America/Chicago')
TODAY = datetime.datetime.now(CT).date().isoformat()   # Nov 2 review (Quality 7a): Central, not the runner's UTC clock


def central(ts):
    """'2026-11-01T11:14:06Z' -> '2026-11-01 5:14 AM CST' ('' when it cannot be read)."""
    try: t = datetime.datetime.fromisoformat(str(ts).replace('Z', '+00:00')).astimezone(CT)
    except ValueError: return ''
    return t.strftime('%Y-%m-%d %I:%M %p %Z').replace(' 0', ' ')


def fers_now(doc, area):
    """The 2-fer file there NOW for a check file: (path, sha256 of its plain bytes) or (None, None)."""
    cands = [doc.get('fers_file')] if doc.get('fers_file') else []
    cands += [f'data/fers/{area}.json', f'data/fers/{area}.json.gz']
    for fp in cands:
        if fp and os.path.isfile(fp):
            raw = gzip.open(fp, 'rb').read() if fp.endswith('.gz') else open(fp, 'rb').read()
            return fp, hashlib.sha256(raw).hexdigest()
    return None, None


def prep_convert(test, out):
    L = json.load(open(f'{ARCH}/leads-oct31.json'))['other_layer']
    keep = [x for x in L if x[1] not in ('PICTURE MAP ONLY', 'NOT FOUND')]
    cnt = collections.Counter(x[0].split('-')[0] for x in keep)
    def rank(x):
        p = x[0].split('-')[0]
        return (0 if p == 'US' else 1 if p == 'CA' else 2, -cnt[p], x[0])
    keep.sort(key=rank)
    rows = [{'ref': r, 'area': r.split('-')[0], 'url': u, 'status': s, 'agency': '', 'note': 'leads-oct31 other_layer'}
            for r, s, u in keep]
    # Oct 31 7:05 PM (HQ): Retry15 world 'other' leads after leads-oct31 (map-layer kinds only; picture / PDF maps go to the picture-map
    # saver, unofficial maps wait for R-G9U, parcels go to the parcel finder)
    R15 = {}
    for f in [f'{D}/world-sources-r15.json'] + sorted(glob.glob(f'{D}/_in/convert/world-sources-*.json')):   # + every world file the intake reader pulled
        try: R15.update(json.load(open(f)).get('other') or {})
        except Exception: pass
    for f in sorted(glob.glob(f'{D}/_in/convert/leads-*.json')):   # newer leads files: their 'other_layer' rows too
        try:
            for x in json.load(open(f)).get('other_layer') or []:
                if len(x) >= 3 and x[1] not in ('PICTURE MAP ONLY', 'NOT FOUND'): R15.setdefault(x[0], {'url': x[2], 'status': 'FOUND ' + str(x[1]), 'agency': ''})
        except Exception: pass
    have = {(x['ref'], x['url']) for x in rows}
    for r, v in R15.items():
        st = str((v or {}).get('status') or '')
        if not (v or {}).get('url') or not st.startswith(('FOUND', 'POSSIBLE MATCH', 'GIS FOUND')) or (r, v['url']) in have: continue
        rows.append({'ref': r, 'area': r.split('-')[0], 'url': v['url'], 'status': st, 'agency': v.get('agency') or '', 'note': 'world-sources-r15 other'})
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
    found = json.load(open(f'{ARCH}/docs-found-us-oct31.json'))
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
    web = {}
    for f in glob.glob('data/parkinfo/US-*.json'):
        for ref, v in json.load(open(f)).get('parks', {}).items():
            if isinstance(v, list) and len(v) > 1 and str(v[1]).startswith('http'): web[ref] = v[1].strip()
    units = collections.defaultdict(lambda: collections.defaultdict(set))   # host -> unit page -> refs
    NATIONAL = ('fs.usda.gov', 'fws.gov', 'nps.gov', 'blm.gov')
    for r in csv.DictReader(open(f'{D}/us-agency-maps-index.csv')):
        st = (r.get('state') or '').strip().upper()
        if test and st != 'TN':   # no KY rows in the index (KY has its own bots); Tennessee = the small test
            continue
        refs = sorted(set(by_st.get(st, [])))
        url = r.get('url', '')
        if not (refs and url.startswith('http')): continue
        host = url.split('/')[2].lower()
        nat = next((h for h in NATIONAL if host == h or host.endswith('.' + h)), None)
        if nat:   # Oct 31 (HQ): a NATIONAL index names no park: go through each unit's own page (forest / refuge / park) instead
            for ref in refs:
                u = web.get(ref, '')
                if u and (u.split('/')[2].lower() == nat or u.split('/')[2].lower().endswith('.' + nat)):
                    units[nat][u.rstrip('/')].add(ref)
            continue
        ag.append({'agency': r['agency'], 'state_or_prov': st, 'index_url': url, 'park_refs': refs})
    for nat, pages in units.items():
        for u, rs in pages.items():
            ag.append({'agency': f'{nat} unit page', 'state_or_prov': '', 'index_url': u, 'park_refs': sorted(rs), 'max_depth': 2,
                       'follow_patterns': [r'map', r'brochure', r'visit', r'plan']})
    used = {x for a in ag for x in a['park_refs']}
    json.dump(ag, open(f'{d}/agency_pages.json', 'w'), indent=1)
    json.dump({k: v for k, v in parks.items() if k in used}, open(f'{d}/parks.json', 'w'))
    print(f'map links: {len(ag)} agency pages, {len(used)} parks with no own map yet')


def post_links(outdir):
    p = f'{outdir}/report.csv'
    if not os.path.exists(p):
        print('no report'); return
    ok, maybe = {}, {}
    stof = {}
    for f in glob.glob('data/parkinfo/US-*.json'):
        for ref in json.load(open(f)).get('parks', {}): stof[ref] = os.path.basename(f)[3:5]
    for r in csv.DictReader(open(p)):
        if not r.get('map_url'):
            continue
        rec = {'st': stof.get(r['ref'], ''), 'page': r.get('page_url', ''), 'map': r['map_url'], 'map_page': 1, 'kind': r.get('kind', ''),
               'date': (r.get('map_date') or '')[:4], 'agency': r.get('agency', ''),
               'notes': f"map-page link extractor (outside tool, not yet reviewed by Fable) {TODAY}: {r.get('why', '')}"[:400]}
        (ok if r.get('status') == 'OK' else maybe if r.get('status') == 'POSSIBLE' else {})[r['ref']] = rec
    json.dump(ok, open(f'{D}/docs-found-maplinks.json', 'w'), indent=0)
    json.dump(maybe, open(f'{D}/docs-found-maplinks-possible.json', 'w'), indent=0)
    print(f'map links: {len(ok)} OK, {len(maybe)} possible')


def fers_alerts():
    """Nov 2 review (Quality 7a): an area whose 2-fer file changed after the check (fers_sha256 no longer matches the file there now,
    plain or gzipped) is left out of the count and listed as stale: its alerts may be about rows that no longer exist.
    Each area shows the date its check started, in Central time."""
    L = [f'# 2-fer checker alerts ({TODAY}, Central)', '', 'Rows the weekly checker found SHRUNK / GONE / MOVED against the live official layers: chat 2 rechecks, chat 11 grades. Nothing changed by the bot.', '']
    n, stale = 0, []
    for f in sorted(glob.glob('data/fers-check/*.json')):
        try:
            doc = json.load(open(f)); rr = doc.get('rows', []); rr = list(rr.values()) if isinstance(rr, dict) else rr
        except Exception: continue
        area = doc.get('area') or os.path.basename(f)[:-5]
        bad = [x for x in rr if x.get('verdict') in ('SHRUNK', 'GONE', 'MOVED')]
        when = central(doc.get('started') or doc.get('updated') or '')
        try: fp, sha = fers_now(doc, area)
        except Exception: fp, sha = None, None  # noqa: BLE001
        if doc.get('fers_sha256') and sha and sha != doc['fers_sha256']:
            stale.append(f"- {area} (checked {when or 'date unknown'}; {len(bad)} alert(s) not counted)")
            continue
        if bad:
            L.append(f"- **{area}** (checked {when or 'date unknown'}): " + ', '.join(f"{k} {v}" for k, v in collections.Counter(x['verdict'] for x in bad).most_common()))
            n += len(bad)
    if n == 0: L.append('- nothing shrank, went or moved')
    if stale:
        L += ['', f'## Stale: the 2-fer file changed since the check ({len(stale)} area(s), left out above until the next check)', ''] + stale
    open('data/fers-check/alerts.md', 'w').write('\n'.join(L) + '\n')
    print(f'ALERTS={n}')


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
     'post-links': lambda: post_links(a[1]), 'summary': summary, 'fers-alerts': fers_alerts}[a[0]]()
