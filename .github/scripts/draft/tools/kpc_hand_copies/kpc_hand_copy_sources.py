#!/usr/bin/env python3
"""kpc_hand_copy_sources.py: propose a source page for each hand-copied size (21 Nov 2026, job E).

A hand copy is a size a person typed in from an agency's figure without saying where it came from. The key counts it only
once it names its source page (KPC-Links kpc_match_checks.tagged_witness). This tool PROPOSES that page for each hand copy,
from what the bots already saved. It fetches nothing and changes no input:
  1. the park's own web page as the page reader saw it (park-pages/facts/<area>.json): its address, and the size line it
     quoted when that size agrees with the hand copy;
  2. park facts (park-facts.json[.gz]) for the same page, when the page reader's own files are not given;
  3. the park's POTA link when it is the agency's own page (link-ids.csv);
  4. a web address already on the map record (an optional ref,url CSV, e.g. the key's saved address fields).

  python3 kpc_hand_copy_sources.py --acres acres.json --pages park-pages/facts [--facts park-facts.json.gz]
                                   [--links link-ids.csv] [--map-urls map-urls.csv] [--parkinfo data/parkinfo] --out DIR
      DIR/PRIVATE-hand-copy-sources-review.csv  park, proposed source_url, where it came from, quoted size line, match yes/no.
                                                PRIVATE: never commit it, never zip it. A person or Quality approves it first.
      DIR/hand-copy-sources-counts.json         PUBLIC: counts by state only.
  python3 kpc_hand_copy_sources.py --selftest

Nothing here writes a source_url into live data: an approved review file is fed in by a later, separate step.
"""
import argparse, collections, csv, datetime, glob, gzip, json, os, re, sys, tempfile

VERSION = 'kpc_hand_copy_sources 2026-11-21a'
URL = re.compile(r'^https?://\S+\.\S+', re.I)
REF = re.compile(r'^[A-Z0-9]{1,4}-\d{4,5}$')
COLS = ['park', 'state', 'hand_acres', 'proposed_source_url', 'from', 'quoted_size_line', 'page_acres', 'match', 'note']


def agrees(hand, page):
    """A page size agrees with a hand copy when they differ by at most half an acre or 0.5% (the agency's own rounding)."""
    try:
        h, p = float(hand), float(page)
    except (TypeError, ValueError):
        return False
    return h > 0 and p > 0 and abs(h - p) <= max(0.6, 0.005 * h)


def clip(s, n=200):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def read_hand(acres_path):
    with open(acres_path, encoding='utf-8') as f:
        d = json.load(f)
    rows = d.get('parks', d) if isinstance(d, dict) else {}
    return {k: v for k, v in rows.items() if isinstance(v, dict) and REF.match(str(k))
            and (str(v.get('how') or '').lower().startswith('hand copy') or v.get('witness') == 'hand_copy')}


def read_page_files(folder):
    """{ref: {'url', 'own', 'area', 'sizes': [{'acres', 'quote', 'total'}]}} from the page reader's facts files."""
    out = {}
    if not folder or not os.path.isdir(folder):          # no folder given: nothing (never the current folder's files)
        return out
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        for ref, p in (d.get('parks') or {}).items():
            if not isinstance(p, dict):
                continue
            pg = p.get('page') or {}
            out[ref] = {'url': pg.get('final_url') or (p.get('asked') or {}).get('url'), 'status': pg.get('status'),
                        'own': (p.get('own_page') or {}).get('is') == 'own' and not p.get('unofficial'),
                        'area': p.get('area') or d.get('area'),
                        'sizes': [{'acres': s.get('acres'), 'quote': s.get('quote') or s.get('line') or s.get('as'), 'total': bool(s.get('total'))}
                                  for s in p.get('sizes') or [] if isinstance(s, dict)]}
    return out


def read_facts(path):
    """The same page facts from park facts (sizes keep only the page's own words 'as', no sentence)."""
    if not path:
        return {}
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt', encoding='utf-8') as f:
        d = json.load(f)
    out = {}
    for ref, r in (d.get('parks') or {}).items():
        pg = r.get('page') or {}
        if not pg:
            continue
        out[ref] = {'url': pg.get('url'), 'status': pg.get('status'), 'own': pg.get('own_page') == 'own' and not pg.get('unofficial'),
                    'area': r.get('area'),
                    'sizes': [{'acres': s.get('acres'), 'quote': s.get('as'), 'total': bool(s.get('total'))} for s in pg.get('sizes') or []]}
    return out


def read_pota_links(parkinfo):
    """{ref: the park's POTA link} from data/parkinfo/<area>.json (the POTA list: parks {ref: [name, link, ...]})."""
    out = {}
    if not parkinfo or not os.path.isdir(parkinfo):
        return out
    for path in sorted(glob.glob(os.path.join(parkinfo, '*.json'))):
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        for ref, r in ((d.get('parks') or {}) if isinstance(d, dict) else {}).items():
            if isinstance(r, list) and len(r) > 1 and URL.match(str(r[1] or '').strip()):
                out[ref] = str(r[1]).strip()
    return out


def read_links(path, pota_links):
    """{ref: (agency page address, area)} for POTA links the link bot found to be the agency's own page of this one park.
    link-ids.csv gives the verdict and the host; the address itself is the POTA list's link (data/parkinfo), and only
    when its host is the one the link bot judged."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            url, host = pota_links.get(r.get('park')) or '', (r.get('website') or '').strip().lower()
            m = re.match(r'^https?://([^/:?#]+)', url, re.I)
            if (m and host and (m.group(1).lower() == host or m.group(1).lower().endswith('.' + host))
                    and str(r.get('site') or '').startswith('agency') and (r.get('page kind') or '') in ('own page', 'document')
                    and str(r.get('link shared by (parks)') or '1').strip() in ('', '1')):
                out[r['park']] = (url, r.get('area'), r.get('page kind'))
    return out


def read_map_urls(path):
    """{ref: [address]} from a ref,url CSV of web addresses already on the map records."""
    out = collections.defaultdict(list)
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            u = (r.get('url') or '').strip()
            if REF.match(str(r.get('park') or r.get('ref') or '')) and URL.match(u):
                out[r.get('park') or r.get('ref')].append(u)
    return out


def propose(ref, hand, pages, facts, links, map_urls, area_of):
    """-> one review row for this hand copy."""
    h = hand.get('acres')
    pg = pages.get(ref) or facts.get(ref)
    row = {'park': ref, 'state': (pg or {}).get('area') or (links.get(ref) or ('', ''))[1] or area_of.get(ref) or 'unknown',
           'hand_acres': h, 'proposed_source_url': '', 'from': '', 'quoted_size_line': '', 'page_acres': '', 'match': 'no', 'note': ''}
    if pg and pg.get('own') and pg.get('status') == 200 and URL.match(str(pg.get('url') or '')):
        sizes = sorted(pg.get('sizes') or [], key=lambda s: (not s.get('total'),))
        hit = next((s for s in sizes if agrees(h, s.get('acres'))), None)
        row.update({'proposed_source_url': pg['url'], 'from': 'own page (page reader)' if ref in pages else 'own page (park facts)'})
        if hit:
            row.update({'quoted_size_line': clip(hit.get('quote')), 'page_acres': hit.get('acres'), 'match': 'yes'})
            return row
        if sizes:
            near = min(sizes, key=lambda s: abs(float(s.get('acres') or 0) - float(h or 0)))
            row.update({'quoted_size_line': clip(near.get('quote')), 'page_acres': near.get('acres'),
                        'note': 'the page gives another size'})
        else:
            row['note'] = 'the page gives no size'
        return row
    if ref in links:
        row.update({'proposed_source_url': links[ref][0], 'note': 'page text not read yet',
                    'from': 'POTA link (agency document)' if links[ref][2] == 'document' else 'POTA link (agency page)'})
    elif map_urls.get(ref):
        row.update({'proposed_source_url': map_urls[ref][0], 'from': 'web address on the map record', 'note': 'page text not read yet'})
    else:
        row['note'] = 'no agency page found'
    return row


def run(acres, pages=None, facts=None, links=None, map_urls=None, parkinfo=None):
    hand = read_hand(acres)
    P, F, L, M = read_page_files(pages), read_facts(facts), read_links(links, read_pota_links(parkinfo)), read_map_urls(map_urls)
    area_of = {}
    if parkinfo:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kpc_park_facts'))
        import kpc_park_facts as PF
        area_of = {ref: r.get('area') for ref, r in PF.read_parkinfo(parkinfo).items()}
    rows = [propose(ref, hand[ref], P, F, L, M, area_of) for ref in sorted(hand)]
    by = collections.defaultdict(collections.Counter)
    for r in rows:
        c = by[r['state']]
        c['hand copies'] += 1
        if r['proposed_source_url']: c['a source page proposed'] += 1
        if r['match'] == 'yes': c['page text agrees'] += 1
        elif r['note']: c[r['note']] += 1
    tot = collections.Counter()
    for c in by.values():
        tot.update(c)
    doc = {'made': datetime.date.today().isoformat(), 'tool': VERSION,
           'note': 'Proposed source pages for hand-copied sizes, counted by state. Proposals wait for a person or Quality to approve '
                   'them; nothing is written into live data. Park numbers are in the PRIVATE review file only.',
           'total': dict(sorted(tot.items())), 'by_state': {k: dict(sorted(v.items())) for k, v in sorted(by.items())}}
    return rows, doc


def write(out, rows, doc):
    parts = os.path.abspath(out).split(os.sep)
    if 'data' in parts and any(os.path.exists(os.path.join(os.sep.join(parts[:i]), '.git')) for i in range(1, len(parts))):
        raise SystemExit(f'refused: {out} is inside a repo data folder; write the review outside the repo')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'PRIVATE-hand-copy-sources-review.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out, 'hand-copy-sources-counts.json'), 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')


def selftest():
    print(f'{VERSION}  (Python {sys.version.split()[0]})  SELF-TEST')
    bad = []

    def ok(what, cond):
        print(f'  {"ok  " if cond else "FAIL"} {what}')
        if not cond:
            bad.append(what)
    ok('a size off by rounding agrees', agrees(1234, 1234.4) and agrees(5000, 5020) and not agrees(5000, 5100) and not agrees(None, 3))
    with tempfile.TemporaryDirectory() as t:
        ap = os.path.join(t, 'acres.json')
        hc = lambda a: {'acres': a, 'how': 'hand copy (ZZ Parks, page not given)', 'agency': 'ZZ Parks', 'source_url': ''}
        json.dump({'US-9001': hc(1234), 'US-9002': hc(500), 'US-9003': hc(77), 'US-9004': hc(88), 'US-9005': hc(99),
                   'US-9006': {'acres': 10, 'how': 'number'}, 'US-9007': hc(60),
                   'US-9008': hc(40), 'US-9009': hc(30)}, open(ap, 'w'))
        pdir = os.path.join(t, 'pages'); os.makedirs(pdir)
        page = lambda u, sizes, own='own': {'page': {'final_url': u, 'status': 200}, 'own_page': {'is': own}, 'area': 'US-ZZ',
                                            'sizes': [{'acres': a, 'quote': q, 'total': True} for a, q in sizes]}
        json.dump({'area': 'US-ZZ', 'parks': {
            'US-9001': page('https://zz.invented.example/lake', [(1234.2, 'The park covers 1,234.2 acres along the lake.')]),
            'US-9002': page('https://zz.invented.example/hill', [(900, 'Hill park: 900 acres.')]),
            'US-9007': page('https://blog.invented.example/hill', [(60, 'about 60 acres')], own='not own')}}, open(os.path.join(pdir, 'US-ZZ.json'), 'w'))
        lp = os.path.join(t, 'links.csv')
        with open(lp, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['park', 'area', 'website', 'site', 'page kind', 'link shared by (parks)'])
            w.writerow(['US-9003', 'US-YY', 'yy.invented.example', 'agency (known)', 'own page', '1'])
            w.writerow(['US-9007', 'US-ZZ', 'zz.invented.example', 'agency (known)', 'own page', '1'])
            w.writerow(['US-9005', 'US-YY', 'other.invented.example', 'agency (known)', 'own page', '1'])
            w.writerow(['US-9008', 'US-YY', 'yy.invented.example', 'agency (known)', 'document', '1'])
            w.writerow(['US-9009', 'US-YY', 'yy.invented.example', 'agency (known)', 'own page', '3'])
        pi = os.path.join(t, 'parkinfo'); os.makedirs(pi)
        json.dump({'parks': {'US-9003': ['Invented Marsh', 'https://yy.invented.example/marsh', 'Wildlife Area'],
                             'US-9007': ['Invented Hill Two', 'https://zz.invented.example/hill-two', 'State Park'],
                             'US-9005': ['Invented Cove', 'https://elsewhere.invented.example/cove', 'State Park'],
                             'US-9008': ['Invented Dunes', 'https://yy.invented.example/dunes.pdf', 'State Park'],
                             'US-9009': ['Invented Glen', 'https://yy.invented.example/area', 'State Park']}},
                  open(os.path.join(pi, 'US-YY.json'), 'w'))
        mp = os.path.join(t, 'map.csv')
        with open(mp, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['park', 'url']); w.writerow(['US-9004', 'https://yy.invented.example/bay'])
        before = {p: open(p, 'rb').read() for p in (ap, lp, mp, os.path.join(pdir, 'US-ZZ.json'))}
        rows, doc = run(ap, pdir, None, lp, mp, pi)
        r = {x['park']: x for x in rows}
        ok('only hand copies get a row', set(r) == {'US-9001', 'US-9002', 'US-9003', 'US-9004', 'US-9005', 'US-9007', 'US-9008', 'US-9009'})
        ok('an agency document link is proposed and says so', r['US-9008']['from'] == 'POTA link (agency document)')
        ok('a link several parks share is never proposed', r['US-9009']['proposed_source_url'] == '')
        ok('the own page whose size agrees is proposed, with its size line quoted, match yes',
           r['US-9001']['match'] == 'yes' and r['US-9001']['proposed_source_url'] == 'https://zz.invented.example/lake'
           and '1,234.2 acres' in r['US-9001']['quoted_size_line'])
        ok('a page with another size: proposed, match no, the line quoted for the reviewer',
           r['US-9002']['match'] == 'no' and r['US-9002']['note'] == 'the page gives another size' and r['US-9002']['page_acres'] == 900)
        ok('no page read: the agency link is proposed, match no', r['US-9003']['from'] == 'POTA link (agency page)' and r['US-9003']['match'] == 'no')
        ok('the web address on the map record is used last', r['US-9004']['from'] == 'web address on the map record')
        ok('nothing found (the link\'s host is not the one judged): no address made up',
           r['US-9005']['proposed_source_url'] == '' and r['US-9005']['note'] == 'no agency page found')
        ok('a page that is not the park\'s own (not official) is never proposed for its size',
           r['US-9007']['match'] == 'no' and r['US-9007']['proposed_source_url'] == 'https://zz.invented.example/hill-two')
        ok('counts by state', doc['by_state']['US-ZZ']['hand copies'] == 3 and doc['total']['page text agrees'] == 1)
        out = os.path.join(t, 'out'); write(out, rows, doc)
        pub = open(os.path.join(out, 'hand-copy-sources-counts.json'), encoding='utf-8').read()
        ok('the public file names no park', not re.search(r'US-9\d{3}', pub))
        ok('the review file is PRIVATE by name and has the review columns',
           next(csv.reader(open(os.path.join(out, 'PRIVATE-hand-copy-sources-review.csv'), encoding='utf-8'))) == COLS)
        ok('no input changed (nothing written into live data)', all(open(p, 'rb').read() == b for p, b in before.items()))
        os.makedirs(os.path.join(t, 'repo', '.git')); os.makedirs(os.path.join(t, 'repo', 'data'))
        try:
            write(os.path.join(t, 'repo', 'data', 'x'), rows, doc); refused = False
        except SystemExit:
            refused = True
        ok('it refuses to write the review into a repo data folder', refused)
    print('SELF-TEST PASSED' if not bad else f'SELF-TEST FAILED: {len(bad)}')
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='Propose a source page for each hand-copied size (review file, private).')
    ap.add_argument('--acres', help="the acreage bot's acres.json")
    ap.add_argument('--pages', help="the page reader's facts folder (park-pages/facts)")
    ap.add_argument('--facts', help='park-facts.json(.gz), for pages the page reader files do not hold')
    ap.add_argument('--links', help='link-ids.csv')
    ap.add_argument('--map-urls', help='ref,url CSV of web addresses already on the map records')
    ap.add_argument('--parkinfo', help='data/parkinfo (a state for parks with no page or link)')
    ap.add_argument('--out', default='hand-copy-sources-out')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.acres:
        ap.error('give --acres')
    rows, doc = run(a.acres, a.pages, a.facts, a.links, a.map_urls, a.parkinfo)
    write(a.out, rows, doc)
    t = doc['total']
    print(f"{t.get('hand copies', 0)} hand copies: {t.get('a source page proposed', 0)} with a source page proposed, "
          f"{t.get('page text agrees', 0)} where the page text agrees. Review: {a.out}/PRIVATE-hand-copy-sources-review.csv (private)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
