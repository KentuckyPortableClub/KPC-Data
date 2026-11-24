#!/usr/bin/env python3
"""23 Nov 2026 (owner 'Yes', audit 4 items 3.1 and 3.2): the PC upload merge never lets a PC read of POTA's front-page link
replace the park's OWN page on file, and an open question of an area the pack does not carry stays in the questions file.
Invented parks. Prints PASS / FAIL, ends ALL PASS or SOME FAILED."""
import gzip, json, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
import kpc_pc_upload as U  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def f(kind, read, own=None, name='Invented Ridge State Park'):
    x = {'page': {'kind': kind, 'read': read}, 'name': {'heading': name}}
    if own: x['own_page'] = {'is': own}
    return x


check("a newer PC read of the front page never replaces the park's own page on file",
      not U.better_read(f('html', '2026-11-20', 'own'), f('html', '2026-11-23', 'agency-home')))
check("a newer read of the park's own page still replaces an older own page", U.better_read(f('html', '2026-11-20', 'own'), f('html', '2026-11-23', 'own')))
check('an own page replaces a front-page read', U.better_read(f('html', '2026-11-23', 'agency-home'), f('html', '2026-11-20', 'own')))
U_ = 'https://parks.zz.invented.gov/mud-lake'
sure_old = dict(f('html', '2026-11-20', 'own'), found={'level': 'sure', 'url': U_})
unsure_new = dict(f('html', '2026-11-20', 'shared'), found={'level': 'unsure', 'url': U_ + '/'})
check("the finder's downgrade (sure -> unsure) replaces the old sure own page on file", U.better_read(sure_old, unsure_new))
check('an empty read marked unsure never replaces a good sure find', not U.better_read(sure_old, dict(f('resting', '2026-11-21', 'shared'), found={'level': 'unsure', 'url': U_})))
check('an older read marked unsure never does', not U.better_read(sure_old, dict(f('html', '2026-11-10', 'shared'), found={'level': 'unsure', 'url': U_})))
check('another page marked unsure never does', not U.better_read(sure_old, dict(f('html', '2026-11-21', 'shared'), found={'level': 'unsure', 'url': U_ + '-other'})))
check('no page at all never does', not U.better_read(sure_old, {'found': {'level': 'unsure', 'url': U_}}))
with tempfile.TemporaryDirectory() as td:
    qf = pathlib.Path(td) / 'q.json.gz'
    old = {'rows': {'US-9701': {'ref': 'US-9701', 'area': 'US-YY', 'level': 'unsure', 'question': 'Is this ...?'}}}
    qf.write_bytes(gzip.compress(json.dumps(old).encode()))
    P = {'made': '2026-11-23-1900', 'pages': {'US-ZZ': {'parks': {'US-9801': {'area': 'US-ZZ', 'pota': {'name': 'Invented Lake Park'},
         'found': {'level': 'unsure', 'url': 'https://parks.zz.invented.gov/x', 'how': 'sister', 'for': 'no link', 'date': '2026-11-23'}}}}}}
    U.write_found(P, None, str(qf))
    rows = json.loads(gzip.decompress(qf.read_bytes()))['rows']
    check('an open question of an area the pack does not carry stays open', 'US-9701' in rows)
    check("the pack's own unsure find is asked too", 'US-9801' in rows)
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
