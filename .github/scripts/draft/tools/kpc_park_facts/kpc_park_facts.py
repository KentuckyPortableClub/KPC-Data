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
  python3 kpc_park_facts.py ... --previous data/park-facts.json.gz     (stop when an input shrank; 27 Nov)
  python3 kpc_park_facts.py --selftest

27 Nov 2026 (audit-facts-nov26): the old key (v1) is no longer read (--key / --layers are taken and ignored); a page size
written in square kilometres is never stored as acres; an impossible pin is no pin; Kentucky's links get their ids; the file
says how new each input is ('inputs') and stops when one shrank; the page reader's new fields are kept.
"""
import argparse, collections, csv, datetime, glob, gzip, hashlib, json, os, re, sys, tempfile

VERSION = 'kpc_park_facts 11 (2026-11-27)'
HERE = os.path.dirname(os.path.abspath(__file__))
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
            pin, problem = pin_check(lat, lon)
            out[ref] = {'area': area, 'name': v[0] if v else '', 'type': v[2] if len(v) > 2 else '', 'pin': pin}
            if problem:
                out[ref]['pin_problem'] = problem
    return out


def pin_check(lat, lon):
    """27 Nov 2026 (audit F2): POTA's pin, checked. -> (pin or None, problem or None). A pin that cannot be a place
    (latitude outside -90..90, longitude outside -180..180) or 0,0 (POTA has no pin) is no pin; POTA's numbers are kept in
    the problem, never fixed here (CA-2456 Maple Lake WMA [100.856, -49.514]: the numbers look swapped)."""
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    if not (num(lat) and num(lon)):
        return None, None
    if lat == 0 and lon == 0:
        return None, {'pota_pin': [lat, lon], 'why': '0,0: POTA gives no real pin for this park'}
    bad = ([] if -90 <= lat <= 90 else ['latitude outside -90..90']) + ([] if -180 <= lon <= 180 else ['longitude outside -180..180'])
    if not bad:
        return [lat, lon], None
    problem = {'pota_pin': [lat, lon], 'why': '; '.join(bad)}
    if -90 <= lon <= 90 and -180 <= lat <= 180:
        problem['hint'] = 'the two numbers look swapped (a sign may be wrong too): not fixed here'
    return None, problem


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
                    'other_sources': len(r.get('other_sources') or []),
                    # 23 Nov (audit 3 S4): how many rows were added together. 27 Nov (audit section 2): 'outline_acres' is
                    # left out: it is the OLD key's outline, and the facts no longer depend on the old key (nothing read it)
                    'parts': r.get('parts') or 1}
    return out, os.path.basename(path)


# ------------------------------------------------------------------ size witness -------------------------------------
# Where an official size came from, so the key's matching knows whether it can count as a second, independent agreement.
#   same_record      read from a map layer the key already joined this park to (the record the name picked): never proof
#   other_layer      read from a different map layer than the ones the key joined: not proof (another layer is not a witness)
#   agency_document  read from the agency's own published list (spreadsheet, PDF, CSV, web table): proof
#   hand_copy        typed in by a person from the agency's figure: proof
#   unknown          can't tell (no address, or the key has no joined layer for the park to compare with)
# 27 Nov 2026 (audit section 2): the old key (v1) is no longer read, so this tool never writes same_record or other_layer
# itself any more: a size read from a map layer is 'unknown'. Not one size changes between proof and not proof (the audit
# recomputed all 1,422: a map-layer size never was proof). A keeper's own tag is still kept as the keeper gave it.
WITNESS_TAGS = ('same_record', 'other_layer', 'agency_document', 'hand_copy', 'unknown')
WITNESS_PROOF = ('agency_document', 'hand_copy')
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


# 27 Nov 2026 (audit section 2): read_key_layers (the old key's joined layers) is gone: nothing here reads the old key.
def witness(ref, row, key_layers=None):
    """(tag, why) for one official size. 27 Nov: run() always passes key_layers=None (the old key is not read); a caller
    that still passes {ref: set of layer addresses} gets the old same_record / other_layer answer (kept for the tests)."""
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
            return 'unknown', 'a map layer: not proof (the old key is no longer read to compare, 27 Nov)'
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
        # 23 Nov (owner 'Yes', audit 3 S2): a size the bot itself flagged (over 50x the outline, another official list more
        # than 10% off, one row for two parks ...) or a hand copy with no source page is kept and shown, but is not proof
        # (KPC-Links already refuses them, so the two repos now agree)
        # 27 Nov 2026 (audit section 2): 'over 50x the current outline' compares with the OLD key's outline: it no longer
        # refuses a size (7 good official sizes came back: US-0492 Washita NWR, US-0731, US-1566, US-1573, US-1596, US-1601,
        # US-7741). The flag is still kept and shown; v2 asks the record's own acres to be within 10% anyway. 'under 0.1 acres'
        # is NOT an outline flag (kpc_acres line 2399: the size itself is under 0.1 acres, US-4564 has 0.0): it still refuses.
        bad = [f for f in r.get('flags') or [] if re.match(r'(under 0\.1|over 20 million|same row matched to two parks'
                                                           r'|\d+ row\(s\) matched to two parks|another official list differs)', str(f))]
        no_src = t == 'hand_copy' and not re.match(r'^https?://\S+\.\S+', str(r.get('source_url') or ''))
        r['witness_counts'] = t in WITNESS_PROOF and not bad and not no_src
        if t in WITNESS_PROOF and not r['witness_counts']:
            r['witness_why'] = f"{why}; not counted as proof: " + ('the bot flagged it (' + bad[0] + ')' if bad else 'a hand copy with no source page')
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
# 27 Nov 2026 (audit F8, F16): extra folders to look in for the page reader's rules and kpc_link_ids.py (--tools; the PC
# button gives the PC page reader's scripts folder). Which one was used, or that none was found, goes into 'sources'.
TOOL_DIRS = []
LOADED = {}


def _load(name, defaults):
    """Import one helper tool from --tools folders first, then the usual places. -> module or False. Never fails the run;
    the file says which copy ran (LOADED)."""
    for d in TOOL_DIRS + [os.path.normpath(x) for x in defaults]:
        if os.path.isfile(os.path.join(d, name + '.py')):
            if d not in sys.path:
                sys.path.insert(0, d)
            try:
                mod = __import__(name)
                LOADED[name] = os.path.dirname(os.path.abspath(mod.__file__))
                return mod
            except Exception as e:  # noqa: BLE001
                LOADED[name] = f'could not be loaded from {d}: {type(e).__name__}'
                return False
    LOADED.setdefault(name, 'not found')
    return False


def _agree(nm, pota_name, others=None):
    """The reader's own name check (kpc_park_pages_rules.name_agreeing) on the saved heading and title; (None, None) when the
    reader's rules are not at hand or nothing agrees."""
    if _R[0] is None:
        _R[0] = _load('kpc_park_pages_rules', [os.path.join(HERE, '..', '..', '..'), HERE])
    if not _R[0] or not isinstance(nm, dict):
        return None, None
    try:
        return _R[0].name_agreeing(nm, pota_name, others)
    except Exception:  # noqa: BLE001
        return None, None


def _norm_name(s):
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', str(s or '').lower()).split())


def _others(area_names, own):
    """The other parks' names of the area (a name two parks share stays in: the page could be either's)."""
    k = _norm_name(own)
    return {n for n, c in area_names.items() if n and (n != k or c > 1)}


PAGE_FILES = []


def sha256_of(path):
    """27 Nov 2026 (audit F7): a file's fingerprint, so the next tool can tell exactly which input was used."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def size_of_page(s, page_url=''):
    """One page size. 27 Nov 2026 (the fixed PC page reader, 26 Nov: 'save the number as written, the unit as written'):
    besides acres, as, total and clean, the reader's unit, the words as written (only when they differ from 'as'), the two
    readings of a number a French page makes unclear, the other totals it disagrees with, and the page the figure came from
    (only when it is not the park's page). Empty ones are left out (the file has a 3 MB cap)."""
    out = {'acres': s.get('acres'), 'as': s.get('as'), 'total': s.get('total'), 'clean': s.get('clean')}
    if s.get('unit'):
        out['unit'] = str(s['unit'])[:20]
    if s.get('written') and str(s['written']) != str(s.get('as') or ''):
        out['written'] = str(s['written'])[:80]
    if isinstance(s.get('ambiguous'), dict):
        out['ambiguous'] = {'readings_acres': list(s['ambiguous'].get('readings_acres') or [])[:2]}
    if s.get('disagrees_with'):
        out['disagrees_with'] = [str(x)[:40] for x in _first(s['disagrees_with'], 2)]
    if s.get('source_url') and str(s['source_url']) != str(page_url or ''):
        out['source_url'] = str(s['source_url'])[:300]
    return out


def reader_extras(nm, pg):
    """27 Nov 2026: what the fixed PC page reader (26-27 Nov) writes and this file kept nothing of. Only when there is one.
      names           every name the page may call the park (title, headings, also-known-as, phrases): plain strings (name.names)
      name_set_aside  names the reader set aside as the site's own heading, a menu or a neighbour's name, and why
                      (name.set_aside, and name.offered rows that carry a reason)
      not_read        why the page was not read (the site rule's reason; for a robots.txt Disallow, the line)
      last_try        a failed later try, written BESIDE the facts kept from the earlier read (its date and reason)
      seen            the day the page was last found unchanged; browser: read after the page built itself
    Report data only: nothing here decides. names is written exactly as draft PR #201 writes it, so the two agree."""
    out = {}
    # 27 Nov 2026 (manager's review): plain strings, 12 at most, 110 letters each: the SAME shape draft PR #201 writes and the
    # key's page_names_land reads (kpc_match_checks: str(x) for x in page.names). A list of dicts would break that reader.
    names = [str(x.get('name') or '')[:110] for x in (nm.get('names') or []) if isinstance(x, dict) and str(x.get('name') or '').strip()][:12]
    if names:
        out['names'] = names
    aside, seen = [], set()
    for x in list(nm.get('set_aside') or []) + [o for o in nm.get('offered') or [] if isinstance(o, dict) and o.get('set_aside')]:
        if not isinstance(x, dict):
            continue
        n = str(x.get('name') or '').strip()
        why = x.get('why') or (x.get('set_aside') if isinstance(x.get('set_aside'), str) else '') or x.get('rule') or ''
        if n and n.lower() not in seen:
            seen.add(n.lower())
            aside.append({'name': n[:80], 'from': str(x.get('from') or '')[:20], 'why': str(why)[:100]})
    if aside:
        out['name_set_aside'] = aside[:3]
    for k in ('not_read', 'last_try'):
        v = pg.get(k)
        if isinstance(v, dict) and (v.get('reason') or v.get('why')):
            out[k] = {kk: (str(v[kk])[:120] if isinstance(v[kk], str) else v[kk]) for kk in ('reason', 'status', 'date', 'line') if v.get(kk) not in (None, '')}
    if pg.get('seen'):
        out['seen'] = pg['seen']
    if pg.get('browser'):
        out['browser'] = True
    return out


# 27 Nov 2026 (audit F1): a page size is checked against its own words. The units are v2's own table (us-key-v2-rules.json
# size_text_units, owner 26 Nov 9:53 PM: hectares and km2 become acres). The page reader stored 29 sizes written in square
# kilometres as that many acres (CA-0062 Nahanni '30,000 square kilometers' = 30,000 ac; true 7.4 million).
SIZE_WORDS = [(re.compile(r'km2|km²|\bsq\.? ?km\b|square kilomet(?:er|re)s?', re.I), 'km2', 247.105),
              (re.compile(r'square miles?|\bsq\.? ?mi\b|mi²', re.I), 'mi2', 640.0),
              (re.compile(r'\bhectares?\b|\bha\b', re.I), 'ha', 2.47105),
              (re.compile(r'\bacres?\b|\bac\b', re.I), 'acres', 1.0)]
SIZE_WORDS_TOL = 0.05


def acres_from_words(text):
    """'30,000 square kilometers' -> (7413150.0, 'km2'); (None, None) when the words hold no number, two numbers, or no unit
    (the same reading as v2's size_from_text)."""
    t = str(text or '').lower().replace(' ', ' ')
    nums = re.findall(r'\d[\d,]*(?:\.\d+)?', re.sub(r'(km|mi)\s*[2²]', r'\1', t))
    if len(nums) != 1:
        return None, None
    x = float(nums[0].replace(',', '')) * (1e6 if re.search(r'\bmillion\b', t) else 1.0)
    for rx, unit, f in SIZE_WORDS:
        if rx.search(t):
            return x * f, unit
    return None, None


def check_page_sizes(pages):
    """27 Nov 2026 (audit F1): acres that disagree with the page's own words (more than 5%, and more than half an acre) are
    replaced by the words' acres; the stored figure stays as 'acres_read'. Square kilometres read as acres is a known slip of
    the reader's converter: the total / clean marks stand. Any other disagreement is never a clean total.
    -> Counter of what was changed."""
    c = collections.Counter()
    for ref, pg in pages.items():
        for s in pg.get('sizes') or []:
            ac, unit = acres_from_words(s.get('as'))
            st = s.get('acres')
            if ac is None or not isinstance(st, (int, float)) or isinstance(st, bool):
                continue
            if abs(ac - st) <= max(SIZE_WORDS_TOL * max(ac, st), 0.5):
                continue
            s['acres_read'], s['acres'] = st, round(ac, 1)
            if unit == 'km2':
                s['fixed'] = 'square kilometres were stored as acres: converted (x 247.105, 27 Nov)'
                c['page sizes in square kilometres converted to acres'] += 1
            else:
                s['clean'] = False
                s['fixed'] = "the stored acres did not agree with the page's words: the words are used, and it is not a clean total (27 Nov)"
                c["page sizes whose acres did not agree with the page's words (not clean now)"] += 1
    return c


def clean_nps_codes(pages):
    """27 Nov 2026 (audit F12): page.nps_code is a National Park Service unit code only on an nps.gov page. The reader's
    'family code' on fws.gov is a refuge's web name ('hakalau-forest'), so it is left out there. -> how many were left out."""
    n = 0
    for pg in pages.values():
        if pg.get('nps_code') and not re.search(r'(?:^|\.)nps\.gov$', str(pg.get('host') or '').lower()):
            pg['nps_code'] = None
            n += 1
    return n


def read_pages(folder):
    """park-pages/facts/<area>.json -> {ref: page fact}. Only the facts a later rule may weigh; quotes are kept short."""
    out, areas = {}, []
    PAGE_FILES[:] = []      # 27 Nov: emptied first, so a run with no page folder never shows an earlier run's files
    if not folder or not os.path.isdir(folder):
        return out, areas
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        areas.append(d.get('area') or os.path.basename(path)[:-5])
        PAGE_FILES.append({'file': os.path.basename(path), 'area': areas[-1], 'sha256': sha256_of(path)})   # 27 Nov (F7)
        # 23 Nov (ruling W-G5): the area's park names, so 'same words, another kind' never takes another park's own name
        area_names = collections.Counter(_norm_name(((q or {}).get('pota') or {}).get('name')) for q in (d.get('parks') or {}).values() if isinstance(q, dict))
        for ref, p in (d.get('parks') or {}).items():
            if not REF.match(str(ref)) or not isinstance(p, dict):
                continue
            pg, own, nm = p.get('page') or {}, p.get('own_page') or {}, p.get('name') or {}
            loc, man, st = p.get('location') or {}, p.get('manager') or {}, p.get('status_words') or {}
            pota = p.get('pota') or {}
            oth = _others(area_names, pota.get('name'))
            ag = _agree(nm, pota.get('name'), oth)
            vs = ag[1] or nm.get('vs_pota')
            if not ag[1] and vs == 'same-core' and _norm_name(nm.get('best') or nm.get('heading') or nm.get('title')) in oth:
                vs = 'differs'      # 23 Nov: the page carries ANOTHER park's own name: that park's page
            out[ref] = {
                '_pota': {'area': p.get('area') or d.get('area'), 'name': pota.get('name'), 'type': pota.get('type'),
                          'pin': pota.get('pin'), 'link': pota.get('link')},
                '_file': areas[-1],
                'read': pg.get('read'), 'url': pg.get('final_url') or (p.get('asked') or {}).get('url'), 'status': pg.get('status'),
                'kind': pg.get('kind'), 'host': pg.get('final_host') or pg.get('host'), 'nps_code': pg.get('nps_code'),
                'own_page': own.get('is'), 'unofficial': bool(p.get('unofficial')),
                # 22 Nov 2026 (owner: "not doing a good job of confirming park names"): a heading that was site chrome hid the
                # name; the part of the heading / title that agrees with POTA's name is used when there is one
                'name_vs_pota': vs,
                'name_on_page': (ag[0] or nm.get('heading') or nm.get('title') or '')[:120],
                'sizes': [size_of_page(s, pg.get('final_url') or (p.get('asked') or {}).get('url'))
                          for s in _first(p.get('sizes'), 3) if isinstance(s, dict)],
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
                # 23 Nov 5:24 AM (owner: "I dont want key bots to do internet stuff"): the named county's middle point and size,
                # looked up on the PC by the converter; the key only reads it
                'county_areas': [{'name': str(c.get('name') or '')[:40], 'lat': c.get('lat'), 'lon': c.get('lon'), 'radius_km': c.get('radius_km')}
                                 for c in _first(loc.get('county_areas'), 4) if isinstance(c, dict) and c.get('lat') is not None and c.get('radius_km')],
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
                'map_names': map_names_of(p.get('maps')) if own.get('is') == 'own' and not p.get('unofficial') else [],
                'maps': [{'url': str(m.get('url') or '')[:300], 'kind': m.get('kind'), 'names_park': bool(m.get('names_park'))}
                         for m in _first(p.get('maps'), 6) if isinstance(m, dict) and str(m.get('url') or '').startswith('https://')],
            }
            # 23 Nov 2026 (rule sheet L, the own-page finder): the park's OWN page found on its agency's site when POTA lists no
            # link, a dead one or the agency's front page. 'sure' = read as the park's page above; 'unsure' = for a person only
            fd = p.get('found') if isinstance(p.get('found'), dict) else None
            if fd and fd.get('level') in ('sure', 'unsure', 'no'):
                out[ref]['found'] = {'url': str(fd.get('url') or '')[:300], 'level': fd.get('level'), 'how': str(fd.get('how') or '')[:20],
                                     'why': str(fd.get('why') or '')[:160], 'for': str(fd.get('for') or '')[:30], 'date': fd.get('date'),
                                     'was': str(fd.get('was') or ((p.get('asked') or {}).get('was')) or '')[:300]}
            out[ref].update(reader_extras(nm, pg))
    SHARED_POINTS[0] = drop_shared_points(out)
    SHARED_MAP_NAMES[0] = drop_shared_map_names(out)
    return out, areas


# 23 Nov 2026 (owner 12:51 AM 'Yes'; rule sheet W5 MAP-LINK NAME): the park's own page links the agency's OWN map viewer and
# the link itself names the place (Wisconsin DNR: dnrmaps.wi.gov/H5/?Viewer=Public_Access_Lands&ID=MACK WILDLIFE AREA;
# Massachusetts and Indiana: ...?find=<name>; Colorado: ...&value=<name>). That name is the one the agency's map uses.
# Never a street-map site, a booking site or a document; never the id of the map itself (32 letters and digits); and a
# value that 3 or more parks' links carry is a map of everything, not this park's name.
MAP_NAME_PARAMS = ('id', 'find', 'value', 'parkname', 'name', 'lbl', 'query', 'search', 'feature', 'unit', 'property')
MAP_HOST_NO = re.compile(r'google\.|goo\.gl|bing\.com|openstreetmap|apple\.com|mapquest|reserveamerica|recreation\.gov|parcsnbparks|adobe\.com', re.I)
MAP_PARAM_RX = re.compile(r'[?&#;]([A-Za-z_]{1,12})=([^&#]{3,160})')
SHARED_MAP_NAME_PARKS = 3
SHARED_MAP_NAMES = [0]


def map_names_of(maps):
    import urllib.parse
    out = []
    for m in maps or []:
        u = str((m or {}).get('url') or '') if isinstance(m, dict) else ''
        u = u.replace('&amp;', '&')
        if not u.startswith('https://') or MAP_HOST_NO.search(u) or re.search(r'\.pdf(\?|#|$)', u, re.I):
            continue
        host = urllib.parse.urlparse(u).netloc.lower()
        for mm in MAP_PARAM_RX.finditer(u):
            param = mm.group(1).lower()
            if param not in MAP_NAME_PARAMS:
                continue
            v = ' '.join(urllib.parse.unquote_plus(mm.group(2)).split())
            if param == 'query' and ',' in v:
                v = v.split(',')[-1].strip()            # ArcGIS: query=<layer>,<field>,<value>
            if (re.fullmatch(r'[0-9a-fA-F-]{20,}', v) or re.match(r'(?i)https?:|urn:', v) or len(re.findall(r'[A-Za-z]', v)) < 4
                    or len(v) > 80 or v.lower() in ('true', 'false', 'null', 'none', 'dark', 'light')):
                continue
            if not any(x['name'].lower() == v.lower() for x in out):
                out.append({'name': v, 'host': host, 'param': param})
    return out[:3]


def drop_shared_map_names(pages):
    seen = {}
    for ref, f in pages.items():
        for m in f.get('map_names') or []:
            seen.setdefault((m['host'], m['param'], m['name'].lower()), set()).add(ref)
    bad = {k for k, refs in seen.items() if len(refs) >= SHARED_MAP_NAME_PARKS}
    n = 0
    for f in pages.values():
        keep = [m for m in f.get('map_names') or [] if (m['host'], m['param'], m['name'].lower()) not in bad]
        n += len(f.get('map_names') or []) - len(keep)
        f['map_names'] = keep
    return n


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


PAGE_LINK_FROM = "POTA's link, as the page reader saved it (27 Nov: the park is not in data/parkinfo, so kpc_link_ids never saw it)"


def add_page_links(links, pages):
    """27 Nov 2026 (audit F5): kpc_link_ids reads only data/parkinfo, and Kentucky is not in it (183 parks, no link row). A
    park the page reader has and link-ids.csv has not gets its row from POTA's own link as the reader saved it (pota.link),
    read by kpc_link_ids' own read_link with its own rules: 'usable' = the park's own page, a known id, no other park with the
    same id, the site in the park's state. An id that a listed park carries too makes BOTH not usable.
    POTA lists no link: nothing (a page the official-links finder found is not turned into an id here: owner's grey area).
    -> Counter (or {'tool not found': n} when kpc_link_ids.py is not at hand)."""
    c = collections.Counter()
    todo = {ref: pg['_pota'] for ref, pg in pages.items() if ref not in links and str(((pg.get('_pota') or {}).get('link')) or '').strip()}
    if not todo:
        return c
    LT = _load('kpc_link_ids', [os.path.join(HERE, '..', 'kpc_link_ids'), HERE])
    if not LT:
        c['parks whose link could not be read: kpc_link_ids.py not found'] = len(todo)
        return c
    new = {}
    for ref, po in todo.items():
        area = str(po.get('area') or '')
        new[ref] = LT.read_link(po.get('link'), po.get('name') or '', po.get('type') or '', area, [area])
    shared = collections.Counter(r['norm'] for r in new.values() if r.get('norm'))
    ids = collections.Counter((r['id_kind'], r['id_value']) for r in new.values() if r.get('id_grade') == 'known')
    for r in links.values():
        if r.get('id_is') == 'known':
            ids[(r.get('id_kind'), r.get('id_value'))] += 1
    for ref, r in new.items():
        sb = shared[r['norm']] if r.get('norm') else 0
        page = r.get('page') or ''
        if sb > 1 and page in ('own page', 'page not confirmed', 'document', 'home page'):
            page = 'shared link'
        known = r.get('id_grade') == 'known'
        isb = ids[(r['id_kind'], r['id_value'])] if known else 0
        usable = page == 'own page' and known and isb == 1 and not str(r.get('state_check') or '').startswith('OTHER')
        links[ref] = {'website': r.get('host') or None, 'agency': r.get('agency') or None, 'site': r.get('site') or None,
                      'page_kind': page or None, 'shared_by': sb or None, 'id_kind': r.get('id_kind') or None,
                      'id_value': r.get('id_value') or None, 'id_is': r.get('id_grade') or None, 'id_shared_by': isb or None,
                      'usable': usable, 'web_name': r.get('web_name') or None, 'name_match': r.get('name_match') or None,
                      'web_kind': r.get('web_kind') or None, 'kind_check': r.get('kind_check') or None,
                      'state_check': r.get('state_check') or None, 'from': PAGE_LINK_FROM}
        c["link row made from POTA's link the page reader saved"] += 1
        c['  of them with a usable link id'] += usable
    for ref, r in links.items():
        if r.get('from') != PAGE_LINK_FROM and r.get('usable') and ids[(r.get('id_kind'), r.get('id_value'))] > 1:
            r['usable'], r['id_shared_by'] = False, ids[(r.get('id_kind'), r.get('id_value'))]
            c['listed park no longer usable: a page-reader park has the same id'] += 1
    return c


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
            ap = alt.get('pin') if isinstance(alt.get('pin'), (list, tuple)) and len(alt.get('pin')) >= 2 else [None, None]
            p['pin'], prob = pin_check(ap[0], ap[1])          # 27 Nov (F2): the same pin check as data/parkinfo's
            if prob:
                p['pin_problem'] = prob
            c['park taken from the page reader\'s POTA copy (not in data/parkinfo)'] += 1
        row = {'area': p['area'] if p else None, 'name': p['name'] if p else None,
               'type': p['type'] if p else None, 'pin': p['pin'] if p else None}
        if p and p.get('pin_problem'):
            row['pin_problem'] = p['pin_problem']      # 27 Nov 2026 (audit F2): POTA's numbers and why they are no pin
            c['pin problem: ' + ('0,0 (no pin)' if p['pin_problem']['why'].startswith('0,0') else 'a place that cannot be')] += 1
        if not p:
            row['not_on_list'] = True
            c['facts for a park not on the POTA list'] += 1
        have = []
        if ref in sizes:
            row['size'] = sizes[ref]; have.append('size')
        if ref in pages:
            row['page'] = {k: v for k, v in pages[ref].items() if not k.startswith('_')}; have.append('page')   # 27 Nov: _pota, _file
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
        if pg.get('map_names'):
            c["page's map link names the place"] += 1
        if pg.get('offsets'):
            c['page says how far and which way from a town'] += 1
        if pg.get('counties'):
            c['page names its county'] += 1
        if pg.get('county_areas'):
            c["page's county has its middle point and size"] += 1
        if pg.get('near'):
            c['approximate point from the page directions'] += 1
        if pg.get('name_vs_pota') in ('same', 'same-core'):
            c["page carries the park's own name"] += 1
        if (pg.get('found') or {}).get('level'):
            c[f"own page looked for on the agency site: {pg['found']['level']}"] += 1
        if ref in sizes and pg.get('sizes'):
            c['official size AND a page size'] += 1
    if SHARED_POINTS[0]:
        c["points taken out: the same point on 3 or more parks' pages of one site"] = SHARED_POINTS[0]
    return rows, c


# ------------------------------------------------------------------ freshness (27 Nov 2026, audit F7, F8) ------------
SHRINK = 0.05        # an input that lost more than 5% (and more than SHRINK_MIN parks) since the previous file stops the run
SHRINK_MIN = 2
DERIVED_SIZE_KEYS = ('witness', 'witness_why', 'witness_counts', 'outline_acres')
MISSING_WORDS = {'acres': 'the official sizes (acres.json)', 'link_ids': 'the link ids (link-ids.csv)',
                 'page_facts': 'the page facts', 'crosswalk': 'the agency lists (crosswalk)'}


def load_previous(path):
    """The park facts file this run replaces (.json or .json.gz). -> (doc, info) or (None, None)."""
    if not path or not os.path.isfile(path):
        return None, None
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt', encoding='utf-8') as f:
        doc = json.load(f)
    return doc, {'file': os.path.basename(path), 'made': doc.get('made'), 'tool': doc.get('tool'), 'sha256': sha256_of(path),
                 'newest_input': doc.get('newest_input')}


def _carried(prev):
    return f"carried from the previous park facts (made {prev.get('made')})"


def carry_sizes(prev):
    """--carry-missing with no size file: the previous file's sizes, as they were read (the witness is tagged again here)."""
    out = {}
    for ref, row in (prev.get('parks') or {}).items():
        s = row.get('size')
        if isinstance(s, dict) and s.get('acres') is not None:
            out[ref] = dict({k: v for k, v in s.items() if k not in DERIVED_SIZE_KEYS}, carried=_carried(prev))
            if out[ref].get('from') == 'keeper' and s.get('witness') in WITNESS_TAGS:
                out[ref]['witness'] = s['witness']
    return out


def carry_links(prev):
    """--carry-missing with no link-ids.csv: the previous file's link rows (their map ties are made again below)."""
    return {ref: dict({k: v for k, v in row['link'].items() if k != 'map_tie'}, carried=_carried(prev))
            for ref, row in (prev.get('parks') or {}).items() if isinstance(row.get('link'), dict)}


def carry_ties(prev):
    """--carry-missing with no crosswalk folder: the previous file's agency-list ties, by (link kind, web id)."""
    ties = {}
    for row in (prev.get('parks') or {}).values():
        lk = row.get('link') or {}
        if isinstance(lk.get('map_tie'), dict) and lk.get('id_kind') and lk.get('id_value'):
            ties[(str(lk['id_kind']).strip().lower(), str(lk['id_value']).strip().upper())] = dict(lk['map_tie'])
    return ties


def _garbled(t):
    t = str(t or '')
    return len(t) >= 4 and sum(1 for ch in t if ord(ch) > 127 or ch == '�' or (ord(ch) < 32 and ch not in '\t\n')) / len(t) > 0.25


def read_strength(pg):
    """The upload job's rule (KPC-Data kpc_pc_upload.read_strength), on this file's page row: 3 = the park's own page, really
    read, name clean; 2 = a real read (html or pdf), name clean; 1 = a read that got nothing, or a garbled name; 0 = none."""
    kind = (pg or {}).get('kind')
    if not kind:
        return 0
    if kind not in ('html', 'pdf') or _garbled(pg.get('name_on_page')):
        return 1
    return 3 if pg.get('own_page') == 'own' else 2


def better_read(old, new):
    """kpc_pc_upload.better_read (owner 22 Nov 'Yeah', 23 Nov 'fix everything'): the new read wins unless it is weaker; as
    strong = the later 'read' date wins, a tie goes to the new one; an own-page finder that took back a SURE find wins."""
    nf, of = (new or {}).get('found') or {}, (old or {}).get('found') or {}
    newer = str((new or {}).get('read') or '') >= str((old or {}).get('read') or '')
    if nf.get('level') == 'unsure' and of.get('level') == 'sure':
        if str(nf.get('url') or '').rstrip('/').lower() == str(of.get('url') or '').rstrip('/').lower() and newer and read_strength(new) >= 2:
            return True
    so, sn = read_strength(old), read_strength(new)
    return sn > so if sn != so else newer


def merge_previous_pages(pages, prev):
    """--carry-missing (the PC, which has only its own reads): a park the page folder lacks keeps the previous file's page
    row; a park in both keeps the better or newer read (better_read). -> Counter."""
    c = collections.Counter()
    for ref, row in (prev.get('parks') or {}).items():
        old = row.get('page')
        if not isinstance(old, dict):
            continue
        if ref in pages and better_read(old, pages[ref]):
            c['page read here kept (better or newer than the previous file)'] += 1
            continue
        c['page row carried from the previous file' + (' (its read is better or newer)' if ref in pages else '')] += 1
        pin = row.get('pin') or (row.get('pin_problem') or {}).get('pota_pin')
        pages[ref] = dict(old, carried=_carried(prev), _file=None,
                          _pota={'area': row.get('area'), 'name': row.get('name'), 'type': row.get('type'), 'pin': pin, 'link': None})
    return c


def _dates(xs):
    xs = sorted(str(x)[:10] for x in xs if re.match(r'^\d{4}-\d\d-\d\d', str(x or '')))
    return (xs[0], xs[-1]) if xs else (None, None)


def input_info(path, n=None, dates=()):
    """One input file: its name, fingerprint, size, parks and the oldest / newest read date inside it."""
    if not path or not os.path.isfile(path):
        return None
    lo, hi = _dates(dates)
    return {'file': os.path.basename(path), 'sha256': sha256_of(path), 'bytes': os.path.getsize(path), 'parks': n,
            'oldest_read': lo, 'newest_read': hi}


def folder_info(folder, pattern='*.json'):
    files = sorted(glob.glob(os.path.join(folder or '', pattern))) if folder and os.path.isdir(folder) else []
    h = hashlib.sha256()
    for p in files:
        h.update(os.path.basename(p).encode() + b'\0' + sha256_of(p).encode() + b'\n')
    return {'files': len(files), 'sha256': h.hexdigest() if files else None}


def shape_counts(rows):
    """What the shrink check compares: parks, parks with a page per area, sizes, usable link ids, agency-list ties."""
    c = collections.Counter()
    for r in rows.values():
        c['parks'] += 1
        if r.get('page'):
            c['parks with a page, ' + str(r.get('area') or '?')] += 1
        if r.get('size'):
            c['parks with an official size'] += 1
        lk = r.get('link') or {}
        if lk.get('usable'):
            c['parks with a usable link id'] += 1
        if lk.get('map_tie'):
            c['parks tied by an agency list'] += 1
    return c


def compare_previous(rows, prev):
    """-> (block for the file, problems). A problem = something lost more than 5% and more than 2 parks."""
    before, after = shape_counts(prev.get('parks') or {}), shape_counts(rows)
    changed, problems = {}, []
    for k in sorted(set(before) | set(after)):
        b, n = before.get(k, 0), after.get(k, 0)
        if b != n:
            changed[k] = [b, n]
        if b - n > max(SHRINK * b, SHRINK_MIN):
            problems.append(f'{k}: {b:,} before, {n:,} now')
    return {'before_after': changed, 'shrank': problems}, problems


def run(a):
    TOOL_DIRS[:] = [os.path.abspath(d) for d in getattr(a, 'tools', None) or []]
    parks = read_parkinfo(a.parkinfo)
    if not parks:
        raise SystemExit(f'STOP: no US or Canadian parks read from {a.parkinfo}')
    # 27 Nov 2026 (audit section 2): the old key is never read. --key / --layers are still taken, so a workflow that passes
    # them keeps running (it cannot fail on an unknown flag), but nothing is read from them and the file says so.
    old_key = 'not read (27 Nov 2026: the park facts no longer depend on the old key)'
    if getattr(a, 'key', None) or getattr(a, 'layers', None):
        old_key += '; --key / --layers were given and ignored: drop them from the workflow'
        say('NOTE: --key / --layers are no longer read (27 Nov 2026). Nothing was read from them.')
    prev, prev_info = load_previous(getattr(a, 'previous', None))
    if getattr(a, 'previous', None) and not prev:
        raise SystemExit(f'STOP: the previous park facts file was not found: {a.previous}')
    carry = bool(getattr(a, 'carry_missing', False))
    if carry and not prev:
        raise SystemExit('STOP: --carry-missing needs --previous (the file whose facts are carried)')
    asizes, sname = read_acres(a.acres)
    ksizes, kname = read_keeper_sizes(getattr(a, 'keeper_sizes', None))
    sizes = merge_sizes(ksizes, asizes)
    carried = collections.Counter()
    if carry and not sname and not kname:
        sizes = carry_sizes(prev)
        carried['official sizes'] = len(sizes)
    pages, pareas = read_pages(a.pages)
    page_files = list(PAGE_FILES)
    if carry:
        carried.update({k: v for k, v in merge_previous_pages(pages, prev).items()})
    fixes = check_page_sizes(pages)
    fixes['nps_code left out: not an nps.gov page'] = clean_nps_codes(pages)
    links, lname = read_links(a.links)
    n_link_file = len(links)
    if carry and not lname:
        links = carry_links(prev)
        carried['link rows'] = len(links)
    ky = add_page_links(links, pages)
    ties, xfiles = read_crosswalk(getattr(a, 'crosswalk', None))
    if carry and not xfiles:
        ties = carry_ties(prev)
        carried['agency-list ties'] = len(ties)
    tied = add_map_ties(links, ties)
    tag_sizes(sizes, None)
    rows, c = combine(parks, sizes, pages, links)
    for r in sizes.values():
        c['size witness: ' + r['witness']] += 1
        c['size from: ' + r['from']] += 1
    for k, v in list(fixes.items()) + list(ky.items()):
        if v:
            c[k] = v
    made = a.today or datetime.date.today().isoformat()
    # 27 Nov 2026 (audit F7): how new each input is, so the next tool (and the owner) can tell the file has the newest
    page_rows = collections.defaultdict(list)
    for ref, pg in pages.items():
        page_rows[pg.get('_file')].append(pg.get('read'))
    inputs = {
        'parks_list': dict(folder_info(a.parkinfo), parks=len(parks)),
        'acres': input_info(a.acres, len(asizes), [r.get('read_date') for r in asizes.values()]),
        'keeper_sizes': input_info(getattr(a, 'keeper_sizes', None), len(ksizes), [r.get('read_date') for r in ksizes.values()]),
        'page_facts': [dict(f, parks=len(page_rows.get(f['area']) or []),
                            **dict(zip(('oldest_read', 'newest_read'), _dates(page_rows.get(f['area']) or []))))
                       for f in page_files],
        'link_ids': input_info(a.links, n_link_file),
        'crosswalk': [{'file': x['file'], 'rows': x.get('rows'), 'source_date': x.get('source_date'),
                       'sha256': sha256_of(os.path.join(a.crosswalk, x['file']))} for x in xfiles if x.get('rows')],
        'old_key': old_key,
        'previous': prev_info or 'not given: no shrink check',
        'carried_from_previous': dict(carried) if carry else 'no (only what this run read)',
    }
    missing = [k for k in ('acres', 'link_ids') if not inputs[k]] + ([] if page_files else ['page_facts']) + \
              ([] if inputs['crosswalk'] else ['crosswalk'])
    inputs['missing'] = missing
    newest = [x for x in [_dates(r.get('read_date') for r in sizes.values())[1]]     # every size used (carried ones too)
              + [f.get('newest_read') for f in inputs['page_facts']] + [x.get('source_date') for x in inputs['crosswalk']]
              + ([_dates(pg.get('read') for pg in pages.values())[1]] if carry else []) if x]
    compared, problems = compare_previous(rows, prev) if prev else (None, [])
    name_check = (f"the page reader's rules ({LOADED['kpc_park_pages_rules']})" if _R[0]
                  else "fallback: the page reader's rules were not found, so each page's saved name answer was kept"
                  + (f" ({LOADED.get('kpc_park_pages_rules')})" if LOADED.get('kpc_park_pages_rules') else ''))
    doc = {'made': made, 'tool': VERSION, 'newest_input': max(newest) if newest else None,
           'note': 'Facts collected by three bots, side by side. Nothing here ties a park to land; each source is one '
                   'agreement at most, and the size-witness rules decide what counts.',
           'sources': {'size': {'bot': 'the keeper first, the acreage bot (kpc_acres) as the fallback',
                                'keeper_file': kname, 'keeper_parks': len(ksizes), 'file': sname, 'parks': len(asizes),
                                'used': len(sizes)},
                       'page': {'bot': 'park page reader (kpc-park-pages)', 'areas_read': pareas, 'parks': len(pages),
                                'name_check': name_check},    # 27 Nov (audit F16): which name check ran
                       'link': {'bot': 'link IDs (kpc_link_ids)', 'file': lname, 'parks': len(links),
                                'from_page_reader': {'tool': LOADED.get('kpc_link_ids'), **dict(ky)} if ky else None},
                       'crosswalk': {'from': 'agency park lists (the keeper, kpc_agency_lists)', 'files': xfiles,
                                     'parks_tied': tied},
                       'parks_list': {'from': 'data/parkinfo (POTA)', 'parks': len(parks)}},
           'inputs': inputs, 'compared_with_previous': compared,
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
             f'  web link facts (link IDs): {len(links):,} parks', '',
             f"Newest input: {doc['newest_input'] or 'no dates in the inputs'}.",
             'Missing: ' + (', '.join(MISSING_WORDS.get(m, m) for m in missing) if missing else 'nothing') + '.']
    if carry:
        lines += ['Carried from the previous file (made ' + str(prev.get('made')) + '): '
                  + (', '.join(f'{v:,} {k}' for k, v in sorted(carried.items())) or 'nothing') + '.']
    if prev:
        lines += [f"Compared with the previous file (made {prev.get('made')}): "
                  + ('; '.join(f'{k} {b:,} -> {n:,}' for k, (b, n) in compared['before_after'].items()) or 'the same counts') + '.']
    lines += ['']
    lines += [f'  {v:>7,}  {k}' for k, v in sorted(c.items())]
    lines += ['', 'One file: park-facts.json, one row per park. Each fact keeps its source and date.',
              'It collects, it does not decide: nothing here ties a park to land or changes a key.']
    a._shrank = problems if not getattr(a, 'allow_shrink', False) else []
    if a._shrank:
        lines += ['', 'STOP: an input shrank since the previous file. Do not use this file:'] + ['  ' + p for p in problems]
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
    # 27 Nov 2026 (audit section 2): --key / --layers are still taken so an old workflow line does not fail, but are never read
    ap.add_argument('--key', action='append', help='no longer used (27 Nov 2026): the old key is not read; taken and ignored')
    ap.add_argument('--keeper-sizes', dest='keeper_sizes', help="the keeper's saved official sizes (taken before the acreage bot's)")
    ap.add_argument('--crosswalk', help="the keeper's agency park lists folder (agency-crosswalk/*.json)")
    ap.add_argument('--layers', help='no longer used (27 Nov 2026); taken and ignored')
    ap.add_argument('--out', default='park-facts', help='output folder (default ./park-facts)')
    # 27 Nov 2026 (audit F7, F8)
    ap.add_argument('--previous', help='the park facts file this run replaces (.json or .json.gz): the run stops (exit 3) when an '
                                       'input lost more than 5%% of its parks since then')
    ap.add_argument('--allow-shrink', dest='allow_shrink', action='store_true', help='write the file even when an input shrank')
    ap.add_argument('--carry-missing', dest='carry_missing', action='store_true',
                    help='with --previous: an input not given here (sizes, link ids, crosswalk) and a park with no page here keep '
                         "the previous file's facts, marked 'carried' (for the PC, which has only its own page reads)")
    ap.add_argument('--tools', action='append', help="a folder holding kpc_park_pages_rules.py and / or kpc_link_ids.py "
                                                     '(looked in first; may be given more than once)')
    ap.add_argument('--today', help=argparse.SUPPRESS)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.parkinfo:
        ap.error('give --parkinfo')
    run(a)
    if getattr(a, '_shrank', None):
        say('STOP: an input shrank since the previous file (see summary.txt). Exit 3: do not save this file.')
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
