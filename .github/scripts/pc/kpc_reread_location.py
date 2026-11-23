#!/usr/bin/env python3
"""kpc_reread_location.py (22 Nov 2026, owner: "a script to run and pull everyone we need just the address or gps"):
before the park page reader runs on this PC, mark for reading again every park whose OWN official page was read but gave no
place to go by: no address and no map point, or no directions that name a road or a town. The reader's address and
directions finders were widened on 22 Nov; reading these pages again fills them in. Only the state's 'read' entry and the
page's fingerprint are dropped (so the next run reads the page again); the facts stay until the new read replaces them.
Each park is marked once (out\\reread-location.json remembers it). Counts only, never a park name.
  python kpc_reread_location.py --out page-reader\\out          (--selftest: invented parks; --count: count, change nothing)"""
import argparse, datetime, json, pathlib, sys, tempfile

REAL = ('html', 'pdf')


def wants_place(fact):
    """True when the park's own official page was read and it gave no place to go by."""
    if not isinstance(fact, dict) or fact.get('unofficial'):
        return False
    if ((fact.get('page') or {}).get('kind')) not in REAL:
        return False
    if (fact.get('own_page') or {}).get('is') != 'own':
        return False
    loc = fact.get('location') or {}
    d = loc.get('directions') or {}
    no_spot = not loc.get('addresses') and not loc.get('coords')
    no_way = not (d.get('roads') or d.get('towns'))
    return no_spot or no_way


def run(out, today=None, count_only=False):
    out = pathlib.Path(out)
    sp, mp = out / 'state.json', out / 'reread-location.json'
    if not sp.is_file():
        print('No state.json yet: nothing to do.')
        return 0
    state = json.loads(sp.read_text(encoding='utf-8'))
    done = json.loads(mp.read_text(encoding='utf-8')) if mp.is_file() else {}
    read, fps = state.get('read') or {}, state.get('fingerprints') or {}
    n = want = 0
    for f in sorted((out / 'facts').glob('*.json')):
        try:
            parks = (json.loads(f.read_text(encoding='utf-8')) or {}).get('parks') or {}
        except ValueError:
            continue
        for ref, fact in parks.items():
            if not wants_place(fact):
                continue
            want += 1
            if ref in done or count_only:
                continue
            r = read.pop(ref, None)
            if r:
                for k in [k for k, v in fps.items() if v == r.get('fingerprint')]:
                    fps.pop(k, None)
            done[ref] = today or datetime.date.today().isoformat()
            n += 1
    if count_only:
        print(f'Own pages with no address, point or directions: {want} (marked before: {sum(1 for _ in done)}).')
        return 0
    if n:
        tmp = sp.with_name(sp.name + '.tmp')
        tmp.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
        tmp.replace(sp)
        mp.write_text(json.dumps(done, indent=0, sort_keys=True), encoding='utf-8')
    print(f'Own pages with no address, point or directions, read again from now on: {n} '
          f'(marked before: {len(done) - n}; still without them after the re-read: shown next time).')
    return 0


def selftest():
    with tempfile.TemporaryDirectory() as t:
        o = pathlib.Path(t)
        (o / 'facts').mkdir()
        own = {'is': 'own'}
        parks = {
            'K4-0001': {'page': {'kind': 'html'}, 'own_page': own, 'location': {}},                       # nothing: re-read
            'K4-0002': {'page': {'kind': 'html'}, 'own_page': own,
                        'location': {'addresses': [{'text': '1 Test Rd, Testville, KY 40000'}],
                                     'directions': {'roads': ['Test Road'], 'towns': []}}},           # has both: keep
            'K4-0003': {'page': {'kind': 'refused'}, 'own_page': own, 'location': {}},                  # not a real read
            'K4-0004': {'page': {'kind': 'html'}, 'own_page': {'is': 'list'}, 'location': {}},           # a list page
            'K4-0005': {'page': {'kind': 'pdf'}, 'own_page': own,
                        'location': {'coords': [{'lat': 37, 'lon': -85}], 'directions': {'sent': 'Hours Fees', 'roads': [], 'towns': []}}},  # menu text: re-read
        }
        (o / 'facts' / 'US-ZZ.json').write_text(json.dumps({'parks': parks}), encoding='utf-8')
        (o / 'state.json').write_text(json.dumps({'read': {r: {'fingerprint': r[-1]} for r in parks},
                                                  'fingerprints': {'x.gov/' + r[-1]: r[-1] for r in parks}}), encoding='utf-8')
        run(o, '2026-11-22')
        s = json.loads((o / 'state.json').read_text(encoding='utf-8'))
        ok = sorted(s['read']) == ['K4-0002', 'K4-0003', 'K4-0004'] and sorted(s['fingerprints']) == ['x.gov/2', 'x.gov/3', 'x.gov/4']
        run(o, '2026-11-23')   # a second run marks nothing again
        s2 = json.loads((o / 'state.json').read_text(encoding='utf-8'))
        ok = ok and s2 == s and sorted(json.loads((o / 'reread-location.json').read_text())) == ['K4-0001', 'K4-0005']
    print('selftest', 'ALL PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out')
    ap.add_argument('--count', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else run(a.out, count_only=a.count))
