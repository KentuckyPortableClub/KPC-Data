"""The shared findings log (Engine spec PART 3.4; method §10 'pass a good trick sideways').

ONE append-only `findings.jsonl` in --out. Every worker reads it at the start and appends the moment it learns something
reusable; every plug-in looks up its agency's / host's findings before working. Rows:
  {date, agency?, host?, kind, value?, old?, new?, url?, note, by}
kinds: name-field | renumbered | agency-wide-page | blocked | points-only | wrong-layer | pin-typo-pattern | renamed | delisted |
       case-sensitive-like | buffer | parcel-fallback | token-only
The seed below is FINDINGS_LOG_Canada_HardLook.md, typed in by hand once (Engine spec: 'by hand, once')."""
import datetime as dt, json, pathlib, threading

SEED = [
    {'host': 'services.arcgis.com', 'agency': 'Yukon Parks', 'kind': 'name-field', 'value': 'REMARKS', 'note': 'Yukon Parks and Campgrounds - Surveyed: names are in REMARKS'},
    {'agency': 'Parks Canada', 'kind': 'name-field', 'value': 'SectionEn', 'note': 'Parks Canada TIMS trails: match on SectionEn'},
    {'agency': 'City of Kingston', 'host': 'api.cityofkingston.ca', 'kind': 'name-field', 'value': 'NOTES_NAME_OF_BLDG', 'url': 'api.cityofkingston.ca .../Planning/NationalHistoricSite/FeatureServer/2'},
    {'agency': 'ECCC', 'host': 'maps-cartes.ec.gc.ca', 'kind': 'case-sensitive-like', 'value': 'NAME_E', 'note': 'CPCAD NAME_E LIKE is case-sensitive and UPPER() gives error 400: use Title Case'},
    {'agency': 'ECCC', 'host': 'maps-cartes.ec.gc.ca', 'kind': 'client-sensitive', 'note': 'CPCAD MapServer returned empty / cached results to python requests while curl worked (Oct 31). Retry the same honest request; never change the User-Agent.'},
    {'kind': 'pin-typo-pattern', 'note': 'POTA pins: 62 typed for 61, 0,0, copied from a neighbour, geocoded to the town (NB 1102-1106, Long Lake Bog NR lon -65.96 for -64.94, Fort Providence 111 km)'},
    {'kind': 'buffer', 'value': 150, 'note': 'pin on the road / entrance: named records 7-110 m from the pin (Ganaraska, ABCA, SNC, RRCA). Always LIKE-search by name and measure the distance (R-G12).'},
    {'agency': 'Grand River Conservation Authority', 'host': 'maps2.grca.on.ca', 'kind': 'wrong-layer', 'note': 'maps2.grca.on.ca LANDMGNT_CA_Lands is GANARASKA Region CA, not Grand River'},
    {'agency': 'Public Services and Procurement Canada', 'kind': 'agency-wide-layer', 'value': 'DFRP_PUBLIC/FeatureServer/4', 'note': 'federal property polygons (name_en, custodian_en): best for Parks Canada NHS + NCC parks; layer 2 points, layer 3 buildings'},
    {'agency': 'National Capital Commission', 'kind': 'name-field', 'value': 'FID', 'note': 'NCC_Parks/0 (services2 WLyMuW006nKOfa5Z): ID field is FID, not OBJECTID'},
    {'agency': 'NRCan CLSS', 'kind': 'buffer', 'value': 500, 'note': 'CLSS Aboriginal lands: intersect at 0 m misses edge pins; use a 30-500 m buffer; names UPPERCASE'},
    {'host': 'whc.unesco.org', 'kind': 'blocked', 'note': 'UNESCO WHS map PDFs only answer a Mozilla UA: we never change our UA, so log as blocked'},
    {'agency': 'Government of the Northwest Territories', 'kind': 'renumbered', 'old': 'Environment_LCC/MapServer/1,2', 'new': '193 terrestrial PAs, 194 marine, 195 conservation areas, 204 TP points, 206 Nagwichoonjik'},
    {'agency': 'Government of the Northwest Territories', 'kind': 'points-only', 'note': 'GNWT territorial parks: points only (Environment_LCC/204); ATLAS_Public 35-37 holds the reserve parcel'},
    {'agency': 'Town of Lunenburg', 'kind': 'token-only', 'note': 'AGOL heritage layers listed public but Token Required: use the town PDF maps'},
    {'host': 'observatoire.cmm.qc.ca', 'kind': 'blocked', 'note': 'Cloudflare 403 challenge to every box request: blocked, not no-hit'},
    {'host': 'cartes.ville.levis.qc.ca', 'kind': 'blocked', 'note': 'resolves to 198.18.0.1 on the box (network block; TLS exit 35)'},
    {'agency': 'Government of Saskatchewan', 'kind': 'token-only', 'note': 'SK Cadastre_Secured needs a token; never use the token inside the Geocortex config'},
    {'agency': 'Government of Saskatchewan', 'kind': 'delisted', 'note': 'SK recreation sites repealed SR 103/2021 (1 Oct 2021), RS 93/2016, SR 62/2002: read the Rec Sites Regs before searching'},
    {'agency': 'Alberta Parks', 'kind': 'delisted', 'note': 'Jan 2024: Chisholm, Fort Vermilion, Crane Meadow -> Sibbald PLUZ, Eyrie Gap -> Kananaskis PLUZ, Big Elbow inside Don Getty WPP; Sylvan Lake PP rescinded OIC 006/2018'},
    {'agency': 'Alberta Parks', 'kind': 'agency-wide-layer', 'value': 'boundary/land_use_management/MapServer/11', 'note': 'AB PLUZ polygons (PLUZ_NAME)'},
    {'agency': 'BC Parks', 'host': 'openmaps.gov.bc.ca', 'kind': 'agency-wide-layer', 'value': 'WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW', 'note': 'BC openmaps WFS public; CQL DWITHIN in EPSG:3005; solved 5 BC PIN OFFs'},
    {'agency': 'BC Parks', 'kind': 'renamed', 'note': 'Maquinna Marine = Nism̓aakqin Park; Mount Douglas = Pkols; Colony Farm = ƛ̓éxətəm; Endeavour Vents MPA merged into Tang.ɢ̲wan—ḥačxʷiqak—Tsig̱is MPA'},
    {'agency': 'Gouvernement du Québec', 'kind': 'parcel-fallback', 'value': 'geo.environnement.gouv.qc.ca Reference/Cadastre_allege/MapServer/0', 'note': 'QC cadastre (NO_LOT spaces every 3 digits) + MAMH roll CUBF 76xx park / 7191 historic: PARCEL grade'},
    {'agency': 'ISC Saskatchewan', 'kind': 'parcel-fallback', 'value': 'services.sac-isc.gc.ca SK_Cadastral_E/FeatureServer/2', 'note': 'SaskGrid quarter sections, public'},
    {'agency': 'NRCan CLSS', 'kind': 'parcel-fallback', 'value': 'CLSS ParcelService/MapServer/57', 'note': 'legal NHS boundaries in the North (Erebus and Terror); Banff / Waterton lots'},
    {'agency': 'Ontario Trails Network', 'kind': 'timeout', 'value': 1200, 'note': 'OTN distance queries beyond ~1.2 km can hang: keep <= 1200 m'},
    {'agency': 'Government of Nunavut', 'kind': 'agency-wide-layer', 'value': 'CIRNAC nms20/nms MapServer/21', 'note': 'NU territorial park polygons incl. small campground parks missing from CPCAD'},
    {'kind': 'no-land-boundary', 'note': 'Biosphere reserves, IBAs, Ramsar and 0,0 marine pins have no land boundary: NOT FOUND with the candidate named'},
    {'kind': 'same-name', 'note': "Same name, different place: DFRP 'Nicholas Denys Site' is not Denys Fort NHS; LTVCA Longwoods Road CA is not Battle Hill NHS: always check the distance too"},
]


class Findings:
    def __init__(self, out_dir, seed=True):
        self.p = pathlib.Path(out_dir) / 'findings.jsonl'
        self.p.parent.mkdir(parents=True, exist_ok=True)
        self._lk = threading.Lock()
        if seed and not self.p.exists():
            with open(self.p, 'w', encoding='utf-8') as f:
                for r in SEED: f.write(json.dumps({'date': '2026-11-01', 'by': 'seed: FINDINGS_LOG_Canada_HardLook.md', **r}, ensure_ascii=False) + '\n')
        self.rows = self.read()

    def read(self):
        out = []
        if self.p.exists():
            for ln in open(self.p, encoding='utf-8'):
                try: out.append(json.loads(ln))
                except ValueError: pass
        return out

    def add(self, by='', **row):
        row = {'date': dt.date.today().isoformat(), 'by': by, **row}
        key = (row.get('agency'), row.get('host'), row.get('kind'), row.get('value'), row.get('url'), row.get('old'))
        with self._lk:
            if any((r.get('agency'), r.get('host'), r.get('kind'), r.get('value'), r.get('url'), r.get('old')) == key for r in self.rows): return False
            self.rows.append(row)
            with open(self.p, 'a', encoding='utf-8') as f: f.write(json.dumps(row, ensure_ascii=False) + '\n')
        return True

    def refresh(self):
        """Pick up what other workers (other processes / shards) wrote since we started."""
        with self._lk: self.rows = self.read()

    def about(self, agency=None, host=None, kind=None):
        a = (agency or '').lower(); h = (host or '').lower()
        return [r for r in self.rows if (not kind or r.get('kind') == kind) and (
            (a and (r.get('agency') or '').lower() in (a,) ) or (h and (r.get('host') or '').lower() == h) or (not a and not h))]

    def name_field(self, agency=None, host=None):
        for r in reversed(self.about(agency, host, 'name-field')): return r.get('value')
        return None

    def renumbered(self, host, old):
        for r in reversed(self.rows):
            if r.get('kind') == 'renumbered' and r.get('host') == host and r.get('old') == old: return r.get('new')
        return None
