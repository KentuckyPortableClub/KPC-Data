"""Builds tests/fixtures.json, tests/sample_input/camping-test.json, tests/known/ and
tests/fixture_states.geojson. All hosts are made-up *.example.* test hosts (not real layers).
Run:  python tests/make_fixtures.py   (then:  python kpc_camp_layers.py --selftest --write-expected)"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import kpc_camp_layers as k  # noqa: E402

R = {}


def put(url, body=None, status=200, text=None, headers=None):
    v = {"status": status}
    if text is not None:
        v["text"] = text
    else:
        v["json"] = body
    if headers:
        v["headers"] = headers
    R[url] = v


def pt(x, y):
    return {"x": x, "y": y}


# ---- A: plain point layer, coded-value domain, paging (maxRecordCount 5) ----
A = "https://gis.dnr.example.gov/arcgis/rest/services/Recreation/Facilities/MapServer/2"
put("https://gis.dnr.example.gov/robots.txt", text="User-agent: *\nDisallow: /private/\n")
codes = ["Campground", "Horse Camp", "Group Camp", "Camper Cabin", "Boat Ramp", "Trailhead", "Picnic Shelter",
         "Day Use Area", "Backpack Campsite", "Overlook"]
put(A + "?f=json", {
    "type": "Feature Layer", "name": "Recreation Facilities", "geometryType": "esriGeometryPoint",
    "copyrightText": "Example State Department of Natural Resources", "maxRecordCount": 5,
    "objectIdField": "OBJECTID", "advancedQueryCapabilities": {"supportsPagination": True},
    "fields": [
        {"name": "OBJECTID", "type": "esriFieldTypeOID"},
        {"name": "FAC_NAME", "type": "esriFieldTypeString"},
        {"name": "FAC_TYPE", "type": "esriFieldTypeSmallInteger",
         "domain": {"type": "codedValue", "name": "FacType",
                    "codedValues": [{"name": n, "code": i + 1} for i, n in enumerate(codes)]}},
        {"name": "STATUS", "type": "esriFieldTypeString"},
        {"name": "PARK_NAME", "type": "esriFieldTypeString"},
        {"name": "WEB_URL", "type": "esriFieldTypeString"},
        {"name": "RESERVE_URL", "type": "esriFieldTypeString"},
        {"name": "DESCRIPTION", "type": "esriFieldTypeString"}]})
a_rows = [
    ("Bear Lake Campground", 1, "Open", -91.5000, 47.2000, "https://dnr.example.gov/parks/bear-lake/camping", ""),
    ("Bear Lake Campground", 1, "Open", -92.3000, 47.9000, "", ""),
    ("Saddle Ridge Horse Camp", 2, "Open", -94.1000, 46.3000, "", ""),
    ("Pine Group Camp", 3, "Open", -94.2000, 46.4000, "", ""),
    ("Aspen Camper Cabins", 4, "Open", -94.3000, 46.5000, "", "https://reserve.example.gov/cabins/aspen"),
    ("Lakeview Boat Ramp", 5, "Open", -94.4000, 46.6000, "", ""),
    ("North Shore Trailhead", 6, "Open", -94.5000, 46.7000, "", ""),
    ("Lakeview Picnic Shelter", 7, "Open", -94.4010, 46.6010, "", "https://reserve.example.gov/shelters/lakeview"),
    ("Sandy Beach Day Use Area", 8, "Open", -94.6000, 46.8000, "", ""),
    ("Old Pine Campground", 1, "Decommissioned", -94.7000, 46.9000, "", ""),
    ("Moose Bay Backpack Site", 9, "Open", -91.8000, 47.8000, "", ""),
    ("Eagle Overlook", 10, "Open", -91.9000, 47.7000, "", ""),
    ("Ghost Campground", 1, "Open", None, None, "", ""),
    ("Prairie Creek Campground", 1, "Open", -93.5000, 42.0000, "", ""),
]
feats = []
for i, (n, t, s, x, y, url, res) in enumerate(a_rows, 1):
    feats.append({"attributes": {"OBJECTID": i, "FAC_NAME": n, "FAC_TYPE": t, "STATUS": s, "PARK_NAME": "Test Park",
                                 "WEB_URL": url or None, "RESERVE_URL": res or None,
                                 "DESCRIPTION": "Picnic tables, boat ramp and trailhead nearby."},
                  "geometry": pt(x, y) if x is not None else None})
for off in range(0, len(feats), 5):
    chunk = feats[off:off + 5]
    put(k.query_url(A, "1=1", [], resultOffset=off, resultRecordCount=5, orderByFields="OBJECTID"),
        {"spatialReference": {"wkid": 4326, "latestWkid": 4326}, "features": chunk,
         "exceededTransferLimit": off + 5 < len(feats)})

# ---- B: polygon layer (campground loops), subtypes, GlobalID, state named in the rows ----
B = "https://services.county.example.org/arcgis/rest/services/Parks/Campground_Loops/FeatureServer/0"
put(B + "?f=json", {
    "type": "Feature Layer", "name": "Campground Loops", "geometryType": "esriGeometryPolygon", "copyrightText": "",
    "maxRecordCount": 1000, "objectIdField": "OBJECTID", "typeIdField": "SiteCat",
    "types": [{"id": 1, "name": "Campground Loop", "domains": {}}, {"id": 2, "name": "Picnic Area", "domains": {}}],
    "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"},
               {"name": "GlobalID", "type": "esriFieldTypeGlobalID"},
               {"name": "Name", "type": "esriFieldTypeString"},
               {"name": "SiteCat", "type": "esriFieldTypeInteger"},
               {"name": "STATE", "type": "esriFieldTypeString"}]})
put("https://services.county.example.org/arcgis/rest/services/Parks/Campground_Loops/FeatureServer?f=json",
    {"documentInfo": {"Author": "Example County Parks Department"}, "copyrightText": ""})


def loop(x0, y0, w, h, wiggle=False):
    ring = [[x0, y0], [x0, y0 + h]]
    if wiggle:   # near-straight vertices along the top edge (< 3 m off) are simplified away
        ring += [[x0 + w * f, y0 + h + (0.000005 if j % 2 else -0.000004)] for j, f in enumerate((0.2, 0.4, 0.6, 0.8))]
    ring += [[x0 + w, y0 + h], [x0 + w, y0], [x0, y0]]
    return ring


b_rows = [("Riverbend Campground Loop A", 1, loop(-91.2, 45.1, 0.002, 0.0015, True)),
          ("Riverbend Picnic Grove", 2, loop(-91.21, 45.11, 0.001, 0.001)),
          ("Tamarack Walk-in Sites", 1, loop(-91.3, 45.2, 0.001, 0.0008))]
put(k.query_url(B, "1=1", [], resultOffset=0, resultRecordCount=1000, orderByFields="OBJECTID"),
    {"spatialReference": {"wkid": 4326}, "exceededTransferLimit": False,
     "features": [{"attributes": {"OBJECTID": i, "GlobalID": "{0000000%d-AAAA-BBBB-CCCC-DDDDDDDDDDDD}" % i,
                                  "Name": n, "SiteCat": c, "STATE": "Wisconsin"},
                   "geometry": {"rings": [r]}} for i, (n, c, r) in enumerate(b_rows, 1)]})

# ---- C: Forest Service EDW-style query URL with its own where and f=html ----
C = "https://apps.fs.example.gov/arcx/rest/services/EDW/EDW_RecreationOpportunities_01/MapServer/0"
C_WHERE = ("FORESTNAME = 'Superior National Forest' AND MARKERACTIVITY IN "
           "('Campground Camping','Group Camping','Dispersed Camping','Cabin Rentals')")
import urllib.parse  # noqa: E402
C_URL = C + "/query?" + urllib.parse.urlencode([("where", C_WHERE), ("outFields", "*"), ("f", "html")])
put(C + "?f=json", {
    "type": "Feature Layer", "name": "Recreation Opportunities", "geometryType": "esriGeometryPoint",
    "copyrightText": "USDA Forest Service", "maxRecordCount": 1000, "objectIdField": "OBJECTID",
    "fields": [{"name": n, "type": t} for n, t in [
        ("OBJECTID", "esriFieldTypeOID"), ("RECAREANAME", "esriFieldTypeString"),
        ("RECAREAID", "esriFieldTypeString"), ("FORESTNAME", "esriFieldTypeString"),
        ("MARKERACTIVITY", "esriFieldTypeString"), ("MARKERACTIVITYGROUP", "esriFieldTypeString"),
        ("RECAREAURL", "esriFieldTypeString"), ("OPENSTATUS", "esriFieldTypeString"),
        ("RESERVATION_INFO", "esriFieldTypeString")]]})
c_rows = [("Fall Lake Campground", "Campground Camping", "open", -91.7200, 47.9500, "https://www.fs.example.gov/recarea/superior/recarea/?recid=101"),
          ("Fall Lake Campground", "Group Camping", "open", -91.7200, 47.9500, "https://www.fs.example.gov/recarea/superior/recarea/?recid=101"),
          ("Echo Lake Group Campground", "Group Camping", "open", -92.4900, 48.1700, "https://www.fs.example.gov/recarea/superior/recarea/?recid=102"),
          ("Isabella River Dispersed Camping Area", "Dispersed Camping", "open", -91.3500, 47.6200, ""),
          ("Beaver Flats Campground", "Campground Camping", "Closed permanently", -91.4000, 47.5000, "")]
put(k.query_url(C, C_WHERE, [], resultOffset=0, resultRecordCount=1000, orderByFields="OBJECTID"),
    {"spatialReference": {"wkid": 4326}, "exceededTransferLimit": False,
     "features": [{"attributes": {"OBJECTID": 500 + i, "RECAREANAME": n, "RECAREAID": str(100 + i),
                                  "FORESTNAME": "Superior National Forest", "MARKERACTIVITY": act,
                                  "MARKERACTIVITYGROUP": "Camping & Cabins", "RECAREAURL": url or None,
                                  "OPENSTATUS": st, "RESERVATION_INFO": None},
                   "geometry": pt(x, y)} for i, (n, act, st, x, y, url) in enumerate(c_rows, 1)]})

# ---- D: "points of interest" layer (New York DEC-style), plain text type field ----
D = "https://gisservices.dec.example.gov/arcgis/rest/services/DEC/PointsOfInterest/MapServer/0"
put(D + "?f=json", {
    "type": "Feature Layer", "name": "Points of Interest", "geometryType": "esriGeometryPoint",
    "copyrightText": "Example State Department of Environmental Conservation", "maxRecordCount": 2000,
    "objectIdField": "OBJECTID",
    "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"}, {"name": "NAME", "type": "esriFieldTypeString"},
               {"name": "ASSET", "type": "esriFieldTypeString"}, {"name": "PROPNAME", "type": "esriFieldTypeString"}]})
d_rows = [("Sawyer Lean-to", "Lean-to", -74.0100, 44.1800), ("Heart Lake Tent Site 3", "Primitive Tent Site", -73.9700, 44.1800),
          ("Heart Lake Parking Area", "Parking Area", -73.9650, 44.1810), ("Heart Lake Boat Launch", "Boat Launch", -73.9660, 44.1820),
          ("Heart Lake Picnic Pavilion", "Pavilion", -73.9670, 44.1830), ("Lake Durant Campground", None, -74.3600, 43.8400)]
put(k.query_url(D, "1=1", [], resultOffset=0, resultRecordCount=2000, orderByFields="OBJECTID"),
    {"spatialReference": {"wkid": 4326}, "exceededTransferLimit": False,
     "features": [{"attributes": {"OBJECTID": i, "NAME": n, "ASSET": a, "PROPNAME": "Example Wild Forest"},
                   "geometry": pt(x, y)} for i, (n, a, x, y) in enumerate(d_rows, 1)]})

# ---- E: needs a token; F: always 429; G: robots.txt says no; H: forbidden source ----
E = "https://gis.tokenparks.example.com/arcgis/rest/services/Secure/Camps/MapServer/0"
put(E + "?f=json", {"error": {"code": 499, "message": "Token Required", "details": []}})
F = "https://busy.example.net/arcgis/rest/services/Camps/MapServer/0"
put(F + "?f=json", text="Too Many Requests", status=429, headers={"Retry-After": "1"})
G = "https://noindex.example.org/arcgis/rest/services/Camps/MapServer/0"
put("https://noindex.example.org/robots.txt", text="User-agent: *\nDisallow: /arcgis/\n")
H = "https://www.openstreetmap.org/api/0.6/map?bbox=-91,47,-90,48"

layers = {A: ["US-1001", "US-1002"], B: ["US-2001"], C_URL: ["US-4321"], D: ["US-NY"],
          E: ["US-5001"], F: ["US-6001"], G: ["US-7001"], H: ["US-8001"]}
with open(os.path.join(HERE, "sample_input", "camping-test.json"), "w") as f:
    json.dump({"layers": layers}, f, indent=1)
with open(os.path.join(HERE, "fixtures.json"), "w") as f:
    json.dump({"note": "Mocked layer answers for --selftest (made-up test hosts).", "responses": R}, f, indent=1)
with open(os.path.join(HERE, "known", "campfed", "US-MN.json"), "w") as f:
    json.dump({"src": "Recreation.gov (test copy)", "camps": [
        ["RG-900001", "Bear Lake CG", 47.2005, -91.5003, "c", "", "", ""],
        ["RG-900002", "Cedar Point Campground", 46.0, -94.0, "c", "", "", ""]]}, f, indent=1)


def rect(code, s, w, n, e):
    return {"type": "Feature", "properties": {"STUSPS": code},
            "geometry": {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}}


with open(os.path.join(HERE, "fixture_states.geojson"), "w") as f:
    json.dump({"type": "FeatureCollection", "note": "two rough test rectangles, not real outlines",
               "features": [rect("MN", 43.5, -97.2, 49.4, -89.5), rect("NY", 40.5, -79.8, 45.0, -71.8)]}, f, indent=1)
print("fixtures written:", len(R), "responses")
