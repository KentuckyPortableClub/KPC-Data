#!/usr/bin/env python3
"""Park page reader (hand-off 05). It reports. It never decides.

Commands: read, find-links, worklist, report, person-page, intake, kits, pc-kit, --selftest.
Every request goes through kpc_manners.Manners. This file does not fetch on its own.

Part 1 of the hand-off is `read` and `--selftest`. Later commands are named here and
filled in by the later parts; until then they say so and do no work.
"""
import argparse, datetime, json, os, pathlib, re, sys, time, urllib.parse


def _kpc_bar(i, n, label, t0):
    """26 Nov (owner: 'a progress bar or something on the long ones'): one line, e.g.
    [#########---------------------]  30%   12 of 40   US-NY   about 8 min left"""
    import time as _t
    f = (i / n) if n else 1.0
    left = ''
    if 0 < i < n:
        m = (_t.time() - t0) / 60 / i * (n - i)
        left = f'   about {m:.0f} min left' if m >= 1 else '   less than a minute left'
    return f'  [{"#" * int(f * 30)}{"-" * (30 - int(f * 30))}] {f * 100:3.0f}%   {i} of {n}   {label}{left}'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_park_pages_rules as R  # noqa: E402
import kpc_park_pages_work as W  # noqa: E402
import kpc_not_sure as NS  # noqa: E402
_HERE = pathlib.Path(__file__).resolve()
# The repo root only when this file sits in the repo's .github/scripts; a PC kit (scripts/ in a plain folder) has none (21 Nov)
REPO_ROOT = _HERE.parents[2] if (_HERE.parent.name, _HERE.parent.parent.name) == ('scripts', '.github') else None
from kpc_manners import Manners, next_run, robots_block  # noqa: E402
import kpc_manners as _KM  # noqa: E402
# 23 Nov (job 10, owner 1:03 PM): the PC's slow-sites step (2g) may wait longer between pages of a site whose robots.txt asks
# for a long Crawl-delay, never cutting it short: it sets KPC_MAX_CRAWL_DELAY (900 s at most) for that one run, which reads only
# the parks waiting on such sites. The nightly walk keeps kpc_manners' own 120 s (kpc_manners.py itself is frozen, N15).
try:
    _KM.MAX_CRAWL_DELAY = max(_KM.MAX_CRAWL_DELAY, min(900.0, float(os.environ.get('KPC_MAX_CRAWL_DELAY') or 0)))
except ValueError:
    pass

JOB = 'KPC park page reader'
GET_MAX_SECONDS = 90  # wall-clock cap on one download; a slow trickle cannot run past this
SAVE_EVERY_SECONDS = 30         # 22 Nov: how often the facts and state are written during a walk (also on stop, error and end)
KEEP_ON_SKIP = ('refused', 'resting', 'script-built')   # a read that says nothing new keeps the earlier facts (21 Nov)


def load_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(path, obj, only_if_changed=False):
    p = pathlib.Path(path)
    text = json.dumps(obj, ensure_ascii=False, indent=1) + '\n'
    if only_if_changed and p.is_file():
        try:
            if p.read_text(encoding='utf-8') == text:
                return False
        except OSError:
            pass
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')   # 22 Nov: written whole, then put in place: a reader stopped mid-write never leaves half a file
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, p)
    return True


def park_row(row):
    """data/parkinfo row: [name, website, type, activation, access, lat, lon, activations, attempts, qsos]."""
    row = list(row or [])
    while len(row) < 10:
        row.append(None)
    return {'name': row[0] or '', 'website': row[1] or '', 'type': row[2] or '',
            'lat': row[5], 'lon': row[6], 'qsos': row[9] or 0}


KY_FROM_SAVED = ('US-KY',)


def _saved_area(root, area):
    """POTA's saved park list for one area, as parkinfo rows. Type from data/docs when that has the park."""
    import gzip
    f = root / 'pota' / 'saved' / 'parks' / f'{area}.json.gz'
    if not f.is_file():
        return {}
    try:
        doc = json.loads(gzip.open(f).read().decode('utf-8'))
    except (OSError, ValueError):
        return {}
    kinds = {ref: (row or {}).get('t') or '' for ref, row in ((load_json(root / 'docs' / f'{area}.json', {}) or {}).get('parks') or {}).items()}
    parks = {}
    for row in doc.get('data') or []:
        ref = row.get('reference')
        if not ref:
            continue
        parks[ref] = park_row([row.get('name'), row.get('website'), kinds.get(ref, ''), None, None, row.get('latitude'),
                               row.get('longitude'), row.get('activations'), row.get('attempts'), row.get('qsos')])
        parks[ref]['area'] = area
    return parks


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
    # 19 Nov (Opus): data/parkinfo leaves Kentucky out on purpose (its own bots keep KY), so the first by-hand Kentucky run read
    # nothing. Kentucky comes from POTA's saved list (data/pota/saved/parks/US-KY.json.gz), its type from data/docs/US-KY.json.
    for area in KY_FROM_SAVED:
        if area in areas:
            continue
        parks = _saved_area(root, area)
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


FOUND_BY = 'bot: page reader'


def choose_link(ref, row, web, docs):
    """POTA's link (first official host), else web, else the docs page. Other addresses are counted, not opened.
    23 Nov (rule sheet L): a page the own-page finder found SURE for a park whose POTA link was dead or only the agency's
    front page ('web_by' starts 'bot: page reader') is read in its place."""
    w = web.get(ref) or {}
    if isinstance(w, dict) and w.get('web') and str(w.get('web_by') or '').startswith(FOUND_BY):
        return w['web'], 'found', 0
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


# 23 Nov (job 10): the address KEY keeps the query that names the page. Before, '?parkId=98' and '?page_id=623' were dropped, so
# every park page of a site that numbers its pages fell into ONE key: one page fetched for all of them (Oregon State Parks 162
# parks, California State Parks 253, Parks Canada historic sites 385, Minnesota DNR 233 ... about 2,000 parks), each called a
# page 'shared' by many parks, and the kept copies written over each other. Tracking and language bits are still left off.
URL_KEY_RULE = W.URL_KEY_RULE
TRACKING_Q = re.compile(r'^(utm_\w+|fbclid|gclid|msclkid|mc_[ce]id|_ga|_gl|sessionid|jsessionid|phpsessid|cfid|cftoken|lang|language|locale|hl)$', re.I)


def norm_url(url):
    p = urllib.parse.urlparse(url or '')
    host = (p.netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    path = (p.path or '').rstrip('/')
    q = sorted((k.lower(), v) for k, v in urllib.parse.parse_qsl(p.query or '', keep_blank_values=True) if not TRACKING_Q.match(k))
    return host + path + ('?' + urllib.parse.urlencode(q) if q else '')


def kept_manifest(path):
    """The kept pages' manifest, less the copies saved under the OLD address key (a numbered page saved before 23 Nov 'q1'
    shares its file with every other page of that site: its content is not this page's)."""
    man = load_json(path, {}) or {}
    pages = man.get('pages') or {}
    stale = [u for u, rec in pages.items() if '?' in str(u) and (rec or {}).get('kr') != URL_KEY_RULE]
    for u in stale:
        pages.pop(u, None)
    man['pages'] = pages
    return man


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

    def get(self, url, rng=None, deadline=None, max_time=None):
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


class KeeperCopyGetter:
    """21 Nov: read the keeper's saved copy of a page first (the same manifest format as the fixtures: pages {url: {file,
    status, type, final}}). A page the keeper holds is never asked of the agency again. A page it does not hold goes to
    the live getter (kpc_manners, robots.txt by our own parser, deadline and max_time), or, with no live getter, is a miss."""

    def __init__(self, manifest, root, live=None):
        self.copy = FixtureGetter(manifest, root)
        self.live = live
        self.calls = []
        self.from_copy = 0

    def links_for(self, url):
        return self.copy.links_for(url) if self.copy._rec(url) is not None else []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        if self.copy._rec(url) is not None:
            self.from_copy += 1
            return self.copy.get(url, rng=rng)
        if self.live is None:
            return 'not-in-copy', {}, b'', url
        return self.live.get(url, rng=rng, deadline=deadline, max_time=max_time)

    def browser_html(self, url):
        return self.live.browser_html(url) if self.live is not None and hasattr(self.live, 'browser_html') else ''

    def resting(self):
        return self.live.resting() if self.live is not None and hasattr(self.live, 'resting') else {}


class PageKeeper:
    """23 Nov 2026 (owner: "stop rerun and rerun"): every page the reader fetches is kept on the PC, packed, next to the facts
    (a pages-kept folder beside out: <2 letters>/<name>.gz and one manifest.json in the keeper-copy format). A later fix to what the reader
    takes from a page is then run over the kept pages (read --reextract): no site is asked again. Keeping never stops a
    run: any disk error is counted and passed over. Nothing kept is ever uploaded (the upload pack takes the facts only)."""
    MAX_BYTES = 3_000_000

    def __init__(self, folder, today):
        self.root = pathlib.Path(folder)
        self.today = today
        self.man_path = self.root / 'manifest.json'
        self.man = load_json(self.man_path, {}) or {}
        self.man.setdefault('pages', {})
        self.kept = self.errors = self.unsaved = 0

    def keep(self, url, final, status, headers, body, ref='', built=False):
        try:
            if status != 200 or not isinstance(body, (bytes, bytearray)) or not body or len(body) > self.MAX_BYTES:
                return
            import gzip, hashlib
            ctype = ''
            if isinstance(headers, dict):
                ctype = str(headers.get('content-type') or headers.get('Content-Type') or '')
            name = hashlib.sha1(norm_url(url).encode('utf-8')).hexdigest()[:20]
            rel = f'{name[:2]}/{name}.gz'
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = bytes(body)
            path.write_bytes(raw if raw[:2] == b'\x1f\x8b' else gzip.compress(raw, 6))
            rec = {'file': rel, 'status': 200, 'type': ctype or 'text/html', 'final': final or url, 'date': self.today, 'kr': URL_KEY_RULE}
            if ref: rec['ref'] = ref
            if built: rec['built'] = True
            self.man['pages'][url] = rec
            self.kept += 1
            self.unsaved += 1
            if self.unsaved >= 40:
                self.save()
        except OSError:
            self.errors += 1

    def save(self):
        try:
            if self.unsaved:
                self.root.mkdir(parents=True, exist_ok=True)
                save_json(self.man_path, self.man)
                self.unsaved = 0
        except OSError:
            self.errors += 1


def request_url(url):
    """The address as it is sent: spaces, control and non-ASCII characters escaped; an address already escaped is unchanged."""
    return urllib.parse.quote(url or '', safe="%:/?#[]@!$&'()*+,;=~")


class LiveGetter:
    def __init__(self, state):
        resting = state.get('hosts') if isinstance(state.get('hosts'), dict) else None
        self.M = Manners(JOB, resting)
        self.calls = []

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append(url)
        # 21 Nov: a link with a space or other unsafe character ('...query=38.2, -106.7') is sent escaped; unescaped,
        # urllib raised InvalidURL and the park was skipped on every run
        return self.M.get(request_url(url), rng=rng, deadline=deadline, max_time=max_time)

    def browser_html(self, url):
        """22 Nov: a page that builds itself, opened in the browser (BROWSER=1 and Playwright installed), same manners."""
        if os.environ.get('BROWSER') != '1':
            return ''
        from kpc_manners import browser_html
        return browser_html(request_url(url), self.M)

    def resting(self):
        return self.M.resting()


REFUSALS_FOR_HOST = 10  # 22 Nov 11:56 PM (owner: "U sure we are getting refused"): 3 put whole sites aside (BLM: 3 pages refused, 723 parks never asked); now 10 DIFFERENT pages (401 / 403 / a wall)


def _refusal_rule(state):
    """21 Nov: one refused page used to put its whole site aside for 30 days without asking again (751 'refused' parks on the
    PC, about 25 really asked). A state saved under the old rule forgets those one-page refusals once, so each site is asked
    again, politely; every refusal is still honoured for its own page."""
    if state.get('refusal_rule') != REFUSALS_FOR_HOST:
        state['refused'] = {}
        state['refusal_pages'] = {}
        state['refusal_rule'] = REFUSALS_FOR_HOST


def _refused_until(state, host, today):
    _refusal_rule(state)
    when = (state.get('refused') or {}).get(host)
    if not when:
        return False
    try:
        day = datetime.date.fromisoformat(when)
        now = datetime.date.fromisoformat(today)
    except ValueError:
        return False
    return (now - day).days < R.REFUSAL_DAYS


def _remember_refusal(state, host, today, url=''):
    """A refused page is counted for its site; the site is put aside once REFUSALS_FOR_HOST different pages refused."""
    _refusal_rule(state)
    pages = state.setdefault('refusal_pages', {}).setdefault(host, [])
    u = norm_url(url) if url else ''
    if u and u not in pages:
        pages.append(u)
        del pages[:-REFUSALS_FOR_HOST]
    if not url or len(pages) >= REFUSALS_FOR_HOST:
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
    if R.is_search_or_list_url(url):
        return 'list', "the address is a search or list page, not this park's own page"
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


LIST_RULE = W.LIST_RULE   # 23 Nov: a list / shared page is followed to the park's own link, or its row is read; older reads are done again


def _park_link(links, pota_name, list_url):
    """23 Nov (owner: "the ones with several parks can we get on the right page?"): on a page many parks share, the ONE link
    whose words are this park's name (same, or same core) on an official site. Two different links naming it: none (unsure)."""
    hits = {}
    base = norm_url(list_url)
    for link, words in links or []:
        if not link or not words or not str(link).startswith(('http://', 'https://')):
            continue
        n = norm_url(link)
        if n == base or not R.official_host(link) or R.is_agency_home(link):
            continue
        if R.compare_names(' '.join(str(words).split()), pota_name) in ('same', 'same-core'):
            hits.setdefault(n, link)
    return next(iter(hits.values())) if len(hits) == 1 else ''


def _list_row(text, ref, refs_here, area_parks):
    """23 Nov: a list page with no link of its own (a table of every WMA): the one line that names this park, and the lines
    under it up to the next park of the list (at most 2). The name, the words of the row and nothing else. Returns
    (row text, the name as the page writes it) or ('', '') when the park is named on no line, or on more than one."""
    core = R.name_core((area_parks.get(ref) or {}).get('name'))
    if not text or not core or len(core) < 4:
        return '', ''
    words = core.split()
    rx = re.compile(r'(?<![a-z0-9])' + r'[^a-z0-9]+'.join(re.escape(w) for w in words) + r'(?![a-z0-9])', re.I)
    others = []
    for r in refs_here or []:
        if r == ref:
            continue
        oc = R.name_core((area_parks.get(r) or {}).get('name'))
        if oc and oc != core:
            others.append(re.compile(r'(?<![a-z0-9])' + r'[^a-z0-9]+'.join(re.escape(w) for w in oc.split()) + r'(?![a-z0-9])', re.I))
    lines = [ln.strip() for ln in text.splitlines()]
    def names_other(ln, own_span=None):
        """Another park of the list is named on this line. A shorter name that sits inside ours does not count
        (Blue Ridge inside Blue Ridge North); a longer one that holds ours means the line is the other park's."""
        for o in others:
            for m in o.finditer(ln):
                if own_span and own_span[0] <= m.start() and m.end() <= own_span[1]:
                    continue
                return True
        return False
    hits = []
    for i, ln in enumerate(lines):
        m = rx.search(ln)
        if m and not names_other(ln, (m.start(), m.end())):
            hits.append((i, m.group(0)))
    if len(hits) != 1:
        return '', ''
    i, written = hits[0]
    row = [lines[i]]
    for ln in lines[i + 1:i + 3]:
        if not ln or names_other(ln) or rx.search(ln):
            break
        row.append(ln)
    return '\n'.join(row), written


def read_parks(areas, web, docs, truth, getter, state, today, refs=None, areas_only=None,
               max_requests=1500, max_per_park=R.MAX_PER_PARK, max_parks=None, on_park=None,
               refresh_days=W.REFRESH_DAYS, deadline=None, out_dir=None, state_path=None,
               get_max_seconds=GET_MAX_SECONDS, quiet=False, started=None, keeper=None, reextract=False):
    """Read every chosen park. Returns {area: {ref: fact}} and the request count.
    refs, when given, is the worklist order across areas. A fresh fingerprint is not fetched again.
    A page older than refresh_days is fetched; the same fingerprint is not parsed again.
    When out_dir is set, facts and state are written after every park (only if they changed),
    so a run that is cut off keeps what it already read."""
    state.setdefault('hosts', {})
    state.setdefault('refused', {})
    state.setdefault('dead', {})
    state.setdefault('read', {})
    state.setdefault('fingerprints', {})
    state['errors'] = {}  # this run's skipped parks only
    out = {}
    requests = 0
    done = 0
    cache = {}  # norm url -> fetched page dict
    cur = {}    # the park being read (for the page keeper)
    started = time.time() if started is None else started

    def budget_left():
        return requests < max_requests and (deadline is None or time.time() < deadline)

    def time_up():
        return deadline is not None and time.time() >= deadline

    def is_deadline(page):
        # 21 Nov: 'err:deadline' comes back both when the run's time is up and when ONE download passed its own cap
        # (get_max_seconds). Only the first ends the run; a download cut at its cap is one slow page (read as resting).
        st = (page or {}).get('status')
        hit = st == 'err:deadline' or (isinstance(st, str) and str(st).startswith('err:deadline'))
        return hit and time_up()

    def progress(area, count, note=''):
        if quiet:
            return
        elapsed = int(time.time() - started)
        line = f'{area}  {count} park(s)  {elapsed // 60} min {elapsed % 60}s'
        if note:
            line += f'  {note}'
        print(line, flush=True)

    saved_at = [0.0]
    # 23 Nov (owner 'Yes', audit 2 MUST 1): a park counts as read recently only when its facts are really in the out folder.
    # Before, a skipped park got today's date (so its 30-day clock never ran out) and, with no earlier fact, an empty stub.
    _old = {}

    def has_old(area, ref):
        if not out_dir:
            return True
        if area not in _old:
            _ps = load_json(pathlib.Path(out_dir) / 'facts' / f'{area}.json', {}).get('parks') or {}
            # an empty stub saved before this fix is not facts: that park is read again
            _old[area] = {r for r, f in _ps.items() if not (isinstance(f, dict) and f.get('unchanged'))}
        return ref in _old[area]

    def save_progress(index, force=False):
        if not out_dir:
            return
        state['left'] = sorted(r for _, r in sequence[index + 1:])   # 21 Nov: sorted, so a saved state never shows the private read order
        # 22 Nov (owner 5:12 PM "speed up going through the done looked parks"): each save re-reads and rewrites every touched
        # area's facts file (Canada's is 19 MB) and the 5 MB state; after EVERY park that made a run crawl through parks it only
        # skips. Now at most every SAVE_EVERY_SECONDS, plus a save on any stop, any reader error and at the end of the walk.
        now = time.monotonic()
        if not force and now - saved_at[0] < SAVE_EVERY_SECONDS:
            return
        saved_at[0] = now
        _write_progress(out_dir, out, state, state_path)

    def fetch(url, rng=None):
        nonlocal requests
        if not url or not budget_left():
            return None
        host = R.host_of(url)
        if R.is_wdpa(url):
            # never WDPA (21 Nov): not asked, not counted as a request
            return {'url': url, 'final': url, 'status': 'refused', 'kind': 'refused', 'text': '', 'links': [],
                    'fingerprint': '', 'html': '', 'title': '', 'heading': '', 'skipped': 'wdpa'}
        if host and _refused_until(state, host, today):
            return {'url': url, 'final': url, 'status': 'refused', 'kind': 'refused', 'text': '', 'links': [],
                    'fingerprint': '', 'html': '', 'title': '', 'heading': '', 'skipped': 'refused'}
        key = norm_url(url) + (f'|rng{rng[0]}-{rng[1]}' if rng else '')
        if key in cache:
            return cache[key]
        requests += 1
        try:
            st, headers, body, final = getter.get(url, rng=rng, deadline=deadline, max_time=get_max_seconds)
        except TypeError:
            st, headers, body, final = getter.get(url, rng=rng)
        from_copy = isinstance(getter, KeeperCopyGetter) and getter.copy._rec(url) is not None
        if keeper is not None and not rng and not from_copy:
            keeper.keep(url, final or url, st, headers, body, ref=cur.get('ref') or '')   # 23 Nov: the page is kept for later fixes
        extra = getter.links_for(url) if hasattr(getter, 'links_for') else []
        vis = R.visible_of(body, headers, final or url, extra)
        kind = _kind_of_status(st, vis.get('text'), final or url, is_pdf=bool(vis.get('pdf')))
        if kind == 'html' and R.unfilled_template(vis.get('html')):
            kind = 'script-built'     # 23 Nov: a heading still a script template (Minnesota DNR): open it in the browser
        browsed = False
        if kind == 'script-built' and not rng and hasattr(getter, 'browser_html') and budget_left():
            # 22 Nov: a page that builds itself is opened once in the browser (same manners, counted as a request) and read
            # like any other page; when the browser is off, missing, refused or the page is still empty, it stays for a person
            requests += 1
            built = getter.browser_html(final or url) or ''
            if built:
                vis2 = R.visible_of(built.encode('utf-8'), {'content-type': 'text/html; charset=utf-8'}, final or url, extra)
                text2 = (vis2.get('text') or '').strip()
                if len(text2) >= 400 and not R.WALL.search(text2):
                    vis, kind, browsed = vis2, 'html', True
                    if keeper is not None:
                        keeper.keep(url, final or url, 200, {'content-type': 'text/html; charset=utf-8'}, built.encode('utf-8'),
                                    ref=cur.get('ref') or '', built=True)
        if kind == 'refused' and st in (401, 403) and not rng and not from_copy and hasattr(getter, 'browser_html') and budget_left():
            # 24 Nov 2026 (owner 7:32 AM, P-2 "yes"): a page that answers our plain reader with 401 / 403 gets ONE try in the PC's
            # browser (BROWSER=1), with every manner of the browser read: the same User-Agent, robots.txt, Crawl-delay, the slow-host
            # budget and the pace. A browser that also gets a wall, an empty page or nothing leaves the refusal as it was.
            requests += 1
            built = getter.browser_html(final or url) or ''
            if built:
                vis2 = R.visible_of(built.encode('utf-8'), {'content-type': 'text/html; charset=utf-8'}, final or url, extra)
                text2 = (vis2.get('text') or '').strip()
                if len(text2) >= 400 and not R.WALL.search(text2):
                    vis, kind, browsed = vis2, 'html', True
                    if keeper is not None:
                        keeper.keep(url, final or url, 200, {'content-type': 'text/html; charset=utf-8'}, built.encode('utf-8'),
                                    ref=cur.get('ref') or '', built=True)
        if kind == 'refused' and not from_copy and not (isinstance(st, str) and robots_block(st)):
            # 21 Nov: robots.txt is read for each address (its rules are per path), so a robots 'no' is never remembered for the
            # whole site; a 401 / 403 / wall counts towards putting the site aside (REFUSALS_FOR_HOST different pages)
            _remember_refusal(state, R.host_of(final or url) or host, today, final or url)
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
                'headings': vis.get('headings') or [],
                'fingerprint': R.fp_of(vis.get('text') or ''), 'dead_twice': vis_dead, 'family': R.family_of(final or url),
                'thin': len((vis.get('text') or '').strip()) < 400}
        if browsed:
            page['browser'] = True
        if from_copy:
            page['kept_date'] = (getter.copy._rec(url) or {}).get('date') or ''
        cache[key] = page
        return page

    groups = {}
    for area, parks in areas.items():
        if areas_only and area not in areas_only:
            continue
        chosen = {ref: choose_link(ref, row, web, docs)[0] for ref, row in parks.items()}
        groups[area] = _shared_map(chosen)
        out.setdefault(area, {})
    if refs:
        loc = {}
        for area, parks in areas.items():
            if areas_only and area not in areas_only:
                continue
            for ref in parks:
                loc[ref] = area
        sequence = [(loc[r], r) for r in refs if r in loc]
    else:
        sequence = [(area, ref) for area, parks in areas.items()
                    if not (areas_only and area not in areas_only) for ref in parks]

    def stop(reason, index):
        if keeper is not None:
            keeper.save()
        state['stopped'] = reason
        state['left'] = sorted(r for _, r in sequence[index:])   # sorted: the private read order is never saved
        if reason == 'minutes' and index < len(sequence):
            area_now = sequence[index][0]
            c = dict(state.get('cutoff') or {})
            c[area_now] = c.get(area_now, 0) + 1
            state['cutoff'] = c
            if c[area_now] >= 2:
                stuck = list(state.get('stuck') or [])
                if area_now not in stuck:
                    stuck.append(area_now)
                state['stuck'] = stuck
        if out_dir:
            _write_progress(out_dir, out, state, state_path)
        return out, requests

    _t0p = time.time()
    for index, (area, ref) in enumerate(sequence):
        if index % 25 == 0: print(_kpc_bar(index, len(sequence), f'pages read ({area})', _t0p), flush=True)
        parks = areas[area]
        if max_parks is not None and done >= max_parks:
            return stop('parks', index)
        row = parks[ref]
        cur['ref'] = ref
        url, src, others = choose_link(ref, row, web, docs)
        progress(area, done, 'reading')
        if on_park:
            on_park(done + 1, ref)
        # A page read inside the refresh window is not fetched again. The caller keeps the old fact.
        prev = (state.get('read') or {}).get(ref) or {}
        age = W.age_days(prev.get('date'), today) if prev.get('date') else None
        fresh = bool(url and prev.get('fingerprint') and prev.get('url') == url and age is not None and age < refresh_days
                     and has_old(area, ref))
        if len((groups.get(area) or {}).get(norm_url(url), [ref])) >= 2 and prev.get('list_rule') != LIST_RULE:
            fresh = False   # 23 Nov: read before shared pages were followed to the park's own link
        if reextract:
            fresh = False   # 23 Nov: reading the kept pages again with today's finders
        if url and '?' in url and prev.get('key_rule') != URL_KEY_RULE:
            fresh = False   # 23 Nov 'q1': a numbered page read under the old address key was another park's page
        if fresh:
            out[area][ref] = {'ref': ref, 'unchanged': True, 'page': {'fingerprint': prev.get('fingerprint'),
                             'kind': prev.get('kind'), 'read': today, 'seen': today}, 'questions': []}
            done += 1   # the read date stays the day of the real read (audit 2 MUST 1)
            save_progress(index)
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
            save_progress(index)
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
            save_progress(index)
            continue
        if time_up():
            return stop('minutes', index)
        if not budget_left():
            return stop('requests', index)
        main = fetch(url)
        if main is None or is_deadline(main):
            return stop('minutes' if (time_up() or is_deadline(main)) else 'requests', index)
        if main.get('kind') in KEEP_ON_SKIP and prev.get('date'):
            # 21 Nov: a refused, robots-blocked, resting or script-built read says nothing new about the park. The facts
            # read before stay exactly as they were (merge_unchanged keeps the bytes), and the park is asked again next run.
            skipped = R.build_facts(ref, area, pota, parks, asked, [main], today, [], 'unknown', 'the read was skipped',
                                    read_blocks=False)
            skipped['page']['kind'] = main.get('kind')
            out[area][ref] = {'ref': ref, 'unchanged': True, 'keep_exact': True, 'fallback': skipped,
                              'page': {'kind': main.get('kind'), 'read': today}, 'questions': []}
            done += 1
            save_progress(index)
            continue
        if (not reextract and prev.get('fingerprint') and prev.get('url') == url and prev.get('fingerprint') == main.get('fingerprint')
                and has_old(area, ref)
                and (len((groups.get(area) or {}).get(norm_url(url), [ref])) < 2 or prev.get('list_rule') == LIST_RULE)):
            # same text: keep the old facts, no new question
            out[area][ref] = {'ref': ref, 'unchanged': True, 'page': {'fingerprint': main.get('fingerprint'),
                             'kind': prev.get('kind') or main.get('kind'), 'read': today, 'seen': today}, 'questions': []}
            kept = dict(prev)
            kept['date'] = today
            kept['fingerprint'] = main.get('fingerprint')
            kept['key_rule'] = URL_KEY_RULE
            state['read'][ref] = kept
            state['fingerprints'][norm_url(url)] = main.get('fingerprint')
            done += 1
            save_progress(index)
            continue
        try:
            pages = [main]
            used = 1
            kind = main.get('kind')
            text = main.get('text') or ''
            mates = [r for r in (groups.get(area) or {}).get(norm_url(url), []) if r != ref]
            refs_here = (groups.get(area) or {}).get(norm_url(url), [ref])
            own_is, own_why = _own_is(url, refs_here, parks, text, row['name'])
            followed, listed_row, list_fp = '', '', main.get('fingerprint') or ''
            if own_is in ('list', 'shared') and kind in ('html', 'pdf'):
                # 23 Nov: get on the park's own page. The one link naming this park is read in place of the list (one request)
                pick = _park_link(main.get('links'), row['name'], url)
                if pick and used < max_per_park and budget_left():
                    got = fetch(pick)
                    used += 1
                    if got is None or is_deadline(got):
                        if time_up() or is_deadline(got):
                            return stop('minutes', index)
                    elif got.get('kind') in ('html', 'pdf') and (got.get('text') or '').strip():
                        main, pages, kind, text, followed = got, [got], got.get('kind'), got.get('text') or '', pick
                        own_is, own_why = 'own', 'followed from the page the parks share: its link names this park'
                        mates = []
                if not followed and own_is == 'list':
                    # no link of its own: the list's one row that names this park
                    rtxt, written = _list_row(text, ref, refs_here, parks)
                    if rtxt:
                        listed_row = rtxt
                        pages = [dict(main, text=rtxt, title='', heading=written, og='', jsonld='', links=[], html='')]
                        own_is, own_why = 'list-row', 'the page lists many parks; only the one row naming this park is read'
            read_blocks = own_is not in ('agency-home', 'list') and kind not in ('refused', 'resting', 'dead', 'script-built')
            fam = main.get('family') or {}
            # one facts page, one directions page, one map. Never past max_per_park.
            if read_blocks and own_is != 'list-row' and used < max_per_park and budget_left():
                extra = _extra_urls(followed or url, main, fam)
                for eu, role in extra:
                    if used >= max_per_park or not budget_left():
                        break
                    if role == 'map':
                        got = fetch(eu, rng=(0, R.PDF_FIRST - 1))
                    else:
                        got = fetch(eu)
                    used += 1
                    if got is None or is_deadline(got):
                        if time_up() or is_deadline(got):
                            return stop('minutes', index)
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
                fact['confirm'] = R.confirm_block(fact, url, main.get('final') or '', '')
                fact['questions'] = R.questions_for(fact)
            fact['questions'] = R.questions_for(fact)
            drafts = R.evidence_drafts(fact)
            fact['evidence_draft'] = drafts[0] if drafts else None
            fact['evidence_drafts'] = drafts
            out[area][ref] = fact
            when = today
            if reextract and main.get('kept_date'):
                when = main['kept_date']          # the day the page was really read
                fact['page']['read'] = when
            if followed:
                fact['asked']['followed'] = followed
            if src == 'found':
                # 23 Nov (rule sheet L): the page the own-page finder found; its note travels with every later read
                fd = (state.get('found') or {}).get(ref)
                if isinstance(fd, dict) and fd.get('level') == 'sure':
                    fact['found'] = {k: fd.get(k) for k in ('url', 'how', 'level', 'why', 'for', 'date', 'rule', 'was') if k in fd}
                    if fd.get('was'):
                        fact['asked']['was'] = fd['was']
            if listed_row:
                fact['asked']['row'] = R.clip(listed_row)
            state['read'][ref] = {'url': url, 'fingerprint': main.get('fingerprint') or '', 'date': when,
                                  'kind': fact['page']['kind'], 'final': main.get('final'), 'key_rule': URL_KEY_RULE}
            if len(refs_here) >= 2:
                state['read'][ref]['list_rule'] = LIST_RULE
            if followed:
                state['read'][ref]['followed'] = followed
            if list_fp:
                state['fingerprints'][norm_url(url)] = list_fp   # the page POTA links (the list), never the followed one
        except Exception as err:  # noqa: BLE001  19 Nov 8 PM: one bad page never stops the other parks
            # nothing is saved for this park, so the next run reads it again; the run says which park and why
            out[area].pop(ref, None)
            state.setdefault('errors', {})[ref] = f'{type(err).__name__}: {err}'[:300]
            print(f'::warning title=Reader skipped a park::{ref}: {type(err).__name__}: {err}'[:400], flush=True)
            save_progress(index, force=True)
            continue
        done += 1
        save_progress(index)
    state['left'] = []
    state['stopped'] = ''
    if keeper is not None:
        keeper.save()
    if out_dir:
        _write_progress(out_dir, out, state, state_path)   # the end of the walk: always saved (save_progress may have waited)
    finished = {a for a, _ in sequence}
    if finished and state.get('cutoff'):
        c = dict(state['cutoff'])
        for a in finished:
            c.pop(a, None)
        state['cutoff'] = c
    if isinstance(getter, LiveGetter) or (isinstance(getter, KeeperCopyGetter) and getter.live is not None):
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
        # origin with scheme and host (19 Nov 8 PM: the urlunsplit line here took urlparse's six parts and stopped the run)
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


def _write_progress(out_dir, facts_by_area, state, state_path):
    """Write facts and state after a park. Only rewrite a file when its contents changed."""
    if not out_dir:
        return
    merge_unchanged(out_dir, facts_by_area)
    root = pathlib.Path(out_dir)
    for area, parks in facts_by_area.items():
        path = root / 'facts' / f'{area}.json'
        save_json(path, {'area': area, 'reader': R.READER, 'parks': area_parks_to_save(path, parks)}, only_if_changed=True)
    if state_path:
        save_json(state_path, state, only_if_changed=True)


def pick_walk_area(areas, done, state, area_refs=None, rank=None):
    """Choose the next US area for a timed walk.

    areas: sorted area codes. done: area codes that already have a facts file.
    state: the reader's state (left, stopped, cutoff, stuck, run, run_area).
    area_refs: {area: set(park refs)} so leftover refs can be placed in an area.
    Returns (area, why, state). After two cut-off runs on the same state, that
    state is skipped and named in why for a person.
    """
    state = dict(state or {})
    cutoff = dict(state.get('cutoff') or {})
    stuck = [a for a in (state.get('stuck') or []) if a]
    areas = list(areas or [])
    if rank:   # 21 Nov: the coverage ranking (biggest agencies first); areas it does not name keep their order after it
        pos = {a: i for i, a in enumerate(rank)}
        areas = sorted(areas, key=lambda a: (pos.get(a, len(pos)), areas.index(a)))
    done = set(done or [])
    area_refs = area_refs or {}

    left = set(state.get('left') or [])
    unfinished = ''
    if left:
        for a in areas:
            refs = set(area_refs.get(a) or [])
            if refs and (left & refs):
                unfinished = a
                break
        if not unfinished:
            run_area = state.get('run_area') or ''
            if run_area in areas:
                unfinished = run_area

    if unfinished and state.get('run') == 'in-progress':
        cutoff[unfinished] = cutoff.get(unfinished, 0) + 1
        state['cutoff'] = cutoff
        state['run'] = 'killed'
        if cutoff[unfinished] >= 2 and unfinished not in stuck:
            stuck.append(unfinished)
            state['stuck'] = stuck

    def next_todo(skip=()):
        skip = set(skip) | set(stuck)
        return [a for a in areas if a not in done and a not in skip]

    if unfinished and cutoff.get(unfinished, 0) >= 2:
        if unfinished not in stuck:
            stuck.append(unfinished)
            state['stuck'] = stuck
        todo = next_todo(skip={unfinished})
        out = todo[0] if todo else ''
        why = f'{unfinished}: skipped after two cut-off runs; a person should look at it'
        why += f'. Next: {out}' if out else '. No other state is left to read'
        return out, why, state

    if unfinished:
        return unfinished, f'{unfinished}: left unfinished by the last run', state

    todo = next_todo()
    out = todo[0] if todo else ''
    if out:
        why = f'{out}: the next state with no facts ({len(todo)} left)' + (' (coverage ranking: biggest agencies first)' if rank else '')
    else:
        why = 'every state has facts: nothing to read'
        if stuck:
            why += f'. Stuck, for a person: {", ".join(stuck)}'
    return out, why, state


ORDER_FILE = pathlib.Path(__file__).resolve().parents[1] / 'park-pages-order.json'


def coverage_order(csv_path):
    """The walk order from the coverage list (area, agency_web_domain, pota_parks ...; biggest rows first): each area at the
    place of its biggest agency row that has a web link. '(no web link)' rows have nothing to read and do not rank."""
    import csv
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    def n(r):
        try:
            return int(str(r.get('pota_parks') or '0').strip())
        except ValueError:
            return 0
    rows = [r for r in rows if (r.get('agency_web_domain') or '').strip() and 'no web link' not in r['agency_web_domain']]
    rows.sort(key=lambda r: -n(r))
    order, top = [], {}
    for r in rows:
        a, d = (r.get('area') or '').strip(), r['agency_web_domain'].strip()
        if not a:
            continue
        if a not in order:
            order.append(a)
        top.setdefault(a, [])
        if len(top[a]) < 3:
            top[a].append([d, n(r)])
    # areas whose rows are all '(no web link)' in the coverage list come after, biggest first: POTA's own list may still
    # hold a link for some of their parks, and the reader reads those
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        allrows = list(csv.DictReader(f))
    tot = {}
    for r in allrows:
        a = (r.get('area') or '').strip()
        if a:
            tot[a] = tot.get(a, 0) + n(r)
    after = sorted((a for a in tot if a not in order), key=lambda a: -tot[a])
    return {'about': 'Page reader walk order: each area ranked by its biggest agency with a web link (coverage list), then the '
                     'areas the list shows with no web link, biggest first. Made by kpc_park_pages.py coverage-order; counts '
                     'and web domains only.',
            'source': os.path.basename(csv_path), 'areas': order + after, 'ranked_by_agency': len(order),
            'top_agencies': top}


def walk_rank(path=None):
    """The ranked area list, or [] when the order file is missing or unreadable (the walk then keeps its old order)."""
    doc = load_json(path or ORDER_FILE, {})
    areas = doc.get('areas') if isinstance(doc, dict) else None
    return [a for a in areas if isinstance(a, str)] if isinstance(areas, list) else []


CONFIRM_FIELDS = ('agency_id', 'size', 'manager', 'address', 'coords', 'map_link')


def confirm_counts(facts_by_area):
    """Public counts only: per state and per agency web host, how many parks have each confirming fact (and how many unclear)."""
    by_state, by_agency = {}, {}
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            c = (fact or {}).get('confirm')
            if not isinstance(c, dict):
                continue
            host = R.base_host((fact.get('page') or {}).get('final_host') or (fact.get('page') or {}).get('host') or '') or '(no host)'
            for bucket, key in ((by_state, area), (by_agency, host)):
                row = bucket.setdefault(key, {'parks': 0})
                row['parks'] += 1
                for k in CONFIRM_FIELDS:
                    v = c.get(k)
                    if isinstance(v, dict) and v.get('unclear'):
                        row[k + ' unclear'] = row.get(k + ' unclear', 0) + 1
                    elif v:
                        row[k] = row.get(k, 0) + 1
    return {'about': 'Confirming facts the page reader found, counted by state and by agency web host. Counts only.',
            'confirm': R.CONFIRM, 'by_state': dict(sorted(by_state.items())),
            'by_agency': dict(sorted(by_agency.items(), key=lambda kv: -kv[1]['parks']))}


def area_parks_to_save(path, parks):
    """21 Nov: the parks to write for one area: every park already in the file, with this run's parks over them. Before, the
    file was replaced by this run's parks alone, so a run that stopped part way (or saved after each park) wiped the facts of
    every park it had not reached yet, and a park re-read as unchanged lost its full fact (only a stub was left)."""
    old = load_json(path, {}).get('parks') or {}
    keep = dict(old)
    keep.update(parks)
    return keep


def write_facts(out_dir, facts_by_area):
    root = pathlib.Path(out_dir)
    for area, parks in facts_by_area.items():
        path = root / 'facts' / f'{area}.json'
        save_json(path, {'area': area, 'reader': R.READER, 'parks': area_parks_to_save(path, parks)},
                  only_if_changed=True)


def merge_unchanged(out_dir, facts_by_area):
    """A park marked unchanged keeps the fact already on disk."""
    root = pathlib.Path(out_dir)
    for area, parks in facts_by_area.items():
        path = root / 'facts' / f'{area}.json'
        old = load_json(path, {}).get('parks') or {}
        for ref, fact in list(parks.items()):
            if fact.get('keep_exact'):
                # a skipped read: the earlier fact, byte for byte; with no earlier fact, the skipped one
                parks[ref] = old[ref] if ref in old else fact.get('fallback') or {'ref': ref}
                continue
            if fact.get('unchanged') and ref not in old:
                parks.pop(ref, None)   # audit 2 MUST 1: never an empty stub in place of the facts
                continue
            if fact.get('unchanged') and ref in old:
                kept = old[ref]
                page = dict(kept.get('page') or {})
                page['seen'] = (fact.get('page') or {}).get('read')
                kept = dict(kept)
                kept['page'] = page
                parks[ref] = kept


def add_found(web, state):
    """23 Nov (rule sheet L): the pages this PC's own-page finder found SURE are read as the parks' pages, until the
    official-links bot carries them in parkinfo-web.json. A person's own value is never covered."""
    for ref, t in (state.get('found') or {}).items():
        if not isinstance(t, dict) or t.get('level') != 'sure' or not t.get('url'):
            continue
        e = web.get(ref) if isinstance(web.get(ref), dict) else {}
        if e.get('web') and not str(e.get('web_by') or '').startswith('bot:'):
            continue
        web[ref] = dict(e, web=t['url'], web_by=f"{FOUND_BY} (this PC, {t.get('date') or ''})")
    return web


def _refs_from_args(args):
    refs = []
    if getattr(args, 'refs', ''):
        refs.extend(r.strip() for r in args.refs.split(',') if r.strip())
    if getattr(args, 'refs_file', ''):
        doc = load_json(args.refs_file, [])
        if isinstance(doc, dict):
            doc = doc.get('parks') or doc.get('refs') or []
        for r in doc:
            ref = r if isinstance(r, str) else (r.get('ref') if isinstance(r, dict) else '')
            if isinstance(ref, str) and ref and ref not in refs:
                refs.append(ref)
    return refs


def _prepare(args):
    areas, web, docs, truth = load_data(args.data)
    today = args.today or datetime.date.today().isoformat()
    state_path = args.state or (str(pathlib.Path(args.out) / 'state.json') if args.out else '')
    state = load_json(state_path, {}) if state_path and pathlib.Path(state_path).is_file() else {}
    add_found(web, state)
    areas_only = set(args.areas.split()) if args.areas else None
    known = {ref for parks in areas.values() for ref in parks}
    done_dir = str(pathlib.Path(args.out) / 'lists-done') if args.out else (args.lists_done or '')
    lists = W.load_lists(args.lists, known, done_dir or args.lists_done)
    keys = W.load_keys(args.links) if args.links else {}
    refs = _refs_from_args(args)
    ns_rows = []
    if getattr(args, 'not_sure', ''):
        ns_rows = NS.NotSure(args.not_sure).open_rows(wants=['page facts', 'official size', 'map'])

    def choose(ref, row):
        return choose_link(ref, row, web, docs)[0]

    priority = W.private_refs(getattr(args, 'priority_file', ''), REPO_ROOT)   # 21 Nov: the likely-mismatch list (private)
    confirmed = W.private_refs(getattr(args, 'confirmed_file', ''), REPO_ROOT)   # parks confirmed by their agency id (private)
    order = W.build_worklist(areas, choose, keys, lists, refs, state, today, areas_only=areas_only,
                             refresh_days=args.refresh_days, not_sure=ns_rows, priority=priority, confirmed=confirmed,
                             confirmed_refresh_days=getattr(args, 'confirmed_refresh_days', W.CONFIRMED_REFRESH_DAYS))
    return areas, web, docs, truth, state, state_path, today, areas_only, lists, order


def _finish(args, facts, order, lists, state, state_path, today, requests, old_facts):
    if not args.out:
        return
    root = pathlib.Path(args.out)
    changes = []
    for area, parks in facts.items():
        for ref, fact in parks.items():
            changes.extend(W.change_rows(ref, (old_facts.get(area) or {}).get(ref), fact, today))
    merge_unchanged(args.out, facts)
    write_facts(args.out, facts)
    seen = {i['ref'] for i in order}
    full = list(order) + [{'ref': ref, 'area': area, 'tier': 9, 'why': ''}
                          for area, parks in facts.items() for ref in parks if ref not in seen]
    W.write_tables(args.out, facts, full, lists, today)
    save_json(root / 'confirm-counts.json', confirm_counts(facts))
    W.append_changes(root / 'changes.csv', changes)
    lines = W.render_summary(facts, order, state, today, requests)
    (root / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    save_json(root / 'worklist.json', W.public_order(order, today))   # 21 Nov: private-list parks are counted, not named
    save_json(root / 'run.json', {'reader': R.READER, 'date': today, 'requests': requests,
              'parks': sum(len(v) for v in facts.values()), 'left': len(state.get('left') or []),
              'stopped': state.get('stopped') or ''})
    if state_path:
        save_json(state_path, state)
    if getattr(args, 'not_sure', ''):
        ns = NS.NotSure(args.not_sure)
        NS.note_from_reader(ns, facts, today)
        qsos = {}
        root = load_data(args.data)[0] if args.data else {}
        for parks in root.values():
            for ref, row in parks.items():
                qsos[ref] = row.get('qsos') or 0
        ns.summary(today=today, qsos=qsos)


def cmd_worklist(args):
    areas, web, docs, truth, state, state_path, today, areas_only, lists, order = _prepare(args)
    if args.out:
        save_json(pathlib.Path(args.out) / 'worklist.json', W.public_order(order, today))
    if not args.quiet:
        print(f'Worklist: {len(order)} parks. Lists: {len(lists)}.')
        for row in W.public_order(order)['order'][:20]:
            print(f"{row['tier']} {row['ref']} {row['why']}")
        if len(order) > 20:
            print(f'... {len(order) - 20} more')
    return 0


def cmd_read(args):
    areas, web, docs, truth, state, state_path, today, areas_only, lists, order = _prepare(args)
    if not areas:
        print('No stored parks. Nothing was read.')
        return 0
    keeper = getattr(args, 'keeper_copies', '') or ''
    keep_arg = getattr(args, 'keep_pages', '') or ''
    reextract = bool(getattr(args, 'reextract', False))
    # beside the out folder, never inside it: the PC run file zips everything under out
    kept_dir = keep_arg if keep_arg and keep_arg != 'off' else (str(pathlib.Path(args.out).resolve().parent / 'pages-kept') if args.out else '')
    if reextract:
        # 23 Nov: only the kept pages, never a site. Every park whose page is kept is read again; the others are not touched.
        man = pathlib.Path(kept_dir) / 'manifest.json'
        if not kept_dir or not man.is_file():
            print('No pages are kept yet (the reader keeps them from its next run on). Nothing was read again.')
            return 0
        getter = KeeperCopyGetter(kept_manifest(man), man.parent, None)
        order = [{'ref': ref, 'area': area, 'tier': 0, 'why': 'kept page read again'} for area, parks in sorted(areas.items())
                 if not areas_only or area in areas_only for ref, row in sorted(parks.items())
                 if getter.copy._rec(choose_link(ref, row, web, docs)[0] or '') is not None]
        # 26 Nov 2026 (owner 5:57 PM: 'to save on time ... just do that step only for the ones that might have name mismatches'):
        # with a refs file, only those parks' kept pages are read again
        _only = set(_refs_from_args(args)) if (getattr(args, 'refs_file', '') or getattr(args, 'refs', '')) else None
        if _only is not None:
            order = [row for row in order if row['ref'] in _only]
        args.max_requests = max(args.max_requests, 10 * len(order) + 10)
    elif args.fixtures:
        getter = FixtureGetter(load_json(args.fixtures, {}), pathlib.Path(args.fixtures).parent)
    elif keeper:
        man = pathlib.Path(keeper) / 'manifest.json' if pathlib.Path(keeper).is_dir() else pathlib.Path(keeper)
        live = None if os.environ.get('KPC_NO_NET') == '1' else LiveGetter(state)
        getter = KeeperCopyGetter(load_json(man, {}), man.parent, live)
    elif os.environ.get('KPC_NO_NET') == '1':
        print('No fixtures and the network is closed. Nothing was read.')
        return 0
    else:
        getter = LiveGetter(state)
    # A plain --refs still limits the read, in the worklist's order. With no worklist hits, read nothing new.
    use_list = reextract or bool(args.lists or args.links or args.refs or args.refs_file or args.areas or getattr(args, 'not_sure', '')
                    or getattr(args, 'priority_file', '') or getattr(args, 'confirmed_file', ''))   # 21 Nov: a PC run with only the private lists
    refs = [row['ref'] for row in order] if use_list else None
    if refs is not None and not refs:
        if not args.quiet:
            print('The worklist is empty. Nothing was read.')
        if args.out:
            _finish(args, {}, order, lists, state, state_path, today, 0, {})
        return 0
    total = len(refs) if refs is not None else sum(len(v) for k, v in areas.items() if not areas_only or k in areas_only)
    old_facts = W.load_facts(args.out) if args.out else {}
    run_area = ''
    if areas_only:
        run_area = sorted(areas_only)[0]
    elif order:
        run_area = order[0].get('area') or ''
    state['run'] = 'in-progress'
    if run_area:
        state['run_area'] = run_area
    if state_path:
        save_json(state_path, state)

    # 21 Nov: the count is the park's place on this run's list, which starts at 1 every run. Parks read before (inside the
    # refresh window) are passed over in a moment, so say so first: '1130 of 15000' looked like the reader had started over.
    seen = state.get('read') or {}
    listed = refs if refs is not None else [r for k, v in areas.items() if not areas_only or k in areas_only for r in v]
    before = sum(1 for r in listed if r in seen)
    if not args.quiet:
        print(f'The list has {total:,} parks. {before:,} of them were read before: they are passed over in a moment unless their '
              f'page is due again, so the count runs fast through them. The others are read now.', flush=True)

    def on_park(i, ref):
        if not args.quiet:
            print(f'Park {i:,} of {total:,} on the list ({ref}){"  (read before)" if ref in seen else ""}.', flush=True)

    deadline = time.time() + args.max_minutes * 60 if args.max_minutes else None
    get_max = getattr(args, 'max_get_seconds', None)
    if get_max is None:
        get_max = GET_MAX_SECONDS
    facts, reqs = read_parks(areas, web, docs, truth, getter, state, today, refs=refs, areas_only=areas_only,
                             max_requests=args.max_requests, max_per_park=args.max_per_park, max_parks=args.max_parks,
                             on_park=None if args.quiet else on_park, refresh_days=args.refresh_days, deadline=deadline,
                             out_dir=args.out or None, state_path=state_path or None,
                             get_max_seconds=get_max, quiet=bool(args.quiet), reextract=reextract,
                             keeper=(PageKeeper(kept_dir, today) if kept_dir and not reextract and keep_arg != 'off'
                                     and (keep_arg or isinstance(getter, LiveGetter)
                                          or (isinstance(getter, KeeperCopyGetter) and getter.live is not None)) else None))
    if not state.get('stopped'):
        state['run'] = 'done'
    else:
        state['run'] = 'stopped'
    _finish(args, facts, order, lists, state, state_path, today, reqs, old_facts)
    reqs = _note_pictures(args, facts, getter, reqs, deadline, today)
    if args.out:
        lines = W.render_summary(facts, order, state, today, reqs)
        pathlib.Path(args.out, 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        run_path = pathlib.Path(args.out) / 'run.json'
        run = load_json(run_path, {})
        run['requests'] = reqs
        save_json(run_path, run)
    if not args.quiet:
        left = len(state.get('left') or [])
        print(f'Done. {reqs} request(s). {left} parks are left. The next run continues. Facts are in {args.out or "(not saved)"}.')
    return 0


def picture_wanted(fact, no_outline=False):
    """R-PR13: a picture only when a real question is still open, or the park has no official outline.
    Information-only codes (a shared page, both parts numbered) are not a question."""
    kind = (fact.get('page') or {}).get('kind') or ''
    if fact.get('unchanged') or kind in ('refused', 'robots', 'none', 'dead'):
        return False
    real = [q for q in (fact.get('questions') or []) if q.get('for') != 'information']
    if real:
        return True
    return bool(no_outline)


def _note_pictures(args, facts, getter, reqs, deadline, today):
    """One picture per park, each counted against the same request budget and the same deadline."""
    if os.environ.get('BROWSER') != '1' or not args.out or not isinstance(getter, LiveGetter):
        return reqs
    from kpc_manners import browser_picture
    left = args.max_requests - reqs
    pin = set()
    if getattr(args, 'links', ''):
        for ref, row in W.load_keys(args.links).items():
            if str((row or {}).get('g') or '') == 'pin':
                pin.add(ref)
    folder = pathlib.Path(args.out) / 'pictures'
    for parks in facts.values():
        for ref, fact in parks.items():
            if left <= 0 or (deadline is not None and time.time() >= deadline):
                return reqs
            if not picture_wanted(fact, no_outline=ref in pin):
                continue
            url = (fact.get('asked') or {}).get('url')
            if not url:
                continue
            left -= 1
            reqs += 1
            saved = browser_picture(url, getter.M, str(folder / f'{ref}.jpg'))
            if saved:
                fact['picture'] = {'file': f'pictures/{ref}.jpg', 'date': today,
                                   'note': 'picture for a reviewer, not a source'}
    write_facts(args.out, facts)
    return reqs


def cmd_coverage_order(args):
    if not args.coverage:
        print('coverage-order needs --coverage <pota-agencies-by-area CSV>')
        return 2
    doc = coverage_order(args.coverage)
    out = pathlib.Path(args.out) if args.out else ORDER_FILE
    save_json(out, doc)
    print(f"{len(doc['areas'])} areas ranked; wrote {out}")
    return 0


def cmd_report(args):
    if not args.out:
        print('A report needs --out, the folder a run already wrote.')
        return 0
    facts = W.load_facts(args.out)
    today = args.today or datetime.date.today().isoformat()
    order = (load_json(pathlib.Path(args.out) / 'worklist.json', {}) or {}).get('order') or []
    state = load_json(pathlib.Path(args.out) / 'state.json', {})
    run = load_json(pathlib.Path(args.out) / 'run.json', {})
    lines = W.render_summary(facts, order, state, today, run.get('requests') or 0)
    pathlib.Path(args.out, 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if not args.quiet:
        print('\n'.join(lines))
    return 0


def cmd_person_page(args):
    import kpc_park_pages_person as P
    facts = W.load_facts(args.out) if args.out else {}
    html = P.person_page(P.cards_from_facts(facts))
    dest = pathlib.Path(args.html or (str(pathlib.Path(args.out) / 'for-a-person.html') if args.out else 'for-a-person.html'))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf-8')
    if not args.quiet:
        print(f'The person page is {dest}. It does not use the network.')
    return 0


def cmd_intake(args):
    import kpc_park_pages_person as P
    if not args.file:
        print('Say which file to fold in.')
        return 0
    if not args.out:
        print('Say --out, the folder that holds the facts.')
        return 0
    incoming, answers = P.load_answers_or_zip(args.file)
    facts = W.load_facts(args.out)
    today = args.today or datetime.date.today().isoformat()
    if incoming:
        for area, parks in incoming.items():
            facts.setdefault(area, {}).update(parks)
    rows = []
    if answers:
        rows = P.apply_person(facts, answers, today=today)
        P.drop_pictures(args.out, [p.get('ref') for p in (answers.get('parks') or []) if isinstance(p, dict)], facts)
    write_facts(args.out, facts)
    if rows:
        P.write_disagreements(pathlib.Path(args.out) / 'disagreements.csv', rows)
    if not args.quiet:
        print(f'Folded in {args.file}. {len(rows)} disagreement(s).')
    return 0


def cmd_pc_kit(args):
    import kpc_park_pages_person as P
    if not args.out:
        print('Say --out, the zip to write.')
        return 0
    areas = args.areas.split() if args.areas else []
    P.build_pc_kit(args.data, areas, args.out, state_path=args.state)
    if not args.quiet:
        print(f'The PC kit is {args.out}. Send it to the PC. It has no secrets.')
    return 0


def cmd_kits(args):
    import kpc_park_pages_kits as K
    if not args.out:
        print('Say --out, the kits folder.')
        return 0
    facts = W.load_facts(args.data) if args.data and (pathlib.Path(args.data) / 'facts').is_dir() else W.load_facts(args.out)
    # facts usually live in --data when that folder is a run folder, else --from
    if getattr(args, 'from_dir', ''):
        facts = W.load_facts(args.from_dir)
    keys = args.keys or str(pathlib.Path(args.out).resolve().parent / 'kit-keys')
    if pathlib.Path(keys).resolve() == pathlib.Path(args.out).resolve() or str(pathlib.Path(keys).resolve()).startswith(str(pathlib.Path(args.out).resolve()) + '/'):
        print('The answer key is not put in the kit.')
        return 0
    info = K.make_kits(facts, args.out, keys, n=args.n or 40, seed=args.seed or 1, known_path=args.known or '')
    if not args.quiet:
        print(f"Two kits in {args.out}. {info['plants']} plants. The key is not in the kit.")
    return 0


def cmd_score(args):
    import kpc_park_pages_kits as K
    if not args.pass1 or not args.pass2 or not args.keys:
        print('Score needs --pass1, --pass2, and --keys.')
        return 0
    res = K.score(args.pass1, args.pass2, args.keys)
    print(f"Agreed: {res['agreed']}")
    print(f"Differ: {res['differ']}")
    print(f"Plants: {res['plant_hits']} of {res['plants']} match the key on both passes")
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
        check('a 403 is refused and counted for its site (put aside after 3 different pages, 21 Nov)',
              facts['US-DE']['US-9']['page']['kind'] == 'refused' and 'documents.example.gov' not in state['refused']
              and len(state['refusal_pages']['documents.example.gov']) == 1)
        getter2 = FixtureGetter(manifest, t)
        facts2, reqs2 = read_parks(areas, web, docs, truth, getter2, state, '2026-11-20', refs=['US-9'])
        check('a refused host is not asked the next day', reqs2 == 0 and getter2.calls == [])

    # worklist: list drop first, then approximate, then pin with a page, then never-read by qsos, then old
    areas = {'US-UT': {
        'US-A': {'name': 'A', 'website': 'https://www.nps.gov/a', 'type': 'National Park', 'qsos': 1, 'lat': 37, 'lon': -113},
        'US-B': {'name': 'B', 'website': 'https://www.nps.gov/b', 'type': 'National Park', 'qsos': 9, 'lat': 37, 'lon': -113},
        'US-C': {'name': 'C', 'website': '', 'type': 'State Park', 'qsos': 50, 'lat': 37, 'lon': -113},
        'US-D': {'name': 'D', 'website': 'https://www.nps.gov/d', 'type': 'National Park', 'qsos': 3, 'lat': 37, 'lon': -113},
        'US-E': {'name': 'E', 'website': 'https://www.nps.gov/e', 'type': 'National Park', 'qsos': 80, 'lat': 37, 'lon': -113},
    }}
    keys = {'US-A': {'g': 'approximate', 'c': []}, 'US-B': {'g': 'pin', 'c': []}, 'US-D': {'g': 'official', 'c': []}}
    lists = [{'name': 'keeper-2026-11-19.json', 'made_by': 'keeper', 'date': '2026-11-19', 'why': 'two records',
              'done': False, 'parks': [{'ref': 'US-D', 'why': 'name matches two records', 'want': ['sizes']}]}]
    state = {'read': {'US-E': {'date': '2026-10-01', 'url': 'https://www.nps.gov/e', 'fingerprint': 'abc'}}}
    order = W.build_worklist(areas, lambda ref, row: row.get('website') or '', keys, lists, ['US-C'], state, '2026-11-19')
    check('worklist order is list, refs file, approximate, pin, never read, then old',
          [r['ref'] for r in order] == ['US-D', 'US-C', 'US-A', 'US-B', 'US-E'] and [r['tier'] for r in order] == [1, 1, 2, 3, 5])
    lines = W.render_summary({'US-UT': {'US-D': {'ref': 'US-D', 'unchanged': False, 'page': {'kind': 'html'},
                                                 'questions': [{'code': 'COMBINED_UNIT', 'plain': 'The page calls this one.'}]}}},
                             order, {'refused': {}, 'left': ['US-E'], 'stopped': ''}, '2026-11-19', 4)
    check('the summary fits on one phone screen', 1 <= len(lines) <= 40 and any('US-D' in ln for ln in lines))

    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description='Park page reader')
    p.add_argument('command', nargs='?', default='read')
    p.add_argument('--data', default='data')
    p.add_argument('--out', default='')
    p.add_argument('--state', default='')
    p.add_argument('--fixtures', default='')
    p.add_argument('--keeper-copies', default='', help="the keeper's saved page copies (a manifest.json like the fixtures'); read first")
    p.add_argument('--keep-pages', default='', help="23 Nov: keep every fetched page, packed, in this folder (default: pages-kept beside <out> on "
                                                    "a live run; 'off' keeps none)")
    p.add_argument('--reextract', action='store_true', help='23 Nov: read the KEPT pages again with today\'s finders. No site is asked.')
    p.add_argument('--coverage', default='', help='coverage-order: the pota-agencies-by-area CSV')
    p.add_argument('--areas', default='')
    p.add_argument('--refs', default='')
    p.add_argument('--refs-file', default='')
    p.add_argument('--today', default='')
    p.add_argument('--max-requests', type=int, default=1500)
    p.add_argument('--max-minutes', type=int, default=50)
    p.add_argument('--max-get-seconds', type=int, default=GET_MAX_SECONDS,
                   help='wall-clock cap on one download, in seconds')
    p.add_argument('--max-per-park', type=int, default=R.MAX_PER_PARK)
    p.add_argument('--max-parks', type=int, default=None)
    p.add_argument('--refresh-days', type=int, default=W.REFRESH_DAYS)
    p.add_argument('--links', default='')
    p.add_argument('--lists', default='')
    p.add_argument('--lists-done', default='')
    p.add_argument('--not-sure', default='')
    p.add_argument('--priority-file', default='', help='PRIVATE list of parks to read first (the likely mismatches); never a repo file')
    p.add_argument('--confirmed-file', default='', help='PRIVATE list of parks confirmed by agency id: read last, then yearly')
    p.add_argument('--confirmed-refresh-days', type=int, default=W.CONFIRMED_REFRESH_DAYS)
    p.add_argument('--html', default='')
    p.add_argument('--pc', action='store_true')
    p.add_argument('--n', type=int, default=40)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--keys', default='')
    p.add_argument('--known', default='')
    p.add_argument('--from', dest='from_dir', default='')
    p.add_argument('--pass1', default='')
    p.add_argument('--pass2', default='')
    p.add_argument('--agency-table', default='', help="find-links: KPC-Links' .github/key-agency-table.json (hosts the reviewed joins tie to land managers)")
    p.add_argument('--again', action='store_true', help='find-links: look again for parks tried in the last 30 days')
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--selftest', action='store_true')
    p.add_argument('file', nargs='?')
    args = p.parse_args(argv)
    if args.pc:
        say_pc_extras()
    try:
        return _dispatch(args)
    except Exception:
        if not args.pc:
            raise
        import traceback
        pathlib.Path('run-log.txt').write_text(traceback.format_exc(), encoding='utf-8')
        print('Something went wrong. The details are in run-log.txt.')
        return 0


def say_pc_extras():
    import kpc_park_pages_person as P
    P.say_extras()


def _dispatch(args):
    if args.selftest or args.command == '--selftest':
        return selftest()
    if args.command == 'read':
        return cmd_read(args)
    if args.command == 'worklist':
        return cmd_worklist(args)
    if args.command == 'report':
        return cmd_report(args)
    if args.command == 'person-page':
        return cmd_person_page(args)
    if args.command == 'intake':
        return cmd_intake(args)
    if args.command == 'pc-kit':
        return cmd_pc_kit(args)
    if args.command == 'kits':
        return cmd_kits(args)
    if args.command == 'score':
        return cmd_score(args)
    if args.command == 'coverage-order':
        return cmd_coverage_order(args)
    if args.command == 'find-links':
        import kpc_park_pages_find as FIND
        return FIND.cmd_find_links(args)
    p.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
