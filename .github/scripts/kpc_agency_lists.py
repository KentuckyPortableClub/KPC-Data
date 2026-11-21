#!/usr/bin/env python3
"""kpc_agency_lists.py: an agency's own park list, read once, as a small crosswalk from its website id to its map id.

Many agencies publish one list or table that holds both their website id (the number in the park's page address, which POTA
links to) and their map or unit id (which the map record carries). This tool reads that one list per agency and writes
agency-crosswalk/<agency>.json:
  {"agency", "link_kind", "source": {"url", "licence", "terms_url", "date"}, "rows": [{"web_id", "map_layer", "map_field", "map_id"}]}
The keys then treat a web id that maps through this file the same as a direct id tie (KPC-Data park facts carries the file;
KPC-Links kpc_match_checks reads it). It never decides a join itself.

It is a tool the KEEPER calls (only the keeper fetches from agency servers). Every agency is OFF in .github/agency-lists.json
until a person has filled in and checked its official source, licence or terms, and robots.txt; nothing is read for an agency
that is off.
  - robots.txt: read and parsed by our own parser (kpc_manners.parse_robots, never urllib.robotparser); a parse error, an
    unreadable file or a Disallow = not fetched.
  - the list itself: kpc_manners.Manners.get(url, deadline=..., max_time=...), one request per agency per run.
  - a read that is skipped (robots, unreadable, resting, a time limit, a bad answer) KEEPS the earlier file exactly as it was.
  - never WDPA: an agency whose source, layer or field is a WDPA one is refused, and a WDPA value is never written.

  python3 .github/scripts/kpc_agency_lists.py --config .github/agency-lists.json --out agency-crosswalk [--minutes 10]
  python3 .github/scripts/kpc_agency_lists.py --selftest
"""
import argparse, csv, datetime, io, json, os, re, sys, tempfile, time

VERSION = 'kpc_agency_lists 2026-11-21b'
WDPA = re.compile(r'wdpa|protectedplanet', re.I)
FORMATS = ('csv', 'json-rows', 'arcgis-json')


def say(*a):
    print(*a, flush=True)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', str(s or '').lower()).strip('-') or 'agency'


def problems(a):
    """Why an agency entry may not be read ([] = it may). Off, or anything missing, or any WDPA trace = not read."""
    out = []
    if not a.get('enabled'):
        out.append('off in the config')
    for k in ('agency', 'link_kind', 'source_url', 'licence', 'terms_url', 'format', 'web_id', 'map'):
        if not a.get(k):
            out.append(f'no {k}')
    if a.get('format') and a['format'] not in FORMATS:
        out.append(f"format {a['format']!r} is not one of {', '.join(FORMATS)}")
    m = a.get('map') or {}
    for k in ('layer', 'field', 'value'):
        if not m.get(k):
            out.append(f'no map.{k}')
    w = a.get('web_id') or {}
    if not w.get('column'):
        out.append('no web_id.column')
    text = json.dumps(a)
    if WDPA.search(text):
        out.append('a WDPA source, layer or field: never used')
    if a.get('source_url') and not re.match(r'^https://', a['source_url']):
        out.append('the source is not an https address')
    if a.get('licence_ok') is not True:
        out.append('the licence is not checked as allowing our use (licence_ok)')
    if not str(a.get('robots') or '').lower().startswith('allowed'):
        out.append('robots.txt is not read as allowing the path (robots)')
    if a.get('source_url'):
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import kpc_host_rules
            hok, why = kpc_host_rules.host_ok(a['source_url'])
        except Exception as e:  # no host rules = fail closed
            hok, why = False, f'host rules not readable ({type(e).__name__})'
        if not hok:
            out.append(why)
    return out


def rows_of(body, fmt):
    """The list's rows as dicts. csv: a header row; json-rows: a JSON list of objects (or {'rows'|'data'|'features': [...]});
    arcgis-json: an ArcGIS query answer ({'features': [{'attributes': {...}}]})."""
    if fmt == 'csv':
        text = body.decode('utf-8-sig', errors='replace')
        return list(csv.DictReader(io.StringIO(text)))
    d = json.loads(body.decode('utf-8-sig', errors='replace'))
    if fmt == 'arcgis-json':
        return [f.get('attributes') or {} for f in (d.get('features') or [])]
    if isinstance(d, dict):
        d = d.get('rows') or d.get('data') or d.get('features') or []
    return [r.get('attributes', r) if isinstance(r, dict) else {} for r in d]


def crosswalk_rows(rows, a):
    """[{'web_id','map_layer','map_field','map_id'}] from the list rows. A web id may come from a column directly, or from a
    page address in that column through web_id.regex (group 1). A row with no web id or no map id is left out; a web id that
    two rows give two different map ids is left out too (not one-to-one: no tie)."""
    w, m = a['web_id'], a['map']
    rx = re.compile(w['regex'], re.I) if w.get('regex') else None
    seen, clash = {}, set()
    for r in rows:
        raw = str(r.get(w['column']) or '').strip()
        mid = str(r.get(m['value']) or '').strip()
        if rx:
            mm = rx.search(raw)
            raw = mm.group(1) if mm else ''
        if not raw or not mid or WDPA.search(mid):
            continue
        wid = raw.upper()
        if wid in seen and seen[wid] != mid:
            clash.add(wid)
        seen.setdefault(wid, mid)
    return [{'web_id': k, 'map_layer': m['layer'], 'map_field': m['field'], 'map_id': v}
            for k, v in sorted(seen.items()) if k not in clash], len(clash)


def write_file(path, doc):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, path)


def run(config_path, out_dir, minutes=10, getter=None, today=None):
    """-> {agency: what happened}. getter = a kpc_manners.Manners (or a test stand-in with .get(url, deadline=, max_time=))."""
    say(f'{VERSION}  (Python {sys.version.split()[0]})')
    with open(config_path, encoding='utf-8') as f:
        cfg = json.load(f)
    os.makedirs(out_dir, exist_ok=True)
    deadline = time.time() + minutes * 60
    today = today or datetime.date.today().isoformat()
    report = {}
    for a in cfg.get('agencies') or []:
        name = a.get('agency') or '?'
        path = os.path.join(out_dir, slug(name) + '.json')
        why = problems(a)
        if why:
            report[name] = 'not read: ' + '; '.join(why)
            continue
        if getter is None:
            from kpc_manners import Manners
            getter = Manners('agency lists')
        if time.time() >= deadline:
            report[name] = 'not read: out of time this run (the earlier file is kept as it was)'
            continue
        st, hd, body, final = getter.get(a['source_url'], deadline=deadline, max_time=min(120, max(1, deadline - time.time())))
        if st != 200 or not body:
            report[name] = f'not read: {st} (the earlier file is kept as it was)'
            continue
        try:
            rows = rows_of(body, a['format'])
        except (ValueError, UnicodeDecodeError, csv.Error) as e:
            report[name] = f'not read: the list could not be parsed ({type(e).__name__}); the earlier file is kept as it was'
            continue
        xw, clashes = crosswalk_rows(rows, a)
        if not xw:
            report[name] = 'read, but no row gave both ids: the earlier file is kept as it was'
            continue
        doc = {'agency': name, 'link_kind': a['link_kind'], 'made_by': VERSION,
               'source': {'url': a['source_url'], 'final_url': final or a['source_url'], 'licence': a['licence'],
                          'terms_url': a['terms_url'], 'date': today},
               'rows': xw, 'left_out_not_one_to_one': clashes}
        write_file(path, doc)
        report[name] = f'written: {len(xw)} web ids' + (f' ({clashes} left out: two map ids)' if clashes else '')
    for k, v in report.items():
        say(f'  {k}: {v}')
    return report


# ------------------------------------------------------------------ self-test ---------------------------------------------
class _Stand:
    """A stand-in for kpc_manners.Manners: answers from a dict, records each call's deadline and max_time."""
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def get(self, url, deadline=None, max_time=None, **kw):
        self.calls.append((url, deadline, max_time))
        return self.answers.get(url, ('err:no answer', {}, b'', url))


def selftest():
    say(f'{VERSION}  (Python {sys.version.split()[0]})  SELF-TEST')
    bad = []

    def check(what, cond):
        say(f'  {"ok  " if cond else "FAIL"} {what}')
        if not cond:
            bad.append(what)
    base = {'enabled': True, 'agency': 'Invented Parks', 'link_kind': 'ZZ page number', 'source_url': 'https://lists.invented.example/parks.csv',
            'licence': 'public domain (invented)', 'licence_ok': True, 'robots': 'allowed (read 2026-11-21)',
            'terms_url': 'https://lists.invented.example/terms', 'format': 'csv',
            'web_id': {'column': 'Web page', 'regex': r'invented\.example/park/(\d+)'}, 'map': {'layer': 'sgzza', 'field': 'UNIT_NO', 'value': 'Unit'}}
    csv_body = ('Name,Web page,Unit\nA,https://invented.example/park/101,U-1\nB,https://invented.example/park/102,U-2\n'
                'C,,U-3\nD,https://invented.example/park/104,\nE,https://invented.example/park/105,U-5\nE2,https://invented.example/park/105,U-6\n').encode()
    with tempfile.TemporaryDirectory() as t:
        cfgp, out = os.path.join(t, 'cfg.json'), os.path.join(t, 'out')

        def go(agencies, answers, minutes=10):
            json.dump({'agencies': agencies}, open(cfgp, 'w'))
            g = _Stand(answers)
            return run(cfgp, out, minutes, getter=g, today='2026-11-21'), g
        rep, g = go([base], {base['source_url']: (200, {}, csv_body, base['source_url'])})
        doc = json.load(open(os.path.join(out, 'invented-parks.json')))
        check('a read list becomes web id -> map id rows', [(r['web_id'], r['map_id']) for r in doc['rows']] == [('101', 'U-1'), ('102', 'U-2')])
        check('a web id with two map ids is left out (not one-to-one)', doc['left_out_not_one_to_one'] == 1)
        check('the file names its source, licence and date', doc['source']['licence'] and doc['source']['date'] == '2026-11-21')
        check('the fetch is given a deadline and a max_time', g.calls and g.calls[0][1] is not None and g.calls[0][2] is not None and g.calls[0][2] <= 120)
        before = open(os.path.join(out, 'invented-parks.json'), 'rb').read()
        for st in ('robots', 'robots-unreadable', 'rest', 'host-rule', 'crawl-delay', 'err:timeout', 404):
            go([base], {base['source_url']: (st, {}, b'', base['source_url'])})
            check(f'a skipped read ({st}) keeps the earlier file exactly', open(os.path.join(out, 'invented-parks.json'), 'rb').read() == before)
        go([base], {base['source_url']: (200, {}, b'\x00not a list', base['source_url'])})
        check('an answer that does not parse keeps the earlier file', open(os.path.join(out, 'invented-parks.json'), 'rb').read() == before)
        rep, g = go([dict(base, enabled=False)], {})
        check('an agency that is off is not read at all', not g.calls and 'off in the config' in rep['Invented Parks'])
        rep, g = go([dict(base, licence='')], {})
        check('no licence: not read', not g.calls and 'no licence' in rep['Invented Parks'])
        rep, g = go([dict(base, licence_ok=False)], {})
        check('licence not checked as allowing our use: not read', not g.calls and 'licence_ok' in rep['Invented Parks'])
        rep, g = go([dict(base, robots='disallowed for AI crawlers')], {})
        check('robots.txt not read as allowing the path: not read', not g.calls and 'robots' in rep['Invented Parks'])
        for u in ('https://services5.arcgis.com/x/ArcGIS/rest/services/L/FeatureServer/0/query', 'https://apps.fs.usda.gov/arcx/rest/services/x/MapServer/0/query',
                  'https://ncnhde.natureserve.org/list.csv'):
            rep, g = go([dict(base, source_url=u)], {})
            check(f'a saved-copies-only or never-contact host is never read ({u.split("/")[2]})', not g.calls and rep['Invented Parks'] != 'read')
        wd = dict(base, agency='Invented WDPA', map={'layer': 'wdpa', 'field': 'WDPA_PID', 'value': 'Unit'})
        rep, g = go([wd], {base['source_url']: (200, {}, csv_body, base['source_url'])})
        check('a WDPA layer or field is refused, never read', not g.calls and 'WDPA' in rep['Invented WDPA'])
        check('a WDPA value is never written', crosswalk_rows([{'Web page': 'https://invented.example/park/9', 'Unit': 'WDPA 555'}], base)[0] == [])
        rep, g = go([dict(base, source_url='http://lists.invented.example/parks.csv')], {})
        check('a plain http source is refused', not g.calls and 'https' in rep['Invented Parks'])
        rep, g = go([base], {base['source_url']: (200, {}, csv_body, base['source_url'])}, minutes=0)
        check('out of time: not read, earlier file kept', not g.calls and open(os.path.join(out, 'invented-parks.json'), 'rb').read() == before)
        js = json.dumps({'features': [{'attributes': {'PAGEID': '7', 'UNIT': 'A7'}}]}).encode()
        arc = dict(base, agency='Invented Arc', format='arcgis-json', web_id={'column': 'PAGEID'}, map={'layer': 'sgzzb', 'field': 'UNIT', 'value': 'UNIT'})
        go([arc], {base['source_url']: (200, {}, js, base['source_url'])})
        check('an ArcGIS answer is read the same way', json.load(open(os.path.join(out, 'invented-arc.json')))['rows'][0]['map_id'] == 'A7')
    cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'agency-lists.json'), encoding='utf-8'))
    check('the shipped config has every agency OFF until a person checks its source, licence and robots.txt',
          all(not a.get('enabled') for a in cfg.get('agencies') or []))
    say('')
    say('SELF-TEST PASSED' if not bad else f'SELF-TEST FAILED: {len(bad)}: ' + '; '.join(bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="An agency's own park list as a web id -> map id crosswalk (the keeper calls it).")
    ap.add_argument('--config', default='.github/agency-lists.json')
    ap.add_argument('--out', default='agency-crosswalk')
    ap.add_argument('--minutes', type=float, default=10)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    run(a.config, a.out, a.minutes)
    return 0


if __name__ == '__main__':
    sys.exit(main())
