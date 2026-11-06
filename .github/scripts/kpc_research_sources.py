#!/usr/bin/env python3
"""Report-only outline ranking for the pile solver.

KPC_RESEARCH_SOURCES defaults to off. Off, rank_outlines() is empty and this
module does not read the abbreviation list. Report mode ranks outlines the
solver has already read. It uses the Mapping Rep Tool Box name matcher
(kpc-maprep-check.js canon / nameScore) and, only then, the research-pack
abbreviation list. It does not choose a join and it does not set pile-solver auto.

No source/field mapping is registered here. The solver keeps asking a layer for
the same fields it asked for before. Nothing in this file fetches a host.
"""
import csv, os, pathlib, re, unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
ABBREV_CSV = ROOT / 'data' / 'research-sources' / 'abbreviations.csv'

# Kind words dropped by kpc-maprep-check.js canon(), in that list.
_CORE_DROP = ('wildlife', 'management', 'area', 'state', 'national', 'park', 'parks', 'nature', 'preserve',
              'natural', 'forest', 'refuge', 'the', 'of', 'and', 'site', 'historic', 'historical',
              'recreational', 'recreation', 'resort')
_GENERIC = {'creek', 'lake', 'river', 'fork', 'branch', 'ridge', 'county', 'hunting', 'public',
            'north', 'south', 'east', 'west'}
_ABBREV = None


def mode():
    """off (default) or report. Anything else stays off so a typo cannot change a run."""
    v = (os.environ.get('KPC_RESEARCH_SOURCES') or 'off').strip().lower()
    return 'report' if v == 'report' else 'off'


def fold(s):
    t = ''.join(c for c in unicodedata.normalize('NFKD', str(s or '')) if not unicodedata.combining(c))
    t = t.lower().replace('ß', 'ss')
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def _abbrev_tokens():
    """Short abbreviations from the research-pack list. Phrases are not expanded."""
    out = []
    if not ABBREV_CSV.is_file():
        return out
    with ABBREV_CSV.open(encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            ab = fold(r.get('abbrev') or '')
            ex = fold(r.get('expansion') or '')
            if re.fullmatch(r'[a-z]{2,8}', ab) and ex and ex != ab:
                out.append((ab, ex))
    return sorted(set(out), key=lambda x: -len(x[0]))


def abbrev_tokens():
    global _ABBREV
    if _ABBREV is None:
        _ABBREV = _abbrev_tokens()
    return _ABBREV


def toolbox_canon(s, report=None):
    """Tool Box canon() from kpc-maprep-check.js, then the abbreviation list when report is true.

    Dotted W.M.A. / S.N.P. / S.N.A. / S.P. are expanded the way the toolbox does, before
    punctuation is stripped. Pack abbreviations (SGA, ZEC, ...) are applied only in report mode.
    """
    if report is None:
        report = mode() == 'report'
    t = str(s or '').lower().replace('&', ' and ')
    t = re.sub(r'w\s*\.\s*m\s*\.\s*a\.?', ' wma ', t)
    t = re.sub(r'\bwma\b', ' wildlife management area ', t)
    t = re.sub(r's\s*\.\s*n\s*\.\s*p\.?', ' snp ', t)
    t = re.sub(r'\bsnp\b', ' state nature preserve ', t)
    t = re.sub(r's\s*\.\s*n\s*\.\s*a\.?', ' sna ', t)
    t = re.sub(r'\bsna\b', ' state natural area ', t)
    t = re.sub(r's\s*\.\s*p\.?', ' sp ', t)
    t = re.sub(r'\bsp\b', ' state park ', t)
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if report:
        t = t.replace('natrue', 'nature')
        if re.search(r'\bzec\b', t) and t.endswith('nature reserve'):
            t = re.sub(r'\s+nature reserve$', '', t).strip()
        for ab, ex in abbrev_tokens():
            t = re.sub(rf'\b{re.escape(ab)}\b', ex, t)
        t = re.sub(r'\s+', ' ', t).strip()
    full = t
    core = re.sub(r'\b(?:' + '|'.join(_CORE_DROP) + r')\b', ' ', t)
    core = re.sub(r'\s+', ' ', core).strip() or full
    return full, core


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
    """0-96, the same steps as the Tool Box nameScore. 0 means it would not be offered."""
    if report is None:
        report = mode() == 'report'
    qf, qc = toolbox_canon(query, report=report)
    cf, cc = toolbox_canon(candidate, report=report)
    if not qc or not cc:
        return 0
    if qc == cc or qf == cf:
        return 96
    qt = [w for w in qc.split() if len(w) > 2]
    ct = [w for w in cc.split() if len(w) > 2]
    if qt and all(w in ct for w in qt):
        return 92 if len(ct) == len(qt) else 84
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
    """Source/field mapping. Empty unless the flag is report, and this change adds none.

    A caller that builds a layer query must keep the field list it already used when
    this returns {}. Report mode does not add a row either: the pile solver still
    asks for the fields it asked for before.
    """
    if mode() != 'report':
        return {}
    return {}
