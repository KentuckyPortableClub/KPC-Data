"""Finds the club's shared reference modules (kpc_manners, kpc_order) WITHOUT copying them into the engine.

Search order (same idea as kpc_shard): $KPC_TOOLS_DIR, the engine's parent folder (KPC-Data .github/scripts/tools/), its
grandparent (.github/scripts/), then vendor/ (a copy kept ONLY so the selftest runs from this folder; a warning is printed)."""
import importlib.util, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
_WARNED = set()


def _load(name):
    if name in sys.modules: return sys.modules[name]
    dirs = [os.environ.get('KPC_TOOLS_DIR', ''), str(HERE.parent), str(HERE.parent.parent)]
    for d in [x for x in dirs if x]:
        p = pathlib.Path(d) / f'{name}.py'
        if p.exists(): break
    else:
        p = HERE / 'vendor' / f'{name}.py'
        if name not in _WARNED and not os.environ.get('KPC_QUIET'):
            _WARNED.add(name); print(f'note: using vendor/{name}.py (set KPC_TOOLS_DIR to the club copy)', file=sys.stderr)
    spec = importlib.util.spec_from_file_location(name, p); mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod; spec.loader.exec_module(mod); return mod


def manners(): return _load('kpc_manners')
def order(): return _load('kpc_order')
