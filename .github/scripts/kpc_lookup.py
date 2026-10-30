#!/usr/bin/env python3
"""KPC SHARED LOOK-UP BOT (chat 10; built Oct 29 2026 in KPC-Links, MOVED to KPC-Data the same evening: Brandon 7:22 PM 'move it over
here we in danger size over there and make sure we can delete the files over and not grow this one either protect size on both repos').
Chat sessions see only part of the web, so any chat writes a small REQUEST file and a GitHub runner (open internet, a real headless
browser) answers it, each request on its OWN job (up to 6 at once), so a big one never blocks a small one. No timers.

WHERE    KPC-Data, ORPHAN BRANCH `lookup` (never main, so nothing here grows main and the whole branch can be squashed):
           requests/<chat>-<id>.json   answers/<chat>-<id>.json (+ <chat>-<id>-<n>.jpg)   read/<chat>-<id> (empty file = 'I read it')
REQUEST  {"chat": 11, "kind": "page", "urls": ["https://..."], "screenshot": true, "report": "is the area closed?"}
         The same URL(s) + kind answered in the last 7 days is REUSED (answer says 'reused'); add "fresh": true to force a new read.
  kind  page        text (first 15,000 characters), links, optional screenshot
        map-check   the same + always a screenshot; a PDF renders page 1 (ask "pages": 3 for up to 3)
        layer-probe ArcGIS layers (chat 9's probe)    parcel  owner + parcel id per point on a parcel layer    probe  a chat-9 config
        save-map    {"ref","name","agency","url","pages"?,"hint"?}: an official PICTURE map (PDF / image; or a page that links one) is
                    shrunk (boundary page(s) only, default page 1, JPEG 2000 px long side, quality 70, 3 MB at most) and saved on the
                    orphan branch picture-maps as maps/<ref>_<short-name>.jpg + rows/<same>.json (index.json is rebuilt from rows/).
                    House rule Oct 29 11:10 PM; map-cleanup deletes a park's maps once its outline is OFFICIAL in the key.
SIZE     screenshots JPEG, 1280 px wide at most, quality 60; one answer capped at 2 MB ('trimmed' note); an answer + its pictures +
         its request are DELETED when the chat writes read/<id>, or after 7 days (mode tidy). The weekly tidy squashes the branch to
         one fresh commit when it passes 150 MB. No inbox writes: each chat fetches the branch when it reads its inbox.
MANNERS  kpc_manners.py: robots.txt obeyed (ArcGIS REST + ridb.recreation.gov/api + developer.nps.gov/api only), 2 s per host.
  python3 kpc_lookup.py todo | run <request> | tidy        (LOOKUP_ROOT = the checkout of the lookup branch)"""
import json, os, pathlib, re, sys, time, urllib.parse

ROOT = pathlib.Path(os.environ.get('LOOKUP_ROOT') or '.')
REQ, ANS, READ = ROOT / 'requests', ROOT / 'answers', ROOT / 'read'
ANSWER_MAX, KEEP_DAYS = 2_000_000, 7
TEXT_MAX, LINKS_MAX, URLS_MAX = 15000, 150, 25
sys.path.insert(0, str(pathlib.Path(__file__).parent))
try:
    from kpc_manners import Manners, page_text, links_in
    M = Manners('shared look-up bot')
except Exception:  # noqa: BLE001  (no manners module = no network work at all: fail closed, say so)
    M = None


def notice(m): print('::notice title=Look-up bot::' + str(m).replace('\n', ' ')[:900], flush=True)


def ans_path(req): return ANS / (pathlib.Path(req).stem + '.json')


def todo():
    out = []
    for p in sorted(REQ.glob('*.json')) if REQ.exists() else []:
        if not ans_path(p).exists(): out.append(str(p.relative_to(ROOT)))
    print(json.dumps(out[:30]))


_BR = None
def browser():
    global _BR
    if _BR is None:
        try:
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start(); b = pw.chromium.launch()
            _BR = b.new_context(viewport={'width': 1280, 'height': 900}, user_agent=M.ua if M else 'KPC look-up bot')
        except Exception as e:  # noqa: BLE001
            _BR = False; notice(f'no browser ({type(e).__name__}): plain reads only')
    return _BR


PDF_PAGES = 3   # the most a request may ask for; page 1 by default


def pdf_answer(r, body, shot_path, pages=1):
    """chat 3 (Oct 29 3:50 PM): a PDF comes back as text + pages 1-3 rendered to PNG (so a checker can SEE the boundary). Poppler
    (pdftotext / pdftoppm), about 1600 px on the long side."""
    import subprocess, tempfile
    r['kind'] = 'pdf'; r['bytes'] = len(body)
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / 'in.pdf'; f.write_bytes(body)
        try:
            info = subprocess.run(['pdfinfo', str(f)], capture_output=True, text=True, timeout=60).stdout
            m = re.search(r'^Pages:\s+(\d+)', info, re.M); r['pages'] = int(m.group(1)) if m else None
            r['text'] = subprocess.run(['pdftotext', '-f', '1', '-l', str(max(pages, 1)), '-layout', str(f), '-'], capture_output=True, text=True, timeout=120).stdout[:TEXT_MAX]
            if shot_path:
                base = str(shot_path)[:-4]
                subprocess.run(['pdftoppm', '-f', '1', '-l', str(max(1, min(pages, PDF_PAGES))), '-jpeg', '-jpegopt', 'quality=60', '-scale-to', '1280', str(f), base + '-p'], capture_output=True, timeout=300)
                shots = sorted(str(q) for q in pathlib.Path(base).parent.glob(pathlib.Path(base).name + '-p*.jpg'))
                r['screenshots'] = shots; r['screenshot'] = shots[0] if shots else None
        except Exception as e:  # noqa: BLE001
            r['pdf_error'] = f'{type(e).__name__}: {str(e)[:120]}'
    return r


def do_steps(pg, steps):
    """Oct 30 (chat 11 card check): simple clicks on OUR OWN pages before the read: {fill: css, text}, {press: css, key},
    {click: css}, {wait: ms}. A step that fails is noted and the rest go on."""
    done = []
    for st in (steps or [])[:12]:
        try:
            if 'fill' in st: pg.fill(st['fill'], str(st.get('text', '')))
            elif 'press' in st: pg.press(st['press'], st.get('key', 'Enter'))
            elif 'click' in st: pg.click(st['click'], timeout=15000)
            if 'wait' in st: pg.wait_for_timeout(min(int(st['wait']), 15000))
            done.append('ok')
        except Exception as e: done.append(f'{type(e).__name__}: {str(e)[:80]}')  # noqa: BLE001
    return done


def read_page(u, shot_path=None, pages=1, steps=None, read=None):
    r = {'url': u}
    if not M: r['status'] = 'no manners module: not read'; return r
    h = M.host(u)
    if M.dead.get(h, 0) > time.time(): r['status'] = 'host left alone (strikes)'; return r
    if not M.robots_ok(u): r['status'] = 'robots.txt says no'; return r
    w = M.gap - (time.time() - M.last.get(h, 0))
    if w > 0: time.sleep(w)
    M.last[h] = time.time()
    if re.search(r'\.pdf(?:$|[?#])|/download(?:$|[?#])', u, re.I):   # a PDF (or a /download link): read the bytes, render pages
        st, hd, body, final = M.get(u, accept='application/pdf,*/*')
        r['status'] = st; r['final_url'] = final; r['read_by'] = 'plain read'
        if body[:5] == b'%PDF-' or 'pdf' in str(hd.get('content-type', '')).lower(): return pdf_answer(r, body, shot_path, pages)
        if isinstance(st, int) and st < 400 and body: r['text'] = page_text(body.decode('utf-8', 'replace'))[:TEXT_MAX]; return r
    ctx = browser()
    if ctx:
        try:
            pg = ctx.new_page()
            resp = pg.goto(u, wait_until='domcontentloaded', timeout=60000)
            try: pg.wait_for_load_state('networkidle', timeout=20000)
            except Exception: pass  # noqa: BLE001
            r['status'] = resp.status if resp else 'no response'
            if steps: r['steps'] = do_steps(pg, steps if M.host(u).endswith('kentuckyportableclub.github.io') else [x for x in steps if set(x) == {'wait'}])   # other sites: waits only (a map viewer drawing)
            if read:
                parts = []
                for sel in (read if isinstance(read, list) else [read])[:4]:   # one box or a few: each read on its own
                    try: parts.append(f'[{sel}] ' + '\n'.join(' '.join(l.split()) for l in pg.inner_text(sel, timeout=5000).split('\n') if l.strip()))
                    except Exception as e: parts.append(f'[{sel}] not found ({type(e).__name__})')  # noqa: BLE001
                r['read_text'] = '\n'.join(parts)[:6000]
            r['final_url'] = pg.url; r['title'] = (pg.title() or '')[:200]
            txt = pg.inner_text('body') if pg.query_selector('body') else ''
            r['text'] = '\n'.join(' '.join(l.split()) for l in txt.split('\n') if l.strip())[:TEXT_MAX]
            r['links'] = [{'url': a, 'text': t[:100]} for a, t in pg.eval_on_selector_all('a[href]', 'els => els.map(e => [e.href, e.innerText])')
                          if a.startswith('http')][:LINKS_MAX]
            if shot_path:
                pg.screenshot(path=str(shot_path), full_page=False, type='jpeg', quality=60); r['screenshot'] = str(shot_path)
            pg.close(); r['read_by'] = 'headless browser'
            return r
        except Exception as e:  # noqa: BLE001
            r['browser_error'] = f'{type(e).__name__}: {str(e)[:120]}'
    st, hd, body, final = M.get(u)
    r['status'] = st; r['final_url'] = final; r['read_by'] = 'plain read'
    if isinstance(st, int) and st < 400 and body:
        html = body.decode('utf-8', 'replace')
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S); r['title'] = ' '.join((m.group(1) if m else '').split())[:200]
        r['text'] = page_text(html)[:TEXT_MAX]
        r['links'] = [{'url': a, 'text': t} for a, t in links_in(html, final)][:LINKS_MAX]
    return r


def arc(u, params):
    st, hd, body, final = M.get(u + ('&' if '?' in u else '?') + urllib.parse.urlencode({**params, 'f': 'json'}), accept='application/json')
    if not (isinstance(st, int) and st < 400): raise RuntimeError(f'no answer ({st})')
    j = json.loads(body.decode('utf-8', 'replace'))
    if isinstance(j, dict) and j.get('error'): raise RuntimeError(str(j['error'])[:140])
    return j


OWNER_RX = r'^(?:own(?:er)?(?:_?name)?\d?|owner1|ownername|own_nm|deeded_?owner|grantee|taxpayer(?:_?name)?|mail(?:ing)?_?name|ownernme1?)$|owner'
PARCEL_RX = r'^(?:parcel(?:_?id|_?no|_?num(?:ber)?)?|pin|apn|parid|par_id|pidn?|parcelnumb|map_?par(?:cel)?|tax_?id|account(?:_?no)?)$|parcel'


def do_parcel(q):
    lay = q['layer'].rstrip('/'); out = []
    for la, lo in (q.get('points') or [])[:50]:
        try:
            j = arc(lay + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                                     'outFields': q.get('fields') or '*', 'returnGeometry': 'false'})
            feats = [f.get('attributes') or {} for f in (j.get('features') or [])][:10]
            pick = lambda a, rx: next((str(v) for k, v in a.items() if v not in (None, '') and re.search(rx, k, re.I)), None)
            out.append({'point': [la, lo], 'owner': [pick(a, OWNER_RX) for a in feats], 'parcel_id': [pick(a, PARCEL_RX) for a in feats],
                        'features': feats})   # P-3 (HQ 6:20 PM): owner + parcel id per point, the full record kept beside them
        except Exception as e: out.append({'point': [la, lo], 'error': str(e)[:140]})  # noqa: BLE001
    return out


def run(req):
    req = req if pathlib.Path(req).exists() else ROOT / req
    q = json.load(open(req))
    rid = pathlib.Path(req).stem; kind = q.get('kind') or 'page'
    ANS.mkdir(parents=True, exist_ok=True)
    out = {'request': str(req), 'id': rid, 'chat': q.get('chat'), 'kind': kind, 'report': q.get('report') or '', 'asked': q,
           'answered': time.strftime('%Y-%m-%d %H:%MZ', time.gmtime()), 'results': []}
    t0 = time.time()
    hit = reuse(q, rid, kind)   # Oct 30 (HQ 7:40 AM): the same URL(s) + kind answered within 7 days = that answer again, no new fetch
    if hit:
        out.update({'results': hit['results'], 'reused': hit['id'], 'reused_from': hit.get('answered'), 'seconds': 0, 'short': f"reused the answer of {hit['id']} ({hit.get('answered')})"})
        ans_path(req).write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n'); notice(f"{rid}: {out['short']}"); return
    try:
        if kind in ('page', 'map-check'):
            for i, u in enumerate((q.get('urls') or [])[:URLS_MAX]):
                shot = ANS / f'{rid}-{i + 1}.jpg' if (kind == 'map-check' or q.get('screenshot')) else None
                if isinstance(u, dict):   # {url, steps, read}: clicks before the read (our own pages only)
                    out['results'].append(read_page(u.get('url', ''), shot, int(q.get('pages') or 1), u.get('steps'), u.get('read')))
                else: out['results'].append(read_page(u, shot, int(q.get('pages') or 1)))
        elif kind == 'layer-probe':
            import kpc_adds_probe as P
            for x in (q.get('layers') or [])[:URLS_MAX]:
                x = x if isinstance(x, dict) else {'url': x}
                try: out['results'].append(P.layer({'st': x.get('st', ''), 'kind': x.get('kind', ''), **x}))
                except Exception as e: out['results'].append({'url': x.get('url'), 'error': str(e)[:140]})  # noqa: BLE001
        elif kind == 'parcel':
            out['results'] = do_parcel(q)
        elif kind == 'probe':
            import kpc_adds_probe as P
            tmp = pathlib.Path('/tmp') / f'{rid}.json'; tmp.write_text(json.dumps(q.get('probe') or q))
            P.CAND = tmp; P.OUT = tmp.with_name(tmp.stem + '-tested.json'); P.main()
            out['results'] = json.load(open(P.OUT)) if P.OUT.exists() else {'error': 'the probe wrote nothing'}
        elif kind == 'save-map':
            out['results'] = [save_map(q, rid)]
        else: out['error'] = f'unknown kind {kind} (page, map-check, layer-probe, parcel, probe, save-map)'
    except Exception as e: out['error'] = f'{type(e).__name__}: {str(e)[:200]}'  # noqa: BLE001
    out['seconds'] = round(time.time() - t0)
    if M: out['manners'] = M.stat
    res = out['results'] if isinstance(out['results'], list) else [out['results']]
    ok = sum(1 for r in res if isinstance(r, dict) and not r.get('error') and (not isinstance(r.get('status'), (int, str)) or (isinstance(r.get('status'), int) and r['status'] < 400)))
    out['short'] = out.get('error') or f"{len(res)} result(s), {ok} read OK" + (f", {sum(1 for r in res if isinstance(r, dict) and r.get('screenshot'))} screenshot(s)" if kind in ('page', 'map-check') else '')
    s = json.dumps(out, indent=1, ensure_ascii=False)
    if len(s.encode()) > ANSWER_MAX:   # size guard: trim the long parts, never cut the JSON in half
        for r in res:
            if isinstance(r, dict):
                if isinstance(r.get('text'), str): r['text'] = r['text'][:3000]
                if isinstance(r.get('links'), list): r['links'] = r['links'][:30]
                if isinstance(r.get('features'), list): r['features'] = r['features'][:3]
        out['trimmed'] = f'answer over {ANSWER_MAX // 1_000_000} MB: texts cut to 3,000 characters, links to 30'
        s = json.dumps(out, indent=1, ensure_ascii=False)
        if len(s.encode()) > ANSWER_MAX: out['results'] = '(too big even trimmed: ask for fewer URLs)'; s = json.dumps(out, indent=1, ensure_ascii=False)
    ans_path(req).write_text(s.replace(str(ROOT) + '/', '') + '\n')
    notice(f'{rid}: {out["short"]} in {out["seconds"]} s')


PIC = pathlib.Path(os.environ.get('PIC_ROOT') or 'pm')
PIC_PX, PIC_Q, PIC_MAX = 2000, 70, 3_000_000
IMG_RX = re.compile(r'\.(?:jpe?g|png|gif|webp|tiff?)(?:$|[?#])', re.I)
FILE_RX = re.compile(r'\.pdf(?:$|[?#])|/pdf/|/download(?:$|[?#/])|widen|\.(?:jpe?g|png|gif|webp|tiff?)(?:$|[?#])', re.I)


def slug(s): return re.sub(r'[^a-z0-9]+', '-', (s or 'map').lower()).strip('-')[:32] or 'map'


def fetch(u):
    if not M or not M.robots_ok(u): return None, None, u, 'robots.txt says no (or no manners module)'
    h = M.host(u); w = M.gap - (time.time() - M.last.get(h, 0))
    if w > 0: time.sleep(w)
    M.last[h] = time.time()
    st, hd, body, final = M.get(u, accept='application/pdf,image/*,*/*')
    if not (isinstance(st, int) and st < 400 and body): return None, None, final, f'answer {st}'
    ct = str(hd.get('content-type', '')).lower()
    kind = 'pdf' if body[:5] == b'%PDF-' or 'pdf' in ct else 'img' if ct.startswith('image/') or body[:3] == b'\xff\xd8\xff' or body[:8] == b'\x89PNG\r\n\x1a\n' else 'html'
    return kind, body, final, ''


def pick_link(links, hint):
    """From a page's links, the most map-like PDF / image: 'map' in the link or its text, plus the request's hint words."""
    best, bs = None, 0
    for l in links or []:
        u, t = l.get('url') or '', (l.get('text') or '').lower()
        if not FILE_RX.search(u): continue
        s = 1 + 2 * ('map' in (u.lower() + ' ' + t)) + sum(3 for w in hint if w in (u.lower() + ' ' + t))
        if s > bs: best, bs = u, s
    return best


def save_map(q, rid):
    import subprocess, tempfile
    ref = str(q.get('ref') or '').strip(); name = q.get('name') or ''
    if not re.match(r'^[A-Z0-9]{1,4}-\d{4,5}$', ref): return {'error': f'save-map needs a park number (ref), got {ref!r}'}
    hint = [w.lower() for w in (q.get('hint') or '').split() if len(w) > 2]
    u = q.get('url') or ''; seen = []
    kind, body, final, err = fetch(u)
    for _ in range(2):   # a page that links the map (an agency park page, a Widen share page): follow the most map-like link
        if kind != 'html': break
        r = read_page(final or u)
        nxt = pick_link(r.get('links'), hint); seen.append(final or u)
        if not nxt or nxt in seen: return {'url': u, 'error': 'no map file (PDF / image) linked on that page: give the map link itself', 'looked': seen}
        kind, body, final, err = fetch(nxt)
    if err or kind not in ('pdf', 'img'): return {'url': u, 'error': err or 'not a PDF or picture', 'looked': seen}
    pages = q.get('pages') or 1
    pages = [int(p) for p in re.findall(r'\d+', str(pages))][:3] if not isinstance(pages, int) else [pages]
    base = f'{ref}_{slug(name)}'
    (PIC / 'maps').mkdir(parents=True, exist_ok=True); (PIC / 'rows').mkdir(parents=True, exist_ok=True)
    saved = []
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / ('in.pdf' if kind == 'pdf' else 'in.img'); src.write_bytes(body)
        for i, pg in enumerate(pages if kind == 'pdf' else [1]):
            out = PIC / 'maps' / (base + ('' if i == 0 else f'-p{pg}') + '.jpg')
            for qual in (PIC_Q, 50, 35):
                if kind == 'pdf':
                    stem = pathlib.Path(td) / f'p{pg}'
                    subprocess.run(['pdftoppm', '-f', str(pg), '-l', str(pg), '-singlefile', '-jpeg', '-jpegopt', f'quality={qual}', '-scale-to', str(PIC_PX), str(src), str(stem)], capture_output=True, timeout=300)
                    tmp = stem.with_suffix('.jpg')
                    if not tmp.exists(): break
                else:
                    from PIL import Image
                    im = Image.open(src); im.thumbnail((PIC_PX, PIC_PX)); tmp = pathlib.Path(td) / 'out.jpg'
                    im.convert('RGB').save(tmp, 'JPEG', quality=qual, optimize=True)
                if tmp.stat().st_size <= PIC_MAX: tmp.replace(out); saved.append(str(out.relative_to(PIC))); break
    if not saved: return {'url': u, 'map_url': final, 'error': f'could not render page(s) {pages} under {PIC_MAX // 1_000_000} MB'}
    row = {'ref': ref, 'name': name, 'agency': q.get('agency') or '', 'source_url': final, 'asked_url': u, 'page': pages if kind == 'pdf' else None,
           'files': saved, 'date': time.strftime('%Y-%m-%d'), 'chat': q.get('chat'), 'request': rid}
    json.dump(row, open(PIC / 'rows' / f'{base}.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return {'url': u, 'map_url': final, 'saved': saved, 'bytes': sum((PIC / s).stat().st_size for s in saved), 'branch': 'picture-maps'}


def map_index():
    rows = []
    for f in sorted((PIC / 'rows').glob('*.json')) if (PIC / 'rows').exists() else []:
        try: rows.append(json.load(open(f, encoding='utf-8')))
        except ValueError: pass
    json.dump({'about': "Official PICTURE maps (no coordinates) for parks with no GIS outline; boundary page only, small JPEG. Deleted when the park gets an OFFICIAL outline. Never traced (G-ID3; R-G9 decides later).",
               'built': time.strftime('%Y-%m-%d %H:%MZ', time.gmtime()), 'count': len(rows), 'maps': rows}, open(PIC / 'index.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Picture maps::{len(rows)} maps in the index')


def map_cleanup():
    """Delete every picture map whose park now has an OFFICIAL outline in KPC-Links data/us-key or data/ca-key (grade g == 'official')."""
    links = pathlib.Path(os.environ.get('LINKS') or 'links'); gone = []
    off = set()
    for f in list((links / 'data' / 'us-key').glob('US-*.json')) + list((links / 'data' / 'ca-key').glob('CA-*.json')):
        try: off |= {r for r, v in (json.load(open(f)).get('parks') or {}).items() if isinstance(v, dict) and v.get('g') == 'official'}
        except ValueError: pass
    if not off: print('::notice title=Picture maps::no key read: nothing deleted'); return
    for f in sorted((PIC / 'rows').glob('*.json')) if (PIC / 'rows').exists() else []:
        row = json.load(open(f, encoding='utf-8'))
        if row.get('ref') in off:
            for s in row.get('files') or []:
                if (PIC / s).exists(): (PIC / s).unlink()
            f.unlink(); gone.append(row['ref'])
    map_index()
    print(f"::notice title=Picture maps::cleanup: {len(gone)} deleted (park now has an official outline){': ' + ', '.join(gone[:20]) if gone else ''}")


def cache_key(q, kind):
    if kind in ('page', 'map-check'): return kind + '|' + '|'.join(sorted(json.dumps(x, sort_keys=True) if isinstance(x, dict) else x for x in q.get('urls') or [])) + f"|p{q.get('pages') or 1}|s{bool(q.get('screenshot'))}"
    if kind == 'layer-probe': return kind + '|' + '|'.join(sorted(str(x.get('url') if isinstance(x, dict) else x) for x in q.get('layers') or []))
    if kind == 'parcel': return kind + '|' + json.dumps({k: q.get(k) for k in ('layer', 'points')}, sort_keys=True)
    return ''   # probe / save-map: never reused (a save-map writes a file; a probe config changes)


def reuse(q, rid, kind):
    k = cache_key(q, kind)
    if not k or q.get('fresh'): return None
    for a in sorted(ANS.glob('*.json')) if ANS.exists() else []:
        if a.stem == rid: continue
        try:
            o = json.load(open(a))
            if o.get('reused') or o.get('error'): continue
            if cache_key(o.get('asked') or {}, o.get('kind')) != k: continue
            if time.time() - time.mktime(time.strptime(o.get('answered', '')[:10], '%Y-%m-%d')) > KEEP_DAYS * 86400: continue
            return o
        except Exception: continue  # noqa: BLE001
    return None


def tidy():
    """Delete an answer, its pictures and its request when the chat wrote read/<id>, or when the answer is over 7 days old."""
    gone = []
    stems = {p.stem for p in ANS.glob('*.json')} if ANS.exists() else set()
    for stem in sorted(stems | ({p.name for p in READ.iterdir()} if READ.exists() else set())):
        a = ANS / f'{stem}.json'; old = False
        try: old = time.time() - time.mktime(time.strptime(json.load(open(a)).get('answered', '')[:10], '%Y-%m-%d')) > KEEP_DAYS * 86400
        except Exception: pass  # noqa: BLE001
        if (READ / stem).exists() or old:
            for f in [a, REQ / f'{stem}.json', READ / stem] + list(ANS.glob(f'{stem}-*')):
                if f.exists(): f.unlink()
            gone.append(stem)
    notice(f'tidy: {len(gone)} answers deleted (read or over {KEEP_DAYS} days)' + (f': {", ".join(gone[:10])}' if gone else ''))


if __name__ == '__main__':
    a = sys.argv[1:] or ['todo']
    try:
        if a[0] == 'todo': todo()
        elif a[0] == 'run': run(a[1])
        elif a[0] == 'tidy': tidy()
        elif a[0] == 'map-index': map_index()
        elif a[0] == 'map-cleanup': map_cleanup()
    except Exception as e:  # noqa: BLE001
        notice(f'stopped ({type(e).__name__}: {str(e)[:200]})')
    sys.exit(0)
