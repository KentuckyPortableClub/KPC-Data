"""Dev-only test of the R-G9U unofficial-map path (re-uses the synthetic maps of synthetic_selftest.py)."""
import csv, json, shutil, subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
src = here / "synth"
root = here / "synth_unofficial"
shutil.rmtree(root, ignore_errors=True)
(root / "maps" / "unofficial").mkdir(parents=True)
shutil.copytree(src / "cache", root / "cache")
pins = json.loads((src / "pins.json").read_text())
pin = pins["US-90001"]
# US-90001: unofficial only -> UNOFFICIAL MAP in traced_unofficial/
shutil.copy(src / "maps/US-90001_synthetic.jpg", root / "maps/unofficial/US-90001_friends.jpg")
# US-90003: official + unofficial -> official used, unofficial SKIPPED, stale unofficial json withdrawn
shutil.copy(src / "maps/US-90003_synthetic.jpg", root / "maps/US-90003_synthetic.jpg")
shutil.copy(src / "maps/US-90003_synthetic.jpg", root / "maps/unofficial/US-90003_landtrust.jpg")
(root / "traced_unofficial").mkdir()
(root / "traced_unofficial/US-90003.json").write_text("{}")
# US-90002: unofficial, no roads on the picture -> NO FIT (same >=3 / <50 m / decoy gates)
shutil.copy(src / "maps/US-90002_synthetic.jpg", root / "maps/unofficial/US-90002_club.jpg")
U = dict(source_type="unofficial", source_url="https://example-friends.org/map.pdf", page=1,
         source_org="Friends of Synthetic Park (TEST)",
         notes="TEST: no agency GIS layer, no county parcel, no agency PDF (looked at agency site + county GIS)")
idx = [
    dict(U, ref="US-90001", name="synthetic US-90001"),
    dict(ref="US-90003", name="synthetic US-90003", agency="TEST agency", source_url="file://synthetic", page=1),
    dict(U, ref="US-90003", name="synthetic US-90003", source_org="Synthetic Land Trust (TEST)"),
    dict(U, ref="US-90002", name="synthetic US-90002"),
    dict(U, ref="US-90004", name="missing notes", notes=""),
    dict(U, ref="US-90005", name="alltrails url", source_url="https://www.alltrails.com/trail/x"),
    dict(U, ref="US-90006", name="google official", source_type="official", agency="X",
         source_url="https://www.google.com/maps/d/viewer?mid=1"),
    dict(U, ref="US-90007", name="banned org", source_org="AllTrails"),
    dict(U, ref="US-90008", name="bad type", source_type="semi-official"),
    dict(U, ref="US-90009", name="no org", source_org=""),
]
(root / "index.json").write_text(json.dumps(idx, indent=1))
(root / "pins.json").write_text(json.dumps({r["ref"]: pins.get(r["ref"], pin) for r in idx}))
subprocess.run([sys.executable, str(here.parent / "kpc_trace_picture.py"), "--base", str(root), "--all"], check=True)

def rep(p):
    return {r["ref"]: r for r in csv.DictReader(open(p))} if p.exists() else {}
off, un = rep(root / "traced/report.csv"), rep(root / "traced_unofficial/report.csv")
fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

r = un.get("US-90001", {})
check(r.get("status") == "UNOFFICIAL MAP", f"US-90001 unofficial drawn: {r.get('status')} fit {r.get('fit_m')} n {r.get('n_points')}")
f = root / "traced_unofficial/US-90001.json"
if f.exists():
    p = json.loads(f.read_text())["features"][0]["properties"]
    check(p["grade"] == "Approximate, from an unofficial map", "grade = " + p["grade"])
    check(p["status"] == "UNOFFICIAL MAP" and p["source_type"] == "unofficial", "status/source_type in GeoJSON")
    check(p["use_for_2fer"] is False and p["official"] is False, "use_for_2fer false, official false")
    check(p["source_org"] and p["notes"] and p["source_url"] and p["page"], "source_org / notes / URL / page recorded")
    check(p["fit_m"] < 50 and p["n_points"] >= 3, f"same gates: fit {p['fit_m']} m, n {p['n_points']}")
else:
    check(False, "traced_unofficial/US-90001.json written")
check(not (root / "traced/US-90001.json").exists() and "US-90001" not in off, "unofficial result not in official folder")
check(off.get("US-90003", {}).get("status") == "DRAWN", f"US-90003 official used: {off.get('US-90003', {}).get('status')}")
check(un.get("US-90003", {}).get("status") == "SKIPPED", "US-90003 unofficial row SKIPPED")
check(not (root / "traced_unofficial/US-90003.json").exists(), "stale unofficial US-90003 outline withdrawn")
check(un.get("US-90002", {}).get("status") == "NO FIT", f"US-90002 unofficial no roads -> {un.get('US-90002', {}).get('status')}")
for ref in ("US-90004", "US-90005", "US-90007", "US-90009"):
    check(un.get(ref, {}).get("status") == "ERROR", f"{ref} ERROR: {un.get(ref, {}).get('why')}")
check(off.get("US-90008", {}).get("status") == "ERROR", f"US-90008 ERROR: {off.get('US-90008', {}).get('why')}")
check(off.get("US-90006", {}).get("status") == "ERROR", f"US-90006 ERROR: {off.get('US-90006', {}).get('why')}")
print("ALL PASS" if not fails else f"{len(fails)} FAIL(S)")
sys.exit(1 if fails else 0)
