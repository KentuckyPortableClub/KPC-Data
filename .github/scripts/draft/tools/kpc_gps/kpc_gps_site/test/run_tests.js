// Plain-node tests for kpc-gps.js:  node test/run_tests.js
// Writes the made files to test/out/. If xmllint is found (PATH or $XMLLINT) every GPX is checked against
// the GPX 1.1 XSD (test/gpx.xsd, from topografix.com) and every KML against the OGC KML 2.2 XSD (test/kml22/).
"use strict";
const fs = require("fs"), path = require("path"), cp = require("child_process");
const K = require("../kpc-gps.js"), S = require("../sample-data.js");
const OUT = path.join(__dirname, "out");
fs.mkdirSync(OUT, { recursive: true });
let pass = 0, fail = 0;
function ok(cond, what) { if (cond) { pass++; } else { fail++; console.log("  FAIL: " + what); } }
function count(s, re) { return (s.match(re) || []).length; }
function unx(s) { return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&"); }

// tiny XML well-formedness check (tags balance, attributes quoted, entities known)
function wellFormed(xml) {
  const stack = []; let i = xml.indexOf("?>") + 2;
  const re = /<!\[CDATA\[[\s\S]*?\]\]>|<!--[\s\S]*?-->|<(\/?)([A-Za-z_][\w:.-]*)((?:\s+[\w:.-]+\s*=\s*(?:"[^"<]*"|'[^'<]*'))*)\s*(\/?)>|<|&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)/g;
  re.lastIndex = i; let m;
  while ((m = re.exec(xml))) {
    if (m[0] === "<") return "bad tag at " + m.index;
    if (m[0][0] === "&") return "bad entity at " + m.index;
    if (!m[2]) continue;
    if (m[1]) { if (stack.pop() !== m[2]) return "unbalanced </" + m[2] + "> at " + m.index; }
    else if (!m[4]) stack.push(m[2]);
  }
  return stack.length ? "unclosed " + stack.join(",") : null;
}
function gpxParts(gpx) {
  const wpts = [...gpx.matchAll(/<wpt lat="([^"]+)" lon="([^"]+)"><name>([^<]*)<\/name><desc>([^<]*)<\/desc>(?:<src>[^<]*<\/src>)?(?:<sym>([^<]*)<\/sym>)?/g)]
    .map(m => ({ lat: +m[1], lon: +m[2], name: unx(m[3]), desc: unx(m[4]), sym: m[5] ? unx(m[5]) : null }));
  const trks = [...gpx.matchAll(/<trk><name>([^<]*)<\/name><desc>([^<]*)<\/desc>(?:<type>([^<]*)<\/type>)?([\s\S]*?)<\/trk>/g)].map(m => ({
    name: unx(m[1]), desc: unx(m[2]), type: m[3],
    segs: [...m[4].matchAll(/<trkseg>([\s\S]*?)<\/trkseg>/g)].map(s => [...s[1].matchAll(/<trkpt lat="([^"]+)" lon="([^"]+)"\/>/g)].map(p => [+p[1], +p[2]]))
  }));
  const meta = unx((gpx.match(/<metadata>[\s\S]*?<desc>([^<]*)<\/desc>/) || [])[1] || "");
  const rte = [...gpx.matchAll(/<rtept lat="([^"]+)" lon="([^"]+)"><name>([^<]*)<\/name>/g)].map(m => ({ lat: +m[1], lon: +m[2], name: unx(m[3]) }));
  return { wpts, trks, meta, rte };
}
const written = [];
function save(r) { for (const k of ["gpx", "kml", "geojson"]) { fs.writeFileSync(path.join(OUT, r.files[k]), r[k]); written.push(path.join(OUT, r.files[k])); } }
function common(r, label, withFers) {
  const g = gpxParts(r.gpx);
  ok(g.meta.startsWith(K.NOTICE), label + ": GPX description starts with the SHORT notice");
  ok(/Data built: \d{4}-\d{2}-\d{2}/.test(g.meta) && g.meta.includes("Site: " + (siteWant || K.SITE_URL)), label + ": GPX description has build date + site link");
  ok(g.meta.includes(K.FER_NOTICE) === withFers, label + ": 2-fer notice in GPX only when 2-fers included (" + withFers + ")");
  ok(g.wpts.every(w => w.name.length <= 30), label + ": every wpt name <= 30 chars");
  ok(g.wpts.every(w => w.desc.length >= w.name.length - 1), label + ": full name in desc");
  ok(g.trks.every(t => t.segs.every(s => s.length >= 2)), label + ": every trkseg has points");
  ok(wellFormed(r.gpx) === null, label + ": GPX well formed " + (wellFormed(r.gpx) || ""));
  ok(wellFormed(r.kml) === null, label + ": KML well formed " + (wellFormed(r.kml) || ""));
  const kd = unx((r.kml.match(/<Document><name>[^<]*<\/name><open>1<\/open><description>([^<]*)<\/description>/) || [])[1] || "");
  ok(kd.startsWith(K.NOTICE), label + ": KML document description starts with the notice");
  ok(kd.includes(K.FER_NOTICE) === withFers, label + ": KML 2-fer notice only when included");
  ok(r.kml.includes("<Folder><name>Parking</name>") && r.kml.includes("<Folder><name>Trails</name>") && r.kml.includes("<Folder><name>Outline</name>"), label + ": KML has Parking/Trails/Outline folders");
  ok(r.kml.includes("<Folder><name>2-fers</name>") === withFers, label + ": KML 2-fers folder only when included");
  let gj = null; try { gj = JSON.parse(r.geojson); } catch (e) { }
  ok(gj && gj.type === "FeatureCollection" && gj.description.startsWith(K.NOTICE) && gj.kpc.notice === K.NOTICE, label + ": GeoJSON parses, notice first");
  ok(gj && (!!gj.kpc.fer_notice) === withFers, label + ": GeoJSON 2-fer notice only when included");
  const pts = gj ? gj.features.filter(f => f.geometry.type === "Point").length : -1;
  ok(pts === g.wpts.length, label + ": GeoJSON has the same points as the GPX (" + pts + " vs " + g.wpts.length + ")");
  ok(gj && gj.features.every(f => f.properties.label), label + ": every GeoJSON feature carries its label");
  for (const k of ["gpx", "kml", "geojson"]) ok(!/openstreetmap|overpass|geofabrik|google/i.test(r[k].replace(/KML \(Google Earth\)/g, "")), label + ": no OSM/Google in " + k);
  return { g, gj };
}

let siteWant = null;
(async () => {
  K.config({ fetch: S.fakeFetch(), dataUrl: p => "kpcdata://" + p, siteBase: "/site/", builtDate: "2026-10-31",
    outline: r => S.outlines[r] || null, trails: r => S.trails[r] || [] });
  const D = "2026-10-31";

  console.log("1. official park, 2-fers OFF (default)");
  let r = await K.park("US-9001", { area: "US-KY", fileDate: D }); save(r);
  let { g, gj } = common(r, "US-9001", false);
  ok(r.files.gpx === "KPC_US-9001_Sample-Lake-Wildlife-Management-Area_2026-10-31.gpx", "file name pattern KPC_<ref>_<short-name>_<date>.gpx: " + r.files.gpx);
  const pin = g.wpts.find(w => w.sym === "Flag, Green");
  ok(pin && pin.name === "US-9001 Sample Lake Wildlife" && pin.desc.startsWith("US-9001 Sample Lake Wildlife Management Area. " + K.PIN_LABEL), "pin: '<ref> <park name>' + POTA pin text");
  ok(pin && pin.desc.includes("Official boundary (Kentucky Dept. of Fish & Wildlife Resources)"), "pin desc says Official boundary (<agency>)");
  ok(g.wpts.filter(w => w.desc.startsWith("Parking (from KDFWR)")).length === 2 && g.wpts.filter(w => w.sym === "Parking Area").length === 3, "parking label 'Parking (from <agency>)' + Parking Area sym");
  ok(g.wpts.some(w => w.desc.startsWith("Boat ramp.") && w.sym === "Boat Ramp"), "Boat ramp label + Boat Ramp sym");
  ok(K.SITE_URL === "https://kentuckyportableclub.github.io/KPC-Links/" && g.meta.includes("Site: https://kentuckyportableclub.github.io/KPC-Links/"), "default site link is the KPC-Links page (ruling Oct 31 2026)");
  {
    const r9 = await K.park("US-9003", { area: "US-KY", fileDate: D }), g9 = gpxParts(r9.gpx);
    ok(g9.wpts.some(w => w.sym === "Parking Area" && w.desc.startsWith("Parking (from an official access list; check the agency\u2019s map before you go).")), "no agency named: exact ruled parking label, curly apostrophe");
    ok(r9.kml.includes("Parking (from an official access list; check the agency\u2019s map before you go)") && JSON.stringify(JSON.parse(r9.geojson)).includes("check the agency\u2019s map"), "ruled parking label also in KML + GeoJSON");
    // ruling Oct 31 2026 9:41 PM CT: access data's own agency only, never the outline's
    const ring = [[-84.0, 37.0], [-83.99, 37.0], [-83.99, 37.01], [-84.0, 37.01], [-84.0, 37.0]];
    const base = { ref: "US-9050", name: "Outline Agency Test Park", lat: 37.005, lon: -83.995,
      outline: { status: "official", agency: "Outline Only Agency", geojson: { type: "Polygon", coordinates: [ring] } } };
    const rA = await K.park(Object.assign({}, base, { access: [{ lat: 37.004, lon: -83.996, label: "Test: Parking" }] }), { fileDate: D }), gA = gpxParts(rA.gpx);
    const pA = gA.wpts.filter(w => w.sym === "Parking Area");
    ok(pA.length === 1 && pA[0].desc.startsWith(K.PARKING_NO_AGENCY + ".") && !rA.gpx.includes("Parking (from Outline Only Agency") && !rA.kml.includes("Parking (from Outline Only Agency") && !rA.geojson.includes("Parking (from Outline Only Agency"),
      "outline has an agency, access data none: new wording, outline agency NOT used (GPX/KML/GeoJSON)");
    ok(gA.trks.some(t => t.desc.startsWith("Official boundary (Outline Only Agency)")), "outline agency still labels the outline itself");
    const rB = await K.park(Object.assign({}, base, { accessAgency: "Access File Agency", access: [{ lat: 37.004, lon: -83.996, label: "Test: Parking" }] }), { fileDate: D });
    ok(gpxParts(rB.gpx).wpts.some(w => w.desc.startsWith("Parking (from Access File Agency)")), "access file's agency used when the row names none");
    const rC = await K.park(Object.assign({}, base, { accessAgency: "Access File Agency", access: [{ lat: 37.004, lon: -83.996, label: "Test: Parking", agency: "Row Agency" }] }), { fileDate: D });
    ok(gpxParts(rC.gpx).wpts.some(w => w.desc.startsWith("Parking (from Row Agency)")), "access row's agency wins over the file's");
    for (const [n, r] of [["A", rA], ["B", rB]]) { fs.writeFileSync(path.join(OUT, "agency" + n + "_" + r.files.gpx), r.gpx); written.push(path.join(OUT, "agency" + n + "_" + r.files.gpx)); fs.writeFileSync(path.join(OUT, "agency" + n + "_" + r.files.kml), r.kml); written.push(path.join(OUT, "agency" + n + "_" + r.files.kml)); }
    siteWant = "https://example.org/override/";
    const ro = await K.park("US-9003", { area: "US-KY", fileDate: D, siteUrl: siteWant });
    ok(gpxParts(ro.gpx).meta.includes("Site: https://example.org/override/"), "site link can still be overridden (opts.siteUrl)");
    siteWant = null;
  }
  ok(g.wpts.some(w => w.desc.startsWith("Entrance.") && w.sym === "Information"), "Entrance label + Information sym");
  ok(g.wpts.filter(w => w.desc.startsWith(K.NEARBY_LABEL)).length === 1, "outside point labelled 'Nearby public access, not the park's own'");
  ok(!g.wpts.some(w => /pull-?off/i.test(w.desc)), "ungraded pull-off candidate left out");
  ok(new Set(g.wpts.map(w => w.name)).size === g.wpts.length, "wpt names are unique (older Garmins merge same names)");
  ok(!g.wpts.some(w => /2-fer/.test(w.name)), "no 2-fer points when the box is off");
  const ob = g.trks.find(t => t.name === "US-9001 boundary (Official)");
  ok(!!ob, "outline track named '<ref> boundary (Official)'");
  ok(ob && ob.segs.length === 3, "one trkseg per ring (outer, hole, second piece): " + (ob && ob.segs.length));
  ok(ob && ob.segs.every(s => s[0][0] === s[s.length - 1][0] && s[0][1] === s[s.length - 1][1]), "every outline trkseg is closed");
  const npts = ob ? ob.segs.reduce((a, s) => a + s.length, 0) : 0;
  ok(npts <= 2000 && npts > 50, "outline simplified to <= 2000 points (" + npts + ", from 7303)");
  ok(ob && /^Official boundary \(Kentucky Dept\. of Fish & Wildlife Resources\)\..*Simplified to ~\d+ m for GPS units/.test(ob.desc), "outline desc: label + 'simplified to ~N m for GPS units'");
  ok(ob && !/Simplified to ~5 m/.test(ob.desc), "7303-point outline needed coarser than 5 m: " + (ob && ob.desc.match(/~\d+ m/)[0]));
  const tr = g.trks.find(t => t.type === "Trail");
  ok(tr && tr.desc.startsWith("Sample Lake Loop Trail (official line, Kentucky Dept. of Fish & Wildlife Resources)"), "trail label '<trail name> (official line, <agency>)'");
  ok(tr && !(tr.segs[0][0][0] === tr.segs[0].at(-1)[0] && tr.segs[0][0][1] === tr.segs[0].at(-1)[1]), "trail line kept open (not closed into a ring)");
  ok(r.kml.includes("<styleUrl>#official</styleUrl><MultiGeometry><Polygon>"), "KML official outline is a real Polygon");
  ok(/<Style id="official"><LineStyle><color>ff00ffff<\/color>/.test(r.kml), "KML official line is yellow (ff00ffff)");
  ok(gj.features.some(f => f.properties.kpc === "outline" && f.geometry.type === "MultiPolygon" && f.properties.label.startsWith("Official boundary")), "GeoJSON outline with label");

  console.log("2. same park, 2-fers ON");
  r = await K.park("US-9001", { area: "US-KY", fers: true, fileDate: D }); fs.writeFileSync(path.join(OUT, "fers_" + r.files.gpx), r.gpx); written.push(path.join(OUT, "fers_" + r.files.gpx));
  fs.writeFileSync(path.join(OUT, "fers_" + r.files.kml), r.kml); written.push(path.join(OUT, "fers_" + r.files.kml));
  ({ g, gj } = common(r, "US-9001+fers", true));
  const fer = g.wpts.filter(w => /^2-fer/.test(w.name));
  ok(fer.length === 1 && fer[0].desc.startsWith(K.FER_NOTICE), "2-fer spot present with the 2-fer notice word for word");

  console.log("3. approximate park");
  r = await K.park("US-9002", { area: "US-KY", fileDate: D }); save(r);
  ({ g, gj } = common(r, "US-9002", false));
  const ab = g.trks.find(t => t.name === "US-9002 boundary (Approximate)");
  ok(ab && ab.desc.startsWith("Approximate outline (traced from the agency's picture map)"), "approximate label 'Approximate outline (<why>)'");
  ok(ab && /Simplified to ~5 m/.test(ab.desc), "small outline simplified at 5 m first");
  ok(ab && ab.segs.every(s => s[0][0] === s.at(-1)[0] && s[0][1] === s.at(-1)[1]), "approximate trkseg closed");
  ok(r.kml.includes("<styleUrl>#dash</styleUrl>") && count(r.kml, /<LineString>/g) > 50, "KML approximate drawn dashed (" + count(r.kml, /<LineString>/g) + " dashes)");
  ok(g.wpts.some(w => w.desc.startsWith("Trailhead.") && w.sym === "Trail Head"), "Trailhead label + Trail Head sym");

  console.log("4. pin-only park");
  r = await K.park("US-9003", { area: "US-KY", fileDate: D }); save(r);
  ({ g, gj } = common(r, "US-9003", false));
  ok(g.trks.length === 0 && !r.kml.includes("<Polygon>") && !gj.features.some(f => /Polygon/.test(f.geometry.type)), "pin-only: no outline drawn anywhere");
  ok(g.wpts[0].desc.includes(K.NO_OUTLINE) && r.kml.includes(K.NO_OUTLINE) && r.geojson.includes(K.NO_OUTLINE), "pin-only: 'No official outline yet' in GPX, KML, GeoJSON");
  ok(g.wpts.length === 2, "pin-only still has pin + parking");

  console.log("5. trip");
  const stops = ["US-9003", "US-9001", { name: "Gas stop", lat: 37.75, lon: -83.66 }, "US-9002"];
  r = await K.trip(stops, { area: "US-KY", fileDate: D }); save(r);
  ({ g, gj } = common(r, "trip", false));
  ok(r.files.gpx === "KPC_trip_2026-10-31.gpx", "trip file name KPC_trip_<date>.gpx");
  ok(g.rte.length === 4 && g.rte.map(x => x.name.split(" ")[1]).join() === "US-9003,US-9001,Gas,US-9002", "rte keeps the stop order: " + g.rte.map(x => x.name).join(" | "));
  ok(count(r.gpx, /<rte>/g) === 1 && r.gpx.indexOf("<rte>") > r.gpx.lastIndexOf("<wpt ") && r.gpx.indexOf("<rte>") < r.gpx.indexOf("<trk>"), "GPX order wpt, rte, trk");
  ok(g.trks.filter(t => / boundary /.test(t.name)).length === 2, "trip has both outlines (box on by default)");
  r = await K.trip(stops, { area: "US-KY", fileDate: D, outlines: false });
  ok(!/<trk><name>[^<]* boundary/.test(r.gpx) && !r.kml.includes("<Polygon>"), "trip outlines left out when the box is off");

  console.log("6. data loading: KPC-Data first, then the site copy");
  K._clearCache(); let log = [];
  K.config({ fetch: S.fakeFetch({ log }) });
  await K.park("US-9001", { area: "US-KY" });
  ok(log[0].startsWith("kpcdata://") && !log.some(u => u.startsWith("/site/")), "reads KPC-Data first: " + log[0]);
  K._clearCache(); log = [];
  K.config({ fetch: S.fakeFetch({ log, kpcDataDown: true }) });
  r = await K.park("US-9001", { area: "US-KY" });
  ok(log.includes("/site/data/access/US-KY.json") && /Parking \(from KDFWR\)/.test(r.gpx), "falls back to the site copy when KPC-Data fails");
  K._clearCache();
  K.config({ fetch: () => Promise.reject(new Error("offline")) });
  r = await K.park({ ref: "US-9009", name: "Given Park", lat: 37.5, lon: -84 }, {});
  ok(/US-9009 Given Park/.test(r.gpx) && r.gpx.includes(K.NO_OUTLINE), "works with no network when the card passes the park in");

  console.log("7. simplifier edge cases");
  const tri = [[[[-84, 37], [-84.001, 37], [-84, 37.001], [-84, 37]]]];
  ok(K.simplifyOutline(tri).polys[0][0].length === 4, "tiny triangle kept");
  const many = []; for (let i = 0; i < 1500; i++) many.push([[[-84 + i * 0.01, 37], [-84 + i * 0.01 + 0.001, 37], [-84 + i * 0.01, 37.001], [-84 + i * 0.01, 37]]]);
  const sm = K.simplifyOutline(many);
  ok(sm.points <= 2000 && sm.dropped > 0, "1500 small pieces: cut to <= 2000 points, smallest left out (" + sm.points + " pts, " + sm.dropped + " dropped)");
  ok(K.readAccess({ ap: { "US-1": [[37.1, -84.2, "X: Parking"]] } })["US-1"].length === 1, "reads Kentucky 'ap' shape");
  ok(K.readAccess({ type: "FeatureCollection", features: [{ type: "Feature", properties: { ref: "US-2", label: "Y: Entrance", outside: true }, geometry: { type: "Point", coordinates: [-84, 37] } }] })["US-2"][0].outside, "reads GeoJSON access points + outside flag");

  // xmllint schema checks
  const xl = process.env.XMLLINT || "xmllint";
  let have = false; try { cp.execFileSync(xl, ["--version"], { stdio: "ignore" }); have = true; } catch (e) { }
  if (have) {
    console.log("8. xmllint schema checks (" + xl + ")");
    const all = fs.readdirSync(OUT).map(f => path.join(OUT, f));
    for (const f of all.filter(f => f.endsWith(".gpx"))) {
      let res; try { cp.execFileSync(xl, ["--noout", "--schema", path.join(__dirname, "gpx.xsd"), f], { stdio: "pipe" }); res = true; } catch (e) { res = false; console.log(String(e.stderr)); }
      ok(res, "GPX 1.1 XSD: " + path.basename(f)); if (res) console.log("  " + path.basename(f) + " validates (GPX 1.1 XSD)");
    }
    for (const f of all.filter(f => f.endsWith(".kml"))) {
      let res; try { cp.execFileSync(xl, ["--noout", "--schema", path.join(__dirname, "kml22", "ogckml22.xsd"), f], { stdio: "pipe" }); res = true; } catch (e) { res = false; console.log(String(e.stderr)); }
      ok(res, "KML 2.2 XSD: " + path.basename(f)); if (res) console.log("  " + path.basename(f) + " validates (OGC KML 2.2 XSD)");
    }
  } else console.log("8. xmllint not found: schema checks SKIPPED (set XMLLINT=/path/to/xmllint)");

  console.log((fail ? "FAIL" : "PASS") + ": " + pass + " passed, " + fail + " failed");
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log("FAIL: crashed", e); process.exit(2); });
