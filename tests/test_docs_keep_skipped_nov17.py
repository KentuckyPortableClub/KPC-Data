#!/usr/bin/env python3
"""Nov 17: a skipped documents-bot read (robots-unreadable, rest / host resting,
or robots-blocked) must keep the earlier map AND rules exactly as they were,
the same way the campground bot keeps a camp when the host is off-limits.
Today only maps were kept, and only when the new status matched 'rest https?://'.
A NY-style file with 555 ok links on one host, robots unreadable this run, must
leave all 555 unchanged; that case fails without the guard. Offline: a local
127.0.0.1 server only; nothing outside is fetched, and nothing in the repo is
written."""
import copy, http.server, json, os, pathlib, re, sys, tempfile, threading, time

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(tempfile.mkdtemp(prefix='kpc-docs-keep-'))
os.environ['OUT'] = str(OUT)
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_docs_bot as B  # noqa: E402

ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and bool(cond)


# --- the old rest-only regex does not keep a robots-unreadable wipe
OLD_REST = re.compile(r'(?:^|[(;:] )rest https?://')
old_map = {'url': 'http://127.0.0.1/maps/park.pdf', 'status': 'ok', 'how': 'on file', 'kind': 'pdf', 'checked': '2020-01-01'}
old_rules = {'url': 'http://127.0.0.1/rules/park.htm', 'status': 'ok', 'how': 'on file'}
old = {'n': 'Park', 'checked': '2020-01-01', 'ver': 1, 'map': copy.deepcopy(old_map), 'rules': copy.deepcopy(old_rules)}
new = {
    'n': 'Park', 'checked': B.TODAY, 'ver': B.VER,
    'map': {'url': '', 'status': 'no working map link (tried: robots-unreadable http://127.0.0.1/maps/park.pdf)', 'how': 'on file'},
    'rules': {'url': 'http://127.0.0.1/rules/park.htm', 'status': 'robots-unreadable', 'how': 'on file'},
    'notes': ['park page: robots-unreadable'],
}
nm = new.get('map') or {}
om = old.get('map') or {}
old_regex_keeps = (not nm.get('url') and om.get('url') and OLD_REST.search(str(nm.get('status') or '')))
check(not old_regex_keeps, 'without the guard (the old rest-only regex) the unreadable wipe is not kept')
check(hasattr(B, 'keep_known_docs'), 'keep_known_docs is defined')
kept = B.keep_known_docs(old, new)
check(kept.get('map') == old_map, 'keep_known_docs leaves the earlier map exactly as it was')
check(kept.get('rules') == old_rules, 'keep_known_docs leaves the earlier rules exactly as they were')

# rest and robots-blocked too
for st, nmap, nrules in (
    ('rest', {'url': '', 'status': 'no working map link (tried: rest http://127.0.0.1/maps/park.pdf)', 'how': 'on file'},
     {'url': 'http://127.0.0.1/rules/park.htm', 'status': 'rules page not read (the site is resting: next run)', 'how': 'on file'}),
    ('robots', {'url': '', 'status': 'no working map link (tried: robots http://127.0.0.1/maps/park.pdf)', 'how': 'on file'},
     {'url': 'http://127.0.0.1/rules/park.htm', 'status': 'robots', 'how': 'on file'}),
):
    rec = B.keep_known_docs(old, {'n': 'Park', 'checked': B.TODAY, 'ver': B.VER, 'map': nmap, 'rules': nrules})
    check(rec.get('map') == old_map and rec.get('rules') == old_rules,
          f'keep_known_docs keeps map and rules on {st}')


# --- NY-style file: 555 ok links on one host, robots unreadable this run
class H(http.server.BaseHTTPRequestHandler):
    hits = {}

    def log_message(self, *a):
        pass

    def do_GET(self):
        H.hits[self.path] = H.hits.get(self.path, 0) + 1
        if self.path == '/robots.txt':
            self.send_response(500); self.end_headers(); return
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
HOST = f'http://127.0.0.1:{port}'

# 400 ok maps + 155 ok rules = 555 ok links, all on this host (155 parks have both)
N_MAP = 400
N_RULES = 155
N_PARKS = 400
parks = {}
web = {}
saved_parks = {}
links = []  # (ref, field, record)
for i in range(N_PARKS):
    ref = f'NY-t{i:04d}'
    name = f'Test Park {i}'
    page = f'{HOST}/places/p{i}'
    murl = f'{HOST}/maps/p{i}.pdf'
    rurl = f'{HOST}/rules/p{i}.htm'
    parks[ref] = [name, page, 'park']
    web[ref] = {'web': page, 'map': murl, 'agency': 'DEC'}
    rec = {
        'n': name, 't': 'park', 'page': page, 'checked': '2020-01-01', 'ver': 1,
        'map': {'url': murl, 'status': 'ok', 'how': 'on file', 'kind': 'pdf', 'checked': '2020-01-01'},
        'rules': None, 'agency': 'DEC', 'runs': [], 'handover': [], 'notes': [],
    }
    links.append((ref, 'map', copy.deepcopy(rec['map'])))
    if i < N_RULES:
        rec['rules'] = {'url': rurl, 'status': 'ok', 'how': 'on file'}
        links.append((ref, 'rules', copy.deepcopy(rec['rules'])))
    saved_parks[ref] = rec

check(len(links) == 555, f'fixture has 555 ok links (got {len(links)})')

B.OUT = OUT
(OUT / 'US-NY.json').write_text(json.dumps({
    'area': 'US-NY', 'about': 'synthetic NY-style docs file for the keep-known guard',
    'parks': saved_parks, 'counts': {'map ok': N_MAP, 'rules ok': N_RULES},
}))
B.park_list = lambda area: parks
B.no_outline = lambda: set()
B.fable_links = lambda: {}
B.GAP = 0.0
B.T0 = time.time()
B.LIMIT = 3600
B.BROWSER = False
B.ROBOTS.clear(); B.ROBOTS_SAID.clear(); B.ROBOTS_REFUSED.clear()
B.LAST.clear(); B.DEAD.clear(); B.STRIKE.clear()
H.hits.clear()

captured = []
_real_save = B.save


def _save(path, obj):
    captured.append((str(path), obj))
    return _real_save(path, obj)


B.save = _save
state = {'areas': {}}
B.run_area('US-NY', state, web, {}, {})
B.save = _real_save
srv.shutdown()

check(captured, 'run_area saved a file')
# Without the guard the 15% map-drop gate would write held/ and leave the original file alone.
held_saves = [p for p, _ in captured if pathlib.Path(p).parent.name == 'held']
check(not held_saves, f'the map-drop gate did not fire (held saves: {held_saves})')
out_saves = [obj for p, obj in captured if pathlib.Path(p).name == 'US-NY.json' and pathlib.Path(p).parent.name != 'held']
check(out_saves, 'the area file was saved as the run result')
D = out_saves[-1] if out_saves else {}
unchanged = 0
changed = []
for ref, field, earlier in links:
    got = ((D.get('parks') or {}).get(ref) or {}).get(field)
    if got == earlier:
        unchanged += 1
    else:
        if len(changed) < 5:
            changed.append((ref, field, got))
check(unchanged == 555, f'all 555 ok links are unchanged after robots-unreadable (kept {unchanged}; e.g. {changed})')

# nothing but robots.txt was fetched from the host
page_hits = {k: v for k, v in H.hits.items() if k != '/robots.txt'}
check(not page_hits, f'no park/map/rules page was fetched (hits {page_hits})')
check(H.hits.get('/robots.txt', 0) >= 1, 'robots.txt was read')
check(B.STAT.get('kept_on_rest', 0) == N_PARKS, f'every park was kept after the skipped read (got {B.STAT.get("kept_on_rest")})')

print('ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
