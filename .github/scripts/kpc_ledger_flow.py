#!/usr/bin/env python3
"""LEDGER-FIRST FLOW (Nov 6 2026 improvements 2, Mapping; Brandon directly in Mapping's chat, 4:58 PM CST Nov 5: "You write the
code and I think super and quality would agree to it"). Built on the agreement ledger (kpc_agreement_ledger.py, Brandon's
two-agreements rule 4:07 / 4:17 PM CST Nov 5). It only WRITES PROPOSALS and REPORTS: it never confirms, never decides, never
touches state.json (auto stays false; Brandon flips auto by hand) and never deletes a row.

  propose <park> <kind> <by> <proposal> [source] [notes]   any bot writes one proposal row (a duplicate open row is skipped)
  import <file.csv> [by]       proposal rows another bot wrote in the ledger's columns (e.g. KPC-Links key health's
                               ledger-proposals.csv). confirmed_by / confirmed_at / decided_by in the file are IGNORED: a file can
                               never carry the second agreement.
  disagree <park> <kind> <by> <reason>   a second bot says NO to an open proposal: one row 'DISAGREE: <reason>' (never a confirm)
  sample [out.csv] [n_control] [seed]    the Quality sheet: EVERY open proposal where bots disagree + a random control sample
                               of the uncontested ones (default 10, rule 18: at least 10), with empty quality_verdict columns
  trend [samples_dir] [trend.csv]        agreement % per graded sample sheet (AGREE / (AGREE + DISAGREE)), appended once per sheet
  --selftest                   10+ frozen cases in a temp folder (never the repo's data/agreement-ledger/)

Files (defaults): data/agreement-ledger/ledger.csv (the ledger), data/agreement-ledger/samples/quality-sample-<date>.csv,
data/agreement-ledger/trend.csv. Offline; no secrets."""
import csv, datetime, hashlib, os, pathlib, random, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_agreement_ledger as AL  # noqa: E402

SAMPLES = pathlib.Path('data/agreement-ledger/samples')
TREND = pathlib.Path('data/agreement-ledger/trend.csv')
SAMPLE_FIELDS = ['sample', 'why_in_sample', 'park', 'kind', 'proposed_by', 'proposal', 'source', 'other_views',
                 'quality_verdict', 'quality_note', 'graded_by']
TREND_FIELDS = ['sheet', 'made', 'graded', 'agree', 'disagree', 'cant_tell', 'agreement_pct', 'disagreement_rows', 'control_rows', 'auto']
NEVER_FROM_FILE = ('confirmed_by', 'confirmed_at', 'decided_by', 'agreed_lat', 'agreed_lon')


def _open(rows, park, kind):
    return [r for r in rows if r.get('park') == park and r.get('kind') == kind and not r.get('confirmed_by')]


def propose_row(park, kind, by, proposal, source='', notes='', pota_lat='', pota_lon='', rows=None, save=True):
    """('added'|'already proposed', rows). Validates through AL.propose (kind, required fields)."""
    rows = list(rows if rows is not None else AL.load_rows())
    for r in _open(rows, park, kind):
        if (r.get('proposed_by') or '').casefold() == (by or '').casefold() and r.get('proposal') == proposal:
            return 'already proposed', rows
    rows = AL.propose(park, kind, by, proposal, source=source, pota_lat=pota_lat, pota_lon=pota_lon, notes=notes, rows=rows)
    if save: AL.save_rows(rows)
    return 'added', rows


def import_file(path, by=None, rows=None, save=True):
    """Append the proposal rows of a CSV in the ledger's columns. Returns {'added', 'skipped', 'bad'}."""
    rows = list(rows if rows is not None else AL.load_rows())
    n = {'added': 0, 'skipped': 0, 'bad': 0}
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            for k in NEVER_FROM_FILE: r.pop(k, None)
            try:
                got, rows = propose_row(r.get('park', ''), r.get('kind', ''), by or r.get('proposed_by', ''), r.get('proposal', ''),
                                        source=r.get('source', ''), notes=r.get('notes', ''), pota_lat=r.get('pota_lat', ''),
                                        pota_lon=r.get('pota_lon', ''), rows=rows, save=False)
                n['added' if got == 'added' else 'skipped'] += 1
            except ValueError: n['bad'] += 1
    if save: AL.save_rows(rows)
    return n


def disagree(park, kind, by, reason, rows=None, save=True):
    """A second bot's NO on an open proposal of another bot. Writes a 'DISAGREE:' proposal row; never confirms anything."""
    rows = list(rows if rows is not None else AL.load_rows())
    others = [r for r in _open(rows, park, kind) if (r.get('proposed_by') or '').casefold() != (by or '').casefold()
              and not str(r.get('proposal', '')).startswith('DISAGREE:')]
    if not others: raise ValueError(f'no open {kind} proposal by another agent for {park}')
    return propose_row(park, kind, by, 'DISAGREE: ' + reason, source='disagree', rows=rows, save=save)


def groups(rows):
    """{(park, kind): [open rows]}."""
    g = {}
    for r in rows:
        if r.get('confirmed_by'): continue
        g.setdefault((r.get('park'), r.get('kind')), []).append(r)
    return g


def contested(rs):
    """True when the open rows of one park + kind disagree: an explicit DISAGREE row, or two agents proposing different things."""
    if any(str(r.get('proposal', '')).startswith('DISAGREE:') for r in rs): return True
    by_prop = {}
    for r in rs: by_prop.setdefault(r.get('proposal'), set()).add((r.get('proposed_by') or '').casefold())
    agents = set().union(*by_prop.values()) if by_prop else set()
    return len(by_prop) > 1 and len(agents) > 1


def sample(rows=None, n_control=10, seed=None, today=None):
    """[sample rows]: every contested proposal (why 'disagreement') + a seeded random control sample of uncontested ones."""
    rows = rows if rows is not None else AL.load_rows()
    today = today or datetime.date.today().isoformat()
    seed = seed if seed is not None else int(hashlib.md5(today.encode()).hexdigest()[:8], 16)
    out, calm = [], []
    for (park, kind), rs in sorted(groups(rows).items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        if contested(rs):
            views = ' | '.join(f"{r.get('proposed_by')}: {r.get('proposal')}" for r in rs)
            for r in rs:
                if str(r.get('proposal', '')).startswith('DISAGREE:'): continue
                out.append({'why_in_sample': 'disagreement', 'park': park, 'kind': kind, 'proposed_by': r.get('proposed_by'),
                            'proposal': r.get('proposal'), 'source': r.get('source'), 'other_views': views})
        else: calm.extend(rs)
    pick = random.Random(seed).sample(calm, min(n_control, len(calm)))
    out += [{'why_in_sample': f'control (random, seed {seed})', 'park': r.get('park'), 'kind': r.get('kind'), 'proposed_by': r.get('proposed_by'),
             'proposal': r.get('proposal'), 'source': r.get('source'), 'other_views': ''} for r in pick]
    for r in out: r.update({'sample': f'quality-sample-{today}', 'quality_verdict': '', 'quality_note': '', 'graded_by': ''})
    return out


def write_sample(out_rows, path):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=SAMPLE_FIELDS); w.writeheader()
        for r in out_rows: w.writerow({k: r.get(k, '') for k in SAMPLE_FIELDS})
    return path


def grade_of(v):
    v = str(v or '').strip().upper()
    if re.match(r'AGREE\b|YES\b', v): return 'agree'
    if re.match(r'DISAGREE\b|NO\b', v): return 'disagree'
    if v: return 'cant_tell'
    return ''


def trend(samples_dir=None, trend_csv=None, state=None):
    """Append one trend row per sample sheet not yet in the trend file. Returns the new rows. auto is read, never written."""
    samples_dir = pathlib.Path(samples_dir or SAMPLES); trend_csv = pathlib.Path(trend_csv or TREND)
    seen = set()
    if trend_csv.exists():
        with open(trend_csv, newline='', encoding='utf-8') as f: seen = {r['sheet'] for r in csv.DictReader(f)}
    auto = (state if state is not None else AL.load_state()).get('auto', False)
    new = []
    for sh in sorted(samples_dir.glob('quality-sample-*.csv')):
        if sh.name in seen: continue
        with open(sh, newline='', encoding='utf-8') as f: rs = list(csv.DictReader(f))
        g = [grade_of(r.get('quality_verdict')) for r in rs]
        if not any(g): continue        # not graded yet: counted when Quality fills it
        a, d, c = g.count('agree'), g.count('disagree'), g.count('cant_tell')
        new.append({'sheet': sh.name, 'made': sh.name[len('quality-sample-'):-4], 'graded': a + d + c, 'agree': a, 'disagree': d, 'cant_tell': c,
                    'agreement_pct': f'{100 * a / (a + d):.1f}' if a + d else '',
                    'disagreement_rows': sum(1 for r in rs if r.get('why_in_sample') == 'disagreement'),
                    'control_rows': sum(1 for r in rs if str(r.get('why_in_sample', '')).startswith('control')), 'auto': str(bool(auto)).lower()})
    if new:
        trend_csv.parent.mkdir(parents=True, exist_ok=True); head = not trend_csv.exists()
        with open(trend_csv, 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=TREND_FIELDS)
            if head: w.writeheader()
            for r in new: w.writerow(r)
    return new


def selftest():
    import tempfile
    ok, n = True, 0
    def check(name, got, want):
        nonlocal ok, n
        n += 1; good = got == want; ok &= good
        print(('PASS ' if good else 'FAIL ') + name + ('' if good else f'  got={got!r} want={want!r}'))
    td = pathlib.Path(tempfile.mkdtemp(prefix='kpc-ledger-flow-'))
    AL.LEDGER, AL.STATE = td / 'ledger.csv', td / 'state.json'      # never the repo's data/agreement-ledger/
    AL.save_rows([]); AL.save_state({'auto': False})
    st0 = AL.STATE.read_bytes()
    got, rows = propose_row('US-0001', 'pile-enter', 'key-health', 'outline lost (was 3 records)', source='key-health us')
    check('a bot writes a proposal row', (got, len(AL.load_rows())), ('added', 1))
    got, rows = propose_row('US-0001', 'pile-enter', 'key-health', 'outline lost (was 3 records)')
    check('the same open proposal twice is skipped', (got, len(AL.load_rows())), ('already proposed', 1))
    r0 = AL.load_rows()[0]
    check('a proposal has no confirmation and no decision', (r0['confirmed_by'], r0['decided_by']), ('', ''))
    try: propose_row('US-0002', 'delete-park', 'bot', 'x'); bad = False
    except ValueError: bad = True
    check('an unknown kind is refused', bad, True)
    f = td / 'in.csv'
    with open(f, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=AL.FIELDS); w.writeheader()
        w.writerow({'park': 'US-0003', 'kind': 'pile-enter', 'proposed_by': 'key-health', 'proposal': 'join 22 km from the pin',
                    'confirmed_by': 'quality', 'decided_by': AL.DECIDED_BY})
        w.writerow({'park': '', 'kind': 'pile-enter', 'proposed_by': 'key-health', 'proposal': 'no park'})
    n_imp = import_file(f)
    rows = AL.load_rows(); r3 = [r for r in rows if r['park'] == 'US-0003'][0]
    check('import adds the good row and counts the bad one', n_imp, {'added': 1, 'skipped': 0, 'bad': 1})
    check('an imported row can NOT carry a confirmation (two-agreements)', (r3['confirmed_by'], r3['decided_by'], AL.ready('pile-enter')), ('', '', []))
    try: disagree('US-0001', 'pile-enter', 'key-health', 'mine'); same = False
    except ValueError: same = True
    check('an agent cannot disagree with only its own proposal', same, True)
    disagree('US-0001', 'pile-enter', 'pile-solver', 'outline is the same land, only re-cut')
    check('a disagreement is a row, never a confirmation', ([r['confirmed_by'] for r in AL.load_rows()], AL.ready()), (['', '', ''], []))
    propose_row('US-0004', 'join', 'pile-solver', "join a1 'Rock Creek'")
    propose_row('US-0004', 'join', 'detective', "join b2 'Rock Creek WMA'")
    propose_row('US-0005', 'join', 'pile-solver', "join c3 'Same'"); propose_row('US-0005', 'join', 'detective', "join c3 'Same'")
    for i in range(10, 25): propose_row(f'US-00{i}', 'pile-enter', 'key-health', f'flag {i}')
    sm = sample(today='2026-11-06')
    dis = sorted({r['park'] for r in sm if r['why_in_sample'] == 'disagreement'})
    check('disagreements: the DISAGREE row and the two different proposals (not two agents proposing the same)', dis, ['US-0001', 'US-0004'])
    ctl = [r for r in sm if r['why_in_sample'].startswith('control')]
    check('control sample = 10 (rule 18: at least 10) from the uncontested rows', (len(ctl), all(r['park'] not in dis for r in ctl)), (10, True))
    check('the same day gives the same control sample (seeded)', [r['park'] for r in ctl], [r['park'] for r in sample(today='2026-11-06') if r['why_in_sample'].startswith('control')])
    sp = write_sample(sm, td / 'samples' / 'quality-sample-2026-11-06.csv')
    check('no trend row for a sheet Quality has not graded', trend(td / 'samples', td / 'trend.csv'), [])
    rs = list(csv.DictReader(open(sp)))
    for i, r in enumerate(rs): r['quality_verdict'] = ['AGREE', 'AGREE', 'AGREE', 'DISAGREE', "CAN'T TELL"][i % 5]
    with open(sp, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=SAMPLE_FIELDS); w.writeheader(); w.writerows(rs)
    t = trend(td / 'samples', td / 'trend.csv')
    a = sum(1 for i in range(len(rs)) if i % 5 < 3); d = sum(1 for i in range(len(rs)) if i % 5 == 3)
    check('trend: agreement % = AGREE / (AGREE + DISAGREE), auto false', (t[0]['agreement_pct'], t[0]['auto']), (f'{100 * a / (a + d):.1f}', 'false'))
    check('trend: a sheet is counted once', trend(td / 'samples', td / 'trend.csv'), [])
    check('state.json untouched: auto stays false', (AL.STATE.read_bytes() == st0, AL.load_state()['auto']), (True, False))
    check('nothing would leave the pile', AL.exit_candidates()['would_exit'], [])
    print(f"SELFTEST {'PASS' if ok else 'FAIL'}: {n} cases")
    return ok


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ('-h', '--help'): print(__doc__); return 0
    if a[0] == '--selftest': return 0 if selftest() else 1
    if a[0] == 'propose':
        got, _ = propose_row(a[1], a[2], a[3], a[4], source=a[5] if len(a) > 5 else '', notes=a[6] if len(a) > 6 else ''); print(got, a[1], a[2]); return 0
    if a[0] == 'import': print(import_file(a[1], by=a[2] if len(a) > 2 else None)); return 0
    if a[0] == 'disagree': got, _ = disagree(a[1], a[2], a[3], a[4]); print(got, a[1], a[2]); return 0
    if a[0] == 'sample':
        today = datetime.date.today().isoformat()
        rs = sample(n_control=int(a[2]) if len(a) > 2 else 10, seed=int(a[3]) if len(a) > 3 else None)
        p = write_sample(rs, a[1] if len(a) > 1 else SAMPLES / f'quality-sample-{today}.csv')
        print(f"{p}: {sum(r['why_in_sample'] == 'disagreement' for r in rs)} disagreement rows + {sum(r['why_in_sample'].startswith('control') for r in rs)} control rows"); return 0
    if a[0] == 'trend':
        new = trend(a[1] if len(a) > 1 else None, a[2] if len(a) > 2 else None); print(f'{len(new)} new trend row(s)'); return 0
    print(__doc__, file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
