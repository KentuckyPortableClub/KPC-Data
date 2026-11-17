#!/usr/bin/env python3
"""EVIDENCE CARDS (KPC owner, 2026-11-17; Handoff 3 proofs 1 and 3, the card described in Handoff 2). One card per park on the
keeper's list, built ONLY from what is already stored (no request of any kind is made here):
  * POTA's record          KPC-Data data/parkinfo/<area>.json (name, website link, type, pin) - the stored copy, never api.pota
  * the official page      KPC-Data data/docs/<area>.json (page, agency, date read, map link + status)
  * the key's view         KPC-Links data/us-key|ca-key/why-not.json (tag + why) and data/status/key-check/dropped-*/latest/no-boundary.csv
  * extra evidence         optional CSV with card columns (the keeper's review rows when the manager session supplies a public-safe copy)
  * earlier decisions      person_no in the extra evidence (a person's NO stands)
Then kpc_card_rules.sort_card gives the sort and the one-line reason.

  python3 kpc_evidence_card.py cards --asks asks.json --data <KPC-Data> --links <KPC-Links> [--extra rows.csv] --out cards.json
  python3 kpc_evidence_card.py compare --answers review-answers.csv [--data .. --links ..] [--out compare.json]
  python3 kpc_evidence_card.py --selftest
review-answers.csv: ref, hand_sort (or sort), and optionally the card columns below (used when nothing is stored for the ref).
Card columns: name, checked, person_no, pin_typo, multistate_one_state, inside_bigger, nothing_at_pin, official_acres,
cand_name, cand_km, cand_acres, cand_easement, cand_held_by, cand_held_by_count, cand_kind, cand_name_unique."""
import csv, datetime as _dt, glob, json, os, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kpc_card_rules as R  # noqa: E402

ACRES_RX = re.compile(r'(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(acres?|ac\b|hectares?|ha\b|km²|km2|square kilomet(?:er|re)s?|sq\.? ?mi(?:les?)?|square miles?)', re.I)
TO_ACRES = {'acre': 1.0, 'ac': 1.0, 'hectare': 2.4710538, 'ha': 2.4710538, 'km': 247.10538, 'square kilomet': 247.10538, 'sq': 640.0, 'square mile': 640.0}


def read_acres(text):
    """(acres, the line it came from) from an official page's text, or (None, ''). The first figure wins; the line is kept."""
    for line in re.split(r'[\r\n]+', str(text or '')):
        m = ACRES_RX.search(line)
        if not m: continue
        v = float(m.group(1).replace(',', '')); u = m.group(2).lower()
        k = 'km' if u.startswith('km') else 'square kilomet' if u.startswith('square kilomet') else 'sq' if u.startswith('sq') else \
            'square mile' if u.startswith('square mile') else 'hectare' if u.startswith('hectare') else 'ha' if u == 'ha' else 'acre'
        return round(v * TO_ACRES[k], 2), line.strip()[:200]
    return None, ''


def _load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def _b(v):
    return str(v or '').strip().lower() in ('1', 'true', 'yes', 'y')


def _f(v):
    try: return float(str(v).replace(',', '')) if str(v or '').strip() != '' else None
    except ValueError: return None


class Stores:
    """Every stored source a card reads. Counts what it read; never fetches."""

    def __init__(self, data=None, links=None, extra=None, checked_default=''):
        self.data, self.links = pathlib.Path(data) if data else None, pathlib.Path(links) if links else None
        self.pinfo, self.docs, self.why, self.nb, self.extra = {}, {}, {}, {}, {}
        self.checked_default = checked_default
        self.reads = 0
        if self.data:
            for f in sorted(glob.glob(str(self.data / 'data/parkinfo/*.json'))):
                for r, a in ((_load(f, {}) or {}).get('parks') or {}).items(): self.pinfo[r] = a
        if self.links:
            for k in ('us', 'ca'):
                for r, v in ((_load(self.links / f'data/{k}-key/why-not.json', {}) or {}).get('parks') or {}).items(): self.why[r] = v
                p = self.links / f'data/status/key-check/dropped-{k}/latest/no-boundary.csv'
                if p.exists():
                    for row in csv.DictReader(open(p, encoding='utf-8')): self.nb[row['ref']] = row
        if extra and os.path.exists(extra):
            for row in csv.DictReader(open(extra, encoding='utf-8')): self.extra[row['ref']] = row

    def docs_for(self, area):
        if area not in self.docs:
            self.docs[area] = ((_load(self.data / f'data/docs/{area}.json', {}) or {}).get('parks') or {}) if self.data else {}
        return self.docs[area]


def area_of(ref, stores, hint=''):
    if hint: return hint
    w = stores.why.get(ref) or {}
    if w.get('st'): return f"{ref.split('-')[0]}-{w['st']}"
    nb = stores.nb.get(ref) or stores.extra.get(ref) or {}
    return nb.get('area') or ''


def build_card(ref, stores, area='', name='', since='', today=None):
    area = area_of(ref, stores, area)
    pi = stores.pinfo.get(ref) or []
    pota = {'name': (pi[0] if pi else '') or name, 'website': pi[1] if len(pi) > 1 else '', 'type': pi[2] if len(pi) > 2 else '',
            'pin': [pi[5], pi[6]] if len(pi) > 6 else None}
    d = stores.docs_for(area).get(ref) or {}
    page = {'url': d.get('page') or '', 'agency': d.get('agency') or '', 'checked': d.get('checked') or '',
            'map_url': (d.get('map') or {}).get('url') or '', 'map_status': (d.get('map') or {}).get('status') or ''}
    w = stores.why.get(ref) or {}
    nb = stores.nb.get(ref) or {}
    x = stores.extra.get(ref) or {}
    sources = [s for s, v in (('data/parkinfo', pi), ('data/docs', d), ('why-not.json', w), ('no-boundary.csv', nb), ('extra evidence', x)) if v]
    stores.reads += len(sources)
    card = {'ref': ref, 'area': area, 'name': x.get('name') or pota['name'] or name or ref, 'pota': pota, 'official_page': page,
            'store': {'why_not_tag': w.get('tag') or '', 'why': w.get('why') or nb.get('detail') or ''},
            'checked': x.get('checked') or (nb.get('checked') or '')[:10] or since or stores.checked_default,
            'person_no': x.get('person_no') or (nb.get('person_answer') if str(nb.get('person_answer') or '').upper().startswith('NO') else ''),
            'pin_typo': _b(x.get('pin_typo')), 'multistate_one_state': _b(x.get('multistate_one_state')),
            'inside_bigger': x.get('inside_bigger') or '', 'nothing_at_pin': _b(x.get('nothing_at_pin')),
            'official_acres': _f(x.get('official_acres')), 'acres_line': x.get('acres_line') or '',
            'candidate': None, 'unsure': [], 'sources': sources, 'fetched': 0}
    if x.get('cand_name'):
        card['candidate'] = {'name': x['cand_name'], 'km': _f(x.get('cand_km')), 'acres': _f(x.get('cand_acres')),
                             'easement': _b(x.get('cand_easement')), 'held_by': x.get('cand_held_by') or '',
                             'held_by_count': int(_f(x.get('cand_held_by_count')) or 0), 'kind': x.get('cand_kind') or '',
                             'name_unique': not (str(x.get('cand_name_unique') or '').lower() in ('0', 'false', 'no'))}
    elif nb.get('cand_name'):
        card['candidate'] = {'name': nb['cand_name'], 'km': _f(nb.get('cand_distance_km')), 'acres': _f(nb.get('cand_acres')),
                             'easement': False, 'held_by': '', 'held_by_count': 0, 'kind': nb.get('cand_kind') or ''}
    tag, why = card['store']['why_not_tag'], card['store']['why']
    if not x:   # the key's own words, when no richer evidence row exists
        m = re.search(r'pin is inside a bigger area:\s*(.+)$', why)
        if m: card['inside_bigger'] = m.group(1).strip()
        elif tag in ('no-layer', 'private', 'picture-map-only') or (nb.get('reason') == 'no_boundary' and not nb.get('cand_name')):
            card['nothing_at_pin'] = True
        if tag == 'name-mismatch': card['unsure'].append(f'the key holds a near-name record for a person: {why or "name mismatch"}')
        if tag == 'pin-doubt': card['unsure'].append('the key doubts the pin')
        if tag == 'needs-parcel' and not card['inside_bigger']: card['unsure'].append('the key says only a parcel trace can outline it')
    s, reason, rule = R.sort_card(card, today)
    card.update(sort=s, reason=reason, rule=rule)
    return card


def compare(answers_csv, stores, today=None):
    """Rules against the hand answers: every disagreement listed with both sides and the rules' reason."""
    rows = list(csv.DictReader(open(answers_csv, encoding='utf-8')))
    out, agree = [], 0
    for row in rows:
        ref = row['ref']; hand = (row.get('hand_sort') or row.get('sort') or '').strip().upper()
        if ref not in stores.extra: stores.extra[ref] = row
        c = build_card(ref, stores, row.get('area') or '', row.get('name') or '', today=today)
        same = c['sort'] == hand
        agree += same
        if not same:
            out.append({'ref': ref, 'hand': hand, 'rules': c['sort'], 'rules_reason': c['reason'], 'hand_note': row.get('hand_note') or row.get('note') or ''})
    return {'rows': len(rows), 'agree': agree, 'disagree': len(out), 'share_agree': round(agree / len(rows), 3) if rows else None,
            'disagreements': out}


def _selftest():
    import tempfile
    ok = True
    def chk(c, w):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + w)
    chk(read_acres('Size\nThe park covers 73 acres of forest.')[0] == 73.0, 'acres reader: "73 acres" and its line')
    a, ln = read_acres('Area: 29.5 ha'); chk(abs(a - 72.9) < 0.1 and ln == 'Area: 29.5 ha', 'acres reader: hectares -> acres, line kept')
    chk(abs(read_acres('1.2 km² of wetland')[0] - 296.5) < 0.1, 'acres reader: km²')
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / 'ans.csv'
        p.write_text('ref,hand_sort,name,checked,nothing_at_pin,cand_name,cand_km,cand_acres,official_acres\n'
                     'US-1,NO ACTION,A Park,2026-11-10,yes,,,,\nUS-2,PROPOSE JOIN,B Park,2026-11-10,,B Park,0,100,105\n'
                     'US-3,PROPOSE JOIN,C Park,2026-11-10,,C Park,30,100,100\n', encoding='utf-8')
        r = compare(str(p), Stores(), _dt.date(2026, 11, 17))
        chk(r['rows'] == 3 and r['agree'] == 2 and r['disagreements'][0]['ref'] == 'US-3', 'compare lists the one disagreement with why')
    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['cards', 'compare'])
    ap.add_argument('--asks'); ap.add_argument('--answers'); ap.add_argument('--data'); ap.add_argument('--links'); ap.add_argument('--extra')
    ap.add_argument('--areas', default=''); ap.add_argument('--out')
    a = ap.parse_args(argv)
    st = Stores(a.data, a.links, a.extra)
    if a.cmd == 'compare':
        res = compare(a.answers, st)
    else:
        asks = _load(a.asks, {}) or {}
        want = {x for x in a.areas.split(',') if x}
        res = [build_card(p['ref'], st, p.get('area') or '', p.get('name') or '', p.get('since') or '') for p in asks.get('parks') or []
               if not want or p.get('area') in want]
    txt = json.dumps(res, indent=1, ensure_ascii=False) + '\n'
    if a.out: open(a.out, 'w', encoding='utf-8', newline='\n').write(txt)
    else: sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]: sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
