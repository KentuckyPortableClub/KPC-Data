#!/usr/bin/env python3
"""kpc_hand_copies.py: which hand-copied sizes do not name their source (21 Nov 2026, job C).

A hand copy is a size a person typed in from an agency's figure. It can only be checked when it names the page it was copied
from (source_url, a web address) and the agency. The key counts a hand copy only when source_url is there (KPC-Links
kpc_match_checks.tagged_witness). This tool lists the ones that do not:

  python3 kpc_hand_copies.py --acres acres.json --parkinfo data/parkinfo --out hand-copies-out
      hand-copies-missing-source.json          PUBLIC: counts by state only (no park numbers, no names)
      PRIVATE-hand-copies-missing-source.csv   park number, state, agency, what is missing (keep it off public branches)
  python3 kpc_hand_copies.py --lines research.json
      checks a research file's hand-copy lines against the template (hand-copy-template.json): every line needs agency
      and source_url. Exit 1 when a line misses one.
  python3 kpc_hand_copies.py --selftest

It reads files only: no network, and it changes no input.
"""
import argparse, collections, csv, datetime, glob, json, os, re, sys, tempfile

VERSION = 'kpc_hand_copies 2026-11-21a'
URL = re.compile(r'^https?://\S+\.\S+', re.I)
UNKNOWN_AGENCY = {'', 'unknown agency', 'unknown', 'none', 'n/a'}
REF = re.compile(r'^[A-Z0-9]{1,4}-\d{4,5}$')


def missing(row):
    """[what a hand copy lacks] ('source_url', 'agency'); [] = it names its source."""
    out = []
    if not URL.match(str(row.get('source_url') or row.get('_page') or '').strip()):
        out.append('source_url')
    if str(row.get('agency') or row.get('_agency') or '').strip().lower() in UNKNOWN_AGENCY:
        out.append('agency')
    return out


def is_hand(row):
    return str(row.get('how') or '').lower().startswith('hand copy') or row.get('witness') == 'hand_copy'


def states_of(parkinfo):
    """{ref: area} from data/parkinfo (the POTA list), read the way park facts reads it."""
    if not parkinfo:
        return {}
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kpc_park_facts'))
    import kpc_park_facts as PF
    return {ref: r.get('area') for ref, r in PF.read_parkinfo(parkinfo).items()}


def check(acres_path, parkinfo=None, facts_path=None):
    """-> (counts doc, private rows). Reads the acreage bot's acres.json, or park facts' park-facts.json(.gz) (size rows)."""
    rows = {}
    if acres_path:
        with open(acres_path, encoding='utf-8') as f:
            d = json.load(f)
        rows = {k: v for k, v in (d.get('parks', d) if isinstance(d, dict) else {}).items() if isinstance(v, dict)}
        area_of = states_of(parkinfo)
    else:
        import gzip
        op = gzip.open if str(facts_path).endswith('.gz') else open
        with op(facts_path, 'rt', encoding='utf-8') as f:
            d = json.load(f)
        area_of = {k: v.get('area') for k, v in (d.get('parks') or {}).items()}
        rows = {k: v['size'] for k, v in (d.get('parks') or {}).items() if isinstance(v.get('size'), dict)}
    by_state, private = collections.defaultdict(collections.Counter), []
    for ref, r in sorted(rows.items()):
        if not is_hand(r):
            continue
        st = area_of.get(ref) or 'unknown'
        by_state[st]['hand copies'] += 1
        miss = missing(r)
        if not miss:
            by_state[st]['name their source'] += 1
            continue
        by_state[st]['missing a source'] += 1
        for m in miss:
            by_state[st]['no ' + m] += 1
        private.append({'park': ref, 'state': st, 'agency': r.get('agency') or '', 'missing': ' and '.join(miss)})
    tot = collections.Counter()
    for c in by_state.values():
        tot.update(c)
    doc = {'made': datetime.date.today().isoformat(), 'tool': VERSION,
           'note': 'Hand-copied sizes that do not name their source page or agency, counted by state. The key counts a hand copy '
                   'only when it names its source page. Park numbers are in the PRIVATE file only.',
           'total': dict(sorted(tot.items())), 'by_state': {k: dict(sorted(v.items())) for k, v in sorted(by_state.items())}}
    return doc, private


def write(out, doc, private):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'hand-copies-missing-source.json'), 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write('\n')
    with open(os.path.join(out, 'PRIVATE-hand-copies-missing-source.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['park', 'state', 'agency', 'missing'])
        w.writeheader()
        w.writerows(private)


def check_lines(research_path):
    """-> [(line number, name, what is missing)] for a research file's hand-copy lines (read the way the acreage bot reads them)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kpc_acres'))
    import kpc_acres as A
    _cfgs, hand, _seen = A.load_research(research_path)
    bad = []
    for i, r in enumerate(hand, 1):
        m = missing(r)
        if m:
            bad.append((i, str(A.pick(r, *A.H_NAME) or '?'), ' and '.join(m)))
    return bad, len(hand)


def selftest():
    print(f'{VERSION}  (Python {sys.version.split()[0]})  SELF-TEST')
    bad = []

    def ok(what, cond):
        print(f'  {"ok  " if cond else "FAIL"} {what}')
        if not cond:
            bad.append(what)
    with tempfile.TemporaryDirectory() as t:
        pi = os.path.join(t, 'parkinfo'); os.makedirs(pi)
        json.dump({'parks': {'US-9001': ['Invented Lake State Park', '', 'State Park'], 'US-9002': ['Invented Hill State Park', '', 'State Park']}},
                  open(os.path.join(pi, 'US-ZZ.json'), 'w'))
        json.dump({'parks': {'US-9003': ['Invented Marsh', '', 'Wildlife Area'], 'US-9004': ['Invented Bay', '', 'State Park']}},
                  open(os.path.join(pi, 'US-YY.json'), 'w'))
        acres = {'US-9001': {'acres': 10, 'how': 'hand copy (ZZ Parks, page not given)', 'agency': 'ZZ Parks', 'source_url': ''},
                 'US-9002': {'acres': 20, 'how': 'hand copy (ZZ Parks, https://zz.invented.example/p)', 'agency': 'ZZ Parks',
                             'source_url': 'https://zz.invented.example/p'},
                 'US-9003': {'acres': 30, 'how': 'hand copy (unknown agency, page not given)', 'agency': 'unknown agency', 'source_url': ''},
                 'US-9004': {'acres': 40, 'how': 'number', 'agency': 'YY Parks', 'source_url': ''}}
        ap = os.path.join(t, 'acres.json'); json.dump(acres, open(ap, 'w'))
        before = open(ap, 'rb').read()
        doc, private = check(ap, pi)
        ok('counts by state', doc['by_state'] == {'US-YY': {'hand copies': 1, 'missing a source': 1, 'no agency': 1, 'no source_url': 1},
                                                  'US-ZZ': {'hand copies': 2, 'missing a source': 1, 'name their source': 1, 'no source_url': 1}})
        ok('only hand copies are looked at (a list size is not)', all(p['park'] != 'US-9004' for p in private))
        ok('the private rows name the park and what is missing', [(p['park'], p['missing']) for p in private] ==
           [('US-9001', 'source_url'), ('US-9003', 'source_url and agency')])
        out = os.path.join(t, 'out'); write(out, doc, private)
        pub = open(os.path.join(out, 'hand-copies-missing-source.json'), encoding='utf-8').read()
        ok('the public file names no park', not re.search(r'[A-Z]{2}-\d{4}', pub.replace('US-ZZ', '').replace('US-YY', '')))
        ok('the private file says PRIVATE in its name', os.path.exists(os.path.join(out, 'PRIVATE-hand-copies-missing-source.csv')))
        ok('no input changed', open(ap, 'rb').read() == before)
        rp = os.path.join(t, 'research.json')
        json.dump({'hand_copies': [{'park_name': 'Invented Lake State Park', 'size': 12, 'unit': 'acres', 'agency': 'ZZ Parks',
                                    'source_url': 'https://zz.invented.example/l'},
                                   {'park_name': 'Invented Marsh', 'size': 5, 'unit': 'acres'}]}, open(rp, 'w'))
        lines, n = check_lines(rp)
        ok('a research line without agency or source_url is listed', n == 2 and [(x[1], x[2]) for x in lines] == [('Invented Marsh', 'source_url and agency')])
    tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand-copy-template.json')
    lines, n = check_lines(tp)
    ok('the template line itself carries agency and source_url', n == 1 and not lines)
    print('SELF-TEST PASSED' if not bad else f'SELF-TEST FAILED: {len(bad)}')
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='Hand-copied sizes that do not name their source.')
    ap.add_argument('--acres', help="the acreage bot's acres.json")
    ap.add_argument('--facts', help="park facts' park-facts.json(.gz) (instead of --acres)")
    ap.add_argument('--parkinfo', help='data/parkinfo (each park\'s state, with --acres)')
    ap.add_argument('--out', default='hand-copies-out')
    ap.add_argument('--lines', help="a research file: check its hand-copy lines against the template")
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.lines:
        bad, n = check_lines(a.lines)
        print(f'{n} hand-copy lines, {len(bad)} without agency or source_url')
        for i, name, m in bad:
            print(f'  line {i}: {name}: no {m}')
        return 1 if bad else 0
    if not (a.acres or a.facts):
        ap.error('give --acres or --facts')
    doc, private = check(a.acres, a.parkinfo, a.facts)
    write(a.out, doc, private)
    print(f"{doc['total'].get('hand copies', 0)} hand copies, {doc['total'].get('missing a source', 0)} missing a source "
          f"({len(doc['by_state'])} states); park numbers in {a.out}/PRIVATE-hand-copies-missing-source.csv")
    return 0


if __name__ == '__main__':
    sys.exit(main())
