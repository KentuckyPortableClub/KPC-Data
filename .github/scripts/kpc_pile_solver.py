#!/usr/bin/env python3
"""REVIEW PILE SOLVER (Nov 4 2026; handoff REVIEW_PILE_SOLVER_HANDOFF.md, Brandon 7:16 AM CST: 'have the whole review list be run one
time then anything new gets ran automatically and eventually I take over the list and check what it can not fix').

Reads KPC-Links' pre-check review pile (review-pile.csv, regenerated every run) and gives every park ONE verdict:
  SOLVED-JOIN   the official outline is confirmed, with evidence        -> proposed answer word YES
  SOLVED-PIN    the park stays a pin, with the reason                    -> proposed answer word PIN
  NEEDS-PERSON  the bot could not settle it; 'whats_missing' says what   -> proposed answer word NOT SURE
  UNTOUCHED     KEEP / ASK BRANDON rows and parks a person already decided (overrides join / a counting sign-off)
PROPOSALS ONLY: it writes to data/waiting/in/data/pile-solver/ (the waiting room grades it), data/pile-solver/state.json and new
'tract' rows in data/detective/questions.json. It never writes a key, overrides.json or the answer sheet, and never deletes a file.

THE RULES (handoff section 4 + Brandon's rulings; when in doubt NEEDS-PERSON, never guess):
  * Join = same place by name (type words dropped, spellings allowed) + same kind + proof of location (pin inside or within 100 m),
    from an official source (agency layer, PAD-US). OpenStreetMap / WDPA never confirm a join.
  * RULE 3 (Brandon's standing ruling, Nov 4 7:34 AM CST): an exact or near name match to the official name AND the POTA pin in a
    county the official outline is in = SOLVED-JOIN with the flag 'POTA pin may be off', even past 5 km. Without both, a pin more
    than 100 m out = NEEDS-PERSON. We never move a POTA pin.
  * Rule 18: a piece word on one side only, North / South Fork, Upper / Lower, Unit 2 / 3, and a compass word that is only inside the
    other name's bracket ('Langres Nord' vs 'Langres (secteur Nord)') = NEEDS-PERSON (a tract join needs a person's review, 18c).
    A bracketed place qualifier ('(Lewis County)') is not a piece.
  * A different kind of place = NEEDS-PERSON; an agency alias = NEEDS-PERSON unless a counting person said YES to that exact name and
    the pin is inside; a small site (campground, boat ramp, dam...) stays a pin unless the agency has a record for the site itself; a
    park never takes the bigger place around it.
  * A person's answer counts only from Brandon (KZ4CP) at or after 9:37 AM CST Nov 2 2026.
  * Rows with one shared cause (the German 'joined row with no id' rows) = ONE grouped NEEDS-PERSON finding, not researched
    (Brandon Nov 4: likely a key-builder bug, being fixed separately).

Env: LINKS (KPC-Links checkout, default ../links) · PILE (review-pile.csv; default: run the pre-check into $RUNNER_TEMP) · AREAS
     ('US-TN US-CO'; blank = every area with rows to do) · MAX_PARKS (0 = no cap) · MINUTES (50) · MODE=backfill|auto (auto: only
     when data/pile-solver/state.json says auto=true) · FREEZE (a folder: save every fetched answer there as a selftest fixture)
     · REPORT_ONLY=1 (write outputs to OUT_DIR, not into the repo: the PR check run)
     --selftest  offline, frozen fixtures in tests/fixtures/pile_solver/
"""
import csv, datetime as dt, glob, hashlib, io, json, math, os, pathlib, re, subprocess, sys, time, urllib.parse

VERSION = '1'
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DATA = pathlib.Path(os.environ.get('DATA') or '.')
LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
sys.path.insert(1, str(LINKS / '.github/scripts'))
import kpc_manners  # noqa: E402
import kpc_detective_bot as DET  # noqa: E402  (imports with no side effects: constants + functions only)
import kpc_key_rules as KR  # noqa: E402  (KPC-Links: the key's own name and piece rules)
import kpc_precheck as PC  # noqa: E402  (KPC-Links: rule18_differs, name_how, kind_ok, tags; reads env at import only)

CST = dt.timezone(dt.timedelta(hours=-6))
CUTOFF = dt.datetime(2026, 11, 2, 9, 37, tzinfo=CST)   # rule 10: only Brandon's sign-offs from here on count
PERSON = re.compile(r'^\s*(?:brandon(?: white)?|kz4cp)\s*$', re.I)
PADUS = 'https://edits.nationalmap.gov/arcgis/rest/services/PAD-US/PAD_US/MapServer/0'
TIGER = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer'
NEAR_M = 100          # rule 1: inside or within 100 m
FIVE_KM = 5000        # rule 3: past this a person check is still asked for unless name + county both back the match
NOT_OFFICIAL = re.compile(r'openstreetmap|\bosm\b|wdpa|protected planet|world database', re.I)
PAD_NEVER = re.compile(r'proclamation|easement', re.I)
SMALL_SITE = re.compile(r'\b(campground|camp ground|boat ramp|boat launch|launch|dam|marina|access site|fishing access|landing|picnic area|trailhead)\b', re.I)
BIGGER = re.compile(r'national forest|national grassland|national recreation area|national park\b|national preserve|national conservation area|'
                    r'state forest|wilderness(?! study)|wildlife management district', re.I)
LAKE_PARK = re.compile(r'\b(lake|reservoir|pond)\b', re.I)
COMPASS = {'north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest',
           'nord', 'sud', 'est', 'ouest', 'nordest', 'nordouest', 'sudest', 'sudouest'}
COLS = ['ref', 'pota_name', 'area', 'pota_lat', 'pota_lon', 'official_site_url', 'verdict', 'answer_word', 'candidate_layer_url', 'record_id',
        'record_name', 'agency', 'distance_m', 'kind_park', 'kind_record', 'rule18_note', 'pin_flag', 'evidence_urls', 'reason', 'whats_missing',
        'source_rows', 'checked_at', 'solver_version']
SHEET_COLS = ['ref', 'pota_name', 'area', 'source_url', 'layer_id', 'record_id', 'key_id', 'unit_id', 'unit_id_field', 'record_name', 'fp', 'status',
              'quality_yes', 'approved_by', 'approved_date', 'evidence', 'last_checked', 'seed_from', 'note']
WORD = {'SOLVED-JOIN': 'YES', 'SOLVED-PIN': 'PIN', 'NEEDS-PERSON': 'NOT SURE'}
PATTERNS = {'P1-no-record-id': ('joined row with no id',
                                'the key builder wrote joined rows with no record id (likely a key-builder bug, being fixed separately); '
                                'rebuild this key after the fix, then the rows that are still doubtful come back to the pile')}
T0 = time.time()


def now_cst(): return dt.datetime.now(CST).strftime('%Y-%m-%d %H:%M CST')
def notice(m): print('::notice title=Pile solver::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > float(os.environ.get('MINUTES') or 50) * 60
def sha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


# ------------------------------------------------------------------ inputs (one reader per source; phase 2 adds the dropped lists)
def read_pile(path):
    """review-pile.csv -> [row dicts] in one shape every later source must also give:
    {ref, area, name, type, flags (set), why, ids, lat, lon, action, src}. A park in two areas (US-6090) keeps its first area."""
    out = []
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            out.append({'ref': r['park'], 'area': (r['area'].split() or [''])[0], 'areas': r['area'], 'name': r['name'], 'type': r['type'],
                        'flags': set(r['flags'].split()), 'why': r['why'], 'ids': [x.strip() for x in r['joined ids'].split(',') if x.strip()],
                        'lat': r['pota_lat'], 'lon': r['pota_lon'], 'action': r['action'], 'src': 'pile',
                        'h': sha([r[k] for k in r if k != 'action'] + [r['action'][:40]])})
    return out


def read_dropped(folder):
    """Phase 2 (not switched on): data/status/key-check/<key>-<build>/dropped/*.csv in the same row shape. Left empty until those
    lists are merged; the solver loop already takes any list of rows."""
    return []


def key_row(area, ref):
    if area.startswith('US-'): f = LINKS / f'data/us-key/{area}.json'
    elif area.startswith('CA-'): f = LINKS / f'data/ca-key/{area}.json'
    else: f = DATA / f'data/world-key/{area}.json'
    return ((KEYS.setdefault(str(f), load(f, {})).get('parks') or {}).get(ref)) or {}


KEYS = {}


def layer_of(rid):
    """record id -> (query url, name field, label, family). Numeric = PAD-US (fee records); 'sgtnh17' = family 'sgtnh' + object id."""
    s = str(rid)
    if s.isdigit(): return PADUS + '/query', 'Unit_Nm', 'USGS PAD-US', 'padus', s
    m = re.match(r'^([a-z]+)(\d+)$', s)
    if not m: return None
    L = LAYERS.get(m.group(1))
    if not L: return None
    return L[0], L[1], L[-1], m.group(1), m.group(2)


LAYERS = {}


# ------------------------------------------------------------------ decisions already made (read only)
def answer_counts(row):
    """Rule 10: True only for Brandon / KZ4CP, dated at or after 9:37 AM CST Nov 2 2026. A date of Nov 2 with no time does not count
    (it might be before 9:37); Quality / chat / bot names never count."""
    if not PERSON.match(str(row.get('approved_by') or '')): return False
    d = str(row.get('approved_date') or '').strip()
    try: day = dt.date.fromisoformat(d[:10])
    except ValueError: return False
    if day > CUTOFF.date(): return True
    if day < CUTOFF.date(): return False
    m = re.search(r'(\d{1,2}):(\d\d)\s*([AP]M)', d + ' ' + str(row.get('evidence') or '') + ' ' + str(row.get('note') or ''), re.I)
    if not m: return False
    h = int(m.group(1)) % 12 + (12 if m.group(3).upper() == 'PM' else 0)
    return (h, int(m.group(2))) >= (9, 37)


def decisions():
    ov = {}
    for f in ('data/us-key/overrides.json', 'data/ca-key/overrides.json'): ov.update(load(LINKS / f, {}).get('parks') or {})
    sheet = {}
    for f in sorted(glob.glob(str(DATA / 'data/answer-sheet/*.csv'))):
        with open(f, newline='', encoding='utf-8') as fh:
            for r in csv.DictReader(fh): sheet.setdefault(r.get('ref'), []).append(r)
    return ov, sheet


# ------------------------------------------------------------------ name / piece / kind tests (offline, all from the shared rules)
def strip_place(t): return re.sub(r'\s*\([^)]*\)', '', str(t or '')).strip()


def bracket_compass(a, b):
    """Rule 4 (Nov 4 handoff): a compass word that is only inside the OTHER name's bracket is another piece:
    'Langres Nord' vs 'Langres (secteur Nord)'. Main's rule18_differs returns '' here; a KPC patch is adding it."""
    for x, y in ((a, b), (b, a)):
        inside = {w for q in re.findall(r'\(([^)]*)\)', str(y or '')) for w in KR._plain_words(q)} & COMPASS
        outside_y = set(KR._plain_words(strip_place(y))) & COMPASS
        outside_x = set(KR._plain_words(strip_place(x))) & COMPASS
        hit = sorted((inside & outside_x) - outside_y)
        if hit: return f"rule 18: '{' '.join(hit)}' is only inside the bracket of '{y}'"
    return ''


def rule18(park, rec): return PC.rule18_differs(park, rec, False) or bracket_compass(park, rec)


def same_name(park, rec):
    """'same' | 'spelling' | 'other' on the names with place brackets taken off (rule 18 is asked separately, first)."""
    return PC.name_how(strip_place(park), strip_place(rec), r18=True)


def kind_clash(ptype, pname, rec):
    k = PC.kind_ok(ptype or pname, rec)
    if k is False: return True
    return DET.judge_name(pname, rec) == 'different' and bool(DET.core_words(pname) & DET.core_words(rec))   # same words, unkindred kind


def kind_words(t): return ' '.join(sorted(PC.tags(t) | DET.classes(t))) or ''


# ------------------------------------------------------------------ fetching (every read goes through kpc_manners)
class Fetch:
    """Polite reads through Manners. In --selftest a FixtureManners stands in for Manners (same .get), so the code path is the same."""
    def __init__(self, M, freeze=None):
        self.M, self.freeze, self.skipped, self.n = M, freeze, [], 0

    def json(self, base, params):
        url = base + '?' + urllib.parse.urlencode(sorted(params.items()))
        self.n += 1
        st, _h, body, _u = self.M.get(url, timeout=40, accept='application/json,*/*;q=0.5')
        if st != 200 or not body:
            self.skipped.append((kpc_manners.safe_url(url), str(st))); return None, url, str(st)
        try: j = json.loads(body.decode('utf-8', 'replace'))
        except Exception: self.skipped.append((url, 'not JSON')); return None, url, 'not JSON'  # noqa: BLE001
        if isinstance(j, dict) and j.get('error'):
            self.skipped.append((url, 'server error')); return None, url, 'server error: ' + str(j['error'])[:80]
        if self.freeze:
            p = pathlib.Path(self.freeze) / 'responses.json'; d = load(p, {}); d[url] = j
            p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(d, indent=1, sort_keys=True), encoding='utf-8')
        return j, url, '200'

    def record(self, rid):
        """-> {id, name, attrs, rings, layer, url, label, family} or {'error': why}."""
        L = layer_of(rid)
        if not L: return {'error': f'no layer known for record id {rid} (not in layers.json)'}
        qurl, nfield, label, fam, oid = L
        base = qurl if qurl.endswith('/query') else qurl.rstrip('/') + '/query'
        for off in ('0.00005', '0.0005'):   # ~5 m detail; a huge outline over Manners' 3 MB read is retried at ~50 m
            j, url, st = self.json(base, {'objectIds': oid, 'outFields': '*', 'returnGeometry': 'true', 'outSR': '4326',
                                          'maxAllowableOffset': off, 'geometryPrecision': '6', 'f': 'json'})
            if j is not None or st != 'not JSON': break
            self.skipped.pop()   # the coarser try decides; only its failure is listed for a person
        if j is None: return {'error': f'could not read {url} ({st})', 'url': url}
        feats = j.get('features') or []
        if not feats: return {'error': f'record {rid} is no longer on its layer ({url})', 'url': url}
        a = feats[0].get('attributes') or {}
        g = feats[0].get('geometry') or {}
        nm = a.get(nfield) or a.get(nfield.upper()) or a.get(DET.name_field(a)) or ''
        return {'id': str(rid), 'name': str(nm), 'attrs': a, 'rings': g.get('rings') or [], 'layer': base[:-6], 'url': url, 'label': label,
                'family': fam, 'html': url.replace('f=json', 'f=html')}

    def counties_at_pin(self, la, lo):
        lu = self.county_layer()
        if not lu: return None, 'the Census county layer could not be read'
        j, url, st = self.json(lu + '/query', {'geometry': f'{lo},{la}', 'geometryType': 'esriGeometryPoint', 'inSR': '4326',
                                               'spatialRel': 'esriSpatialRelIntersects', 'outFields': 'GEOID,NAME,STATE', 'returnGeometry': 'false', 'f': 'json'})
        if j is None: return None, f'could not read {url} ({st})'
        return {str((f.get('attributes') or {}).get('GEOID')): (f.get('attributes') or {}).get('NAME') for f in j.get('features') or []}, url

    def counties_of(self, rings):
        lu = self.county_layer()
        if not lu: return None, 'the Census county layer could not be read'
        pts = sum(len(r) for r in rings)
        k = max(1, math.ceil(pts / 160))
        simple = [[[round(p[0], 4), round(p[1], 4)] for p in r[::k]] + [[round(r[0][0], 4), round(r[0][1], 4)]] for r in rings if len(r) >= 4]
        simple = [r for r in simple if len(r) >= 4]
        if not simple: return None, 'the outline has no usable rings'
        j, url, st = self.json(lu + '/query', {'geometry': json.dumps({'rings': simple}, separators=(',', ':')), 'geometryType': 'esriGeometryPolygon',
                                               'inSR': '4326', 'spatialRel': 'esriSpatialRelIntersects', 'outFields': 'GEOID,NAME,STATE',
                                               'returnGeometry': 'false', 'f': 'json'})
        if j is None: return None, f'could not read the county layer ({st})'
        return {str((f.get('attributes') or {}).get('GEOID')): (f.get('attributes') or {}).get('NAME') for f in j.get('features') or []}, url

    _county = None

    def county_layer(self):
        """The 'Counties' layer of TIGERweb State_County, found by name (its number is not hard-coded)."""
        if self._county is None:
            j, _u, _st = self.json(TIGER, {'f': 'json'})
            lid = next((L.get('id') for L in (j or {}).get('layers') or [] if str(L.get('name')).strip().lower() == 'counties'), None)
            self._county = f'{TIGER}/{lid}' if lid is not None else ''
        return self._county


class FixtureManners:
    """--selftest: answers .get(url) from frozen responses; anything not frozen is a 404 (never the network)."""
    def __init__(self, responses): self.r, self.asked = responses, []

    def get(self, u, **kw):
        self.asked.append(u)
        if u in self.r: return 200, {}, json.dumps(self.r[u]).encode(), u
        return 404, {}, b'', u


# ------------------------------------------------------------------ geometry (pin to outline, metres; small-area flat projection)
def dist_m(la, lo, rings):
    """0 when the pin is inside the outline (even-odd over all rings, so holes count), else the metres to the nearest edge."""
    if not rings: return None
    kx, ky = 111320 * math.cos(math.radians(la)), 110540
    inside, best = False, float('inf')
    for r in rings:
        for i in range(len(r) - 1):
            (x1, y1), (x2, y2) = r[i][:2], r[i + 1][:2]
            if (y1 > la) != (y2 > la) and lo < (x2 - x1) * (la - y1) / ((y2 - y1) or 1e-12) + x1: inside = not inside
            ax, ay, bx, by = (x1 - lo) * kx, (y1 - la) * ky, (x2 - lo) * kx, (y2 - la) * ky
            dx, dy = bx - ax, by - ay
            t = 0 if dx == dy == 0 else max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return 0 if inside else round(best)


# ------------------------------------------------------------------ the verdict
def base_row(p, ver=VERSION):
    return {'ref': p['ref'], 'pota_name': p['name'], 'area': p['area'], 'pota_lat': p['lat'], 'pota_lon': p['lon'], 'official_site_url': p.get('page', ''),
            'verdict': '', 'answer_word': '', 'candidate_layer_url': '', 'record_id': '', 'record_name': '', 'agency': '', 'distance_m': '',
            'kind_park': kind_words(p['type'] or p['name']), 'kind_record': '', 'rule18_note': '', 'pin_flag': '', 'evidence_urls': '',
            'reason': '', 'whats_missing': '', 'source_rows': f"{' '.join(sorted(p['flags']))}: {p['why']}"[:500], 'checked_at': now_cst(),
            'solver_version': ver}


def done(row, verdict, reason, missing='', **kw):
    row.update(kw); row['verdict'] = verdict; row['answer_word'] = WORD.get(verdict, '')
    row['reason'] = reason; row['whats_missing'] = missing if verdict == 'NEEDS-PERSON' else ''
    return row


def solve(p, F, ov, sheet):
    """One pile row -> one output row. F = Fetch (None = offline: anything that needs the web becomes NEEDS-PERSON)."""
    row = base_row(p)
    act = p['action'].upper()
    if act.startswith('KEEP'): return done(row, 'UNTOUCHED', 'KEEP: a person approved this park (rule 22); not re-decided')
    if act.startswith('ASK BRANDON'): return done(row, 'UNTOUCHED', 'ASK BRANDON: already a question to Brandon; not answered here')
    o = ov.get(p['ref']) or {}
    if o.get('join'):   # handoff: an override is a person's decision; the note says whose, so Brandon can spot one that is not his
        who = 'Brandon' if re.search(r'brandon|kz4cp', str(o.get('why')), re.I) else 'not marked as Brandon: ' + str(o.get('why') or '')[:120]
        return done(row, 'UNTOUCHED', f"decided in overrides.json (join {o.get('join')}, {o.get('when', '')}; {who}); not re-proposed")
    yes = [r for r in sheet.get(p['ref'], []) if str(r.get('status')).strip().upper() in ('YES', 'APPROVED') and answer_counts(r)]
    if yes: return done(row, 'UNTOUCHED', f"answered on the answer sheet by {yes[0].get('approved_by')} ({yes[0].get('approved_date')}); not re-proposed")
    # pattern rows: one grouped finding, no research (Brandon Nov 4)
    if 'BROKEN_ROW' in p['flags'] and 'joined row with no id' in p['why']:
        return done(row, 'NEEDS-PERSON', 'grouped finding P1-no-record-id: ' + PATTERNS['P1-no-record-id'][1],
                    'the key builder fix for joined rows with no record id, then a rebuild of this key', pattern='P1-no-record-id')
    kp = key_row(p['area'], p['ref'])
    nos = {str(x) for x in (o.get('no') or [])}
    m = [x for x in (kp.get('m') or []) if isinstance(x, list) and str(x[0]) not in nos]
    if not m and p['ids']: m = [[i, '', 0, ''] for i in p['ids'] if i not in ('None', '') and i not in nos]
    if not m:
        return done(row, 'NEEDS-PERSON', 'the key has no joined record left for this park', 'which official record (layer + id) is this park, if any')
    pname, ptype = p['name'] or kp.get('n') or '', p['type'] or kp.get('t') or ''

    # 1. rule 18 (pieces): never a bot join
    r18 = [(x, w) for x in m if x[1] for w in [rule18(pname, x[1])] if w]
    if r18:
        x, w = r18[0]
        row['rule18_note'] = '; '.join(f'{y[0]} {y[1]} ({ww})' for y, ww in r18[:4])
        piece = re.search(r"'([^']+)'", w)
        return done(row, 'NEEDS-PERSON', f"rule 18: the joined record '{x[1]}' ({x[0]}) may be another piece of the land than '{pname}'",
                    f"a person's tract review (rule 18c): is '{pname}' the whole land or only the '{piece.group(1) if piece else 'named'}' piece, "
                    f"and is there an official record for that piece alone", record_id=str(x[0]), record_name=x[1], question='tract')
    # 2. kind
    clash = [x for x in m if x[1] and kind_clash(ptype, pname, x[1])]
    if clash:
        x = clash[0]; water = bool(LAKE_PARK.search(pname) and any(LAKE_PARK.search(str(y[1])) and not PC.tags(y[1]) - {'water'} for y in m))
        return done(row, 'NEEDS-PERSON', f"kind differs: '{pname}' ({ptype or 'park'}) vs the record '{x[1]}' ({x[0]}, {kind_words(x[1]) or 'other kind'})"
                    + ('; a water-only lake outline is possible (rule 7)' if water else ''),
                    "a person's call on the kind: is the park this record's land" + (", or only the lake water (labelled 'water only')" if water else ', or another record') + '?',
                    record_id=str(x[0]), record_name=x[1], kind_record=kind_words(x[1]))
    # 3. small site (rule 9)
    if SMALL_SITE.search(pname) and not any(SMALL_SITE.search(str(x[1])) for x in m if x[1]):
        x = m[0]
        return done(row, 'SOLVED-PIN', f"'{pname}' is a small site; the joined record '{x[1]}' ({x[0]}) is not a record for the site itself (rule 9): the park stays a pin",
                    record_id=str(x[0]), record_name=x[1])
    # 4. names; an alias is a person's call (rule 8)
    names = {str(x[0]): same_name(pname, x[1]) if x[1] else 'other' for x in m}
    alias = [x for x in m if names[str(x[0])] == 'other']
    if alias:   # no fetch needed unless a counting YES to that exact name exists, or the record may be the bigger place (rule 5)
        x = alias[0]
        said = [s for s in sheet.get(p['ref'], []) if str(s.get('record_name')).strip().lower() == str(x[1]).strip().lower()
                and str(s.get('status')).strip().upper() == 'YES' and answer_counts(s)]
        if not said and not BIGGER.search(str(x[1])):
            return done(row, 'NEEDS-PERSON', f"the record name '{x[1]}' ({x[0]}) is not the park name '{pname}': an agency alias joins only on a person's YES "
                        f"to that exact name with the pin inside (rule 8)", f"a person's YES or NO to the exact name '{x[1]}' for {p['ref']}",
                        record_id=str(x[0]), record_name=x[1])
    if F is None:
        return done(row, 'NEEDS-PERSON', 'offline run: the outline and county could not be read', 'a run with the network (GitHub Actions)')
    # 5. read every joined record (official layer, pin distance, county)
    try: la, lo = float(p['lat']), float(p['lon'])
    except ValueError: return done(row, 'NEEDS-PERSON', 'the POTA pin is not a number', 'a person to report the pin to POTA')
    recs, errs = [], []
    for x in m:
        r = F.record(x[0])
        if r.get('error'): errs.append(r['error']); continue
        if NOT_OFFICIAL.search(r['label']): errs.append(f"{x[0]} is from {r['label']} (not an official source)"); continue
        if r['family'] == 'padus' and PAD_NEVER.search(str(r['attrs'].get('Category'))): errs.append(f"{x[0]} is a PAD-US {r['attrs'].get('Category')} record (never an outline)"); continue
        r['d'] = dist_m(la, lo, r['rings']); r['how'] = same_name(pname, r['name'] or x[1]); r['r18'] = rule18(pname, r['name'] or x[1])
        r['agency'] = str(r['attrs'].get('Mang_Name') or r['attrs'].get('Loc_Mang') or r['label'])[:80]
        recs.append(r)
    if errs and not recs:
        return done(row, 'NEEDS-PERSON', 'no joined record could be read: ' + '; '.join(errs[:3]), 'a person to open the record(s) by hand: ' + '; '.join(errs[:2]))
    best = min(recs, key=lambda r: (r['d'] is None, r['d'] or 0))
    row.update(candidate_layer_url=best['layer'], record_id=best['id'], record_name=best['name'], agency=' + '.join(sorted({r['agency'] for r in recs}))[:160],
               distance_m='' if best['d'] is None else best['d'], kind_record=kind_words(best['name']),
               evidence_urls=' | '.join(dict.fromkeys(r['html'] for r in recs))[:900])
    if any(r['r18'] for r in recs):
        r = next(r for r in recs if r['r18'])
        return done(row, 'NEEDS-PERSON', f"rule 18 on the live record name '{r['name']}': {r['r18']}", "a person's tract review (rule 18c)", rule18_note=r['r18'], question='tract')
    if any(kind_clash(ptype, pname, r['name']) for r in recs if r['name']):
        r = next(r for r in recs if r['name'] and kind_clash(ptype, pname, r['name']))
        return done(row, 'NEEDS-PERSON', f"kind differs on the live record '{r['name']}'", "a person's call on the kind of place")
    # an alias (no name match): only a counting YES to that exact name with the pin inside joins
    al = [r for r in recs if r['how'] == 'other']
    if al or alias:
        r = al[0] if al else best
        said = [s for s in sheet.get(p['ref'], []) if str(s.get('record_name')).strip().lower() == str(r['name']).strip().lower()
                and str(s.get('status')).strip().upper() == 'YES' and answer_counts(s)]
        if said and r['d'] == 0 and len(recs) == 1:
            return done(row, 'SOLVED-JOIN', f"the agency name '{r['name']}' was said YES by {said[0]['approved_by']} ({said[0]['approved_date']}) and the pin is inside")
        if BIGGER.search(r['name']) and r['d'] == 0 and not BIGGER.search(ptype + ' ' + pname):
            hit = DET.judge_name(pname, r['name'])
            return done(row, 'SOLVED-PIN', f"the joined record '{r['name']}' is the bigger place around the park (rule 5; names: {hit}); no record of the park itself is joined")
        return done(row, 'NEEDS-PERSON', f"the record name '{r['name']}' ({r['id']}) is not the park name '{pname}' (an alias needs a person's YES, rule 8)",
                    f"a person's YES or NO to the exact name '{r['name']}' for {p['ref']}" + (f" (the pin is {r['d']} m from it)" if r['d'] else ' (the pin is inside)'))
    if errs:
        return done(row, 'NEEDS-PERSON', f"{len(recs)} record(s) read, but: " + '; '.join(errs[:3]), 'a person to open these record(s) by hand: ' + '; '.join(errs[:2]))
    far = [r for r in recs if r['d'] is None or r['d'] > NEAR_M]
    if not far:
        return done(row, 'SOLVED-JOIN', f"name {best['how']}, same kind, pin inside or within {NEAR_M} m of every joined record (rule 1)"
                    + (f"; dual agency: {row['agency']}" if len({r['agency'] for r in recs}) > 1 else ''))
    # rule 3 (Brandon's standing ruling): name match + pin in a county the outline is in = SOLVED-JOIN + flag, even past 5 km
    pin_c, cu = F.counties_at_pin(la, lo)
    if pin_c is None: return done(row, 'NEEDS-PERSON', f'the pin is {best["d"]} m from the outline and the county could not be checked: {cu}', 'the county of the pin and of the outline')
    if not pin_c: return done(row, 'NEEDS-PERSON', 'the pin is in no US county (water or out of the country?)', 'a person to check the POTA pin and report it to POTA')
    bad = []
    for r in far:
        rc, why = F.counties_of(r['rings'])
        if rc is None: bad.append(f"{r['id']}: {why}"); continue
        if not set(pin_c) & set(rc): bad.append(f"{r['id']} lies in {', '.join(sorted(v for v in rc.values() if v)) or '?'}; the pin is in {', '.join(v for v in pin_c.values() if v)}")
    km = round((best['d'] or 0) / 1000, 1)
    if bad:
        return done(row, 'NEEDS-PERSON', f"the pin is {km} km from the outline and the county does not back the match: " + '; '.join(bad[:2]),
                    f"a person to say whether '{best['name']}' is {p['ref']} (pin {km} km out, other county), or report the POTA pin to POTA")
    return done(row, 'SOLVED-JOIN', f"name {best['how']} ('{best['name']}'), same kind, and the pin is in {', '.join(v for v in pin_c.values() if v)} like the outline "
                f"(rule 3, Brandon's ruling) although it is {km} km out" + (' (more than 5 km)' if (best['d'] or 0) > FIVE_KM else ''),
                pin_flag='POTA pin may be off')


# ------------------------------------------------------------------ outputs
def sheet_rows(r):
    """Proposed answer-sheet rows in the sheet's own columns; status is always PROPOSED and approved_by stays empty (rule 11)."""
    note = f"pile solver v{VERSION}: proposed {r['answer_word']}" + (f" ({r['pin_flag']})" if r['pin_flag'] else '') + f"; {r['reason']}"[:300]
    if r['verdict'] == 'NEEDS-PERSON': note += f"; missing: {r['whats_missing']}"[:300]
    lay = r['candidate_layer_url']
    return [{'ref': r['ref'], 'pota_name': r['pota_name'], 'area': r['area'], 'source_url': lay, 'layer_id': lay.rstrip('/').rsplit('/', 1)[-1] if lay else '',
             'record_id': re.sub(r'^[a-z]+', '', r['record_id']) if r['verdict'] == 'SOLVED-JOIN' else '', 'key_id': r['record_id'] if r['verdict'] == 'SOLVED-JOIN' else '',
             'unit_id': '', 'unit_id_field': '', 'record_name': r['record_name'] if r['verdict'] == 'SOLVED-JOIN' else '', 'fp': '', 'status': 'PROPOSED',
             'quality_yes': '', 'approved_by': '', 'approved_date': '', 'evidence': r['evidence_urls'], 'last_checked': r['checked_at'][:10],
             'seed_from': 'pile solver', 'note': note}]


def csv_text(cols, rows):
    b = io.StringIO(); w = csv.DictWriter(b, cols, extrasaction='ignore', lineterminator='\n'); w.writeheader(); w.writerows(rows); return b.getvalue()


def write_if_changed(path, text, written):
    path = pathlib.Path(path)
    if path.exists() and path.read_text(encoding='utf-8') == text: return
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8'); written.append(str(path))


def write_outputs(root, rows, build, pile_sha):
    """All rows ever solved (this run + earlier ones) -> the area JSONs + the CSVs under data/waiting/in/data/pile-solver/."""
    out, written = pathlib.Path(root) / 'data/waiting/in/data/pile-solver', []
    by = {}
    for r in rows.values(): by.setdefault(r['area'], {})[r['ref']] = r
    for area, P in sorted(by.items()):
        old = load(out / f'{area}.json', None) or load(pathlib.Path(root) / f'data/pile-solver/{area}.json', {})
        if (old.get('parks') or {}) == P: continue   # nothing new for this area: no file, no stamp-only change
        write_if_changed(out / f'{area}.json', json.dumps({'made': now_cst(), 'build': build, 'pile_sha': pile_sha, 'solver_version': VERSION,
                                                           'parks': P}, ensure_ascii=False, indent=1, sort_keys=True) + '\n', written)
    allr = sorted(rows.values(), key=lambda r: (not r['ref'].startswith('US-'), not r['ref'].startswith('CA-'), r['ref']))
    for v, f in (('SOLVED-JOIN', 'solved-join.csv'), ('SOLVED-PIN', 'solved-pin.csv')):
        write_if_changed(out / f, csv_text(COLS, [r for r in allr if r['verdict'] == v]), written)
    write_if_changed(out / 'needs-person.csv', csv_text(COLS, [r for r in allr if r['verdict'] == 'NEEDS-PERSON' and not r.get('pattern')]), written)
    pats = []
    for pid, (_m, cause) in PATTERNS.items():
        for area in sorted({r['area'] for r in allr if r.get('pattern') == pid}):
            refs = [r['ref'] for r in allr if r.get('pattern') == pid and r['area'] == area]
            pats.append({'pattern': pid, 'area': area, 'rows': len(refs), 'verdict': 'NEEDS-PERSON', 'answer_word': 'NOT SURE', 'cause': cause,
                         'whats_missing': 'the key-builder fix, then a rebuild of this key', 'refs': ' '.join(refs)})
    write_if_changed(out / 'patterns.csv', csv_text(['pattern', 'area', 'rows', 'verdict', 'answer_word', 'cause', 'whats_missing', 'refs'], pats), written)
    for reg, pre in (('US', ('US-',)), ('CA', ('CA-',)), ('world', None)):
        sel = [x for r in allr if r['verdict'] in WORD and not r.get('pattern') and (r['ref'].startswith(pre) if pre else not r['ref'].startswith(('US-', 'CA-')))
               for x in sheet_rows(r)]
        if sel: write_if_changed(out / f'answer-sheet-proposals-{reg}.csv', csv_text(SHEET_COLS, sel), written)
    return written


def add_questions(root, rows):
    """A 'tract' question for the detective per rule-18 park (US / Canada), once per park (id pile-<ref>-tract)."""
    p = pathlib.Path(root) / 'data/detective/questions.json'
    d = load(p, {'questions': []}); have = {q.get('id') for q in d.get('questions') or []}; add = []
    for r in rows:
        if r.get('question') != 'tract' or not r['ref'].startswith(('US-', 'CA-')): continue
        qid = f"pile-{r['ref']}-tract"
        if qid in have: continue
        add.append({'id': qid, 'ref': r['ref'], 'park': r['pota_name'], 'area': r['area'], 'what': 'tract',
                    'note': f"pile solver: {r['rule18_note'] or r['reason']}"[:300], 'added': r['checked_at'][:10], 'by': f'pile solver v{VERSION}'})
    if add:
        d.setdefault('questions', []).extend(add)
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return len(add)


# ------------------------------------------------------------------ the run
def pile_path():
    if os.environ.get('PILE'): return pathlib.Path(os.environ['PILE'])
    out = pathlib.Path(os.environ.get('RUNNER_TEMP') or '/tmp') / 'kpc-precheck'
    env = dict(os.environ, OUT=str(out.resolve()), DATA=str(DATA.resolve()))
    subprocess.run([sys.executable, '.github/scripts/kpc_precheck.py'], cwd=LINKS, env=env, check=True)
    return out / 'review-pile.csv'


def run(root, pile_rows, F, areas=None, max_parks=0, mode='backfill'):
    """Solve the rows to do -> (rows by ref, stats, files written). root = where outputs go (the repo, or REPORT_ONLY's folder)."""
    root = pathlib.Path(root)
    state = load(root / 'data/pile-solver/state.json', {'version': VERSION, 'refs': {}, 'areas': {}, 'auto': False})
    if mode == 'auto' and not state.get('auto'):
        notice('automatic mode is not switched on yet (data/pile-solver/state.json auto=false): nothing to do'); return {}, {'skipped': 'auto off'}, []
    pile_sha = sha(sorted(p['h'] for p in pile_rows))
    ov, sheet = decisions()
    LAYERS.update(load(LINKS / 'data/us-key/layers.json', {}))
    pages = DET.pins() if F is not None else {}
    old = {}
    for f in list((root / 'data/pile-solver').glob('*.json')) + list((root / 'data/waiting/in/data/pile-solver').glob('*.json')):
        if f.name != 'state.json': old.update((load(f, {}).get('parks') or {}))
    todo, kept = [], {}
    for p in pile_rows:
        if areas and p['area'] not in areas: continue
        kh = sha(key_row(p['area'], p['ref']))
        s = (state['refs'] or {}).get(p['ref']) or {}
        if s.get('h') == p['h'] and s.get('k') == kh and s.get('v') == VERSION and p['ref'] in old: kept[p['ref']] = old[p['ref']]; continue
        p['kh'] = kh; p['page'] = (pages.get(p['ref']) or ('', '', '', '', ''))[4] or ''
        todo.append(p)
    todo.sort(key=lambda p: (not p['flags'] & {'BROKEN_ROW'}, p['ref']))   # grouped rows first: cheap
    if max_parks: todo = todo[:max_parks]
    stats = {'to_do': len(todo), 'kept': len(kept)}
    rows = {r: v for r, v in old.items()}
    done_now = []
    for p in todo:
        if late(): stats['left_for_next_run'] = len(todo) - len(done_now); break
        try: r = solve(p, F, ov, sheet)
        except Exception as e:  # noqa: BLE001  (one park's error never stops the run; it goes to a person)
            r = done(base_row(p), 'NEEDS-PERSON', f'the solver stopped on this park: {type(e).__name__}: {str(e)[:120]}', 'a person, or a solver fix (report it to chat 10)')
        rows[p['ref']] = r; done_now.append(r)
        state.setdefault('refs', {})[p['ref']] = {'h': p['h'], 'k': p['kh'], 'v': VERSION, 'verdict': r['verdict']}
    # rows that left the pile stay in the files (never deleted); their state line says so
    inpile = {p['ref'] for p in pile_rows}
    for ref in rows:
        if ref not in inpile and (state['refs'].get(ref) or {}).get('gone') is None: state['refs'].setdefault(ref, {})['gone'] = now_cst()[:10]
    for a in {p['area'] for p in pile_rows if not areas or p['area'] in areas}:
        left = [p for p in pile_rows if p['area'] == a and p['ref'] not in rows]
        state.setdefault('areas', {})[a] = {'rows': sum(1 for p in pile_rows if p['area'] == a), 'left': len(left)}
    written = write_outputs(root, rows, os.environ.get('KEY_BUILD') or '', pile_sha)
    nq = add_questions(root, done_now)
    if done_now or written or nq:
        state.update(version=VERSION, pile_sha=pile_sha)
        if F is not None and hasattr(F.M, 'resting'): state['hosts'] = F.M.resting()   # hosts resting after three strikes stay rested next run
        state['last'] = {'when': now_cst(), 'solved': len(done_now), 'questions_added': nq, 'fetches': F.n if F else 0,
                         'skipped_urls': (F.skipped if F else [])[:50]}
        sp = root / 'data/pile-solver/state.json'; sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8'); written.append(str(sp))
    import collections
    stats.update(solved=len(done_now), questions_added=nq, by_verdict=dict(collections.Counter(r['verdict'] for r in done_now)),
                 fetches=F.n if F else 0, skipped_urls=len(F.skipped) if F else 0)
    return rows, stats, written


def run_log(rows, stats, areas):
    sel = [r for r in rows.values() if not areas or r['area'] in areas]
    L = [f"# Pile solver run log ({now_cst()}, v{VERSION})", '', f"Areas: {' '.join(sorted(areas)) if areas else 'all'} · {json.dumps(stats)}", '',
         '| ref | park | verdict | flag | distance m | record | reason | what is missing |', '|---|---|---|---|---|---|---|---|']
    for r in sorted(sel, key=lambda r: r['ref']):
        L.append('| ' + ' | '.join(str(x).replace('|', '/') for x in (r['ref'], r['pota_name'], r['verdict'], r['pin_flag'], r['distance_m'],
                                                                          f"{r['record_id']} {r['record_name']}", r['reason'][:200], r['whats_missing'][:160])) + ' |')
    return '\n'.join(L) + '\n'


def main():
    mode = (os.environ.get('MODE') or 'backfill').lower()
    areas = set((os.environ.get('AREAS') or '').upper().split())
    root = pathlib.Path(os.environ.get('OUT_DIR') or '.') if os.environ.get('REPORT_ONLY') == '1' else DATA
    pile = read_pile(pile_path()) + read_dropped(None)
    st = load(DATA / 'data/pile-solver/state.json', {})
    if mode == 'auto' and st.get('pile_sha') == sha(sorted(p['h'] for p in pile)) and st.get('version') == VERSION:
        notice('the pile has not changed since the last run: nothing to do'); return
    M = kpc_manners.Manners('pile solver (review-pile verdict proposals)', st.get('hosts'))
    F = Fetch(M, os.environ.get('FREEZE') or None)
    rows, stats, written = run(root, pile, F, areas or None, int(os.environ.get('MAX_PARKS') or 0), mode)
    log = run_log(rows, stats, areas)
    if written or os.environ.get('REPORT_ONLY') == '1':
        p = pathlib.Path(root) / 'data/waiting/in/data/pile-solver/run-log.md'; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(log, encoding='utf-8')
    if M.for_person: notice(f'{len(M.for_person)} URL(s) for a person: ' + '; '.join(f'{u} ({w})' for u, w in M.for_person[:5]))
    notice(f"{stats} · files: {len(written)} · manners {M.stat}")
    print(log)


# ------------------------------------------------------------------ selftest (offline)
def selftest():
    import shutil, tempfile, urllib.request
    fx = HERE.parent.parent / 'tests/fixtures/pile_solver'
    FX = load(fx / 'cases.json', {})
    ok, out = True, []

    def check(name, got, want):
        nonlocal ok
        good = got == want; ok &= good; out.append(f"{'PASS' if good else 'FAIL'}  {name}: got {got!r}" + ('' if good else f', want {want!r}'))

    # rule 18 / names, with no network at all
    check('Langres Nord vs Langres (secteur Nord): pile', bool(rule18('Langres Nord', 'Langres (secteur Nord)')), True)
    check('Lac Nord-Est vs Lac Nord: pile', bool(rule18('Lac Nord-Est', 'Lac Nord')), True)
    check('Cabin Creek WMA (Lewis County) vs Cabin Creek WMA: no rule-18 flag', rule18('Cabin Creek WMA (Lewis County)', 'Cabin Creek WMA'), '')
    check('Cabin Creek: same place by name', same_name('Cabin Creek WMA (Lewis County)', 'Cabin Creek WMA'), 'same')
    # answer counting (rule 10)
    check('a Quality YES does not count', answer_counts({'approved_by': 'chat 11 (Quality)', 'approved_date': '2026-11-03'}), False)
    check('Brandon before 9:37 AM Nov 2 does not count', answer_counts({'approved_by': 'Brandon', 'approved_date': '2026-11-02', 'note': '8:15 AM CST'}), False)
    check('Brandon Nov 2 with no time does not count', answer_counts({'approved_by': 'KZ4CP', 'approved_date': '2026-11-02'}), False)
    check('Brandon Nov 1 does not count', answer_counts({'approved_by': 'Brandon', 'approved_date': '2026-11-01'}), False)
    check('Brandon 9:40 AM Nov 2 counts', answer_counts({'approved_by': 'Brandon', 'approved_date': '2026-11-02', 'note': '9:40 AM CST'}), True)
    check('KZ4CP Nov 3 counts', answer_counts({'approved_by': 'KZ4CP', 'approved_date': '2026-11-03'}), True)
    check('distance: inside a square = 0', dist_m(0.5, 0.5, [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]), 0)
    check('distance: 0.01 deg east of the edge ~ 1113 m', dist_m(0.5, 1.01, [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]) in range(1100, 1125), True)

    # whole cases from frozen pile rows, key rows, sheet rows and fetched answers
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='pile-solver-test-'))
    real_open = urllib.request.urlopen

    def no_net(*a, **k): raise AssertionError('a fetch went around kpc_manners')
    urllib.request.urlopen = no_net
    try:
        for case in FX.get('cases') or []:
            KEYS.clear(); LAYERS.clear(); LAYERS.update(FX.get('layers') or {})
            KEYS[str(LINKS / f"data/us-key/{case['pile']['area']}.json")] = {'parks': {case['pile']['park']: case.get('key') or {}}}
            KEYS[str(DATA / f"data/world-key/{case['pile']['area']}.json")] = {'parks': {case['pile']['park']: case.get('key') or {}}}
            c = case['pile']
            p = {'ref': c['park'], 'area': c['area'], 'areas': c['area'], 'name': c['name'], 'type': c['type'], 'flags': set(c['flags'].split()),
                 'why': c['why'], 'ids': c['ids'], 'lat': c['lat'], 'lon': c['lon'], 'action': c['action'], 'src': 'pile', 'h': 'x', 'page': ''}
            FM = FixtureManners(FX.get('responses') or {})
            F = Fetch(FM) if case.get('online', True) else None
            ov = {c['park']: case['override']} if case.get('override') else {}
            sheet = {c['park']: case['sheet']} if case.get('sheet') else {}
            r = solve(p, F, ov, sheet)
            check(case['name'], (r['verdict'], r['pin_flag'], bool(r['whats_missing']) if r['verdict'] == 'NEEDS-PERSON' else True),
                  (case['want'], case.get('want_flag', ''), True))
            if case.get('never_join_on'): check(case['name'] + ': never SOLVED-JOIN on ' + case['never_join_on'],
                                                r['verdict'] == 'SOLVED-JOIN' and r['record_id'] == case['never_join_on'], False)
        # a whole run twice: the second run writes nothing; nothing is deleted; nothing outside the allowed paths
        KEYS.clear()
        pile = [dict(p, flags=set(p['flags'].split()), h=sha(p), areas=p['area'], ids=p['ids'], src='pile', ref=p['park'], lat=p['lat'], lon=p['lon'])
                for p in [c['pile'] for c in FX['cases'] if not c.get('online', True)]]
        for c in FX['cases']:
            KEYS[str(LINKS / f"data/us-key/{c['pile']['area']}.json")] = {'parks': {c['pile']['park']: c.get('key') or {}}}
        (tmp / 'data/detective').mkdir(parents=True); (tmp / 'data/detective/questions.json').write_text('{"questions": []}')
        before = {str(x) for x in tmp.rglob('*') if x.is_file()}
        LAYERS.update(FX.get('layers') or {})
        _r1, s1, w1 = run(tmp, pile, None)
        _r2, s2, w2 = run(tmp, pile, None)
        after = {str(x) for x in tmp.rglob('*') if x.is_file()}
        check('first run writes files', bool(w1), True)
        check('second run with no change writes nothing', w2, [])
        check('no file deleted', before - after, set())
        allowed = (str(tmp / 'data/waiting/in/data/pile-solver') + '/', str(tmp / 'data/pile-solver/state.json'), str(tmp / 'data/detective/questions.json'))
        check('writes only to the allowed paths', sorted(f for f in after if not f.startswith(allowed) and f != allowed[1] and f != allowed[2]), [])
        hdr = (tmp / 'data/waiting/in/data/pile-solver/needs-person.csv').read_text().splitlines()[0]
        check('needs-person.csv has the handoff columns in order', hdr, ','.join(COLS))
        check('the grouped finding is in patterns.csv', 'P1-no-record-id' in (tmp / 'data/waiting/in/data/pile-solver/patterns.csv').read_text(), True)
        refs = {p['ref'] for p in pile}
        check('every pile park has exactly one verdict (counts add up)', (set(_r1) == refs, all(v['verdict'] in ('SOLVED-JOIN', 'SOLVED-PIN', 'NEEDS-PERSON', 'UNTOUCHED') for v in _r1.values())), (True, True))
        # US-13614 has an overrides.json join (sgneb161, chat 11 YES applied Nov 2) on main: decided, so untouched in a real run
        check('KEEP, ASK BRANDON and override rows untouched', sorted(r for r, v in _r1.items() if v['verdict'] == 'UNTOUCHED'), ['CA-2218', 'US-10972', 'US-13614'])
    finally:
        urllib.request.urlopen = real_open
        shutil.rmtree(tmp, ignore_errors=True)
    # every fetch goes through kpc_manners: no urllib / requests / curl in this file's code outside the selftest guard
    src = pathlib.Path(__file__).read_text(encoding='utf-8').split('\ndef selftest():')[0]
    check('no direct web reads in the solver code', bool(re.search(r'urlopen|requests\.|http\.client|subprocess\.run\(\[.curl', src)), False)
    print('\n'.join(out))
    print('SELFTEST ' + ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    try: main()
    except Exception as e:  # noqa: BLE001  (a crash must not look like a clean run, and must not save half a result)
        import traceback; traceback.print_exc()
        print(f'::error title=Pile solver::stopped: {type(e).__name__}: {str(e)[:300]}'); sys.exit(1)
