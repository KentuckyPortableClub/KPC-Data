#!/usr/bin/env python3
"""kpc_link_ids.py: what does each park's POTA web link say about the park, WITHOUT opening the website?

Plain words
-----------
POTA gives nearly every park a web link. POTA made that link, not a name match, so it is an independent tie between
the park number and the agency's own page. This tool reads only the link text already saved in the parks list
(KPC-Data data/parkinfo) and works out, for every park:

  agency        whose website it is                              (nps.gov = the National Park Service)
  page kind     own page / shared link / home page / document / page not confirmed / not an agency site / no link
  id kind       what sort of id the address holds                 ("NPS unit code")
  id value      the id itself                                     ("CUGA")
  web name      the name the agency itself uses in the address    (".../state-parks/goliad" -> "goliad")
  name match    does that web name fit the park's POTA name?      (strong / part / none)
  web kind      what kind of place the address says it is         (state park, wildlife management area, ...)
  kind check    does that agree with POTA's own type for the park?
  state check   is the website's state the park's state?

With --key FOLDER (the public key files, KPC-Links data/us-key) it also runs one CHECK, never a match:
  a joined record whose full name is ANOTHER park's own name (POTA name or web name) is listed for a person.
  Agency web names are often the short form ("X WMA"), which is how many map records are named too.

What it never does
------------------
It opens no website and downloads nothing: no network code is in this file. It changes no input file. It writes its
report into a NEW folder. Standard library only. Python 3.8 or newer.

A link id is ONE agreement. It never ties a park to land by itself: the park still needs a matching size or place.

  python kpc_link_ids.py --parkinfo FOLDER [--key FOLDER] [--areas "US CA"] [--out FOLDER]
  python kpc_link_ids.py --selftest
"""
import argparse, collections, csv, datetime, json, os, pathlib, re, sys, tempfile, time
import urllib.parse      # splits a web address into its parts; it does not contact anything

VERSION = '2026-11-20a'

# ---- whose website is it: host -> (agency, the one area it serves or '') -------------------------------------------
AGENCY = {
    'nps.gov': ('US National Park Service', ''), 'fws.gov': ('US Fish and Wildlife Service', ''), 'blm.gov': ('US Bureau of Land Management', ''),
    'fs.usda.gov': ('US Forest Service', ''), 'recreation.gov': ('Recreation.gov (federal)', ''), 'rivers.gov': ('National Wild and Scenic Rivers', ''),
    'pc.gc.ca': ('Parks Canada', ''), 'parks.canada.ca': ('Parks Canada', ''), 'historicplaces.ca': ("Canada's Historic Places", ''),
    'canada.ca': ('Government of Canada', ''), 'bcparks.ca': ('BC Parks', 'CA-BC'), 'www2.gov.bc.ca': ('British Columbia', 'CA-BC'),
    'ontarioparks.com': ('Ontario Parks', 'CA-ON'), 'ontario.ca': ('Ontario', 'CA-ON'), 'albertaparks.ca': ('Alberta Parks', 'CA-AB'),
    'sepaq.com': ('Sepaq (Quebec)', 'CA-QC'), 'environnement.gouv.qc.ca': ('Quebec Environment', 'CA-QC'), 'novascotia.ca': ('Nova Scotia', 'CA-NS'),
    'parks.novascotia.ca': ('Nova Scotia Parks', 'CA-NS'), 'www2.gnb.ca': ('New Brunswick', 'CA-NB'), 'gov.mb.ca': ('Manitoba', 'CA-MB'),
    'parksnl.ca': ('Newfoundland and Labrador Parks', 'CA-NL'), 'gov.nl.ca': ('Newfoundland and Labrador', 'CA-NL'), 'yukon.ca': ('Yukon', 'CA-YT'),
    'nwtparks.ca': ('NWT Parks', 'CA-NT'),
    'dec.ny.gov': ('NY Dept of Environmental Conservation', 'US-NY'), 'parks.ny.gov': ('NY State Parks', 'US-NY'),
    'mdc.mo.gov': ('MO Dept of Conservation', 'US-MO'), 'mostateparks.com': ('MO State Parks', 'US-MO'), 'mass.gov': ('Massachusetts', 'US-MA'),
    'dnr.wisconsin.gov': ('WI Dept of Natural Resources', 'US-WI'), 'pgc.pa.gov': ('PA Game Commission', 'US-PA'), 'dcnr.pa.gov': ('PA DCNR', 'US-PA'),
    'dnr.state.mn.us': ('MN Dept of Natural Resources', 'US-MN'), 'wdfw.wa.gov': ('WA Fish and Wildlife', 'US-WA'), 'parks.wa.gov': ('WA State Parks', 'US-WA'),
    'dnr.wa.gov': ('WA Dept of Natural Resources', 'US-WA'), 'ohiodnr.gov': ('OH Dept of Natural Resources', 'US-OH'), 'parks.ca.gov': ('CA State Parks', 'US-CA'),
    'www2.dnr.state.mi.us': ('MI Dept of Natural Resources', 'US-MI'), 'michigandnr.com': ('MI Dept of Natural Resources', 'US-MI'),
    'cpw.state.co.us': ('CO Parks and Wildlife', 'US-CO'), 'in.gov': ('Indiana', 'US-IN'), 'floridastateparks.org': ('FL State Parks', 'US-FL'),
    'myfwc.com': ('FL Fish and Wildlife', 'US-FL'), 'fdacs.gov': ('FL Forest Service', 'US-FL'), 'sjrwmd.com': ('St. Johns River Water Mgmt District', 'US-FL'),
    'tn.gov': ('Tennessee', 'US-TN'), 'tnstateparks.com': ('TN State Parks', 'US-TN'), 'stateparks.oregon.gov': ('OR State Parks', 'US-OR'),
    'myodfw.com': ('OR Fish and Wildlife', 'US-OR'), 'dnr.maryland.gov': ('MD Dept of Natural Resources', 'US-MD'), 'dnr.illinois.gov': ('IL Dept of Natural Resources', 'US-IL'),
    'dnrhistoric.illinois.gov': ('IL Historic Sites', 'US-IL'), 'portal.ct.gov': ('Connecticut', 'US-CT'), 'tpwd.texas.gov': ('TX Parks and Wildlife', 'US-TX'),
    'thc.texas.gov': ('TX Historical Commission', 'US-TX'), 'georgiawildlife.com': ('GA Wildlife Resources', 'US-GA'), 'gastateparks.org': ('GA State Parks', 'US-GA'),
    'agfc.com': ('AR Game and Fish', 'US-AR'), 'arkansasstateparks.com': ('AR State Parks', 'US-AR'), 'arkansasheritage.com': ('AR Natural Heritage', 'US-AR'),
    'myfwp.mt.gov': ('MT Fish, Wildlife and Parks', 'US-MT'), 'fwp.mt.gov': ('MT Fish, Wildlife and Parks', 'US-MT'), 'outdoornebraska.gov': ('NE Game and Parks', 'US-NE'),
    'iowadnr.gov': ('IA Dept of Natural Resources', 'US-IA'), 'idfg.idaho.gov': ('ID Fish and Game', 'US-ID'), 'parksandrecreation.idaho.gov': ('ID Parks and Recreation', 'US-ID'),
    'wvdnr.gov': ('WV Division of Natural Resources', 'US-WV'), 'wvstateparks.com': ('WV State Parks', 'US-WV'), 'gfp.sd.gov': ('SD Game, Fish and Parks', 'US-SD'),
    'wildlifedepartment.com': ('OK Wildlife Conservation', 'US-OK'), 'mdwfp.com': ('MS Wildlife, Fisheries and Parks', 'US-MS'), 'dnr.alaska.gov': ('AK Dept of Natural Resources', 'US-AK'),
    'dwrapps.utah.gov': ('UT Division of Wildlife Resources', 'US-UT'), 'stateparks.utah.gov': ('UT State Parks', 'US-UT'), 'dlnr.hawaii.gov': ('HI Land and Natural Resources', 'US-HI'),
    'ksoutdoors.com': ('KS Wildlife and Parks', 'US-KS'), 'ksoutdoors.gov': ('KS Wildlife and Parks', 'US-KS'), 'wlf.louisiana.gov': ('LA Wildlife and Fisheries', 'US-LA'),
    'lastateparks.com': ('LA State Parks', 'US-LA'), 'nhstateparks.org': ('NH State Parks', 'US-NH'), 'nh.gov': ('New Hampshire', 'US-NH'),
    'wgfd.wyo.gov': ('WY Game and Fish', 'US-WY'), 'wyoparks.wyo.gov': ('WY State Parks', 'US-WY'), 'dcr.virginia.gov': ('VA Conservation and Recreation', 'US-VA'),
    'dof.virginia.gov': ('VA Dept of Forestry', 'US-VA'), 'gf.nd.gov': ('ND Game and Fish', 'US-ND'), 'history.nd.gov': ('ND Historical Society', 'US-ND'),
    'vtstateparks.com': ('VT State Parks', 'US-VT'), 'fpr.vermont.gov': ('VT Forests, Parks and Recreation', 'US-VT'), 'nj.gov': ('New Jersey', 'US-NJ'),
    'state.nj.us': ('New Jersey', 'US-NJ'), 'dep.nj.gov': ('NJ Environmental Protection', 'US-NJ'), 'southcarolinaparks.com': ('SC State Parks', 'US-SC'),
    'www2.dnr.sc.gov': ('SC Dept of Natural Resources', 'US-SC'), 'apps.web.maine.gov': ('Maine', 'US-ME'), 'maine.gov': ('Maine', 'US-ME'),
    'ncwildlife.gov': ('NC Wildlife Resources', 'US-NC'), 'ncwildlife.org': ('NC Wildlife Resources', 'US-NC'), 'ncparks.gov': ('NC State Parks', 'US-NC'),
    'historicsites.nc.gov': ('NC Historic Sites', 'US-NC'), 'emnrd.nm.gov': ('NM State Parks', 'US-NM'), 'parks.nv.gov': ('NV State Parks', 'US-NV'),
    'azstateparks.com': ('AZ State Parks', 'US-AZ'), 'fw.ky.gov': ('KY Fish and Wildlife', 'US-KY'), 'app.fw.ky.gov': ('KY Fish and Wildlife', 'US-KY'),
    'parks.ky.gov': ('KY State Parks', 'US-KY'), 'eec.ky.gov': ('KY Energy and Environment', 'US-KY'),
}
NOT_AGENCY = re.compile(r'(^|\.)(wikipedia\.org|mapcarta\.com|facebook\.com|alltrails\.com|tripadvisor\.[a-z.]+|google\.[a-z.]+|goo\.gl|youtube\.com|'
                        r'stateparks\.com|arcgis\.com|southwestexplorers\.com|destination4x4\.com|tourismsaskatchewan\.com|novascotia\.com|travelok\.com|'
                        r'wta\.org|hikingproject\.com|recreation\.[a-z]+\.com|yelp\.com|instagram\.com|x\.com|twitter\.com)$')
GOV = re.compile(r'(\.gov|\.gov\.[a-z]{2}|\.mil|\.gc\.ca|\.gouv\.qc\.ca|(^|\.)gov\.[a-z]{2}\.ca|\.state\.[a-z]{2}\.us|\.us)$')

# ---- ids in the address: (host pattern, how to read it) -> (id kind, value) -----------------------------------------
def _q(pu, *keys):
    q = {k.lower(): v for k, v in urllib.parse.parse_qsl(pu.query, keep_blank_values=False)}
    for k in keys:
        if q.get(k): return q[k].strip()
    return ''


def id_rules(host, pu, segs):
    """The id a KNOWN website puts in its address -> (id kind, id value), or None. Each rule was written from the real links."""
    low = [s.lower() for s in segs]
    if host == 'nps.gov' and low and re.fullmatch(r'[a-z]{4}', low[0]) and ' ' not in pu.path: return 'NPS unit code', low[0].upper()
    if host == 'pc.gc.ca' and len(low) >= 3 and low[1] == 'dfhd' and _q(pu, 'id') and not _q(pu, 'i'):
        return 'Parks Canada DFHD id (' + re.sub(r'^page_|_eng\.aspx$|_fra\.aspx$', '', low[2]) + ')', _q(pu, 'id')
    if host == 'historicplaces.ca' and _q(pu, 'id'): return "Canada's Historic Places id", _q(pu, 'id')
    if host == 'dnr.state.mn.us' and _q(pu, 'id'): return 'MN DNR unit id', _q(pu, 'id').upper()
    if host in ('www2.dnr.state.mi.us', 'michigandnr.com') and 'details.aspx' in low and _q(pu, 'id'):
        return 'MI DNR parks and trails id', (_q(pu, 'type').upper() + ':' if _q(pu, 'type') else '') + _q(pu, 'id')
    if host == 'parks.ca.gov' and _q(pu, 'page_id'): return 'CA State Parks page id', _q(pu, 'page_id')
    if host == 'stateparks.oregon.gov' and _q(pu, 'parkid'): return 'OR State Parks park id', _q(pu, 'parkid')
    if host == 'parks.ny.gov' and len(low) >= 2 and low[0] in ('parks', 'historic-sites', 'golf-courses') and low[1].isdigit(): return 'NY State Parks number', low[1]
    if host == 'dec.ny.gov' and len(low) == 2 and re.fullmatch(r'\d+\.html', low[1]): return 'NY DEC page number', low[1][:-5]
    if host == 'myfwp.mt.gov' and _q(pu, 'lmsid'): return 'MT FWP lands id', _q(pu, 'lmsid')
    if host == 'myfwp.mt.gov' and len(low) == 3 and low[1] == 'fas' and low[2].isdigit(): return 'MT FWP lands id', low[2]
    if host == 'agfc.com' and 'zone-map' in low and low[-1].isdigit(): return 'AR Game and Fish map id', low[-1]
    if host == 'tpwd.texas.gov' and 'wma' in low and _q(pu, 'id'): return 'TX Parks and Wildlife WMA id', _q(pu, 'id')
    if host == 'www2.dnr.sc.gov' and len(low) >= 4 and low[2] == 'managedland' and low[3].isdigit(): return 'SC DNR managed land id', low[3]
    if host == 'apps.web.maine.gov' and (_q(pu, 'park_id') or _q(pu, 'state_park')): return 'ME parks id', _q(pu, 'park_id') or _q(pu, 'state_park')
    if host == 'fs.usda.gov' and _q(pu, 'recid'): return 'US Forest Service rec area id', _q(pu, 'recid')
    if host == 'recreation.gov' and len(low) >= 2 and low[-2] == 'gateways' and low[-1].isdigit(): return 'Recreation.gov rec area id', low[-1]
    if host == 'recreation.gov' and len(low) >= 2 and low[-2] in ('campgrounds', 'poi') and low[-1].isdigit(): return 'Recreation.gov facility id', low[-1]
    if host == 'wdfw.wa.gov' and len(low) >= 3 and low[-2] == 'water-access-sites' and low[-1].isdigit(): return 'WA Fish and Wildlife water access id', low[-1]
    if host == 'novascotia.ca' and 'areahandler.ashx' in low and _q(pu, 'id'): return 'NS protected areas id', _q(pu, 'id')
    if host == 'sepaq.com' and len(low) >= 2 and low[0] == 'pq' and re.fullmatch(r'[a-z]{3}', low[1]): return 'Sepaq park code', low[1].upper()
    if host in ('fw.ky.gov', 'app.fw.ky.gov') and _q(pu, 'kdfwr_id', 'id'): return 'KY Fish and Wildlife area id', _q(pu, 'kdfwr_id', 'id')
    return None


RULE_HOSTS = {'nps.gov', 'pc.gc.ca', 'historicplaces.ca', 'dnr.state.mn.us', 'www2.dnr.state.mi.us', 'michigandnr.com', 'parks.ca.gov', 'stateparks.oregon.gov',
              'parks.ny.gov', 'dec.ny.gov', 'myfwp.mt.gov', 'agfc.com', 'tpwd.texas.gov', 'www2.dnr.sc.gov', 'apps.web.maine.gov', 'fs.usda.gov', 'recreation.gov',
              'wdfw.wa.gov', 'novascotia.ca', 'sepaq.com', 'fw.ky.gov', 'app.fw.ky.gov'}     # a website with a rule is never guessed at
ON_MAP = {'NPS unit code'}      # id kinds known to be the same code on the agency's own map layer; every other kind is unchecked
IDKEY = re.compile(r'^(id|.*_id|.*id|recid|site|siteid|unit|unitid|park|parkid|area|areaid|code|num|no|lmsid|pid)$')


def id_guess(pu, segs):
    """An id-looking part of an address on a website with no rule yet -> (id kind, value) marked as a guess, or None."""
    for k, v in urllib.parse.parse_qsl(pu.query):
        if IDKEY.match(k.lower()) and re.fullmatch(r'[A-Za-z]{0,6}\d{2,12}', v.strip()) and k.lower() not in ('page', 'p', 'lang', 'language_id', 'locale'):
            return f'web id ({k})', v.strip()
    for s in reversed(segs):
        if re.fullmatch(r'\d{2,9}', s) and not re.fullmatch(r'(19|20)\d\d', s) and s.strip('0'): return 'web id (number in the address)', s
    return None


# ---- names and kinds ------------------------------------------------------------------------------------------------
GENERIC = {'index', 'home', 'default', 'details', 'detail', 'info', 'information', 'visit', 'about', 'aboutus', 'about-us', 'pages', 'page', 'park', 'parks',
           'maps', 'map', 'planyourvisit', 'basicinfo', 'recreation', 'overview', 'en', 'fr', 'eng', 'fra', 'detail_report', 'main', 'welcome', 'directions',
           'history', 'learn', 'historyculture', 'files', 'pdf', 'pdfs', 'documents', 'uploads', 'content', 'download', 'location', 'locations', 'property'}
EXT = re.compile(r'\.(html?|aspx?|php|cfm|shtml|dot|action|pl|jsp|pdf|png|jpe?g|ashx)$', re.I)
DOC = re.compile(r'\.(pdf|png|jpe?g|docx?|xlsx?|kmz|kml|zip)$', re.I)
STOP = {'the', 'of', 'and', 'at', 'in', 'a', 'an', 'on', 'for', 'de', 'du', 'la', 'le', 'des', 'st', 'saint', 'mt', 'mount', 'no'}
KINDWORDS = {'state', 'park', 'parks', 'national', 'provincial', 'wildlife', 'management', 'area', 'areas', 'forest', 'refuge', 'historic', 'historical', 'site',
             'recreation', 'recreational', 'conservation', 'natural', 'nature', 'preserve', 'reserve', 'game', 'land', 'lands', 'wma', 'sp', 'sf', 'nwr', 'sna', 'swa',
             'sgl', 'sra', 'shs', 'nhs', 'wsa', 'hma', 'memorial', 'monument', 'trail', 'river', 'lake', 'fishing', 'access', 'public', 'unit', 'tract', 'wilderness',
             'study', 'herd', 'heritage', 'scenic', 'wild', 'ecological', 'county', 'regional', 'municipal', 'city', 'beach', 'marine', 'seashore', 'lakeshore',
             'battlefield', 'military', 'fish', 'hatchery', 'waterfowl', 'production', 'sanctuary', 'habitat', 'protected', 'easement', 'grassland', 'grasslands'}
SHORT = {'wma': 'wildlife management area', 'sp': 'state park', 'sf': 'state forest', 'nwr': 'national wildlife refuge', 'sna': 'state natural area',
         'swa': 'state wildlife area', 'sgl': 'state game land', 'sra': 'state recreation area', 'shs': 'state historic site', 'nhs': 'national historic site',
         'np': 'national park', 'nf': 'national forest', 'nm': 'national monument', 'nra': 'national recreation area', 'wsa': 'wilderness study area',
         'hma': 'herd management area', 'pp': 'provincial park', 'shp': 'state historic park', 'sfl': 'state fishing lake', 'sfwa': 'state fish and wildlife area',
         'sga': 'state game area', 'nhp': 'national historical park', 'wa': 'wildlife area', 'ca': 'conservation area'}
KINDS = [   # (kind, what the address or POTA's type must contain); the first that fits wins, so the narrow ones come first
    ('historic site', r'historic-?(site|park|place)|(^|-)(nhs|shs|nhp|shp)(-|$)|lhn-nhs|historicsites|heritage'),
    ('wildlife management area', r'wildlife-?management-?area|(^|-)wmas?(-|$)|wma-|-wma'),
    ('wildlife refuge', r'refuge|(^|-)nwr(-|$)|waterfowl-?production'),
    ('wildlife area', r'wildlife-?areas?|(^|-)(swa|sfwa)(-|$)|game-?lands?|game-?area|(^|-)(sgl|sga)(-|$)|habitat|conservation-?area|(^|-)whma(-|$)'),
    ('natural area', r'natural-?areas?|nature-?(preserve|reserve)s?|(^|-)sna(s)?(-|$)|ecological-?reserve|ec-reserves|protected-?(natural-?)?areas?|preserve|reserves?'),
    ('forest', r'forests?|forestry|(^|-)(sf|nf)(-|$)'),
    ('recreation area', r'recreation-?areas?|rec-area|(^|-)(sra|nra)(-|$)'),
    ('wilderness', r'wilderness|(^|-)wsa(-|$)'),
    ('herd management area', r'herd-?management|(^|-)hma(-|$)'),
    ('trail', r'trails?(-|$)|(^|-)(nht|nst)(-|$)|watertrail'),
    ('river', r'wild-?and-?scenic|scenic-?river|(^|-)river(s)?(-|$)'),
    ('fishing or water access', r'fishing|hatcher|(^|-)(fas|sfl)(-|$)|water-?access|boat|lakes(-|$)'),
    ('monument or memorial', r'monument|memorial|battlefield'),
    ('park', r'parks?(-|$)|(^|-)(sp|np|pp)(-|$)|pn-np|seashore|lakeshore|beach'),
]
KINDS = [(k, re.compile(rx)) for k, rx in KINDS]
STRICT = [   # for the place's OWN words in the address: only a full designation counts, never a bare 'river', 'lake', 'forest' or 'park' inside a name
    ('historic site', r'(state|national|provincial)-historic-(site|park)|(^|-)(nhs|shs|nhp|shp)$'),
    ('wildlife management area', r'wildlife-management-area|(^|-)wma(-|$)'),
    ('wildlife refuge', r'wildlife-refuge|(^|-)nwr(-|$)'),
    ('wildlife area', r'wildlife-area|(^|-)(swa|sfwa|sgl|sga)(-|$)|state-game-lands?|conservation-area'),
    ('natural area', r'natural-area|nature-(preserve|reserve)|(^|-)sna(-|$)|ecological-reserve'),
    ('forest', r'(state|national|provincial)-forest|(^|-)(sf|nf)$'),
    ('recreation area', r'recreation-area|(^|-)(sra|nra)(-|$)'),
    ('wilderness', r'wilderness-(study-)?area|(^|-)wsa(-|$)|-wilderness$'),
    ('herd management area', r'herd-management-area|(^|-)hma(-|$)'),
    ('park', r'(state|national|provincial|regional|county)-park|(^|-)(sp|np|pp)$'),
]
STRICT = [(k, re.compile(rx)) for k, rx in STRICT]
FAMILY = {'park': 'park', 'recreation area': 'park', 'historic site': 'park', 'monument or memorial': 'park', 'trail': 'park', 'river': 'park',
          'wildlife management area': 'wildlife', 'wildlife area': 'wildlife', 'wildlife refuge': 'wildlife', 'fishing or water access': 'wildlife',
          'herd management area': 'wildlife', 'natural area': 'nature', 'wilderness': 'nature', 'forest': 'forest'}


def words(text):
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', urllib.parse.unquote(str(text or '')))
    return [w for w in re.split(r'[^a-z0-9]+', t.lower().replace("'", '').replace('’', '')) if w]


def kinds_of(text, table=None):
    t = '-'.join(words(text))
    return [k for k, rx in (table or KINDS) if rx.search(t)]


def full_name(text):
    """A name squeezed for an exact comparison: lower case, no punctuation, 'the' dropped, short forms spelled out."""
    out = []
    for w in words(text):
        if w == 'the': continue
        out.extend(SHORT.get(w, w).split())
    return ' '.join(out)


def split_link(link):
    u = str(link or '').strip()
    if not u: return None, '', []
    u = u.split()[0]                                           # two links pasted into one cell: the first one counts
    if not re.match(r'[a-z][a-z0-9+.-]*://', u, re.I): u = 'http://' + u
    try: pu = urllib.parse.urlsplit(u)
    except ValueError: return None, '', []
    host = (pu.hostname or '').lower().rstrip('.')
    if host.startswith('www.'): host = host[4:]
    if '.' not in host: return None, '', []
    return pu, host, [s for s in pu.path.split('/') if s]


def web_name(segs):
    """The agency's own words for the place, taken from the address: the last part that is not a filler word or a number."""
    for s in reversed(segs):
        base = EXT.sub('', urllib.parse.unquote(s))
        w = words(base)
        if not w or all(x.isdigit() for x in w) or base.lower() in GENERIC or (len(w) == 1 and w[0] in GENERIC): continue
        return ' '.join(w)
    return ''


def name_match(park_name, wname):
    if not wname: return 'no name in the address'
    pw = [w for w in words(park_name) if w not in STOP]
    key = [w for w in pw if w not in KINDWORDS] or pw
    ww = set(words(wname)); squashed = ''.join(words(wname))
    hit = sum(1 for w in key if w in ww or (len(w) >= 4 and w in squashed))
    if key and hit == len(key): return 'strong'
    return 'part' if key and hit * 2 >= len(key) and hit else 'none'


def read_link(link, park_name='', pota_type='', area='', areas=()):
    """Everything one link says, with no network: a dict of the report's columns (page kind is finished later, once shared links are known)."""
    pu, host, segs = split_link(link)
    r = {'host': host, 'agency': '', 'site': '', 'id_kind': '', 'id_value': '', 'id_grade': '', 'web_name': '', 'name_match': '', 'web_kind': '',
         'kind_check': '', 'state_check': '', 'norm': '', 'page': ''}
    if not str(link or '').strip(): r['page'] = 'no link'; return r
    if pu is None: r['page'] = 'bad link'; return r
    ag = AGENCY.get(host)
    if ag is None and host.count('.') >= 2 and host.split('.', 1)[1] in AGENCY and host.split('.', 1)[1] not in ('in.gov', 'tn.gov', 'nj.gov', 'nh.gov', 'mass.gov', 'maine.gov', 'canada.ca', 'ontario.ca'):
        ag = AGENCY[host.split('.', 1)[1]]
    r['agency'] = ag[0] if ag else host
    r['site'] = 'agency (known)' if ag else 'not an agency site' if NOT_AGENCY.search(host) else 'government site' if GOV.search(host) else 'other site'
    r['norm'] = host + '/' + '/'.join(segs).lower() + ('?' + pu.query.lower() if pu.query else '')
    if ag and ag[1] and area and area.startswith(('US-', 'CA-')): r['state_check'] = 'same state' if ag[1] == area or ag[1] in areas else f'OTHER STATE ({ag[1]})'
    got = id_rules(host, pu, segs)
    if got: r['id_kind'], r['id_value'], r['id_grade'] = got[0], got[1], 'known'
    elif r['site'] != 'not an agency site' and host not in RULE_HOSTS:
        g = id_guess(pu, segs)
        if g: r['id_kind'], r['id_value'], r['id_grade'] = g[0], g[1], 'guess'
    if not (got and got[0] == 'NPS unit code'): r['web_name'] = web_name(segs)
    r['name_match'] = name_match(park_name, r['web_name'])
    # the kind of place: from the place's own words in the address first; failing that, from the website section just above it
    wk = kinds_of(r['web_name'], STRICT) if r['site'] != 'not an agency site' else []; where = 'name'
    if not wk and len(segs) >= 2 and r['site'] != 'not an agency site': wk = kinds_of(segs[-2]); where = 'section'
    pk = kinds_of(pota_type)
    r['web_kind'] = wk[0] if wk else ''
    if wk and pk:
        same = {FAMILY[k] for k in wk} & {FAMILY[k] for k in pk}
        r['kind_check'] = 'agrees' if same else (f'DIFFERS (POTA says {pk[0]})' if where == 'name' else f'differs? by website section (POTA says {pk[0]})')
    last = segs[-1] if segs else ''
    if r['site'] == 'not an agency site': r['page'] = 'not an agency site'
    elif not pu.query and (not segs or all(EXT.sub('', s).lower() in GENERIC for s in segs)): r['page'] = 'home page'
    elif DOC.search(last): r['page'] = 'document'
    else: r['page'] = 'own page' if (r['id_grade'] == 'known' or r['name_match'] in ('strong', 'part')) else 'page not confirmed'
    return r


# ---- the run --------------------------------------------------------------------------------------------------------
def say(*a):
    print(*a, flush=True)


def load_parks(folder, areas):
    d = pathlib.Path(folder).expanduser()
    if not d.is_dir(): raise SystemExit(f'STOP: parks list folder not found: {d}')
    files = sorted(p for p in d.glob('*.json') if not areas or any(p.stem == a or p.stem.startswith(a + '-') for a in areas))
    if not files: raise SystemExit(f'STOP: no park files (*.json) in {d}' + (f' for areas {" ".join(areas)}' if areas else ''))
    parks, bad = {}, []
    for p in files:
        try: doc = json.loads(p.read_text(encoding='utf-8'))
        except (OSError, ValueError) as e: bad.append(f'{p.name}: {e}'); continue
        for ref, row in ((doc.get('parks') if isinstance(doc, dict) else None) or {}).items():
            if not isinstance(row, list) or not row: continue
            area = p.stem
            if area == 'CA' and len(row) > 10 and isinstance(row[10], str) and row[10]: area = 'CA-' + row[10]
            if ref in parks:
                if area not in parks[ref]['areas']: parks[ref]['areas'].append(area)
                continue
            parks[ref] = {'name': str(row[0] or ''), 'link': str(row[1] or '') if len(row) > 1 else '', 'type': str(row[2] or '') if len(row) > 2 else '',
                          'area': area, 'areas': [area]}
    return parks, files, bad


def run(parkinfo, key=None, out=None, areas=None):
    t0 = time.time()
    parks, files, bad = load_parks(parkinfo, areas or [])
    out_root = pathlib.Path(out).expanduser() if out else pathlib.Path.cwd() / 'link-ids-out'
    stamp, n = 'link-ids-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'), 1
    out_dir = out_root / stamp
    while out_dir.exists(): n += 1; out_dir = out_root / f'{stamp}-{n}'
    out_dir.mkdir(parents=True)
    say(f'Read {len(parks):,} parks from {len(files)} file(s) in {files[0].parent}')
    rows = {ref: read_link(p['link'], p['name'], p['type'], p['area'], p['areas']) for ref, p in parks.items()}
    shared = collections.Counter(r['norm'] for r in rows.values() if r['norm'])
    idshare = collections.Counter((r['id_kind'], r['id_value']) for r in rows.values() if r['id_grade'] == 'known')
    for ref, r in rows.items():
        r['shared_by'] = shared[r['norm']] if r['norm'] else 0
        r['id_shared_by'] = idshare[(r['id_kind'], r['id_value'])] if r['id_grade'] == 'known' else 0
        if r['shared_by'] > 1 and r['page'] in ('own page', 'page not confirmed', 'document', 'home page'): r['page'] = 'shared link'
        r['ties'] = 'yes' if r['page'] == 'own page' and r['id_grade'] == 'known' and r['id_shared_by'] == 1 and not r['state_check'].startswith('OTHER') else ''

    with open(out_dir / 'link-ids.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['park', 'area', 'POTA type', 'website', 'agency', 'site', 'page kind', 'link shared by (parks)', 'id kind', 'id value', 'id is', 'id shared by (parks)',
                    'usable as a link id', 'web name', 'name match', 'web kind', 'kind check', 'state check'])
        for ref in sorted(parks):
            p, r = parks[ref], rows[ref]
            w.writerow([ref, ' '.join(p['areas']), p['type'], r['host'], r['agency'], r['site'], r['page'], r['shared_by'] or '', r['id_kind'], r['id_value'], r['id_grade'],
                        r['id_shared_by'] or '', r['ties'], r['web_name'], r['name_match'], r['web_kind'], r['kind_check'], r['state_check']])
    by = collections.defaultdict(collections.Counter)
    for ref, r in rows.items():
        if not r['host']: continue
        c = by[(r['agency'], r['host'])]; c['parks'] += 1; c[r['page']] += 1
        c['known id'] += r['id_grade'] == 'known'; c['guess id'] += r['id_grade'] == 'guess'; c['usable'] += r['ties'] == 'yes'
        c['strong'] += r['name_match'] == 'strong' and r['page'] == 'own page'; c['kind differs'] += r['kind_check'].startswith('DIFFERS'); c['other state'] += r['state_check'].startswith('OTHER')
        if r['id_grade'] == 'known': c['kind:' + r['id_kind']] += 1
    with open(out_dir / 'by-website.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['agency', 'website', 'parks', 'own page', 'shared link', 'home page', 'document', 'page not confirmed', 'with a known id', 'usable as a link id',
                    'with a guessed id', 'own page with a strong name match', 'kind differs from POTA', 'another state', 'id kinds'])
        for (ag, host), c in sorted(by.items(), key=lambda kv: (-kv[1]['parks'], kv[0])):
            w.writerow([ag, host, c['parks'], c['own page'], c['shared link'], c['home page'], c['document'], c['page not confirmed'], c['known id'], c['usable'], c['guess id'],
                        c['strong'], c['kind differs'], c['other state'], '; '.join(f'{k[5:]} ({v})' for k, v in c.items() if k.startswith('kind:'))])

    flags = name_flags(parks, rows, key, out_dir) if key else None

    tot = collections.Counter(r['page'] for r in rows.values())
    kinds = collections.Counter(r['id_kind'] for r in rows.values() if r['id_grade'] == 'known')
    usable = collections.Counter(r['id_kind'] for r in rows.values() if r['ties'] == 'yes')
    nshared = sum(1 for (k, v), c in idshare.items() if c > 1)
    T = [f'KPC link ids {VERSION}   made {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}   Python {sys.version.split()[0]}',
         f'Parks list read: {files[0].parent}   ({len(files)} files, {len(parks):,} parks)', '',
         'WHAT EACH PARK\'S LINK IS']
    for k in ('own page', 'shared link', 'home page', 'document', 'page not confirmed', 'not an agency site', 'bad link', 'no link'):
        T.append(f'  {tot[k]:>7,}  {k}')
    T += ['', 'IDS FOUND IN THE ADDRESS (websites with a rule)']
    for k, v in kinds.most_common(): T.append(f'  {v:>7,}  {k:<44} usable as a link id: {usable[k]:,}' + ('   (same code is on the map layer)' if k in ON_MAP else ''))
    T += [f'  {sum(kinds.values()):>7,}  in all; usable as a link id: {sum(usable.values()):,}',
          f'  "Usable" = the park\'s own page, a known id, no other park has the same id, and the website is in the park\'s state.',
          f'  Only the Park Service code is KNOWN to be on a map layer too. Every other kind above is an id on the WEBSITE: check it against',
          f'  the ID finder\'s fields for that agency\'s layer before counting on it. A web page number usually is not on the map.',
          f'  {nshared:,} ids are shared by two or more parks. A shared id is not a tie on its own.',
          f'  {sum(1 for r in rows.values() if r["id_grade"] == "guess"):,} more addresses hold something that LOOKS like an id (a guess, on a website with no rule yet).', '',
          'THE AGENCY\'S OWN NAME IN THE ADDRESS (no id needed)',
          f'  {sum(1 for r in rows.values() if r["page"] == "own page" and r["name_match"] == "strong"):>7,}  own pages whose address names the park in full (strong)',
          f'  {sum(1 for r in rows.values() if r["page"] == "own page" and r["name_match"] == "part"):>7,}  own pages whose address names part of it',
          f'  {sum(1 for r in rows.values() if r["page"] == "page not confirmed"):>7,}  pages where the address neither names the park nor holds a known id', '',
          'CHECKS ON THE LINK ITSELF',
          f'  {sum(1 for r in rows.values() if r["kind_check"].startswith("DIFFERS")):>7,}  the place\'s own words in the address say a different kind than POTA\'s type (look at these)',
          f'  {sum(1 for r in rows.values() if r["kind_check"].startswith("differs?")):>7,}  only the website section says a different kind (a weak hint)',
          f'  {sum(1 for r in rows.values() if r["state_check"].startswith("OTHER")):>7,}  the website belongs to another state\'s agency (likely a wrong link, or a border park)', '']
    if flags is not None:
        T += ['THE NAME CHECK AGAINST THE KEY (a check only; nothing is matched or moved)',
              f'  {flags["parks"]:>7,}  joined parks looked at, {flags["rows"]:,} joined records',
              f'  {flags["flag"]:>7,}  joined records whose full name is ANOTHER park\'s own name in the same state, on {flags["flag_parks"]:,} parks ({len(flags["pairs"]):,} park pairs)',
              f'  {flags["web_only"]:>7,}  of those are caught only through the other park\'s WEB name (POTA\'s wording alone misses them)',
              f'  The list is in PRIVATE-name-flags.csv. It names parks and records: keep it with the store.', '']
    T += ['HOW TO READ IT',
          '  A link id is ONE agreement. A park still needs a matching size or place before it is tied to land.',
          '  Compare a link id only with a map id of the SAME kind. A web page number is usually not the id on the map layer.',
          '  A dead or wrong link cannot be seen from here: nothing is opened. The id must still be found in the agency\'s own list.',
          '  "web name" and "web kind" are read from the address only. They are new facts for the plan: the reviewer decides if they may be used.', '',
          'FILES', '  link-ids.csv     one line per park', '  by-website.csv   one line per website: how many parks, own pages, ids',
          '  All of it comes from POTA\'s public park list. Nothing here is from the store.']
    if bad: T += ['', 'WARNINGS'] + ['  ' + b for b in bad]
    T += ['', f'Run time {time.time() - t0:.1f}s. No website was opened and no input file was changed.']
    (out_dir / 'summary.txt').write_text('\n'.join(T) + '\n', encoding='utf-8')
    say('')
    for line in T: say(line)
    say(''); say(f'Report folder: {out_dir}')
    return out_dir


def name_flags(parks, rows, key, out_dir):
    """A CHECK against the public key: a joined record whose full name is another park's own name (POTA name or web name) in the same state."""
    d = pathlib.Path(key).expanduser()
    if not d.is_dir(): raise SystemExit(f'STOP: key folder not found: {d}')
    out = {'parks': 0, 'rows': 0, 'flag': 0, 'flag_parks': 0, 'web_only': 0, 'pairs': set()}; lines = []
    for kf in sorted(d.glob('*.json')):
        try: doc = json.loads(kf.read_text(encoding='utf-8'))
        except (OSError, ValueError): continue
        kp = doc.get('parks') if isinstance(doc, dict) else None
        if not isinstance(kp, dict): continue
        own = collections.defaultdict(set); viaweb = collections.defaultdict(set)      # full name -> parks of this area that carry it
        for ref, p in kp.items():
            if not isinstance(p, dict): continue
            pn = full_name(p.get('n') or (parks.get(ref) or {}).get('name'))
            if pn: own[pn].add(ref)
            r = rows.get(ref)
            if r and r['page'] == 'own page' and r['name_match'] == 'strong' and r['web_name']:
                # the agency's wording of this park's name. A bare name ("big lake") is not a full name: it gets the park's own kind
                # added ("big lake national wildlife refuge"), the way a list's bare name gets the list's kind.
                wn = full_name(r['web_name'] if kinds_of(r['web_name'], STRICT) else r['web_name'] + ' ' + (parks.get(ref) or {}).get('type', ''))
                if wn and wn != pn and len(wn.split()) >= 3: viaweb[wn].add(ref)
        for ref, p in kp.items():
            if not isinstance(p, dict) or not p.get('m'): continue
            out['parks'] += 1; hit = False
            mine = {full_name(p.get('n'))} | ({full_name(rows[ref]['web_name'])} if ref in rows and rows[ref]['web_name'] else set())
            mine_loose = {' '.join(w for w in m.split() if w != 'state') for m in mine}      # "X State Wildlife Area" and "X Wildlife Area" are one name
            for row in p['m']:
                if not isinstance(row, list) or len(row) < 2: continue
                out['rows'] += 1; rn = full_name(row[1])
                if not rn or rn in mine or ' '.join(w for w in rn.split() if w != 'state') in mine_loose: continue
                a = own.get(rn, set()) - {ref}; b = viaweb.get(rn, set()) - {ref}
                others = a | b
                if len(others) != 1: continue                    # no other park, or two: not a clear case
                other = next(iter(others)); only_web = not a
                out['flag'] += 1; out['web_only'] += only_web; hit = True; out['pairs'].add((ref, other))
                lines.append([kf.stem, ref, p.get('n') or '', row[0], row[1], row[3] if len(row) > 3 else '', other, (kp.get(other) or {}).get('n') or '',
                              'web name only' if only_web else 'POTA name'])
            out['flag_parks'] += hit
    with open(out_dir / 'PRIVATE-name-flags.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['area', 'park', 'park name', 'joined record id', 'joined record name', 'how it was joined', "the park whose own name that is", 'its name', 'found through'])
        w.writerows(lines)
    return out


# ---- the built-in self-test (invented parks and ids on real agency web addresses; nothing is opened) ----------------
def selftest():
    say(f'KPC link ids {VERSION} self-test (invented parks; no website is opened)')
    bad = []
    def check(what, got, want):
        ok = got == want
        say(f'  {"ok  " if ok else "FAIL"} {what}' + ('' if ok else f': got {got!r}, wanted {want!r}'))
        if not ok: bad.append(what)
    def L(link, name='', typ='', area='', areas=()): return read_link(link, name, typ, area, areas)
    r = L('https://www.nps.gov/zzqq/index.htm', 'Invented Gap National Historical Park', 'National Historical Park', 'US-KY')
    check('Park Service link gives the 4-letter code', (r['agency'], r['id_kind'], r['id_value'], r['page']), ('US National Park Service', 'NPS unit code', 'ZZQQ', 'own page'))
    check('Park Service home page gives no id', (L('https://www.nps.gov/index.htm')['id_kind'], L('https://nps.gov')['page']), ('', 'home page'))
    check('a Park Service article page is not a unit code', L('https://www.nps.gov/articles/000/invented-wild-and-scenic-river.htm')['id_kind'], '')
    r = L('https://www.dnr.state.mn.us/state_parks/park.html?id=spk00999#homepage', 'Invented Falls State Park', 'State Park', 'US-MN')
    check('Minnesota id= is read, the #part is ignored, and the state matches', (r['id_kind'], r['id_value'], r['state_check'], r['web_kind']), ('MN DNR unit id', 'SPK00999', 'same state', 'park'))
    check('California page_id', L('https://www.parks.ca.gov/?page_id=99999')['id_value'], '99999')
    check('Oregon parkId', L('https://stateparks.oregon.gov/index.cfm?do=park.profile&parkId=9999')['id_kind'], 'OR State Parks park id')
    check('Michigan id and type', L('https://www2.dnr.state.mi.us/ParksandTrails/Details.aspx?id=9999&type=SPRK')['id_value'], 'SPRK:9999')
    check('Parks Canada DFHD id', L('https://www.pc.gc.ca/apps/dfhd/page_nhs_eng.aspx?id=99999')['id_kind'], 'Parks Canada DFHD id (nhs)')
    check('Forest Service recid', L('https://www.fs.usda.gov/recarea/zzzz/recarea/?recid=99999')['id_value'], '99999')
    r = L('https://tpwd.texas.gov/state-parks/invented-creek', 'Invented Creek State Park', 'State Park', 'US-TX')
    check('no id, but the address names the park: own page, strong', (r['id_kind'], r['web_name'], r['name_match'], r['page'], r['kind_check']), ('', 'invented creek', 'strong', 'own page', 'agrees'))
    r = L('https://dnr.wisconsin.gov/topic/Lands/WildlifeAreas/inventedmarsh.html', 'Invented Marsh State Wildlife Area', 'State Wildlife Area', 'US-WI')
    check('a run-together address still matches the name', (r['name_match'], r['web_kind']), ('strong', 'wildlife area'))
    r = L('https://www.tn.gov/twra/wildlife-management-areas/middle-tennessee-r2/invented-lake-wma.html', 'Invented Lake State Park', 'State Park', 'US-TN')
    check('the address says wildlife management area, POTA says state park: flagged', r['kind_check'], 'DIFFERS (POTA says park)')
    check('a state recreation area on a state parks website is not a difference', L('https://stateparks.utah.gov/parks/invented-reservoir/', 'Invented Reservoir State Recreation Area', 'State Recreation Area')['kind_check'], 'agrees')
    check('a state code in the address is not read as a kind', L('https://www.blm.gov/programs/national-conservation-lands/oregon-washington/invented-canyon-wsa', 'Invented Canyon Wilderness Study Area', 'Wilderness Study Area')['kind_check'], 'agrees')
    check('a query-only address with an id is the park\'s own page, not a home page', L('https://www.parks.ca.gov/?page_id=99999', 'Invented Beach State Park')['page'], 'own page')
    check('a park in two states: its website may be in either', L('https://parks.nv.gov/parks/invented-lake', 'Invented Lake State Park', 'State Park', 'US-CA', ('US-CA', 'US-NV'))['state_check'], 'same state')
    check('a link to another state\'s agency is flagged', L('https://mdc.mo.gov/discover-nature/places/invented-conservation-area', 'Invented Conservation Area', '', 'US-IL')['state_check'], 'OTHER STATE (US-MO)')
    check('Wikipedia is not an agency site', L('https://en.wikipedia.org/wiki/Invented_State_Park', 'Invented State Park')['page'], 'not an agency site')
    check('a PDF is a document', L('https://wvdnr.gov/wp-content/uploads/2022/11/InventedWMA_11x17.pdf', 'Invented WMA')['page'], 'document')
    check('a page that neither names the park nor holds a known id is not confirmed', L('https://www.blm.gov/visit/some-other-place', 'Invented Canyon')['page'], 'page not confirmed')
    check('an unknown government site: id is only a guess', (lambda x: (x['site'], x['id_grade'], x['id_value']))(L('https://parks.example.gov/unit?id=12345', 'Invented Park')), ('government site', 'guess', '12345'))
    check('a year in the address is not an id', L('https://parks.example.gov/2023/invented-park', 'Invented Park')['id_value'], '')
    check('no link, bad link', (L('')['page'], L('not a link at all')['page']), ('no link', 'bad link'))
    check('two links pasted in one cell: the first one counts', L('https://www.nps.gov/zzqq/index.htm https://www.rivers.gov/rivers/x.php')['id_value'], 'ZZQQ')
    check('short forms are spelled out for an exact comparison', full_name('The Invented Lake WMA'), 'invented lake wildlife management area')
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp); pi = tmp / 'parkinfo'; pi.mkdir(); ky = tmp / 'us-key'; ky.mkdir()
        P = {'US-9001': ['Invented Gap National Park', 'https://www.nps.gov/zzqq/index.htm', 'National Park', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9002': ['Invented Gap National Preserve', 'https://www.nps.gov/zzqq/index.htm', 'National Preserve', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9003': ['Invented Fort National Historic Site', 'https://www.nps.gov/zzff/index.htm', 'National Historic Site', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9004': ['Invented Lake State Wildlife Management Area', 'https://fw.ky.gov/areas/invented-lake-wma', 'Wildlife Management Area', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9005': ['Invented State Wildlife Management Area', 'https://fw.ky.gov/areas/invented-wma', 'Wildlife Management Area', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9006': ['Invented Hollow State Game Land', 'https://fw.ky.gov/lands/list.aspx', 'State Game Land', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9007': ['Invented Ridge State Game Land', 'https://fw.ky.gov/lands/list.aspx', 'State Game Land', '', '', 37.0, -84.0, 0, 0, 0, 'KY'],
             'US-9008': ['Invented Nowhere', '', '', '', '', 37.0, -84.0, 0, 0, 0, 'KY']}
        (pi / 'US-KY.json').write_text(json.dumps({'parks': P, 'program': 'US', 'sites': {}}), encoding='utf-8')
        before = (pi / 'US-KY.json').read_bytes()
        K = {'US-9004': {'n': 'Invented Lake State Wildlife Management Area', 'm': [['a1', 'Invented Lake WMA', 2000, 'reviewed'], ['a2', 'Invented WMA', 19000, 'name']]},
             'US-9005': {'n': 'Invented State Wildlife Management Area', 'm': [['a2', 'Invented WMA', 19000, 'reviewed'], ['a1', 'Invented Lake WMA', 2000, 'name']]},
             'US-9003': {'n': 'Invented Fort National Historic Site', 'm': [['b1', 'Invented Fort NHS', 12, 'NPS']]},
             'US-9006': {'n': 'Invented Hollow State Game Land', 'm': [['c1', 'Invented Hollow Game Land', 300, 'name']]}}
        (ky / 'US-KY.json').write_text(json.dumps({'parks': K}), encoding='utf-8')
        out = run(pi, key=ky, out=tmp / 'report')
        rows = {r['park']: r for r in csv.DictReader((out / 'link-ids.csv').read_text(encoding='utf-8-sig').splitlines())}
        check('the parks list is unchanged after the run', (pi / 'US-KY.json').read_bytes(), before)
        check('one code on two parks: both are "shared link", neither is usable', [(rows[k]['page kind'], rows[k]['id shared by (parks)'], rows[k]['usable as a link id']) for k in ('US-9001', 'US-9002')],
              [('shared link', '2', ''), ('shared link', '2', '')])
        check('a code on one park only is usable', (rows['US-9003']['id value'], rows['US-9003']['usable as a link id']), ('ZZFF', 'yes'))
        check('a list page used by two parks is a shared link', rows['US-9006']['page kind'], 'shared link')
        flags = list(csv.DictReader((out / 'PRIVATE-name-flags.csv').read_text(encoding='utf-8-sig').splitlines()))
        check('the Cheatham pattern: each park holds a record carrying the OTHER park\'s own name, and both are flagged',
              sorted((f['park'], f['joined record name'], f["the park whose own name that is"]) for f in flags),
              [('US-9004', 'Invented WMA', 'US-9005'), ('US-9005', 'Invented Lake WMA', 'US-9004')])
        check('a park\'s own record is never flagged, also when the record leaves out the word State', [f for f in flags if f['park'] in ('US-9003', 'US-9006')], [])
        txt = (out / 'summary.txt').read_text(encoding='utf-8')
        check('the summary counts the shared id', '1 ids are shared by two or more parks' in txt, True)
    src = pathlib.Path(__file__).read_text(encoding='utf-8')
    check('this file holds no code that opens a website', [w for w in ('urlopen', 'urllib.request', 'http.client', 'socket', 'requests', 'subprocess') if w in src.split('def selftest')[0]], [])
    say(''); say('SELF-TEST PASSED' if not bad else f'SELF-TEST FAILED: {len(bad)} check(s): ' + '; '.join(bad))
    return 0 if not bad else 1


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(errors='replace')
        except Exception: pass   # noqa: BLE001
    ap = argparse.ArgumentParser(description="What each park's POTA web link says, without opening any website.")
    ap.add_argument('folder', nargs='?', help='the parks list folder (same as --parkinfo)')
    ap.add_argument('--parkinfo', help='KPC-Data data/parkinfo')
    ap.add_argument('--key', help='optional: KPC-Links data/us-key, for the name check')
    ap.add_argument('--areas', help='which files to read, e.g. "US CA" (default: every file in the folder)')
    ap.add_argument('--out', help='where the report folder is made (default: link-ids-out in the current folder)')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    say(f'KPC link ids {VERSION}   Python {sys.version.split()[0]}   {sys.platform}')
    if a.selftest: return selftest()
    src = a.parkinfo or a.folder
    if not src: ap.error('give the parks list folder')
    run(src.strip('"'), a.key.strip('"') if a.key else None, a.out, (a.areas or '').split())
    return 0


if __name__ == '__main__':
    sys.exit(main())
