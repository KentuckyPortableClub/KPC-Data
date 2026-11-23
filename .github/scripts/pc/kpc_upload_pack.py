#!/usr/bin/env python3
"""kpc_upload_pack.py: the PC's page facts and agency crosswalk, packed into ONE file the owner carries up by hand (22 Nov 2026).

Runs on the owner's PC (Tools\\KPC-PC-BOTS-NOV21\\tools, copied from KPC-Data .github/scripts/pc). Standard library only, no
internet, nothing is uploaded. It reads:
  page-reader\\out\\facts\\<area>.json                          the PC park page reader's facts (the same format as GitHub's)
  page-reader\\data\\parkinfo\\<area>.json                       the POTA list of each area (to see that an area is read WHOLE)
  KPC-ID-crosswalk\\agency-fields-out\\<newest>\\proposed-agency-lists.json   the proposed web id / map id columns per agency
  the store tool's results\\agency-lists\\<agency>.json.gz      each agency's own list (rows), read once by its A step
  KPC-ID-crosswalk\\crosswalk-out\\<newest>\\link-ids.csv          the link id kind of each agency's parks (link_kind)
  upload-approved-agencies.txt                                 optional: only these agencies (owner, 22 Nov: agency data needs no
                                                               approval, so with no names EVERY agency whose columns tie is packed)
and writes SEND-BACK\\kpc-upload-pack-<date>-<time>.zip:
  manifest.json            counts only
  pages\\<area>.json        each area's page facts, as the PC reader wrote them (no other file of the reader)
  crosswalk\\<agency>.json  for each agency whose proposed columns TIE on the rows (at least 80% of the rows give the same park,
                            the PC's agency field check): those columns and, from its list, ONLY those two columns
Never packed: anything in PRIVATE, the store, the cache, a list of an agency you did not allow, WDPA, and the page facts of an
area the reader has not finished (every park of the area must have a fact): which parks were read first would show the
private likely-mismatch list. GitHub's reader
(KPC-Data kpc_pc_upload.py) checks the file again before anything is kept.

  py -3 tools\\kpc_upload_pack.py                 make the pack (the plan and the counts are printed)
  py -3 tools\\kpc_upload_pack.py --selftest
"""
import argparse, collections, csv, datetime, gzip, io, json, os, pathlib, re, sys, tempfile, zipfile

VERSION = 'kpc_upload_pack 2026-11-22a'
HERE = pathlib.Path(__file__).resolve().parent
BOTS = HERE.parent                                   # Tools\KPC-PC-BOTS-NOV21
TOOLS = BOTS.parent                                  # Tools
STORE = TOOLS / 'KPC-TOOLS-NOV14' / '1-STORE-TOOL' / 'kpc-outline-store-full'
XWALK = TOOLS / 'KPC-ID-crosswalk'
AREA_RX = re.compile(r'^(?:[A-Z]{2}-[A-Z0-9]{1,4}|CA)$')   # US-XX, and CA (all of Canada in one file)
WDPA = re.compile(r'wdpa|protected ?planet|unep[\s-]?wcmc', re.I)


def say(*a):
    print(*a, flush=True)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', str(s or '').lower()).strip('-')[:80] or 'agency'


def newest(folder, pattern):
    c = sorted(pathlib.Path(folder).glob(pattern), key=lambda p: p.stat().st_mtime) if pathlib.Path(folder).is_dir() else []
    return c[-1] if c else None


def approved_agencies(path):
    """22 Nov (owner: agency data needs no approval): no file, or a file with no names, = every proposal is packed (None). A file
    with names = only those (a way to leave an agency out)."""
    try: lines = pathlib.Path(path).read_text(encoding='utf-8-sig').splitlines()
    except OSError: return None
    names = [l.strip() for l in lines if l.strip() and not l.lstrip().startswith('#')]
    return names or None


def link_kinds(link_ids_csv):
    """agency -> the commonest 'id kind' of its parks with a usable link id (lower case, as the park facts tie reads it)."""
    c = collections.defaultdict(collections.Counter)
    if not link_ids_csv or not pathlib.Path(link_ids_csv).is_file(): return {}
    with open(link_ids_csv, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if (r.get('usable as a link id') or '').strip().lower() == 'yes' and r.get('agency') and r.get('id kind'):
                c[r['agency'].strip()][r['id kind'].strip().lower()] += 1
    return {a: k.most_common(1)[0][0] for a, k in c.items() if k}


def list_rows(lists_dir, agency, entry):
    """The agency's saved list: its rows from the layer the proposal names (or its first complete layer)."""
    for f in sorted(pathlib.Path(lists_dir).glob('*.json.gz')) if pathlib.Path(lists_dir).is_dir() else []:
        try: d = json.loads(gzip.decompress(f.read_bytes()))
        except (OSError, ValueError, EOFError): continue
        if str(d.get('agency') or '') != agency: continue
        lays = d.get('layers') or []
        want = entry.get('source_url_layer') or ''
        lay = next((x for x in lays if want and x.get('url') == want), None) or next((x for x in lays if x.get('rows')), None)
        if lay: return lay.get('rows') or [], bool(lay.get('complete')), str(d.get('read_on') or '')
    return None, False, ''


def blank_wdpa(o):
    """A WDPA address or word inside a park's facts (its POTA link, never read) is blanked; -> (value, how many)."""
    if isinstance(o, dict):
        n = 0; out = {}
        for k, v in o.items():
            out[k], m = blank_wdpa(v); n += m
        return out, n
    if isinstance(o, list):
        n = 0; out = []
        for v in o:
            x, m = blank_wdpa(v); out.append(x); n += m
        return out, n
    if isinstance(o, str) and WDPA.search(o): return '', 1
    return o, 0


def area_refs(parkinfo_dir, area):
    """The POTA list's parks of one area (page-reader\\data\\parkinfo\\<area>.json), or None when it is not on this PC."""
    f = pathlib.Path(parkinfo_dir or '') / f'{area}.json'
    try: d = json.loads(f.read_text(encoding='utf-8'))
    except (OSError, ValueError): return None
    return set((d.get('parks') if isinstance(d, dict) else None) or {})


def make_pack(out_dir, pages_dir, proposals, lists_dir, link_ids, approved, now=None, parkinfo=None):
    """-> (zip path or None, counts, reasons). Nothing outside the named inputs is read."""
    now = now or datetime.datetime.now()
    counts, why = collections.Counter(), []
    members = {}
    pages = {}
    # 22 Nov: a park POTA lists in two or more areas is saved once, in one area's file; it counts as read for every area
    read_any = set()
    for f in sorted(pathlib.Path(pages_dir).glob('*.json')) if pages_dir and pathlib.Path(pages_dir).is_dir() else []:
        try: read_any |= set((json.loads(f.read_text(encoding='utf-8')).get('parks') or {}))
        except (OSError, ValueError, AttributeError): pass
    for f in sorted(pathlib.Path(pages_dir).glob('*.json')) if pages_dir and pathlib.Path(pages_dir).is_dir() else []:
        if not AREA_RX.match(f.stem): counts['page files skipped (not an area name)'] += 1; continue
        try: d = json.loads(f.read_text(encoding='utf-8'))
        except (OSError, ValueError): counts['page files that could not be read'] += 1; continue
        if not isinstance(d, dict) or not isinstance(d.get('parks'), dict): counts['page files not in the reader\'s format'] += 1; continue
        if WDPA.search(json.dumps(d)):
            d, nb = blank_wdpa(d); counts['WDPA addresses blanked (a POTA link to WDPA: never read, never sent)'] += nb
        want = area_refs(parkinfo, f.stem)
        if want is None: counts['areas left out: no POTA list on this PC to show the area is read whole'] += 1; continue
        if not want or not want <= (set(d['parks']) | read_any):
            counts['areas left out: not every park read yet (packed once the area is finished)'] += 1; continue
        members[f'pages/{f.stem}.json'] = json.dumps(d, ensure_ascii=False).encode('utf-8')
        pages[f.stem] = len(d['parks'])
    ok_names = None if approved is None else set(approved)   # None = every proposal (owner, 22 Nov: agency data needs no approval)
    props = []
    if proposals and pathlib.Path(proposals).is_file():
        try: props = json.loads(pathlib.Path(proposals).read_text(encoding='utf-8')).get('agencies') or []
        except (OSError, ValueError): why.append('proposed-agency-lists.json could not be read: no crosswalk packed')
    kinds = link_kinds(link_ids)
    xw = {}
    for e in props:
        ag = str(e.get('agency') or '')
        if ok_names is not None and ag not in ok_names: counts['proposed agencies listed as not allowed (not packed)'] += 1; continue
        w, m = e.get('web_id') or {}, e.get('map') or {}
        if not w.get('column') or not all(m.get(k) for k in ('layer', 'field', 'value')):
            counts['allowed agencies left out: no web id or map id column proposed'] += 1; why.append(f'{ag}: no web id or map id column'); continue
        tm = re.search(r'row tie (\d+) same / (\d+) different', str(e.get('status') or ''))
        same, diff = (int(tm.group(1)), int(tm.group(2))) if tm else (0, 0)
        if not same or same < 0.8 * (same + diff):
            counts['agencies left out: their two columns do not tie on the rows (under 80% the same park)'] += 1; why.append(f'{ag}: columns do not tie'); continue
        lk = str(e.get('link_kind') or '').strip().lower()
        if not lk and w.get('from_address') and not w.get('regex'): lk = 'page address'   # 22 Nov: the column holds the park's page address
        lk = lk or kinds.get(ag, '')
        if not lk: counts['allowed agencies left out: no link kind known'] += 1; why.append(f'{ag}: no link kind'); continue
        if WDPA.search(json.dumps(e)): counts['allowed agencies left out: WDPA'] += 1; continue
        rows, complete, read_on = list_rows(lists_dir, ag, e)
        if rows is None: counts['allowed agencies left out: its list is not on this PC'] += 1; why.append(f'{ag}: list not on this PC'); continue
        two = [{'web': str(r.get(w['column']) if r.get(w['column']) is not None else ''), 'map': str(r.get(m['value']) if r.get(m['value']) is not None else '')}
               for r in rows if isinstance(r, dict)]
        two = [x for x in two if x['web'].strip() and x['map'].strip()]
        doc = {'agency': ag, 'link_kind': lk,
               'source': {'url': e.get('source_url') or '', 'licence': e.get('licence') or '', 'terms_url': e.get('terms_url') or '', 'date': read_on[:10]},
               'web_id': {'column': w['column'], 'regex': w.get('regex') or ''}, 'map': {k: m[k] for k in ('layer', 'field', 'value')},
               'list_complete': complete, 'rows': two}
        members[f'crosswalk/{slug(ag)}.json'] = json.dumps(doc, ensure_ascii=False).encode('utf-8')
        xw[slug(ag)] = len(two)
    if not members:
        return None, counts, why + ['nothing to pack: no page facts and no allowed agency']
    manifest = {'kind': 'kpc-pc-upload-pack', 'format': 1, 'tool': VERSION, 'made': now.isoformat(timespec='seconds'),
                'pages': pages, 'crosswalk': xw, 'left_out': dict(counts)}
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    zp = out / f'kpc-upload-pack-{now.strftime("%Y-%m-%d-%H%M")}.zip'
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json', json.dumps(manifest, indent=1))
        for n, b in sorted(members.items()): z.writestr(n, b)
    counts['areas of page facts packed'] = len(pages); counts['parks of page facts packed'] = sum(pages.values())
    counts['agencies of crosswalk packed'] = len(xw)
    return zp, counts, why


def selftest():
    ok = True
    def check(m, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + m)
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        (t / 'facts').mkdir(); (t / 'lists').mkdir(); (t / 'PRIVATE').mkdir(); (t / 'pi').mkdir()
        (t / 'facts' / 'US-ZZ.json').write_text(json.dumps({'area': 'US-ZZ', 'reader': 'v1', 'parks': {'US-9001': {'ref': 'US-9001',
                                                            'asked': {'url': 'https://www.protectedplanet.net/555555'}}}}))
        (t / 'facts' / 'US-YY.json').write_text(json.dumps({'area': 'US-YY', 'reader': 'v1', 'parks': {'US-9101': {'ref': 'US-9101'}}}))
        (t / 'pi' / 'US-ZZ.json').write_text(json.dumps({'parks': {'US-9001': []}}))
        (t / 'pi' / 'US-YY.json').write_text(json.dumps({'parks': {'US-9101': [], 'US-9102': []}}))
        (t / 'facts' / 'notes.json').write_text('{}')
        (t / 'PRIVATE' / 'priority-parks.csv').write_text('park\nUS-9001\n')
        (t / 'prop.json').write_text(json.dumps({'agencies': [
            {'agency': 'ZZ Parks', 'source_url': 'https://gis.zz.example.gov/arcgis/rest/services/P/FeatureServer/0', 'web_id': {'column': 'PARKNUM'},
             'map': {'layer': 'sgzza', 'field': 'UNIT_NO', 'value': 'UNIT'}, 'status': 'off: fields PROPOSED (row tie 9 same / 0 different)'},
            {'agency': 'YY Lands', 'source_url': 'https://yy.example.gov/x', 'web_id': {'column': 'ID'}, 'map': {'layer': 'sgyya', 'field': 'F', 'value': 'G'},
             'status': 'off: fields PROPOSED (row tie 9 same / 0 different)'},
            {'agency': 'XX Untied', 'source_url': 'https://xx.example.gov/x', 'web_id': {'column': 'ID'}, 'map': {'layer': 'sgxxa', 'field': 'F', 'value': 'G'},
             'status': 'off: fields PROPOSED (row tie 1 same / 5 different)'}]}))
        (t / 'lists' / 'zz-parks.json.gz').write_bytes(gzip.compress(json.dumps({'agency': 'ZZ Parks', 'layers': [
            {'url': 'u', 'complete': True, 'rows': [{'PARKNUM': '501', 'UNIT': 'A1', 'SECRET': 'not packed'}, {'PARKNUM': '', 'UNIT': 'A2'}]}]}).encode()))
        (t / 'link-ids.csv').write_text('park,agency,id kind,usable as a link id\nUS-9001,ZZ Parks,ZZ Park Id,yes\n')
        zp, c, why = make_pack(t / 'out', t / 'facts', t / 'prop.json', t / 'lists', t / 'link-ids.csv', ['ZZ Parks'],
                               now=datetime.datetime(2026, 11, 22, 1, 30), parkinfo=t / 'pi')
        names = zipfile.ZipFile(zp).namelist()
        check('the pack holds the manifest, the page facts and the allowed agency only', names == ['manifest.json', 'crosswalk/zz-parks.json', 'pages/US-ZZ.json'])
        x = json.loads(zipfile.ZipFile(zp).read('crosswalk/zz-parks.json'))
        check('only the two columns of the list are packed, rows with both ids only', x['rows'] == [{'web': '501', 'map': 'A1'}] and 'SECRET' not in json.dumps(x))
        check('the link kind comes from link-ids.csv', x['link_kind'] == 'zz park id')
        pz = zipfile.ZipFile(zp).read('pages/US-ZZ.json').decode()
        check('a WDPA address in a park\'s facts is blanked, the park kept', 'protectedplanet' not in pz and 'US-9001' in pz)
        check('nothing from PRIVATE is packed', not any('PRIVATE' in n or 'priority' in n for n in names))
        check('an area not read whole is left out (its read order would show the private list)', 'pages/US-YY.json' not in names
              and c['areas left out: not every park read yet (packed once the area is finished)'] == 1)
        man = json.loads(zipfile.ZipFile(zp).read('manifest.json'))
        check('the manifest holds counts only (no park number)', 'US-9001' not in json.dumps(man) and man['pages'] == {'US-ZZ': 1})
        zp2, c2, why2 = make_pack(t / 'out2', t / 'nothing', t / 'prop.json', t / 'lists', t / 'link-ids.csv', [])
        check('no page facts and no allowed agency: no pack', zp2 is None)
        zp3, c3, _ = make_pack(t / 'out3', t / 'facts', t / 'prop.json', t / 'lists', t / 'link-ids.csv', None, parkinfo=t / 'pi')
        n3 = zipfile.ZipFile(zp3).namelist()
        check('no approval list (owner, 22 Nov): every agency whose columns tie is packed, an agency whose columns do not tie is not',
              'crosswalk/zz-parks.json' in n3 and 'crosswalk/xx-untied.json' not in n3
              and c3['agencies left out: their two columns do not tie on the rows (under 80% the same park)'] == 1)
    print('ALL PASS' if ok else 'SOME FAILED')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='Pack the PC page facts and agency crosswalk for a hand upload')
    ap.add_argument('--pages', default=str(BOTS / 'page-reader' / 'out' / 'facts'))
    ap.add_argument('--parkinfo', default=str(BOTS / 'page-reader' / 'data' / 'parkinfo'))
    ap.add_argument('--proposals', default='')
    ap.add_argument('--lists', default=str(STORE / 'results' / 'agency-lists'))
    ap.add_argument('--link-ids', default='')
    ap.add_argument('--approved', default=str(BOTS / 'upload-approved-agencies.txt'))
    ap.add_argument('--out', default=str(BOTS / 'SEND-BACK'))
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest: return selftest()
    say(f'{VERSION}  Python {sys.version.split()[0]}')
    ap_ = pathlib.Path(a.approved)
    if not ap_.exists():
        ap_.write_text('# Owner, 22 Nov: agency data needs no approval, so EVERY agency whose proposed columns tie is packed.\n'
                       '# To leave agencies out, list here only the ones to pack (one name per line, as in proposed-agency-lists.json).\n', encoding='utf-8')
    prop = a.proposals or str((newest(XWALK / 'agency-fields-out', '*/proposed-agency-lists.json') or ''))
    links = a.link_ids or str((newest(XWALK / 'crosswalk-out', '*/link-ids.csv') or ''))
    zp, c, why = make_pack(a.out, a.pages, prop, a.lists, links, approved_agencies(ap_), parkinfo=a.parkinfo)
    for k, v in sorted(c.items()): say(f'  {v:6,}  {k}')
    for w in why[:20]: say('  note: ' + w)
    if not zp: say('No pack made.'); return 1
    say(f'Made {zp}  ({zp.stat().st_size / 1e6:.1f} MB). Carry it up by hand: see README "Upload pack".')
    return 0


if __name__ == '__main__':
    sys.exit(main())
