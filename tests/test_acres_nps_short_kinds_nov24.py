#!/usr/bin/env python3
"""24 Nov 2026 (owner: sizes from each agency's yearly list): the acreage bot reads the Park Service acreage report's short kinds
(NM, NHS, NHP, NMEM, NMP, NB, NS, NL, NSR, WILD RVR, N PRESERVE, NP & PRES) so its rows meet POTA's full names. No network."""
import pathlib, socket, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_acres'))
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('no network in tests'))
import kpc_acres as A  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


same = lambda a, b: A.name_kind(a)[:2] == A.name_kind(b)[:2]
check('NM = National Monument', same('INVENTED BUTTE NM', 'Invented Butte National Monument'))
check('NHS = National Historic Site', same('INVENTED HOUSE NHS', 'Invented House National Historic Site'))
check('NHP = National Historical Park', same('INVENTED FORGE NHP', 'Invented Forge National Historical Park'))
check('NMEM = National Memorial', same('INVENTED NMEM', 'Invented National Memorial'))
check('NMP / NB = battlefield', same('INVENTED RIDGE NMP', 'Invented Ridge National Military Park') and same('INVENTED CREEK NB', 'Invented Creek National Battlefield'))
check('NS / NL = shore', same('INVENTED NS', 'Invented National Seashore') and same('INVENTED ISLANDS NL', 'Invented Islands National Lakeshore'))
check('NSR / WILD RVR = river', same('INVENTED NSR', 'Invented National Scenic River') and same('INVENTED WILD RVR', 'Invented National Wild and Scenic River'))
check('N PRESERVE / NP & PRES / National Park and Preserve', same('INVENTED N PRESERVE', 'Invented National Preserve')
      and same('INVENTED NP & PRES', 'Invented National Park and Preserve'))
check('a monument is not a historic site', not same('INVENTED NM', 'Invented National Historic Site'))
check('a state park short form is unchanged', A.name_kind('Invented SP')[0] == 'state_park')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
