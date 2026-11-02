/* SAMPLE data for demo.html and the tests. The parks are MADE UP (refs US-9001..US-9003),
 * placed in eastern Kentucky only so the map position looks right. Not real club data.
 * The file shapes copy the install contract's "Club file shapes"; the access, fers, KPCB and trail shapes are ASSUMED. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.KPC_SAMPLE = factory();
}(typeof self !== "undefined" ? self : this, function () {
  function rnd(seed) { var x = seed; return function () { x = (x * 1103515245 + 12345) % 2147483648; return x / 2147483648; }; }
  // a wiggly closed ring around (lat, lon), radius r (deg), n points
  function ring(lat, lon, r, n, seed) {
    var R = rnd(seed), out = [];
    for (var i = 0; i < n; i++) {
      var t = 2 * Math.PI * i / n, w = r * (1 + 0.18 * Math.sin(5 * t) + 0.06 * Math.sin(37 * t) + 0.01 * (R() - 0.5));
      out.push([+(lon + w * Math.cos(t) / Math.cos(lat * Math.PI / 180)).toFixed(7), +(lat + w * Math.sin(t)).toFixed(7)]);
    }
    out.push(out[0].slice());
    return out;
  }
  var lake = { type: "Feature", properties: { ref: "US-9001", agency: "Kentucky Dept. of Fish & Wildlife Resources", status: "official" },
    geometry: { type: "MultiPolygon", coordinates: [
      [ring(37.80, -83.65, 0.035, 6000, 7), ring(37.80, -83.65, 0.008, 400, 9).reverse()],   // main piece with a lake hole
      [ring(37.75, -83.60, 0.006, 900, 11)]                                                    // a separate piece
    ] } };
  var creek = { type: "Feature", properties: { ref: "US-9002", status: "approximate", why: "traced from the agency's picture map" },
    geometry: { type: "Polygon", coordinates: [ring(37.86, -83.55, 0.012, 300, 5)] } };
  var trailLine = { type: "Feature", properties: { ref: "US-9001", name: "Sample Lake Loop Trail", agency: "Kentucky Dept. of Fish & Wildlife Resources" },
    geometry: { type: "LineString", coordinates: ring(37.80, -83.65, 0.02, 1500, 3).slice(0, 1200) } };
  var files = {
    "data/parkinfo/US-KY.json": { parks: {
      "US-9001": ["Sample Lake Wildlife Management Area", "https://example.org/sample-lake", "WMA", "", "", 37.80, -83.65],
      "US-9002": ["Sample Creek State Natural Area", "https://example.org/sample-creek", "SNA", "", "", 37.86, -83.55],
      "US-9003": ["Sample Ridge Preserve", "", "Preserve", "", "", 37.70, -83.70]
    } },
    "data/us-key/US-KY.json": { parks: {
      "US-9001": { g: "official", m: [["KDFWR-123", "Sample Lake WMA", 9000, "agency boundary file"]], src: [{ agency: "Kentucky Dept. of Fish & Wildlife Resources", url: "https://example.org/kdfwr" }] },
      "US-9002": { g: "approximate", m: [["PM-1", "Sample Creek SNA", 700, "traced from the agency's picture map"]], src: [] },
      "US-9003": { g: "pin", m: [], src: [] }
    } },
    "data/access/US-KY.json": { parks: {
      "US-9001": [
        [37.8301, -83.6512, "Sample Lake WMA: Parking", { agency: "KDFWR", source_url: "https://example.org/kdfwr/access", read_date: "2026-10-30" }],
        [37.7702, -83.6431, "Sample Lake WMA: Parking", { agency: "KDFWR" }],
        [37.8005, -83.6799, "Sample Lake WMA: Boat ramp"],
        [37.8200, -83.6205, "Sample Lake WMA: Entrance"],
        [37.8700, -83.6500, "Sample Lake WMA: Parking", "outside", { agency: "Daniel Boone NF" }],
        { lat: 37.7900, lon: -83.6100, label: "Sample Lake WMA: Possible pull-off", grade: null }
      ],
      "US-9002": [[37.8650, -83.5520, "Sample Creek SNA: Trailhead"]],
      "US-9003": [[37.7010, -83.7020, "Sample Ridge Preserve: Parking"]]
    } },
    "data/fers/US-KY.json": { rows: [
      { a: "US-9001", b: "US-9002", lat: 37.8420, lon: -83.5900, note: "edges may touch near the county road" }
    ] }
  };
  return {
    files: files,
    outlines: { "US-9001": lake, "US-9002": creek },          // what the KPCB adapter returns (assumed)
    trails: { "US-9001": [{ name: "Sample Lake Loop Trail", agency: "Kentucky Dept. of Fish & Wildlife Resources", geojson: trailLine }] },
    // a fetch() that serves the sample files; "kpcdata:" URLs fail when opts.kpcDataDown is set (to test the site-copy fallback)
    fakeFetch: function (opts) {
      opts = opts || {};
      return function (url) {
        var path = String(url).replace(/^kpcdata:\/\//, "").replace(/^\/?site\//, "");
        var down = opts.kpcDataDown && /^kpcdata:/.test(url);
        if (opts.log) opts.log.push(url);
        var body = !down && files[path];
        return Promise.resolve({ ok: !!body, status: body ? 200 : 404, json: function () { return Promise.resolve(JSON.parse(JSON.stringify(body))); } });
      };
    }
  };
}));
