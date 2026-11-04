#!/usr/bin/env python3
"""KPC ANSWER SHEET NIGHTLY CHECK (Mapping, Nov 3 2026; PROTOTYPE, for KPC-Data .github/scripts/ once a person approves).

Reads data/answer-sheet/<XX>.csv (READ ONLY: this script never edits the sheet) and asks each row's OFFICIAL layer, politely,
whether the record is still there and still the same place:
  OK        the record id answers with the fp name (and acres within 10% / 20 ac when both are known)
  CHANGED   the id answers, but the name or the acres are no longer the fp        -> the builders treat the row as CAN'T TELL
  REFOUND   the id is gone, but exactly ONE record has the row's agency unit id, or the fp name + acres (the same fingerprint rule
            data/us-key/overrides.json 'fp' uses, kpc_us_key.py lines 1034-1041)     -> a proposal to update record_id
  VANISHED  the id is gone and nothing unique re-finds it                            -> CAN'T TELL, never a guess
  UNREAD    the layer could not be read tonight (robots, 403 after one retry, deferred slow host, error)
Writes data/answer-sheet/check/<XX>.json  {built, green, sheet, counts, layers, rows:{"ref|key_id": {...}}} for the builders, and
data/answer-sheet/check/<XX>-proposals.csv (unit ids found, fp acres filled, new record ids) for a person / Super to batch.
green = the run finished and every APPROVED row was read (UNREAD = 0). Builders give sheet rows hand-join protection only while
green is true and the file is under 36 h old.

Manners: kpc_manners (robots.txt, 1 request / 2 s / host or the host's Crawl-delay, honest KPC User-Agent, a 403 retried once
then left for a person). Reads are batched (up to 100 ids a query, attributes only, returnGeometry=false).
Nov 3 remake after Quality's grade (K1-K4, shared words):
  K1  no disk cache, ever, in this checker (a cached 200 could hide a vanished record for 7 days); each row carries its real read time.
  K2  a record_id that is not a number is not this layer's OBJECTID: UNREAD with that reason (never VANISHED / REFOUND).
  K3  a non-number acres value never crashes the run (that row is CHANGED: 'acres not a number'); batches follow the layer's
      maxRecordCount, and a query that says exceededTransferLimit makes the layer UNREAD instead of dropping ids silently.
  K4  <XX>-proposals.csv has an 'answer' column (YES / NO / NOT SURE) and 'answered_by'; answers already written there are carried
      over to the next night for the same proposal, never wiped. Decisions still go to an inbox batch for Quality to apply.
  Status words are the shared list (kpc_answer_words.py): YES rows (old word APPROVED) and NOT SURE / PIN / FIXED rows are checked;
  PROPOSED and NO rows only with --all. green = finished, whole sheet, and every YES row read.
Use:  python3 kpc_answer_sheet_check.py --sheet data/answer-sheet/US.csv --out data/answer-sheet/check/US.json [--all] [--limit-layers N]
"""
import argparse, csv, json, os, re, sys, time, unicodedata, urllib.parse, datetime, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_manners as KM   # noqa: E402
import kpc_answer_words as AW   # noqa: E402
KM.CACHE_DIR = ''   # K1: this checker never reads or writes the disk cache, whatever KPC_MANNERS_CACHE says

UNIT_RE = re.compile(r'^(unit_?id|unit_?code|unit_?nbr|unit_?no|unitcode|site_?id|siteid|prop(erty)?_?id|parcel_?id|park_?id|parkid|area_?id|'
                     r'prop_?code|mgmt_?unit_?id|orgcode|org_?code|cmpt_?id|tract_?id|wma_?id|sp_?id|fac_?id|gis_?id|unit_?cd|areaid)$', re.I)
NAME_RE = re.compile(r'^(unit_?nm|name|prop(erty)?_?name|site_?name|park_?name|area_?name|unit_?name|mgmt_?name|loc_?nm|orgname|label)$', re.I)
ACRES_RE = re.compile(r'^(gis_?acres|acres|acreage|calc_?acres|total_?acres|area_?ac(res)?|deeded_?acres|prop_?acres|gisacres|sum_acres|acres_gis)$', re.I)

def nf(s): return unicodedata.normalize('NFC', str(s or '')).casefold().strip()

def get_json(M, url, stat):
    st, hd, body, _ = M.get(url, accept='application/json')
    if st != 200: stat[str(st)] = stat.get(str(st), 0) + 1; return None, str(st)
    try:
        j = json.loads(body.decode('utf-8', 'replace'))
    except ValueError: return None, 'not json'
    if isinstance(j, dict) and j.get('error'): return None, 'arcgis error ' + str(j['error'].get('code'))
    return j, 'ok'

def num(v):
    """K3: a number or None (never raises)."""
    try: return None if v in (None, '') else float(str(v).replace(',', ''))
    except (TypeError, ValueError): return None

def fp_of(r):
    fp = AW.fp_cell(r.get('fp'))
    return (fp[0] or None, fp[1]) if fp else (None, None)

def close(la, fa):
    la, fa = num(la), num(fa)
    return fa in (None, 0) or la is None or abs(la - fa) <= max(20, .1 * fa)

def esc(v): return "'" + str(v).replace("'", "''") + "'"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheet', required=True); ap.add_argument('--out', required=True); ap.add_argument('--proposals')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--limit-layers', type=int, default=0); ap.add_argument('--only-refs', default='')
    a = ap.parse_args()
    want = None if a.all else {'join', 'not sure'}   # YES rows + NOT SURE / PIN / FIXED / unknown words
    only = {r.strip() for r in a.only_refs.split(',') if r.strip()}
    rows = [r for r in csv.DictReader(open(a.sheet, encoding='utf-8'))
            if (want is None or AW.use(r.get('status')) in want) and (not only or r['ref'] in only)]
    M = KM.Manners('KPC answer sheet check (reads official map records by id, attributes only)')
    by_layer = collections.OrderedDict()
    for r in rows: by_layer.setdefault((r.get('source_url') or '').rstrip('/'), []).append(r)
    if a.limit_layers: by_layer = collections.OrderedDict(list(by_layer.items())[:a.limit_layers])
    out_rows, layers, props, stat = {}, {}, [], {}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    for url, rs in by_layer.items():
        L = layers[url] = {'rows': len(rs), 'read_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}   # K1: real read time
        info, why = get_json(M, url + '?f=json', stat) if url else (None, 'no source_url')
        if info is None:
            L['read'] = why
            for r in rs: out_rows[f"{r['ref']}|{r['key_id']}"] = {'state': 'UNREAD', 'why': why, 'read_at': now}
            continue
        fields = [f.get('name') for f in info.get('fields') or [] if f.get('name')]
        oidf = info.get('objectIdField') or next((f.get('name') for f in info.get('fields') or [] if f.get('type') == 'esriFieldTypeOID'), 'OBJECTID')
        unitf = next((f for f in fields if UNIT_RE.match(f)), None)
        acf = next((f for f in fields if ACRES_RE.match(f)), None)
        strf = [f.get('name') for f in info.get('fields') or [] if f.get('type') == 'esriFieldTypeString']
        L.update({'objectIdField': oidf, 'unit_id_field': unitf, 'acres_field': acf, 'read': 'ok'})
        ids = sorted({r['record_id'] for r in rs if re.fullmatch(r'\d+', r.get('record_id') or '')}, key=int)
        per = max(1, min(100, int(num(info.get('maxRecordCount')) or 100)))   # K3: never ask for more than the layer hands back
        live = {}
        for i in range(0, len(ids), per):
            q = url + '/query?' + urllib.parse.urlencode({'objectIds': ','.join(ids[i:i + per]), 'outFields': '*', 'returnGeometry': 'false', 'f': 'json'})
            j, why = get_json(M, q, stat)
            if j is None: L['read'] = 'query ' + why; break
            if j.get('exceededTransferLimit'): L['read'] = 'query cut short (exceededTransferLimit): ids would be missed'; break
            for ft in j.get('features') or []:
                at = ft.get('attributes') or {}
                if at.get(oidf) is not None: live[str(at[oidf])] = at
        if L['read'] != 'ok':
            for r in rs: out_rows[f"{r['ref']}|{r['key_id']}"] = {'state': 'UNREAD', 'why': L['read'], 'read_at': now}
            continue
        # which string field carries the names (the one that equals the fp name most often)
        votes = collections.Counter()
        for r in rs:
            fn = fp_of(r)[0]
            at = live.get(r.get('record_id') or '')
            if at and fn:
                for f in strf:
                    if nf(at.get(f)) == nf(fn): votes[f] += 1
        namef = votes.most_common(1)[0][0] if votes else next((f for f in strf if NAME_RE.match(f)), None)   # no record answered: the layer's name field
        L['name_field'] = namef
        for r in rs:
            k = f"{r['ref']}|{r['key_id']}"
            fn, fa = fp_of(r)
            at = live.get(r.get('record_id') or '')
            res = {'read_at': L.get('read_at', now), 'record_id': r.get('record_id')}
            if not re.fullmatch(r'\d+', r.get('record_id') or ''):   # K2
                out_rows[k] = {**res, 'state': 'UNREAD', 'why': "record_id is not this layer's OBJECTID (store the real OBJECTID in the sheet)"}; continue
            if at is not None:
                ln = next((at.get(f) for f in ([namef] if namef else []) + strf if nf(at.get(f)) == nf(fn)), None) if fn else None
                la = at.get(acf) if acf else None
                res.update({'live_name': ln if ln is not None else (at.get(namef) if namef else None), 'live_acres': la})
                ok_name = bool(fn) and ln is not None
                ok_ac = close(la, fa) and (la in (None, '') or num(la) is not None)
                res['state'] = 'OK' if ok_name and ok_ac else 'CHANGED'
                if not ok_name: res['why'] = 'the record answers with another name'
                elif num(la) is None: res['why'] = f'acres not a number ({str(la)[:20]})'
                elif not ok_ac: res['why'] = f'acres now {la}, fp {fa}'
                if unitf and at.get(unitf) not in (None, '') and str(at.get(unitf)) != (r.get('unit_id') or ''):
                    res['unit_id'] = str(at[unitf])
                    props.append([r['ref'], r['key_id'], r['record_id'], 'unit_id', r.get('unit_id', ''), str(at[unitf]), f'{unitf} on the live record'])
                    if not r.get('unit_id_field'): props.append([r['ref'], r['key_id'], r['record_id'], 'unit_id_field', '', unitf, 'layer field'])
                if res['state'] == 'OK' and fa in (None, 0) and num(la) is not None:
                    props.append([r['ref'], r['key_id'], r['record_id'], 'fp', r.get('fp', ''), json.dumps([fn, round(num(la))]), f'acres from {acf}'])
            else:
                hit = []
                if r.get('unit_id') and (r.get('unit_id_field') or unitf):
                    uf = r.get('unit_id_field') or unitf
                    j, _ = get_json(M, url + '/query?' + urllib.parse.urlencode({'where': f"{uf}={esc(r['unit_id'])}", 'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}), stat)
                    hit = (j or {}).get('features') or []
                    res['refind'] = f'unit id {uf}={r["unit_id"]}'
                elif fn and namef:
                    j, _ = get_json(M, url + '/query?' + urllib.parse.urlencode({'where': f"{namef}={esc(fn)}", 'outFields': '*', 'returnGeometry': 'false', 'f': 'json'}), stat)
                    hit = [h for h in (j or {}).get('features') or [] if fa in (None, 0) or not acf or (num(h['attributes'].get(acf)) is not None
                           and close(h['attributes'].get(acf), fa))]
                    if (j or {}).get('exceededTransferLimit'): hit = []   # K3: a cut-off answer is never 'exactly one'
                    res['refind_answers'] = len(hit)
                    if fa in (None, 0): hit = hit if len(hit) == 1 else []   # name alone (acres unknown): only a single answer counts
                    res['refind'] = f'fp {namef}={fn!r} + acres'
                if len(hit) == 1:
                    nid = str(hit[0]['attributes'].get(oidf))
                    res.update({'state': 'REFOUND', 'new_record_id': nid, 'why': 'record id gone; one record re-found'})
                    props.append([r['ref'], r['key_id'], r['record_id'], 'record_id', r['record_id'], nid, res['refind'] + ' (key_id must follow: prefix + new id)'])
                else:
                    res.update({'state': 'VANISHED', 'why': f"record id gone; re-find gave {res.get('refind_answers', len(hit))} answers (needs exactly 1)"})
            out_rows[k] = res
    counts = dict(collections.Counter(v['state'] for v in out_rows.values()))
    appr_unread = sum(1 for r in rows if AW.use(r.get('status')) == 'join' and out_rows.get(f"{r['ref']}|{r['key_id']}", {}).get('state') == 'UNREAD')
    res = {'built': now, 'green': appr_unread == 0 and not a.limit_layers and not only, 'sheet': a.sheet, 'checked_status': sorted(want) if want else 'all',
           'counts': counts, 'approved_unread': appr_unread, 'requests': {k: v for k, v in M.stat.items() if k != 'for_person_urls'},
           'for_person': [list(x) for x in M.for_person], 'cache': 'off (K1)', 'layers': layers, 'rows': out_rows}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    pp = a.proposals or re.sub(r'\.json$', '', a.out) + '-proposals.csv'
    # K4: carry a person's answers over: same ref + key_id + column + proposed value keeps its answer / answered_by
    old = {}
    try:
        for o in csv.DictReader(open(pp, encoding='utf-8')):
            if (o.get('answer') or '').strip():
                old[(o.get('ref'), o.get('key_id'), o.get('column'), o.get('proposed'))] = (AW.word(o['answer'])[0], o.get('answered_by') or '')
    except FileNotFoundError: pass
    kept = 0
    with open(pp, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['ref', 'key_id', 'record_id', 'column', 'old', 'proposed', 'why', 'answer', 'answered_by'])
        seen = set()
        for p_ in props:
            ans = old.get((p_[0], p_[1], p_[3], p_[5]), ('', '')); kept += bool(ans[0]); seen.add((p_[0], p_[1], p_[3], p_[5]))
            w.writerow(p_ + list(ans))
        for k_, ans in old.items():   # an answered proposal that did not come up tonight is kept too (never wiped)
            if k_ not in seen: w.writerow([k_[0], k_[1], '', k_[2], '', k_[3], 'answered earlier; not proposed tonight', ans[0], ans[1]]); kept += 1
    res['answers_carried'] = kept
    json.dump(res, open(a.out, 'w', encoding='utf-8'), indent=1, sort_keys=True, ensure_ascii=False)

    print(f"::notice title=Answer sheet check::{a.sheet}: {len(out_rows)} rows on {len(layers)} layers: {counts}; green={res['green']}; requests {res['requests']}")

if __name__ == '__main__':
    main()
