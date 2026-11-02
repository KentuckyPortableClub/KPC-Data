"""Load the Mapping agent's retry list (world_keys/retry/retry-servers-down-nov1.csv) into registry/retry.json.

Every row is tagged 'retry from GitHub network': try the SAME honest request once from another network (the nightly GitHub
runner). Never get around a 403, robot check, captcha, sign-in or token: a 403 again means a person looks in a normal browser.
Spain's MITECO enp.zip (robot check) is a person-downloads item, never fetched by the engine.

  python3 registry/import_retry.py /workspace/world_keys/retry/retry-servers-down-nov1.csv
"""
import csv, datetime, hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
TAG = 'retry from GitHub network'


def how(r):
    t = ' '.join(r.values()).lower()
    if re.search(r'\b403\b', t): return 'blocked 403', 'retry the same honest request once; a 403 again -> a person in a normal browser. Never bypass.'
    if re.search(r'token[- ]based|token required|token api|token-only', t): return 'needs sign-in', 'do not retry: token-only API = "needs sign-in" (waiting on the user: WAITING-ON-USER-OK #2)'
    if 'no service endpoint' in t or 'no open polygon' in t: return 'person', 'a person looks in a browser (no open service found from the box)'
    if 'expired certificate' in t: return 'retry', 'retry once; never click through an expired certificate (TLS stays verified)'
    return 'retry', 'retry the same honest request once from another network (box egress pattern: 500 / TLS EOF / timeout)'


def run(path, out=HERE / 'retry.json'):
    raw = open(path, 'rb').read()
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    items = []
    for n, r in enumerate(rows, start=2):
        kind, what = how(r)
        last = [k for k in r if k and k.lower().startswith('nov1')]
        items.append({'id': f"RETRY-{r.get('Code')}", 'cc': r.get('Code'), 'country': r.get('Country'), 'pota_parks': r.get('POTA parks (from list)') or None,
                      'agency': r.get('Agency'), 'address': r.get('Address to retry'), 'what_happened': r.get('What happened'),
                      'likely_cause': r.get('Likely cause'), 'what_to_do': r.get('What to do on retry'),
                      'last_try': ' | '.join(r[k] for k in last if r.get(k)), 'tag': TAG, 'kind': kind, 'engine_action': what,
                      'csv_row': n, 'automatic': kind == 'retry' or kind == 'blocked 403'})
    items.append({'id': 'RETRY-ES-enp', 'cc': 'ES', 'country': 'Spain', 'pota_parks': '~660 still open', 'agency': 'MITECO (Banco de Datos de la Naturaleza)',
                  'address': 'MITECO national protected-areas download enp.zip (59.6 MB); see world_keys/handback5/README-mapping-nov1e.md',
                  'what_happened': 'robot check on the download', 'tag': TAG, 'kind': 'person downloads',
                  'engine_action': 'a person downloads it in a normal browser and drops it in the cache; the engine never fetches it (no robot-check bypass)',
                  'automatic': False, 'source': 'round5_note.txt section 1 + WAITING-ON-USER-OK #11 (not a CSV row)'})
    d = {'about': f"Retry list (round 5). Tag '{TAG}': the same honest request, once, from the nightly GitHub runner. Never bypass a 403, "
                  "robot check, captcha, sign-in or token. 'automatic': false rows are for a person.",
         'loaded': datetime.datetime.now().isoformat(timespec='seconds'), 'csv': str(path), 'csv_sha256': hashlib.sha256(raw).hexdigest(),
         'csv_rows': len(rows), 'items': items}
    json.dump(d, open(out, 'w'), indent=1, ensure_ascii=False)
    return d


if __name__ == '__main__':
    d = run(sys.argv[1] if len(sys.argv) > 1 else '/workspace/world_keys/retry/retry-servers-down-nov1.csv')
    from collections import Counter
    print(len(d['items']), 'items;', dict(Counter(i['kind'] for i in d['items'])))
