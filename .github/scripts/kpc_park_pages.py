#!/usr/bin/env python3
"""Park page reader (hand-off 05). It reports. It never decides.

Commands: read, worklist, report, person-page, intake, kits, pc-kit, --selftest.
Every request goes through kpc_manners.Manners. This file does not fetch on its own.

Part 1 of the hand-off is `read` and `--selftest`. Later commands are named here and
filled in by the later parts; until then they say so and do no work.
"""
import argparse, datetime, json, os, pathlib, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_park_pages_rules as R  # noqa: E402
from kpc_manners import Manners, next_run, robots_block  # noqa: E402

JOB = 'KPC park page reader'


def load_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def park_row(row):
    """data/parkinfo row: [name, website, type, activation, access, lat, lon, activations, attempts, qsos]."""
    row = list(row or [])
    while len(row) < 10:
        row.append(None)
    return {'name': row[0] or '', 'website': row[1] or '', 'type': row[2] or '',
            'lat': row[5], 'lon': row[6], 'qsos': row[9] or 0}


def load_data(data):
    root = pathlib.Path(data)
    areas = {}
    for f in sorted((root / 'parkinfo').glob('*.json')) if (root / 'parkinfo').is_dir() else []:
        if f.name == 'index.json':
            continue
        doc = load_json(f, {})
        area = f.stem
        parks = {}
        for ref, row in (doc.get('parks') or {}).items():
            parks[ref] = park_row(row)
            parks[ref]['area'] = area
        if parks:
            areas[area] = parks
    web = load_json(root / 'parkinfo-web.json', {})
    if 'parks' in web:
        web = web['parks']
    docs, truth = {}, {}
    for folder, dest in (('docs', docs), ('truth', truth)):
        d = root / folder
        if not d.is_dir():
            continue
        for f in d.glob('*.json'):
            doc = load_json(f, {})
            for ref, row in (doc.get('parks') or {}).items():
                dest[ref] = row
    return areas, web, docs, truth


def choose_link(ref, row, web, docs):
    """POTA's link (first official host), else web, else the docs page. Other addresses are counted, not opened."""
    urls = R.split_urls(row.get('website'))
    official = [u for u in urls if R.official_host(u)]
    if official:
        return official[0], 'pota', max(0, len(urls) - 1)
    if urls:
        return urls[0], 'pota', max(0, len(urls) - 1)
    w = web.get(ref) or {}
    if isinstance(w, dict) and w.get('web'):
        return w['web'], 'web', 0
    d = docs.get(ref) or {}
    if isinstance(d, dict) and d.get('page'):
        return d['page'], 'docs', 0
    return '', 'none', 0


def norm_url(url):
    p = urllib.parse.urlparse(url or '')
    host = (p.netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    path = (p.path or '').rstrip('/')
    return host + path


class FixtureGetter:
    """Offline pages. A URL with no fixture is a 404 and is never a live request."""

    def __init__(self, manifest, root):
        self.pages = (manifest or {}).get('pages') or {}
        self.root = pathlib.Path(root)
        self.calls = []

    def links_for(self, url):
        rec = self._rec(url) or {}
        return [tuple(x) for x in (rec.get('links') or [])]

    def _rec(self, url):
        rec = self.pages.get(url)
        if rec is None:
            for k, v in self.pages.items():
                if norm_url(k) == norm_url(url):
                    return v
        return rec

    def get(self, url, rng=None):
        self.calls.append(url)
        rec = self._rec(url)
        if rec is None:
            # match without a trailing slash or a query
            for k, v in self.pages.items():
                if norm_url(k) == norm_url(url):
                    rec = v
                    break
        if rec is None:
            return 404, {}, b'', url
        if rec.get('file'):
            body = (self.root / rec['file']).read_bytes()
        else:
            body = (rec.get('body') or '').encode('utf-8')
        if rng:
            body = body[rng[0]:rng[1] + 1]
        headers = {'content-type': rec.get('type') or 'text/html'}
        return rec.get('status', 200), headers, body, rec.get('final') or url


class LiveGetter:
    def __init__(self, state):
        resting = state.get('hosts') if isinstance(state.get('hosts'), dict) else None
        self.M = Manners(JOB, resting)
        self.calls = []

    def get(self, url, rng=None):
        self.calls.append(url)
        return self.M.get(url, rng=rng)

    def resting(self):
        return self.M.resting()


def _refused_until(state, host, today):
    when = (state.get('refused') or {}).get(host)
    if not when:
        return False
    try:
        day = datetime.date.fromisoformat(when)
        now = datetime.date.fromisoformat(today)
    except ValueError:
        return False
    return (now - day).days < R.REFUSAL_DAYS


def _remember_refusal(state, host, today):
    state.setdefault('refused', {})[host] = today


def _kind_of_status(st, body_text, url, is_pdf=False):
    if isinstance(st, str) and robots_block(st) and not next_run(st):
        return 'refused'
    if st in (401, 403):
        return 'refused'
    if isinstance(st, str) and (next_run(st) or str(st).startswith('err')):
        return 'resting'
    if st in (404, 410):
        return 'dead'
    if isinstance(st, int) and st >= 500:
        return 'resting'
    if isinstance(st, str):
        return 'resting'
    if R.WALL.search(body_text or ''):
        return 'refused'
    if is_pdf or urllib.parse.urlparse(url or '').path.lower().endswith('.pdf'):
        return 'pdf'
    if R.script_shell(url):
        return 'script-built'
    # A real page is long. Under 400 characters of visible text, with no article, the page built itself.
    if body_text is not None and len(body_text.strip()) < 400:
        return 'script-built'
    return 'html'


def _shared_map(chosen):
    """url -> [refs]. A family page that names the place is still read; a list of 3 or more is not."""
    by = {}
    for ref, url in chosen.items():
        if not url:
            continue
        by.setdefault(norm_url(url), []).append(ref)
    return by


def _own_is(url, refs_here, area_parks, text, pota_name):
    if not url:
        return 'unknown', 'no address on file'
    if R.is_agency_home(url):
        return 'agency-home', 'the address has no path: it is the agency front page'
    if not R.official_host(url):
        return 'unofficial-host', f"the host {R.host_of(url)} is not an agency or its government"
    n = len(refs_here)
    if n >= 3 and not _family_names_all(text, refs_here, area_parks):
        return 'list', f'{n} parks of the area list this page and it does not name each of them'
    if n >= 2:
        return 'shared', f'{n} parks of the area list this page'
    return 'own', 'official host; only this park of the area lists the page'


def _family_names_all(text, refs, area_parks):
    """An NPS (or other family) page names them all when each park's core contains the heading core, or the text names each park."""
    if not text:
        return False
    heading = ''
    for line in text.splitlines():
        if R.kinds_in(line):
            heading = line
            break
    h_core = R.name_core(heading)
    if not h_core:
        return False
    for ref in refs:
        core = R.name_core((area_parks.get(ref) or {}).get('name'))
        if not core:
            return False
        if h_core == core or h_core in core or core in h_core:
            continue
        # a distinctive word of the park must appear
        bits = [w for w in core.split() if len(w) > 3]
        if not bits or not any(w in text.lower() for w in bits):
            return False
    return True


def read_parks(areas, web, docs, truth, getter, state, today, refs=None, areas_only=None,
               max_requests=1500, max_per_park=R.MAX_PER_PARK, max_parks=None, on_park=None):
    """Read every chosen park. Saves nothing itself. Returns {area: {ref: fact}} and the request count."""
    state.setdefault('hosts', {})
    state.setdefault('refused', {})
    state.setdefault('dead', {})
    state.setdefault('read', {})
    state.setdefault('fingerprints', {})
    out = {}
    requests = 0
    done = 0
    cache = {}  # norm url -> fetched page dict

    def budget_left():
        return requests < max_requests

    def fetch(url, rng=None):
        nonlocal requests
        if not url or not budget_left():
            return None
        host = R.host_of(url)
        if host and _refused_until(state, host, today):
            return {'url': url, 'final': url, 'status': 'refused', 'kind': 'refused', 'text': '', 'links': [],
                    'fingerprint': '', 'html': '', 'title': '', 'heading': '', 'skipped': 'refused'}
        key = norm_url(url) + (f'|rng{rng[0]}-{rng[1]}' if rng else '')
        if key in cache:
            return cache[key]
        requests += 1
        st, headers, body, final = getter.get(url, rng=rng)
        extra = getter.links_for(url) if hasattr(getter, 'links_for') else []
        vis = R.visible_of(body, headers, final or url, extra)
        kind = _kind_of_status(st, vis.get('text'), final or url, is_pdf=bool(vis.get('pdf')))
        if kind == 'refused':
            _remember_refusal(state, R.host_of(final or url) or host, today)
        if kind == 'dead':
            prev = (state.get('dead') or {}).get(url)
            twice = False
            if prev:
                try:
                    twice = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(prev)).days >= 7
                except ValueError:
                    twice = False
            else:
                state.setdefault('dead', {})[url] = today
            vis_dead = twice
        else:
            vis_dead = False
        if kind == 'resting' and isinstance(st, str) and st == 'rest':
            pass
        page = {'url': url, 'final': final or url, 'status': st, 'kind': kind, 'text': vis.get('text') or '',
                'html': vis.get('html') or '', 'title': vis.get('title') or '', 'heading': vis.get('heading') or '',
                'og': vis.get('og') or '', 'jsonld': vis.get('jsonld') or '', 'links': vis.get('links') or [],
                'fingerprint': R.fp_of(vis.get('text') or ''), 'dead_twice': vis_dead, 'family': R.family_of(final or url),
                'thin': len((vis.get('text') or '').strip()) < 400}
        cache[key] = page
        return page

    for area, parks in areas.items():
        if areas_only and area not in areas_only:
            continue
        chosen = {ref: choose_link(ref, row, web, docs)[0] for ref, row in parks.items()}
        groups = _shared_map(chosen)
        order = list(parks)
        if refs:
            order = [r for r in refs if r in parks] + [r for r in order if r not in refs]
        out.setdefault(area, {})
        for ref in order:
            if max_parks is not None and done >= max_parks:
                return out, requests
            if refs and ref not in refs:
                continue
            row = parks[ref]
            url, src, others = choose_link(ref, row, web, docs)
            if on_park:
                on_park(done + 1, ref)
            # a finished park with the same fingerprint is not read again
            prev = (state.get('read') or {}).get(ref)
            if prev and prev.get('url') == url and prev.get('fingerprint') and url:
                # still need the stored fact; the caller keeps the old file. Mark unchanged.
                out[area][ref] = {'ref': ref, 'unchanged': True, 'page': {'fingerprint': prev.get('fingerprint'),
                                 'kind': prev.get('kind'), 'read': today}, 'questions': []}
                # The caller merges the old fact. We do not fetch.
                done += 1
                continue
            pota = {'name': row['name'], 'type': row['type'], 'pin': [row['lat'], row['lon']],
                    'link': url, 'qsos': row['qsos']}
            asked = {'url': url, 'from': src, 'others_noted': others}
            if not url:
                fact = R.build_facts(ref, area, pota, parks, asked, [{'kind': 'none', 'status': None, 'text': '',
                                      'final': '', 'links': [], 'fingerprint': ''}], today, [], 'unknown',
                                     'no page on file', read_blocks=False)
                fact['page']['kind'] = 'none'
                fact['questions'] = R.questions_for(fact)
                out[area][ref] = fact
                state['read'][ref] = {'url': '', 'fingerprint': '', 'date': today, 'kind': 'none'}
                done += 1
                continue
            if R.is_agency_home(url):
                fact = R.build_facts(ref, area, pota, parks, asked, [{'kind': 'none', 'status': 'not-asked', 'text': '',
                                      'final': url, 'links': [], 'fingerprint': '', 'family': R.family_of(url)}],
                                     today, [], 'agency-home', 'the address has no path: it is the agency front page',
                                     read_blocks=False)
                fact['page']['kind'] = 'none'
                fact['page']['requests'] = 0
                fact['questions'] = R.questions_for(fact)
                fact['sizes'] = []
                out[area][ref] = fact
                state['read'][ref] = {'url': url, 'fingerprint': '', 'date': today, 'kind': 'none'}
                done += 1
                continue
            if not budget_left():
                return out, requests
            main = fetch(url)
            if main is None:
                return out, requests
            pages = [main]
            used = 1
            kind = main.get('kind')
            text = main.get('text') or ''
            mates = [r for r in groups.get(norm_url(url), []) if r != ref]
            own_is, own_why = _own_is(url, groups.get(norm_url(url), [ref]), parks, text, row['name'])
            read_blocks = own_is not in ('agency-home', 'list') and kind not in ('refused', 'resting', 'dead', 'script-built')
            fam = main.get('family') or {}
            # one facts page, one directions page, one map. Never past max_per_park.
            if read_blocks and used < max_per_park and budget_left():
                extra = _extra_urls(url, main, fam)
                for eu, role in extra:
                    if used >= max_per_park or not budget_left():
                        break
                    if role == 'map':
                        got = fetch(eu, rng=(0, R.PDF_FIRST - 1))
                    else:
                        got = fetch(eu)
                    used += 1
                    if got is None:
                        break
                    if got.get('kind') in ('html', 'pdf') and (got.get('text') or '').strip():
                        got = dict(got)
                        got['role'] = role
                        pages.append(got)
                    elif role == 'facts' and got.get('kind') == 'dead':
                        continue
            if kind in ('refused', 'resting', 'dead', 'script-built'):
                read_blocks = False
            fact = R.build_facts(ref, area, pota, parks, asked, pages, today, mates, own_is, own_why, read_blocks=read_blocks)
            fact['page']['requests'] = used if main.get('skipped') != 'refused' else 0
            fact['page']['kind'] = kind if kind != 'html' or not main.get('pdf') else 'pdf'
            if main.get('kind') == 'pdf':
                fact['page']['kind'] = 'pdf'
            # a list page: nothing was read
            if own_is == 'list':
                fact['sizes'] = []
                fact['inside_of'] = []
                fact['location'] = R._blank_location()
                fact['name']['best'] = None
                fact['questions'] = R.questions_for(fact)
            fact['questions'] = R.questions_for(fact)
            drafts = R.evidence_drafts(fact)
            fact['evidence_draft'] = drafts[0] if drafts else None
            fact['evidence_drafts'] = drafts
            out[area][ref] = fact
            state['read'][ref] = {'url': url, 'fingerprint': main.get('fingerprint') or '', 'date': today,
                                  'kind': fact['page']['kind'], 'final': main.get('final')}
            if main.get('fingerprint'):
                state['fingerprints'][norm_url(url)] = main.get('fingerprint')
            done += 1
    if isinstance(getter, LiveGetter):
        state['hosts'] = getter.resting()
    return out, requests


def _extra_urls(url, main, fam):
    """At most the facts page, a directions page, and one map that names the park. In that order."""
    out = []
    fid = (fam or {}).get('id')
    if fid == 'nps' and (fam or {}).get('code'):
        for u in R.nps_facts_urls(fam['code']):
            out.append((u, 'facts'))
            break  # the second (basic info) is fetched only when the first comes back dead; see caller loop
        # The caller stops on a good facts page. We pass statistics only; basic info is added if we detect a miss.
        # Both are listed; the caller fetches the next only while the previous facts page was dead. Handled below.
        out = [(R.nps_facts_urls(fam['code'])[0], 'facts')]
    elif fid == 'fws' and (fam or {}).get('code'):
        origin = urllib.parse.urlunsplit(urllib.parse.urlparse(url)._replace(path='', query='', fragment=''))
        # origin with scheme and host
        p = urllib.parse.urlparse(url)
        origin = f'{p.scheme}://{p.netloc}'
        facts = R.fws_facts_urls(origin, fam['code'])
        if facts:
            out.append((facts[0], 'facts'))
    elif fid == 'usfs':
        for link, text in main.get('links') or []:
            if 'about-area' in (link or '') or 'about the forest' in (text or '').lower():
                out.append((link, 'facts'))
                break
    # directions page only when this page has none of its own
    if not R._section(main.get('text') or '', {'directions', 'getting here', 'how to get there', 'driving directions'}):
        for link, text in main.get('links') or []:
            if re.search(r'direction|getting here|how to get there', (text or '') + ' ' + link, re.I):
                out.append((link, 'directions'))
                break
    # one map document that names the park. Script apps are not opened.
    for link, text in main.get('links') or []:
        if R.script_shell(link):
            continue
        row = R.classify_link(link, text, '', R.host_of(url))
        if not row or row['kind'] not in ('pdf', 'image', 'gis'):
            continue
        names, _unit = R.names_park_link(link, text, '')
        # names_park needs the park name; the caller filters. Open the first pdf that map_score accepts.
        if row['score'] >= 0 and row['kind'] == 'pdf':
            out.append((link, 'map'))
            break
    return out


def write_facts(out_dir, facts_by_area):
    root = pathlib.Path(out_dir)
    for area, parks in facts_by_area.items():
        save_json(root / 'facts' / f'{area}.json', {'area': area, 'reader': R.READER, 'parks': parks})


def merge_unchanged(out_dir, facts_by_area):
    """A park marked unchanged keeps the fact already on disk."""
    root = pathlib.Path(out_dir)
    for area, parks in facts_by_area.items():
        path = root / 'facts' / f'{area}.json'
        old = load_json(path, {}).get('parks') or {}
        for ref, fact in list(parks.items()):
            if fact.get('unchanged') and ref in old:
                kept = old[ref]
                page = dict(kept.get('page') or {})
                page['seen'] = (fact.get('page') or {}).get('read')
                kept = dict(kept)
                kept['page'] = page
                parks[ref] = kept


def cmd_read(args):
    areas, web, docs, truth = load_data(args.data)
    if not areas:
        print('No stored parks. Nothing was read.')
        return 0
    state = load_json(args.state, {}) if args.state and pathlib.Path(args.state).is_file() else {}
    today = args.today or datetime.date.today().isoformat()
    if args.fixtures:
        manifest = load_json(args.fixtures, {})
        getter = FixtureGetter(manifest, pathlib.Path(args.fixtures).parent)
    elif os.environ.get('KPC_NO_NET') == '1':
        print('No fixtures and the network is closed. Nothing was read.')
        return 0
    else:
        getter = LiveGetter(state)
    refs = None
    if args.refs:
        refs = [r.strip() for r in args.refs.split(',') if r.strip()]
    if args.refs_file:
        doc = load_json(args.refs_file, [])
        if isinstance(doc, dict):
            doc = doc.get('parks') or doc.get('refs') or []
        refs = [r if isinstance(r, str) else r.get('ref') for r in doc]
    areas_only = set(args.areas.split()) if args.areas else None
    total = sum(len(v) for k, v in areas.items() if not areas_only or k in areas_only)
    n = {'i': 0}

    def on_park(i, ref):
        n['i'] = i
        if not args.quiet:
            print(f'Reading {i} of {total} parks ({ref}).')

    facts, reqs = read_parks(areas, web, docs, truth, getter, state, today, refs=refs, areas_only=areas_only,
                             max_requests=args.max_requests, max_per_park=args.max_per_park, max_parks=args.max_parks,
                             on_park=None if args.quiet else on_park)
    if args.out:
        merge_unchanged(args.out, facts)
        write_facts(args.out, facts)
        save_json(pathlib.Path(args.out) / 'run.json', {'reader': R.READER, 'date': today, 'requests': reqs,
                  'parks': sum(len(v) for v in facts.values())})
    if args.state:
        save_json(args.state, state)
    if os.environ.get('BROWSER') == '1' and args.out and isinstance(getter, LiveGetter):
        from kpc_manners import browser_picture
        pic = pathlib.Path(args.out) / 'pictures'
        for parks in facts.values():
            for ref, fact in parks.items():
                if fact.get('unchanged') or not fact.get('questions'):
                    continue
                if (fact.get('page') or {}).get('kind') in ('refused', 'robots', 'none', 'dead'):
                    continue
                url = (fact.get('asked') or {}).get('url')
                if url:
                    browser_picture(url, getter.M, str(pic / f'{ref}.jpg'))
    if not args.quiet:
        print(f'Done. {reqs} request(s). Facts are in {args.out or "(not saved)"}.')
    return 0


def cmd_later(name):
    print(f'{name} is not in this part of the reader. Nothing was changed.')
    return 0


def selftest():
    """Offline. No request leaves this process."""
    import tempfile, urllib.request
    def boom(*a, **k):
        raise SystemExit('SELFTEST FAIL network')
    urllib.request.urlopen = boom
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(('PASS ' if cond else 'FAIL ') + msg)

    # address facts: longitude first, zero requests
    url = ('https://experience.arcgis.com/experience/bde784e367c3495fa76e3d071720182b'
           '#widget_6=active_datasource_id:dataSource_6,center:-12624110.76729428%2C4470298.853808017%2C102100,'
           'level:17,marker:-113.405%2C37.224%3B%3BRed%20Cliffs%20Recreation%20Area')
    got = R.address_facts(url, 'Red Cliffs Recreation Area', [37.224, -113.405])
    marker = next(c for c in got['coords'] if c['from'] == 'map-link marker')
    center = next(c for c in got['coords'] if 'center' in c['from'])
    check('marker is latitude 37.224 and longitude -113.405 (longitude is written first)',
          abs(marker['lat'] - 37.224) < 1e-9 and abs(marker['lon'] + 113.405) < 1e-9 and marker['role'] == 'park')
    check('center converts from Web Mercator and stays an unknown role',
          abs(center['lat'] - 37.22345) < 0.0001 and abs(center['lon'] + 113.40432) < 0.0001 and center['role'] == 'unknown')
    check('an address is not a request', got['requests_made'] == 0)
    check('a marker whose label is a different place is not a park point',
          R.address_facts(url, 'Zion National Park')['coords'][0]['role'] == 'unknown')

    # combined name, and the one kind that must not split
    check('Denali joins two kinds', R.combined_of('Denali National Park & Preserve') == (True, ['National Park', 'National Preserve']))
    check('a wild and scenic river is one kind', R.combined_of('Aniakchak National Wild and Scenic River')[0] is False)
    check('Parks & Recreation is not two kinds', R.combined_of('Department of Parks & Recreation')[0] is False)
    check('BLM letters come off before the names are compared',
          R.name_core('Red Cliffs BLM Recreation Management Area') == R.name_core('Red Cliffs Recreation Area') == 'red cliffs')

    # the owner's Red Cliffs text
    here = pathlib.Path(__file__).resolve().parents[2] / 'tests/fixtures/park-pages/blm-red-cliffs-recreation-area.page.txt'
    if here.is_file():
        text = here.read_text(encoding='utf-8')
        vis = R.visible_of(text.encode('utf-8'), {'content-type': 'text/plain'}, 'https://www.blm.gov/visit/red-cliffs-recreation-area')
        inside, maybe = R.inside_units(vis['text'], 'Red Cliffs Recreation Area')
        check('Red Cliffs is inside the conservation area, once',
              len(inside) == 1 and inside[0]['unit'] == 'Red Cliffs National Conservation Area')
        check('the trail sentence and the rule line are not a second inside',
              all('Cottonwood' not in (m.get('unit') or '') for m in inside + maybe) or all('Cottonwood' not in m.get('unit', '') for m in inside))
        addrs = R.addresses_in(vis['text'])
        check('the field office address is an office', bool(addrs) and addrs[0]['role'] == 'office')
        sizes = R.sizes_labelled(vis['text'], 'Red Cliffs Recreation Area', 'BLM Recreation Management Area')
        check('feet, miles, a fee and a site count are not sizes',
              all(s['acres'] > 50 for s in sizes) and not any(abs(s['acres'] - 15) < 0.1 or abs(s['acres'] - 11) < 0.1 for s in sizes))

    # fail closed: fixtures missing, network closed
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        (t / 'parkinfo').mkdir()
        (t / 'parkinfo' / 'US-UT.json').write_text(json.dumps({'parks': {
            'US-1': ['Sample National Park', 'https://www.nps.gov/samp/index.htm', 'National Park', '', '', 37.2, -113.4, 0, 0, 1]}}))
        os.environ['KPC_NO_NET'] = '1'
        areas, web, docs, truth = load_data(t)
        getter = FixtureGetter({'pages': {}}, t)
        facts, reqs = read_parks(areas, web, docs, truth, getter, {}, '2026-11-19')
        check('a page with no fixture is not invented and makes one recorded miss, not a live request',
              reqs == 1 and facts['US-UT']['US-1']['page']['kind'] == 'dead' and getter.calls == ['https://www.nps.gov/samp/index.htm'])
        # agency front page: zero requests
        (t / 'parkinfo' / 'US-ID.json').write_text(json.dumps({'parks': {
            'US-11524': ['Deep Creek Reservoir State Fishing Lake', 'https://www.idfg.idaho.gov', 'State Fishing Lake', '', '', 42.2, -112.1, 0, 0, 1]}}))
        areas, web, docs, truth = load_data(t)
        getter = FixtureGetter({'pages': {}}, t)
        facts, reqs = read_parks(areas, web, docs, truth, getter, {}, '2026-11-19', refs=['US-11524'])
        fact = facts['US-ID']['US-11524']
        check('an agency front page is not opened', reqs == 0 and getter.calls == [] and fact['own_page']['is'] == 'agency-home'
              and fact['sizes'] == [] and any(q['code'] == 'AGENCY_HOME_ONLY' for q in fact['questions']))
        # refusal is remembered
        (t / 'parkinfo' / 'US-DE.json').write_text(json.dumps({'parks': {
            'US-9': ['Sample', 'https://documents.example.gov/a.pdf', 'State Wildlife Area', '', '', 38.5, -75.5, 0, 0, 1]}}))
        areas, web, docs, truth = load_data(t)
        manifest = {'pages': {'https://documents.example.gov/a.pdf': {'status': 403, 'body': 'no', 'type': 'text/html'}}}
        getter = FixtureGetter(manifest, t)
        state = {}
        facts, reqs = read_parks(areas, web, docs, truth, getter, state, '2026-11-19', refs=['US-9'])
        check('a 403 is refused and remembered', facts['US-DE']['US-9']['page']['kind'] == 'refused' and 'documents.example.gov' in state['refused'])
        getter2 = FixtureGetter(manifest, t)
        facts2, reqs2 = read_parks(areas, web, docs, truth, getter2, state, '2026-11-20', refs=['US-9'])
        check('a refused host is not asked the next day', reqs2 == 0 and getter2.calls == [])

    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description='Park page reader')
    p.add_argument('command', nargs='?', default='read')
    p.add_argument('--data', default='data')
    p.add_argument('--out', default='')
    p.add_argument('--state', default='')
    p.add_argument('--fixtures', default='')
    p.add_argument('--areas', default='')
    p.add_argument('--refs', default='')
    p.add_argument('--refs-file', default='')
    p.add_argument('--today', default='')
    p.add_argument('--max-requests', type=int, default=1500)
    p.add_argument('--max-per-park', type=int, default=R.MAX_PER_PARK)
    p.add_argument('--max-parks', type=int, default=None)
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--selftest', action='store_true')
    args = p.parse_args(argv)
    if args.selftest or args.command == '--selftest':
        return selftest()
    if args.command == 'read':
        return cmd_read(args)
    if args.command in ('worklist', 'report', 'person-page', 'intake', 'kits', 'pc-kit', 'score'):
        return cmd_later(args.command)
    p.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
