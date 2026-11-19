"""Run #278's own preserve_apart() (cut from the branch file, as its test does) on the REAL saved shapes, the REAL joined rows of
run 44528656941 (rules 7c6e01e1bc2b = the PR's base) and POTA's REAL pins, for the 13 scope states."""
import json, gzip, re, sys, pathlib
ROOT = pathlib.Path('/home/claude/repos/KPC-Links'); SCR = ROOT / '.github' / 'scripts'
sys.path.insert(0, str(SCR)); import kpc_key_rules as KR
src = (SCR / 'kpc_us_key.py').read_text(encoding='utf-8')
m = re.search(r"^PRESERVE_HIT = \[\].*?^def preserve_apart\(.*?(?=^NPS_CODE_HIT = \[\])", src, re.S | re.M)
geo = ''.join(re.search(rf"^def {fn}\(.*?(?=^def |\Z)", src, re.S | re.M).group(0) for fn in ('rings', 'in_ring', 'inside'))
ns = {'KR': KR, '_oid': lambda a: str(a['OBJECTID']), '_kr': lambda name: True, 'P_ALL': {}}
exec(geo, ns); exec(m.group(0), ns)
fcd = '/home/claude/work/to/key-quality/2026-11-19/factcheck-run-44528656941'
for st in 'AK AL CA CO FL ID KS LA NM NV OR TX WV'.split():
    recs = json.load(gzip.open(f'/home/claude/work/cache/US-{st}.json.gz'))['recs']
    for a in recs: a['_g'] = {'rings': a.get('_r') or []}
    key = json.load(open(f'/home/claude/work/newkeys/US-{st}.json'))['parks']
    fc = json.load(gzip.open(f'{fcd}/factcheck-US-{st}.json.gz'))['parks']
    P = {r: ['', '', '', '', '', (e.get('pin') or [0, 0])[0], (e.get('pin') or [0, 0])[1]] for r, e in fc.items()}
    parks = {r: {'n': p.get('n'), 'm': [list(x) for x in p.get('m') or []], 'c': [list(x) for x in p.get('c') or []]} for r, p in key.items()}
    nps = sum(1 for a in recs if (KR.nps_record_code(a) or str(a.get('Mang_Name') or '') == 'NPS'))
    npre = sum(1 for a in recs if (KR.nps_record_code(a) or str(a.get('Mang_Name') or '') == 'NPS') and re.search(r'\bpreserve\b', str(a.get('Unit_Nm') or a.get('Loc_Nm') or ''), re.I))
    ns['PRESERVE_HIT'].clear(); ns['PRESERVE_ASK'].clear()
    n = ns['preserve_apart'](st, parks, recs, on=True, P=P)
    hit = [f"{h[1]} {h[3]} ({h[2]})" for h in ns['PRESERVE_HIT']]; ask = [f"{h[1]} {h[3]} ({h[2]})" for h in ns['PRESERVE_ASK']]
    print(f"{st}: Park Service records {nps}, named Preserve {npre} | moved {n}: {hit or '-'} | kept as a person's question: {ask or '-'}")
