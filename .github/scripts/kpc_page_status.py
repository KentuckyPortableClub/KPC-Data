#!/usr/bin/env python3
"""PAGE-READER-STATUS.txt: one screen, plain words, what the page reader has and what to do next (26 Nov 2026; owner:
"I am tired of pressing the same buttons again and still coming up short").

Reads only files on this PC (out/facts/*.json, out/state.json, pages-kept/manifest.json). It never asks a website.

  python kpc_page_status.py --out out [--status-file ..\\PAGE-READER-STATUS.txt]
"""
import argparse, collections, datetime, json, os, pathlib, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_net_rule as NR  # noqa: E402

SECONDS_PER_PAGE = 4      # a normal site: our 2 s gap, the answer, and a second page for some parks
SECONDS_PER_KEPT = 0.05   # re-reading a kept page: no website, only this PC


def _load(p, default):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except Exception:  # noqa: BLE001
        return default


def country(area):
    a = str(area or '')
    return 'US' if a.startswith('US') else 'Canada' if a.startswith('CA') else (a.split('-')[0] or 'other')


def default_status_file(out_dir):
    o = pathlib.Path(out_dir).resolve()
    return (o.parent.parent if o.parent.name == 'page-reader' else o) / 'PAGE-READER-STATUS.txt'


def park_status(fact):
    """-> (read?, reason code or '', host, name state, size state) for one saved park fact."""
    pg = fact.get('page') or {}
    own = fact.get('own_page') or {}
    kind, st = pg.get('kind'), pg.get('status')
    host = pg.get('host') or own.get('host') or ''
    nr = pg.get('not_read') or {}
    read = kind in ('html', 'pdf')
    reason = '' if read else (nr.get('reason') or NR.reason_of(st, kind, own.get('is')))
    nm = fact.get('name') or {}
    if not read:
        name = ''
    elif nm.get('best'):
        name = 'real'
    elif nm.get('set_aside'):
        name = 'junk'
    else:
        name = 'none'
    sizes = fact.get('sizes') or []
    if not read:
        size = ''
    elif any(s.get('total') and s.get('clean') for s in sizes):
        size = 'clean'
    elif any(s.get('disagrees_with') for s in sizes):
        size = 'disagree'
    elif any(s.get('ambiguous') for s in sizes):
        size = 'ambiguous'
    elif sizes:
        size = 'not-clean'
    else:
        size = 'none'
    return read, reason, host, name, size


def gather(out_dir):
    facts_dir = pathlib.Path(out_dir) / 'facts'
    by_ref = {}
    for f in sorted(facts_dir.glob('*.json')) if facts_dir.is_dir() else []:
        doc = _load(f, {}) or {}
        area = doc.get('area') or f.stem
        for ref, fact in (doc.get('parks') or {}).items():
            if isinstance(fact, dict) and not fact.get('unchanged'):
                by_ref.setdefault(ref, (area, fact))   # a park listed in two areas is counted once
    c = {'read': collections.Counter(), 'all': collections.Counter(), 'reason': collections.Counter(),
         'hosts': collections.defaultdict(collections.Counter), 'name': collections.Counter(), 'size': collections.Counter(),
         'failed_kept': 0}
    for ref, (area, fact) in by_ref.items():
        read, reason, host, name, size = park_status(fact)
        k = country(area)
        c['all'][k] += 1
        if read:
            c['read'][k] += 1
            c['name'][name] += 1
            c['size'][size] += 1
            if (fact.get('page') or {}).get('last_try'):
                c['failed_kept'] += 1
        else:
            c['reason'][reason] += 1
            c['hosts'][reason][host or '(no address)'] += 1
    return c


def render(out_dir, now=None, kept_pages=None):
    c = gather(out_dir)
    now = now or datetime.datetime.now()
    if kept_pages is None:
        kept_pages = len((_load(pathlib.Path(out_dir).resolve().parent / 'pages-kept' / 'manifest.json', {}) or {}).get('pages') or {})
    total, read = sum(c['all'].values()), sum(c['read'].values())
    L = [f'PAGE READER STATUS   {now.strftime("%Y-%m-%d %H:%M")}   (made from the files on this PC; no website was asked)', '']
    L.append(f'Parks with their page read: {read:,} of {total:,}   ' + '   '.join(f'{k} {c["read"][k]:,} of {c["all"][k]:,}' for k in sorted(c['all'])))
    if c['failed_kept']:
        L.append(f'  {c["failed_kept"]:,} of them failed on the last try and kept their earlier facts (the failure is noted beside them).')
    L.append('')
    L.append(f'NOT read: {total - read:,} parks. Why (only the first line is a real "no"):')
    for code, words in NR.REASONS:
        n = c['reason'].get(code, 0)
        if not n and code == 'club-rule':
            continue
        top = ', '.join(f'{h} {k:,}' for h, k in c['hosts'][code].most_common(3)) if n else ''
        L.append(f'  {n:>6,}  {words}' + (f'\n          top sites: {top}' if top else ''))
    L.append('')
    nm, sz = c['name'], c['size']
    L.append(f'Names (of the {read:,} read): {nm["real"]:,} have an official name from the page; {nm["none"]:,} have none; '
             f'{nm["junk"]:,} had only a heading, menu or site name, set aside.')
    L.append(f'Sizes (of the {read:,} read): {sz["clean"]:,} have a clean total; {sz["disagree"]:,} set aside (two totals disagree); '
             f'{sz["ambiguous"]:,} set aside (the number reads two ways); {sz["not-clean"]:,} only part sizes; {sz["none"]:,} no size.')
    L.append('')
    due = sum(c['reason'].get(k, 0) for k in ('busy', 'stopped', 'disallow'))
    slow = c['reason'].get('slow', 0)
    mins_kept = max(1, round(kept_pages * SECONDS_PER_KEPT / 60)) if kept_pages else 0
    hrs = due * SECONDS_PER_PAGE / 3600
    when = 'under an hour' if hrs < 1 else f'about {hrs:.0f} h'
    L.append('What to do next (fewest steps):')
    step = 1
    if kept_pages:
        L.append(f'  {step}. PAGE-READER.bat, choice 2: read the {kept_pages:,} kept pages again with the newest rules. No website. About {mins_kept} min.')
        step += 1
    if due or slow:
        L.append(f'  {step}. PAGE-READER.bat, choice 3: read ONLY the pages not read above ({due:,} parks, {when}), then the '
                 f'{slow:,} on slow sites as slowly as each asks (leave it overnight; it carries on next time).')
        step += 1
    if c['reason'].get('disallow'):
        L.append(f'  {step}. The {c["reason"]["disallow"]:,} "real Disallow" parks: a hand look only (the list is out\\robots-disallow-hand-look.csv).')
        step += 1
    if step == 1:
        L.append('  Nothing. Every park that can be read is read.')
    L.append('  Then 5-MAKE-UPLOAD-PACK.bat as before.')
    return '\n'.join(L) + '\n'


def write(out_dir, status_file=None, now=None):
    p = pathlib.Path(status_file) if status_file else default_status_file(out_dir)
    text = render(out_dir, now=now)
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    if tmp.read_text(encoding='utf-8') != text:
        raise OSError(f'{p}: the status page did not read back the same')
    os.replace(tmp, p)
    return p, text


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--status-file', default='')
    a = ap.parse_args(argv)
    p, text = write(a.out, a.status_file or None)
    print(text)
    print(f'(saved as {p})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
