#!/usr/bin/env python3
"""RETRY FROM GITHUB (chat 10, Nov 1 2026; Brandon 6:11 PM 'might even try the blocked list try again list in the notes').
The outside research's 'RETRY FROM A BROWSER OR OTHER NETWORK' list (engine registry/retry.json, 24 country servers: Turkey,
Argentina, Japan, Thailand, Romania, ...) failed from the researcher's box. This asks every address ONCE from GitHub's network,
the honest way (kpc_manners: robots.txt obeyed, slow per host; a 403 / robot check / sign-in is reported, never bypassed).
  - an ArcGIS REST layer / service that answers  -> its polygon layers go on the club layer list (data/intake/queue.json,
    from 'retry list (GitHub try)'); the park-info engine tests them at the POTA pins on its next run -> collector -> chat 11
  - an OGC WFS that answers GetCapabilities       -> the same, as a WFS lead (the map-format converter reads WFS)
  - anything else that answers (a catalog / download page) -> listed for a person (data/intake/retry-github.json)
Writes data/intake/retry-github.json (what each address answered, dated). Decides nothing; never fails.
  python3 .github/scripts/kpc_retry_hosts.py [retry.json]"""
import json, pathlib, re, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kpc_manners import Manners  # noqa: E402

M = Manners('KPC retry list (chat 10): one honest try from GitHub')
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.github/scripts/draft/tools/kpc_engine/registry/retry.json')
OUT, QUEUE = pathlib.Path('data/intake/retry-github.json'), pathlib.Path('data/intake/queue.json')
TODAY = time.strftime('%Y-%m-%d')


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def get(u):
    st, hd, body, final = M.get(u, timeout=60)
    return st, (body or b'')[:2_000_000].decode('utf-8', 'replace'), final


def main():
    items = (load(SRC, {}) or {}).get('items') or []
    Q = load(QUEUE, {}) or {}; rows = Q.setdefault('rows', [])
    have = {str(r.get('url') or '').rstrip('/').lower() for r in rows}
    res, added = [], 0
    for it in items:
        urls = re.findall(r'https?://[^\s;|,)]+', str(it.get('address') or ''))
        for host in re.findall(r'(?<![/\w.])((?:[a-z0-9-]+\.)+(?:gov|gob|go|gouv|govt|org|gv|ac)\.[a-z]{2,3}|(?:[a-z0-9-]+\.)+gov\.[a-z]{2})(?![\w/])', str(it.get('address') or ''), re.I):
            if not any(host in u for u in urls): urls.append('https://' + host + '/')
        for u in urls[:4]:
            u = u.rstrip('.')
            rest = re.search(r'/rest/services', u, re.I)
            ask = u if not rest else re.sub(r'(/(?:MapServer|FeatureServer))(?:/\d+)?.*$', r'\1', u, flags=re.I) + '?f=json'
            if re.search(r'/(?:geoserver|ows|wfs)', u, re.I) and 'request=' not in u.lower():
                ask = u.split('?')[0] + '?service=WFS&request=GetCapabilities'
            st, body, final = get(ask)
            r = {'id': it.get('id'), 'country': it.get('country'), 'cc': it.get('cc'), 'asked': ask, 'answer': st, 'date': TODAY}
            if not (isinstance(st, int) and st < 400):
                r['result'] = {403: '403: refused (not bypassed)', 'robots': 'robots.txt says no (not asked)', 'robots-unreadable': 'robots.txt could not be read: tried again next run', 'deferred': 'slow host: tried again next run', 'crawl-delay': 'Crawl-delay over 120 s: for a person (not asked)'}.get(st, f'no answer ({st})'); res.append(r); continue
            if rest:
                try: j = json.loads(body)
                except ValueError: j = {}
                lays = [l for l in (j.get('layers') or []) if 'olygon' in str(l.get('geometryType', '')) or not l.get('geometryType')]
                base = ask.split('?')[0]
                for l in lays[:40]:
                    lu = f"{base}/{l.get('id')}"
                    if lu.lower() in have: continue
                    rows.append({'url': lu, 'area': it.get('cc'), 'cc': it.get('cc'), 'title': f"{l.get('name')} ({it.get('agency')})"[:120], 'publisher': it.get('agency') or '',
                                 'from': 'retry list (GitHub try)', 'added': TODAY, 'note': f"{it.get('id')}: failed from the research box, answered from GitHub", 'expect': None})
                    have.add(lu.lower()); added += 1
                r['result'] = f'ArcGIS answered: {len(lays)} layers to the layer list' if lays else 'ArcGIS answered: no polygon layers listed'
            elif 'WFS_Capabilities' in body or 'wfs:WFS_Capabilities' in body or 'FeatureTypeList' in body:
                names = re.findall(r'<(?:wfs:)?Name>([^<]{2,120})</(?:wfs:)?Name>', body)
                hits = [n for n in names if re.search(r'protect|park|parque|reserv|natur|area|apn|snap|conserv|forest|wild|national', n, re.I)][:20]
                base = ask.split('?')[0]
                for n in hits:
                    lu = f'{base}?service=WFS&request=GetFeature&typeName={urllib.parse.quote(n)}'
                    if lu.lower() in have: continue
                    rows.append({'url': lu, 'area': it.get('cc'), 'cc': it.get('cc'), 'title': f'{n} ({it.get("agency")})'[:120], 'publisher': it.get('agency') or '',
                                 'from': 'retry list (GitHub try)', 'added': TODAY, 'note': f"{it.get('id')}: WFS answered from GitHub (the converter reads WFS)", 'expect': None})
                    have.add(lu.lower()); added += 1
                r['result'] = f'WFS answered: {len(names)} feature types, {len(hits)} park-like to the layer list'
            else:
                r['result'] = 'answered (a page, not a layer service): a person follows it'
                r['title'] = (re.search(r'<title>([^<]{1,120})', body, re.I) or [None, ''])[1].strip()
            res.append(r)
    if added: json.dump(Q, open(QUEUE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump({'about': __doc__.split('\n')[0], 'date': TODAY, 'added_to_layer_list': added, 'tries': res}, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    ok = sum(1 for r in res if isinstance(r['answer'], int) and r['answer'] < 400)
    print(f'::notice title=Retry list (GitHub try)::{len(items)} servers, {len(res)} addresses asked: {ok} answered, {added} layers added to the layer list; '
          + '; '.join(f"{r['country']}: {r['result'][:50]}" for r in res if isinstance(r['answer'], int) and r['answer'] < 400)[:600], flush=True)


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Retry list::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
