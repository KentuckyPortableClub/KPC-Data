#!/usr/bin/env python3
"""kpc_pc_upload.py: GitHub's reader for the owner's PC upload pack (22 Nov 2026; the pack is made by .github/scripts/pc/kpc_upload_pack.py).

The owner carries the pack up by hand (intake-files branch, pc-upload/<pack>.zip) and starts "KPC PC upload pack" by hand. Nothing
here runs on its own, downloads anything or opens a website.

  check  Reads the pack and refuses it WHOLE on any problem (nothing is kept): only manifest.json, pages/<area>.json and
         crosswalk/<agency>.json inside; sizes capped; every file parses and has its shape; no store-only field anywhere (shapes,
         records, licence internals, withheld marks); no WDPA field or word; a pages file must hold EVERY park of its area on the
         POTA list (data/parkinfo/<area>.json), so the order the PC read parks in can never show the private likely-mismatch
         list; a crosswalk file must pass the same checks as an agency list (kpc_agency_lists.problems, host rules included).
  merge  After a clean check:
           park-pages/facts/<area>.json (tools-out): a park already in the file is kept unless the PC's read of it is better (it
             read the real page where the one on file got nothing or a garbled name) or as good and newer (better_read; owner
             22 Nov); a park only the PC has is added. A park taken from the PC is marked "from_pc_upload": <date>.
           data/agency-crosswalk/<agency>.json (main): a file the keeper made is kept; else the PC's crosswalk is written, built
             by kpc_agency_lists.crosswalk_rows (a web id that maps to two map ids is left out), marked made_by "PC upload".
         The report holds counts only.

  python3 .github/scripts/kpc_pc_upload.py check --pack P [--parkinfo data/parkinfo]
  python3 .github/scripts/kpc_pc_upload.py merge --pack P --pages DIR --crosswalk DIR [--parkinfo data/parkinfo] [--report F]
"""
import argparse, collections, datetime, json, os, pathlib, re, sys, zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
VERSION = 'kpc_pc_upload 2026-11-22a'
MAX_TOTAL = 300_000_000
MAX_FILE = 60_000_000
NAME_RX = re.compile(r'^(manifest\.json|pages/(?:[A-Z]{2}-[A-Z0-9]{1,4}|CA)\.json|crosswalk/[a-z0-9][a-z0-9-]{0,79}\.json)$')
REF_RX = re.compile(r'^[A-Z0-9]{1,3}-[0-9]{3,6}$')
WDPA_RX = re.compile(r'wdpa|protected ?planet|unep[\s-]?wcmc|\bwdpaid\b', re.I)
# fields that belong to the private store or a licence decision, never to page facts or a crosswalk
STORE_ONLY = {'rings', 'geometry', 'coordinates', 'records', 'attributes', 'attrs', 'private_reason', 'publish_why', 'publish_basis',
              'publish_basis_detail', 'publishable', 'licence_class', 'terms_text_sha256', 'terms_text_file', 'withheld', 'held_reason',
              'store_record', 'kpcstore', 'source_detail', 'sha256'}
# 22 Nov: 'PRIVATE-' only in capitals (the PC's private files are named PRIVATE-...); a park page about the 'Private John Allen'
# fish hatchery (private-john-allen) is not a private file
PRIVATE_RX = re.compile(r'PRIVATE-|(?i:priority-parks|confirmed-parks|do-not-share)')


def walk(o, path=''):
    """Every (key path, key, value) in a JSON value."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield path, str(k), v
            yield from walk(v, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f'{path}[{i}]')


def field_problems(name, doc):
    out = []
    for p, k, v in walk(doc):
        if k.lower() in STORE_ONLY: out.append(f'{name}: a store-only field "{k}" (at {p or "/"})'); break
    for p, k, v in walk(doc):
        if WDPA_RX.search(k) or (isinstance(v, str) and WDPA_RX.search(v)): out.append(f'{name}: a WDPA field or word (at {p or "/"})'); break
    for p, k, v in walk(doc):
        if isinstance(v, str) and PRIVATE_RX.search(v): out.append(f'{name}: names a private file (at {p or "/"})'); break
    return out


def parkinfo_refs(parkinfo, area):
    """The POTA list's parks of one area (data/parkinfo/<area>.json, or .json.gz), or None."""
    for f in (pathlib.Path(parkinfo) / f'{area}.json', pathlib.Path(parkinfo) / f'{area}.json.gz'):
        if f.is_file():
            try:
                raw = f.read_bytes()
                if f.suffix == '.gz':
                    import gzip; raw = gzip.decompress(raw)
                d = json.loads(raw)
            except (OSError, ValueError, EOFError): return None
            return set((d.get('parks') if isinstance(d, dict) else None) or {})
    # 22 Nov: Kentucky is not in data/parkinfo (its own bots keep it); its parks come from POTA's saved list, as the reader does
    g = pathlib.Path(parkinfo).parent / 'pota' / 'saved' / 'parks' / f'{area}.json.gz'
    if g.is_file():
        try:
            import gzip
            rows = json.loads(gzip.decompress(g.read_bytes())).get('data') or []
            return {r.get('reference') for r in rows if isinstance(r, dict) and r.get('reference')} or None
        except (OSError, ValueError, EOFError, AttributeError): return None
    return None


def read_pack(pack, parkinfo='data/parkinfo'):
    """-> (pack dict or None, problems). The whole pack is refused on any problem."""
    probs = []
    try: z = zipfile.ZipFile(pack)
    except (OSError, zipfile.BadZipFile) as e: return None, [f'not a readable zip ({type(e).__name__})']
    with z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        bad = [n for n in names if not NAME_RX.match(n)]
        if bad: probs.append(f'{len(bad)} file(s) that do not belong in a pack (only manifest.json, pages/<area>.json, crosswalk/<agency>.json)')
        if 'manifest.json' not in names: probs.append('no manifest.json')
        if sum(i.file_size for i in infos) > MAX_TOTAL or any(i.file_size > MAX_FILE for i in infos): probs.append('too big (a file over 60 MB, or over 300 MB in all)')
        if len(set(names)) != len(names): probs.append('a file name twice')
        if probs: return None, probs
        docs = {}
        for n in names:
            try: docs[n] = json.loads(z.read(n).decode('utf-8'))
            except (ValueError, UnicodeDecodeError): probs.append(f'{n}: not JSON')
    if probs: return None, probs
    man = docs.pop('manifest.json')
    if not isinstance(man, dict) or man.get('kind') != 'kpc-pc-upload-pack' or man.get('format') != 1:
        return None, ['manifest.json is not a KPC PC upload pack (format 1)']
    made = str(man.get('made') or '')[:10]
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', made): probs.append('manifest.json has no date')
    pages, xw = {}, {}
    # 22 Nov: a park POTA lists in two areas is saved once, under one area; it counts as read for every area of the pack
    read_any = {r for n, d in docs.items() if n.startswith('pages/') and isinstance(d, dict) and isinstance(d.get('parks'), dict) for r in d['parks']}
    for n, d in sorted(docs.items()):
        probs += field_problems(n, d)
        if n.startswith('pages/'):
            area = n[6:-5]
            if not isinstance(d, dict) or d.get('area') != area or not isinstance(d.get('parks'), dict):
                probs.append(f'{n}: not a page facts file of {area}'); continue
            refs = set(d['parks'])
            if any(not REF_RX.match(str(r)) or not isinstance(v, dict) or (v.get('ref') not in (None, r)) for r, v in d['parks'].items()):
                probs.append(f'{n}: a park entry that is not a park reference with its facts'); continue
            want = parkinfo_refs(parkinfo, area)
            if want is None: probs.append(f'{n}: no POTA list for {area} here, so it cannot be shown to be read whole'); continue
            if not want or not want <= (refs | read_any):
                probs.append(f'{n}: not every park of {area} is in it (an area is taken only when read whole)'); continue
            pages[area] = d
        else:
            if not isinstance(d, dict) or not isinstance(d.get('rows'), list) or not d.get('agency'):
                probs.append(f'{n}: not a crosswalk file'); continue
            # 22 Nov review M5: the agency-list checks run here too, so one refused crosswalk refuses the WHOLE pack (it used to be
            # skipped quietly at merge while the rest of the pack was saved)
            try: _doc, _why = crosswalk_doc(d, made)
            except Exception as e: _doc, _why = None, [f'the agency-list checks stopped ({type(e).__name__})']  # noqa: BLE001
            if not _doc: probs.append(f'{n}: refused by the agency-list checks ({"; ".join(map(str, _why))[:200]})'); continue
            xw[n[10:-5]] = d
    if probs: return None, probs
    return {'made': made, 'manifest': man, 'pages': pages, 'crosswalk': xw}, []


def crosswalk_doc(d, made):
    """The PC's crosswalk -> the keeper's agency-crosswalk format, through kpc_agency_lists' own checks and builder."""
    import kpc_agency_lists as AL
    src = d.get('source') or {}
    entry = {'enabled': True, 'agency': d.get('agency'), 'link_kind': str(d.get('link_kind') or '').strip().lower(),
             'source_url': src.get('url') or '', 'format': 'json-rows', 'web_id': d.get('web_id') or {}, 'map': d.get('map') or {},
             'licence': src.get('licence') or '', 'terms_url': src.get('terms_url') or ''}
    # the 'saved copies only' host rule is a FETCH rule; the pack's rows were read by the PC (store rules) and nothing is fetched here
    why = [w for w in AL.problems(entry) if 'saved copies only' not in w]
    if why: return None, why
    w, m = entry['web_id'], entry['map']
    rows = [{w['column']: r.get('web'), m['value']: r.get('map')} for r in d['rows'] if isinstance(r, dict)]
    out, clashes = AL.crosswalk_rows(rows, entry)
    if not out: return None, ['no row gave both ids']
    return {'agency': entry['agency'], 'link_kind': entry['link_kind'], 'made_by': f'PC upload ({d.get("tool") or "kpc_upload_pack"}) via {VERSION}',
            'source': {'url': entry['source_url'], 'final_url': entry['source_url'], 'licence': entry['licence'], 'terms_url': entry['terms_url'],
                       'date': src.get('date') or made, 'list_complete': bool(d.get('list_complete'))},
            'rows': out, 'left_out_not_one_to_one': clashes}, []


def write_json(path, doc):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    os.replace(tmp, path)


REAL_PAGE = ('html', 'pdf')


def _garbled(t):
    t = str(t or '')
    return len(t) >= 4 and sum(1 for ch in t if ord(ch) > 127 or ch == '\ufffd' or (ord(ch) < 32 and ch not in '\t\n')) / len(t) > 0.25


def read_strength(fact):
    """2 = the park's page was really read (html or pdf) and its name is clean; 1 = a read that got nothing (busy, refused, dead,
    a page that builds itself) or a garbled name; 0 = no read."""
    pg, nm = (fact or {}).get('page') or {}, (fact or {}).get('name') or {}
    kind = pg.get('kind')
    if not kind: return 0
    name = nm.get('heading') or nm.get('title') if isinstance(nm, dict) else nm
    return 2 if kind in REAL_PAGE and not _garbled(name) else 1


def better_read(old, new):
    """22 Nov (owner 7:10 PM "Yeah"): the PC's read wins unless it is weaker than the one on file (it came back busy, refused,
    dead or garbled where the old one read the real page); equally strong = the newer read wins (the later 'read' date, a tie
    goes to the PC). -> True when the new read should replace the old."""
    so, sn = read_strength(old), read_strength(new)
    if sn != so: return sn > so
    return str(((new or {}).get('page') or {}).get('read') or '') >= str(((old or {}).get('page') or {}).get('read') or '')


def merge(P, pages_dir, xw_dir):
    """Every park on file is kept unless the PC's read of it is better or, as good and newer (better_read). -> counts"""
    c = collections.Counter()
    for area, d in sorted(P['pages'].items()):
        f = pathlib.Path(pages_dir) / f'{area}.json'
        try: old = json.loads(f.read_text(encoding='utf-8')) if f.is_file() else None
        except (OSError, ValueError): c['areas whose facts file could not be read (left as it is)'] += 1; continue
        parks = dict((old or {}).get('parks') or {})
        added = 0
        for ref, v in d['parks'].items():
            if ref in parks:
                if {k: x for k, x in parks[ref].items() if k != 'from_pc_upload'} == v: c['parks already holding this PC read'] += 1; continue
                if not better_read(parks[ref], v): c['parks on file kept (their read is better or newer)'] += 1; continue
                c['parks on file replaced by a better or newer PC read'] += 1
            else:
                c['parks added from the PC'] += 1
            parks[ref] = dict(v, from_pc_upload=P['made']); added += 1
        if not added: c['areas with nothing new'] += 1; continue
        doc = dict(old or {'area': area, 'reader': d.get('reader') or 'v1'}); doc['parks'] = dict(sorted(parks.items()))
        write_json(f, doc)
        c['areas written'] += 1
    for sl, d in sorted(P['crosswalk'].items()):
        f = pathlib.Path(xw_dir) / f'{sl}.json'
        if f.is_file():
            try: old = json.loads(f.read_text(encoding='utf-8'))
            except (OSError, ValueError): old = {}
            if not str(old.get('made_by') or '').startswith('PC upload'):
                c["agencies kept (the keeper's file is there)"] += 1; continue
        doc, why = crosswalk_doc(d, P['made'])
        if not doc: c['agencies refused by the agency-list checks'] += 1; continue
        write_json(f, doc)
        c['agencies written from the PC'] += 1; c['web ids written'] += len(doc['rows'])
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description='Check and merge the PC upload pack')
    ap.add_argument('step', choices=['check', 'merge'])
    ap.add_argument('--pack', required=True)
    ap.add_argument('--parkinfo', default='data/parkinfo')
    ap.add_argument('--pages', default='')
    ap.add_argument('--crosswalk', default='')
    ap.add_argument('--report', default='')
    a = ap.parse_args(argv)
    P, probs = read_pack(a.pack, a.parkinfo)
    lines = [f'{VERSION}: {pathlib.Path(a.pack).name}']
    if probs:
        lines += ['REFUSED, nothing kept:'] + [f'  - {p}' for p in probs[:40]]
        print('\n'.join(lines))
        if a.report: pathlib.Path(a.report).write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f'::error title=PC upload pack::refused ({len(probs)} problem(s)): nothing was kept', flush=True)
        return 1
    lines.append(f'checked: {len(P["pages"])} areas of page facts ({sum(len(d["parks"]) for d in P["pages"].values()):,} parks), '
                 f'{len(P["crosswalk"])} agencies of crosswalk, made {P["made"]}')
    if a.step == 'merge':
        if not a.pages or not a.crosswalk: print('merge needs --pages and --crosswalk'); return 2
        c = merge(P, a.pages, a.crosswalk)
        lines += [f'  {v:7,}  {k}' for k, v in sorted(c.items())]
    print('\n'.join(lines))
    if a.report: pathlib.Path(a.report).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
