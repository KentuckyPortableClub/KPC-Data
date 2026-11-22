#!/usr/bin/env python3
"""22 Nov 2026 (owner): the map audit's bot list, data/waiting/questions/map-audit-auto.json, must exist and be readable before
any 2-fer run starts. Missing or unreadable = the 2-fer gate starts nothing and every area says why; the chain plan (gate on)
holds every area, the world pass-through too. An empty list (rows: []) is fine. Offline, invented areas only.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import importlib.util, json, os, pathlib, sys, tempfile

S = pathlib.Path(__file__).resolve().parents[1] / '.github' / 'scripts'
sys.path.insert(0, str(S))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def mod(name):
    spec = importlib.util.spec_from_file_location(name, S / f'{name}.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G = mod('kpc_fers_gate')
P = mod('kpc_fers_chain_plan')


def w(p, o):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o))


def gate_case(auto):
    """auto: None = no bot list; 'broken' = not JSON; a dict = written as is. -> fers-ready.json areas"""
    with tempfile.TemporaryDirectory() as t:
        here = os.getcwd(); os.chdir(t)
        try:
            for a in ('US-ZZ', 'US-YY'): w(f'data/parkinfo/{a}.json', {})
            w('data/status/audited.json', {a: {'built': '2026-11-21', 'rows': 1, 'flagged': 1} for a in ('US-ZZ', 'US-YY', 'US-KY')})
            w('data/waiting/questions/map-audit.json', {'questions': []})
            if auto == 'broken':
                pathlib.Path('data/waiting/questions/map-audit-auto.json').write_text('{not json')
            elif auto is not None:
                w('data/waiting/questions/map-audit-auto.json', auto)
            calls = []
            G.gh = lambda *a: (calls.append(a), (1, ''))[1]
            G.subprocess.run = lambda *a, **k: None
            G.gate()
            return json.load(open('data/status/fers-ready.json'))['areas'], calls
        finally:
            os.chdir(here)


st, calls = gate_case(None)
check('gate: no bot list -> no area is ready, each says "stopped" and why', all(v['status'].startswith('stopped:') and 'missing' in v['status'] for v in st.values()))
check('gate: no bot list -> no 2-fer run is started', not any('dispatches' in ' '.join(map(str, c)) for c in calls))
st, _ = gate_case('broken')
check('gate: an unreadable bot list stops too, saying it cannot be read', all(v['status'].startswith('stopped:') and 'cannot be read' in v['status'] for v in st.values()))
st, _ = gate_case({'rows': 'x'})
check('gate: a bot list that is not a list of rows stops too', all(v['status'].startswith('stopped:') for v in st.values()))
st, _ = gate_case({'rows': []})
check('gate: an empty bot list is fine (the clean areas are ready)', st['US-ZZ']['status'].startswith('ready for 2-fers'))

with tempfile.TemporaryDirectory() as t:
    D = pathlib.Path(t)
    w(D / 'data/status/audited.json', {a: {'built': '2026-11-21', 'rows': 0} for v in P.R.values() for a in v.split()})
    w(D / 'data/waiting/questions/map-audit.json', {'questions': []})
    passed = []
    bad = P.audit_clean(D, passed)
    allareas = {a for v in P.R.values() for a in v.split()}
    check('chain plan: no bot list -> every area (world too) is held with the reason', set(bad) == allareas
          and all(x.startswith('stopped:') and 'missing' in x for x in bad.values()) and not passed)
    (D / 'data/waiting/questions/map-audit-auto.json').write_text('{broken')
    bad = P.audit_clean(D, [])
    check('chain plan: an unreadable bot list holds every area', set(bad) == allareas and all('cannot be read' in x for x in bad.values()))
    w(D / 'data/waiting/questions/map-audit-auto.json', {'rows': []})
    bad = P.audit_clean(D, [])
    check('chain plan: an empty bot list with every area audited holds none of them', not any(x.startswith('stopped:') for x in bad.values()))

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
