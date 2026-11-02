"""MAP + PAGE plug-in: the official park page and its own map (PDF / image / map page).
Page ladder (method §3-4): 1) the POTA website link, kept only when it is on an official domain, opens, and its title / heading
names the park; a dead / moved / wrong link goes to fixes.csv ("link wrong/dead; correct official page: <URL>"), never edited;
2) the agency's own sitemap (robots.txt 'Sitemap:' lines or /sitemap.xml): URLs whose path carries the park's name words, read
and checked the same way. No search engines, no guessed URLs.
Map: links ON the official page (PDF / image named map, or a 'maps' page one click away). Picture maps are listed, not traced.
Output: docs-found-<area>.json {ref: {st, page, map, map_page, kind, date, agency, notes}}."""
import re, urllib.parse, xml.etree.ElementTree as ET
from core import names, read as rd
from core.agencies import official_domain, AGENCY_DOMAINS
from core.polite import links_in
from core.notes import Notes
from .base import Plugin, dump, today

MAP_FILE = re.compile(r'\.(pdf|jpe?g|png|gif)(\?|$)', re.I)
MAP_WORD = re.compile(r'(^|[^a-z])(maps?|brochure|carte|karte|mapa|kaart|kort)([^a-z]|$)', re.I)
AREA_DOMAINS = {'US-KY': ['parks.ky.gov', 'fw.ky.gov', 'eec.ky.gov', 'nps.gov', 'fs.usda.gov', 'fws.gov'],
                'US': ['nps.gov', 'fs.usda.gov', 'fws.gov', 'blm.gov'], 'CA': ['parks.canada.ca'], 'CA-ON': ['ontarioparks.ca'],
                'CA-BC': ['bcparks.ca'], 'CA-QC': ['sepaq.com'], 'CA-AB': ['albertaparks.ca'], 'CA-NS': ['parks.novascotia.ca'],
                # world, in hunt order: national / regional agency sites only (never NGOs, never tourism portals)
                'GB': ['nature.scot', 'naturalresources.wales', 'gov.uk'], 'DE': ['bfn.de'], 'RO': ['ancpi.ro', 'mmediu.ro'],
                'AU': ['parks.vic.gov.au', 'nationalparks.nsw.gov.au', 'parks.des.qld.gov.au', 'parks.sa.gov.au', 'parks.tas.gov.au', 'parks.dpaw.wa.gov.au'],
                'NL': ['staatsbosbeheer.nl'], 'SI': ['gov.si'], 'ES': ['miteco.gob.es'], 'IE': ['npws.ie'], 'FR': ['ofb.gouv.fr'],
                'DK': ['naturstyrelsen.dk', 'mst.dk'], 'AT': ['nationalparksaustria.at'], 'CH': ['bafu.admin.ch'], 'BE': ['natuurenbos.be', 'biodiversite.wallonie.be'],
                'MX': ['gob.mx'], 'CR': ['sinac.go.cr'], 'SE': ['naturvardsverket.se', 'lansstyrelsen.se'], 'FI': ['nationalparks.fi'], 'NO': ['miljodirektoratet.no']}


def names_park(p, title, text):
    w = names.core_words(p.get('n') or '')
    if not w: return False
    return names.words_in_text(w, title or '') or names.words_in_text(w, (text or '')[:1500])


class Docs(Plugin):
    KIND = 'docs'
    GAP_KINDS = ('map', 'page')

    def __init__(self): self._sm = {}

    def work_row(self, agency, row, eng, pass_no):
        p = eng.park(row); nt = Notes()
        out = {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'kind': 'docs', 'st': row['area'], 'agency': agency, 'date': today()}
        page, how = self.find_page(eng, row, p, nt, deep=True)
        if not page:
            bl = nt.any_blocked()       # an unread page is never NOT FOUND
            out.update(status='blocked' if bl else 'not found', notes=nt.as_dict(),
                       whynot={'tag': f"blocked: {len(bl)} official page(s) could not be read ({str(bl[0]['gave'])[8:60]})" if bl else 'no official page found on the agency site', 'date': today()})
            return out
        out['page'] = page.final_url or page.url; out['page_how'] = how; out['page_title'] = page.title
        m = self.find_map(eng, row, p, page, nt)
        if m: out['map'] = m; out['map_page'] = m.get('page')
        out['status'] = 'found' if m else 'candidate'
        nt.because(f"page title '{(page.title or '')[:80]}' names the park ({how})")
        nt.set_confidence('likely' if m else 'weak', 'open the page and the map: same park?')
        out['notes'] = nt.as_dict()
        return out

    # ---------------------------------------------------------------- page
    def find_page(self, eng, row, p, nt, deep=True):
        webs = [w for w in re.split(r'[\s,;|]+', str(p.get('web') or '')) if w.startswith('http')]
        for w in webs[:2]:
            host = urllib.parse.urlsplit(w).netloc
            if not _dom_ok(host):
                nt.looked(w, 'not an official domain (skipped)'); continue
            pg = rd.read(eng.P, w, ref_=p['ref'], kind='page')
            if pg.blocked:
                nt.looked(w, f'blocked ({pg.blocked[:60]})'); continue
            if names_park(p, pg.title, pg.text):
                nt.looked(w, 'POTA website link: opens and names the park'); return pg, 'POTA website'
            nt.looked(w, 'POTA website link opens but does not name the park')
            eng.fix(row, p, w, 'link opens but the page does not name the park')
        if not deep: return None, None
        doms = self.domains(eng, row, p, webs)
        words = names.core_words(p.get('n') or '')
        if not words: return None, None
        for d in doms[:4]:
            urls = self.sitemap(eng, d, p['ref'])
            if urls is None: nt.looked(f'sitemap {d}', 'blocked or none'); continue
            hits = sorted(((self._slug_score(u, words), u) for u in urls), reverse=True)
            hits = [u for s, u in hits if s >= 0.99][:3]
            nt.looked(f'sitemap {d}', f'{len(urls)} URLs, {len(hits)} name matches')
            for u in hits:
                pg = rd.read(eng.P, u, ref_=p['ref'], kind='page')
                if pg.blocked: nt.looked(u, f'blocked ({pg.blocked[:60]})'); continue
                if names_park(p, pg.title, pg.text):
                    for w in webs: eng.fix(row, p, w, f'link wrong/dead; correct official page: {pg.final_url or u}')
                    return pg, f'agency sitemap ({d})'
        return None, None

    @staticmethod
    def _slug_score(u, words):
        path = urllib.parse.unquote(urllib.parse.urlsplit(u).path).lower()
        toks = set(re.split(r'[^a-z0-9à-ÿ]+', names.strip_accents(path)))
        hit = sum(1 for w in words if names.strip_accents(w.lower()) in toks)
        return hit / len(words)

    def domains(self, eng, row, p, webs):
        out = []
        ag = row.get('agency') or ''
        for k, ds in AGENCY_DOMAINS.items():
            if k.lower() in ag.lower() or ag.lower() in k.lower(): out += ds
        for w in webs:
            h = urllib.parse.urlsplit(w).netloc.lower()
            if official_domain(h): out.append(re.sub(r'^www\.', '', h))
        if '.' in ag and official_domain(ag): out.append(ag)
        from core.agencies import PACK_DOMAINS
        out += AREA_DOMAINS.get(row['area'], []) + AREA_DOMAINS.get(row['area'][:2], []) + PACK_DOMAINS.get(row['area'], [])
        return list(dict.fromkeys(out))

    def sitemap(self, eng, domain, ref_):
        if domain in self._sm: return self._sm[domain]
        urls, todo, seen = [], [], set()
        for base in (f'https://www.{domain}', f'https://{domain}'):
            r = eng.P.get(base + '/robots.txt', ref_=ref_, kind='sitemap', ttl_days=30)
            if r.ok:
                todo += re.findall(r'(?im)^\s*sitemap:\s*(\S+)', r.text())
                if not todo: todo.append(base + '/sitemap.xml')
                break
        n = 0
        while todo and n < 25:
            u = todo.pop(0)
            if u in seen: continue
            seen.add(u); n += 1
            r = eng.P.get(u, ref_=ref_, kind='sitemap', ttl_days=30, max_bytes=40 * 2**20)
            if not r.ok: continue
            body = r.body
            if u.endswith('.gz') or body[:2] == b'\x1f\x8b':
                import gzip
                try: body = gzip.decompress(body)
                except OSError: continue
            locs = re.findall(rb'<loc>\s*([^<\s]+)\s*</loc>', body)
            if b'<sitemapindex' in body[:2000]: todo += [x.decode('utf-8', 'replace') for x in locs]
            else: urls += [x.decode('utf-8', 'replace').replace('&amp;', '&') for x in locs]
        self._sm[domain] = urls if urls else None
        return self._sm[domain]

    # ---------------------------------------------------------------- map
    def find_map(self, eng, row, p, page, nt):
        base = page.final_url or page.url
        links = links_in(page.html or '', base)
        words = names.core_words(p.get('n') or '')
        files = [(u, t) for u, t in links if MAP_FILE.search(u) and (MAP_WORD.search(t) or MAP_WORD.search(u.rsplit('/', 1)[-1]))
                 and _dom_ok(urllib.parse.urlsplit(u).netloc)]
        mpages = [(u, t) for u, t in links if not MAP_FILE.search(u) and MAP_WORD.search(t) and len(t) < 40
                  and urllib.parse.urlsplit(u).netloc == urllib.parse.urlsplit(base).netloc and u != base]
        via_page = base
        if not files:
            for u, t in mpages[:2]:
                pg = rd.read(eng.P, u, ref_=p['ref'], kind='map-page')
                if pg.blocked or not pg.html: continue
                files = [(x, tt) for x, tt in links_in(pg.html, pg.final_url or u) if MAP_FILE.search(x) and (MAP_WORD.search(tt) or MAP_WORD.search(x.rsplit('/', 1)[-1]))
                         and _dom_ok(urllib.parse.urlsplit(x).netloc)]
                if files: via_page = pg.final_url or u; break
        if not files: nt.looked(base + ' (map links)', 'no map link on the page'); return None
        files.sort(key=lambda f: -(names.words_in_text(words, f[1] + ' ' + f[0]) if words else 0))
        u, t = files[0]
        r = eng.P.get(u, ref_=p['ref'], kind='map', ttl_days=30, rng=(0, 65535))
        if r.blocked: nt.looked(u, f'map blocked ({r.blocked[:60]})'); return None
        if r.status not in (200, 206): nt.looked(u, f'map link HTTP {r.status}'); return None
        kind = 'pdf' if u.lower().split('?')[0].endswith('.pdf') else 'image'
        lm = (r.headers or {}).get('last-modified') if isinstance(r.headers, dict) else None
        m = {'url': u, 'status': 'ok', 'kind': kind, 'names_park': bool(words and names.words_in_text(words, t + ' ' + u)), 'page': via_page,
             'date': None, 'date_label': 'date unknown', 'posted': lm, 'via': 'the agency site', 'link_text': t}
        eng.picture_map(row, p, u, via_page)
        nt.looked(u, 'map link opens')
        return m

    def write(self, results, out_dir, eng=None):
        by = {}
        for r in results:
            if r.get('status') not in ('found', 'candidate'): continue
            by.setdefault(r['area'], {})[r['ref']] = {'st': r['area'], 'n': r.get('park'), 'page': r.get('page'), 'map': r.get('map'), 'map_page': r.get('map_page'),
                                                      'kind': (r.get('map') or {}).get('kind'), 'date': r.get('date'), 'agency': r.get('agency'),
                                                      'checked': r.get('date'), 'notes': r.get('notes')}
        for a, rows in by.items(): dump(rows, f'{out_dir}/docs-found-{a}.json')
        dump({r['ref']: r['whynot'] for r in results if r.get('whynot')}, f'{out_dir}/docs-whynot.json')

    def grade(self, results, eng):
        g = super().grade(results, eng)
        g['pages'] = sum(1 for r in results if r.get('page')); g['maps'] = sum(1 for r in results if r.get('map'))
        g['pages_official_domain'] = all(official_domain(urllib.parse.urlsplit(r['page']).netloc) for r in results if r.get('page'))
        return g


def _dom_ok(host):
    """Official domains only. If the club switches off source_policy.unofficial_docs_kept_apart, other domains are let in
    (never a never-use one) and every such row is stamped 'non-official: ...' by rules.stamp_rows."""
    from core import rules
    if official_domain(host): return True
    return not rules.on('source_policy.unofficial_docs_kept_apart') and not rules.forbidden(host)
