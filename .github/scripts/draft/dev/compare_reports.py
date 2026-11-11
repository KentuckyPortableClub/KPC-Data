#!/usr/bin/env python3
"""Compare two picture-tracer report.csv files (before / after a tracer change). Nov 11 (KPC owner, 2026-11-11). Offline, read only.

  python3 compare_reports.py before.csv after.csv [--md out.md]

Prints: status counts before -> after; every map whose status changed; the NO FIT reasons before -> after; and, for every map that is
newly DRAWN, the inputs a person grades it by (points, fit, leave-one-out, line share / z against the decoy's, acres ratio, pin
distance) with its debug picture names. A map that WAS drawn and no longer is gets its own list (a regression to look at first)."""
import argparse, collections, csv, re, sys

ORDER = ['DRAWN', 'UNOFFICIAL MAP', 'NEEDS A PERSON', 'NO FIT', 'NO LINE', 'ERROR']


def read(p):
    with open(p, newline='', encoding='utf-8') as f:
        return {r['ref']: r for r in csv.DictReader(f)}


def bucket(why):
    w = why or ''
    out = []
    if 'not better than chance' in w: out.append('not better than a rotated decoy')
    if 'leave-one-out' in w: out.append('leave-one-out over 50 m')
    if re.search(r'RMS fit [\d.]+ m is not under', w): out.append('RMS over 50 m')
    m = re.search(r'only (\d+) control point', w)
    if m: out.append(f'only {m.group(1)} control point(s)')
    if 'no basemap control points' in w: out.append('no basemap control points')
    if "do not sit on the picture's lines" in w: out.append('lines do not agree (new gate)')
    return ' + '.join(out) or (w[:60] if w else '(none)')


def nl_bucket(why):
    w = why or ''
    if 'of the POTA pin on this page' in w: return 'GeoPDF page: no shape in any colour at the pin'
    if 'no closed boundary colour' in w: return 'no closed boundary colour / route line on the picture'
    return w[:60] or '(none)'


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('before'); ap.add_argument('after'); ap.add_argument('--md')
    a = ap.parse_args(argv)
    B, A = read(a.before), read(a.after)
    L = []
    cb = collections.Counter(r['status'] for r in B.values()); ca = collections.Counter(r['status'] for r in A.values())
    L.append(f'maps: {len(B)} before, {len(A)} after; in both: {len(set(B) & set(A))}')
    L.append('| status | before | after |'); L.append('|---|---|---|')
    for s in sorted(set(cb) | set(ca), key=lambda s: ORDER.index(s) if s in ORDER else 99):
        L.append(f'| {s} | {cb.get(s, 0)} | {ca.get(s, 0)} |')
    nf_b = collections.Counter(bucket(r['why']) for r in B.values() if r['status'] == 'NO FIT')
    nf_a = collections.Counter(bucket(r['why']) for r in A.values() if r['status'] == 'NO FIT')
    L.append(''); L.append('| NO FIT reason | before | after |'); L.append('|---|---|---|')
    for k in sorted(set(nf_b) | set(nf_a), key=lambda k: -(nf_b.get(k, 0) + nf_a.get(k, 0))):
        L.append(f'| {k} | {nf_b.get(k, 0)} | {nf_a.get(k, 0)} |')
    # Nov 11: the NO LINE and ERROR reasons too (an 'offline:' ERROR = no saved basemap for that map in an --offline replay)
    for st, fn in (('NO LINE', nl_bucket), ('ERROR', lambda w: 'offline: no saved basemap' if (w or '').startswith('offline:') else (w or '(none)')[:60])):
        xb = collections.Counter(fn(r['why']) for r in B.values() if r['status'] == st)
        xa = collections.Counter(fn(r['why']) for r in A.values() if r['status'] == st)
        if xb or xa:
            L.append(''); L.append(f'| {st} reason | before | after |'); L.append('|---|---|---|')
            for k in sorted(set(xb) | set(xa), key=lambda k: -(xb.get(k, 0) + xa.get(k, 0))):
                L.append(f'| {k} | {xb.get(k, 0)} | {xa.get(k, 0)} |')
    moved = collections.Counter((B[r]['status'], A[r]['status']) for r in set(B) & set(A) if B[r]['status'] != A[r]['status'])
    L.append(''); L.append('status changes: ' + (', '.join(f'{x} -> {y}: {n}' for (x, y), n in sorted(moved.items())) or 'none'))
    lost = sorted(r for r in set(B) & set(A) if B[r]['status'] == 'DRAWN' and A[r]['status'] != 'DRAWN')
    L.append(''); L.append(f'WAS DRAWN, NOT NOW ({len(lost)}): look at these first')
    for r in lost: L.append(f'- {r}: {A[r]["status"]} - {A[r]["why"][:220]}')
    new = sorted(r for r in A if A[r]['status'] == 'DRAWN' and B.get(r, {}).get('status') != 'DRAWN')
    L.append(''); L.append(f'NEWLY DRAWN ({len(new)}): grade each (is the line the park? on the right roads / shore?)')
    L.append('| ref | points | fit m | loo m | line share | line z | decoy line z | score / decoy | acres traced / known | pin m | debug |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in new:
        x = A[r]
        L.append(f"| {r} | {x.get('n_points')} | {x.get('fit_m')} | {x.get('fit_loo_m')} | {x.get('line_share', '')} | {x.get('line_z', '')} | "
                 f"{x.get('decoy_line_z', '')} | {x.get('n_search', '')} / {x.get('decoy_best', '')} | {x.get('acres_traced', '')} / {x.get('acres_known', '')} | "
                 f"{x.get('pin_dist_m', '')} | debug/{r}_1_boundary.jpg, debug/{r}_2_controlpoints.jpg |")
    out = '\n'.join(L) + '\n'
    sys.stdout.write(out)
    if a.md: open(a.md, 'w', encoding='utf-8').write(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
