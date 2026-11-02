"""Measure T3 acceptance on a finished run: python3 t3_measure.py <out> <docs/US-XX.json> <parkinfo/US-XX.json>"""
import json, sys, glob, os, re
from urllib.parse import urlparse, unquote
out, docs, pinfo = sys.argv[1:4]
def norm(u):
    p = urlparse(u.strip())
    h = (p.hostname or '').lower().removeprefix('www.')
    path = unquote(p.path or '/').rstrip('/').lower()
    path = re.sub(r'/index\.(html?|php|aspx?)$', '', path)
    return h + path + ('?' + p.query if p.query else '')
refs = set(json.load(open(pinfo))['parks'])
got, files_by_host, items_by_host = {}, {}, {}
for f in glob.glob(os.path.join(out, 'sitemaps', '*.json')):
    if f.endswith('.sources.json'):
        continue
    d = json.load(open(f))
    for m in d['maps'] + d['pages']:
        got[norm(m['url'])] = d['host']
    tn = [m for m in d['maps'] if any(r['ref'] in refs for r in m['refs'])]
    items_by_host[d['host']] = len(tn)
    files_by_host[d['host']] = sum(1 for m in tn if re.search(r'\.(pdf|jpe?g|png)$', unquote(urlparse(m['url']).path), re.I))
links = [(r, v['map']['url']) for r, v in json.load(open(docs))['parks'].items() if (v.get('map') or {}).get('url')]
hosts_read = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(out, 'sitemaps', '*.json')) if not f.endswith('.sources.json')}
hit = [(r, u) for r, u in links if norm(u) in got]
miss = [(r, u) for r, u in links if norm(u) not in got]
print(f'docs map links: {len(links)}; found in output: {len(hit)} = {100*len(hit)/max(1,len(links)):.0f}%')
for r, u in miss: print('  MISS', r, u)
print('map items naming a park of the area, by host:', items_by_host)
print('  of which files (pdf/jpg/png):', files_by_host, 'total', sum(files_by_host.values()), 'items total', sum(items_by_host.values()))
