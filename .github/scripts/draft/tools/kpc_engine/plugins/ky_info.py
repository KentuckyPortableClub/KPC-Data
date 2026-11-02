"""HOURS / FEES / CLOSURES plug-ins: KENTUCKY ONLY (scope.guard refuses any other area).
Method (KPC_method_updated.md): official agency page only; text copied word for word; standard wording when nothing is stated
("not stated on the agency page"); blocked pages are left blank and logged, never NOT FOUND. NPS parks: the public keyless
structured_data_<code>.json behind the page (operatingHours / entranceFees). Links are only the ones found on the page."""
import json, re, urllib.parse
from core import read as rd, rule_g, scope
from core.polite import links_in
from core.notes import Notes
from .base import Plugin, dump, today
from .docs import Docs

TIME = re.compile(r'\b\d{1,2}(:\d{2})?\s?(a\.?m\.?|p\.?m\.?)|\bdawn\b|\bdusk\b|\bsunrise\b|\bsunset\b|24 hours|open (all year|year[- ]round|daily)', re.I)
FEE = re.compile(r'\$\s?\d|\bno (entrance |day[- ]use )?fees?\b|\bfree\b|\bfee(s)? (is|are|per)\b|admission|day[- ]use fee', re.I)
CLOSE = re.compile(r'\b(closed|closure|closures|alert|temporarily|road work|burn ban|flood)\b', re.I)
SUB = re.compile(r'hours|fees|rates|pricing|admission|operating|alerts|conditions|closures', re.I)


def lines_matching(text, rx, n=4, maxlen=300):
    out = []
    for ln in (text or '').split('\n'):
        ln = ln.strip()
        if 8 <= len(ln) <= maxlen and rx.search(ln) and ln not in out: out.append(ln)
        if len(out) >= n: break
    return out


class _KY(Plugin):
    WHAT = 'hours'

    def wants(self, row):
        return row.get('area') == 'US-KY' and super().wants(row)

    def work_row(self, agency, row, eng, pass_no):
        scope.guard(self.KIND, row['area'])
        p = eng.park(row); nt = Notes()
        out = {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'kind': self.KIND, 'agency_group': agency, 'date': today()}
        page, how = eng.docs.find_page(eng, row, p, nt, deep=True)
        if not page:
            out.update(status='blocked' if nt.blocked_only() else 'not found', notes=nt.as_dict(),
                       whynot={'tag': 'NO AGENCY PAGE' if not nt.blocked_only() else 'blocked', 'date': today()})
            return out
        url = page.final_url or page.url
        texts, unread = [(url, page.text, page.how)], []
        sj = rd.structured_for(url)
        if sj:
            r, j = eng.P.get_json(sj, ref_=p['ref'], kind=self.KIND)
            if j: texts.insert(0, (sj, self._nps_text(j), 'NPS structured data'))
            elif r.blocked: unread.append((sj, r.blocked))
        for u, t in links_in(page.html or '', url):
            if SUB.search(t) and len(t) < 50 and urllib.parse.urlsplit(u).netloc == urllib.parse.urlsplit(url).netloc and u != url:
                pg = rd.read(eng.P, u, ref_=p['ref'], kind=self.KIND)
                if not pg.blocked: texts.append((pg.final_url or u, pg.text, pg.how))
                else: unread.append((u, pg.blocked)); nt.looked(u, f'blocked ({pg.blocked[:60]})')
                if len(texts) >= 4: break
        got = self.extract(texts)
        nt.looked(url, f'official page read ({how}, {page.how})')
        for u, _, h in texts[1:]: nt.looked(u, f'linked page read ({h})')
        if got:
            out.update(status='found', **got)
            nt.because('copied word for word from the agency page'); nt.set_confidence('likely', 'compare with the page: same park, current season?')
        elif unread:      # never NOT FOUND while a linked official page went unread
            out.update(status='blocked', url=url, whynot={'tag': f'blocked: {len(unread)} linked official page(s) could not be read ({unread[0][1][:50]})', 'date': today()})
        else:
            out.update(status='not found', **{self.WHAT: f'not stated on the agency page'}, url=url,
                       whynot={'tag': 'NOT FOUND (pages checked, nothing stated)', 'date': today()})
        out['notes'] = nt.as_dict()
        return out

    @staticmethod
    def _nps_text(j):
        L = []
        for oh in (j.get('operatingHours') or []) if isinstance(j, dict) else []:
            if isinstance(oh, dict):
                L.append(f"Hours: {oh.get('name', '')}: {oh.get('description', '')}")
                sh = oh.get('standardHours') or {}
                if sh: L.append('Standard hours: ' + '; '.join(f'{k}: {v}' for k, v in sh.items()))
        for fe in (j.get('entranceFees') or []) if isinstance(j, dict) else []:
            if isinstance(fe, dict): L.append(f"Fee: {fe.get('title', '')} ${fe.get('cost', '')}: {fe.get('description', '')}")
        return '\n'.join(L) if L else rd.json_text(j)


class Hours(_KY):
    KIND = 'hours'; WHAT = 'hours'; GAP_KINDS = ('hours',)

    def extract(self, texts):
        for u, t, h in texts:
            ls = [x for x in lines_matching(t, TIME, n=8) if rule_g.hours_line_ok(x, 'hours')[0]][:4]   # chat 11's 12/12 rules
            if ls: return {'hours': ' | '.join(ls), 'url': u, 'how': h}
        return None

    def write(self, results, out_dir, eng=None):
        _merge_hours(results, out_dir, 'hours')


class Fees(_KY):
    KIND = 'fees'; WHAT = 'fees'; GAP_KINDS = ('fees',)

    def extract(self, texts):
        for u, t, h in texts:
            ls = [x for x in lines_matching(t, FEE, n=8) if rule_g.hours_line_ok(x, 'fees')[0]][:4]
            if ls: return {'fees': ' | '.join(ls), 'fee_url': u, 'url': u, 'how': h}
        return None

    def write(self, results, out_dir, eng=None):
        _merge_hours(results, out_dir, 'fees')


class Closures(_KY):
    KIND = 'closures'; WHAT = 'notice'; GAP_KINDS = ('closures',)

    def extract(self, texts):
        for u, t, h in texts:
            ls = lines_matching(t, CLOSE, n=3)
            ls = [x for x in ls if not re.search(r'cookie|javascript|privacy', x, re.I)]
            if ls: return {'notice': ' | '.join(ls), 'url': u, 'how': h}
        return {'notice': 'no closure stated on the agency page', 'url': texts[0][0], 'how': texts[0][2]}

    def write(self, results, out_dir, eng=None):
        d = {'area': 'US-KY', 'read': today(), 'sources': {}, 'notices': []}
        for r in results:
            if r.get('area') != 'US-KY' or not r.get('url'): continue
            d['sources'][r['ref']] = {'url': r['url'], 'checked': r['date']}
            if r.get('notice') and not r['notice'].startswith('no closure'):
                d['notices'].append({'ref': r['ref'], 'park': r.get('park'), 'text': r['notice'], 'url': r['url'], 'date': r['date']})
        dump(d, f'{out_dir}/closures/US-KY.json')


def _merge_hours(results, out_dir, key):
    import pathlib
    p = pathlib.Path(out_dir) / 'hours' / 'US-KY.json'
    d = json.load(open(p)) if p.exists() else {'area': 'US-KY', 'read': today(), 'parks': {}}
    for r in results:
        if r.get('area') != 'US-KY': continue
        row = d['parks'].setdefault(r['ref'], {'n': r.get('park')})
        if r.get('status') == 'found':
            row[key] = r[key]; row[key + '_url'] = r.get('url'); row['checked'] = r['date']; row.setdefault('notes', []).append(f"{key}: {r.get('how')}")
        elif r.get('status') == 'not found' and r.get(key):
            row[key] = r[key]; row[key + '_url'] = r.get('url'); row['checked'] = r['date']
        else:
            row.setdefault('blocked', []).append(key)
        row['status'] = 'FOUND' if row.get('hours') and row.get('fees') and 'not stated' not in str(row.get('hours')) else 'PARTLY' if (row.get('hours') or row.get('fees')) else 'NOT FOUND'
    dump(d, p)
