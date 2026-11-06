#!/usr/bin/env python3
"""Report-only outline ranking for the pile solver.

KPC_RESEARCH_SOURCES defaults to off. Off, rank_outlines() is empty and this
module does not read the abbreviation table. Report mode ranks outlines the
solver has already read, using the active Mapping Rep Tool Box matcher
(kpc-maprep-logic.js nameScore / canon / expandName) and its abbreviation
table (data/maprep/abbreviations.json). Short codes from the round-3 return
that are marked sourced are added on top (data/research-sources/abbreviations.csv).
from_memory rows are not in that file. It does not choose a join and it does
not set pile-solver auto.

'game' is not a kind word that gets dropped, so a game area and a recreation
area stay different. No source/field mapping is registered here. Nothing in
this file fetches a host.
"""
import csv, json, os, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ABBREV_JSON = ROOT / 'data' / 'maprep' / 'abbreviations.json'
# Round-3 return: only rows whose origin is sourced. from_memory rows are not in this file.
ABBREV_CSV = ROOT / 'data' / 'research-sources' / 'abbreviations.csv'

# Built-in core from kpc-maprep-logic.js. The JSON table is layered on top.
CORE = (
    ('wma', 'wildlife management area'),
    ('snp', 'state nature preserve'),
    ('sna', 'state natural area'),
    ('sp', 'state park'),
    ('nwr', 'national wildlife refuge'),
    ('nf', 'national forest'),
    ('nra', 'national recreation area'),
    ('sga', 'state game area'),
    ('swa', 'state wildlife area'),
    ('srp', 'state resort park'),
    ('zec', 'zone d exploitation controlee'),
)
# Kind words dropped by canon(). 'game' is not in this list.
_CORE_DROP = ('wildlife', 'management', 'area', 'state', 'national', 'park', 'parks', 'nature', 'preserve',
              'natural', 'forest', 'refuge', 'the', 'of', 'and', 'site', 'historic', 'historical',
              'recreational', 'recreation', 'resort')
_STOP = re.compile(
    r'\b(the|of|and|at|state|national|natural|nature|historic|historical|site|park|parks|wildlife|management|'
    r'area|areas|wma|preserve|forest|recreation|recreational|refuge|sanctuary|center|fee|tract|unit|ky|resort|'
    r'fishing|public|hunting|commission|corps|engineers|us)\b')
_GENERIC = {'creek', 'lake', 'river', 'fork', 'branch', 'ridge', 'county', 'hunting', 'public',
            'north', 'south', 'east', 'west'}
_DOTTED = re.compile(r'\b([a-z](?:\.[a-z]){1,6})\.?\b')
_COMPILED = None
_FROM = None


def mode():
    """off (default) or report. Anything else stays off so a typo cannot change a run."""
    v = (os.environ.get('KPC_RESEARCH_SOURCES') or 'off').strip().lower()
    return 'report' if v == 'report' else 'off'


def reset_matcher():
    """Drop the cached abbreviation table. Tests point ABBREV_JSON elsewhere, then call this."""
    global _COMPILED, _FROM
    _COMPILED = None
    _FROM = None


def _compile(rows):
    """CORE first, then table rows. A repeated token keeps its place and takes the new expansion."""
    seen, order = {}, []

    def put(tok, exp):
        if tok in seen:
            seen[tok] = exp
            return
        seen[tok] = exp
        order.append(tok)

    for tok, exp in CORE:
        put(tok, exp)
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        token = str(r.get('token') or '').lower().replace('.', '')
        expansion = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', str(r.get('expansion') or '').lower())).strip()
        if len(token) >= 2 and expansion:
            put(token, expansion)
    items = [(t, seen[t]) for t in order]
    items.sort(key=lambda x: -len(x[0]))
    return items


def _read_json_rows(path):
    """Toolbox abbreviations.json. Not valid UTF-8 raises; research_rank catches that and
    leaves the solver's verdict alone."""
    doc = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    if isinstance(doc, dict):
        return list(doc.get('rows') or [])
    return list(doc or [])


def _note_expansion(text):
    """A commentary about a name, not a designation to substitute."""
    low = text.lower()
    return any(w in low for w in (
        'combined dual', 'apostrophe', 'hyphenat', 'misspell', 'distinct from', 'also in',
        'same name', 'spelled out', 'slash', 'dash-separated', 'possessive', 'french-derived',
        'also listed', 'two designations'))


def _sourced_tokens(path):
    """Short codes from the sourced abbreviation list. Phrases and from_memory rows are not applied.
    A code the toolbox table already defines keeps that expansion when the words differ (SPA)."""
    out = []
    with pathlib.Path(path).open(encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if (r.get('origin') or '').strip() != 'sourced':
                continue
            ab = (r.get('abbrev') or '').strip()
            if not re.fullmatch(r'[A-Za-z]{2,8}', ab.replace('.', '')) or ' ' in ab or '/' in ab:
                continue
            ex = (r.get('expansion') or '').strip()
            if not ex or _note_expansion(ex):
                continue
            out.append({'token': ab, 'expansion': ex})
    return out


def table_rows():
    """Rows passed to the same compile the Tool Box uses: its table, then sourced short codes.
    Reading either file can raise UnicodeDecodeError. The caller is report mode only."""
    rows = _read_json_rows(ABBREV_JSON) if pathlib.Path(ABBREV_JSON).is_file() else []
    if pathlib.Path(ABBREV_CSV).is_file():
        have = {str(r.get('token') or '').lower().replace('.', '') for r in rows if isinstance(r, dict)}
        for extra in _sourced_tokens(ABBREV_CSV):
            tok = extra['token'].lower().replace('.', '')
            if tok in have:
                for i, r in enumerate(rows):
                    if isinstance(r, dict) and str(r.get('token') or '').lower().replace('.', '') == tok:
                        rows[i] = dict(r, token=extra['token'], expansion=extra['expansion'])
                        break
                continue
            rows.append(extra)
            have.add(tok)
    return rows


def compiled():
    global _COMPILED, _FROM
    key = (str(ABBREV_JSON), str(ABBREV_CSV))
    if _COMPILED is not None and _FROM == key:
        return _COMPILED
    _COMPILED = _compile(table_rows())
    _FROM = key
    return _COMPILED


def expand_name(s):
    """kpc-maprep-logic.js expandName: dotted letters collapse, then the abbreviation table."""
    t = str(s or '').lower().replace('&', ' and ')
    t = _DOTTED.sub(lambda m: m.group(0).replace('.', ''), t)
    for tok, exp in compiled():
        rx = re.compile(r'(?<![a-z0-9])' + re.escape(tok) + r'(?![a-z0-9])')
        t = rx.sub(lambda m, e=exp: ' ' + e + ' ', t)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', t)).strip()


def canon(s):
    """full text after expansion, and the core with kind words removed. 'game' stays."""
    full = expand_name(s)
    core = re.sub(r'\b(?:' + '|'.join(_CORE_DROP) + r')\b', ' ', full)
    core = re.sub(r'\s+', ' ', core).strip() or full
    return full, core


def toolbox_canon(s, report=None):
    """Same pair as canon(). report is accepted so older callers keep working; the table
    is the toolbox table either way. rank_outlines still returns nothing unless report mode."""
    return canon(s)


def norm_name(s):
    return re.sub(r'\s+', ' ', _STOP.sub(' ', expand_name(s))).strip()


def fuzzy_same(a, b):
    """Shorter name of at least two words is a whole-word prefix or suffix of the longer one."""
    n, m = norm_name(a), norm_name(b)
    if not n or not m or len(n) < 4 or len(m) < 4:
        return False
    if n == m:
        return True
    w, x = n.split(' '), m.split(' ')
    if len(w) <= len(x):
        sh, lo = w, x
    else:
        sh, lo = x, w
    if len(sh) < 2:
        return False
    phrase = ' '.join(sh)
    return ' '.join(lo[:len(sh)]) == phrase or ' '.join(lo[-len(sh):]) == phrase


def _tokens(s):
    return [w for w in str(s or '').split(' ') if len(w) > 2]


def _dice(a, b):
    if a == b:
        return 1.0
    if not a or not b or len(a) < 2 or len(b) < 2:
        return 0.0

    def bg(s):
        m = {}
        for i in range(len(s) - 1):
            k = s[i:i + 2]
            m[k] = m.get(k, 0) + 1
        return m

    A, B = bg(a), bg(b)
    inter = sum(min(n, B.get(k, 0)) for k, n in A.items())
    return (2.0 * inter) / ((sum(A.values()) + sum(B.values())) or 1)


def name_score(query, candidate, report=None):
    """0-96, the same steps as kpc-maprep-logic.js nameScore. 0 means it would not be offered."""
    if report is None:
        report = mode() == 'report'
    qf, qc = canon(query)
    cf, cc = canon(candidate)
    if not qc or not cc:
        return 0
    if qc == cc or qf == cf:
        return 96
    qt, ct = _tokens(qc), _tokens(cc)
    if qt and all(w in ct for w in qt):
        return 92 if len(ct) == len(qt) else 84
    if fuzzy_same(query, candidate):
        return 88
    d = _dice(qc, cc)
    shared = [w for w in qt if w in ct and w not in _GENERIC and len(w) >= 4]
    if d >= 0.8 and shared:
        return 70
    if d >= 0.72 and shared:
        return 58
    if any(len(w) >= 6 for w in shared) and d >= 0.45:
        return 52
    return 0


def rank_outlines(park_name, candidates, report=None):
    """Rank outlines already read. Empty unless report mode. Does not pick a join or set auto."""
    if report is None:
        report = mode() == 'report'
    if not report:
        return []
    out = []
    for c in candidates or []:
        name = c.get('name') if isinstance(c, dict) else str(c)
        row = dict(c) if isinstance(c, dict) else {'name': name}
        row['name'] = name
        row['score'] = name_score(park_name, name, report=True)
        out.append(row)
    out.sort(key=lambda r: (-r['score'], str(r.get('id') or ''), str(r.get('name') or '')))
    return out


def gated_source_fields(url='', fields=None):
    """Source/field mapping. Empty unless the flag is report, and this change adds none."""
    if mode() != 'report':
        return {}
    return {}
