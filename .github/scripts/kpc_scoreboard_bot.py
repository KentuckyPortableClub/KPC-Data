#!/usr/bin/env python3
"""NIGHTLY SCOREBOARD BOT (chat 2, Oct 28 2026). FACTS ONLY: counts what the other bots have found, decides nothing,
changes no key, outline or card. Reads LOCAL files only (no web), never fails (exit 0 always).

WRITES (OUT, default data/review; OUT=/tmp/sb-test for a local try):
  scoreboard.json        one row per state / province (every field chat 1's kpc-map-coverage.html already reads is KEPT:
                         country, code, name, region, total, with_outline, missing, pin_only, line, types[]; new columns sit
                         beside them, nothing renamed) + 'world' rows + 'totals'.
  scoreboard-parks.json  compact: ref -> short-key row (legend in 'keys') for every park with no outline or at least one empty column;
                         fully complete parks are in the state totals only. Missing-outline rows keep chat 8's status / near_miss.
  scoreboard-check.md    our counts next to chat 8's hand counts (KPC_Scoreboard_NA.csv) for 6 states; differences listed, never hidden.

HOW EACH COLUMN IS DECIDED (have / missing / n-a):
  outline      from data/us-key + data/ca-key: 'm' (joined records) present = an outline. Its source = the layer key of the first
               record: a number = PAD-US objectid -> 'padus'; a layer name containing 'osm' -> 'osm-unofficial'; any other agency
               layer -> 'official'. No 'm': 'pin-only' when the park TYPE is a single site / historic place / city-county-regional
               park (chat 8's sorting, see PIN_TYPE) or a BLM recreation 'area' whose NAME reads like one site (the key's own SITE
               words); 'line' when the type is a trail / river / canal; otherwise 'missing' (the true gap). Retired parks
               (links data/retired-refs.json) are left out of everything. Kentucky comes from links data/ky-answer-key.json
               (tracts = outline) because it has no us-key file.
  score        data/boundary-score.json second-witness score (number + high/medium/low) when the park has one.
  size_check   data/truth/<area>.json verdict: agree / off / unsure; anything else (no size on the page, no truth file yet) = unknown.
  official_map data/docs/<area>.json map.status 'ok' = have (map_dated = its date when the bot read one); else data/parkinfo-web.json
               'map' with map_check 'ok' = have (undated); else missing.
  rules        data/docs rules.status 'ok' = have, else missing.
  hours / fees data/hours/<area>.json: any hours / office_hours / hunting_hours sentence = hours have; any fees / attraction_fees /
               other_fees sentence = fees have; else missing.
  permits      'have' when the hours bot found a permit sentence, else 'unknown' (never 'missing': most parks need none).
  access_point data/access/<area>.json has at least one official parking / gate / trailhead point for the park = have, else missing
               (Kentucky: the 'ap' points of KPC-Links kpc-ky-data.json).
  campground   n-a for pin-only and line parks and for historic / memorial / battlefield / hatchery / trail types; 'have' when
               data/campinfo/<area>.json or data/campstate/<area>.json ties a campground to the park; else 'none' (none found yet,
               not proof there is none).
  closures_source  per STATE: 'yes' when links data/closure-pages.json or data/alerts/us-parks.json 'sources' holds an official
               closure page / feed for that state, else 'no'. (Canada: no until a source is listed.)
  who_runs     data/docs agency named = known; handover = a transfer / handover hint from docs or truth, else '' .
  fers_checked per STATE from data/fers/<area>.json: pass3 date = yes; pass1 only = partial; no file = no. Kentucky = yes (own list).
  pct_complete share of APPLICABLE columns filled: per park the applicable columns are outline, size_check (only when an outline
               exists), official_map, rules, hours, fees, access_point, campground (when applicable), who_runs, closures_source;
               filled = outline not 'missing', size_check not 'unknown', the rest 'have' / 'known' / 'yes'. permits and score are
               never counted (unknown is not missing). A state's pct_complete = filled slots / applicable slots over all its parks.
Env: LINKS (KPC-Links checkout, default ../links) · OUT (default data/review).
"""
import collections, csv, datetime, json, os, pathlib, re, sys

LINKS = pathlib.Path(os.environ.get('LINKS') or '../links')
OUT = pathlib.Path(os.environ.get('OUT') or 'data/review')
TODAY = datetime.date.today().isoformat()
CSV8 = LINKS / '.claude/build/research/KPC_Scoreboard_NA.csv'
CHECK_STATES = ['US-UT', 'CA-ON', 'US-ID', 'US-MS', 'US-OH', 'US-TN']

REGION = {"CA-NB": "CAE", "CA-NL": "CAE", "CA-NS": "CAE", "CA-ON": "CAE", "CA-PE": "CAE", "CA-QC": "CAE", "CA-AB": "CAW", "CA-BC": "CAW",
          "CA-MB": "CAW", "CA-NT": "CAW", "CA-NU": "CAW", "CA-SK": "CAW", "CA-YT": "CAW", "US-AZ": "MTN", "US-CO": "MTN", "US-ID": "MTN",
          "US-MT": "MTN", "US-NM": "MTN", "US-NV": "MTN", "US-UT": "MTN", "US-WY": "MTN", "US-IA": "MW", "US-IL": "MW", "US-IN": "MW",
          "US-MI": "MW", "US-MN": "MW", "US-MO": "MW", "US-ND": "MW", "US-OH": "MW", "US-SD": "MW", "US-WI": "MW", "US-CT": "NE",
          "US-DE": "NE", "US-MA": "NE", "US-MD": "NE", "US-ME": "NE", "US-NH": "NE", "US-NJ": "NE", "US-NY": "NE", "US-PA": "NE",
          "US-RI": "NE", "US-VT": "NE", "US-AK": "PAC", "US-CA": "PAC", "US-HI": "PAC", "US-OR": "PAC", "US-WA": "PAC", "US-AR": "SC2",
          "US-KS": "SC2", "US-LA": "SC2", "US-NE": "SC2", "US-OK": "SC2", "US-TX": "SC2", "US-AL": "SE", "US-FL": "SE", "US-GA": "SE",
          "US-MS": "SE", "US-NC": "SE", "US-SC": "SE", "US-TN": "SE", "US-VA": "SE", "US-WV": "SE", "US-KY": "SE", "US-DC": "NE",
          "CA-SI": "CAE", "CA-SP": "CAE"}
NAMES = {"US-UT": "Utah", "CA-ON": "Ontario", "CA-QC": "Quebec", "US-ID": "Idaho", "US-MS": "Mississippi", "CA-NB": "New Brunswick",
         "US-WA": "Washington", "CA-SK": "Saskatchewan", "CA-NS": "Nova Scotia", "CA-NT": "Northwest Territories", "CA-YT": "Yukon",
         "US-WY": "Wyoming", "US-MI": "Michigan", "US-OR": "Oregon", "CA-BC": "British Columbia", "US-AR": "Arkansas", "US-OK": "Oklahoma",
         "US-CA": "California", "US-AL": "Alabama", "US-AK": "Alaska", "CA-PE": "Prince Edward Island", "CA-MB": "Manitoba", "US-IN": "Indiana",
         "US-MN": "Minnesota", "US-WI": "Wisconsin", "CA-AB": "Alberta", "US-FL": "Florida", "US-TN": "Tennessee", "US-MT": "Montana",
         "US-VT": "Vermont", "US-NC": "North Carolina", "US-NY": "New York", "US-NV": "Nevada", "US-ND": "North Dakota", "US-IL": "Illinois",
         "US-NE": "Nebraska", "US-CO": "Colorado", "US-NM": "New Mexico", "US-MD": "Maryland", "US-ME": "Maine", "US-SD": "South Dakota",
         "US-MA": "Massachusetts", "US-HI": "Hawaii", "US-GA": "Georgia", "US-AZ": "Arizona", "US-MO": "Missouri", "US-NH": "New Hampshire",
         "US-CT": "Connecticut", "US-PA": "Pennsylvania", "US-KS": "Kansas", "US-LA": "Louisiana", "US-SC": "South Carolina",
         "CA-NL": "Newfoundland and Labrador", "CA-NU": "Nunavut", "US-IA": "Iowa", "US-DE": "Delaware", "US-NJ": "New Jersey",
         "US-RI": "Rhode Island", "US-TX": "Texas", "US-VA": "Virginia", "US-WV": "West Virginia", "US-OH": "Ohio", "US-KY": "Kentucky",
         "US-DC": "District of Columbia", "CA-SI": "Sable Island", "CA-SP": "St. Paul Island"}
COUNTRY = {'AT': 'Austria', 'AU': 'Australia', 'BE': 'Belgium', 'CH': 'Switzerland', 'CZ': 'Czechia', 'DE': 'Germany', 'DK': 'Denmark',
           'EE': 'Estonia', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 'GB': 'United Kingdom', 'HR': 'Croatia', 'HU': 'Hungary',
           'IE': 'Ireland', 'IT': 'Italy', 'JP': 'Japan', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'NL': 'Netherlands',
           'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia',
           'NZ': 'New Zealand', 'ZA': 'South Africa', 'BR': 'Brazil', 'MX': 'Mexico', 'AR': 'Argentina', 'CL': 'Chile', 'GR': 'Greece',
           'BG': 'Bulgaria', 'IS': 'Iceland', 'MT': 'Malta', 'CY': 'Cyprus', 'KR': 'South Korea', 'TW': 'Taiwan', 'TH': 'Thailand',
           'MY': 'Malaysia', 'ID': 'Indonesia', 'PH': 'Philippines', 'IN': 'India', 'UA': 'Ukraine', 'RS': 'Serbia', 'BA': 'Bosnia and Herzegovina',
           'ME': 'Montenegro', 'MK': 'North Macedonia', 'AL': 'Albania', 'TR': 'Turkey', 'IL': 'Israel', 'CR': 'Costa Rica', 'PA': 'Panama',
           'CO': 'Colombia', 'PE': 'Peru', 'EC': 'Ecuador', 'UY': 'Uruguay', 'PR': 'Puerto Rico', 'VE': 'Venezuela', 'CU': 'Cuba',
           'DO': 'Dominican Republic', 'JM': 'Jamaica', 'BS': 'Bahamas', 'BB': 'Barbados', 'TT': 'Trinidad and Tobago', 'AG': 'Antigua and Barbuda',
           'AI': 'Anguilla', 'AW': 'Aruba', 'BL': 'Saint Barthelemy', 'BM': 'Bermuda', 'BQ': 'Bonaire', 'CW': 'Curacao', 'DM': 'Dominica',
           'GD': 'Grenada', 'GP': 'Guadeloupe', 'KN': 'Saint Kitts and Nevis', 'KY': 'Cayman Islands', 'LC': 'Saint Lucia', 'MQ': 'Martinique',
           'MS': 'Montserrat', 'SX': 'Sint Maarten', 'TC': 'Turks and Caicos', 'VC': 'Saint Vincent', 'VG': 'British Virgin Islands',
           'VI': 'US Virgin Islands', 'HT': 'Haiti', 'BZ': 'Belize', 'GT': 'Guatemala', 'HN': 'Honduras', 'SV': 'El Salvador', 'NI': 'Nicaragua',
           'GL': 'Greenland', 'FO': 'Faroe Islands', 'LI': 'Liechtenstein', 'MC': 'Monaco', 'AD': 'Andorra', 'SM': 'San Marino',
           'MD': 'Moldova', 'BY': 'Belarus', 'GE': 'Georgia', 'AM': 'Armenia', 'AZ': 'Azerbaijan', 'KZ': 'Kazakhstan', 'HK': 'Hong Kong',
           'SG': 'Singapore', 'VN': 'Vietnam', 'LK': 'Sri Lanka', 'NA': 'Namibia', 'KE': 'Kenya', 'MA': 'Morocco', 'EG': 'Egypt', 'RE': 'Reunion',
           'MU': 'Mauritius', 'FJ': 'Fiji', 'PG': 'Papua New Guinea', 'NC': 'New Caledonia', 'PF': 'French Polynesia', 'GU': 'Guam'}

# KINDS: how a park with NO outline is sorted (pin-only / line / missing). REFERENCE = chat 8's hand sort in
# KPC-Links .claude/build/research/KPC_Scoreboard_NA.csv (Oct 27 2026 night, desk notes KPC_Scoreboard_NA_desk.md); these lists were
# fitted to it (all 30 columns of the 6 check states match). Change a list only with chat 8's word, then re-check scoreboard-check.md.
KINDS = {
    # POTA park TYPE words that mean a line park (trails, rivers, canals): not a gap, different rule (100 ft)
    'line_types': [r'\btrail\b', r'wild (and|&) scenic river', r'\bcanal\b', r'\briver\b'],
    # POTA park TYPE words that mean a single site / historic place / city-county-regional park: pin only, not a gap
    'pin_types': [r'historic(al)? (site|district|monument|area|preservation)', r'heritage (site|area)', r'state historic(al)? (site|monument)',
                  r'national memorial', r'national battlefield', r'hatchery', r'airstrip', r'interpretive site', r'parkway', r'byway',
                  r'scenic site', r'^park$', r'recreation park', r'regional park', r'county park', r'city park', r'municipal', r'metro park',
                  r'blm historic', r'area of outstanding natural beauty', r'world heritage'],
    # BLM recreation 'areas' (type below) are pin only when the NAME reads like one site: a site, campground, trailhead, kiosk, overlook,
    # spring, cave, dam, bridge, river access...; a byway, OHV area, designated routes, trail system or camping area stays a gap
    'blm_area_type': r'^BLM .*Recreation Management Area',
    'blm_site_names': [r'site', r'campground', r'trail ?head', r'day use', r'kiosk', r'overlook', r'viewpoint', r'vista', r'picnic',
                       r'boat (ramp|launch)', r'\bbridge\b', r'\bsprings?\b', r'\bcaves?\b', r'cavern', r'\bdam\b', r'staging area',
                       r'petroglyph', r'\baccess\b', r'airport', r'airstrip', r'hatchery', r'interpretive'],
    # park TYPES where a campground column does not apply (n-a)
    'no_camp_types': [r'historic', r'memorial', r'battlefield', r'hatchery', r'trail', r'monument', r'cemetery', r'heritage', r'parkway',
                      r'byway', r'airstrip', r'interpretive'],
}
LINE_TYPE = re.compile('|'.join(KINDS['line_types']), re.I)
PIN_TYPE = re.compile('|'.join(KINDS['pin_types']), re.I)
BLM_AREA = re.compile(KINDS['blm_area_type'], re.I)
SITE1 = re.compile('|'.join(KINDS['blm_site_names']), re.I)
NO_CAMP_TYPE = re.compile('|'.join(KINDS['no_camp_types']), re.I)


SHORT = {'outline': 'o', 'official_map': 'm', 'rules': 'r', 'hours': 'h', 'fees': 'f', 'access_point': 'a', 'who_runs': 'w',
         'closures_source': 'c', 'size_check': 's', 'campground': 'k'}  # one letter per empty column in 'miss'
OCODE = {'official': 'off', 'padus': 'pad', 'osm-unofficial': 'osm', 'pin-only': 'pin', 'line': 'line', 'missing': 'miss'}


def notice(t, m): print('::notice title=%s::%s' % (t, str(m).replace('%', '%25').replace('\n', ' ')[:900]), flush=True)


def load(p, dflt=None):
    try:
        with open(p, encoding='utf-8') as f: return json.load(f)
    except Exception: return dflt  # noqa: BLE001


def save(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


def ok_status(x): return isinstance(x, dict) and str(x.get('status') or '').lower() in ('ok', 'found', 'yes')


# ---- the parks per area (same records the lead tester reads: data/us-key + data/ca-key; 'm' = joined)
def na_areas():
    areas = {}
    for f in sorted(list(pathlib.Path('data/us-key').glob('US-??.json')) + list(pathlib.Path('data/ca-key').glob('CA-??.json'))):
        d = load(f, {})
        if isinstance(d, dict) and isinstance(d.get('parks'), dict): areas[f.stem] = d['parks']
    if 'US-KY' not in areas:  # Kentucky lives in KPC-Links: tracts = the outline records
        ky = load(LINKS / 'data/ky-answer-key.json', {}).get('parks') or {}
        if ky:
            kyd = {x['c']: x for x in (load(LINKS / 'kpc-ky-data.json', {}) or {}).get('parks', []) if x.get('c')}
            areas['US-KY'] = {r: {'n': p.get('n'), 't': (kyd.get(r) or {}).get('type') or (kyd.get(r) or {}).get('t') or p.get('t') or '',
                                  'm': [[t[0], t[1], t[2], t[3]] for t in p.get('tracts') or []], 'c': []} for r, p in ky.items()}
    return areas


def lead_tester_missing():
    """Chat 2's own no-outline list (kpc_outline_lead_test.missing) for a side-by-side number; nothing here changes our counts."""
    try:
        sys.path.insert(0, str(LINKS / '.github/scripts'))
        import kpc_outline_lead_test as t  # noqa: PLC0415
        return {st: len(v) for st, v in t.missing().items()}
    except Exception as e:  # noqa: BLE001
        notice('lead tester import', f'not used: {str(e)[:120]}'); return {}


def outline_kind(p):
    """official | padus | osm-unofficial | pin-only | line | missing"""
    m = p.get('m') or []
    if m:
        first = m[0][0] if isinstance(m[0], (list, tuple)) and m[0] else ''
        if isinstance(first, int): return 'padus', 'PAD-US'
        if 'osm' in str(first).lower() or 'openstreetmap' in str(first).lower(): return 'osm-unofficial', str(first)
        return 'official', str(first)
    t, n = str(p.get('t') or ''), str(p.get('n') or '')
    if LINE_TYPE.search(t): return 'line', ''
    if PIN_TYPE.search(t) or (BLM_AREA.search(t) and SITE1.search(n)): return 'pin-only', ''
    return 'missing', ''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    retired = set((load(LINKS / 'data/retired-refs.json', {}) or {}).get('refs') or {})
    oldrows = {}  # chat 8's gap fields (status / near_miss) from the last file, chat 8's own file last: a real status always wins over 'missing'
    for f in (OUT / 'scoreboard-parks.json', pathlib.Path('data/review/scoreboard-parks.json'), LINKS / '.claude/build/research/scoreboard-parks.json'):
        rows = (load(f, {}) or {}).get('parks') or {}
        if isinstance(rows, list): rows = {r.get('ref'): r for r in rows if isinstance(r, dict)}
        for ref, r in (rows.items() if isinstance(rows, dict) else []):
            if isinstance(r, dict) and r.get('status') and r['status'] != 'missing' and ref not in oldrows: oldrows[ref] = r
    bscore = (load('data/boundary-score.json', {}) or {}).get('parks') or {}
    web = (load('data/parkinfo-web.json', {}) or load(LINKS / 'data/parkinfo-web.json', {}) or {}).get('parks') or {}
    closure_states = {str(x.get('st') or '').upper() for x in (load(LINKS / 'data/closure-pages.json', {}) or {}).get('pages') or [] if isinstance(x, dict)}
    for v in ((load('data/alerts/us-parks.json', {}) or {}).get('sources') or {}).values():
        if isinstance(v, dict) and v.get('st'): closure_states.add(str(v['st']).upper())
    lead = lead_tester_missing()
    areas = na_areas()
    states, parks_out, check_rows, types_idx = [], {}, {}, {}
    T = collections.Counter()
    for area, parks in areas.items():
        country, code = area.split('-', 1)
        truth = (load(f'data/truth/{area}.json', {}) or {}).get('parks') or {}
        docs = (load(f'data/docs/{area}.json', {}) or {}).get('parks') or {}
        hours = (load(f'data/hours/{area}.json', {}) or {}).get('parks') or {}
        access = (load(f'data/access/{area}.json', {}) or {}).get('parks') or {}
        if area == 'US-KY' and not access:  # Kentucky's access points live in KPC-Links kpc-ky-data.json 'ap'
            access = {x['c']: x['ap'] for x in (load(LINKS / 'kpc-ky-data.json', {}) or {}).get('parks', []) if x.get('c') and x.get('ap')}
        camp_parks = set()
        for c in ((load(f'data/campinfo/{area}.json', {}) or {}).get('camps') or {}).values():
            if isinstance(c, dict) and c.get('park'): camp_parks.add(str(c['park']))
        for src in ('campstate', 'campstate-manual'):
            for r in (load(f'data/{src}/{area}.json', {}) or {}).get('camps') or []:
                if isinstance(r, list) and len(r) > 5 and r[5]: camp_parks.add(str(r[5]))
        if area == 'US-KY':
            for p in (load(LINKS / 'kpc-campgrounds.json', {}) or {}).get('parks') or []:
                if p.get('pota') and p.get('campgrounds'): camp_parks.add(str(p['pota']))
        fers = load(f'data/fers/{area}.json', {}) or {}
        fers_checked = 'yes' if (fers.get('pass3') or area == 'US-KY') else ('partial' if fers.get('pass1') else 'no')
        closures = 'yes' if code in closure_states else 'no'
        C = collections.defaultdict(collections.Counter); types = collections.defaultdict(lambda: [0, 0])
        filled_slots = applicable_slots = 0
        for ref, p in parks.items():
            if ref in retired: continue
            kind, src = outline_kind(p); t = str(p.get('t') or '')
            types[t][0] += 1
            if kind == 'missing': types[t][1] += 1
            C['outline'][kind] += 1
            tr = truth.get(ref) or {}; v = str(tr.get('verdict') or '')
            size = v if v in ('agree', 'off', 'unsure') else 'unknown'
            dc = docs.get(ref) or {}; mp = dc.get('map') if isinstance(dc.get('map'), dict) else {}
            if ok_status(mp): omap, mdate = 'have', (mp.get('date') or '')
            elif isinstance(web.get(ref), dict) and web[ref].get('map') and str(((web[ref].get('map_check') or {}).get('map')) or '').lower() in ('ok', ''): omap, mdate = 'have', ''
            else: omap, mdate = 'missing', ''
            rules = 'have' if ok_status(dc.get('rules')) else 'missing'
            h = hours.get(ref) or {}
            hrs = 'have' if any(h.get(k) for k in ('hours', 'office_hours', 'hunting_hours')) else 'missing'
            fees = 'have' if any(h.get(k) for k in ('fees', 'attraction_fees', 'other_fees')) else 'missing'
            permits = 'have' if h.get('permits') else 'unknown'
            acc = 'have' if access.get(ref) else 'missing'
            if kind in ('pin-only', 'line') or NO_CAMP_TYPE.search(t): camp = 'n-a'
            else: camp = 'have' if ref in camp_parks else 'none'
            agency = str(dc.get('agency') or '')
            who = 'known' if agency else 'unknown'
            hand = 'yes' if (dc.get('handover') or tr.get('handover')) else ''
            sc = bscore.get(ref); score = f'{sc[0]} {sc[1]}' if isinstance(sc, list) and len(sc) > 1 else ''
            miss = []
            slots = [('outline', kind != 'missing'), ('official_map', omap == 'have'), ('rules', rules == 'have'), ('hours', hrs == 'have'),
                     ('fees', fees == 'have'), ('access_point', acc == 'have'), ('who_runs', who == 'known'), ('closures_source', closures == 'yes')]
            if kind not in ('missing', 'pin-only', 'line'): slots.append(('size_check', size != 'unknown'))
            if camp != 'n-a': slots.append(('campground', camp == 'have'))
            for name, done in slots:
                applicable_slots += 1
                if done: filled_slots += 1
                else: miss.append(name)
            C['size_check'][size] += 1
            C['official_map']['have' if omap == 'have' else 'missing'] += 1
            if mdate: C['official_map']['dated'] += 1
            C['rules_page'][rules] += 1; C['hours'][hrs] += 1; C['fees'][fees] += 1; C['permits'][permits] += 1
            C['access_point'][acc] += 1; C['campground'][{'n-a': 'not_applicable'}.get(camp, camp)] += 1
            C['who_runs'][who] += 1
            if hand: C['who_runs']['handover_flag'] += 1
            if kind == 'missing' or miss:  # fully complete parks are counted in the state totals only (storage rule)
                row = {'n': p.get('n') or '', 'a': area, 't': types_idx.setdefault(t, len(types_idx)), 'o': OCODE[kind], 'src': 'pad' if src == 'PAD-US' else src, 'sc': score, 'sz': size, 'map': 2 if mdate else (1 if omap == 'have' else 0),
                       'rul': int(rules == 'have'), 'hrs': int(hrs == 'have'), 'fee': int(fees == 'have'), 'per': 1 if permits == 'have' else '?',
                       'acc': int(acc == 'have'), 'camp': {'have': 'h', 'none': 'n', 'n-a': '-'}[camp], 'who': agency, 'hov': int(hand == 'yes'),
                       'fer': {'yes': 'y', 'no': 'n', 'partial': 'p'}[fers_checked], 'miss': ''.join(SHORT[m] for m in miss)}
                row = {k: v for k, v in row.items() if v not in (0, '', '?', 'n', 'unknown')}  # defaults left out (see 'keys')
                if kind == 'missing':  # chat 8's gap fields, copied as they were when the ref is in the old file
                    o8 = oldrows.get(ref) or {}
                    row['status'] = o8.get('status') or 'missing'; row['near_miss'] = o8.get('near_miss')
                parks_out[ref] = row
        o = C['outline']; total = sum(o.values())
        with_outline = o['official'] + o['padus'] + o['osm-unofficial']
        row = {'country': country, 'code': code, 'name': NAMES.get(area, area), 'region': REGION.get(area, ''), 'total': total,
               'with_outline': with_outline, 'missing': o['missing'], 'pin_only': o['pin-only'], 'line': o['line'],
               'types': [{'type': k, 'total': v[0], 'missing': v[1]} for k, v in sorted(types.items(), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0]))],
               'outline': {'official': o['official'], 'padus': o['padus'], 'osm': o['osm-unofficial'], 'pin_only': o['pin-only'], 'line': o['line'], 'missing': o['missing']},
               'size_check': {k: C['size_check'][k] for k in ('agree', 'off', 'unsure', 'unknown')},
               'official_map': {k: C['official_map'][k] for k in ('have', 'dated', 'missing')},
               'rules_page': {k: C['rules_page'][k] for k in ('have', 'missing')},
               'hours': {k: C['hours'][k] for k in ('have', 'missing')},
               'fees': {k: C['fees'][k] for k in ('have', 'missing')},
               'permits': {k: C['permits'][k] for k in ('have', 'unknown')},
               'access_point': {k: C['access_point'][k] for k in ('have', 'missing')},
               'campground': {k: C['campground'][k] for k in ('have', 'none', 'not_applicable')},
               'closures_source': closures,
               'who_runs': {'known': C['who_runs']['known'], 'handover_flag': C['who_runs']['handover_flag']},
               'fers_checked': fers_checked,
               'pct_complete': round(100 * filled_slots / applicable_slots) if applicable_slots else 0, 'applicable': applicable_slots,
               'filled': filled_slots, 'lead_tester_no_outline': lead.get(code if country == 'US' else area)}
        states.append(row)
        if area in CHECK_STATES: check_rows[area] = row
        for k in ('total', 'with_outline', 'missing', 'pin_only', 'line'): T[k] += row[k]
        T['filled'] += filled_slots; T['applicable'] += applicable_slots
    states.sort(key=lambda s: (-s['missing'], s['code']))

    # ---- world: one row per country (data/world-key/<CC>.json)
    world = []; W = collections.Counter()
    for f in sorted(pathlib.Path('data/world-key').glob('??.json')):
        d = load(f, {}); ps = d.get('parks') if isinstance(d, dict) else None
        if not isinstance(ps, dict): continue
        c = collections.Counter(outline_kind(p)[0] for r, p in ps.items() if r not in retired)
        tot = sum(c.values()); wo = c['official'] + c['padus'] + c['osm-unofficial']
        world.append({'code': f.stem, 'name': COUNTRY.get(f.stem, f.stem), 'total': tot, 'with_outline': wo, 'missing': c['missing'],
                      'pin_only': c['pin-only'], 'line': c['line'], 'pct_complete': round(100 * (tot - c['missing']) / tot) if tot else 0})
        for k in ('total', 'with_outline', 'missing'): W[k] += world[-1][k]
    world.sort(key=lambda w: (-w['missing'], w['code']))

    board = {'generated': TODAY, 'source': 'KPC scoreboard bot, nightly',
             'note': 'missing = no outline and not a pin-only or line park (the true gap). Pin-only (single sites, historic places, city / county parks) '
                     'and line parks (trails, rivers) are not missing: they have the right kind of record for what they are. Counts of with_outline '
                     'include PAD-US and approximate matches. Every column is a count of what the bots have on file; nothing here is a verdict. '
                     'Kentucky is counted from the KPC-Links answer key. See the docstring of .github/scripts/kpc_scoreboard_bot.py for how each column is decided.',
             'states': states, 'world': world,
             'totals': {'north_america': {k: T[k] for k in ('total', 'with_outline', 'missing', 'pin_only', 'line')},
                        'north_america_pct_complete': round(100 * T['filled'] / T['applicable']) if T['applicable'] else 0,
                        'world': dict(W), 'states': len(states), 'countries': len(world), 'parks_listed': len(parks_out)}}
    save(OUT / 'scoreboard.json', board)
    save(OUT / 'scoreboard-parks.json', {
        'about': 'US / Canada parks that still have something empty: no outline, or at least one column still missing. Parks with every column '
                 'filled are counted in scoreboard.json only. Facts only; built nightly by .github/scripts/kpc_scoreboard_bot.py (column logic in '
                 'its docstring). status / near_miss on missing-outline rows are chat 8\'s gap fields (no layer / likely name mismatch), kept as they were.',
        'built': TODAY,
        'keys': {'_': 'a key left out means 0 / empty / unknown / n (per: ?, sz: unknown, fer: n, camp: n)', 'n': 'name', 'a': 'area (US-XX / CA-XX)',
                 't': "POTA type: index into 'types'", 'o': 'outline: off official | pad PAD-US | osm OpenStreetMap (unofficial) | pin pin-only | line | miss missing',
                 'src': 'outline layer (pad = PAD-US)', 'sc': 'second-witness score', 'sz': 'size_check: agree | off | unsure | unknown',
                 'map': 'official map: 0 missing, 1 have, 2 have + dated', 'rul': 'rules page 0/1', 'hrs': 'hours 0/1', 'fee': 'fees 0/1',
                 'per': 'permits: 1 found, ? unknown', 'acc': 'access point 0/1', 'camp': 'campground: h have, n none found, - not applicable',
                 'who': 'agency that runs it', 'hov': 'handover hint 0/1', 'fer': '2-fer passes: y yes, n no, p partial',
                 'miss': 'columns still empty, one letter each: o outline, m official map, r rules, h hours, f fees, a access point, w who runs, c closures source (state), s size check, k campground', 'status': "chat 8: 'no layer' | 'likely name mismatch' | 'missing' (new)", 'near_miss': "chat 8's near-miss name"},
        'types': [t for t, i in sorted(types_idx.items(), key=lambda kv: kv[1])],
        'counts': {'listed': len(parks_out), 'parks': T['total'], 'missing_outline': T['missing'], 'pin_only': T['pin_only'], 'line': T['line']},
        'parks': parks_out})
    check(check_rows)
    notice('scoreboard', f"{len(states)} states / provinces, {T['total']} parks: {T['with_outline']} with outline, {T['missing']} missing, "
                         f"{T['pin_only']} pin-only, {T['line']} line · world {len(world)} countries {W['total']} parks ({W['missing']} missing) · "
                         f"columns filled {board['totals']['north_america_pct_complete']}%")


def check(rows):
    """Our 6 states next to chat 8's hand counts (KPC_Scoreboard_NA.csv). Differences are listed, never hidden."""
    lines = [f'# Scoreboard check ({TODAY})', '', 'Bot counts (data/us-key, data/ca-key tonight) next to chat 8\'s hand counts (KPC_Scoreboard_NA.csv, Oct 27 night).',
             'A difference is not an error by itself: the keys move nightly, retired parks are left out here, and chat 8 sorted BLM areas by name.', '',
             '| Area | Column | Bot | Chat 8 | Diff |', '|---|---|---|---|---|']
    c8 = collections.defaultdict(collections.Counter); have_csv = CSV8.exists()
    if have_csv:
        try:
            for r in csv.DictReader(open(CSV8, encoding='utf-8')):
                a = f"{r['country']}-{r['state_or_province']}"
                for ours, theirs in (('total', 'total'), ('with_outline', 'with_outline'), ('missing', None), ('pin_only', 'pin_only'), ('line', 'line_type')):
                    if theirs: c8[a][ours] += int(r[theirs] or 0)
                c8[a]['missing'] += int(r['likely_name_mismatch'] or 0) + int(r['no_layer_found'] or 0)
        except Exception as e:  # noqa: BLE001
            have_csv = False; lines.append(f'(could not read the csv: {e})')
    diffs = 0
    for area in CHECK_STATES:
        row = rows.get(area)
        if not row: lines.append(f'| {area} | (no key file tonight) | | | |'); continue
        for k in ('total', 'with_outline', 'missing', 'pin_only', 'line'):
            theirs = c8[area][k] if have_csv and area in c8 else None
            d = (row[k] - theirs) if theirs is not None else None
            if d: diffs += 1
            lines.append(f"| {area} | {k} | {row[k]} | {theirs if theirs is not None else 'n/a'} | {('%+d' % d) if d else ('0' if d == 0 else '')} |")
    lines += ['', f'Columns that differ: {diffs}.' if have_csv else 'Chat 8\'s csv was not found: no comparison tonight.',
              '', 'Known reasons for a small difference elsewhere: parks POTA retired since Oct 27 (links data/retired-refs.json) are left out of the bot counts '
              '(Oct 28: WY -4, QC -1); the keys are rebuilt nightly.']
    (OUT / 'scoreboard-check.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    notice('check vs chat 8', f'{diffs} differing columns over {len(CHECK_STATES)} states; details in {OUT}/scoreboard-check.md')


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice('stopped', str(e)[:300])
    sys.exit(0)
