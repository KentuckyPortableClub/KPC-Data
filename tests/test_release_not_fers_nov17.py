#!/usr/bin/env python3
"""Nov 17: the 2-fer 'never replace live with 0 pairs' guard must only act on 2-fer files (data/fers/).
Any file named US-XX.json (camp state, campinfo, truth, docs) was refused as a 2-fer with 0 pairs, so a by-hand release of
those never moved. Offline: synthetic data only, nothing is fetched or written."""
import importlib.util, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


tmp = pathlib.Path(tempfile.mkdtemp(prefix='kpc-wr-fers-'))
os.environ['DATA'] = str(tmp); os.environ['LINKS'] = str(tmp / 'nolinks')
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
spec = importlib.util.spec_from_file_location('wr_fers_guard', HERE / '.github/scripts/kpc_waiting_room.py')
WR = importlib.util.module_from_spec(spec); spec.loader.exec_module(WR)

live2 = {'spots': [{'status': 'candidate'}, {'status': 'candidate'}]}
none2 = {'spots': []}
for rel in ('data/campstate/US-CA.json', 'data/campinfo/US-AL.json', 'data/truth/US-NY.json', 'data/docs/US-KY.json'):
    check(WR.refuse_fers_promote(rel, new={'camps': []}, live=live2) == '', f'{rel} is not a 2-fer file: never refused')
check('0 pairs' in WR.refuse_fers_promote('data/fers/US-NY.json', new=none2, live=live2), 'a 2-fer file with 0 pairs against a live file with pairs is still refused')
check(WR.refuse_fers_promote('data/fers/US-NY.json', new=live2, live=live2) == '', 'a 2-fer file with pairs is let through')
check('never public' in WR.refuse_fers_promote('data/fers/W-AU.json', new=live2, live=live2), 'a world 2-fer is still never public')
print('ALL PASS' if ok else 'FAILED'); sys.exit(0 if ok else 1)
