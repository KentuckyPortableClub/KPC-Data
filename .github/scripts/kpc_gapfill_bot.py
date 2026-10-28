#!/usr/bin/env python3
"""GAP FILLER shim (Oct 28 2026): the gap filler grew into the PARK DETECTIVE (kpc_detective_bot.py, workflow kpc-detective.yml,
folder data/detective). This file only runs it, so earlier wiring (kpc-gapfill.yml, notes) still works. Same env, same --selftest."""
import os, runpy, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpc_detective_bot.py'), run_name='__main__')
