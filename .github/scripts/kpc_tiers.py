#!/usr/bin/env python3
"""THREE TIERS FOR A CANDIDATE OUTLINE (chat 10 / Fable, Oct 30 2026, Brandon 5:05 AM 'go do your magic'). Rule lines: KPC-Links
.claude/notes/mapping.md 'HUNTER TIERS T-1..T-6'. Built from chat 11's 2,480 answers (US + Canada hunter, world finder): nearly every
NO was (a) one record under several parks' pins (a container), (b) a park whose NAME is a line (trail / river / path) matched to a
polygon, (c) one shared word counted as a match, (d) sister sites (Little / North / Lower Armit River), (e) SSSI / zone / district
land classes. Nearly every YES had the same PROPER words on both sides once kind words (park, reserve, SS.R., WMA ...) were stripped.

  tier(park_name, record_name, record_acres, park_acres, pins_under_record) -> ('SURE' | 'LIKELY' | 'UNLIKELY', why)
    SURE     = proper words equal both ways, not a line park, not a container, size fits or unknown  -> chat 2 recheck + chat 11 10% sample
    LIKELY   = proper words overlap (2+ words, or the whole shorter side), not a line, not a container -> chat 11 grades
    UNLIKELY = everything else (one shared word, no shared word, container, line, size far off)        -> evidence only, never a question
Learned answers (kpc_learned): a (layer, record) chat 11 said NO to is never asked again; a layer under 10% YES after 20 answers is
demoted to evidence-only. Shared by kpc_gis_hunter.py and kpc_world_finder.py. No network."""
import json, pathlib, re, unicodedata

# kind words: what the land IS, not which land it is. Stripped before names are compared (both languages we meet).
KIND = set('''park parks parc parcs reserve reserves réserve reserva reservat area areas aire site sites state states national nationale nacional
provincial provinciale regional régional regionale local county city town municipal district wildlife faune fauna management conservation
conservancy natural nature naturelle natural natuur natur nationalpark naturpark naturschutzgebiet landschaftsschutzgebiet nature-reserve
historic historical heritage national-historic recreation recreational rec forest forêt forestry forests woodland woods wood
fish fishing fishery fisheries hatchery game land lands public unit units section sections tract tracts campground camp camping
scenic wild coastal marine
streamside bushland flora features ecological ecology environmental environment preserve preserved protected protection
multiple use retained staging ohv dam production tva public
sanctuary refuge refuges wma wmas swa sfwa sra srs shs nhs nwr wpa nra pra plrec pluz sssi sac spa ramsar nsa acec rma blm usfs
monument memorial battlefield trail trails path paths way byway parkway greenway canal corridor route
the and of de la le les du des del der die das und von van het in at on by for with & -'''.split())
LINE = re.compile(r'(trail|trails|path|byway|parkway|greenway|canal|corridor|route|rail trail|sentier|chemin|coast path)|'
                  r'(wild and scenic|scenic river|heritage river|national (?:wild )?(?:and )?(?:scenic )?river|recreational river)', re.I)
CONTAINER = re.compile(r'\b(zone|zones|pluz|region|district|country|county|counties|shire|municipality|catchment|watershed|sssi|sac|spa|'
                       r'ramsar|aonb|national park authority|land use|forest reserve|forest management|ranger district|field office|'
                       r'grazing|allotment|township|parish|borough|electoral|ward)\b', re.I)
VIC = {'ss.r': 'streamside reserve', 'n.c.r': 'nature conservation reserve', 'n.f.r': 'natural features reserve', 'n.f.s.r': 'natural features scenic reserve',
       'f.r': 'flora reserve', 'f.f.r': 'flora fauna reserve', 'b.r': 'bushland reserve', 'g.l.r': 'gippsland lakes reserve', 'w.r': 'wildlife reserve',
       'h.a': 'historic area', 's.r': 'scenic reserve', 'n.p': 'national park', 's.p': 'state park', 'c.p': 'coastal park', 'r.p': 'regional park',
       'sfwa': 'state fish wildlife area', 'swa': 'state wildlife area', 'wma': 'wildlife management area', 'sra': 'state recreation area',
       'srs': 'state recreation site', 'shs': 'state historic site', 'nhs': 'national historic site', 'nwr': 'national wildlife refuge',
       'wpa': 'waterfowl production area', 'nra': 'national recreation area', 'acec': 'area of critical environmental concern', 'nnr': 'national nature reserve',
       'lnr': 'local nature reserve', 'sssi': 'sssi', 'pp': 'provincial park', 'pra': 'provincial recreation area'}
GENERIC_KIND = {'park', 'parks', 'parc', 'reserve', 'reserves', 'reserva', 'area', 'areas', 'aire', 'site', 'sites', 'state', 'national', 'provincial',
                'regional', 'local', 'public', 'land', 'lands', 'unit', 'the', 'and', 'of', 'de', 'la', 'le', 'du', 'des', 'del', '&', '-'}
ABBR = {'gov': 'governor', 'govr': 'governor', 'mt': 'mount', 'mtn': 'mountain', 'mtns': 'mountains', 'ft': 'fort', 'st': 'saint', 'ste': 'sainte',
        'pt': 'point', 'is': 'island', 'isl': 'island', 'lk': 'lake', 'cr': 'creek', 'rvr': 'river', 'hbr': 'harbor', 'harbour': 'harbor',
        'centre': 'center', 'colour': 'color', 'jct': 'junction', 'no': 'number', 'nr': 'near'}


def norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r"[’'`]s\b", '', s)
    for k, v in sorted(VIC.items(), key=lambda kv: -len(kv[0])):
        s = re.sub(r'(?<![a-z])' + re.escape(k).replace(r'\.', r'\.?') + r'\.?(?![a-z])', ' ' + v + ' ', s)
    return re.findall(r'[a-z0-9]+', s)


def kinds(name):
    """The distinctive KIND words (streamside / campground / wildlife ...): generic ones (park, reserve, area, state) say nothing."""
    return {w for w in norm(name) if w in KIND and w not in GENERIC_KIND and len(w) > 2}


def same_word(a, b):
    if a == b: return True
    if len(a) >= 6 and len(b) >= 6 and abs(len(a) - len(b)) <= 1:   # Inuujarvik / Inuujaarvik: one letter off
        if len(a) == len(b): return sum(c != d for c, d in zip(a, b)) <= 1
        s, l = (a, b) if len(a) < len(b) else (b, a)
        return any(l[:i] + l[i + 1:] == s for i in range(len(l)))
    return False


def match(pw, rw):
    """-> (shared, park-only, record-only) with one-letter spelling slips counted as the same word."""
    shared, ponly = set(), set()
    rw2 = set(rw)
    for w in pw:
        m = next((r for r in rw2 if same_word(w, r)), None)
        if m is None: ponly.add(w)
        else: shared.add(w); rw2.discard(m)
    return shared, ponly, rw2


def proper(name):
    """The words that say WHICH land: no kind words, no 1-2 letter bits (SS.R. -> gone), plurals folded, abbreviations opened."""
    out = set()
    for w in norm(name):
        w = ABBR.get(w, w)
        if w in KIND: continue
        if len(w) <= 2 and not re.search(r'\d', w): continue
        if len(w) > 3 and w.endswith('s') and not w.endswith('ss'): w = w[:-1]
        out.add(w)
    return out


SMALL_KIND = re.compile(r'site|hatchery|campground|monument|historic|natural area|staging|picnic|boat|access|landing|cemetery|lighthouse|museum|battlefield|memorial|tower|lookout|spring', re.I)
UNIT = re.compile(r'\b(park|parc|reserve|refuge|sanctuary|site|campground|hatchery|preserve|monument|production|wma|swa|wpa|nwr|conservation area|natural area|recreation)\b', re.I)


COMMON = set('lake lakes river creek mountain mountains island point bay north south east west upper lower little big great long new old mount fort saint '
             'valley hill hills ridge canyon spring springs falls pond beach harbor forest wood woods prairie meadow grove rock rocks bluff landing branch fork'.split())


def distinctive(w): return len(w) >= 6 and w not in COMMON and not re.search(r'\d', w)


def unbracket(s):
    t = re.sub(r'\([^)]*\)', ' ', str(s or ''))
    return t if proper(t) else s


def tier(park, record, rec_acres=None, park_acres=None, pins_under=1):
    park, record = unbracket(park), unbracket(record)   # 'Thackeray Provincial Park (Nature Reserve Class)' = Thackeray Provincial Park
    pw, rw = proper(park), proper(record)
    if not rw or not pw: return 'UNLIKELY', 'no proper name to compare'
    shared, ponly, ronly = match(pw, rw)
    equal = not ponly and not ronly
    if pins_under >= 3 and not equal: return 'UNLIKELY', f'container: one record under {pins_under} parks'
    if CONTAINER.search(str(record or '')) and not CONTAINER.search(str(park or '')) and not UNIT.search(str(record or '')):
        return 'UNLIKELY', 'container word in the record name (zone / district / county / SSSI ...)'
    if LINE.search(str(park or '')): return 'UNLIKELY', 'a line park (trail / scenic river) on a polygon record'
    both = isinstance(rec_acres, (int, float)) and isinstance(park_acres, (int, float)) and park_acres > 0 and rec_acres > 0
    if both and rec_acres > 20 * park_acres: return 'UNLIKELY', f'record {rec_acres:,.0f} ac is over 20x the park ({park_acres:,.0f} ac)'
    big = isinstance(rec_acres, (int, float)) and ((rec_acres > 50_000 and SMALL_KIND.search(str(park or ''))) or rec_acres > 250_000) \
        and not re.search(r'national park|national forest|provincial park|wilderness|state forest|grassland|public use area|territorial park', str(park or ''), re.I)
    if equal:
        if pins_under >= 3: return 'LIKELY', f'same name, but {pins_under} parks share this record (sectors of one park, or a container)'
        if big: return 'LIKELY', f'same name, record {rec_acres:,.0f} ac looks big for this kind of place'
        if both and not (0.33 <= rec_acres / park_acres <= 3): return 'LIKELY', f'same name, size {rec_acres:,.0f} vs {park_acres:,.0f} ac'
        kp, kr = kinds(park), kinds(record)
        if kp and kr and not (kp & kr): return 'LIKELY', f"same name, different kind ({' '.join(sorted(kp))} vs {' '.join(sorted(kr))})"
        return 'SURE', 'same proper name' + (f' ({" ".join(sorted(kp & kr))})' if kp & kr else '')
    if shared and (len(shared) >= 2 or not ponly or not ronly or (len(shared) == 1 and distinctive(next(iter(shared))))) and len(shared) >= 0.5 * min(len(pw), len(rw)):
        if big: return 'UNLIKELY', f'part of the name shared, record {rec_acres:,.0f} ac far bigger than this kind of place'
        return 'LIKELY', f"shared {', '.join(sorted(shared))}; extra: park {', '.join(sorted(ponly)) or '-'} / record {', '.join(sorted(ronly)) or '-'}"
    if shared: return 'UNLIKELY', f"one shared word ({', '.join(sorted(shared))}) only"
    return 'UNLIKELY', 'no shared proper word'


class Learned:
    """What chat 11 already said: never re-ask a NO; demote a layer, or an area's LIKELY tier, that is nearly always wrong."""
    def __init__(self, *question_files):
        self.no, self.by_layer, self.by_area = set(), {}, {}
        for f in question_files:
            try: qs = json.load(open(f, encoding='utf-8')).get('questions') or []
            except (OSError, ValueError, AttributeError): continue
            for q in qs:
                a = str(q.get('answer') or '').upper()
                if not a: continue
                yes = 0 if a.startswith('YES') else 1
                L = self.by_layer.setdefault(q.get('layer'), [0, 0]); L[yes] += 1
                t = q.get('tier') or tier(q.get('park'), q.get('record_name'), q.get('acres_approx'))[0]
                A = self.by_area.setdefault((q.get('area'), t), [0, 0]); A[yes] += 1
                if a.startswith('NO'): self.no.add((q.get('ref'), str(q.get('record')), q.get('layer')))

    def said_no(self, ref, record, layer): return (ref, str(record), layer) in self.no

    def demoted(self, layer, area=None):
        y, n = self.by_layer.get(layer, (0, 0))
        if (y + n) >= 20 and y < 0.1 * (y + n): return True
        y, n = self.by_area.get((area, 'LIKELY'), (0, 0))
        return (y + n) >= 20 and y < 0.1 * (y + n)


if __name__ == '__main__':
    import sys
    for a in [('Greig Creek Streamside Reserve', 'Greig Creek SS.R.', None, None, 1), ('Little Armit River Recreation Site', 'Armit River Recreation Site', 124, None, 1),
              ('Castle Falls Natural Area', 'Castle', 62396, None, 1), ('Fitzgerald National Wild and Scenic River', 'Fitzgerald River', None, None, 1),
              ('Gov. Wentworth State Historic Site', 'Governor Wentworth Historical Site', 96, None, 1), ('Huckleberry Recreation Site BLM Recreation Management Area', 'Huckleberry Campground', 138, None, 1),
              ('Black Kettle Recreation Site', 'Black Kettle', 30105, 40, 1), ('Eyrie Gap Provincial Recreation Area', 'The Kananaskis Country', 115344, None, 1),
              ('Heathlake Woodland Nature Reserve & Site of Special Scientific Interest', 'HEATHLAKE', None, None, 1), ('Murray River K16 Streamside Reserve', 'Murray River K15 SS.R.', None, None, 1),
              ('Rainbow Basin Natural Area', 'Rainbow Basin/Owl Canyon', 4090, None, 1), ('Parc regional Kiamika Regional Park', 'Parc régional du réservoir Kiamika', 33980, None, 1)]:
        print(tier(*a), '|', a[0][:40], '|', a[1][:35])
    sys.exit(0)
