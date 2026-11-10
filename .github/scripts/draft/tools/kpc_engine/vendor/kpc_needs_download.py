#!/usr/bin/env python3
"""kpc_needs_download.py (Nov 10): the ONE needs-download list, data/needs-download.json (one schema, one file).

The hunters, finders, the collector and the engine ONLY add rows here (a layer they may not or could not fetch); they never save
a layer. The master step in the KPC-Links US key workflow is the one that downloads what a bot may read (who=bot) and merges it
into the saved copies; the PC helper (KPC-Links tools/kpc_pc_helper.py) walks a person through the who=brandon rows;
who=never rows are never contacted by anybody. The master step's own rows come from the KPC-Links release asset
needs-download.json (same schema), merged here by kpc-copy-from-links.

Row: id (area|layer), area (US-XX / CA-.. / W-.. or ''), layer (the key's prefix when known, else url:<hash>), url, page, host,
     who (bot|brandon|never), why, expected, have, source (the bot), added (date), status (open|done|held), note,
     src (the download source in KPC-Links data/outlines/download-sources.json), check (bot = a bot may check it for a change; person).

  python3 kpc_needs_download.py merge <rows.json ...>   # add rows from files (a release asset, a bot's run) into the list
  python3 kpc_needs_download.py summary                 # open rows by who
"""
import datetime, hashlib, json, os, pathlib, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_host_rules as HR  # noqa: E402

LIST = pathlib.Path(os.environ.get('KPC_NEEDS_FILE') or 'data/needs-download.json')
FORMAT = 1   # the same as KPC-Links kpc_master.NEEDS_FORMAT
FIELDS = ('id', 'area', 'layer', 'url', 'page', 'host', 'who', 'why', 'expected', 'have', 'source', 'added', 'status', 'note',
          'src', 'check')   # Nov 10: src = the download source id (KPC-Links data/outlines/download-sources.json); check = bot | person
ABOUT = ('Layers somebody must download for the saved copies. who=bot: the master step downloads it; who=brandon: the PC helper '
         '(KPC-Links tools/kpc_pc_helper.py) opens the official page in a browser; who=never: nobody contacts it. Hunters and the '
         'engine only add rows here; only the master step saves layers. One row per area|layer.')


def norm_url(u): return re.sub(r'/query/?$', '', str(u or '').replace('svc:', '', 1).split('|')[0].split('?')[0]).rstrip('/')


_PRE = None
def layer_key(url, root='.'):
    """The US key's prefix for a layer url (data/us-key/layers.json), else url:<12 hex> (a lead the key does not read yet)."""
    global _PRE
    if _PRE is None:
        _PRE = {}
        try:
            for k, v in json.load(open(pathlib.Path(root) / 'data/us-key/layers.json', encoding='utf-8')).items():
                if isinstance(v, list) and v: _PRE[norm_url(v[0])] = k
        except Exception: pass  # noqa: BLE001
    n = norm_url(url)
    return _PRE.get(n) or 'url:' + hashlib.sha1(n.encode()).hexdigest()[:12]


def official_page(url):
    u = norm_url(url); host, path = HR.parts(u)
    if HR.is_arcgis_services_host(host):
        m = re.search(r'/services/([^/]+)/(?:Feature|Map)Server', path)
        if m: return 'https://hub.arcgis.com/search?q=' + urllib.parse.quote(m.group(1).replace('_', ' '))
    return u


def row(area, url, why, source, who=None, layer=None, expected=None, have=None, note='', date=None):
    w, w_why = HR.who_for(url) if who is None else (who, '')
    lay = layer or layer_key(url)
    return {'id': f'{area}|{lay}', 'area': area or '', 'layer': lay, 'url': str(url or ''), 'page': official_page(url), 'host': HR.parts(url)[0], 'who': w,
            'why': why + (f' ({w_why})' if w_why and w_why not in why else ''), 'expected': expected, 'have': have, 'source': source,
            'added': date or datetime.date.today().isoformat(), 'status': 'open', 'note': note, 'src': '', 'check': ''}


def load(path=None):
    try: doc = json.load(open(path or LIST, encoding='utf-8'))
    except Exception: doc = None  # noqa: BLE001
    if not isinstance(doc, dict) or not isinstance(doc.get('rows'), list): doc = {'format': FORMAT, 'about': ABOUT, 'rows': []}
    return doc


def merge(doc, rows):
    """By area|layer; a done row stays done unless the new row is newer. Same rule as kpc_master.merge_needs (KPC-Links)."""
    have = {f"{r.get('area')}|{r.get('layer')}": r for r in doc.get('rows') or []}
    added = updated = 0
    for r in rows:
        r = {k: r.get(k) for k in FIELDS}; r['id'] = f"{r.get('area')}|{r.get('layer')}"; k = r['id']; old = have.get(k)
        if old is None: have[k] = r; added += 1; continue
        if old.get('status') == 'done' and r.get('status') != 'done' and str(r.get('added') or '') <= str(old.get('added') or ''): continue
        if old.get('status') == 'held' and r.get('status') == 'open' and r.get('source') != 'change check': continue   # a held row stays held
        new = dict(old)
        for f in FIELDS:
            if f != 'added' and r.get(f) not in (None, ''): new[f] = r[f]
        if new != old: have[k] = new; updated += 1
    doc['rows'] = [have[k] for k in sorted(have)]; doc['format'] = FORMAT; doc.setdefault('about', ABOUT)
    return doc, added, updated


def save(doc, path=None):
    p = pathlib.Path(path or LIST); p.parent.mkdir(parents=True, exist_ok=True)
    new = json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + '\n'
    if p.exists() and p.read_text(encoding='utf-8') == new: return False   # no change, no save (no commit noise)
    tmp = p.with_name(p.name + '.tmp'); tmp.write_text(new, encoding='utf-8'); os.replace(tmp, p); return True


def add(rows, path=None):
    """Add rows to the one list. Returns (added, updated, saved)."""
    if not rows: return 0, 0, False
    doc, a, u = merge(load(path), rows)
    return a, u, save(doc, path)


def summary(doc):
    c = {}
    for r in doc.get('rows') or []:
        if r.get('status') == 'open': c[r.get('who')] = c.get(r.get('who'), 0) + 1
    return c


def main(argv):
    if argv[:1] == ['merge']:
        rows = []
        for f in argv[1:]:
            try: rows += (json.load(open(f, encoding='utf-8')).get('rows') or [])
            except Exception as e: print(f'::warning title=needs-download::{f} not read ({e})')  # noqa: BLE001
        a, u, s = add(rows)
        print(f'::notice title=needs-download::{a} new, {u} updated' + ('' if s else ' (no change, not saved)') + f'; open {summary(load())}'); return 0
    if argv[:1] == ['summary']: print(json.dumps(summary(load()))); return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
