#!/usr/bin/env python3
"""22 Nov 2026 (owner: "We can read arcgis"): the store KEEPER may read services*.arcgis.com and apps.fs.usda.gov (his 15 Nov
ruling for the keeper), so the keeper's agency-lists job can read the agency lists that sit there. Only inside the keeper's own
jobs: KPC_KEEPER_HOST_RULES=owner-2026-11-15, which KPC-Store sets and NO KPC-Data workflow sets. Every KPC-Data bot keeps the
saved-copies-only rule; the never-contact hosts stay never-contact in every case; a host added by KPC_SAVED_ONLY_HOSTS stays
saved-copies-only. Offline. Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import importlib.util, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def load():
    spec = importlib.util.spec_from_file_location('kpc_host_rules_t', ROOT / '.github/scripts/kpc_host_rules.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


H = load()
ARC = 'https://services3.arcgis.com/abc/arcgis/rest/services/Parks/FeatureServer/0/query'
FS = 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_Wilderness_01/MapServer/0'
os.environ.pop('KPC_KEEPER_HOST_RULES', None); os.environ.pop('KPC_SAVED_ONLY_HOSTS', None)
check('a KPC-Data bot: services*.arcgis.com stays saved copies only', not H.host_ok(ARC)[0])
check('a KPC-Data bot: apps.fs.usda.gov stays saved copies only', not H.host_ok(FS)[0])
os.environ['KPC_KEEPER_HOST_RULES'] = 'yes'
check('a wrong value of the setting changes nothing', not H.host_ok(ARC)[0])
os.environ['KPC_KEEPER_HOST_RULES'] = 'owner-2026-11-15'
check('inside the keeper: services*.arcgis.com may be read (robots.txt still decides, in kpc_manners)', H.host_ok(ARC)[0])
check('inside the keeper: services1.arcgis.com (on the default saved-only list) may be read', H.host_ok('https://services1.arcgis.com/x/arcgis/rest/services/A/FeatureServer/0')[0])
check('inside the keeper: apps.fs.usda.gov may be read', H.host_ok(FS)[0])
check('inside the keeper: the Grant County never-contact server stays never-contact',
      not H.host_ok('https://services.arcgis.com/33TOOklri9xpic7U/arcgis/rest/services/x/FeatureServer/0')[0])
check('inside the keeper: ncnhde.natureserve.org stays never-contact', not H.host_ok('https://ncnhde.natureserve.org/x')[0])
os.environ['KPC_SAVED_ONLY_HOSTS'] = 'services3.arcgis.com'
check('inside the keeper: a host added by KPC_SAVED_ONLY_HOSTS stays saved copies only', not H.host_ok(ARC)[0])
os.environ.pop('KPC_KEEPER_HOST_RULES', None); os.environ.pop('KPC_SAVED_ONLY_HOSTS', None)
setters = [f.name for f in (ROOT / '.github' / 'workflows').glob('*.yml') if re.search(r'KPC_KEEPER_HOST_RULES', f.read_text(encoding='utf-8'))]
check(f'no KPC-Data workflow sets the keeper setting ({setters})', not setters)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
