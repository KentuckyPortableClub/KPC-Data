// Rebuilds the selftest fixtures from ../../kpc_gps_site/sample-data.js (same made-up parks as the site demo),
// plus a second area (US-TN) and one broken park row. Run: node tests/make_fixtures.js   (only needed if the sample changes)
const fs = require("fs"), path = require("path");
const S = require(path.join(__dirname, "..", "..", "kpc_gps_site", "sample-data.js"));
const d = __dirname, w = (n, o) => fs.writeFileSync(path.join(d, n), JSON.stringify(o, null, 1) + "\n");
fs.mkdirSync(path.join(d, "data", "parkinfo"), { recursive: true });
for (const sub of ["access", "us-key", "fers"]) fs.mkdirSync(path.join(d, "data", sub), { recursive: true });
const pi = JSON.parse(JSON.stringify(S.files["data/parkinfo/US-KY.json"]));
pi.parks["US-9004"] = ["Broken Row Park", "", "Park", "", "", "not a number", null];     // must be reported, not crash
w("data/parkinfo/US-KY.json", pi);
w("data/parkinfo/US-TN.json", { parks: { "US-9101": ["Sample Hollow State Park", "", "SP", "", "", 36.50, -85.10] } });
w("data/access/US-KY.json", S.files["data/access/US-KY.json"]);
w("data/access/US-TN.json", { parks: { "US-9101": [[36.501, -85.101, "Sample Hollow SP: Parking", { agency: "Tennessee State Parks" }]] } });
w("data/us-key/US-KY.json", S.files["data/us-key/US-KY.json"]);
w("data/us-key/US-TN.json", { parks: { "US-9101": { g: "pin", m: [], src: [] } } });
w("data/fers/US-KY.json", S.files["data/fers/US-KY.json"]);
w("outlines.geojson", { type: "FeatureCollection", features: [S.outlines["US-9001"], S.outlines["US-9002"]] });
w("trails.geojson", { type: "FeatureCollection", features: [S.trails["US-9001"][0].geojson] });
console.log("fixtures written");
