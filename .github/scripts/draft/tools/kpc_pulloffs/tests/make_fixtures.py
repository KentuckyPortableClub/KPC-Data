"""Developer helper: rebuilds parks.json, outlines, access.json and pictures_index.json from scene.json.
Not needed to run the selftest (the files it writes are already in tests/)."""
import json, os
from pyproj import Transformer
here = os.path.dirname(os.path.abspath(__file__))
sc = json.load(open(os.path.join(here, "scene.json")))
o = sc["origin"]
epsg = (32600 if o["lat"] >= 0 else 32700) + int((o["lon"] + 180) // 6) + 1
fwd = Transformer.from_crs(4326, epsg, always_xy=True); inv = Transformer.from_crs(epsg, 4326, always_xy=True)
ox, oy = fwd.transform(o["lon"], o["lat"])
ll = lambda x, y: [round(v, 7) for v in inv.transform(ox + x, oy + y)]
parks = []
for ref, p in sc["parks_local"].items():
    x0, y0, x1, y1 = p["box"]
    ring = [ll(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))]
    fn = f"outline_{ref}.geojson"
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"ref": ref, "agency": "Test agency"},
               "geometry": {"type": "Polygon", "coordinates": [ring]}}]}, open(os.path.join(here, fn), "w"))
    c = ll((x0 + x1) / 2, (y0 + y1) / 2)
    parks.append({"ref": ref, "name": p["name"], "outline_file": fn, "lat": c[1], "lon": c[0], "area": "US-KY"})
c = ll(1200, 1200)
parks.insert(1, {"ref": "US-9002", "name": "City Park with no official outline", "lat": c[1], "lon": c[0], "area": "US-KY"})
parks.append({"ref": "US-9004", "name": "Park whose outline host says no in robots.txt",
              "outline_url": "https://data.example.gov/private/outline.geojson", "lat": c[1], "lon": c[0], "area": "US-KY"})
parks.append({"ref": "US-9005", "name": "Tennessee park (filtered out by --areas)", "outline_file": "outline_US-9001.geojson",
              "lat": c[1], "lon": c[0], "area": "US-TN"})
json.dump(parks, open(os.path.join(here, "parks.json"), "w"), indent=1)
a1, a2, a3 = ll(720, 321), ll(485, 310), ll(5000, 5000)
json.dump({"parks": {"US-9001": [[a1[1], a1[0], "Test Lake WMA: Parking"], [a2[1], a2[0], "Test Lake WMA: Boat ramp"]],
                     "US-7777": [[a3[1], a3[0], "Far away park: Parking"]]}},
          open(os.path.join(here, "access.json"), "w"), indent=1)
pp = ll(620, 675)
json.dump({"maps": [{"ref": "US-9001", "name": "Test Lake WMA", "agency": "Test agency", "source_url": "https://agency.example.gov/map.pdf",
                     "page": 1, "files": ["maps/US-9001_test-lake.jpg"], "date": "2026-01-01", "p_points": [[pp[1], pp[0]]]},
                    {"ref": "US-9003", "name": "Lonely Ridge SNP", "agency": "Test agency", "source_url": "https://agency.example.gov/lr.pdf",
                     "page": 1, "files": ["maps/US-9003_lonely.jpg"], "date": "2026-01-01"}]},
          open(os.path.join(here, "pictures_index.json"), "w"), indent=1)
print("fixtures written")
