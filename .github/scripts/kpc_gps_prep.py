#!/usr/bin/env python3
"""GPS PACKS: build the pack bot's inputs from the club's REAL files (chat 10, Oct 31 2026; HQ 9:50 PM).
  python3 kpc_gps_prep.py <links dir> <out dir> [areas]
Kentucky lives in KPC-Links (kpc-ky-data.json pins + 'ap' parking; the official ky-*.geojson layers, matched to parks by the answer
key's tracts = the same matching the site uses). Other US / Canada areas: data/parkinfo + data/access (pins + parking; their outlines
are read live from the agencies by the site and are not stored, so their packs are pins + parking until a stored copy exists).
Writes <out>/parkinfo/US-KY.json, <out>/access/US-KY.json (club shapes), <out>/outlines/US-KY.geojson (properties ref / agency /
status official). The proclamation line (Daniel Boone 'Forest boundary line') and OpenStreetMap outlines are never used."""
import ast, json, pathlib, sys

L, O = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
FILES = {'bstate': ('ky-state-parks.geojson', 'Kentucky State Parks'), 'bwma': ('ky-hunting-areas.geojson', 'Kentucky Fish & Wildlife'),
         'bsnp': ('ky-nature-preserves.geojson', 'Kentucky Office of Nature Preserves'), 'bsna': ('ky-natural-areas.geojson', 'Kentucky Office of Nature Preserves'),
         'bdbnfo': ('ky-dbnf-owned.geojson', 'U.S. Forest Service'), 'bnps': ('ky-nps.geojson', 'National Park Service'),
         'bwild': ('ky-wild-rivers.geojson', 'Kentucky Office of Nature Preserves'), 'bwilder': ('ky-wilderness.geojson', 'U.S. Forest Service'),
         'bfws': ('ky-fws.geojson', 'U.S. Fish & Wildlife Service'), 'bpad': ('ky-padus-parks.geojson', 'USGS PAD-US (official land records)')}


def lst(v):
    if isinstance(v, list): return v
    try: return ast.literal_eval(v) if v else []
    except Exception: return []  # noqa: BLE001


AG = {'KDFWR': 'Kentucky Fish & Wildlife', 'NPS': 'National Park Service', 'Forest Service': 'U.S. Forest Service', 'Kentucky State Parks': 'Kentucky State Parks'}


def main():
    nkpc = [0]
    for d in ('parkinfo', 'access', 'outlines'): (O / d).mkdir(parents=True, exist_ok=True)
    D = json.load(open(L / 'kpc-ky-data.json'))
    pk, ac = {}, {}
    for p in D.get('parks') or []:
        r = p.get('c')
        if not r: continue
        try: la, lo = float(p['la']), float(p['lo'])
        except Exception: continue  # noqa: BLE001
        pk[r] = [p.get('n') or r, p.get('web') or '', p.get('t') or '', '', '', la, lo]
        ap = []
        for a in lst(p.get('ap')):
            if len(a) < 2: continue
            lab = str(a[2]) if len(a) > 2 else 'Parking'
            if lab.split(' ')[0] == 'KPC' or '(KPC' in lab: nkpc[0] += 1; continue   # club-made points are not an official access list: left out of the packs
            ag = next((v for k, v in AG.items() if lab.startswith(k)), '')
            out_ = 'just outside the line' in lab
            ap.append([float(a[0]), float(a[1]), lab + (f' ({ag})' if ag and not lab.rstrip().endswith(')') else '')] + (['outside'] if out_ else []))
        if ap: ac[r] = ap
    json.dump({'parks': pk, 'state': 'KY'}, open(O / 'parkinfo/US-KY.json', 'w'))
    json.dump({'note': 'Kentucky parking / access points (kpc-ky-data.json ap: KDFWR, Kentucky State Parks, NPS, Forest Service ...)', 'parks': ac}, open(O / 'access/US-KY.json', 'w'))
    key = json.load(open(L / 'data/ky-answer-key.json')).get('parks') or {}
    feats, cache = [], {}
    for ref, v in key.items():
        polys, ags = [], []
        for t in v.get('tracts') or []:
            k, nm = t[0], t[1]
            if k not in FILES: continue
            f, ag = FILES[k]
            if f not in cache:
                try: cache[f] = json.load(open(L / f)).get('features') or []
                except Exception: cache[f] = []  # noqa: BLE001
            for ft in cache[f]:
                pr = ft.get('properties') or {}
                if pr.get('NAME') == nm or (k == 'bdbnfo' and pr.get('ref') == ref) or (k == 'bpad' and pr.get('ref') == ref):
                    g = ft.get('geometry') or {}
                    if g.get('type') == 'Polygon': polys.append(g['coordinates'])
                    elif g.get('type') == 'MultiPolygon': polys += g['coordinates']
                    ags.append(ag)
        if polys:
            feats.append({'type': 'Feature', 'properties': {'ref': ref, 'agency': ' / '.join(dict.fromkeys(ags)), 'status': 'official'},
                          'geometry': {'type': 'MultiPolygon', 'coordinates': polys}})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(O / 'outlines/US-KY.geojson', 'w'))
    (O / 'one').mkdir(exist_ok=True); pl = []   # the pull-off finder's input: one outline file per park + parks.json
    for ft in feats:
        r = ft['properties']['ref']; fp = (O / 'one' / f'{r}.geojson').resolve()
        json.dump({'type': 'FeatureCollection', 'features': [ft]}, open(fp, 'w'))
        pl.append({'ref': r, 'name': pk.get(r, [r])[0], 'outline_file': str(fp), 'lat': pk.get(r, [0] * 7)[5], 'lon': pk.get(r, [0] * 7)[6], 'area': 'US-KY'})
    json.dump(pl, open(O / 'pulloff-parks.json', 'w'), indent=0)
    print(f'::notice title=GPS prep::KY {len(pk)} parks, {len(ac)} with parking, {len(feats)} official outlines, {nkpc[0]} club-made points left out')


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=GPS prep::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
