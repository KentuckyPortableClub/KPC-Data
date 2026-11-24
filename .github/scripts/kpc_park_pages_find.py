#!/usr/bin/env python3
"""The own-page finder (rule sheet L, 23 Nov 2026; owner 7:41 AM: "Finish the bot so I can do the webpage look up").

For a park whose page the reader could not read (POTA lists no link, the link is dead, or the link is only the agency's front
page) it looks for the park's OWN page on its managing agency's own site, with the reader's own tools: the same manners
(kpc_manners: robots.txt always wins, slow pacing), the same list of official sites, the same name test and the same kept pages.
It never uses a search engine, Wikipedia, a trail, tourism, map or booking site.

Where it looks, cheapest first (every candidate is then READ and judged; nothing is taken on its address alone):
  kept    links already seen on kept official pages whose words are the park's name (no request)
  up      a dead link: the dead address's own folders, walked up (3 at most), and the one link there naming the park
  home    the agency front page POTA gave: the one link there naming the park
  sister  the agency's park list its sister parks (same area, same kind) have their own pages under: the one link naming the
          park, then the address the sisters' pattern gives (/parks/<park-name>); one or two requests per AGENCY, reused
  sitemap (L-sitemap, 23 Nov d) the site's own sitemap (robots.txt's Sitemap lines, else /sitemap.xml; 6 files at most, read
          one time per site): the addresses whose last part carries every word of the park's name core, 2 at most
  moved   (L-moved, 23 Nov d) a link on an agency site that MOVED (MOVED_SITES: NY DEC, Michigan DNR) and could not be read is
          a dead link; the old site is not asked, the new one is (its lists and its sitemap)
  list    (L-list, 23 Nov c) the agency's own park LIST pages, reached from its front page by their words (parks, find a park,
          A-Z, wildlife areas, historic sites ...; same site only, two steps down at most, 8 pages per site, read one time per
          site): the one link there naming the park. For sites whose park pages carry numbers, not names, in their addresses.
SURE (rule L1) = an official site, one park per page (no other park of the area uses or found the page), the page's own name is
the park's ('same' or 'same-core', never another kind of place), no other park of the area carries that name, AND a second
witness: a point on the page within 5 km of POTA's pin, or the page sits in the agency park list its sister parks use on a host
the reviewed joins tie to land managers (.github/key-agency-table.json of KPC-Links). Anything less is UNSURE (listed for a
person, never taken as the park's page) or NOT FOUND (counted).

A SURE page is read as the park's page at once (the reader's own build_facts), so its name, address and points reach the park
facts; the fact carries found = {url, how, level, why}. The reader's later runs read it in place of POTA's dead or front-page
link (state.json 'found', and parkinfo-web.json entries the official-links bot writes as 'bot: page reader ...').

  python kpc_park_pages.py find-links --data DATA --out OUT [--areas "US-WI"] [--refs-file FIRST.json] [--agency-table F]
                                      [--max-minutes 50] [--max-requests 1500] [--again]
"""
import collections, datetime, gzip, json, os, pathlib, re, time, urllib.parse
import kpc_park_pages as P
import kpc_park_pages_rules as R
import kpc_park_pages_work as W

FIND_RULE = 'L 2026-11-23d'   # d (job 10, owner 1:03 PM "10 and 11 dont stop till you are done"): moved agency sites (L-moved)
                              # and the agency site's own sitemap (L-sitemap); all not-found parks looked again
                              # c also: a site that says no (robots.txt / 403) is counted apart from a busy one, rests 30 days
                              # b (9:20 AM, the owner's NH trial): kept-page links only from the area's own sites
                              # c (afternoon, the first full run found little): the agency's own park LIST pages, reached from
                              # its front page (two steps down at most), are a place to look too (L-list); all parks looked again
POINT_KM = 5.0
WALK_UP = 3
READS_PER_PARK = 4
RETRY_DAYS = 30
GOOD_ROLES = {'park', 'visitor-centre', 'unknown'}
HOW_ORDER = ('kept', 'up', 'home', 'sister', 'pattern', 'list', 'sitemap')
SITEMAP_FILES = 6   # sitemap files read per site at most (the robots.txt list or /sitemap.xml, then its parts)
SITEMAP_PICKS = 2   # addresses taken from a sitemap per park at most
# L-moved (23 Nov, job 10): an agency site that MOVED. The old host no longer serves its park pages to the reader (New York DEC's old
# www.dec.ny.gov: robots.txt never answers on any run, 567 parks; Michigan DNR's old www2.dnr.state.mi.us: 403 or resting, the
# DNR's pages now live on michigan.gov/dnr). A POTA link there that could not be read is a DEAD link, looked for on the new site.
MOVED_SITES = {'www.dec.ny.gov': 'dec.ny.gov', 'dec.state.ny.us': 'dec.ny.gov', 'www.dec.state.ny.us': 'dec.ny.gov',
               'www2.dnr.state.mi.us': 'www.michigan.gov', 'www.dnr.state.mi.us': 'www.michigan.gov'}
LIST_FIRST = 4      # list pages taken from the front page
LIST_SECOND = 2     # ... and from each of those, one step further down
LIST_PAGES = 8      # list pages read per site at most (one time, for every park that site has)
LIST_WORDS = re.compile(r"(?<![a-z])(parks?|parcs?|find a park|all parks|a ?- ?z|a to z|locations?|places|destinations?|"
                        r"areas?|sites?|lieux|lands?|forests?|for[eê]ts?|refuges?|preserves?|reserves?|r[ée]serves?|wildlife|"
                        r"wmas?|recreation|directory|properties|historic|nature)(?![a-z])", re.I)
LIST_NOT = re.compile(r"(log ?in|sign ?in|news|event|calendar|contact|jobs?|careers?|about|donat|shop|store|licen[cs]e|"
                      r"permit|reserv(e|ation)s? (a|your)|book|search|privacy|accessib|\.(pdf|jpe?g|png|zip|docx?)$)", re.I)


# ---------------------------------------------------------------- which parks
def moved_to(url):
    """L-moved: the front page of the site an agency site moved to, or ''."""
    h = (urllib.parse.urlparse(url or '').netloc or '').lower().split(':')[0]
    new = MOVED_SITES.get(h)
    return f'https://{new}/' if new else ''


def why_needed(fact):
    """'no link' | 'dead link' | 'agency home only' | '' for a reader fact."""
    if not isinstance(fact, dict) or fact.get('unchanged'):
        return ''
    if (fact.get('found') or {}).get('level') == 'sure':
        return ''
    pg = fact.get('page') or {}
    asked = fact.get('asked') or {}
    own = (fact.get('own_page') or {}).get('is')
    if pg.get('kind') in ('resting', 'refused', 'dead', 'none') and moved_to(asked.get('url') or pg.get('final_url') or ''):
        return 'dead link'        # L-moved: the agency's old site, which no longer serves the page
    codes = {q.get('code') for q in fact.get('questions') or [] if isinstance(q, dict)}
    if own == 'agency-home' or 'AGENCY_HOME_ONLY' in codes:
        return 'agency home only'
    if pg.get('kind') == 'dead' or 'LINK_DEAD' in codes:
        return 'dead link'
    if not asked.get('url') or pg.get('kind') == 'none' or 'NO_PAGE' in codes:
        return 'no link'
    return ''


def worklist(facts_by_area, state, today, first=(), areas_only=None, again=False):
    """[(area, ref, why)] in order: the parks of `first` (a private list, e.g. joined and not confirmed), then no link, dead
    link, agency home only. A park tried in the last RETRY_DAYS days is passed over unless `again`."""
    tried = state.get('found') or {}
    rows = []
    for area, parks in sorted(facts_by_area.items()):
        if areas_only and area not in areas_only:
            continue
        for ref, fact in sorted(parks.items()):
            why = why_needed(fact)
            if not why:
                continue
            t = tried.get(ref) or {}
            if not again and t.get('date') and t.get('rule') == FIND_RULE and W.age_days(t['date'], today) < RETRY_DAYS:
                continue      # a park looked for under an older rule is looked for again
            rows.append((area, ref, why))
    rank = {r: i for i, r in enumerate(first or ())}
    kind = {'no link': 0, 'dead link': 1, 'agency home only': 2}
    rows.sort(key=lambda x: (0 if x[1] in rank else 1, rank.get(x[1], 0), kind[x[2]], x[0], x[1]))
    return rows


# ---------------------------------------------------------------- what the sister parks teach
def parent_of(url):
    p = urllib.parse.urlparse(url or '')
    path = (p.path or '').rstrip('/')
    if '/' not in path.strip('/'):
        return '', ''
    return f'{p.scheme or "https"}://{p.netloc.lower()}', path.rsplit('/', 1)[0] + '/'


def slug(s, sep='-'):
    import html as _html
    t = re.sub(r"['’‘`´.]", '', _html.unescape(str(s or ''))).lower()
    return sep.join(re.findall(r'[a-z0-9]+', t))


def slug_forms(name):
    """The ways an agency writes a park's name in its addresses: full name, or the name without its kind words."""
    core = R.name_core(name)
    out = {}
    for sep in ('-', '_'):
        out['full' + sep] = slug(name, sep)
        if core:
            out['core' + sep] = slug(core, sep)
    return {k: v for k, v in out.items() if v}


def sister_sites(facts_by_area, areas):
    """(area, POTA kind) -> [(origin, folder, count, pattern)] best first: the folders the area's own pages of that kind sit
    in (2 or more sisters), and the address pattern most of them share there ('full-', 'core_' ... or '')."""
    groups = collections.defaultdict(collections.Counter)
    forms = collections.defaultdict(collections.Counter)
    for area, parks in facts_by_area.items():
        rows = areas.get(area) or {}
        for ref, fact in parks.items():
            if not isinstance(fact, dict) or (fact.get('own_page') or {}).get('is') != 'own' or fact.get('unofficial'):
                continue
            url = (fact.get('page') or {}).get('final_url') or (fact.get('asked') or {}).get('url') or ''
            if not url or not R.official_host(url) or R.is_agency_home(url):
                continue
            if (fact.get('page') or {}).get('kind') in ('resting', 'refused', 'dead', 'none') or moved_to(url):
                continue      # a page never read (or on a site that moved) teaches no folder
            origin, folder = parent_of(url)
            if not folder:
                continue
            kind = (rows.get(ref) or {}).get('type') or ((fact.get('pota') or {}).get('type')) or ''
            key = (area, kind)
            groups[key][(origin, folder)] += 1
            last = urllib.parse.unquote(urllib.parse.urlparse(url).path.rstrip('/').rsplit('/', 1)[-1]).lower()
            last = re.sub(r'\.(html?|aspx?|php)$', '', last)
            name = (rows.get(ref) or {}).get('name') or ((fact.get('pota') or {}).get('name')) or ''
            for form, s in slug_forms(name).items():
                if last == s:
                    forms[(key, origin, folder)][form] += 1
                    break
    out = {}
    for key, c in groups.items():
        rows = []
        for (origin, folder), n in c.most_common(2):
            if n < 2:
                continue
            f = forms.get((key, origin, folder)) or collections.Counter()
            pat = f.most_common(1)[0][0] if f and f.most_common(1)[0][1] >= 2 else ''
            rows.append((origin, folder, n, pat))
        if rows:
            out[key] = rows
    return out


def agency_hosts(path):
    try:
        d = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return set()
    return {R.base_host(str(h).lower()) for h in (d.get('hosts') or {})}


def on_agency_table(url, hosts):
    h = R.base_host(R.host_of(url or ''))
    return bool(h) and any(h == x or h.endswith('.' + x) for x in hosts)


# ---------------------------------------------------------------- kept pages, read with no request
def kept_index(manifest_path):
    """name core -> {url}: every link on a kept official page, by the core of its words. Nothing is asked of any site."""
    idx = collections.defaultdict(set)
    man = P.kept_manifest(manifest_path)
    root = pathlib.Path(manifest_path).parent
    for url, rec in (man.get('pages') or {}).items():
        if not isinstance(rec, dict) or 'html' not in str(rec.get('type') or 'text/html') or not R.official_host(url):
            continue
        try:
            raw = (root / rec['file']).read_bytes()
            raw = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
        except (OSError, KeyError, EOFError, ValueError):
            continue
        vis = R.visible_of(raw, {'content-type': 'text/html'}, rec.get('final') or url)
        for link, words in vis.get('links') or []:
            if not words or not R.official_host(link) or R.is_agency_home(link):
                continue
            c = R.name_core(' '.join(str(words).split()))
            if c and len(c) >= 4:
                idx[c].add(link.split('#')[0])
    return idx


# ---------------------------------------------------------------- one polite fetch, the reader's way
class Fetcher:
    """The reader's fetch (kpc_park_pages.read_parks), cut down: WDPA never asked, a site put aside stays aside, every page
    kept for later fixes, one request counted per address, the run's deadline and request budget honoured."""

    def __init__(self, getter, state, today, keeper=None, max_requests=1500, deadline=None, get_max_seconds=P.GET_MAX_SECONDS):
        self.getter, self.state, self.today, self.keeper = getter, state, today, keeper
        self.max_requests, self.deadline, self.get_max = max_requests, deadline, get_max_seconds
        self.requests = 0
        self.cache = {}
        self.busy = 0     # answers that say nothing about the page (busy, resting, not asked): the park is tried again next run
        self.said_no = 0  # the site says no to the reader (robots.txt, 401/403, a bot wall): NOT busy, it rests 30 days like any miss
        self.lists = {}   # site -> its park list pages, read one time for every park of that site (L-list)
        self.sitemaps = {}   # site -> the addresses its own sitemap lists, read one time for every park of that site (L-sitemap)

    def get_raw(self, url):
        """A file that is not a web page (robots.txt, a sitemap): the same manners, budget and refusals as get(); not kept.
        -> body bytes, b'' when the site answered no or nothing, None when the run's budget is spent."""
        if not url or not url.startswith(('http://', 'https://')):
            return b''
        host = R.host_of(url)
        if host and P._refused_until(self.state, host, self.today):
            self.said_no += 1
            return b''
        from_copy = isinstance(self.getter, P.KeeperCopyGetter) and self.getter.copy._rec(url) is not None
        if not from_copy and not self.left():
            self.busy += 1
            return None
        if not from_copy:
            self.requests += 1
        try:
            st, _h, body, _f = self.getter.get(url, deadline=self.deadline, max_time=self.get_max)
        except TypeError:
            st, _h, body, _f = self.getter.get(url)
        if st != 200:
            if st in (401, 403) or (isinstance(st, str) and P.robots_block(st) and not P.next_run(st)):
                self.said_no += 1      # the site says no
            elif isinstance(st, str) and (P.next_run(st) or st.startswith('err')) or (isinstance(st, int) and st >= 500):
                self.busy += 1         # busy or resting: the park is looked for again next run
            return b''
        body = body or b''
        if body[:2] == b'\x1f\x8b':
            try:
                body = gzip.decompress(body)
            except OSError:
                return b''
        return body

    def time_up(self):
        return self.deadline is not None and time.time() >= self.deadline

    def left(self):
        return self.requests < self.max_requests and not self.time_up()

    def get(self, url):
        if not url or not url.startswith(('http://', 'https://')):
            return None
        key = P.norm_url(url)
        if key in self.cache:
            k = (self.cache[key] or {}).get('kind')
            if k == 'resting':
                self.busy += 1     # the same busy site, for this park too
            elif k == 'refused':
                self.said_no += 1  # the same site that says no, for this park too
            return self.cache[key]
        if R.is_wdpa(url):
            return None
        host = R.host_of(url)
        if host and P._refused_until(self.state, host, self.today):
            self.said_no += 1
            page = {'url': url, 'final': url, 'status': 'refused', 'kind': 'refused', 'text': '', 'links': []}
            self.cache[key] = page
            return page
        from_copy = isinstance(self.getter, P.KeeperCopyGetter) and self.getter.copy._rec(url) is not None
        if not from_copy and not self.left():
            self.busy += 1
            return None
        if not from_copy:
            self.requests += 1
        try:
            st, headers, body, final = self.getter.get(url, deadline=self.deadline, max_time=self.get_max)
        except TypeError:
            st, headers, body, final = self.getter.get(url)
        if self.keeper is not None and not from_copy:
            self.keeper.keep(url, final or url, st, headers, body)
        extra = self.getter.links_for(url) if hasattr(self.getter, 'links_for') else []
        vis = R.visible_of(body, headers, final or url, extra)
        kind = P._kind_of_status(st, vis.get('text'), final or url, is_pdf=bool(vis.get('pdf')))
        if kind == 'html' and R.unfilled_template(vis.get('html')):
            kind = 'script-built'
        if kind == 'refused' and not from_copy and not (isinstance(st, str) and P.robots_block(st)):
            P._remember_refusal(self.state, R.host_of(final or url) or host, self.today, final or url)
        page = {'url': url, 'final': final or url, 'status': st, 'kind': kind, 'text': vis.get('text') or '',
                'html': vis.get('html') or '', 'title': vis.get('title') or '', 'heading': vis.get('heading') or '',
                'og': vis.get('og') or '', 'jsonld': vis.get('jsonld') or '', 'links': vis.get('links') or [],
                'headings': vis.get('headings') or [], 'fingerprint': R.fp_of(vis.get('text') or ''),
                'family': R.family_of(final or url), 'thin': len((vis.get('text') or '').strip()) < 400}
        if from_copy:
            page['kept_date'] = (self.getter.copy._rec(url) or {}).get('date') or ''
        if kind == 'resting':
            self.busy += 1
        elif kind == 'refused':
            self.said_no += 1
        self.cache[key] = page
        return page


# ---------------------------------------------------------------- the judge (rule sheet L)
def judge(ref, area, row, area_parks, page, claimed, today, how, sisters=(), table=frozenset()):
    """-> (level 'sure' | 'unsure' | 'no', why, fact or None)."""
    if not page or page.get('kind') != 'html' or not (page.get('text') or '').strip():
        return 'no', 'the page could not be read as a web page' + (' (a PDF does not count)' if (page or {}).get('kind') == 'pdf' else ''), None
    url = page.get('final') or page.get('url') or ''
    if not R.official_host(url):
        return 'no', 'not an official site', None
    if R.is_agency_home(url):
        return 'no', "the agency's front page", None
    owner = claimed.get(P.norm_url(url))
    if owner and owner != ref:
        return 'unsure', 'another park of the area uses or found this page', None
    pota = {'name': row.get('name'), 'type': row.get('type'), 'pin': [row.get('lat'), row.get('lon')], 'link': '', 'qsos': row.get('qsos')}
    asked = {'url': url, 'from': 'found', 'others_noted': 0}
    fact = R.build_facts(ref, area, pota, area_parks, asked, [page], today, [], 'own',
                         f'found on the agency site ({how}): its own name, one park per page', read_blocks=True)
    vs = (fact.get('name') or {}).get('vs_pota')
    if (fact.get('designation') or {}).get('vs_pota_type') == 'differs':
        return 'no', 'the page is another kind of place (a sister unit)', None
    if vs == 'same-words':
        return 'unsure', "same words, another kind of place: never sure by itself", fact
    if vs not in ('same', 'same-core'):
        return 'no', "the page's own name is not the park's", None
    best = (fact.get('name') or {}).get('best') or ''
    for r2, other in (area_parks or {}).items():
        # 23 Nov (owner 'Yes', audit 4 MUST 2.1): a page named only by the core ('Mud Lake') fits every park of the area with
        # that core ('Mud Lake State Park', 'Mud Lake Wildlife Area'): never sure for one of them
        cmp_ = R.compare_names(best, (other or {}).get('name')) if r2 != ref else None
        if cmp_ == 'same' or (vs == 'same-core' and cmp_ == 'same-core'):
            return 'unsure', 'another park of the area carries this name' + (' (the same core)' if cmp_ == 'same-core' else ''), fact
    pts = [c for c in ((fact.get('location') or {}).get('coords') or [])
           if isinstance(c, dict) and (c.get('role') or 'unknown') in GOOD_ROLES and c.get('km_from_pin') is not None]
    if any(c['km_from_pin'] <= POINT_KM for c in pts):
        return 'sure', f'own name ({vs}) and a point on the page within {POINT_KM:g} km of the pin', fact
    if pts:
        # a point on the page far from the pin speaks AGAINST the page: no other witness makes it sure
        return 'unsure', f"own name ({vs}), but the page's point is {min(c['km_from_pin'] for c in pts)} km from the pin", fact
    origin, folder = parent_of(url)
    if (origin, folder) in {(o, f) for o, f, *_ in sisters} and on_agency_table(url, table):
        return 'sure', f"own name ({vs}) on the agency park list its sister parks use ({R.host_of(url)})", fact
    return 'unsure', f'own name ({vs}), but no second witness (no point on the page, not on a sister-park list of a known agency site)', fact


# ---------------------------------------------------------------- the agency's own park lists (L-list)
def list_links(page, home):
    """The links of a page that lead to a park LIST on the same site, best first (most list words)."""
    base = R.base_host(R.host_of(home))
    seen, out = set(), []
    for link, words in (page or {}).get('links') or []:
        if not link or not str(link).startswith(('http://', 'https://')) or R.base_host(R.host_of(link)) != base:
            continue
        path = urllib.parse.unquote(urllib.parse.urlparse(link).path or '')
        text = ' '.join(str(words or '').split())
        if LIST_NOT.search(text) or LIST_NOT.search(path) or R.is_agency_home(link):
            continue
        score = len(LIST_WORDS.findall(text)) + len(LIST_WORDS.findall(path.replace('-', ' ').replace('_', ' ')))
        n = P.norm_url(link)
        if score and n not in seen and n != P.norm_url(home):
            seen.add(n)
            out.append((-score, len(text), link))
    return [u for *_k, u in sorted(out)]


def list_pages(F, home):
    """The park list pages of the site `home` is the front page of: the front page's list links (LIST_FIRST), then one step
    further down (LIST_SECOND each), LIST_PAGES at most; read ONE time per site and kept for every park of that site."""
    if F is None or not home:
        return []
    p = urllib.parse.urlparse(home)
    if not p.netloc:
        return []
    root = f'{p.scheme or "https"}://{p.netloc.lower()}/'
    key = R.base_host(R.host_of(root))
    if key in F.lists:
        return F.lists[key]
    got, asked = [], set()
    front = F.get(root)
    if front is None:
        return []          # the run's budget is spent: not kept, the next park (or run) tries again
    first = list_links(front, root)[:LIST_FIRST] if front.get('kind') == 'html' else []
    for u in first:
        if len(asked) >= LIST_PAGES:
            break
        asked.add(P.norm_url(u))
        pg = F.get(u)
        if pg is None:
            return got
        if pg.get('kind') == 'html':
            got.append(pg)
    for pg in list(got):
        for u in list_links(pg, root)[:LIST_SECOND]:
            if len(asked) >= LIST_PAGES:
                break
            if P.norm_url(u) in asked:
                continue
            asked.add(P.norm_url(u))
            p2 = F.get(u)
            if p2 is None:
                return got
            if p2.get('kind') == 'html':
                got.append(p2)
    if front.get('kind') == 'html':
        got.insert(0, front)
    F.lists[key] = got
    return got


# ---------------------------------------------------------------- the agency site's own sitemap (L-sitemap)
SITEMAP_LOC = re.compile(rb'<loc>\s*([^<\s]+)\s*</loc>', re.I)
SITEMAP_PART = re.compile(r'(place|park|land|area|forest|wildlife|page|node|content|site|location|destination|recreat)', re.I)


def sitemap_urls(F, home):
    """Every address the site's own sitemap lists (robots.txt 'Sitemap:' lines on the same site, else /sitemap.xml; a sitemap
    index is followed into its parts, the park-like ones first, SITEMAP_FILES files at most), read ONE time per site."""
    if F is None or not home:
        return []
    p = urllib.parse.urlparse(home)
    if not p.netloc:
        return []
    root = f'{p.scheme or "https"}://{p.netloc.lower()}/'
    key = R.base_host(R.host_of(root))
    if key in F.sitemaps:
        return F.sitemaps[key]
    robots = F.get_raw(root + 'robots.txt')
    if robots is None:
        return []
    todo = [m.group(1).strip() for m in re.finditer(r'(?im)^\s*sitemap\s*:\s*(\S+)', robots.decode('utf-8', 'replace'))]
    todo = [u for u in todo if R.base_host(R.host_of(u)) == key] or [root + 'sitemap.xml']
    urls, done = [], 0
    while todo and done < SITEMAP_FILES:
        u = todo.pop(0)
        body = F.get_raw(u)
        done += 1
        if body is None:
            return urls
        locs = [m.group(1).decode('utf-8', 'replace').replace('&amp;', '&') for m in SITEMAP_LOC.finditer(body)]
        if b'<sitemapindex' in body[:2000].lower():
            parts = [x for x in locs if R.base_host(R.host_of(x)) == key]
            todo += sorted(parts, key=lambda x: (0 if SITEMAP_PART.search(x.rsplit('/', 1)[-1]) else 1, len(x)))
            continue
        urls += [x for x in locs if R.base_host(R.host_of(x)) == key]
    F.sitemaps[key] = urls
    return urls


def sitemap_picks(urls, name):
    """The sitemap addresses whose LAST part carries every word of the park's name core (in any order), fewest extra words
    first; SITEMAP_PICKS at most. A core of one short word gives none (too loose)."""
    core = R.name_core(name).split()
    if not core or (len(core) == 1 and len(core[0]) < 5):
        return []
    want, out = set(core), []
    for u in urls:
        last = urllib.parse.unquote(urllib.parse.urlparse(u).path.rstrip('/').rsplit('/', 1)[-1]).lower()
        last = re.sub(r'\.(html?|aspx?|php|cfm)$', '', last)
        words = set(re.findall(r'[a-z0-9]+', last.replace("'", '')))
        if want <= words and not R.is_agency_home(u):
            out.append((len(words - want), len(u), u))
    return [u for *_k, u in sorted(out)[:SITEMAP_PICKS]]


# ---------------------------------------------------------------- the walk
def area_sites(facts_by_area):
    """area -> the hosts (www. left off) the area's own parks' pages and links use: a kept page's link is a candidate only on
    one of these (9:20 AM trial: 'Taylor State Forest' was offered a city park in British Columbia by name alone)."""
    out = collections.defaultdict(set)
    for area, parks in facts_by_area.items():
        for fact in parks.values():
            if not isinstance(fact, dict):
                continue
            for u in ((fact.get('page') or {}).get('final_url'), (fact.get('asked') or {}).get('url')):
                if u and R.official_host(u):
                    out[area].add(R.base_host(R.host_of(u)))
    return out


def candidates_for(ref, row, fact, why, F, kept, sisters, sites=None):
    """Yield (how, url) in order, asking each site as little as it can."""
    name = row.get('name') or ''
    core = R.name_core(name)
    seen = set()

    def fresh(u):
        n = P.norm_url(u)
        if not u or n in seen:
            return False
        seen.add(n)
        return True

    for u in sorted(kept.get(core) or ()) if core else ():
        if sites is not None and R.base_host(R.host_of(u)) not in sites:
            continue          # a link on another state's or country's site is never this park's page
        if fresh(u):
            yield 'kept', u
    asked = ((fact or {}).get('asked') or {}).get('url') or ''
    moved = moved_to(asked)
    if why == 'dead link' and asked and not moved:      # L-moved: the old site is not asked at all
        url = asked
        for _ in range(WALK_UP):
            origin, folder = parent_of(url)
            if not folder or folder == '/':
                break
            up = origin + folder
            page = F.get(up)
            if page and page.get('kind') == 'html':
                pick = P._park_link(page.get('links'), name, up)
                if pick and fresh(pick):
                    yield 'up', pick
                    break
            url = up.rstrip('/')
    if why == 'agency home only' and asked:
        page = F.get(asked)
        if page and page.get('kind') == 'html':
            pick = P._park_link(page.get('links'), name, asked)
            if pick and fresh(pick):
                yield 'home', pick
    for origin, folder, _n, pat in sisters or ():
        page = F.get(origin + folder)
        if page and page.get('kind') == 'html':
            pick = P._park_link(page.get('links'), name, origin + folder)
            if pick and fresh(pick):
                yield 'sister', pick
                continue
        if pat:
            s = slug_forms(name).get(pat)
            if s and fresh(origin + folder + s):
                yield 'pattern', origin + folder + s
    # L-list: the agency's own park lists, from its front page (the front page POTA gave, the dead link's site, the sisters' site)
    homes = []
    if moved:
        homes.append(moved)
    elif why in ('agency home only', 'dead link') and asked:
        homes.append(asked)
    for origin, _folder, _n, _pat in sisters or ():
        homes.append(origin + '/')
    done = set()
    for home in homes:
        h = R.base_host(R.host_of(home) or '')
        if not h or h in done or (sites is not None and sites and h not in sites and why != 'agency home only' and home != moved):
            continue
        done.add(h)
        for pg in list_pages(F, home):
            pick = P._park_link(pg.get('links'), name, pg.get('final') or pg.get('url'))
            if pick and R.base_host(R.host_of(pick)) == h and fresh(pick):
                yield 'list', pick
        # L-sitemap: the site's own sitemap, the addresses that carry the park's name
        for pick in sitemap_picks(sitemap_urls(F, home), name):
            if fresh(pick):
                yield 'sitemap', pick


def find_links(areas, facts_by_area, getter, state, today, first=(), areas_only=None, again=False, kept=None,
               table=frozenset(), keeper=None, max_requests=1500, deadline=None, get_max_seconds=P.GET_MAX_SECONDS,
               quiet=False, web=None, docs=None, on_save=None, save_every=60):
    """-> (rows, facts written {area: {ref: fact}}, requests). Each row: ref, area, why, level, how, url, reason.
    on_save(rows, written) is called about every save_every seconds, so a window closed part way keeps what was found."""
    web, docs = web or {}, docs or {}
    F = Fetcher(getter, state, today, keeper, max_requests, deadline, get_max_seconds)
    sisters = sister_sites(facts_by_area, areas)
    sites = area_sites(facts_by_area)
    claimed = {}
    for area, parks in areas.items():
        for r, row in parks.items():
            u = P.choose_link(r, row, web, docs)[0]
            if u and R.official_host(u) and not R.is_agency_home(u):
                claimed.setdefault(P.norm_url(u), r)
            f = (facts_by_area.get(area) or {}).get(r) or {}
            fu = (f.get('page') or {}).get('final_url')
            if fu and (f.get('own_page') or {}).get('is') == 'own':
                claimed.setdefault(P.norm_url(fu), r)
    for r, t in (state.get('found') or {}).items():
        if (t or {}).get('level') == 'sure' and t.get('url'):
            claimed[P.norm_url(t['url'])] = r
    todo = worklist(facts_by_area, state, today, first, areas_only, again)
    rows, written = [], collections.defaultdict(dict)
    sure_now, contested = {}, set()   # 23 Nov (audit 4 SHOULD 2.2): who wins a shared page must not depend on the work order
    # 23 Nov (owner 'Yes', audit 4 MUST 2.1): an earlier SURE find whose page is named only by a core another park of the area
    # shares ('Mud Lake' for 'Mud Lake State Park' and 'Mud Lake Wildlife Area') is re-judged here, offline (no request):
    # it becomes unsure and its page counts as shared, not the park's own
    where = {r: a for a, ps in facts_by_area.items() for r in ps}
    for r, t in sorted((state.get('found') or {}).items()):
        a = where.get(r)
        if not a or (t or {}).get('level') != 'sure' or (areas_only and a not in areas_only):
            continue
        f = facts_by_area[a][r] or {}
        nm = f.get('name') or {}
        best = nm.get('best') or ''
        if nm.get('vs_pota') != 'same-core' or not best:
            continue
        if any(r2 != r and R.compare_names(best, (row2 or {}).get('name')) == 'same-core' for r2, row2 in (areas.get(a) or {}).items()):
            why_ = 'another park of the area carries this name (the same core): re-judged 23 Nov'
            t.update(level='unsure', why=why_)
            f2 = dict(f)
            f2['own_page'] = dict(f.get('own_page') or {}, **{'is': 'shared', 'why': why_})
            if isinstance(f2.get('found'), dict): f2['found'] = dict(f2['found'], level='unsure', why=why_)
            written[a][r] = f2
            if claimed.get(P.norm_url(t.get('url') or '')) == r: claimed.pop(P.norm_url(t['url']), None)
            rows.append({'ref': r, 'area': a, 'why': t.get('for') or '', 'level': 'unsure', 'how': t.get('how') or '',
                         'url': t.get('url') or '', 'reason': why_})
    stopped = ''
    last = [time.monotonic()]
    for i, (area, ref, why) in enumerate(todo):
        if on_save is not None and time.monotonic() - last[0] >= save_every:
            on_save(rows, written)
            last[0] = time.monotonic()
        if F.time_up():
            stopped = 'minutes'
            break
        if not F.left():
            stopped = 'requests'
            break
        row = (areas.get(area) or {}).get(ref)
        fact = (facts_by_area.get(area) or {}).get(ref) or {}
        if not row:
            continue
        if not quiet:
            print(f'Looking for the own page of park {i + 1:,} of {len(todo):,} ({ref}, {why}).', flush=True)
        best = ('no', 'nothing on the agency sites named this park', None, '', '')
        reads = 0
        busy0, no0 = F.busy, F.said_no
        for how, url in candidates_for(ref, row, fact, why, F, kept or {}, sisters.get((area, row.get('type') or '')), sites.get(area) or set()):
            if reads >= READS_PER_PARK:
                break
            page = F.get(url)
            reads += 1
            if page is None:
                break
            level, reason, built = judge(ref, area, row, areas.get(area) or {}, page, claimed, today, how,
                                         sisters.get((area, row.get('type') or '')) or (), table)
            if level == 'sure':
                best = (level, reason, built, how, page.get('final') or url)
                break
            if level == 'unsure' and reason.startswith('another park of the area uses or found this page'):
                o_ = claimed.get(P.norm_url(page.get('final') or url))
                if o_ in sure_now: contested.add(o_)   # audit 4 SHOULD 2.2: a page two parks want is sure for neither
            if level == 'unsure' and best[0] != 'unsure':
                best = (level, reason, built, how, page.get('final') or url)
        level, reason, built, how, url = best
        busy = F.busy > busy0
        if level == 'no' and busy:
            reason = 'a site was busy or not asked this run: looked for again next run'
        elif level == 'no' and F.said_no > no0:
            reason = "the agency site says no to our reader (robots.txt or it refuses us): robots.txt always wins, a person's link is needed"
        found = {'url': url if level != 'no' else '', 'how': how, 'level': level, 'why': reason, 'for': why,
                 'date': today, 'rule': FIND_RULE, 'was': (fact.get('asked') or {}).get('url') or ''}
        if level == 'sure' and built:
            built['found'] = found
            built['asked']['was'] = (fact.get('asked') or {}).get('url') or ''
            built['questions'] = R.questions_for(built)
            written[area][ref] = built
            claimed[P.norm_url(url)] = ref
            sure_now[ref] = area
            page = F.cache.get(P.norm_url(url)) or {}
            when = page.get('kept_date') or today
            built['page']['read'] = when
            # the reader's next run sees this page as read (same address, same text): it is not fetched again inside 30 days
            state.setdefault('read', {})[ref] = {'url': url, 'fingerprint': page.get('fingerprint') or '', 'date': when,
                                                 'kind': 'html', 'final': url}
        else:
            kept_fact = dict(fact)
            kept_fact['found'] = found
            written[area][ref] = kept_fact
        state.setdefault('found', {})[ref] = dict(found, date='' if (level == 'no' and busy) else today)
        rows.append({'ref': ref, 'area': area, 'why': why, 'level': level, 'how': how, 'url': found['url'], 'reason': reason})
    # audit 4 SHOULD 2.2: a page found SURE this run for one park that another park of the area also wanted is unsure for both
    # (before, the park looked at first kept it, and the private work order decides who is first)
    why_c = 'another park of the area wanted the same page: a person decides'
    for ref in sorted(contested):
        a = sure_now[ref]
        f2 = dict(written[a][ref])
        f2['own_page'] = dict(f2.get('own_page') or {}, **{'is': 'shared', 'why': why_c})
        f2['found'] = dict(f2.get('found') or {}, level='unsure', why=why_c)
        written[a][ref] = f2
        state.setdefault('found', {})[ref] = dict(state['found'].get(ref) or {}, level='unsure', why=why_c)
        (state.get('read') or {}).pop(ref, None)
        for r in rows:
            if r['ref'] == ref: r.update(level='unsure', reason=why_c)
    state['find_stopped'] = stopped
    state['find_left'] = max(0, len(todo) - len(rows)) if stopped else 0
    return rows, dict(written), F.requests


def counts_of(rows):
    c = collections.Counter()
    for r in rows:
        c[f"{r['level']}"] += 1
        c[f"{r['level']} | {r['area']}"] += 1
        if r['level'] != 'no':
            c[f"{r['level']} by {r['how']}"] += 1
        c[f"for {r['why']}: {r['level']}"] += 1
    return c


def summary_lines(rows, requests, state):
    c = counts_of(rows)
    lines = [f'Own-page finder ({FIND_RULE}): {len(rows):,} parks looked at, {requests:,} request(s).',
             f"  sure (taken as the park's page): {c['sure']:,}",
             f'  unsure (listed for a person):     {c["unsure"]:,}',
             f'  not found:                        {c["no"]:,}',
             f'    of them, a site was busy or not asked (looked for again next run): {sum(1 for r in rows if "busy" in r["reason"]):,}',
             f'    of them, the agency site says no to our reader (robots.txt / refused; never forced): {sum(1 for r in rows if "says no" in r["reason"]):,}']
    if state.get('find_stopped'):
        lines.append(f"  stopped ({state['find_stopped']}); {state.get('find_left', 0):,} parks are left for the next run.")
    for k in sorted(k for k in c if ' by ' in k or k.startswith('for ')):
        lines.append(f'  {k}: {c[k]:,}')
    lines.append('By area (sure / unsure / not found):')
    for a in sorted({r['area'] for r in rows}):
        lines.append(f"  {a}: {c['sure | ' + a]:,} / {c['unsure | ' + a]:,} / {c['no | ' + a]:,}")
    return lines


def cmd_find_links(args):
    areas, web, docs, _truth = P.load_data(args.data)
    if not areas:
        print('No stored parks. Nothing was looked for.')
        return 0
    if not args.out:
        print('find-links needs --out (the reader\'s out folder with its facts).')
        return 2
    today = args.today or datetime.date.today().isoformat()
    state_path = args.state or str(pathlib.Path(args.out) / 'state.json')
    state = P.load_json(state_path, {}) or {}
    facts = W.load_facts(args.out)
    if not facts:
        print('No page facts in the out folder yet: run the reader first. Nothing was looked for.')
        return 0
    areas_only = set(args.areas.split()) if args.areas else None
    first = P._refs_from_args(args)
    if getattr(args, 'priority_file', '') and pathlib.Path(args.priority_file).is_file():
        # the PRIVATE likely-mismatch list (the joined, not confirmed parks first); its order is never written anywhere
        first = first + [r for r in W.private_refs(args.priority_file, P.REPO_ROOT) if r not in set(first)]
    keep_arg = getattr(args, 'keep_pages', '') or ''
    kept_dir = keep_arg if keep_arg and keep_arg != 'off' else str(pathlib.Path(args.out).resolve().parent / 'pages-kept')
    man = pathlib.Path(kept_dir) / 'manifest.json'
    kept = kept_index(man) if man.is_file() else {}
    table = agency_hosts(getattr(args, 'agency_table', '') or '')
    if args.fixtures:
        getter = P.FixtureGetter(P.load_json(args.fixtures, {}), pathlib.Path(args.fixtures).parent)
        keeper = None
    else:
        live = None if os.environ.get('KPC_NO_NET') == '1' else P.LiveGetter(state)
        getter = P.KeeperCopyGetter(P.kept_manifest(man) if man.is_file() else {}, man.parent, live)
        keeper = P.PageKeeper(kept_dir, today) if keep_arg != 'off' and live is not None else None
    if not args.quiet:
        print(f'Own-page finder: kept pages give {sum(len(v) for v in kept.values()):,} named links; '
              f'{len(table):,} agency sites known from reviewed joins.', flush=True)
    deadline = time.time() + args.max_minutes * 60 if args.max_minutes else None
    out = pathlib.Path(args.out)
    old_rows = {r['ref']: r for r in ((P.load_json(out / 'found-links.json', {}) or {}).get('rows') or []) if isinstance(r, dict)}

    def persist(rows, written, reqs=None):
        """Facts, the found list and the state, written whole (a window closed part way keeps every park done so far)."""
        if keeper is not None:
            keeper.save()
        for area, parks in written.items():
            path = out / 'facts' / f'{area}.json'
            doc = P.load_json(path, {}) or {'area': area, 'reader': R.READER, 'parks': {}}
            doc.setdefault('parks', {}).update(parks)
            P.save_json(path, doc, only_if_changed=True)
        keep = dict(old_rows)
        keep.update({r['ref']: r for r in rows})
        P.save_json(out / 'found-links.json', {'rule': FIND_RULE, 'date': today, 'rows': [keep[k] for k in sorted(keep)]})
        P.save_json(state_path, state)
        if reqs is not None:
            (out / 'found-links-summary.txt').write_text('\n'.join(summary_lines(rows, reqs, state)) + '\n', encoding='utf-8')

    rows, written, reqs = find_links(areas, facts, getter, state, today, first=first, areas_only=areas_only,
                                     again=bool(getattr(args, 'again', False)), kept=kept, table=table, keeper=keeper,
                                     max_requests=args.max_requests, deadline=deadline,
                                     get_max_seconds=getattr(args, 'max_get_seconds', None) or P.GET_MAX_SECONDS,
                                     quiet=bool(args.quiet), web=web, docs=docs, on_save=persist)
    if isinstance(getter, P.KeeperCopyGetter) and getter.live is not None:
        state['hosts'] = getter.resting()
    persist(rows, written, reqs)
    if not args.quiet:
        print((out / 'found-links-summary.txt').read_text(encoding='utf-8'), flush=True)
    return 0
