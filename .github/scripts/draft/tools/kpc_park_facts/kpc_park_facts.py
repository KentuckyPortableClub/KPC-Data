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

VERSION = 'kpc_park_facts 7 (2026-11-23)'
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


# ------------------------------------------------------------------ size witness -------------------------------------
# Where an official size came from, so the key's matching knows whether it can count as a second, independent agreement.
#   same_record      read from a map layer the key already joined this park to (the record the name picked): never proof
#   other_layer      read from a different map layer than the ones the key joined: not proof (another layer is not a witness)
#   agency_document  read from the agency's own published list (spreadsheet, PDF, CSV, web table): proof
#   hand_copy        typed in by a person from the agency's figure: proof
#   unknown          can't tell (no address, or the key has no joined layer for the park to compare with)
WITNESS_TAGS = ('same_record', 'other_layer', 'agency_document', 'hand_copy', 'unknown')
WITNESS_PROOF = ('agency_document', 'hand_copy')
# the key's national layers (KPC-Links kpc_us_key.py Q and FWS); the state layers come from data/us-key/layers.json
NATIONAL_LAYERS = {'PAD-US': 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0/query',
                   'fws': 'https://services.arcgis.com/QVENGdaPbd4LUkLV/arcgis/rest/services/FWSInterest_Simplified_Authoritative/FeatureServer/0/query'}
MAP_LAYER = re.compile(r'/(?:feature|map)server/\d+', re.I)
LAYER_EXPORT = re.compile(r'/api/download/v\d+/items/|/sharing/rest/content/items/|hub\.arcgis\.com/|/datasets/', re.I)
DOC_EXT = re.compile(r'\.(?:pdf|xlsx?|csv|txt|docx?)(?:$|[?#])', re.I)


def norm_layer(url):
    """A map layer address without the scheme, 'www.', the query and a trailing /query: 'host/path/featureserver/2'."""
    u = re.sub(r'^[a-z]+://', '', str(url or '').strip().lower()).split('?')[0].split('#')[0].rstrip('/')
    u = re.sub(r'^www\.', '', u)
    u = re.sub(r'/query$', '', u)
    m = MAP_LAYER.search(u)
    return u[:m.end()] if m else u


def read_key_layers(key_dirs, layers_path=None):
    """KPC-Links' saved keys -> {ref: set of normalised layer addresses the key joined the park to}. A park the key has with
    no joined layer gets an empty set. layers.json gives each state layer's address; NATIONAL_LAYERS the two national ones."""
    ids = {k: norm_layer(v) for k, v in NATIONAL_LAYERS.items()}
    if layers_path and os.path.exists(layers_path):
        with open(layers_path, encoding='utf-8') as f:
            for lid, v in (json.load(f) or {}).items():
                if isinstance(v, list) and v and isinstance(v[0], str):
                    ids[lid] = norm_layer(v[0])
    out = {}
    for d in key_dirs or []:
        for path in sorted(glob.glob(os.path.join(d, '*.json'))):
            if not AREA.match(os.path.basename(path)[:-5]):
                continue
            with open(path, encoding='utf-8') as f:
                doc = json.load(f)
            for ref, p in ((doc.get('parks') if isinstance(doc.get('parks'), dict) else doc) or {}).items():
                if REF.match(str(ref)) and isinstance(p, dict):
                    out[ref] = {ids.get(s) or ids.get(re.sub(r'\s.*$', '', str(s)), '') for s in p.get('src') or []} - {''}
    return out


def witness(ref, row, key_layers):
    """(tag, why) for one official size. key_layers = read_key_layers(...) or None when the key was not read."""
    how = str(row.get('how') or '').lower()
    url = str(row.get('source_url') or '').strip()
    if how.startswith('hand copy') or row.get('witness') == 'hand_copy':
        return 'hand_copy', 'typed in by a person from the agency figure'
    if not re.match(r'^https?://', url, re.I):
        return 'unknown', 'no web address for the size'
    if LAYER_EXPORT.search(url):
        return 'unknown', "a map layer's table downloaded from an open-data site: can't tell which layer it is"
    if MAP_LAYER.search(url) or re.search(r'\.zip(?:$|[?#])', url, re.I):
        if key_layers is None:
            return 'unknown', 'a map layer, and the key was not read to compare'
        if not key_layers.get(ref):
            return 'unknown', 'a map layer, and the key has no joined layer for this park'
        if norm_layer(url) in key_layers[ref]:
            return 'same_record', 'a map layer the key already joined this park to'
        return 'other_layer', 'a map layer the key did not join this park to'
    if DOC_EXT.search(url):
        return 'agency_document', "the agency's own published list"
    return 'unknown', 'not sure what the address is'


def tag_sizes(sizes, key_layers):
    for ref, r in sizes.items():
        if r.get('from') == 'keeper' and r.get('witness') in WITNESS_TAGS:   # the keeper's own tag wins
            t, why = r['witness'], r.get('witness_why') or 'tagged by the keeper'
        else:
            t, why = witness(ref, r, key_layers)
        r['witness'], r['witness_why'] = t, why
        r['witness_counts'] = t in WITNESS_PROOF
    return sizes


def read_keeper_sizes(path):
    """The keeper's saved official sizes -> {ref: size fact}. Only the keeper fetches from agency servers, so its sizes come
    first; the acreage bot's fill only the parks the keeper has none for. Expected shape (the same as acres.json):
    {ref: {acres, source_url, read_date, agency?, record_name?, how?, witness?}} or {'parks': {...}}. A missing file = {}."""
    if not path or not os.path.exists(path):
        return {}, None
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    d = d.get('parks', d) if isinstance(d, dict) else {}
    out = {}
    for ref, r in d.items():
        if not REF.match(str(ref)) or not isinstance(r, dict) or r.get('acres') is None:
            continue
        out[ref] = {'acres': r.get('acres'), 'value_given': r.get('value_given'), 'unit_given': r.get('unit_given'),
                    'agency': r.get('agency'), 'record_name': r.get('record_name'), 'how': r.get('how'),
                    'flags': r.get('flags') or [], 'source_url': r.get('source_url'), 'read_date': r.get('read_date'),
                    'other_sources': 0, 'witness': r.get('witness') if r.get('witness') in WITNESS_TAGS else None}
    return out, os.path.basename(path)


def merge_sizes(keeper, acres):
    """Keeper first, the acreage bot as the fallback. Each row says which one it came from ('from')."""
    out = {}
    for ref, r in acres.items():
        out[ref] = dict(r, **{'from': 'acreage bot'})
    for ref, r in keeper.items():
        out[ref] = dict(r, **{'from': 'keeper'})
    return out


def _first(xs, n):
    return list(xs or [])[:n]


_R = [None]


def _agree(nm, pota_name):
    """The reader's own name check (kpc_park_pages_rules.name_agreeing) on the saved heading and title; (None, None) when the
    reader's rules are not at hand or nothing agrees."""
    if _R[0] is None:
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, os.path.normpath(os.path.join(here, '..', '..', '..')))
            import kpc_park_pages_rules as R
            _R[0] = R
        except Exception:  # noqa: BLE001
            _R[0] = False
    if not _R[0] or not isinstance(nm, dict):
        return None, None
    try:
        return _R[0].name_agreeing(nm, pota_name)
    except Exception:  # noqa: BLE001
        return None, None


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
                # 22 Nov 2026 (owner: "not doing a good job of confirming park names"): a heading that was site chrome hid the
                # name; the part of the heading / title that agrees with POTA's name is used when there is one
                'name_vs_pota': _agree(nm, pota.get('name'))[1] or nm.get('vs_pota'),
                'name_on_page': (_agree(nm, pota.get('name'))[0] or nm.get('heading') or nm.get('title') or '')[:120],
                'sizes': [{'acres': s.get('acres'), 'as': s.get('as'), 'total': s.get('total'), 'clean': s.get('clean')}
                          for s in _first(p.get('sizes'), 3)],
                # 22 Nov (owner: "address and directions would help matching"): each page point with its role (park, visitor
                # centre, office, unknown) and the roads and towns the page's directions name
                'coords': [{'lat': c.get('lat'), 'lon': c.get('lon'), 'km_from_pin': c.get('km_from_pin'), 'from': c.get('from'),
                            'role': c.get('role') or 'unknown'}
                           for c in _first(loc.get('coords'), 3) if isinstance(c, dict) and c.get('lat') is not None],
                'directions': ({'roads': [str(r)[:60] for r in _first((loc.get('directions') or {}).get('roads'), 6)],
                                'towns': [str(t)[:40] for t in _first((loc.get('directions') or {}).get('towns'), 4)]}
                               if isinstance(loc.get('directions'), dict) and ((loc.get('directions') or {}).get('roads')
                                                                               or (loc.get('directions') or {}).get('towns')) else None),
                'addresses': [{'text': a.get('text'), 'role': a.get('role')} for a in _first(loc.get('addresses'), 2)],
                # 23 Nov 2026 (owner: "using real names, addresses and directions"): how far and which way from a named town
                # ('2 miles east of Shiocton'), the counties the page names, and the approximate points the converter made
                # from them. 'near' is never a page point: it is approximate, and no key reads it as a point.
                'offsets': [{'km': o.get('km'), 'dir': o.get('dir'), 'of': str(o.get('of') or '')[:40]}
                            for o in _first(loc.get('offsets'), 3) if isinstance(o, dict) and o.get('of')],
                'counties': [str(x)[:40] for x in _first(loc.get('counties'), 4) if str(x).strip()],
                'near': [{'lat': n.get('lat'), 'lon': n.get('lon'), 'within_km': n.get('within_km'), 'from': str(n.get('from') or '')[:60]}
                         for n in _first(loc.get('near'), 3) if isinstance(n, dict) and n.get('lat') is not None],
                'manager': man.get('agency'),
                'status_words': {k: v for k, v in st.items() if v},
                'questions': sorted({q.get('code') for q in p.get('questions') or [] if q.get('code')}),
                # 22 Nov 2026 (owner 3:55 PM, plan P3-P5): what the keys may weigh for matching. Only the reader's SURE parent unit
                # (inside_of), never maybe_inside; tract names as written; map links with their kind (never opened here)
                'parts': [str(x)[:80] for x in _first(p.get('parts'), 12) if str(x).strip()],
                'inside_of': [{'unit': str(u.get('unit') or '')[:100], 'kind': str(u.get('kind') or '')[:40], 'pota_ref': u.get('pota_ref')}
                              for u in _first(p.get('inside_of'), 3) if isinstance(u, dict) and str(u.get('unit') or '').strip()],
                'maps': [{'url': str(m.get('url') or '')[:300], 'kind': m.get('kind'), 'names_park': bool(m.get('names_park'))}
                         for m in _first(p.get('maps'), 6) if isinstance(m, dict) and str(m.get('url') or '').startswith('https://')],
            }
    SHARED_POINTS[0] = drop_shared_points(out)
    return out, areas


SHARED_POINT_PARKS = 3   # the same point on this many parks' pages of one site = the site's own furniture, never a park's point
SHARED_POINTS = [0]


def drop_shared_points(pages):
    """23 Nov 2026: a point that 3 or more parks' pages of ONE site carry (a template's default map, the agency's office,
    as on Illinois DNR where every park page holds the same park's point) is taken out of all of them. A point that
    came from the park's own address is left to the converter's own shared-address rule. -> how many were taken out."""
    seen = {}
    for ref, f in pages.items():
        for c in f.get('coords') or []:
            if str(c.get('from') or '').startswith('address'):
                continue
            try:
                k = (f.get('host') or '', round(float(c['lat']), 3), round(float(c['lon']), 3))
            except (TypeError, ValueError, KeyError):
                continue
            seen.setdefault(k, set()).add(ref)
    bad = {k for k, refs in seen.items() if len(refs) >= SHARED_POINT_PARKS}
    n = 0
    for ref, f in pages.items():
        keep = []
        for c in f.get('coords') or []:
            try:
                k = (f.get('host') or '', round(float(c['lat']), 3), round(float(c['lon']), 3))
            except (TypeError, ValueError, KeyError):
                k = None
            if k in bad and not str(c.get('from') or '').startswith('address'):
                n += 1
                continue
            keep.append(c)
        f['coords'] = keep
    return n


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


def read_crosswalk(folder):
    """The keeper's agency park lists (kpc_agency_lists.py): agency-crosswalk/<agency>.json, each
    {agency, link_kind, source{url, licence, date}, rows[{web_id, map_layer, map_field, map_id}]} -> ({(link kind, web id): tie}, summary).
    A web id two agencies' files map to different map ids is left out (no tie). Never WDPA. A missing folder = no ties."""
    ties, clash, files = {}, set(), []
    if not folder or not os.path.isdir(folder):
        return {}, files
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
        except (OSError, ValueError):
            files.append({'file': os.path.basename(path), 'rows': 0, 'note': 'could not be read: not used'})
            continue
        kind = str(d.get('link_kind') or '').strip().lower()
        src = d.get('source') or {}
        n = 0
        for r in d.get('rows') or []:
            wid, mid = str(r.get('web_id') or '').strip().upper(), str(r.get('map_id') or '').strip()
            lay, fld = str(r.get('map_layer') or ''), str(r.get('map_field') or '')
            if not kind or not wid or not mid or re.search(r'wdpa|protectedplanet', lay + fld + mid, re.I):
                continue
            tie = {'agency': d.get('agency'), 'map_layer': lay, 'map_field': fld, 'map_id': mid,
                   'source_url': src.get('url'), 'source_date': src.get('date')}
            k = (kind, wid)
            if k in ties and (ties[k]['map_layer'], ties[k]['map_id']) != (lay, mid):
                clash.add(k)
            ties.setdefault(k, tie)
            n += 1
        files.append({'file': os.path.basename(path), 'agency': d.get('agency'), 'rows': n,
                      'source_url': src.get('url'), 'licence': src.get('licence'), 'source_date': src.get('date')})
    for k in clash:
        ties.pop(k, None)
    return ties, files


def add_map_ties(links, ties):
    """A usable link id that an agency list maps to a map id gets link['map_tie'] (the keys treat it like a direct id tie)."""
    n = 0
    for r in links.values():
        if not r.get('usable'):
            continue
        t = ties.get((str(r.get('id_kind') or '').strip().lower(), str(r.get('id_value') or '').strip().upper()))
        if t:
            r['map_tie'] = dict(t); n += 1
    return n


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
        # 23 Nov 2026: POTA lists no link for the park, but the reader read the park's own official page from the official-links
        # bot's address. An empty 'no link' row said nothing and made the keys pass over everything that page gave (371 parks,
        # 254 of them Alberta Parks): it is left out, so the reader's own-page test stands.
        no_link = ref in links and str(links[ref].get('page_kind') or '') == 'no link'
        if no_link and (pages.get(ref) or {}).get('own_page') == 'own' and not (pages.get(ref) or {}).get('unofficial'):
            c["page read from the official-links bot's address (POTA lists no link)"] += 1
        elif ref in links:
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
        if pg.get('addresses'):
            c['page gives an address'] += 1
        if pg.get('directions'):
            c['page gives directions (roads or towns)'] += 1
        if pg.get('offsets'):
            c['page says how far and which way from a town'] += 1
        if pg.get('counties'):
            c['page names its county'] += 1
        if pg.get('near'):
            c['approximate point from the page directions'] += 1
        if pg.get('name_vs_pota') in ('same', 'same-core'):
            c["page carries the park's own name"] += 1
        if ref in sizes and pg.get('sizes'):
            c['official size AND a page size'] += 1
    if SHARED_POINTS[0]:
        c["points taken out: the same point on 3 or more parks' pages of one site"] = SHARED_POINTS[0]
    return rows, c


def run(a):
    parks = read_parkinfo(a.parkinfo)
    if not parks:
        raise SystemExit(f'STOP: no US or Canadian parks read from {a.parkinfo}')
    asizes, sname = read_acres(a.acres)
    ksizes, kname = read_keeper_sizes(getattr(a, 'keeper_sizes', None))
    sizes = merge_sizes(ksizes, asizes)
    pages, pareas = read_pages(a.pages)
    links, lname = read_links(a.links)
    ties, xfiles = read_crosswalk(getattr(a, 'crosswalk', None))
    tied = add_map_ties(links, ties)
    key_layers = read_key_layers(a.key, a.layers) if a.key else None
    tag_sizes(sizes, key_layers)
    rows, c = combine(parks, sizes, pages, links)
    for r in sizes.values():
        c['size witness: ' + r['witness']] += 1
        c['size from: ' + r['from']] += 1
    made = a.today or datetime.date.today().isoformat()
    doc = {'made': made, 'tool': VERSION,
           'note': 'Facts collected by three bots, side by side. Nothing here ties a park to land; each source is one '
                   'agreement at most, and the size-witness rules decide what counts.',
           'sources': {'size': {'bot': 'the keeper first, the acreage bot (kpc_acres) as the fallback',
                                'keeper_file': kname, 'keeper_parks': len(ksizes), 'file': sname, 'parks': len(asizes),
                                'used': len(sizes)},
                       'page': {'bot': 'park page reader (kpc-park-pages)', 'areas_read': pareas, 'parks': len(pages)},
                       'link': {'bot': 'link IDs (kpc_link_ids)', 'file': lname, 'parks': len(links)},
                       'crosswalk': {'from': 'agency park lists (the keeper, kpc_agency_lists)', 'files': xfiles,
                                     'parks_tied': tied},
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
             f'  official size: {len(sizes):,} parks ({len(ksizes):,} from the keeper, {len(sizes) - len(ksizes):,} from the acreage bot)',
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
                         'addresses': [{'text': '1 Lake Rd', 'role': 'park'}],
                         'directions': {'sent': 'From Testville take Highway 99', 'roads': ['Highway 99'], 'towns': ['Testville']}},
            'manager': {'agency': 'Invented Parks'}, 'status_words': {'closed': None},
            'questions': [{'code': 'NAME_DIFFERS'}, {'code': 'NAME_DIFFERS'}],
            'parts': ['North Unit', 'South Unit', ''], 'inside_of': [{'unit': 'Invented State Forest', 'kind': 'State Forest', 'quote': 'q'}],
            'maybe_inside': [{'unit': 'Not Sure Forest'}],
            'maps': [{'url': 'https://maps.example.gov/arcgis/x', 'kind': 'web-map', 'names_park': True}, {'url': 'http://plain.example/x.pdf', 'kind': 'pdf'}]},
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
                                out=os.path.join(t, 'out'), today='2026-11-20', key=None, layers=None)
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
        check('tracts, the sure parent unit and https map links are kept; maybe_inside is not (22 Nov)',
              (P['US-9001']['page']['parts'], [u['unit'] for u in P['US-9001']['page']['inside_of']], [m['url'] for m in P['US-9001']['page']['maps']]),
              (['North Unit', 'South Unit'], ['Invented State Forest'], ['https://maps.example.gov/arcgis/x']))
        check("page points keep their role, and the directions' roads and towns are kept (22 Nov)",
              (P['US-9001']['page']['coords'][0]['role'], P['US-9001']['page']['directions']),
              ('unknown', {'roads': ['Highway 99'], 'towns': ['Testville']}))
        check('link id kept and marked usable', (P['US-9002']['link']['id_value'], P['US-9002']['link']['usable']), ('77', True))
        check('a park with no facts still has its row', P['US-9003']['facts_from'], ['link'])
        check('a size for a park not on the list is kept and marked', (P['US-9009'].get('not_on_list'), P['US-9009']['facts_from']),
              (True, ['size']))
        check('counts: one park has an official size AND a page size', doc['counts'].get('official size AND a page size'), 1)
        check('no input file changed', {n: open(os.path.join(t, n), 'rb').read() for n in before} == before, True)
        check('the file says it collects and does not decide', 'Nothing here ties a park to land' in doc['note'], True)
        empty = argparse.Namespace(parkinfo=os.path.join(t, 'parkinfo'), acres=None, pages=None, links=None,
                                   out=os.path.join(t, 'out2'), today='2026-11-20', key=None, layers=None)
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
    ap.add_argument('--key', action='append', help="KPC-Links data/us-key (and data/ca-key): the key's joined layers, for the size witness")
    ap.add_argument('--keeper-sizes', dest='keeper_sizes', help="the keeper's saved official sizes (taken before the acreage bot's)")
    ap.add_argument('--crosswalk', help="the keeper's agency park lists folder (agency-crosswalk/*.json)")
    ap.add_argument('--layers', help='KPC-Links data/us-key/layers.json (each state layer\'s address)')
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
