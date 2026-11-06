#!/usr/bin/env python3
"""Nov 6 Part B: layer_of CA/world root cause — never PAD-US for non-US; CPCAD / world src."""
import os, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
os.environ.setdefault('LINKS', '/tmp/fers/L')
os.environ.setdefault('DATA', str(ROOT))
import kpc_pile_solver as S
S.LINKS = pathlib.Path(os.environ['LINKS']); S.DATA = pathlib.Path(os.environ['DATA'])
S.LAYERS.update(S.load(S.LINKS / 'data/us-key/layers.json', {}))
S.LAYERS_CA.update(S.load(S.LINKS / 'data/ca-key/layers.json', {}) or S.load(S.DATA / 'data/ca-key/layers.json', {}))
S.LAYERS_W.update(S.load(S.LINKS / 'data/world-key/layers.json', {}) or S.load(S.DATA / 'data/world-key/layers.json', {}))
ok=True
def check(c,m):
  global ok
  print(('PASS ' if c else 'FAIL ')+m); ok = ok and bool(c)
ca=S.layer_of(22084,'CA-ON')
check(bool(ca) and 'CPCAD' in ca[2] and ca[4]=='22084', f'CA digit -> CPCAD ({ca and ca[2:5]})')
check(bool(ca) and 'PAD-US' not in ca[0], 'CA not PAD-US')
pre=S.layer_of('Ontario fede:321','CA-ON')
check(bool(pre) and pre[4]=='321' and 'lioservices' in pre[0].lower(), f'CA Prefix:id ({pre and pre[0][:60]})')
check(S.layer_of(6927,'FR') is None, 'world without src -> None')
w=S.layer_of(6927,'FR', src='EEA nationally designated areas')
check(bool(w) and w[4]=='6927' and 'discomap' in w[0].lower(), f'world+src ({w and w[0][:60]})')
us=S.layer_of(255681,'US-TN')
check(bool(us) and 'PAD-US' in us[0], f'US digit PAD-US')
print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
