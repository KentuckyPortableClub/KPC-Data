import re
"""Park-name matching in many languages: core words, a 0-1 similarity score, and the name tiers T-1..T-6.

The tiers here are the engine's reading of 'the collector's tiers' (Finder3 PART 1.1); chat 10 can re-map them in TIERS:
  T-1  same name (normalised) and the pin inside
  T-2  every core word found and the pin inside
  T-3  most core words, pin inside;  OR every core word with the pin within 150 m of the edge (G-F1 'pin just outside')
  T-4  every core word but the pin far away (possible PIN OFF: needs an official point, G-F2; never a bot YES)
  T-5  pin inside, the name does not match (a parent area, a neighbour, another kind of record)
  T-6  a core word only in some other text field (lesson 2: odd name fields), or a weak partial match"""
import difflib, re, unicodedata

GENERIC = set("""
the of and de la le les du des di del della dello y et und der die das van het en og i a an at on
park parks state national provincial regional county city municipal community memorial recreation recreational area areas
wildlife management wma natural nature preserve reserve reservation forest forests state-forest refuge nwr nwa sanctuary
historic historical site sites monument landmark heritage conservation conservancy protected scenic
wilderness seashore lakeshore battlefield wild resort srp snp wsr nhs nht
centre center camp campground provincial-park
nationalpark naturpark naturschutzgebiet landschaftsschutzgebiet biosphärenreservat biosphaerenreservat schutzgebiet nsg lsg
parc naturel national régional regional réserve reserve naturelle nationale forêt domaniale site classé
parque natural nacional reserva paraje espacio protegido monumento
parco nazionale naturale regionale riserva area protetta oasi
park narodowy krajobrazowy rezerwat przyrody obszar chronionego krajobrazu
nasjonalpark naturreservat landskapsvernområde naturvernområde nationalpark naturreservat kansallispuisto luonnonpuisto
nationaal natuurgebied natuurreservaat landgoed
parcul parcului rezervatia rezervatie rezervatiei naturala naturale stiintifica aria protejata national nationala
naturpark landschaftsschutzgebiet nationalpark naturreservat reservaat
national-park nature-reserve country sssi nnr aonb
natura sci sac spa spas sacs ramsar zps zsc lic zepa psci ffh vogelschutzgebiet habitatomrade fuglebeskyttelsesomrade habitatomraade
""".split())

TRANS = str.maketrans({'æ': 'ae', 'Æ': 'Ae', 'ø': 'oe', 'Ø': 'Oe', 'ß': 'ss', 'œ': 'oe', 'Œ': 'Oe', 'ł': 'l', 'Ł': 'L', 'đ': 'd', 'Đ': 'D', 'þ': 'th'})


def strip_accents(s):
    """Accents off, and the letters NFKD cannot split spelled the Nordic / German way (Rørbæk = Roerbaek, as POTA writes it)."""
    s = (s or '').translate(TRANS)
    return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c))


def norm(s):
    s = strip_accents(str(s or '')).lower().replace('&', ' and ')
    s = re.sub(r"[’'`´]", '', s)
    s = re.sub(r'\b(st|ste)\.?\s', 'saint ', s)
    s = re.sub(r'\bmt\.?\s', 'mount ', s)
    s = re.sub(r'\bft\.?\s', 'fort ', s)
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', s).split())


def _pack_words():
    """Local-language park words per country from the club pack (world_agencies.json via registry/pack_sources.json):
    Naturschutzgebiet, parc naturel, rezervație ... are designations, not the park's own name."""
    import json, pathlib
    try: d = json.load(open(pathlib.Path(__file__).resolve().parent.parent / 'registry' / 'pack_sources.json')).get('words', {})
    except (OSError, ValueError): return set()
    out = set()
    for cc, ws in d.items():
        if cc in ('GB', 'IE', 'AU', 'NZ', 'ZA', 'US', 'CA'): continue      # English words are already handled; keep 'Heritage' etc. meaningful
        for w in ws:
            for x in norm(w).split():
                if len(x) > 3: out.add(x)
    return out


LOCAL_WORDS = _pack_words()
GENERIC |= LOCAL_WORDS


SITE_CODE = re.compile(r'^[a-z]{2}(sci|spa|sac|pa)?\d{3,}[a-z]?$')   # Natura 2000 site codes such as ROSCI0123, DE4321301
GENERIC |= {'situl', 'sit', 'aria', 'protejata', 'rezervatia', 'rezervatie', 'naturala', 'naturale'}


def core_words(name):
    w = [x for x in norm(name).split() if x not in GENERIC and len(x) > 1 and not x.isdigit() and not SITE_CODE.match(x)]
    return w or [x for x in norm(name).split() if len(x) > 2][:3]


def similarity(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb: return 0.0
    if na == nb: return 1.0
    ca, cb = set(core_words(a)), set(core_words(b))
    jac = len(ca & cb) / max(1, len(ca | cb)) if ca and cb else 0
    cover = len(ca & cb) / max(1, len(ca)) if ca else 0
    seq = difflib.SequenceMatcher(None, ' '.join(sorted(ca)), ' '.join(sorted(cb))).ratio() if ca and cb else 0
    return round(max(jac, 0.6 * cover + 0.4 * seq, seq * 0.9), 3)


def _fuzzy_in(w, toks):
    """A long word spelt a little differently (Văcăraști / Văcărești, Gaelic / English spellings): ratio >= 0.85."""
    return len(w) > 5 and any(abs(len(x) - len(w)) <= 2 and difflib.SequenceMatcher(None, w, x).ratio() >= 0.85 for x in toks)


def words_in_text(words, text):
    t = ' ' + norm(text) + ' '
    toks = t.split()
    return sum(1 for w in words if f' {w} ' in t or (len(w) > 5 and w in t) or _fuzzy_in(w, toks))


def all_text(attrs):
    """Lesson 2: EVERY text field (Yukon REMARKS, Kingston NOTES_NAME_OF_BLDG, Parks Canada SectionEn ...)."""
    return ' | '.join(str(v) for k, v in (attrs or {}).items() if isinstance(v, str) and not re.match(r'^(shape|globalid|guid|uuid)', k, re.I))


KIND_WORDS = [  # (kind, regex on the normalised name); first match wins
    ('trail', r'\b(trail|trails|trace|greenway|rail trail|camino|sentier|weg|wanderweg)\b'),
    ('river', r'\b(river|creek|wild river|scenic river|fluss|riviere|rio)\b'),
    ('lake', r'\b(lake|reservoir|dam|see|lac|lago)\b'),
    ('wildlife', r'\b(wma|wildlife|refuge|nwr|hunting|game|fish|hatchery|bird sanctuary|vogel)\b'),
    ('forest', r'\b(forest|forests|grassland|wald|foret|bosque)\b'),
    ('preserve', r'\b(preserve|natural area|nature reserve|reserve|reserva|naturschutzgebiet|reservat)\b'),
    ('historic', r'\b(historic|historical|battlefield|monument|memorial|museum|fort)\b'),
    ('park', r'\b(park|parks|parc|parque|parco|nationalpark)\b'),
]


def kind_of(name):
    """The kind named LAST wins ('Trail of Tears Park' is a park, 'Lake Barkley WMA' is wildlife)."""
    n, best = norm(name), (-1, None)
    for k, rx in KIND_WORDS:
        for m in re.finditer(rx, n):
            if m.end() > best[0]: best = (m.end(), k)
    return best[1]


def kind_clash(park_name, hit_name):
    """'Trail of Tears National Historic Trail' vs 'Trail Of Tears Park': same words, other kind of place. Lakes, rivers and
    trails are often named after each other, so a clash only pushes the tier down one step and is written in the notes."""
    a, b = kind_of(park_name), kind_of(hit_name)
    return bool(a and b and a != b and not ({a, b} <= {'park', 'preserve'}))


def _rg12():
    from core import rules
    return rules.num('rg12_m')


DOWN = {'T-1': 'T-2', 'T-2': 'T-3', 'T-3': 'T-4', 'T-4': 'T-6'}


def tier(park_name, hit_name, attrs, inside, dist_m):
    t, sim = _tier(park_name, hit_name, attrs, inside, dist_m)
    if t in DOWN and kind_clash(park_name, hit_name): return DOWN[t], sim
    return t, sim


def _tier(park_name, hit_name, attrs, inside, dist_m):
    words = core_words(park_name)
    nm_hit = words_in_text(words, hit_name or '')
    any_hit = words_in_text(words, all_text(attrs))
    full = words and nm_hit == len(words)
    most = words and nm_hit >= max(1, (len(words) + 1) // 2)
    sim = similarity(park_name, hit_name or '')
    if inside and norm(park_name) == norm(hit_name): return 'T-1', sim
    if inside and full: return 'T-2', sim
    if inside and most: return 'T-3', sim
    if full and dist_m is not None and dist_m <= _rg12(): return 'T-3', sim      # G-F1: pin just outside (candidate only)
    if full: return 'T-4', sim
    if inside and any_hit < max(1, len(words)): return ('T-6' if any_hit else 'T-5'), sim
    if any_hit and any_hit == len(words): return 'T-6', sim
    return None, sim
