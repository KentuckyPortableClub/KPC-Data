#!/usr/bin/env python3
"""kpc_park_facts.py: ONE file of what the three collecting bots know about each park.

Plain words
-----------
Three bots each keep their own file:
  acreage bot   (kpc_acres)       tools-out acres/acres.json           the agency's official size
  page reader   (kpc-park-pages)  tools-out park-pages/facts/*.json    what the park's own web page says
  link IDs      (kpc_link_ids)    link-ids.csv                         what the park's POTA web link says
This tool puts them side by side, one row per park, in park-facts.json, with each fact's source and date.

It COLLECTS, it does not DECIDE: no fact here ties a park to land, picks an outline or changes a key. Each source is one
agreement at most (owner's plan, 20 Nov 2026); the size-witness rules decide what counts, later, through the keeper.
Nothing is downloaded and no input file is changed. Standard library only.

  python3 kpc_park_facts.py --parkinfo data/parkinfo --acres acres.json --pages park-pages/facts --links link-ids.csv --out OUT
  python3 kpc_park_facts.py --selftest
"""
import argparse, collections, csv, datetime, glob, json, os, re, sys, tempfile

VERSION = 'kpc_park_facts 1 (2026-11-20)'
REF = re.compile(r'^[A-Z0-9]{1,4}-\d{4,5}$')
AREA = re.compile(r'^(US|CA)-[A-Z]{2}$')


def say(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ readers -------------------------------------------
def read_parkinfo(folder, areas=('US', 'CA')):
    """data/parkinfo/<area>.json -> {ref: {area, name, type, pin}}. Only US and Canadian areas (the bots' scope)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        area = os.path.basename(path)[:-5]
        whole = area in areas                      # CA.json holds all of Canada; the province is the park's last field
        if not whole and (not AREA.match(area) or area.split('-')[0] not in areas):
            continue
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        for ref, v in (d.get('parks') or {}).items():
            if not REF.match(ref) or not isinstance(v, list):
                continue
            if whole:
                prov = v[10] if len(v) > 10 and isinstance(v[10], str) and re.fullmatch(r'[A-Z]{2}', v[10]) else None
                area = f'{os.path.basename(path)[:-5]}-{prov}' if prov else os.path.basename(path)[:-5]
            lat = v[5] if len(v) > 5 else None
            lon = v[6] if len(v) > 6 else None
            out[ref] = {'area': area, 'name': v[0] if v else '', 'type': v[2] if len(v) > 2 else '',
                        'pin': [lat, lon] if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) else None}
    return out


def read_acres(path):
    """acres.json -> {ref: size fact}."""
    if not path or not os.path.exists(path):
        return {}, None
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    out = {}
    for ref, r in d.items():
        if not REF.match(str(ref)) or not isinstance(r, dict) or r.get('acres') is None:
            continue
        out[ref] = {'acres': r.get('acres'), 'value_given': r.get('value_given'), 'unit_given': r.get('unit_given'),
                    'agency': r.get('agency'), 'record_name': r.get('record_name'), 'how': r.get('how') or r.get('match'),
                    'flags': r.get('flags') or [], 'source_url': r.get('source_url'), 'read_date': r.get('read_date'),
                    'other_sources': len(r.get('other_sources') or [])}
    return out, os.path.basename(path)


def _first(xs, n):
    return list(xs or [])[:n]


def read_pages(folder):
    """park-pages/facts/<area>.json -> {ref: page fact}. Only the facts a later rule may weigh; quotes are kept short."""
    out, areas = {}, []
    if not folder or not os.path.isdir(folder):
        return out, areas
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        areas.append(d.get('area') or os.path.basename(path)[:-5])
        for ref, p in (d.get('parks') or {}).items():
            if not REF.match(str(ref)) or not isinstance(p, dict):
                continue
            pg, own, nm = p.get('page') or {}, p.get('own_page') or {}, p.get('name') or {}
            loc, man, st = p.get('location') or {}, p.get('manager') or {}, p.get('status_words') or {}
            pota = p.get('pota') or {}
            out[ref] = {
                '_pota': {'area': p.get('area') or d.get('area'), 'name': pota.get('name'), 'type': pota.get('type'),
                          'pin': pota.get('pin'), 'link': pota.get('link')},
                'read': pg.get('read'), 'url': pg.get('final_url') or (p.get('asked') or {}).get('url'), 'status': pg.get('status'),
                'kind': pg.get('kind'), 'host': pg.get('final_host') or pg.get('host'), 'nps_code': pg.get('nps_code'),
                'own_page': own.get('is'), 'unofficial': bool(p.get('unofficial')),
                'name_vs_pota': nm.get('vs_pota'), 'name_on_page': (nm.get('heading') or nm.get('title') or '')[:120],
                'sizes': [{'acres': s.get('acres'), 'as': s.get('as'), 'total': s.get('total'), 'clean': s.get('clean')}
                          for s in _first(p.get('sizes'), 3)],
                'coords': [{'lat': c.get('lat'), 'lon': c.get('lon'), 'km_from_pin': c.get('km_from_pin'), 'from': c.get('from')}
                           for c in _first(loc.get('coords'), 3)],
                'addresses': [{'text': a.get('text'), 'role': a.get('role')} for a in _first(loc.get('addresses'), 2)],
                'manager': man.get('agency'),
                'status_words': {k: v for k, v in st.items() if v},
                'questions': sorted({q.get('code') for q in p.get('questions') or [] if q.get('code')}),
            }
    return out, areas


def read_links(path):
    """link-ids.csv -> {ref: link fact}."""
    if not path or not os.path.exists(path):
        return {}, None
    out = {}
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            ref = (r.get('park') or '').strip()
            if not REF.match(ref):
                continue
            out[ref] = {'website': r.get('website') or None, 'agency': r.get('agency') or None, 'site': r.get('site') or None,
                        'page_kind': r.get('page kind') or None, 'shared_by': _int(r.get('link shared by (parks)')),
                        'id_kind': r.get('id kind') or None, 'id_value': r.get('id value') or None, 'id_is': r.get('id is') or None,
                        'id_shared_by': _int(r.get('id shared by (parks)')),
                        'usable': (r.get('usable as a link id') or '').strip().lower() == 'yes',
                        'web_name': r.get('web name') or None, 'name_match': r.get('name match') or None,
                        'web_kind': r.get('web kind') or None, 'kind_check': r.get('kind check') or None,
                        'state_check': r.get('state check') or None}
    return out, os.path.basename(path)


def _int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ the one file --------------------------------------
def combine(parks, sizes, pages, links):
    """-> (rows by ref, counts). Every park on the POTA list gets a row, with the facts each bot has for it.
    A bot's fact for a park that is not on the list is kept too (marked not_on_list) so nothing is dropped silently."""
    refs = sorted(set(parks) | set(sizes) | set(pages) | set(links))
    rows, c = {}, collections.Counter()
    for ref in refs:
        p = parks.get(ref)
        alt = (pages.get(ref) or {}).get('_pota') or {}
        if not p and alt.get('name'):        # Kentucky is not in data/parkinfo: the page reader read it from POTA itself
            p = {k: alt.get(k) for k in ('area', 'name', 'type', 'pin')}
            c['park taken from the page reader\'s POTA copy (not in data/parkinfo)'] += 1
        row = {'area': p['area'] if p else None, 'name': p['name'] if p else None,
               'type': p['type'] if p else None, 'pin': p['pin'] if p else None}
        if not p:
            row['not_on_list'] = True
            c['facts for a park not on the POTA list'] += 1
        have = []
        if ref in sizes:
            row['size'] = sizes[ref]; have.append('size')
        if ref in pages:
            row['page'] = {k: v for k, v in pages[ref].items() if k != '_pota'}; have.append('page')
        if ref in links:
            row['link'] = links[ref]; have.append('link')
        row['facts_from'] = have
        rows[ref] = row
        c['parks'] += 1
        c[f'facts from {len(have)} bot(s)'] += 1
        for h in have:
            c['with ' + h] += 1
        if links.get(ref, {}).get('usable'):
            c['with a usable link id'] += 1
        pg = pages.get(ref) or {}
        if pg.get('sizes'):
            c['page states a size'] += 1
        if pg.get('coords'):
            c['page gives coordinates'] += 1
        if ref in sizes and pg.get('sizes'):
            c['official size AND a page size'] += 1
    return rows, c


def run(a):
    parks = read_parkinfo(a.parkinfo)
    if not parks:
        raise SystemExit(f'STOP: no US or Canadian parks read from {a.parkinfo}')
    sizes, sname = read_acres(a.acres)
    pages, pareas = read_pages(a.pages)
    links, lname = read_links(a.links)
    rows, c = combine(parks, sizes, pages, links)
    made = a.today or datetime.date.today().isoformat()
    doc = {'made': made, 'tool': VERSION,
           'note': 'Facts collected by three bots, side by side. Nothing here ties a park to land; each source is one '
                   'agreement at most, and the size-witness rules decide what counts.',
           'sources': {'size': {'bot': 'acreage bot (kpc_acres)', 'file': sname, 'parks': len(sizes)},
                       'page': {'bot': 'park page reader (kpc-park-pages)', 'areas_read': pareas, 'parks': len(pages)},
                       'link': {'bot': 'link IDs (kpc_link_ids)', 'file': lname, 'parks': len(links)},
                       'parks_list': {'from': 'data/parkinfo (POTA)', 'parks': len(parks)}},
           'counts': dict(sorted(c.items())), 'parks': rows}
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, 'park-facts.json')
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, separators=(',', ':'), sort_keys=False)
    os.replace(tmp, path)
    lines = [f'Park facts, {made} ({VERSION})', '',
             f'{len(parks):,} US and Canadian parks on the POTA list.',
             f'  official size (acreage bot): {len(sizes):,} parks',
             f'  own web page read (page reader): {len(pages):,} parks in {", ".join(pareas) or "no state yet"}',
             f'  web link facts (link IDs): {len(links):,} parks', '']
    lines += [f'  {v:>7,}  {k}' for k, v in sorted(c.items())]
    lines += ['', 'One file: park-facts.json, one row per park. Each fact keeps its source and date.',
              'It collects, it does not decide: nothing here ties a park to land or changes a key.']
    with open(os.path.join(a.out, 'summary.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    for ln in lines:
        say(ln)
    say(f'Wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB)')
    return path


# ------------------------------------------------------------------ self-test -----------------------------------------
def selftest():
    bad = []

    def check(what, got, want):
        ok = got == want
        say(f'  {"ok  " if ok else "FAIL"} {what}' + ('' if ok else f': got {got!r}, wanted {want!r}'))
        if not ok:
            bad.append(what)
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, 'parkinfo'))
        os.makedirs(os.path.join(t, 'pages'))
        json.dump({'parks': {'US-9001': ['Invented Lake State Park', 'https://parks.example.gov/invented-lake', 'State Park', '', '',
                                         37.5, -85.1, 1, 1, 1],
                             'US-9002': ['Invented Wildlife Area', 'https://wild.example.gov/wma/77', 'Wildlife Management Area',
                                         '', '', 37.6, -85.2, 1, 1, 1],
                             'US-9003': ['Invented Trail', '', 'Trail', '', '', 37.7, -85.3, 1, 1, 1]}},
                  open(os.path.join(t, 'parkinfo', 'US-ZZ.json'), 'w'))
        json.dump({'parks': {'XX-0001': ['Not us', '', '', '', '', 0, 0, 0, 0, 0]}}, open(os.path.join(t, 'parkinfo', 'XX.json'), 'w'))
        json.dump({'program': 'CA', 'parks': {'CA-9001': ['Invented Provincial Park', '', 'Provincial Park', '', '', 49.0, -123.0,
                                                          1, 1, 1, 'BC']}}, open(os.path.join(t, 'parkinfo', 'CA.json'), 'w'))
        json.dump({'US-9001': {'acres': 1200.0, 'value_given': 1200.0, 'unit_given': 'acres', 'agency': 'Invented Parks',
                               'record_name': 'INVENTED LAKE SP', 'how': 'name+kind', 'source_url': 'https://x.example/list.csv',
                               'read_date': '2026-11-02', 'other_sources': [{}, {}]},
                   'US-9009': {'acres': 5.0, 'agency': 'Invented', 'read_date': '2026-11-02'}},
                  open(os.path.join(t, 'acres.json'), 'w'))
        json.dump({'area': 'US-ZZ', 'parks': {'US-9001': {
            'page': {'final_url': 'https://parks.example.gov/invented-lake', 'status': 200, 'kind': 'html', 'read': '2026-11-20'},
            'own_page': {'is': 'own'}, 'name': {'vs_pota': 'same', 'heading': 'Invented Lake State Park'},
            'sizes': [{'acres': 1180.0, 'as': '1,180 acres', 'total': True, 'clean': True, 'quote': 'x' * 300}],
            'location': {'coords': [{'lat': 37.5, 'lon': -85.1, 'km_from_pin': 0.1, 'from': 'map-link q'}],
                         'addresses': [{'text': '1 Lake Rd', 'role': 'park'}]},
            'manager': {'agency': 'Invented Parks'}, 'status_words': {'closed': None},
            'questions': [{'code': 'NAME_DIFFERS'}, {'code': 'NAME_DIFFERS'}]},
            'US-9010': {'pota': {'name': 'Invented Kentucky Park', 'type': 'State Park', 'pin': [37.0, -86.0]},
                        'page': {'read': '2026-11-20'}, 'own_page': {'is': 'own'}}}},
                  open(os.path.join(t, 'pages', 'US-ZZ.json'), 'w'))
        with open(os.path.join(t, 'link-ids.csv'), 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['park', 'area', 'POTA type', 'website', 'agency', 'site', 'page kind', 'link shared by (parks)', 'id kind',
                        'id value', 'id is', 'id shared by (parks)', 'usable as a link id', 'web name', 'name match', 'web kind',
                        'kind check', 'state check'])
            w.writerow(['US-9002', 'US-ZZ', 'Wildlife Management Area', 'wild.example.gov', 'Invented Wildlife', 'agency (known)',
                        'own page', '1', 'wma number', '77', 'known', '1', 'yes', '', '', '', '', 'same state'])
            w.writerow(['US-9003', 'US-ZZ', 'Trail', '', '', '', 'no link', '', '', '', '', '', '', '', '', '', '', ''])
        ns = argparse.Namespace(parkinfo=os.path.join(t, 'parkinfo'), acres=os.path.join(t, 'acres.json'),
                                pages=os.path.join(t, 'pages'), links=os.path.join(t, 'link-ids.csv'),
                                out=os.path.join(t, 'out'), today='2026-11-20')
        before = {n: open(os.path.join(t, n), 'rb').read() for n in ('acres.json', 'link-ids.csv')}
        path = run(ns)
        doc = json.load(open(path, encoding='utf-8'))
        P = doc['parks']
        check('every park on the list gets a row, other countries left out', sorted(P),
              ['CA-9001', 'US-9001', 'US-9002', 'US-9003', 'US-9009', 'US-9010'])
        check("a park missing from parkinfo is named from the page reader's POTA copy",
              (P['US-9010']['name'], P['US-9010']['area'], P['US-9010'].get('not_on_list'), '_pota' in P['US-9010']['page']),
              ('Invented Kentucky Park', 'US-ZZ', None, False))
        check("Canada's one file: each park gets its province", P['CA-9001']['area'], 'CA-BC')
        check('size, page and link side by side for one park', (P['US-9001']['facts_from'], P['US-9002']['facts_from']),
              (['size', 'page'], ['link']))
        check('official size kept with its source and date', (P['US-9001']['size']['acres'], P['US-9001']['size']['read_date'],
                                                              P['US-9001']['size']['other_sources']), (1200.0, '2026-11-02', 2))
        check('page size kept, long quote left out', (P['US-9001']['page']['sizes'][0]['acres'], 'quote' in P['US-9001']['page']['sizes'][0]),
              (1180.0, False))
        check('page questions listed once each', P['US-9001']['page']['questions'], ['NAME_DIFFERS'])
        check('empty status words dropped', P['US-9001']['page']['status_words'], {})
        check('link id kept and marked usable', (P['US-9002']['link']['id_value'], P['US-9002']['link']['usable']), ('77', True))
        check('a park with no facts still has its row', P['US-9003']['facts_from'], ['link'])
        check('a size for a park not on the list is kept and marked', (P['US-9009'].get('not_on_list'), P['US-9009']['facts_from']),
              (True, ['size']))
        check('counts: one park has an official size AND a page size', doc['counts'].get('official size AND a page size'), 1)
        check('no input file changed', {n: open(os.path.join(t, n), 'rb').read() for n in before} == before, True)
        check('the file says it collects and does not decide', 'Nothing here ties a park to land' in doc['note'], True)
        empty = argparse.Namespace(parkinfo=os.path.join(t, 'parkinfo'), acres=None, pages=None, links=None,
                                   out=os.path.join(t, 'out2'), today='2026-11-20')
        d2 = json.load(open(run(empty), encoding='utf-8'))
        check('runs with only the parks list (a bot file missing is not an error)', d2['counts'].get('facts from 0 bot(s)'), 4)
    say('')
    say('SELF-TEST PASSED' if not bad else f'SELF-TEST FAILED: {len(bad)}: ' + '; '.join(bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='One file of what the acreage bot, the page reader and the link IDs know per park.')
    ap.add_argument('--parkinfo', help='KPC-Data data/parkinfo')
    ap.add_argument('--acres', help="the acreage bot's acres.json")
    ap.add_argument('--pages', help="the page reader's facts folder (park-pages/facts)")
    ap.add_argument('--links', help="kpc_link_ids' link-ids.csv")
    ap.add_argument('--out', default='park-facts', help='output folder (default ./park-facts)')
    ap.add_argument('--today', help=argparse.SUPPRESS)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.parkinfo:
        ap.error('give --parkinfo')
    run(a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
