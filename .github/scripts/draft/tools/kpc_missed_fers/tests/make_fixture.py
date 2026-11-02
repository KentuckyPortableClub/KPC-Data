"""Builds the synthetic selftest fixture in tests/fixture (run once; output is committed).
All callsigns below are made up."""
import json, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixture")

# ref: (name, type, lat, lon, outline status, bbox or None, area)
P = {
 "US-0050": ("Mammoth Cave National Park", "National Park", 37.1877, -86.1012, "official", None, "US-KY"),
 "US-10105": ("Green River State Wild River", "Wild and Scenic River", 37.20, -86.05, "approximate", None, "US-KY"),
 "US-3001": ("Two People State Park", "State Park", 37.50, -85.00, "official", None, "US-KY"),
 "US-3002": ("Two People WMA", "Wildlife Management Area", 37.55, -85.02, "official", None, "US-KY"),
 "US-4001": ("Alpha State Park", "State Park", 37.80, -84.50, "official", None, "US-KY"),
 "US-4002": ("Beta State Park", "State Park", 37.82, -84.45, "official", None, "US-KY"),
 "US-5001": ("Daniel Boone National Forest", "National Forest", 37.30, -83.90, "official", None, "US-KY"),
 "US-5002": ("Gamma State Nature Preserve", "State Nature Preserve", 37.35, -83.95, "approximate", None, "US-KY"),
 "US-6001": ("Far West WMA", "Wildlife Management Area", 37.00, -88.00, "official", None, "US-KY"),
 "US-6002": ("Far East WMA", "Wildlife Management Area", 37.00, -87.30, "official", None, "US-KY"),
 "US-6003": ("Big Forest A", "State Forest", 36.70, -85.00, "official", [-85.10, 36.60, -84.86, 36.80], "US-KY"),
 "US-6004": ("Big Forest B", "State Forest", 36.70, -84.70, "official", [-84.85, 36.60, -84.60, 36.80], "US-KY"),
 "US-7001": ("Sheltowee Trace National Recreation Trail", "National Recreation Trail", 37.60, -84.00, "approximate", None, "US-KY"),
 "US-7002": ("Delta State Park", "State Park", 37.62, -84.02, "official", None, "US-KY"),
 "CA-0001": ("Border Test Provincial Park", "Provincial Park", 37.81, -84.48, "official", None, "CA-ON"),
}
for i in range(1, 9):
    P[f"US-800{i}"] = (f"Listed Park {i}", "State Park", 38.0 + i * 0.001, -85.5, "official", None, "US-KY")
for i in range(1, 13):
    P[f"US-90{i:02d}"] = (f"Rover Stop {i}", "WMA", 38.5 + i * 0.01, -83.5, "official", None, "US-KY")

ev = []  # (callsign, yyyymmdd, [refs])
def three_by_three(a, b, calls=("W1AAA", "W2BBB", "K3CCC"), base=20250101):
    for i, c in enumerate(calls):
        ev.append((c, str(base + i), [a, b]))

for i, c in enumerate(["W1AAA", "W2BBB", "K3CCC", "N4DDD"]):          # known pair: 4x4
    ev.append((c, str(20240601 + i), ["US-0050", "US-10105"]))
ev += [("W1AAA", "20240701", ["US-3001", "US-3002"]), ("W2BBB", "20240702", ["US-3001", "US-3002"]),
       ("W1AAA", "20240703", ["US-3001", "US-3002"])]                    # 2 people, 3 dates
three_by_three("US-4001", "US-4002", base=20240801)
ev.append(("W1AAA/P", "20240810", ["US-4001", "US-4002"]))               # same person as W1AAA
three_by_three("US-5001", "US-5002", base=20240901)
three_by_three("US-6001", "US-6002", base=20241001)
three_by_three("US-6003", "US-6004", base=20241101)
three_by_three("US-7001", "US-7002", base=20241201)
three_by_three("US-4001", "CA-0001", calls=("VE3XXX", "VE3YYY", "VA3ZZZ"), base=20240501)
for k in range(1, 8, 2):
    three_by_three(f"US-800{k}", f"US-800{k + 1}", base=20230101 + k * 10)
for d, c in enumerate(["KR0VER", "KR1VER", "KR2VER", "KR3VER"]):        # 12-park rove days
    ev.append((c, str(20240301 + d), [f"US-90{i:02d}" for i in range(1, 13)]))
ev.append(("N4DDD", "20240815", ["US-4001"]))                             # single-park day

acts = defaultdict(list)
for c, d, refs in ev:
    for r in refs:
        acts[r].append({"activeCallsign": c, "qso_date": d, "totalQSOs": 12, "locationDesc": P[r][6]})

def w(rel, obj):
    p = os.path.join(FX, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)

for area in ("US-KY", "CA-ON"):
    w(f"pota/parks/{area}.json", [{"reference": r, "name": v[0], "latitude": v[2], "longitude": v[3],
       "locationDesc": area, "attempts": len(acts[r]), "activations": len(acts[r]), "qsos": 12 * len(acts[r])}
       for r, v in P.items() if v[6] == area] +
      ([{"reference": "US-0999", "name": "Never Activated", "latitude": 37, "longitude": -85, "locationDesc": "US-KY",
         "attempts": 0, "activations": 0, "qsos": 0}] if area == "US-KY" else []))
for r, rows in acts.items():
    w(f"pota/activations/{r}.json", rows)
w("data/parkinfo/US-KY.json", {"parks": {r: [v[0], "", v[1], "", "", v[2], v[3]] for r, v in P.items() if r.startswith("US-")}})
w("data/parkinfo/CA.json", {"parks": {r: [v[0], "", v[1], "", "", v[2], v[3], "", "", "", "ON"] for r, v in P.items() if r.startswith("CA-")}})
w("data/us-key/US-KY.json", {"parks": {r: {"g": v[4], "m": [], "src": [], **({"bbox": v[5]} if v[5] else {})}
                                     for r, v in P.items() if r.startswith("US-")}})
w("data/ca-key/CA.json", {"parks": {"CA-0001": {"g": "official", "m": [], "src": []}}})
# four different (made-up) shapes of club 2-fer files, to exercise the lenient reader
w("data/fers/US-KY.json", {"fers": [{"refs": ["US-8001", "US-8002"], "status": "live"}]})
w("data/fers/missing-US-KY.json", {"rows": [{"a": "US-8003", "b": "US-8004", "why": "no outline"}]})
w("data/fers/known-answers.json", {"yes": ["US-0050+US-10105"], "no": [{"pair": "US-8005 / US-8006"}]})
w("data/fers/dropped.json", {"US-8007": {"with": "US-8008", "why": "checked NO"}})
print("fixture written")
