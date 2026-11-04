#!/usr/bin/env python3
"""Offline test for kpc_answer_sheet_check.py (Nov 3 remake: K1-K4 + shared words). Local fake ArcGIS layer on 127.0.0.1 only.
Run from the KPC-Data root:  python3 .github/scripts/tests/test_answer_sheet_check_offline.py"""
import csv, http.server, json, os, subprocess, sys, tempfile, threading, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.abspath(os.path.join(HERE, '..'))
REC = {1: {'OBJECTID': 1, 'NAME': 'Alpha WMA', 'ACRES': 100}, 2: {'OBJECTID': 2, 'NAME': 'Beta SP', 'ACRES': 'about 50'},
       3: {'OBJECTID': 3, 'NAME': 'Gamma SF', 'ACRES': 300}}
hits = []
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = urllib.parse.urlparse(self.path); q = dict(urllib.parse.parse_qsl(p.query)); hits.append(self.path)
        if p.path == '/robots.txt': self.send_response(404); self.end_headers(); return
        if p.path.startswith('/cut/'):   # a layer that says exceededTransferLimit
            body = {'fields': [{'name': 'OBJECTID', 'type': 'esriFieldTypeOID'}, {'name': 'NAME', 'type': 'esriFieldTypeString'}], 'objectIdField': 'OBJECTID', 'maxRecordCount': 1000} \
                if not p.path.endswith('/query') else {'features': [{'attributes': REC[1]}], 'exceededTransferLimit': True}
        elif p.path.endswith('/query'):
            ids = [int(x) for x in (q.get('objectIds') or '').split(',') if x]
            body = {'features': [{'attributes': REC[i]} for i in ids if i in REC]}
            if q.get('where'): body = {'features': []}
        else:
            body = {'fields': [{'name': 'OBJECTID', 'type': 'esriFieldTypeOID'}, {'name': 'NAME', 'type': 'esriFieldTypeString'}, {'name': 'ACRES', 'type': 'esriFieldTypeDouble'}],
                    'objectIdField': 'OBJECTID', 'maxRecordCount': 2}
        b = json.dumps(body).encode(); self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b)
srv = http.server.HTTPServer(('127.0.0.1', 18811), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
L, CUT = 'http://127.0.0.1:18811/arcgis/rest/services/x/MapServer/0', 'http://127.0.0.1:18811/cut/MapServer/0'
d = tempfile.mkdtemp(); sheet = os.path.join(d, 'US.csv'); out = os.path.join(d, 'check', 'US.json')
cols = ['ref', 'key_id', 'status', 'approved_by', 'approved_date', 'fp', 'source_url', 'record_id', 'unit_id', 'unit_id_field']
rows = [['US-1', '1', 'YES', 'Brandon', '2026-11-01', '["Alpha WMA", 100]', L, '1', '', ''],
        ['US-2', '2', 'APPROVED', 'Brandon', '2026-11-01', '["Beta SP", 50]', L, '2', '', ''],
        ['US-3', '3', 'NOT SURE', '', '', '["Gamma SF", "300"]', L, '3', '', ''],
        ['US-4', 'bpad:Bullock Pen', 'YES', 'Brandon', '2026-11-01', '["Bullock Pen", 10]', L, 'bpad:Bullock Pen', '', ''],
        ['US-5', '9', 'PROPOSED', '', '', '["Zeta", 1]', L, '9', '', ''],
        ['US-6', '1', 'YES', 'Brandon', '2026-11-01', '["Alpha WMA", 100]', CUT, '1', '', '']]
with open(sheet, 'w', newline='') as f: w = csv.writer(f); w.writerow(cols); w.writerows(rows)
os.makedirs(os.path.dirname(out)); pp = out.replace('.json', '-proposals.csv')
with open(pp, 'w', newline='') as f:   # a person's earlier answer that must survive the night
    w = csv.writer(f); w.writerow(['ref', 'key_id', 'record_id', 'column', 'old', 'proposed', 'why', 'answer', 'answered_by'])
    w.writerow(['US-9', '77', '77', 'record_id', '77', '78', 'old proposal', 'yes', 'Brandon'])
cache = os.path.join(d, 'cache')
env = dict(os.environ, KPC_MANNERS_CACHE=cache, KPC_MANNERS_CACHE_ALL='1', KPC_SLOW_HOST_DELAY='0')
r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'kpc_answer_sheet_check.py'), '--sheet', sheet, '--out', out], env=env, capture_output=True, text=True, timeout=120)
srv.shutdown()
bad = []
def check(n, ok, x=''):
    print(('PASS ' if ok else 'FAIL ') + n, x)
    if not ok: bad.append(n)
check('the run finished', r.returncode == 0, r.stderr[-400:])
J = json.load(open(out)); R = J['rows']
check('YES row with matching record = OK', R['US-1|1']['state'] == 'OK')
check('old word APPROVED is read as YES and checked', 'US-2|2' in R)
check('K3 acres "about 50" does not crash: CHANGED with the reason', R['US-2|2']['state'] == 'CHANGED' and 'not a number' in R['US-2|2']['why'], R['US-2|2'])
check('NOT SURE rows are checked too; fp acres given as a string work', R['US-3|3']['state'] == 'OK', R['US-3|3'])
check("K2 a record_id that is not a number is UNREAD (not VANISHED)", R['US-4|bpad:Bullock Pen']['state'] == 'UNREAD' and 'OBJECTID' in R['US-4|bpad:Bullock Pen']['why'])
check('PROPOSED rows are not checked without --all', 'US-5|9' not in R)
check('K3 batches follow maxRecordCount 2 (3 ids -> 2 queries)', sum('objectIds=' in h and '/x/' in h for h in hits) == 2, [h[:80] for h in hits if 'objectIds' in h])
check('K3 exceededTransferLimit makes the layer UNREAD', R['US-6|1']['state'] == 'UNREAD' and 'exceededTransferLimit' in R['US-6|1']['why'])
check('green is false while a YES row is UNREAD', J['green'] is False and J['approved_unread'] == 2)
check('K1 no cache files were written although KPC_MANNERS_CACHE(_ALL) were set', not os.path.exists(cache) or not os.listdir(cache))
check('K1 each layer has its real read time', all(v.get('read_at') for v in J['layers'].values()))
P = list(csv.DictReader(open(pp)))
check("K4 a person's earlier answer is carried over (normalised to the shared word)", any(p['ref'] == 'US-9' and p['answer'] == 'YES' and p['answered_by'] == 'Brandon' for p in P), P)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); import kpc_answer_words as AW  # noqa: E402
check("Q4 KZ4CP is Brandon's sign-off (Brandon, relayed by Super 6:52 PM CST Nov 3)", 'kz4cp' in AW.persons(None) and AW.signed_off('KZ4CP', '2026-11-01', AW.persons(None)))
print('ALL PASS' if not bad else f'{len(bad)} FAILED: {bad}')
sys.exit(1 if bad else 0)
