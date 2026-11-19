#!/usr/bin/env python3
"""The shared not-sure list (hand-off 05, addendum 1).

One row is one park and one doubt. Standard library only. No network.
The list lives on tools-out under not-sure/. This module only writes the folder it is given.
The page reader may add rows and tried notes. It may not settle a row.
"""
import argparse, json, os, pathlib, re, sys

HOW_SURE = ('wrong likely', 'unsure', 'incomplete', 'unchecked', 'fairly sure')
STATUS = ('open', 'parked', 'settled', 'gone')
# Longest first so "official size" is seen before a shorter word.
WANTS = (
    'page facts', 'official size', 'official layer', 'far-join evidence',
    'random sample', 'a person', 'the owner', 'map',
)
BOT_WANTS = {'page facts', 'official size', 'map', 'official layer', 'far-join evidence', 'random sample'}
PERSON_WANTS = {'a person', 'the owner'}

# Codes already on the club's seed, plus the reader's question codes. A new code is refused
# until it has a line here, which is also written into not-sure/README.md.
CODES = {
    'APPROX_UNVERIFIED': 'the outline was a saved guess, so the park stays a pin until someone confirms it',
    'WRONG_NO': 'a pass said no, and the doubt is still open',
    'CONTEST': 'two readings disagree',
    'PART_RECORD': 'the record looks like a part of the park, not the whole park',
    'LAKE_SURFACE_ONLY': 'only the water matched, and the shore is still a doubt',
    'CANNOT_TELL': 'the passes could not tell',
    'ONLY_A_COPY': 'the only record is a copy of another park',
    'CROSS_STATE_PIECE': 'the park crosses a state line',
    'HERITAGE_AREA': 'a heritage area is a region, not one piece of public land',
    'PIN_BUT_RECORD_KNOWN': 'a record is known and the grade is still a pin',
    'UNCHECKED_NEW_LAND': 'new land has not been checked',
    'SIZE_UNCHECKED': 'a size has not been checked',
    'PLACED_FROM_PICTURE': 'the outline was placed from a picture',
    'NAME_VS_LINK': 'the name and the link do not say the same place',
    'FIXED_WATCH': 'a fix is in, and the park is being watched',
    'FAR_FROM_PIN': 'the land sits far from the pin',
    'RECORD_NOT_SIGNED': 'a record has not been signed off',
    'ONE_WITNESS': 'only one witness',
    'PIN_OUTSIDE_LAND': 'pins sit outside the land, and nobody has sorted them',
    'NOT_SAMPLED': 'these outlines were not in the sample',
    'UNREVIEWED_RELEASE': 'a release has not been reviewed',
    'OUTLINE_SOURCE_UNCLEAR': 'the source of the outline is not clear',
    'COMBINED_UNIT': 'the page name joins two kinds and POTA numbers no separate park for the other part',
    'COMBINED_BOTH_NUMBERED': 'the page covers two kinds and POTA numbers both',
    'INSIDE_BIGGER_UNIT': 'the page says this place is inside a bigger named unit',
    'DESIGNATION_DIFFERS': 'the page kind and POTA\'s type share no word',
    'NAME_DIFFERS': 'the page name and POTA\'s name differ beyond the kind words',
    'SHARED_PAGE': 'several parks use one page',
    'AGENCY_HOME_ONLY': 'the link is the agency\'s front page',
    'UNOFFICIAL_HOST': 'the link is not an agency page',
    'OFFICE_ADDRESS_ONLY': 'the only address is an office',
    'PIN_FAR_FROM_PAGE': 'the page\'s map point is far from POTA\'s pin',
    'SIZE_LISTED_BY_PART': 'the page gives sizes by part',
    'MANY_TRACTS': 'the page names more than one tract',
    'LINK_MOVED': 'the link now lands on another host',
    'LINK_DEAD': 'the link does not open',
    'REFUSED': 'the site does not take automated visitors',
    'SCRIPT_BUILT': 'the page builds itself in the browser',
    'NO_PAGE': 'no page is on file',
    'CLOSED_OR_MOVED_WORDS': 'the page says the park closed, moved, or was renamed',
}
QUESTION_CODES = {
    'COMBINED_UNIT', 'COMBINED_BOTH_NUMBERED', 'INSIDE_BIGGER_UNIT', 'DESIGNATION_DIFFERS',
    'NAME_DIFFERS', 'SHARED_PAGE', 'AGENCY_HOME_ONLY', 'UNOFFICIAL_HOST', 'OFFICE_ADDRESS_ONLY',
    'PIN_FAR_FROM_PAGE', 'SIZE_LISTED_BY_PART', 'MANY_TRACTS', 'LINK_MOVED', 'LINK_DEAD',
    'REFUSED', 'SCRIPT_BUILT', 'NO_PAGE', 'CLOSED_OR_MOVED_WORDS',
}
READER = 'park page reader'


def _blank():
    return {'source': '', 'saw': '', 'date': ''}


def _settled_blank():
    return {'by': '', 'date': '', 'how': '', 'link': ''}


def known_wants(text):
    """Pull the fixed wants out of a sentence. Unknown phrases are left out, not stored as wants."""
    if isinstance(text, list):
        return [w for w in text if w in WANTS]
    blob = str(text or '').lower()
    found = []
    for phrase in WANTS:
        if phrase == 'map':
            if re.search(r'\bmap\b', blob):
                found.append('map')
        elif phrase in blob:
            found.append(phrase)
    if 'location facts' in blob and 'page facts' not in found:
        found.insert(0, 'page facts')
    if 'far join' in blob and 'far-join evidence' not in found:
        found.append('far-join evidence')
    return found


def _row_key(row):
    return (str(row.get('ref') or ''), str(row.get('code') or ''))


class NotSure:
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, area):
        safe = re.sub(r'[^A-Za-z0-9_-]', '', str(area or 'US')) or 'US'
        return self.root / f'{safe}.json'

    def _load_area(self, area):
        path = self._path(area)
        if not path.is_file():
            return []
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return []
        return list(doc.get('rows') or [])

    def _write_area(self, area, rows):
        rows = sorted(rows, key=_row_key)
        doc = {'area': area, 'rows': rows}
        text = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + '\n'
        path = self._path(area)
        path.write_text(text, encoding='utf-8')
        return path

    def areas(self):
        return sorted(p.stem for p in self.root.glob('*.json') if p.name != 'last-summary.json')

    def all_rows(self):
        rows = []
        for area in self.areas():
            rows.extend(self._load_area(area))
        return rows

    def add(self, row, today=''):
        """Same park and code again moves last_seen and does not make a second row. Returns the row, or None if refused."""
        code = str((row or {}).get('code') or '')
        ref = str((row or {}).get('ref') or '')
        area = str((row or {}).get('area') or '')
        if code not in CODES or not ref or not area:
            return None
        how = str(row.get('how_sure') or 'unsure')
        if how not in HOW_SURE:
            return None
        status = str(row.get('status') or 'open')
        if status not in STATUS:
            return None
        raw_wants = row.get('wants') if row.get('wants') is not None else []
        if isinstance(raw_wants, list):
            if any(w not in WANTS for w in raw_wants):
                return None
            wants = list(raw_wants)
        else:
            # a sentence: keep only the fixed phrases. An unknown phrase alone is a refusal
            # when the sentence has words and none of them are a fixed phrase.
            wants = known_wants(raw_wants)
            if str(raw_wants).strip() and not wants:
                return None
        day = str(today or row.get('date') or row.get('last_seen') or '')
        rows = self._load_area(area)
        cur = next((r for r in rows if r.get('ref') == ref and r.get('code') == code), None)
        if cur:
            cur['last_seen'] = day or cur.get('last_seen') or ''
            if row.get('why'):
                cur['why'] = str(row.get('why'))[:500]
            if row.get('evidence'):
                cur['evidence'] = {
                    'source': str((row.get('evidence') or {}).get('source') or ''),
                    'saw': str((row.get('evidence') or {}).get('saw') or '')[:200],
                    'date': str((row.get('evidence') or {}).get('date') or day),
                }
            if wants:
                cur['wants'] = wants
            self._write_area(area, rows)
            return cur
        made = {
            'ref': ref, 'area': area, 'name': str(row.get('name') or '')[:200], 'code': code,
            'how_sure': how, 'shows_now': str(row.get('shows_now') or '')[:80],
            'why': str(row.get('why') or '')[:500], 'wants': wants,
            'found_by': str(row.get('found_by') or '')[:120],
            'first_seen': day, 'last_seen': day,
            'evidence': {
                'source': str((row.get('evidence') or {}).get('source') or ''),
                'saw': str((row.get('evidence') or {}).get('saw') or '')[:200],
                'date': str((row.get('evidence') or {}).get('date') or day),
            },
            'tried': [],
            'status': status,
            'settled': _settled_blank(),
        }
        rows.append(made)
        self._write_area(area, rows)
        return made

    def import_seed(self, path, today=''):
        """Split a flat seed into one file per area. Every input row is kept. Returns the count."""
        raw = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
        n = 0
        for row in raw:
            if not isinstance(row, dict) or row.get('code') not in CODES:
                continue
            day = str(row.get('date') or today or '')
            wants = known_wants(row.get('wants'))
            made = self.add({
                'ref': row.get('ref'), 'area': row.get('area'), 'name': row.get('name'),
                'code': row.get('code'), 'how_sure': row.get('how_sure') or 'unsure',
                'shows_now': row.get('shows_now') or '', 'why': row.get('why') or '',
                'wants': wants, 'found_by': row.get('found_by') or '',
                'status': row.get('status') or 'open', 'date': day,
            }, today=day)
            if made:
                n += 1
        self.write_readme()
        return n

    def tried(self, ref, code, by, result, quote='', today=''):
        """Append a note. Older notes stay."""
        found = self._find(ref, code)
        if not found:
            return None
        area, rows, row = found
        row.setdefault('tried', []).append({
            'by': str(by or '')[:120], 'date': str(today or '')[:20],
            'result': str(result or '')[:80], 'quote': str(quote or '')[:200],
        })
        if today:
            row['last_seen'] = today
        self._write_area(area, rows)
        return row

    def settle(self, ref, code, by, how, link='', today=''):
        """Close a row with who and how. The story stays. The page reader does not call this."""
        found = self._find(ref, code)
        if not found:
            return None
        area, rows, row = found
        row['status'] = 'settled'
        row['settled'] = {'by': str(by or '')[:120], 'date': str(today or '')[:20],
                          'how': str(how or '')[:300], 'link': str(link or '')[:300]}
        if today:
            row['last_seen'] = today
        self._write_area(area, rows)
        return row

    def mark_gone(self, ref, code, by, today=''):
        """The doubt no longer shows up. Not a settlement. The story stays."""
        found = self._find(ref, code)
        if not found:
            return None
        area, rows, row = found
        if row.get('status') == 'settled':
            return row
        row['status'] = 'gone'
        row.setdefault('tried', []).append({
            'by': str(by or '')[:120], 'date': str(today or '')[:20],
            'result': 'gone', 'quote': 'the question no longer comes up',
        })
        if today:
            row['last_seen'] = today
        self._write_area(area, rows)
        return row

    def _find(self, ref, code):
        for area in self.areas():
            rows = self._load_area(area)
            for row in rows:
                if row.get('ref') == ref and row.get('code') == code:
                    return area, rows, row
        return None

    def open_rows(self, area=None, wants=None, include_class=False):
        """Open rows a bot may work. A class row (ref '(class)') is left out unless include_class is set."""
        want = set(wants or [])
        rows = []
        areas = [area] if area else self.areas()
        for name in areas:
            for row in self._load_area(name):
                if row.get('status') != 'open':
                    continue
                if not include_class and str(row.get('ref')) == '(class)':
                    continue
                if want and not (set(row.get('wants') or []) & want):
                    continue
                rows.append(row)
        return rows

    def summary(self, today='', qsos=None):
        """One phone screen. Writes summary.md and returns the lines."""
        qsos = qsos or {}
        rows = self.all_rows()
        open_rows = [r for r in rows if r.get('status') == 'open' and str(r.get('ref')) != '(class)']
        by_how = {}
        for r in open_rows:
            by_how[r.get('how_sure') or 'unsure'] = by_how.get(r.get('how_sure') or 'unsure', 0) + 1
        prev_path = self.root / 'last-summary.json'
        try:
            prev = json.loads(prev_path.read_text(encoding='utf-8')) if prev_path.is_file() else {}
        except (OSError, json.JSONDecodeError):
            prev = {}
        already = set(prev.get('closed') or [])
        closed_now = []
        if prev_path.is_file():
            for r in rows:
                if r.get('status') in ('settled', 'gone'):
                    key = f"{r.get('ref')}|{r.get('code')}"
                    if key not in already:
                        closed_now.append(r)
        who = {}
        for r in closed_now:
            name = (r.get('settled') or {}).get('by') or ''
            if not name:
                notes = [t for t in (r.get('tried') or []) if t.get('result') == 'gone']
                name = notes[-1].get('by') if notes else ''
            name = name or 'not named'
            who[name] = who.get(name, 0) + 1
        no_bot = [r for r in open_rows if set(r.get('wants') or []) and not (set(r.get('wants') or []) & BOT_WANTS)]
        no_bot += [r for r in open_rows if not (r.get('wants') or [])]
        wrong = [r for r in open_rows if r.get('how_sure') == 'wrong likely']
        wrong.sort(key=lambda r: (-(qsos.get(r.get('ref')) or 0), r.get('ref') or ''))
        lines = [f'Not sure list, {today or "undated"}.',
                 'Open rows: ' + ', '.join(f'{h} {by_how.get(h, 0)}' for h in HOW_SURE) + '.',
                 f'Closed since last time: {len(closed_now)}' + ('' if not who else ' (' + ', '.join(f'{k} {v}' for k, v in sorted(who.items())) + ')') + '.',
                 f'No bot can help: {len(no_bot)}. Those wait on a person or the owner.',
                 'Wrong likely, busiest first:']
        if not wrong:
            lines.append('None.')
        for r in wrong[:15]:
            lines.append(f"{r.get('ref')} {r.get('name')}. {r.get('why')}")
        lines = lines[:40]
        (self.root / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        closed_keys = sorted(already | {f"{r.get('ref')}|{r.get('code')}" for r in rows if r.get('status') in ('settled', 'gone')})
        prev_path.write_text(json.dumps({'date': today, 'closed': closed_keys}, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        self.write_readme()
        return lines

    def write_readme(self):
        lines = ['# Not sure list', '',
                 'One row is one park and one doubt. A bot adds a row when it is not sure.',
                 'A row closes only when evidence settles it, with who and how.',
                 'Nothing is deleted. The page reader may add notes. It does not settle a row.',
                 'A row whose ref is (class) is about a whole group. No bot works it.',
                 '', '## Codes', '']
        for code in sorted(CODES):
            lines.append(f'- {code}: {CODES[code]}')
        lines.append('')
        (self.root / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


def note_from_reader(ns, facts, today):
    """After a read: tried notes on open rows, a row per question, and gone when that question is gone.
    The reader never settles."""
    if ns is None:
        return
    for area, parks in facts.items():
        for ref, fact in parks.items():
            if fact.get('unchanged'):
                continue
            kind = (fact.get('page') or {}).get('kind') or ''
            questions = fact.get('questions') or []
            quote = ''
            for q in questions:
                if q.get('quote'):
                    quote = q['quote']
                    break
            if kind in ('refused', 'robots'):
                result = 'refused'
            elif kind == 'script-built':
                result = 'script-built'
            elif not questions and not quote:
                result = 'page silent'
            else:
                result = quote or 'page silent'
            for row in ns.open_rows(area=area):
                if row.get('ref') != ref:
                    continue
                ns.tried(ref, row.get('code'), READER, result if result in ('refused', 'script-built', 'page silent') else 'read',
                         quote or result, today=today)
            asked = set()
            pota = fact.get('pota') or {}
            source = (fact.get('page') or {}).get('final_url') or (fact.get('asked') or {}).get('url') or ''
            for q in questions:
                code = q.get('code')
                if code not in QUESTION_CODES:
                    continue
                asked.add(code)
                wants = ['page facts']
                if code == 'SIZE_LISTED_BY_PART':
                    wants = ['official size', 'page facts']
                elif code == 'MANY_TRACTS':
                    wants = ['map', 'page facts']
                elif code in ('REFUSED', 'SCRIPT_BUILT', 'NO_PAGE', 'LINK_DEAD', 'AGENCY_HOME_ONLY'):
                    wants = ['a person']
                ns.add({
                    'ref': ref, 'area': area, 'name': pota.get('name') or '', 'code': code,
                    'how_sure': 'unsure', 'shows_now': kind, 'why': q.get('plain') or '',
                    'wants': wants, 'found_by': READER, 'status': 'open',
                    'evidence': {'source': source, 'saw': q.get('quote') or '', 'date': today},
                }, today=today)
            for row in ns.open_rows(area=area, include_class=False):
                if row.get('ref') != ref:
                    continue
                if row.get('found_by') != READER or row.get('code') not in QUESTION_CODES:
                    continue
                if row.get('code') not in asked:
                    ns.mark_gone(ref, row.get('code'), READER, today=today)
    return ns


def selftest():
    import tempfile
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(('PASS ' if cond else 'FAIL ') + msg)

    with tempfile.TemporaryDirectory() as td:
        a = NotSure(td + '/a')
        b = NotSure(td + '/b')
        r1 = {'ref': 'US-1', 'area': 'US-UT', 'name': 'One', 'code': 'NAME_DIFFERS', 'how_sure': 'unsure',
              'why': 'names differ', 'wants': ['page facts'], 'found_by': 'test', 'status': 'open'}
        r2 = {'ref': 'US-2', 'area': 'US-UT', 'name': 'Two', 'code': 'INSIDE_BIGGER_UNIT', 'how_sure': 'wrong likely',
              'why': 'inside', 'wants': ['page facts'], 'found_by': 'test', 'status': 'open'}
        a.add(r1, today='2026-11-19')
        a.add(r2, today='2026-11-19')
        b.add(r2, today='2026-11-19')
        b.add(r1, today='2026-11-19')
        check('two writers in either order write the same file',
              (a.root / 'US-UT.json').read_bytes() == (b.root / 'US-UT.json').read_bytes())
        a.add(r1, today='2026-11-20')
        rows = a._load_area('US-UT')
        check('adding the same park and code again keeps one row and moves last_seen',
              len([r for r in rows if r['ref'] == 'US-1']) == 1 and
              next(r for r in rows if r['ref'] == 'US-1')['last_seen'] == '2026-11-20' and
              next(r for r in rows if r['ref'] == 'US-1')['first_seen'] == '2026-11-19')
        check('an unknown code is refused', a.add({'ref': 'US-9', 'area': 'US-UT', 'code': 'MADE_UP', 'how_sure': 'unsure', 'wants': ['page facts']}) is None)
        check('an unknown wants word is refused', a.add({'ref': 'US-8', 'area': 'US-UT', 'code': 'NAME_DIFFERS', 'how_sure': 'unsure', 'wants': ['a crystal ball']}) is None)
        a.add({'ref': '(class)', 'area': 'US', 'name': 'a group', 'code': 'NOT_SAMPLED', 'how_sure': 'unchecked',
               'why': 'a class', 'wants': ['random sample'], 'found_by': 'test', 'status': 'open'}, today='2026-11-19')
        check('a class row is never handed to a bot', all(r['ref'] != '(class)' for r in a.open_rows()))
        a.tried('US-1', 'NAME_DIFFERS', 'park page reader', 'read', 'the page says One', today='2026-11-20')
        a.tried('US-2', 'INSIDE_BIGGER_UNIT', 'park page reader', 'read', 'inside the big unit', today='2026-11-20')
        a.settle('US-2', 'INSIDE_BIGGER_UNIT', 'a reviewer', 'the page quote settled it', 'https://example.gov/p', today='2026-11-20')
        us1 = next(r for r in a._load_area('US-UT') if r['ref'] == 'US-1')
        us2 = next(r for r in a._load_area('US-UT') if r['ref'] == 'US-2')
        check('tried and settle keep the story',
              len(us1['tried']) == 1 and us2['status'] == 'settled' and len(us2['tried']) == 1 and us2['settled']['by'] == 'a reviewer')
    print('SELFTEST PASS' if ok else 'SELFTEST FAIL')
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description='Not sure list')
    p.add_argument('command', nargs='?', default='summary')
    p.add_argument('--root', default='not-sure')
    p.add_argument('--seed', default='')
    p.add_argument('--today', default='')
    p.add_argument('--selftest', action='store_true')
    args = p.parse_args(argv)
    if args.selftest or args.command == '--selftest':
        return selftest()
    ns = NotSure(args.root)
    if args.command == 'import-seed':
        n = ns.import_seed(args.seed, today=args.today)
        print(f'Imported {n} rows into {args.root}.')
        return 0 if n else 1
    if args.command == 'summary':
        print('\n'.join(ns.summary(today=args.today)))
        return 0
    if args.command == 'open':
        for row in ns.open_rows():
            print(f"{row['ref']} {row['code']} {row['how_sure']}")
        return 0
    print('Commands: import-seed, summary, open, --selftest.')
    return 2


if __name__ == '__main__':
    sys.exit(main())
