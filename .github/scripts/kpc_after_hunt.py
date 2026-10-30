#!/usr/bin/env python3
"""AFTER A GIS-HUNTER PASS (chat 10, Oct 30 2026; HQ 7:50 AM (1), Brandon 7:43 AM). Runs at the END of a hunter pass, by itself; the
hunter's logic is untouched (Brandon's hold to Nov 6). For the parks the pass left with no SURE / LIKELY find:
  - a WEBSITE-NAME READ: the park's official page (documents bot 'page', else POTA's website) is read once (plain, manners) and its
    <title> compared with POTA's name by the tiers (T-1): data/gis-hunter/name-reads.json {ref: {url, title, tier, why, date}};
    re-read after 30 days only. 60 a pass per area, 400 a pass in all.
  - the areas go to the documents bot (kpc-docs, official maps / documents) for one run: printed as DOCS_AREAS=...
Notes only: nothing goes to the waiting room or a key. Never fails.
  LINKS=../links python3 kpc_after_hunt.py AREA [AREA ...]   (blank = every area in data/gis-hunter/state.json run today)"""
import datetime as dt, html, json, os, pathlib, re, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_tiers as T  # noqa: E402
try:
    from kpc_manners import Manners
    M = Manners('KPC after-hunt name reads (chat 10)')
except Exception:  # noqa: BLE001
    M = None
OUT = pathlib.Path('data/gis-hunter'); NR = OUT / 'name-reads.json'
TODAY = dt.date.today()


def load(p, d=None):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def site_of(area, r):
    if area.startswith('US-'):
        d = (((load(f'data/docs/{area}.json', {}) or {}).get('parks') or {}).get(r) or {}).get('page')
        if d: return d
        v = ((load(f'data/parkinfo/{area}.json', {}) or {}).get('parks') or {}).get(r) or []
        if len(v) > 1 and str(v[1]).startswith('http'): return v[1]
    w = ((load('data/parkinfo-web.json', {}) or {}).get('parks') or {}).get(r) or {}
    return w.get('web') or w.get('agency_page') or ''


def main():
    want = sys.argv[1:]
    st = load(OUT / 'state.json', {}) or {}
    areas = want or [a for a, v in st.items() if (v or {}).get('run') == TODAY.isoformat()]
    reads = load(NR, {}) or {}
    total, docs = 0, []
    for area in areas:
        R = ((load(OUT / f'{area}.json', {}) or {}).get('parks') or {})
        left = [r for r, x in R.items() if not str(x.get('verdict', '')).startswith('candidate')]
        if left: docs.append(area)
        n = 0
        for r in left:
            if n >= 60 or total >= 400 or not M: break
            old = reads.get(r) or {}
            try:
                if old.get('date') and (TODAY - dt.date.fromisoformat(old['date'])).days < 30: continue
            except ValueError: pass
            u = site_of(area, r)
            if not u.startswith('http'): continue
            n += 1; total += 1
            try:
                s, hd, body, final = M.get(u)
                t = re.search(r'<title[^>]*>(.*?)</title>', body.decode('utf-8', 'replace'), re.I | re.S) if isinstance(s, int) and s < 400 and body else None
                title = ' '.join(html.unescape(t.group(1)).split())[:160] if t else ''
            except Exception as e:  # noqa: BLE001
                title, s = '', f'{type(e).__name__}'
            pn = R[r].get('park') or ''
            core = re.split(r'\s[|\-–—:]\s', title)[0] if title else ''
            tier, why = T.tier(pn, core) if core else ('', f'no title (answer {s})')
            reads[r] = {'url': u, 'title': title, 'tier': tier, 'why': why, 'date': TODAY.isoformat(), 'area': area}
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(reads, open(NR, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=After hunt::{total} website-name reads; documents bot next for {len(docs)} areas' + (f'; manners {M.stat}' if M else ''))
    print('DOCS_AREAS=' + ' '.join(a for a in docs if a.startswith('US-')))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=After hunt::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
