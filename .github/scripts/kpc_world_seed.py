#!/usr/bin/env python3
"""WORLD HARVESTER, the seed (Fable, chat 2, Oct 27 2026). Builds data/harvest/countries.json = where to look per country, from
(1) chat 8's scouting in the KPC-Links checkout (.claude/build/research/WORLD + UK: every map-server / WFS / catalog address it
recorded, and the AGOL organisations behind them) and (2) the hand list below (national open-data catalogs, native-language park
words, country names). The harvester reads the result; a person edits the hand list, never the generated file.
Usage: run from the KPC-Data root with the KPC-Links checkout at ./links (the workflow does this)."""
import glob, json, os, pathlib, re, sys

LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
OUT = pathlib.Path('data/harvest/countries.json')

# code: (English name, [native / other names], [park words in the local language], [catalogs], stage, queue order)
# catalogs: ('ckan', base) | ('datagouv', base) | ('dane', base) ; AGOL + the country's own servers come from the research files
HAND = {
 'JP': ('Japan', ['日本'], ['国立公園', '国定公園', '自然公園', '保護区', 'national park'], [('ckan', 'https://data.e-gov.go.jp/data')], 1, 1),
 'GB': ('United Kingdom', ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Great Britain'], ['national park', 'nature reserve', 'country park', 'national landscape', 'open access land', 'national trail'], [('ckan', 'https://data.gov.uk')], 1, 2),
 'DE': ('Germany', ['Deutschland'], ['Nationalpark', 'Naturschutzgebiet', 'Naturpark', 'Schutzgebiet', 'Biosphärenreservat', 'Landschaftsschutzgebiet'], [('ckan', 'https://www.govdata.de/ckan')], 1, 3),
 'PL': ('Poland', ['Polska'], ['park narodowy', 'park krajobrazowy', 'rezerwat przyrody', 'formy ochrony przyrody', 'obszar chroniony'], [('dane', 'https://api.dane.gov.pl/1.4')], 1, 4),
 'AU': ('Australia', [], ['national park', 'conservation park', 'nature reserve', 'protected areas', 'state forest', 'land tenure'], [('ckan', 'https://data.gov.au/data'), ('ckan', 'https://data.nsw.gov.au/data'), ('ckan', 'https://data.qld.gov.au'), ('ckan', 'https://discover.data.vic.gov.au')], 1, 5),
 'FR': ('France', [], ['parc national', 'parc naturel régional', 'réserve naturelle', 'espace protégé', 'forêt domaniale', 'forêts publiques'], [('datagouv', 'https://www.data.gouv.fr/api/1')], 1, 6),
 'ES': ('Spain', ['España'], ['parque nacional', 'parque natural', 'espacio natural protegido', 'reserva natural', 'red natura'], [], 1, 7),
 'IT': ('Italy', ['Italia'], ['parco nazionale', 'parco regionale', 'riserva naturale', 'area protetta', 'aree protette'], [('ckan', 'https://www.dati.gov.it/opendata')], 1, 8),
 'NO': ('Norway', ['Norge'], ['nasjonalpark', 'naturreservat', 'verneområde', 'friluftsliv', 'statlig sikra'], [], 1, 9),
 'NL': ('Netherlands', ['Nederland'], ['nationaal park', 'natuurgebied', 'natura 2000', 'natuurmonument'], [('ckan', 'https://data.overheid.nl/data')], 1, 10),
 'CH': ('Switzerland', ['Schweiz', 'Suisse', 'Svizzera'], ['Nationalpark', 'Naturpark', 'Pärke', 'Schutzgebiet', 'parc naturel'], [('ckan', 'https://opendata.swiss')], 1, 11),
 'PT': ('Portugal', [], ['parque natural', 'parque nacional', 'reserva natural', 'área protegida', 'áreas protegidas'], [('ckan', 'https://dados.gov.pt/api')], 1, 12),
 'RO': ('Romania', ['România'], ['parc național', 'parc natural', 'arie protejată', 'rezervație'], [('ckan', 'https://data.gov.ro')], 1, 13),
 'AT': ('Austria', ['Österreich'], ['Nationalpark', 'Naturpark', 'Naturschutzgebiet', 'Schutzgebiet', 'Europaschutzgebiet'], [('ckan', 'https://www.data.gv.at/katalog')], 1, 14),
 'SE': ('Sweden', ['Sverige'], ['nationalpark', 'naturreservat', 'skyddad natur', 'naturvårdsregistret'], [], 1, 15),
 'SI': ('Slovenia', ['Slovenija'], ['narodni park', 'krajinski park', 'naravni rezervat', 'zavarovano območje'], [('ckan', 'https://podatki.gov.si')], 1, 16),
 'CZ': ('Czechia', ['Česko', 'Czech Republic'], ['národní park', 'chráněná krajinná oblast', 'přírodní rezervace', 'zvláště chráněné území'], [('ckan', 'https://data.gov.cz')], 1, 17),
 'BE': ('Belgium', ['België', 'Belgique'], ['natuurreservaat', 'nationaal park', 'réserve naturelle', 'parc naturel', 'natuurgebied'], [], 1, 18),
 'DK': ('Denmark', ['Danmark'], ['nationalpark', 'fredede områder', 'naturpark', 'naturreservat'], [], 1, 19),
 'IE': ('Ireland', ['Éire'], ['national park', 'nature reserve', 'special area of conservation', 'coillte'], [('ckan', 'https://data.gov.ie')], 1, 20),
 'SK': ('Slovakia', ['Slovensko'], ['národný park', 'chránená krajinná oblasť', 'prírodná rezervácia', 'chránené územie'], [('ckan', 'https://data.gov.sk')], 1, 21),
 'HR': ('Croatia', ['Hrvatska'], ['nacionalni park', 'park prirode', 'zaštićeno područje', 'posebni rezervat'], [('ckan', 'https://data.gov.hr')], 1, 22),
 'FI': ('Finland', ['Suomi'], ['kansallispuisto', 'luonnonsuojelualue', 'luonnonpuisto', 'suojelualue'], [('ckan', 'https://www.avoindata.fi/data')], 1, 23),
 'HU': ('Hungary', ['Magyarország'], ['nemzeti park', 'tájvédelmi körzet', 'természetvédelmi terület', 'védett terület'], [], 1, 24),
 'EE': ('Estonia', ['Eesti'], ['rahvuspark', 'kaitseala', 'looduskaitseala', 'maastikukaitseala'], [('ckan', 'https://avaandmed.eesti.ee')], 1, 25),
 'LV': ('Latvia', ['Latvija'], ['nacionālais parks', 'dabas parks', 'dabas liegums', 'aizsargājamā teritorija'], [('ckan', 'https://data.gov.lv/dati')], 1, 26),
 'LT': ('Lithuania', ['Lietuva'], ['nacionalinis parkas', 'regioninis parkas', 'draustinis', 'saugoma teritorija'], [('ckan', 'https://data.gov.lt')], 1, 27),
 'LU': ('Luxembourg', ['Lëtzebuerg'], ['parc naturel', 'réserve naturelle', 'zone protégée', 'forêts publiques'], [('ckan', 'https://data.public.lu')], 1, 28),
 'NZ': ('New Zealand', ['Aotearoa'], ['public conservation land', 'national park', 'regional park', 'conservation area', 'reserve'], [('ckan', 'https://catalogue.data.govt.nz')], 3, 29),
 'DO': ('Dominican Republic', ['República Dominicana'], ['parque nacional', 'área protegida', 'reserva científica', 'monumento natural'], [], 2, 30),
 'BR': ('Brazil', ['Brasil'], ['unidade de conservação', 'parque nacional', 'parque estadual', 'reserva biológica', 'área de proteção ambiental'], [('ckan', 'https://dados.gov.br/dados')], 3, 31),
 'KR': ('South Korea', ['대한민국', 'Korea'], ['국립공원', '보호지역', '도립공원', 'national park'], [], 3, 32),
 'MX': ('Mexico', ['México'], ['área natural protegida', 'parque nacional', 'reserva de la biosfera', 'ANP'], [('ckan', 'https://datos.gob.mx')], 2, 33),
 'TH': ('Thailand', ['ประเทศไทย'], ['อุทยานแห่งชาติ', 'เขตรักษาพันธุ์สัตว์ป่า', 'national park', 'wildlife sanctuary'], [('ckan', 'https://data.go.th')], 3, 34),
 'ZA': ('South Africa', [], ['national park', 'nature reserve', 'protected areas', 'protected environment'], [], 3, 35),
 'AR': ('Argentina', [], ['parque nacional', 'área protegida', 'reserva natural', 'parque provincial'], [('ckan', 'https://datos.gob.ar')], 3, 36),
 'CL': ('Chile', [], ['parque nacional', 'reserva nacional', 'área silvestre protegida', 'monumento natural'], [('ckan', 'https://datos.gob.cl')], 3, 37),
 'CO': ('Colombia', [], ['parque nacional natural', 'área protegida', 'reserva natural', 'SINAP'], [], 3, 38),
 'PH': ('Philippines', ['Pilipinas'], ['protected area', 'national park', 'natural park', 'NIPAS'], [], 3, 39),
 'TR': ('Turkey', ['Türkiye'], ['milli park', 'tabiat parkı', 'korunan alan', 'tabiatı koruma alanı'], [], 3, 40),
 'RU': ('Russia', ['Россия'], ['национальный парк', 'заповедник', 'заказник', 'особо охраняемая природная территория', 'ООПТ'], [], 3, 41),
 'CN': ('China', ['中国'], ['国家公园', '自然保护区', '自然公园', 'nature reserve'], [], 3, 42),
}
RESEARCH_FILE = {'GB': ['WORLD/KPC_W_GB_desk.md', 'UK/*.md'], 'DO': ['WORLD/KPC_X1_DO_desk.md'], 'MX': ['WORLD/KPC_X3_MX_CENTRALAM_desk.md'],
                 'EE': ['WORLD/KPC_W_BALTIC_desk.md'], 'LV': ['WORLD/KPC_W_BALTIC_desk.md'], 'LT': ['WORLD/KPC_W_BALTIC_desk.md'], 'LU': ['WORLD/KPC_W_BALTIC_desk.md']}
GOVWORDS = ('ministry|ministerio|ministère|ministerium|ministero|ministerstwo|agency|agentur|agence|agencia|agenzia|department|dept|'
            'government|gouvernement|gobierno|governo|regierung|bund|federal|national|nacional|nazionale|nationale|natural england|naturescot|'
            'natural resources wales|forestry|forest service|parks|parques|parcs|parchi|environment|umwelt|environnement|ambiente|medio ambiente|'
            'conservation|naturschutz|nature|natur|natuur|natura|miljø|miljö|ympäristö|conselleria|generalitat|junta de|xunta|regione|'
            'landesamt|land |canton|kanton|county council|crown|state of|geological survey|survey|cartográfic|geoportal|lasy|gdoś|gios|'
            'bfn|icnf|inpn|mnhn|ign|metsähallitus|naturvårdsverket|miljødirektoratet|rvo|pdok|bafu|ofev|doc |department of conservation|'
            'anb|coillte|npws|moe|環境省|国土|自然|ministerstvo|ministerul|agenția|úrad|urząd|ministère de|institut|instituto|istituto')


def main():
    seeds = {}
    for cc, (name, other, words, cats, stage, order) in HAND.items():
        files = RESEARCH_FILE.get(cc) or [f'WORLD/KPC_W_{cc}_desk.md', f'WORLD/KPC_Y_{cc}_desk.md']
        txt = ''
        for pat in files:
            for f in glob.glob(str(LINKS / '.claude/build/research' / pat)):
                try: txt += open(f, encoding='utf-8').read() + '\n'
                except Exception: pass  # noqa: BLE001
        urls = sorted(set(u.rstrip('.,;)') for u in re.findall(r'https?://[^\s<>)|,`"\']+', txt)))
        servers, ogc, orgs, pages = set(), set(), set(), set()
        for u in urls:
            m = re.match(r'(https?://[^/]+/[^?#]*?/rest/services)', u, re.I)
            if m: servers.add(m.group(1).rstrip('/')); continue
            m = re.match(r'https?://services\d*(?:-[a-z0-9]+)?\.arcgis\.com/([A-Za-z0-9]+)/', u)
            if m: orgs.add(m.group(1))
            if re.search(r'wfs|wms|geoserver|/ows\b|ogcapi|/wss/', u, re.I): ogc.add(u.split('?')[0]); continue
            if re.search(r'/dataset[s]?/', u): pages.add(u)
        orgs |= {m.group(1) for m in re.finditer(r'arcgis\.com/([A-Za-z0-9]{16,})/', txt)}
        seeds[cc] = {'name': name, 'names': [name] + other, 'words': words, 'catalogs': cats, 'stage': stage, 'order': order,
                     'servers': sorted(servers), 'agol_orgs': sorted(orgs), 'ogc': sorted(ogc), 'catalog_pages': sorted(pages)[:40],
                     'known_good': sorted(u for u in urls if re.search(r'/rest/services/|wfs|ows|ogcapi', u, re.I))[:60],
                     'research': [os.path.relpath(f, LINKS) for pat in files for f in glob.glob(str(LINKS / '.claude/build/research' / pat))]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'about': 'Where the WORLD HARVESTER looks, per country: chat 8\'s scouted addresses (servers, WFS, AGOL organisations) + the hand list in kpc_world_seed.py (catalogs, native park words). Regenerated by the workflow; edit the script, not this file.',
                               'govwords': GOVWORDS, 'countries': seeds}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    n = sum(len(v['servers']) + len(v['ogc']) + len(v['agol_orgs']) for v in seeds.values())
    print(f'::notice title=World harvester seed::{len(seeds)} countries, {n} scouted addresses + organisations', flush=True)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=World harvester seed::stopped: {e}', flush=True)  # noqa: BLE001
    sys.exit(0)
