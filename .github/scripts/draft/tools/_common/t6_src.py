#!/usr/bin/env python3
"""KPC European protected-area service finder (T6, kpc_inspire).

For each European country, find the government's own protected-area services (WFS, OGC API, ArcGIS) and
downloads in the public open-data catalogues, and open each link once to see if it works. It decides nothing.

  python kpc_inspire.py --areas AT,DE,ES --out out/
  python kpc_inspire.py --selftest

Catalogues read:
  1. data.europa.eu (the EU open-data portal; it took over the INSPIRE Geoportal's harvest when that closed on
     1 Jul 2026): its SPARQL endpoint, asked with POST to https://data.europa.eu/sparql (robots.txt allows that
     path; it forbids the GET search pages /*search?* and /*?query=*).
  2. the country's national INSPIRE catalogue (CSW), from a short built-in list, when it answers.
Out: <out>/inspire.json  {CC: [{title, publisher, licence, date, links: [{url, kind, opens, layers}],
                              source_url, read_date, why, catalogue}],
                          "EU": [... the EEA Natura 2000 / CDDA compilations, each with eu_compilation: true]}
     <out>/report.json, <out>/state.json (for --resume)
Exit: 0 all done, 3 time ran out (run again with --resume), 2 bad input, anything else = a crash.
"""
from xml.sax.saxutils import escape as xml_escape
import argparse, csv, hashlib, json, os, re, sys, time
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse, urlencode, quote, parse_qsl, urlunparse

import requests

#@@POLITE@@

HERE = os.path.dirname(os.path.abspath(__file__))
SPARQL = 'https://data.europa.eu/sparql'
DATASET_PAGE = 'https://data.europa.eu/data/datasets/'

# country: (ISO3 used by the EU country list, languages)
COUNTRIES = {
    'AT': ('AUT', ['de']), 'BE': ('BEL', ['nl', 'fr', 'de']), 'BG': ('BGR', ['bg']), 'HR': ('HRV', ['hr']),
    'CY': ('CYP', ['el']), 'CZ': ('CZE', ['cs']), 'DK': ('DNK', ['da']), 'EE': ('EST', ['et']),
    'FI': ('FIN', ['fi', 'sv']), 'FR': ('FRA', ['fr']), 'DE': ('DEU', ['de']), 'GR': ('GRC', ['el']),
    'HU': ('HUN', ['hu']), 'IE': ('IRL', ['ga']), 'IT': ('ITA', ['it']), 'LV': ('LVA', ['lv']),
    'LT': ('LTU', ['lt']), 'LU': ('LUX', ['fr', 'de']), 'MT': ('MLT', []), 'NL': ('NLD', ['nl']),
    'PL': ('POL', ['pl']), 'PT': ('PRT', ['pt']), 'RO': ('ROU', ['ro']), 'SK': ('SVK', ['sk']),
    'SI': ('SVN', ['sl']), 'ES': ('ESP', ['es', 'ca', 'eu', 'gl']), 'SE': ('SWE', ['sv']),
    'NO': ('NOR', ['no']), 'IS': ('ISL', ['is']), 'LI': ('LIE', ['de']), 'CH': ('CHE', ['de', 'fr', 'it']),
}
# words for "protected area" (and the main kinds) in each language; English and Natura 2000 are always added
WORDS = {
    'en': ['protected site', 'protected area', 'nature reserve', 'national park', 'natura 2000', 'conservation area',
           'special area of conservation', 'special protection area', 'nature conservation', 'cdda',
           'designated areas'],
    'de': ['schutzgebiet', 'naturschutz', 'nationalpark', 'naturpark', 'biosphärenreservat', 'natura 2000',
           'europaschutzgebiet', 'ffh-gebiet', 'vogelschutzgebiet', 'naturdenkmal'],
    'es': ['espacios naturales protegidos', 'espacio natural protegido', 'espacios protegidos', 'áreas protegidas',
           'zonas protegidas', 'parque nacional', 'parques nacionales', 'parque natural', 'reserva natural',
           'red natura', 'lugares protegidos', 'zepa', 'lic '],
    'ca': ['espais naturals protegits', 'espais protegits', "espais d'interès natural", 'parc natural'],
    'eu': ['babestutako', 'natura sarea'],
    'gl': ['espazos naturais protexidos', 'espazos protexidos'],
    'fr': ['aires protégées', 'aire protégée', 'espaces protégés', 'espace naturel protégé', 'parc national',
           'parc naturel', 'réserve naturelle', 'sites protégés', 'zones protégées'],
    'nl': ['beschermde gebieden', 'beschermde natuur', 'natuurgebied', 'nationaal park', 'beschermde sites'],
    'it': ['aree protette', 'area protetta', 'parco nazionale', 'parchi', 'riserva naturale', 'siti protetti'],
    'pl': ['obszary chronione', 'formy ochrony przyrody', 'park narodowy', 'park krajobrazowy', 'rezerwat'],
    'pt': ['áreas protegidas', 'área protegida', 'rede natura', 'sítios protegidos', 'parque natural'],
    'cs': ['chráněná území', 'zvláště chráněn', 'národní park', 'chráněné krajinné'],
    'sk': ['chránené územia', 'chránené územie', 'národný park', 'chránené vtáčie'],
    'hu': ['védett természeti', 'védett terület', 'nemzeti park', 'természetvédelmi'],
    'ro': ['arii protejate', 'arii naturale protejate', 'arie protejată', 'parc național', 'parc natural'],
    'bg': ['защитени територии', 'защитени зони', 'защитена територия'],
    'el': ['προστατευόμεν', 'περιοχές natura'],
    'hr': ['zaštićena područja', 'zaštićeno područje', 'nacionalni park', 'park prirode'],
    'sl': ['zavarovana območja', 'zavarovano območje', 'naravne vrednote'],
    'da': ['beskyttede områder', 'beskyttet natur', 'fredede', 'fredning', 'nationalpark', 'habitatområde'],
    'sv': ['skyddade områden', 'skyddad natur', 'naturreservat', 'nationalpark', 'naturvårdsområde'],
    'fi': ['suojelualue', 'luonnonsuojelualue', 'kansallispuisto', 'suojellut'],
    'et': ['kaitsealad', 'kaitseala', 'kaitstavad loodusobjektid'],
    'lv': ['aizsargājamās', 'īpaši aizsargājamās dabas teritorijas'],
    'lt': ['saugomos teritorijos', 'saugoma teritorija'],
    'no': ['verneområde', 'verneområder', 'naturvern', 'nasjonalpark'],
    'is': ['friðlýst', 'verndarsvæði'],
    'ga': ['protected sites', 'láithreáin chosanta'],
}
# national INSPIRE catalogues (CSW 2.0.2) known to the club; each run checks whether they answer
NATIONAL_CSW = {
    'AT': 'https://geometadatensuche.inspire.gv.at/metadatensuche/srv/ger/csw',
    'DE': 'https://gdk.gdi-de.org/gdi-de/srv/ger/csw',
    'ES': 'https://www.idee.es/csw-codsi-idee/srv/spa/csw',
    'NL': 'https://nationaalgeoregister.nl/geonetwork/srv/dut/csw',
    'BE': 'https://metadata.vlaanderen.be/srv/dut/csw',
    'CZ': 'https://micka.cenia.cz/csw/',
    'DK': 'https://geodata-info.dk/srv/dan/csw',
    'FI': 'https://paikkatietohakemisto.fi/geonetwork/srv/eng/csw',
    'IT': 'https://geodati.gov.it/RNDT/csw',
    'PT': 'https://snig.dgterritorio.gov.pt/rndg/srv/por/csw',
    'SE': 'https://www.geodata.se/geodataportalen/srv/eng/csw',
    'NO': 'https://www.geonorge.no/geonetwork/srv/nor/csw',
    'CH': 'https://www.geocat.ch/geonetwork/srv/eng/csw',
}
CSW_WORDS = {'AT': ['Schutzgebiet'], 'DE': ['Schutzgebiet'], 'ES': ['espacios naturales protegidos', 'red natura'],
             'NL': ['beschermde gebieden', 'Natura 2000'], 'BE': ['beschermde gebieden'], 'CZ': ['chráněná území'],
             'DK': ['beskyttede områder', 'Natura 2000'], 'FI': ['suojelualue'], 'IT': ['aree protette'],
             'PT': ['áreas protegidas'], 'SE': ['skyddade områden', 'naturreservat'], 'NO': ['verneområder'],
             'CH': ['Schutzgebiet']}
EU_BODY = re.compile(r'european environment agency|\beea\b|eea\.europa\.eu|european commission|joint research centre',
                     re.I)
EU_CATALOGUE = 'eea-sdi'
EU_NAME = re.compile(r'natura ?2000|\bcdda\b|common database on designated areas|nationally designated areas', re.I)
NOT_AREA = re.compile(r'\b(report|bericht|informe|rapport|statisti|budget|haushalt|presupuesto|förder|subvenc|'
                      r'ausgaben|kosten|besucher|visitors|monitoring of|stellungnahme|press|noise|lärm|wasserschutz|'
                      r'trinkwasser|grundwasser|hochwasser|überschwemmung|inundación|lawinen|wasserschutzgebiet|'
                      r'heilquellen|quellschutz|trinkwasserschutz|flood|water protection)\b', re.I)


def today():
    return datetime.now().strftime('%Y-%m-%d')


def ln(tag):
    return tag.rsplit('}', 1)[-1]


def link_kind(url, fmt=''):
    """wfs | ogcapi | arcgis | download | wms | None (a web page), from the address and the catalogue's format."""
    u, f = url.lower(), (fmt or '').lower()
    q = dict((k.lower(), v.lower()) for k, v in parse_qsl(urlparse(url).query))
    if q.get('service') == 'wfs' or 'wfs' in f or re.search(r'/wfs\b|_wfs\b|wfs\?|/ows/services/.*wfs', u):
        return 'wfs'
    if q.get('service') in ('wms', 'wmts') or re.search(r'\bwms|wmts', f) or re.search(r'/wms\b|_wms\b|wms\?|wmts', u):
        return 'wms'
    if re.search(r'/rest/services/', u):
        return 'arcgis'
    if re.search(r'/collections\b|/ogcapi|/ogc/features|ogc ?api|/features/v1', u) or 'ogc_api' in f or 'ogcapi' in f:
        return 'ogcapi'
    if re.search(r'\.(zip|gpkg|geojson|json|shp|gml|kml|kmz|xml|7z|gz)(\?|$)', u) or \
            re.search(r'\b(zip|shp|shapefile|gpkg|geopackage|geojson|gml|kml|esri)\b', f) or \
            re.search(r'atom|download|/files/|downloadservice', u):
        return 'download'
    return None


def kind_from_iri(fmt):
    return fmt.rsplit('/', 1)[-1].replace('_', ' ') if fmt else ''


def caps_url(url, service='WFS'):
    p = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(p.query) if k.lower() not in ('request', 'service', 'version', 'typename',
                                                                     'typenames', 'outputformat', 'acceptversions')]
    q += [('SERVICE', service), ('REQUEST', 'GetCapabilities')]
    return urlunparse(p._replace(query=urlencode(q)))


def base_key(url, kind):
    p = urlparse(url)
    if kind in ('wfs', 'wms'):
        q = [(k.lower(), v) for k, v in parse_qsl(p.query) if k.lower() not in
             ('request', 'service', 'version', 'typename', 'typenames', 'outputformat', 'acceptversions', 'layers')]
        return (p.netloc.lower() + p.path.rstrip('/') + '?' + urlencode(sorted(q))).lower()
    if kind == 'arcgis':
        m = re.match(r'(.*/rest/services/.*?/(MapServer|FeatureServer))', url, re.I)
        return (m.group(1) if m else url).lower()
    if kind == 'ogcapi':
        return (p.netloc + re.sub(r'/collections.*$', '', p.path)).lower()
    return url


class Opener:
    """Opens each link once: WFS GetCapabilities (feature types), OGC API /collections, ArcGIS ?f=json (layers),
    a download's first bytes."""
    def __init__(self, web):
        self.web = web
        self.done = {}

    def _fail(self, what, st, url):
        """A link that does not open. A 403 is accepted as it is (club decision, Oct 31): 'blocked from here'."""
        if st == 403:
            k = self.web._block_key(url)
            return False, [], f'blocked from here (403): {self.web.blocked.get(k) or "403 Forbidden on " + url}'
        return False, [], f'{what} -> {st}'

    def open(self, url, kind):
        key = (kind, base_key(url, kind))
        if key not in self.done:
            try:
                self.done[key] = getattr(self, '_' + kind)(url)
            except Exception as e:                       # one bad link never stops the run
                self.done[key] = (False, [], f'could not read: {type(e).__name__}')
        return self.done[key]

    def _wfs(self, url):
        cu = caps_url(url)
        st, hd, body, fin = self.web.get(cu)
        if st != 200:
            return self._fail('GetCapabilities', st, cu)
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return False, [], 'GetCapabilities is not XML'
        if 'exception' in ln(root.tag).lower():
            return False, [], 'GetCapabilities answered with an error'
        names = []
        for ft in root.iter():
            if ln(ft.tag) == 'FeatureType':
                nm = tt = None
                for c in ft:
                    if ln(c.tag) == 'Name':
                        nm = (c.text or '').strip()
                    elif ln(c.tag) == 'Title':
                        tt = (c.text or '').strip()
                if nm:
                    names.append(nm if not tt or tt == nm else f'{nm} ({tt})')
        if not names:
            return False, [], 'GetCapabilities lists no feature types'
        return True, names[:40], f'GetCapabilities {cu} lists {len(names)} feature type(s)'

    def _wms(self, url):
        return None, [], 'a picture service (WMS), not opened: it has no outlines to read'

    def _ogcapi(self, url):
        p = urlparse(url)
        path = re.sub(r'/collections.*$', '', p.path).rstrip('/')
        cu = urlunparse(p._replace(path=path + '/collections', query='f=json'))
        st, hd, body, fin = self.web.get(cu, headers={'Accept': 'application/json'})
        if st != 200:
            return self._fail('/collections', st, cu)
        try:
            d = json.loads(body)
        except ValueError:
            return False, [], '/collections is not JSON'
        names = [c.get('id') + (f" ({c.get('title')})" if c.get('title') and c.get('title') != c.get('id') else '')
                 for c in d.get('collections', []) if c.get('id')]
        return bool(names), names[:40], f'{cu} lists {len(names)} collection(s)'

    def _arcgis(self, url):
        m = re.match(r'(.*/rest/services/.*?/(MapServer|FeatureServer))', url, re.I)
        su = m.group(1) if m else url.split('?')[0]
        st, hd, body, fin = self.web.get(su + '?f=json')
        if st != 200:
            return self._fail(f'{su}?f=json', st, su + '?f=json')
        try:
            d = json.loads(body)
        except ValueError:
            return False, [], 'not JSON'
        if d.get('error'):
            return False, [], f"error {d['error'].get('code')}"
        names = [f"{l.get('id')}: {l.get('name')}" for l in d.get('layers', [])]
        return bool(names), names[:40], f'{su}?f=json lists {len(names)} layer(s)'

    def _download(self, url):
        old = self.web.max_bytes
        self.web.max_bytes = 200_000
        try:
            st, hd, body, fin = self.web.get(url, headers={'Range': 'bytes=0-65535'}, nocache=True)
        finally:
            self.web.max_bytes = old
        if st not in (200, 206):
            return self._fail('download', st, url)
        ct = (hd.get('Content-Type') or hd.get('content-type') or '').lower()
        head = body[:600].lower()
        if 'html' in ct or head.lstrip().startswith(b'<!doctype html') or head.lstrip().startswith(b'<html'):
            return False, [], 'the address gives a web page, not a file'
        layers = []
        if b'<feed' in head:     # an INSPIRE Atom download feed: the entries name the files
            try:
                root = ET.fromstring(body)
                layers = [(e.findtext('{http://www.w3.org/2005/Atom}title') or '').strip()
                          for e in root.findall('{http://www.w3.org/2005/Atom}entry')][:40]
            except ET.ParseError:
                pass
        size = hd.get('Content-Range', '').split('/')[-1] or hd.get('Content-Length', '')
        return True, layers, f'the file starts to download ({ct or "no type"}{", " + size + " bytes" if size else ""})'


def sparql(web, q):
    st, hd, body, fin = web.get(SPARQL, method='POST', data={'query': q},
                                headers={'Accept': 'application/sparql-results+json'})
    if st != 200:
        return None, st
    if str(hd.get('X-SQL-State') or hd.get('x-sql-state') or '').upper() == 'S1TAT':
        return None, 'partial answer (the server ran out of time)'
    try:
        return json.loads(body)['results']['bindings'], 200
    except (ValueError, KeyError):
        return None, 'not JSON'


def sq(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


# words for the catalogue's full-text index (whole words; a trailing * = any ending, at least 4 letters before it)
TEXT_WORDS = {
    'de': ['schutzgebiet*', 'naturschutzgebiet*', 'landschaftsschutzgebiet*', 'vogelschutzgebiet*',
           'europaschutzgebiet*', 'nationalpark*', 'naturpark*', 'biosphärenreservat*', 'ffh gebiet*', 'natura 2000'],
    'es': ['espacios naturales protegidos', 'espacio natural protegido', 'espacios protegidos', 'áreas protegidas',
           'zonas protegidas', 'parque nacional', 'parques nacionales', 'parque natural', 'parques naturales',
           'reserva natural', 'red natura', 'lugares de importancia comunitaria', 'zepa'],
    'ca': ['espais naturals protegits', 'espais protegits', 'parc natural'],
    'eu': ['natura sarea'], 'gl': ['espazos naturais protexidos'],
    'fr': ['aires protégées', 'espaces protégés', 'espaces naturels protégés', 'parc national', 'parcs nationaux',
           'parc naturel', 'réserve naturelle', 'réserves naturelles', 'sites protégés', 'natura 2000'],
    'nl': ['beschermde gebieden', 'beschermde natuur', 'nationaal park', 'nationale parken', 'natura 2000'],
    'it': ['aree protette', 'area protetta', 'parco nazionale', 'parchi nazionali', 'riserva naturale',
           'riserve naturali', 'siti protetti', 'natura 2000'],
    'pl': ['obszary chronione', 'formy ochrony przyrody', 'park narodowy', 'parki narodowe', 'park krajobrazowy',
           'rezerwat*', 'natura 2000'],
    'pt': ['áreas protegidas', 'área protegida', 'rede natura', 'sítios protegidos', 'parque natural'],
    'cs': ['chráněná území', 'zvláště chráněná území', 'národní park', 'chráněná krajinná oblast', 'natura 2000'],
    'sk': ['chránené územia', 'chránené územie', 'národný park', 'natura 2000'],
    'hu': ['védett természeti területek', 'védett területek', 'nemzeti park', 'natura 2000'],
    'ro': ['arii protejate', 'arii naturale protejate', 'parc național', 'parc natural', 'natura 2000'],
    'bg': ['защитени територии', 'защитени зони', 'натура 2000'],
    'el': ['προστατευόμενες περιοχές', 'natura 2000'],
    'hr': ['zaštićena područja', 'zaštićeno područje', 'nacionalni park', 'park prirode', 'natura 2000'],
    'sl': ['zavarovana območja', 'zavarovano območje', 'natura 2000'],
    'da': ['beskyttede områder', 'fredede områder', 'fredning*', 'nationalpark*', 'natura 2000'],
    'sv': ['skyddade områden', 'naturreservat*', 'nationalpark*', 'natura 2000'],
    'fi': ['suojelualue*', 'luonnonsuojelualue*', 'kansallispuisto*', 'natura 2000'],
    'et': ['kaitsealad', 'kaitseala*', 'natura 2000'], 'lv': ['aizsargājamās dabas teritorijas', 'natura 2000'],
    'lt': ['saugomos teritorijos', 'natura 2000'], 'no': ['verneområde*', 'naturvern*', 'nasjonalpark*'],
    'is': ['friðlýst*', 'verndarsvæði*'],
    'ga': ['protected sites', 'protected areas', 'special areas of conservation', 'natura 2000'],
    'en': ['protected sites', 'protected areas', 'special areas of conservation', 'nature reserves', 'natura 2000'],
}
PFX = ('PREFIX dcat: <http://www.w3.org/ns/dcat#> PREFIX dct: <http://purl.org/dc/terms/> '
       'PREFIX foaf: <http://xmlns.com/foaf/0.1/> ')


def batched(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def europa_records(web, cc, log, words):
    """data.europa.eu in three steps that its server answers quickly (one big joined query times out):
    1. its full-text index: datasets whose title has a protected-area word of the country's languages;
    2. which of them sit in a catalogue of this country; 3. publisher, date, licence and links of those."""
    iso3, langs = COUNTRIES[cc]
    tl = [l for l in (langs or [])] + (['en'] if (not langs or 'ga' in langs) else [])
    tw = list(dict.fromkeys(sum((TEXT_WORDS.get(l, []) for l in tl), [])))
    # the portal machine-translates every title into all EU languages (tagged e.g. "de-t-en-t0-mtec"); only titles
    # in the country's own languages as published (plain "de") are searched, else every country's data comes back
    # titles tagged "en" are searched too: some national records carry a German / Spanish title tagged "en"
    # (e.g. Umweltbundesamt's "Schutzgebiete Österreich 2025")
    lang_f = 'FILTER(LANG(?title) IN (' + ', '.join(f'"{l}"' for l in dict.fromkeys(tl + ['en'])) + '))'
    notes, titles = [], {}
    for chunk in batched(tw, 4):
        expr = ' OR '.join('"' + w.replace('"', '') + '"' for w in chunk)
        for page in range(3):
            q = PFX + (f"SELECT DISTINCT ?d ?title WHERE {{ ?d dct:title ?title . ?title bif:contains '{expr}' . "
                       f"?d a dcat:Dataset . {lang_f} }} LIMIT 10000 OFFSET {page * 10000}")
            rows, st = sparql(web, q)
            if rows is None:
                notes.append(f'text search {chunk} -> {st}')
                break
            for r in rows:
                titles.setdefault(r['d']['value'], set()).add(r['title']['value'])
            if len(rows) < 10000:
                break
    cand = [d for d, ts in titles.items() if not NOT_AREA.search(' | '.join(ts))]
    mine, eu = [], []
    n_bad = 0
    for b in batched(cand, 100):
        vals = ' '.join(f'<{d}>' for d in b)
        rows, st = sparql(web, PFX + f'SELECT ?d ?cat ?c WHERE {{ VALUES ?d {{ {vals} }} ?cat dcat:dataset ?d . '
                                     f'OPTIONAL {{ ?cat dct:spatial ?c }} }}')
        if rows is None:
            n_bad += 1
            continue
        mine += [r['d']['value'] for r in rows if r.get('c', {}).get('value', '').endswith('/' + iso3)]
        eu += [r['d']['value'] for r in rows if r['cat']['value'].rstrip('/').endswith('/' + EU_CATALOGUE)
               and EU_NAME.search(' '.join(titles[r['d']['value']]))]
    mine = list(dict.fromkeys(mine))
    eu = [d for d in dict.fromkeys(eu) if d not in mine][:30]
    recs = {d: {'id': d, 'titles': titles[d], 'publisher': None, 'date': None, 'licence': None, 'links': {},
                'eu': d in eu} for d in mine + eu}
    for b in batched(mine + eu, 40):
        vals = ' '.join(f'<{d}>' for d in b)
        q = PFX + (f'SELECT ?d ?pub ?mod ?lic ?url ?fmt WHERE {{ VALUES ?d {{ {vals} }} '
                   f'OPTIONAL {{ ?d dct:publisher ?p . ?p foaf:name ?pub }} OPTIONAL {{ ?d dct:modified ?mod }} '
                   f'OPTIONAL {{ ?d dcat:distribution ?x . ?x dcat:accessURL ?url . OPTIONAL {{ ?x dct:format ?fmt }} '
                   f'OPTIONAL {{ ?x dct:license ?lic }} }} }}')
        rows, st = sparql(web, q)
        if rows is None:
            n_bad += 1
            continue
        for r in rows:
            rec = recs[r['d']['value']]
            if r.get('pub'):
                rec['publisher'] = rec['publisher'] or r['pub']['value']
            if r.get('mod'):
                rec['date'] = max(rec['date'] or '', r['mod']['value'][:10])
            if r.get('lic') and r['lic'].get('type') == 'uri':
                rec['licence'] = rec['licence'] or r['lic']['value']
            if r.get('url'):
                rec['links'].setdefault(r['url']['value'], kind_from_iri(r.get('fmt', {}).get('value', '')))
    notes.insert(0, f'data.europa.eu SPARQL: {len(titles)} dataset(s) in Europe with a protected-area word '
                    f'({", ".join(tw)}), {len(mine)} in a catalogue of {cc}, {len(eu)} in the EEA catalogue' +
                 (f'; {n_bad} batch(es) did not answer' if n_bad else ''))
    return list(recs.values()), '; '.join(notes)


def csw_records(web, cc, log):
    url = NATIONAL_CSW.get(cc)
    if not url:
        return [], 'no national catalogue in the built-in list'
    out, notes = [], []
    for w in CSW_WORDS.get(cc, []):
        p = {'service': 'CSW', 'version': '2.0.2', 'request': 'GetRecords', 'typeNames': 'csw:Record',
             'resultType': 'results', 'elementSetName': 'full', 'outputSchema': 'http://www.opengis.net/cat/csw/2.0.2',
             'constraintLanguage': 'FILTER', 'constraint_language_version': '1.1.0',
             'constraint': ('<Filter xmlns="http://www.opengis.net/ogc"><PropertyIsLike wildCard="*" '
                            'singleChar="_" escapeChar="\\"><PropertyName>AnyText</PropertyName>'
                            f'<Literal>*{xml_escape(w)}*</Literal></PropertyIsLike></Filter>'),
             'maxRecords': '100'}
        u = url + '?' + urlencode(p)
        st, hd, body, fin = web.get(u)
        if st != 200:
            notes.append(f'{url} -> {st}')
            break
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            notes.append(f'{url}: not XML')
            break
        if 'exception' in ln(root.tag).lower():
            msg = ' '.join(t.strip() for t in root.itertext() if t.strip())[:120]
            notes.append(f'{url}: {msg}')
            break
        n = 0
        for rec in root.iter():
            if ln(rec.tag) != 'Record':
                continue
            n += 1
            r = {'id': None, 'titles': set(), 'publisher': None, 'date': None, 'licence': None, 'links': {},
                 'csw': u}
            for c in rec:
                t, v = ln(c.tag), (c.text or '').strip()
                if t == 'identifier' and v:
                    r['id'] = r['id'] or v
                elif t == 'title' and v:
                    r['titles'].add(v)
                elif t in ('publisher', 'creator') and v:
                    r['publisher'] = r['publisher'] or v
                elif t in ('modified', 'date') and v:
                    r['date'] = r['date'] or v[:10]
                elif t in ('rights', 'license', 'accessRights') and v:
                    r['licence'] = r['licence'] or v[:200]
                elif t in ('URI', 'references') and v.startswith('http'):
                    proto = ' '.join(str(x) for x in c.attrib.values())
                    r['links'].setdefault(v, proto)
            if r['id']:
                out.append(r)
        notes.append(f'{url}: "{w}" -> {n} record(s)')
    return out, '; '.join(notes)


def make_records(raw, cc, words, catalogue, opener, read_date, deadline, max_links, log):
    """Keep datasets with a service or download link; open each link once."""
    rx = re.compile('|'.join(re.escape(w) for w in words), re.I)
    keep = []
    for r in raw:
        title = sorted(r['titles'], key=len)[0] if r['titles'] else ''
        alltitles = ' | '.join(sorted(r['titles']))
        if not rx.search(alltitles) or NOT_AREA.search(alltitles):
            continue
        links = []
        for u, fmt in r['links'].items():
            if not u.startswith('http') or banned(u):
                continue
            k = link_kind(u, fmt)
            if k:
                links.append((u, k))
        if not links:
            continue
        eu = r.get('eu') or (bool(EU_BODY.search(r.get('publisher') or '') or
                                  any('eea.europa.eu' in u for u, k in links)) and bool(EU_NAME.search(alltitles)))
        prio = (0 if any(k == 'wfs' for u, k in links) else 1 if any(k in ('ogcapi', 'arcgis') for u, k in links)
                else 2 if any(k == 'download' for u, k in links) else 3)
        keep.append((prio, title, r, links, eu))
    keep.sort(key=lambda x: (x[0], x[1]))
    out, opened = [], 0
    for prio, title, r, links, eu in keep:
        rows = []
        for u, k in links[:8]:
            if k == 'wms':
                continue
            if time.time() > deadline or opened >= max_links:
                rows.append({'url': u, 'kind': k, 'opens': None, 'layers': [], 'why': 'not opened (link budget used)'})
                continue
            fresh = (k, base_key(u, k)) not in opener.done
            ok, layers, how = opener.open(u, k)
            opened += fresh
            row = {'url': u, 'kind': k, 'opens': ok, 'layers': layers, 'why': how}
            if not ok and str(how).startswith('blocked from here'):
                row['status'] = 'blocked from here'   # kept in the list: the club tries it again from GitHub
            rows.append(row)
        if not rows:
            continue
        src = (DATASET_PAGE + r['id'].rsplit('/', 1)[-1]) if catalogue == 'data.europa.eu' else r.get('csw')
        why = [f'listed in {catalogue} for {cc}' + (f' (record {r["id"]})' if catalogue != 'data.europa.eu' else ''),
               'its title names ' + ', '.join(sorted({m.group(0).lower() for m in rx.finditer(' '.join(r['titles']))}))]
        if eu:
            why.append('in the European Environment Agency\'s catalogue (or published by an EU body) about Natura '
                       '2000 / CDDA: a Europe-wide compilation, not the country\'s own file')
        rec = {'title': title, 'publisher': r.get('publisher'), 'licence': r.get('licence'), 'date': r.get('date'),
               'links': rows, 'source_url': src, 'read_date': read_date, 'why': '; '.join(why) + '.',
               'catalogue': catalogue}
        if eu:
            rec['eu_compilation'] = True
        out.append(rec)
    return out


def run(args, web=None):
    t0 = time.time()
    deadline = t0 + args.max_minutes * 60
    log = (lambda *a: print(*a, flush=True)) if not args.quiet else (lambda *a: None)
    areas = [a.strip().upper().split('-')[-1] for a in (args.areas or ','.join(COUNTRIES)).split(',') if a.strip()]
    bad = [a for a in areas if a not in COUNTRIES]
    if bad:
        print(f'bad input: unknown country code(s) {", ".join(bad)}; known: {", ".join(COUNTRIES)}', file=sys.stderr)
        return 2
    if args.limit:
        areas = areas[:args.limit]
    out = args.out
    os.makedirs(out, exist_ok=True)
    web = web or Polite(cache=args.cache, log=log, rest_exempt=True)
    web.log = log
    read_date = today()
    ij, sj, rj = (os.path.join(out, n) for n in ('inspire.json', 'state.json', 'report.json'))
    resume = args.resume and os.path.exists(sj)
    result = json.load(open(ij)) if resume and os.path.exists(ij) else {}
    state = json.load(open(sj)) if resume else {'done': {}}
    report = json.load(open(rj)) if resume and os.path.exists(rj) else {'countries': {}}
    opener = Opener(web)
    left = 0
    for cc in areas:
        if cc in state['done']:
            continue
        if time.time() > deadline:
            left += 1
            continue
        langs = COUNTRIES[cc][1]
        words = list(dict.fromkeys(sum((WORDS.get(l, []) for l in langs), []) + WORDS['en']))
        log(f'{cc}: searching ({", ".join(langs) or "en"})')
        notes, recs = [], []
        try:
            raw, note = europa_records(web, cc, log, words)
            notes.append(note)
            if raw:
                recs += make_records(raw, cc, words, 'data.europa.eu', opener, read_date, deadline, args.max_links, log)
            raw2, note2 = csw_records(web, cc, log)
            notes.append('national catalogue: ' + note2)
            if raw2:
                seen = {l['url'] for r in recs for l in r['links']}
                more = make_records(raw2, cc, words, 'national catalogue ' + urlparse(NATIONAL_CSW[cc]).hostname,
                                    opener, read_date, deadline, args.max_links, log)
                recs += [r for r in more if not all(l['url'] in seen for l in r['links'])]
        except Exception as e:      # one bad country never stops the run
            notes.append(f'stopped early: {type(e).__name__}: {e}')
        eu = [r for r in recs if r.get('eu_compilation')]
        own = [r for r in recs if not r.get('eu_compilation')]
        # the most useful first: a WFS that opens, then any service that opens, then the rest
        def rank(r):
            ks = [(l['kind'], l['opens']) for l in r['links']]
            return (0 if ('wfs', True) in ks else 1 if any(o for k, o in ks) else 2, r['title'].lower())
        own.sort(key=rank)
        own = own[:args.max_records]
        result[cc] = own
        if eu:
            have = {r['title'] for r in result.get('EU', [])}
            result.setdefault('EU', []).extend(r for r in eu if r['title'] not in have)
        wfs_ok = sum(1 for r in own for l in r['links'] if l['kind'] == 'wfs' and l['opens'])
        report['countries'][cc] = {'records': len(own), 'eu_compilation_records': len(eu),
                                   'wfs_links_that_open': wfs_ok, 'notes': notes, 'read_date': read_date}
        log(f'  {len(own)} record(s), {wfs_ok} WFS link(s) that open; {len(eu)} EU compilation record(s)')
        state['done'][cc] = read_date
        for path, obj in ((ij, result), (sj, state), (rj, report)):
            tmp = path + '.tmp'
            json.dump(obj, open(tmp, 'w'), ensure_ascii=False, indent=1)
            os.replace(tmp, path)
    report['web'] = dict(web.stats)
    report['resting_hosts'] = sorted(web.resting)
    report['blocked_hosts'] = dict(sorted({**report.get('blocked_hosts', {}), **web.blocked}.items()))
    json.dump(report, open(rj, 'w'), ensure_ascii=False, indent=1)
    if left:
        log(f'time is up: {left} countr(ies) left; run again with --resume')
        return 3
    return 0


class FakeWeb(Polite):
    def __init__(self, routes):
        super().__init__(cache=None, gap=0, rest_exempt=True)
        self.routes = routes

    def _raw(self, url, method='GET', data=None, headers=None):
        self.stats['requests'] += 1
        from urllib.parse import unquote_plus
        u = unquote_plus(url) + ' ' + unquote_plus(urlencode(data) if isinstance(data, dict) else str(data or ''))
        for r in self.routes:
            if all(m in u for m in r['match']):
                return r.get('status', 200), r.get('headers', {}), open(os.path.join(HERE, 'tests', r['file']), 'rb').read(), url
        return 404, {}, b'', url


def selftest():
    import tempfile, shutil
    T = os.path.join(HERE, 'tests')
    routes = json.load(open(os.path.join(T, 'web.json')))['routes']
    tmp = tempfile.mkdtemp(prefix='kpc_inspire_test_')
    ok = True
    try:
        a = argparse.Namespace(areas='AT', out=tmp, cache=None, max_minutes=5, resume=False, limit=0, quiet=True,
                               max_links=60, max_records=80)
        code = run(a, web=FakeWeb(routes))
        if code != 0:
            ok = False
            print('exit code', code)
        got = json.load(open(os.path.join(tmp, 'inspire.json')))
        exp = json.load(open(os.path.join(T, 'expected', 'inspire.json')))
        for d in (got, exp):
            for v in d.values():
                for r in v:
                    r['read_date'] = 'X'
        if got != exp:
            ok = False
            print('inspire.json differs from tests/expected/inspire.json:')
            print(json.dumps(got, indent=1, ensure_ascii=False)[:4000])
        for u, k in (('https://x.gv.at/wfs?service=WFS&request=GetCapabilities', 'wfs'),
                     ('https://x.de/arcgis/rest/services/A/MapServer', 'arcgis'),
                     ('https://x.es/ogcapi/collections', 'ogcapi'), ('https://x.es/enp.zip', 'download'),
                     ('https://x.es/wms?service=WMS', 'wms'), ('https://x.es/about.html', None)):
            if link_kind(u) != k:
                ok = False
                print(f'link kind of {u} should be {k}, got {link_kind(u)}')
        if not banned('https://www.protectedplanet.net/en') or not banned('https://overpass-api.de/api'):
            ok = False
            print('banned-source check wrong')
        # Spain's national WFS answers 403 from here: kept, opens=false, "blocked from here (403)"
        bw = FakeWeb([{'match': ['geoserver.iepnb.es'], 'status': 403, 'file': routes[0]['file']}])
        bo = Opener(bw).open('https://geoserver.iepnb.es/geoserver/ENP/wms?service=WFS&request=GetCapabilities', 'wfs')
        if bo[0] is not False or not bo[2].startswith('blocked from here (403): 403 Forbidden on https://geoserver.iepnb.es/'):
            ok = False
            print('a 403 link should read "blocked from here (403)", got', bo)
        if 'geoserver.iepnb.es' not in bw.blocked:
            ok = False
            print('the 403 host was not marked blocked')
        if not os.path.exists(os.path.join(tmp, 'state.json')):
            ok = False
            print('no state.json')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for m in polite_selftest():
        ok = False
        print(m)
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description='KPC European protected-area service finder (T6)')
    ap.add_argument('--areas', help='country codes, e.g. AT,DE,ES (default: all %d)' % len(COUNTRIES))
    ap.add_argument('--in', dest='inp', help='(optional) a text / CSV file of country codes, one per line')
    ap.add_argument('--out', help='output folder (the tool writes only here)')
    ap.add_argument('--cache', help='download cache folder (public catalogue replies only)')
    ap.add_argument('--max-minutes', type=float, default=50)
    ap.add_argument('--resume', action='store_true', help='carry on from <out>/state.json')
    ap.add_argument('--limit', type=int, default=0, help='only the first N countries')
    ap.add_argument('--max-links', type=int, default=60, help='links opened per country (default 60)')
    ap.add_argument('--max-records', type=int, default=80, help='records kept per country (default 80)')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true', help='run the built-in test (no network) and print PASS / FAIL')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.out:
        print('bad input: --out is needed', file=sys.stderr)
        return 2
    if a.inp:
        try:
            codes = [l.strip().split(',')[0] for l in open(a.inp, encoding='utf-8') if l.strip() and not l.startswith('#')]
        except OSError as e:
            print(f'bad input: {e}', file=sys.stderr)
            return 2
        a.areas = ','.join(c for c in codes if c.lower() not in ('cc', 'country'))
    return run(a)


if __name__ == '__main__':
    sys.exit(main())
