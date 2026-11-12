#!/usr/bin/env python3
"""OFFICIAL PIN FILLS (KPC owner, 2026-11-12: "official pin better than no pin"). data/intake/official-pins-*.json rows with
action 'pin-fill' are an agency's own point for a park whose POTA pin is 0,0 or missing. The search bots (park detective, GIS
hunter) use one ONLY where the park has no usable pin, so the park can be searched by location. A POTA pin is never moved,
a point-circle candidate or held row is never used here, and nothing here is a boundary. Reads only; never fetches."""
import json, pathlib


def fills(folder='data/intake'):
    out = {}
    for f in sorted(pathlib.Path(folder).glob('official-pins-*.json')):
        try: rows = json.load(open(f, encoding='utf-8')).get('rows') or []
        except Exception: continue  # noqa: BLE001
        for r in rows:
            if not isinstance(r, dict) or r.get('action') != 'pin-fill' or r.get('pota_pin'): continue
            try: la, lo = float(r['lat']), float(r['lon'])
            except (KeyError, TypeError, ValueError): continue
            if (la, lo) != (0.0, 0.0) and -90 <= la <= 90 and -180 <= lo <= 180: out.setdefault(r.get('ref'), (la, lo, r.get('source_url') or ''))
    return out
