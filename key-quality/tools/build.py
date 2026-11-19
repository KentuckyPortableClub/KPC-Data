#!/usr/bin/env python3
"""Offline US key build of a checkout (scratch copy), the scorecard's recipe. Usage: build.py REPO OUT STATES... [--jobs N] [--set K=V]"""
import sys, os, pathlib, shutil, json, time, concurrent.futures as cf
repo = pathlib.Path(sys.argv[1]).resolve(); out = pathlib.Path(sys.argv[2]).resolve()
args = sys.argv[3:]; jobs = 2; sets = {}
st = []
i = 0
while i < len(args):
    if args[i] == '--jobs': jobs = int(args[i+1]); i += 2; continue
    if args[i] == '--set': k, v = args[i+1].split('=', 1); sets[k] = v; i += 2; continue
    st.append(args[i].upper()); i += 1
sys.path.insert(0, str(repo / '.github/scripts'))
import kpc_key_scorecard as SC
tree = out / 'tree'; keys = out / 'keys'; logs = out / 'logs'
if not tree.exists():
    tree.mkdir(parents=True); SC.copy_tree(repo, tree); SC.lay_kpc_data(tree, '/home/claude/kpc-data')
SC.lay_cache(tree, '/home/claude/work/cache', st)
keys.mkdir(parents=True, exist_ok=True); logs.mkdir(parents=True, exist_ok=True)
env = SC.build_env(os.environ, sets, '2026-11-18', out / 'offline.txt')
# each state in its own copy of the tree so parallel builds do not share files
def one(s):
    t = out / f'tree-{s}'
    if t.exists(): shutil.rmtree(t)
    shutil.copytree(tree, t, symlinks=True)
    r = SC.build_one(t, s, env, logs / f'{s}.log')
    f = t / f'data/us-key/US-{s}.json'
    if r['ok'] and f.is_file(): shutil.copyfile(f, keys / f'US-{s}.json')
    shutil.rmtree(t, ignore_errors=True)
    return s, r
with cf.ThreadPoolExecutor(jobs) as ex:
    for s, r in ex.map(one, st): print(s, r, flush=True)
