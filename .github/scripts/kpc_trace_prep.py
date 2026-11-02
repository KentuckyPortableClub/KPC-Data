#!/usr/bin/env python3
"""PARCEL TRACER INPUT from the Hard Look workbooks (chat 10, Nov 1 2026; AUTOMATION FIRST). Reads data/intake/_in/hardlook/*.json
(the intake reader's copies) and writes <out> = the tracer's parks.json: every row the researcher marked PARCEL with an ArcGIS parcel
layer (MapServer/n or FeatureServer/n): ref, name, area, pin, the owner names we know (agency + quoted owner text in the record /
notes), the parcel layer, the owner field when the researcher named one. The tracer still decides nothing (Approximate, held back
on any size / other-park / cut-off check). Never fails.   python3 kpc_trace_prep.py <out.json>"""
import glob, json, re, sys

FED = re.compile(r'Parks Canada|Environment (?:and Climate Change )?Canada|Canadian Wildlife Service|National Defence|Fisheries and Oceans|Agriculture and Agri-Food|Transport Canada|Natural Resources Canada|National Capital Commission|Public Services and Procurement|Crown-Indigenous|Indigenous Services Canada|Parcs Canada|Environnement', re.I)
LAY = re.compile(r'^https?://\S+?/(?:MapServer|FeatureServer)/\d+', re.I)
out = []
for f in sorted(glob.glob('data/intake/_in/hardlook/hardlook-*.json')):
    try: rows = (json.load(open(f, encoding='utf-8')) or {}).get('rows') or {}
    except Exception: continue  # noqa: BLE001
    for ref, v in rows.items():
        if v.get('status') != 'PARCEL': continue
        m = LAY.match(str(v.get('url') or '').strip())
        if not m and not (ref.startswith('CA-') and FED.search(f"{v.get('agency') or ''} {v.get('record') or ''}")): continue   # Nov 2 review: only FEDERAL Canadian land goes to the federal property register (DFRP)
        try: lat, lon = float(v.get('lat')), float(v.get('lon'))
        except Exception: continue  # noqa: BLE001
        txt = f"{v.get('record') or ''} {v.get('notes') or ''}"
        owners = [o for o in [str(v.get('agency') or '').strip()] if o]
        owners += [q for q in re.findall(r'(?:owner|OWNER|Owner)[^"\']{0,20}["\']([^"\']{4,80})["\']', txt)]
        fld = re.split(r'[\s/,;(]', str(v.get('field') or '').strip())[0]
        st = str(v.get('st') or '')
        out.append({'ref': ref, 'name': v.get('name'), 'state_or_prov': f'{ref[:2]}-{st}' if st else ref[:2], 'lat': lat, 'lon': lon,
                    'agency_owner_names': list(dict.fromkeys(owners)), **({'parcel_layer_url': m.group(0)} if m else {'owner_source': 'dfrp'}),
                    **({'owner_field': fld} if re.search(r'own|name|prop', fld, re.I) else {}),
                    'club_source': f"Hard Look ({v.get('_file') or f.split('/')[-1]}): {str(v.get('record') or '')[:200]}"})
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(f'::notice title=Tracer input::{len(out)} PARCEL parks from the Hard Look files')
