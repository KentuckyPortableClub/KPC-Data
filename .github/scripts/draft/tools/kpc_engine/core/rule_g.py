"""Chat 11's bars, in code (GRADING_BAR_chat11.md, Nov 1). Pure functions, so every grader and the regression tests use
the very same rules. The engine still decides nothing: these rules only say which rows may become questions.

Rule G (outlines): accepted only on a SURE official match. All three must hold: the pin is INSIDE the record (or within
150 m of it with a name match, R-G12), the NAME matches, and the SIZE is similar.
  SURE     proper words equal both ways once kind words are stripped; kinds match; not a line matched to a polygon;
           not a container; size fits or is unknown.                  -> bot YES allowed (chat 11's 1-in-10 sample)
  LIKELY   proper words overlap (2+ words, or the whole shorter name); not a line, not a container.  -> chat 11 grades
  UNLIKELY everything else (one word in common, none, container, line vs polygon, size far off, other kind). -> evidence only,
           NEVER a question.
Size: within 1.5x PASS, 1.5-5x OFF (a person looks), over 5x WAY OFF (no). Parcels outside 0.2-2x are held."""
import math, re
from core import names, rules

# ---------------------------------------------------------------- kinds (a WMA only matches a WMA, a state park only a state park)
KINDS = [  # (kind, regex on the normalised name). The kind named LAST in the name wins.
    ('container', r'\b(wetland management district|management district|district|management unit complex|surface management)\b'),
    ('wpa', r'\b(waterfowl production area|wpa)\b'),
    ('wma', r'\b(wildlife management area|wma|fish and wildlife area|fish wildlife area|wildlife area|public hunting area|game land|game lands|wildlife management unit)\b'),
    ('refuge', r'\b(national wildlife refuge|nwr|wildlife refuge|refuge)\b'),
    ('wild_river', r'\b(wild river|scenic river|wild and scenic river|wsr|wild river corridor)\b'),
    ('state_park', r'\b(state park|state resort park|provincial park|territorial park|parc provincial|parc national du quebec)\b'),
    ('state_rec_area', r'\b(state recreation area|state recreational area|provincial recreation area|recreation site)\b'),
    ('state_forest', r'\b(state forest|provincial forest|demonstration forest)\b'),
    ('national_forest', r'\b(national forest|national grassland)\b'),
    ('national_park', r'\b(national park|national preserve|parc national)\b'),
    ('nra', r'\b(national recreation area|national river and recreation area|nrra|nra)\b'),
    ('rma', r'\b(recreation management area|special recreation management area|rma|srma|erma)\b'),
    ('guard_station', r'\b(guard station|gs|ranger station|work center)\b'),
    ('nature_reserve', r'\b(national nature reserve|nnr|local nature reserve|lnr|nature reserve)\b'),
    ('nature_preserve', r'\b(state nature preserve|nature preserve|snp|natural area preserve|state natural area|sna)\b'),
    ('natural_area', r'\b(natural area|na|wildland park|ecological reserve)\b'),
    ('historic_site', r'\b(state historic site|national historic site|historic site|nhs|lieu historique national|national historical park|state historic park)\b'),
    ('trail', r'\b(national scenic trail|national historic trail|state trail|rail trail|trail|trace|greenway)\b'),
    ('conservation_area', r'\b(conservation area|conservation reserve)\b'),
    ('wilderness', r'\b(wilderness|wilderness study area|wsa)\b'),
    ('city_park', r'\b(county park|city park|municipal park|regional park|metropark)\b'),
]
COMPAT = [{'state_park', 'state_rec_area'}, {'nature_preserve', 'natural_area', 'nature_reserve'}, {'national_park', 'nra'}]
LINE_KINDS = {'trail', 'wild_river'}
KIND_STRIP = set('district management unit complex production waterfowl station guard ranger work center corridor sma rma srma erma '
                 'nrra nra sna snp nhs nnr lnr na gs wpa wsa wsr tract fish game lands land lieu historique scenic'.split())
DENY_LAYER = re.compile(r'BLM_Natl_SMA|Surface_?Management_?Agency|SurfaceManagement|\bSMA\b', re.I)   # whole-state surface manager polygons
# WDPA / Protected Planet is never a source, not even a copy re-hosted by an official org (club, round 3). Checked on the
# layer's address, name, description, licence / copyright text and field names.
WDPA_CITE = re.compile(rules.WDPA + r'|WDPAID|WDPA_PID', re.I)     # incl. HDX copies (round 5)
# A forestry record is the wrong KIND of record for a nature reserve (GB-0889 Glen Nant NNR vs a Forest Blocks record).
FORESTRY_LAYER = re.compile(r'forest[\s_-]*blocks?|forestry|woodland|timber|felling|sub[\s_-]*compartments?|\bcompartments?\b|'
                            r'forest[\s_-]*estate|forest[\s_-]*inventory|\bNFI\b|forest[\s_-]*stands?|harvest', re.I)
FOREST_KINDS = {'state_forest', 'national_forest'}
ALIASES = {   # official renames and Indigenous / French names (Hard Look). Both directions are checked.
    'prairie coulees natural area': ['hargrave coulees natural area'],
    'colony farm regional park': ['ƛ̓exətəm regional park', 'texetem regional park', 'lhexetem regional park'],
    'mount douglas park': ['pkols', 'pkols park'],
}


def cites_wdpa(meta):
    """True when a layer cites WDPA / Protected Planet anywhere: meta is a URL / text, or an ArcGIS ?f=json dict
    (name, description, serviceDescription, copyrightText, licenseInfo, documentInfo, field names)."""
    if not meta: return False
    if isinstance(meta, str): return bool(WDPA_CITE.search(meta))
    parts = [str(meta.get(k) or '') for k in ('name', 'description', 'serviceDescription', 'copyrightText', 'licenseInfo',
                                              'documentInfo', 'url', 'layer_name', 'licence', 'title', 'about')]
    parts += [str(f.get('name') or '') + ' ' + str(f.get('alias') or '') for f in meta.get('fields') or [] if isinstance(f, dict)]
    return bool(WDPA_CITE.search(' '.join(parts)))


GAME_RESERVE = re.compile(r'\bgame[\s_-]*(reserve|park|farm|ranch|management[\s_-]*area|controlled[\s_-]*area)s?\b|\bhunting[\s_-]*(reserve|area|block|concession|preserve)s?\b|'
                          r'\bcontrolled[\s_-]*hunting\b|\bcoto[s]?[\s_-]*de[\s_-]*caza\b|\breservas?[\s_-]*de[\s_-]*caza\b|\breserves?[\s_-]*de[\s_-]*chasse\b|'
                          r'\bjagdreviere?\b|\bwildgehege\b|\briserv[ae][\s_-]*di[\s_-]*caccia\b', re.I)


def is_game_reserve(name, layer_text=''):
    """Club kind rule (round 5): game / hunting reserves are not POTA parks. True when the record (or its layer) is one."""
    return bool(GAME_RESERVE.search(name or '') or GAME_RESERVE.search(layer_text or ''))


def layer_kind_ok(park, layer_text):
    """-> (ok, why). A forestry / woodland layer only matches a forest; never a nature reserve, park or refuge."""
    if not FORESTRY_LAYER.search(layer_text or ''): return True, ''
    k = kind_g(park)
    if k is None or k in FOREST_KINDS or re.search(r'\b(forest|woods?)\b', names.norm(park)) and k not in ('nature_reserve', 'nature_preserve'):
        return True, ''
    return False, f'wrong kind of record: a forestry layer for a {k.replace("_", " ")}'


def kind_g(name):
    n, best = names.norm(name), (-1, None)
    for k, rx in KINDS:
        for m in re.finditer(rx, n):
            if m.end() > best[0] or (m.end() == best[0] and m.end() - m.start() > best[2]):
                best = (m.end(), k, m.end() - m.start())
    return best[1] if best[0] >= 0 else None


def kinds_all(name):
    n = names.norm(name)
    return {k for k, rx in KINDS if re.search(rx, n)}


def kinds_match(a, b):
    """A WMA only matches a WMA, a state park only a state park. A name holding two kinds ("Dawkins Line Rail Trail State
    Park") may match either one."""
    ka, kb = kind_g(a), kind_g(b)
    if 'container' in (ka, kb): return False
    if not ka or not kb or ka == kb: return True
    A, B = kinds_all(a) or {ka}, kinds_all(b) or {kb}
    return any(x == y or any({x, y} <= c for c in COMPAT) for x in A for y in B)


def proper_words(name):
    """The park's own words, with kind words (park, reserve, WMA, state, national, district ...) stripped."""
    return [w for w in names.core_words(name) if w not in KIND_STRIP]


def _alias_equal(a, b):
    na, nb = names.norm(a), names.norm(b)
    for k, vs in ALIASES.items():
        group = {names.norm(k)} | {names.norm(v) for v in vs}
        if na in group and nb in group and na != nb: return True
    return False


def name_level(park, rec):
    """'equal' (both ways), 'overlap' (2+ words, or the whole shorter name), 'one' (one word in common) or 'none'."""
    if _alias_equal(park, rec): return 'equal'
    a, b = set(proper_words(park)), set(proper_words(rec))
    if not a or not b: return 'none'
    if a == b: return 'equal'
    shared = a & b
    fuzzy = {x for x in a - shared if any(names._fuzzy_in(x, [y]) for y in b - shared)}
    if a - shared and fuzzy == a - shared and len(a) == len(b): return 'equal'
    if len(shared) >= 2 or (shared and (shared == a or shared == b)): return 'overlap'
    return 'one' if shared else 'none'


def size_band(ratio):
    if ratio is None or ratio <= 0: return 'unknown'
    r = max(ratio, 1 / ratio)
    return 'PASS' if r <= rules.num('size_pass_max') else ('OFF' if r <= rules.num('size_off_max') else 'WAY OFF')


def parcel_hold(ratio):
    """The parcel tracer holds anything outside 0.2-2x of the expected size (Salato 921 vs 229.85 ac, Hiwassee 9.8x)."""
    return ratio is None or not (rules.num('parcel_low') <= ratio <= rules.num('parcel_high'))


def is_line(kind_or_geom):
    if isinstance(kind_or_geom, str): return kind_or_geom in ('line', 'polyline', 'esriGeometryPolyline') or kind_or_geom in LINE_KINDS
    return getattr(kind_or_geom, 'geom_type', '') in ('LineString', 'MultiLineString')


def park_is_line(park_name):
    """True for a trail, False for a polygon kind, None when the name can be either: a trail that is also a state park,
    or a river (rivers are filed as lines or as corridor polygons)."""
    ks = kinds_all(park_name)
    if 'trail' in ks: return None if ks - {'trail'} else True
    if 'wild_river' in ks: return None
    return False


def tier_g(park, rec, inside, pin_m=None, rec_line=False, container=False, size_ratio=None, park_line=None, layer='', last_resort=False):
    """-> (SURE | LIKELY | UNLIKELY, reason). last_resort: the W-10 WDPA path (never SURE: at most LIKELY, approx)."""
    if DENY_LAYER.search(layer or ''): return 'UNLIKELY', 'surface-manager layer: never matched against parks'
    lr = bool(last_resort) and rules.wdpa_last_resort_ok()
    if rules.on('source_policy.wdpa_guard') and cites_wdpa(layer) and not lr:
        return 'UNLIKELY', 'WDPA / Protected Planet: rejected because an official layer exists or was not checked first (club rule W-10)'
    if lr:
        t, why = _tier_g_core(park, rec, inside, pin_m, rec_line, container, size_ratio, park_line, layer, allow_wdpa=True)
        if t == 'SURE': t, why = 'LIKELY', why + '; WDPA (last resort): never SURE'
        return t, why
    return _tier_g_core(park, rec, inside, pin_m, rec_line, container, size_ratio, park_line, layer)


def _tier_g_core(park, rec, inside, pin_m, rec_line, container, size_ratio, park_line, layer, allow_wdpa=False):
    bad = rules.forbidden(layer, allow_wdpa=allow_wdpa)
    if bad: return 'UNLIKELY', f'never-use source ({bad})'
    ok, why = layer_kind_ok(park, layer)
    if not ok and rules.on('checks.forestry_kind_guard'): return 'UNLIKELY', why
    if rules.on('checks.game_reserve_not_park') and is_game_reserve(rec, layer) and not is_game_reserve(park):
        return 'UNLIKELY', 'game reserve: not a POTA park (club kind rule)'
    nl = name_level(park, rec)
    near = inside or (pin_m is not None and pin_m <= rules.num('rg12_m') and nl in ('equal', 'overlap'))      # R-G12
    if not near: return 'UNLIKELY', 'pin not inside nor within 150 m with a name match (distance check)'
    if (container or kind_g(rec) == 'container') and rules.on('checks.containers'): return 'UNLIKELY', 'container: one record under several parks (or a management district)'
    pl = park_is_line(park) if park_line is None else park_line
    if pl is not None and pl != bool(rec_line) and rules.on('checks.line_vs_polygon'): return 'UNLIKELY', 'line park vs polygon record (or the other way round)'
    if not kinds_match(park, rec): return 'UNLIKELY', f'other kind of place ({kind_g(park)} vs {kind_g(rec)})'
    sb = size_band(size_ratio)
    if sb == 'WAY OFF': return 'UNLIKELY', f'size WAY OFF ({size_ratio:.2f}x)'
    if nl == 'equal' and sb in ('PASS', 'unknown'): return 'SURE', 'names equal once kind words are stripped' + ('' if inside else ' (R-G12: pin within 150 m)')
    if nl in ('equal', 'overlap'): return 'LIKELY', 'names overlap' + (f'; size {sb} ({size_ratio:.2f}x): a person looks' if sb == 'OFF' else '')
    return 'UNLIKELY', f'name: {nl} word(s) in common'


def containers(rows):
    """Records that sit under several parks' pins: {(layer, record): [refs]} with 2+ refs."""
    seen = {}
    for r in rows:
        if r.get('record') is None or not r.get('layer'): continue
        seen.setdefault((r['layer'], str(r['record'])), set()).add(r['ref'])
    return {k: sorted(v) for k, v in seen.items() if len(v) > 1}


def same_land(a, b, share=0.9):
    """Two records that are the same land (Big South Fork's 30,138-acre copy inside the main outline): merge, don't count twice."""
    try:
        small = min(a.area, b.area)
        return small > 0 and a.intersection(b).area / small >= share
    except Exception:  # noqa: BLE001
        return False


def absorbs_other_park(parcel, other_outlines, share=0.5):
    """A parcel inside another POTA park's official outline (Halfmoon Pond in Bomoseen SP) is never taken."""
    for g in other_outlines or []:
        try:
            if parcel.area > 0 and parcel.intersection(g).area / parcel.area >= share: return True
        except Exception:  # noqa: BLE001
            continue
    return False


def pin_typo(pin, official):
    """R-G13: POTA pin vs the official point. Returns a note when they are far apart AND the gap looks like a typing slip
    (one degree of latitude or longitude, a lost minus sign, lat/lon swapped). The pin never moves: it is a question."""
    (la, lo), (oa, oo) = pin, official
    km = _km(la, lo, oa, oo)
    if km < 5: return None
    why = None
    if abs(round(la - oa) - (la - oa)) < 0.15 and abs(lo - oo) < 0.2 and round(abs(la - oa)) >= 1: why = f'latitude typed {int(la)} for {int(oa)}'
    elif abs(round(lo - oo) - (lo - oo)) < 0.15 and abs(la - oa) < 0.2 and round(abs(lo - oo)) >= 1: why = f'longitude typed {int(lo)} for {int(oo)}'
    elif abs(lo + oo) < 0.2 and abs(la - oa) < 0.2: why = 'longitude sign lost'
    elif abs(la - oo) < 0.2 and abs(lo - oa) < 0.2: why = 'latitude and longitude swapped'
    return {'km': round(km, 1), 'why': why or 'far from the official point', 'rule': 'R-G13', 'pin_moves': False}


def _km(a1, o1, a2, o2):
    r = math.pi / 180
    d = math.sin((a2 - a1) * r / 2) ** 2 + math.cos(a1 * r) * math.cos(a2 * r) * math.sin((o2 - o1) * r / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(d))


def pick_name_field(fields, wanted=None):
    """Alberta: PARK_NAME returned nothing because the field is NAME. Read the layer's ?f=json field names first."""
    names_ = [f['name'] if isinstance(f, dict) else f for f in fields or []]
    if wanted and wanted in names_: return wanted
    low = {n.lower(): n for n in names_}
    for k in ('name', 'park_name', 'parkname', 'site_name', 'unit_name', 'name_en', 'nom', 'label', 'title'):
        if k in low: return low[k]
    return next((n for n in names_ if re.search(r'name|nom\b|navn|naam', n, re.I)), None)


# ---------------------------------------------------------------- documents
DOC_NOT_OFFICIAL = re.compile(r'wikipedia|wikimedia|tripadvisor|alltrails|yelp|visit[a-z]*\.(com|org)|tourism|travel|apps?\.apple|play\.google|google\.', re.I)
DOC_LOGO = re.compile(r'logo|letterhead|signage|\bsign[s_-]|banner|icon|favicon|seal\b|header', re.I)


def link_of(x):
    """A docs field may be a URL or {'url': ..., ...}."""
    if isinstance(x, dict): return x.get('url') or x.get('link') or ''
    return x or ''


def doc_problems(row, shared_count=1, existing_ok=False):
    p = []
    link = link_of(row.get('map')) or link_of(row.get('page')) or link_of(row.get('url'))
    bad = rules.forbidden(link)
    if bad: p.append(f'not official ({bad})')
    elif rules.on('source_policy.unofficial_docs_kept_apart') and DOC_NOT_OFFICIAL.search(link) and not rules.switched_off_hits(link):
        p.append('not official (Wikipedia / tourism / app)')
    if row.get('map') and DOC_LOGO.search(link_of(row['map'])): p.append('a sign / logo / letterhead, not a map')
    if shared_count > rules.num('docs_same_file_max'): p.append(f'the same file is used by {shared_count} parks')
    if existing_ok and row.get('map'): p.append('would replace a map already marked status: ok')
    return p


# ---------------------------------------------------------------- parking / access points
BAD_LABEL = re.compile(r'\bwilderness\b|\boffice\b|\bhotel\b|\bmotel\b|\blodge\b|\bheadquarters\b|^\s*(US|KY|TN|SR|CR|SH|HWY|I|Route|Rte|County Road|State Route)[- ]?\d+\s*$', re.I)


def point_problems(pt, area):
    """pt = [lat, lon, label, how]. Returns problems (any one fails the point)."""
    lat, lon, label = pt[0], pt[1], str((pt[2] if len(pt) > 2 else '') or '')
    p = []
    if area[:2] in ('US', 'CA') and lon > 0: p.append('west longitude written as positive')
    if rules.on('checks.point_label_filter') and BAD_LABEL.search(label.split(' (')[0]): p.append(f'bad label ({label[:40]})')
    return p


def same_points(rows, nd=5):
    """One feature filed under 2+ parks: {(lat, lon): [refs]}. For parking / camping this is a DUPLICATE FACILITY (one
    facility listed under 2+ parks; chat 11's bar is 0). For trails it is usually "Overlapping boundaries" (not a failure)."""
    seen = {}
    for r in rows:
        for f in r.get('features') or []:
            k = (round(float(f[0]), nd), round(float(f[1]), nd)) if isinstance(f, (list, tuple)) else (round(f.get('lat', 0), nd), round(f.get('lon', 0), nd))
            seen.setdefault(k, set()).add(r['ref'])
    return {k: sorted(v) for k, v in seen.items() if len(v) > 1}


shared_points = same_points        # old name (round 2-3), kept for scripts


def resolve_duplicates(rows):
    """Chat 11 (parking / camping): 0 duplicate facilities. One facility listed under 2+ parks stays only with the park whose
    pin is nearest; returns how many rows lost a point."""
    got = [r for r in rows if r and r.get('status') == 'found']
    n = 0
    for key, refs in same_points(got).items():
        owners = [(f['m'], r['ref']) for r in got for f in r['features'] if (round(f['lat'], 5), round(f['lon'], 5)) == key]
        keep = min(owners)[1]
        for r in got:
            if r['ref'] == keep: continue
            before = len(r['features'])
            r['features'] = [f for f in r['features'] if (round(f['lat'], 5), round(f['lon'], 5)) != key]
            if len(r['features']) != before:
                n += 1
                r.setdefault('notes', {}).setdefault('where_looked', []).append({'source': 'duplicate facility check', 'gave': f'facility at {key} is also listed under {keep} (nearer pin): kept there only'})
            if not r['features']:
                r.update(status='not found', whynot={'tag': 'only a duplicate facility (kept with the park whose pin is nearer)', 'date': r.get('date')})
    return n


resolve_shared = resolve_duplicates


# ---------------------------------------------------------------- trail bar (club, round 4)
NHT = re.compile(r'\bNational Historic Trail\b', re.I)
APPROX_MARK = re.compile(r'\bapprox(imate|imately|\.)?\b|\bgeneral(ized)? (route|location)\b', re.I)
AGGREGATOR = re.compile(r'KyGovMaps|USGS[_ ]Aggregated|aggregated trails|statewide trails inventory', re.I)
# Club ruling (round 5): a STATE MAPPING AGENCY compilation (KyGovMaps = Kentucky's state mapping agency) counts as official when the
# managing agency publishes no line of its own; the agency's own line wins whenever it turns up. Switch:
# source_policy.state_mapping_compilations. Add other states' mapping agencies here (or flag a registry source
# 'state_mapping_compilation': true).
STATE_MAPPING = re.compile(r'KyGovMaps|kygisserver\.ky\.gov|opengisdata\.ky\.gov|Kentucky (Division|Office) of Geographic Information|'
                           r'\bTN ?STS\b|Tennessee (Geographic Information Council|Strategic Technology Solutions)|tnmap\.tn\.gov', re.I)
WATER_LAYER = re.compile(r'\bNHD\b|nhd_|stream|blueline|hydro|river', re.I)
WATER_PARK = re.compile(r'\b(wild and scenic river|scenic river|national river|water ?trail|blueway|paddl\w* trail|canoe trail|river ?trail)\b|'
                        r'^\W*[\w\s.\'-]*\b(river|creek|fork|bayou)\W*$', re.I)     # the park IS a river / water trail ('Beaver Creek WMA' is not)
# a trail piece with its own name is tied to the POTA trail ONLY by another field on the same record (trail system / route) or by
# the managing agency's own page listing the piece. Never on location alone.
SYSTEM_FIELD = re.compile(r'system|route|network|parent|corridor|segment_?of|part_?of|trail_?group|nat(ional)?_?trail|long_?dist', re.I)


def agency_own(feature, park_agency):
    """Is the line the managing agency's own? park_agency is the park's agency group (a web domain such as parks.ky.gov, or a
    name). The line's agency (registry 'agency') must be that agency: same name, or one of its official domains."""
    from core.agencies import AGENCY_DOMAINS
    fa = (feature.get('agency') or '').strip()
    pa = (park_agency or '').strip().lower()
    if not fa or not pa or AGGREGATOR.search(fa) or AGGREGATOR.search(feature.get('source') or ''): return False
    if fa.lower() == pa: return True
    doms = [d.lower() for d in AGENCY_DOMAINS.get(fa, [])]
    return any(pa == d or pa.endswith('.' + d) or d.endswith('.' + pa) for d in doms)


def state_compilation(feature, park_name=''):
    """A state mapping agency's compiled line (switch source_policy.state_mapping_compilations). Stream / hydrography lines only
    count for a river or water-trail park."""
    if not rules.on('source_policy.state_mapping_compilations'): return False
    txt = ' '.join(str(feature.get(k) or '') for k in ('agency', 'source', 'record_link'))
    if not (feature.get('state_mapping_compilation') or STATE_MAPPING.search(txt)): return False
    if WATER_LAYER.search(feature.get('source') or '') and not WATER_PARK.search(park_name or ''): return False
    return True


def name_tie(f, park_name):
    """-> (ok, how). The line's own name matches the trail, or (for a piece with its own name) an official tie: another field on the
    same record names the trail system, or the managing agency's page lists the piece (f['agency_page_lists'] = that page)."""
    if name_level(park_name or '', f.get('name') or '') in ('equal', 'overlap'): return True, 'name'
    for v in f.get('system_names') or []:
        if name_level(park_name or '', str(v)) in ('equal', 'overlap'): return True, f'trail-system field on the same record: {str(v)[:60]}'
    if f.get('agency_page_lists'): return True, f"the managing agency's page lists it: {f['agency_page_lists']}"
    return False, ''


def trail_bar(f, park_name, park_agency, own_exists=None):
    """Club trail bar: the managing agency's own line (or, when the agency publishes none, a state mapping agency compilation)
    + its name matches the trail (or an official tie, never location alone) + the POTA pin within grader.trail_pin_m (200 m)
    of the line. -> (passes, [reasons it does not])."""
    why = []
    if not agency_own(f, park_agency):
        if own_exists: why.append(f"not the managing agency's own line ({f.get('agency') or '?'}); the agency's own line wins")
        elif state_compilation(f, park_name): f['basis'] = "state mapping agency compilation (the managing agency publishes no line of its own)"
        else: why.append(f"not the managing agency's own line ({f.get('agency') or '?'})")
    ok, how = name_tie(f, park_name)
    if ok and how != 'name': f['name_tie'] = how
    if not ok: why.append(f"name does not match the trail ({(f.get('name') or '')[:40]}) and nothing official ties it to the trail (never on location alone)")
    d = f.get('pin_line_m')
    if d is None: why.append('pin-to-line distance not measured (rerun the trail plug-in)')
    elif d > rules.num('trail_pin_m'): why.append(f"pin {d:.0f} m from the line (bar {rules.num('trail_pin_m'):.0f} m)")
    return (not why), why


def trail_approx(f, park_name):
    """National historic trails that the agency itself marks approximate stay approximate."""
    return bool(NHT.search(park_name or '') and (f.get('agency_marks_approx') or APPROX_MARK.search(f.get('name') or '')))


def apply_trail_bar(rows):
    """Trail rows: 'found' only when a feature meets the bar; otherwise 'candidate' with the reasons (a person looks)."""
    for r in rows:
        if not r or r.get('status') not in ('found', 'candidate') or not r.get('features'): continue
        best = None
        own = any(agency_own(f, r.get('agency_group')) for f in r['features'])     # the agency's own line wins over a compilation
        for f in r['features']: f.pop('basis', None); f.pop('name_tie', None)
        for f in sorted(r['features'], key=lambda f: not agency_own(f, r.get('agency_group'))):
            ok, why = trail_bar(f, r.get('park'), r.get('agency_group'), own_exists=own)
            f['trail_bar'] = 'PASS' if ok else '; '.join(why)
            if trail_approx(f, r.get('park')): f['grade'] = 'approx'
            if ok and best is None: best = f
        if best is not None:
            r['status'] = 'found'; r['trail_bar'] = 'PASS'
            if best.get('basis'): r['basis'] = best['basis']
            r['features'] = [best] + [f for f in r['features'] if f is not best]
            if best.get('grade') == 'approx': r['grade'] = 'approx'; r['g'] = 'approx'
        else:
            r['status'] = 'candidate'; r['trail_bar'] = 'not met'
            r['whynot'] = {'tag': 'trail bar not met: ' + r['features'][0]['trail_bar'], 'date': r.get('date')}
    return rows


# ---------------------------------------------------------------- campgrounds
OTHER_BUSINESS = re.compile(r'\bgolf\b|\bmarina\b|\bpool\b|\bpicnic shelter|\bshelter house|\bboat ramp|\bboat launch|\bscuba\b|\brestaurant\b|\bdining\b|\bgift shop\b', re.I)


def camp_feature_ok(label):
    if not rules.on('checks.camp_feature_filter'): return True
    return not OTHER_BUSINESS.search(label or '')


# ---------------------------------------------------------------- Kentucky hours / fees
HOURS_OTHER = re.compile(r'\bmarina\b|\bscuba\b|\bpool\b|\bgolf\b|\brestaurant\b|\bdining\b|\bgift shop\b|\blodge\b|\bfront desk\b|\bpro shop\b|\bboat rental', re.I)
BARE_TIME = re.compile(r'^\W*(\d{1,2}(:\d{2})?\s?(a\.?m\.?|p\.?m\.?)?\s*[-–to]+\s*\d{1,2}(:\d{2})?\s?(a\.?m\.?|p\.?m\.?))\W*$', re.I)
HUNTING = re.compile(r'\bhunt(ing|ers)?\b|\bseason\b.*\b(deer|turkey|dove|waterfowl)\b', re.I)


def hours_line_ok(line, what='hours'):
    """The Oct 31 sample failed 3 of 12: marina / scuba hours as park hours, bare '10 AM - 4 PM' fragments,
    'Open seasonally' under hunting hours."""
    s = (line or '').strip()
    if not s: return False, 'empty'
    if rules.on('hours_rules.separate_marina_scuba') and HOURS_OTHER.search(s): return False, 'another business (marina, scuba, pool, golf, lodge ...)'
    if rules.on('hours_rules.reject_fragments') and BARE_TIME.match(s): return False, 'bare time fragment with no subject'
    if what == 'hours' and rules.on('hours_rules.hunting_hours_apart') and HUNTING.search(s): return False, 'hunting season, not park hours'
    return True, ''
