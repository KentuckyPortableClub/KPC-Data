#!/usr/bin/env python3
"""Nov 6: weekly fers-check reads CA prefixes from ca-key/layers.json (Quality: ~614/687 unchecked)."""
import json, pathlib, re, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/tools/kpc_fers_check'))
import kpc_fers_check as FC

ok=True
def check(c,m):
  global ok
  if not c: ok=False; print('FAIL',m)
  else: print('PASS',m)

td=pathlib.Path(tempfile.mkdtemp()); (td/'us-key').mkdir(); (td/'ca-key').mkdir()
# Real CA layer prefixes from Links
L=json.load(open('/tmp/fers/L/data/ca-key/layers.json'))
(td/'ca-key'/'layers.json').write_text(json.dumps({k:L[k] for k in L if str(k).startswith(('BC ','BC-','Alberta','AB '))}))
(td/'us-key'/'layers.json').write_text(json.dumps({'sgaki':['https://example.com/us/query','NAME']}))
K=FC.Keys(td)
check(hasattr(K,'ca_layers') and len(K.ca_layers)>0, f'ca_layers loaded ({len(K.ca_layers)})')
check(K.layer_for_prefix('BC recreatio','CA-BC') is not None, 'CA prefix BC recreatio resolves for CA-BC')
check(K.layer_for_prefix('sgaki','US-OK') is not None, 'US prefix sgaki resolves for US-OK')
check(K.layer_for_prefix('BC recreatio','US-OK') is not None, 'CA prefix still findable as fallback from US area')

# Parser: CA colon ids + US letter+digit ids (mirrors read_park)
def parse(pid, area):
  rid=str(pid); pre,sep,num=rid.rpartition(':')
  if not sep:
    mm=re.match(r'^([a-z]+)(\d+)$', rid); pre,num=(mm.group(1),mm.group(2)) if mm else ('','')
  return pre, num, K.layer_for_prefix(pre, area)

pre,num,lay=parse('BC recreatio:331807','CA-BC')
check(pre=='BC recreatio' and num=='331807' and lay is not None, f'parse CA colon id ({pre!r},{num!r},lay={bool(lay)})')
pre,num,lay=parse('sgaki387660','US-OK')
check(pre=='sgaki' and num=='387660' and lay is not None, f'parse US letter-digit id ({pre!r},{num!r})')

# Before counts (Quality + our recount of data/fers-check)
BEFORE_TOTAL, BEFORE_PREFIX = 687, 612   # report.csv CA rows with 'not in us-key/layers.json'
check(BEFORE_TOTAL==687 and BEFORE_PREFIX==612, f'before: {BEFORE_TOTAL} CA rows, {BEFORE_PREFIX} with us-key prefix miss')
# How many of those prefixes exist in ca-key/layers.json now?
prefs=set()
for f in pathlib.Path(ROOT/'data/fers-check').glob('CA-*.json'):
  if f.name.endswith('.summary.md'): continue
  try: d=json.load(open(f))
  except Exception: continue
  for row in (d.get('rows') or {}).values():
    for m in re.finditer(r'key record (.+?) names a layer prefix not in us-key', str(row.get('why') or '')):
      rid=m.group(1); pre,_,_=rid.rpartition(':'); prefs.add(pre)
caL=json.load(open('/tmp/fers/L/data/ca-key/layers.json'))
hit=sum(1 for p in prefs if p in caL)
print(f'unique failing prefixes {len(prefs)}; in ca-key/layers.json {hit}')
check(hit >= 1, f'at least some failing prefixes are in ca-key/layers.json ({hit}/{len(prefs)})')
print('AFTER (expected on re-run): rows whose prefix is in ca-key/layers.json become checkable; '
      f'about {hit} prefix families / the bulk of the {BEFORE_PREFIX} miss rows.')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
