#!/usr/bin/env python3
"""kpc_missed_fers - Missed 2-fer finder (KPC chat 10 spec, Oct 31 2026).

Reads POTA's public activation history, finds pairs of nearby POTA parks that
several different activators activated on the same UTC day, and lists the pairs
that the club's 2-fer lists do not have yet.  LEADS ONLY - it never adds a 2-fer.

Callsigns are used only in memory (and in the download cache) to count distinct
people. They never appear in any file written to --out.

Python 3.12, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import defaultdict
from itertools import combinations

# ---------------------------------------------------------------- thresholds
# Grey areas G-M1 / G-M2 are for Brandon: all thresholds are constants AND flags.
MIN_ACTIVATORS = 3        # G-M1: distinct callsigns per pair
MIN_DATES = 3             # G-M1: distinct UTC dates per pair
MAX_PIN_KM = 15.0         # G-M2: max distance between POTA pins
MAX_OUTLINE_KM = 2.0      # outlines may be this far apart instead
ROVE_PARKS = 5            # a (callsign, date) with >= this many parks is a rove day
MAX_MINUTES = 50

API = "https://api.pota.app"
URL_PARKS = API + "/location/parks/{loc}"
URL_ACTS = API + "/park/activations/{ref}?count=all"
URL_LOCATIONS = API + "/programs/locations"
MIN_INTERVAL_S = 2.0      # per host
RETRIES = 3

ROUTE_RETEST = "fers-retest"
ROUTE_MAP = "check-official-map"
ROUTE_TRAIL = "trail-river"

# POTA park reference: PREFIX-NNNN(N). WWFF uses xxFF-NNNN -> excluded.
POTA_REF = re.compile(r"^([A-Z0-9]{1,4})-(\d{4,6})$")
REF_IN_TEXT = re.compile(r"\b([A-Z0-9]{1,4}-\d{4,6})\b")
# park TYPE (parkinfo column 2) may say trail/river broadly; the NAME must look like a trail/river park
# itself ("Green River State Forest" or "Barren River Lake State Park" are not river parks).
TRAIL_RIVER_TYPE = re.compile(r"\b(trail|trails|river|rivers|greenway|byway|canal|waterway)\b", re.I)
TRAIL_RIVER_NAME = re.compile(r"\b(trail|trails|greenway|byway|canal|water ?trail)\b|scenic river|wild river|"
                              r"national river|\briver\s*$|\brivers\s*$", re.I)

FORBIDDEN_HOSTS = ("openstreetmap", "overpass", "geofabrik", "google.", "googleapis.com/maps",
                   "alltrails", "gaiagps", "strava", "tripadvisor", "yelp", "wikipedia",
                   "protectedplanet", "wdpa", "unep-wcmc")

EXIT_DONE, EXIT_TIME = 0, 3


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")


def is_pota_ref(ref) -> bool:
    if not isinstance(ref, str):
        return False
    m = POTA_REF.match(ref.strip().upper())
    return bool(m) and not m.group(1).endswith("FF")


def country(ref: str) -> str:
    return ref.split("-", 1)[0].upper()


def haversine_km(a, b) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(h)))


def person_id(callsign: str) -> str:
    """Pseudonymous id for counting distinct people: the cache never stores callsigns either.
    W1AW, W1AW/P and VE3/W1AW count as the same person (longest part of the call)."""
    base = max(str(callsign).upper().strip().split("/"), key=len)
    return "p" + hashlib.sha256(("kpc-missed-fers:" + base).encode()).hexdigest()[:12]


def pair_key(a: str, b: str):
    return (a, b) if a <= b else (b, a)


# ---------------------------------------------------------------- HTTP
class HostResting(Exception):
    pass


class Fetcher:
    """Polite JSON fetcher: robots.txt, 1 req / 2 s per host, UA, 429/503 back-off."""

    def __init__(self, contact: str, log):
        self.ua = f"KPC park tools ({contact})"
        self.last = {}
        self.robots = {}
        self.resting = set()
        self.log = log

    def _wait(self, host):
        gap = time.monotonic() - self.last.get(host, -1e9)
        if gap < MIN_INTERVAL_S:
            time.sleep(MIN_INTERVAL_S - gap)
        self.last[host] = time.monotonic()

    def _raw(self, url, timeout=60):
        host = urllib.parse.urlsplit(url).netloc
        self._wait(host)
        req = urllib.request.Request(url, headers={"User-Agent": self.ua, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()

    def allowed(self, url) -> bool:
        parts = urllib.parse.urlsplit(url)
        host = parts.netloc
        if any(f in host for f in FORBIDDEN_HOSTS):
            return False
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                _, body = self._raw(f"{parts.scheme}://{host}/robots.txt", timeout=30)
                rp.parse(body.decode("utf-8", "replace").splitlines())
            except urllib.error.HTTPError as e:
                if 400 <= e.code < 500:      # RFC 9309: 4xx (api.pota.app gives 403) = no rules
                    rp.allow_all = True
                else:                         # 5xx = assume disallowed this run
                    rp.disallow_all = True
                    self.log(f"robots.txt for {host}: HTTP {e.code}, host treated as closed")
            except Exception as e:  # noqa: BLE001
                rp.disallow_all = True
                self.log(f"robots.txt for {host} unreachable ({e}); host treated as closed")
            self.robots[host] = rp
        return self.robots[host].can_fetch(self.ua, url)

    def get_json(self, url):
        host = urllib.parse.urlsplit(url).netloc
        if host in self.resting:
            raise HostResting(host)
        if not self.allowed(url):
            raise PermissionError(f"blocked by robots.txt or source rules: {url}")
        delay = 10
        for attempt in range(RETRIES + 1):
            try:
                _, body = self._raw(url)
                return json.loads(body.decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (401, 403) and "auth" in (e.read() or b"").decode("utf-8", "replace").lower():
                    raise PermissionError("needs sign-in") from e
                if e.code in (429, 503, 502, 504):
                    if attempt == RETRIES:
                        self.resting.add(host)
                        self.log(f"{host}: HTTP {e.code} {RETRIES} retries, host resting for this run")
                        raise HostResting(host) from e
                    ra = e.headers.get("Retry-After") if e.headers else None
                    wait = int(ra) if ra and ra.isdigit() else delay
                    self.log(f"{host}: HTTP {e.code}, waiting {wait}s (retry {attempt + 1}/{RETRIES})")
                    time.sleep(min(wait, 300))
                    delay *= 2
                    continue
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt == RETRIES:
                    raise
                self.log(f"{host}: network error {e}, retry {attempt + 1}/{RETRIES}")
                time.sleep(delay)
                delay *= 2


class FixtureFetcher:
    """Offline fetcher for --selftest: maps API URLs to files in tests/fixture/pota."""

    def __init__(self, root):
        self.root = root
        self.calls = 0

    def get_json(self, url):
        self.calls += 1
        if url == URL_LOCATIONS:
            p = os.path.join(self.root, "locations.json")
        elif "/location/parks/" in url:
            p = os.path.join(self.root, "parks", url.rsplit("/", 1)[1] + ".json")
        else:
            ref = url.split("/park/activations/")[1].split("?")[0]
            p = os.path.join(self.root, "activations", ref + ".json")
        if not os.path.exists(p):
            raise urllib.error.HTTPError(url, 404, "Not Found (fixture)", None, None)
        with open(p, encoding="utf-8") as f:
            return json.load(f)


# ---------------------------------------------------------------- club files
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_pins(parkinfo_dir, log):
    """parkinfo/US-XX.json {"parks": {ref: [name, website, type, access, access2, lat, lon, ...]}},
    CA.json same (col 10 = province); world rows [ref, name, lat, lon] (data/pota/t/*.json)."""
    pins = {}
    if not parkinfo_dir:
        return pins
    files = sorted(glob.glob(os.path.join(parkinfo_dir, "*.json")))
    world = os.path.join(os.path.dirname(os.path.abspath(parkinfo_dir)), "pota", "t")
    files += sorted(glob.glob(os.path.join(world, "*.json")))
    for p in files:
        try:
            d = load_json(p)
        except Exception as e:  # noqa: BLE001
            log(f"pins: cannot read {p}: {e}")
            continue
        parks = d.get("parks") if isinstance(d, dict) else d
        rows = parks.items() if isinstance(parks, dict) else (
            ((r[0], r[1:]) for r in parks if isinstance(r, list) and r) if isinstance(parks, list) else [])
        for ref, row in rows:
            try:
                if isinstance(row, list) and len(row) >= 7 and isinstance(parks, dict):
                    name, typ, lat, lon = row[0], row[2], float(row[5]), float(row[6])
                elif isinstance(row, list) and len(row) >= 3:      # [name, lat, lon]
                    name, typ, lat, lon = row[0], "", float(row[1]), float(row[2])
                elif isinstance(row, dict):
                    name = row.get("name", "")
                    typ = row.get("type", "")
                    lat, lon = float(row.get("lat", row.get("latitude"))), float(row.get("lon", row.get("longitude")))
                else:
                    continue
                pins[str(ref).upper()] = {"name": name or "", "type": typ or "", "lat": lat, "lon": lon}
            except (TypeError, ValueError):
                continue
    return pins


def load_keys(keys_dir, log):
    """keys: data/{us,ca,world}-key/*.json {"parks": {ref: {"g": official|approximate|pin, "m": [...], ...}}}.
    Optional (not in the documented shape): "bbox": [w, s, e, n] -> used for the 2 km outline test."""
    keys = {}
    if not keys_dir:
        return keys
    for sub in ("us-key", "ca-key", "world-key"):
        for p in sorted(glob.glob(os.path.join(keys_dir, sub, "*.json"))):
            try:
                d = load_json(p)
            except Exception as e:  # noqa: BLE001
                log(f"keys: cannot read {p}: {e}")
                continue
            for ref, v in (d.get("parks") or {}).items():
                if isinstance(v, dict):
                    keys[ref.upper()] = v
    return keys


def outline_status(keys, ref):
    g = str((keys.get(ref) or {}).get("g", "pin")).lower()
    return g if g in ("official", "approximate", "pin") else "pin"


def bbox_km(b1, b2):
    """Gap in km between two [w, s, e, n] boxes (0 if they overlap)."""
    try:
        w1, s1, e1, n1 = map(float, b1)
        w2, s2, e2, n2 = map(float, b2)
    except (TypeError, ValueError):
        return None
    lat_gap = max(0.0, s2 - n1, s1 - n2)
    lon_gap = max(0.0, w2 - e1, w1 - e2)
    mid = math.radians((s1 + n1 + s2 + n2) / 4)
    return round(math.hypot(lat_gap * 111.32, lon_gap * 111.32 * math.cos(mid)), 3)


def extract_ref_pairs(obj, out: set):
    """Lenient: find ref pairs in any plausible JSON shape (the fers files' exact shape is not
    known to the builder). Rules:
      * one string holding >= 2 refs ("US-0050+US-10105", "US-0050 / US-10105")      -> all pairs
      * a list whose direct string items are >= 2 refs (["US-0050", "US-10105"])      -> all pairs
      * a dict whose direct string values are >= 2 refs ({"a": .., "b": ..})          -> all pairs
      * a dict keyed by a ref whose value names other refs ({"US-0050": ["US-10105"]}) -> key x each
      * a dict with one direct ref and child lists of refs / of dicts with a ref       -> owner x each
    Every nested level is searched."""
    def refs_in_str(s):
        return [r for r in REF_IN_TEXT.findall(s.upper()) if is_pota_ref(r)]

    def add_all(refs):
        refs = sorted(set(refs))
        if 2 <= len(refs) <= 12:
            for a, b in combinations(refs, 2):
                out.add(pair_key(a, b))

    def direct_refs(v):
        if isinstance(v, str):
            return refs_in_str(v)
        if isinstance(v, dict):
            return [r for x in v.values() if isinstance(x, str) for r in refs_in_str(x)]
        if isinstance(v, list):
            res = []
            for x in v:
                if isinstance(x, str):
                    res += refs_in_str(x)
                elif isinstance(x, dict):
                    res += [r for y in x.values() if isinstance(y, str) for r in refs_in_str(y)][:1]
            return res
        return []

    if isinstance(obj, str):
        add_all(refs_in_str(obj))
    elif isinstance(obj, list):
        add_all([r for x in obj if isinstance(x, str) for r in refs_in_str(x)])
        for x in obj:
            if not isinstance(x, str):
                extract_ref_pairs(x, out)
    elif isinstance(obj, dict):
        own = [r for x in obj.values() if isinstance(x, str) for r in refs_in_str(x)]
        add_all(own)
        for k, v in obj.items():
            ku = str(k).upper()
            if is_pota_ref(ku):
                for r in direct_refs(v):
                    if r != ku:
                        out.add(pair_key(ku, r))
            if len(set(own)) == 1 and isinstance(v, list):
                for r in direct_refs(v):
                    if r != own[0]:
                        out.add(pair_key(own[0], r))
            if not isinstance(v, str):
                extract_ref_pairs(v, out)


def load_known_pairs(fers_dir, log):
    """Every pair in any JSON under --fers: live lists (<area>.json), missing-*.json,
    known-answers.json (YES and NO), dropped / checked-NO rows (any file, any row)."""
    pairs, per_file = set(), {}
    if not fers_dir:
        return pairs, per_file
    for p in sorted(glob.glob(os.path.join(fers_dir, "**", "*.json"), recursive=True)):
        s = set()
        try:
            extract_ref_pairs(load_json(p), s)
        except Exception as e:  # noqa: BLE001
            log(f"fers: cannot read {p}: {e}")
            continue
        per_file[os.path.relpath(p, fers_dir)] = s
        pairs |= s
    return pairs, per_file


# ---------------------------------------------------------------- run
class Run:
    def __init__(self, args, fetcher, clock=time.monotonic):
        self.a = args
        self.f = fetcher
        self.clock = clock
        self.t0 = clock()
        self.out = os.path.abspath(args.out)
        self.work = os.path.join(self.out, "work")
        os.makedirs(self.work, exist_ok=True)
        self.cache = os.path.abspath(args.cache) if args.cache else os.path.join(self.work, "cache")
        os.makedirs(os.path.join(self.cache, "activations"), exist_ok=True)
        os.makedirs(os.path.join(self.cache, "parks"), exist_ok=True)
        self.logf = open(os.path.join(self.out, "run.log"), "a", encoding="utf-8")
        self.problems = []
        self.state_path = os.path.join(self.out, "state.json")
        self.state = {"areas_listed": [], "parks_done": [], "read_date": today()}
        if args.resume and os.path.exists(self.state_path):
            try:
                self.state = load_json(self.state_path)
            except Exception as e:  # noqa: BLE001
                self.log(f"state.json unreadable ({e}), starting fresh")
        self.done = set(self.state.get("parks_done", []))

    def log(self, msg):
        line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
        self.logf.write(line + "\n")
        self.logf.flush()
        if not self.a.quiet:
            print(line, file=sys.stderr)

    def problem(self, item, reason):
        self.problems.append({"item": item, "reason": reason, "read_date": today()})
        self.log(f"PROBLEM {item}: {reason}")

    def time_left(self):
        return (self.clock() - self.t0) < self.a.max_minutes * 60

    def save_state(self):
        self.state["parks_done"] = sorted(self.done)
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=1)
        os.replace(tmp, self.state_path)

    # ---- step 0: areas
    def areas(self):
        if self.a.areas:
            return [x.strip().upper() for x in self.a.areas.split(",") if x.strip()]
        try:
            progs = self.f.get_json(URL_LOCATIONS)
        except Exception as e:  # noqa: BLE001
            self.problem("areas", f"cannot read {URL_LOCATIONS}: {e}")
            return []
        locs = []
        for p in progs:
            for ent in p.get("entities") or []:
                for loc in ent.get("locations") or []:
                    if loc.get("parks"):
                        locs.append(loc["descriptor"])
        us = sorted(x for x in locs if x.startswith("US-"))
        ca = sorted(x for x in locs if x.startswith("CA-"))
        rest = [x for x in locs if not x.startswith(("US-", "CA-"))]
        return us + ca + rest

    # ---- step 1: park list
    def park_list(self, area):
        path = os.path.join(self.cache, "parks", f"{area}.json")
        if area in self.state.get("areas_listed", []) and os.path.exists(path):
            return load_json(path)
        data = self.f.get_json(URL_PARKS.format(loc=urllib.parse.quote(area)))
        if not isinstance(data, list):
            raise ValueError("park list is not a list")
        keep = ("reference", "name", "latitude", "longitude", "locationDesc", "attempts", "activations")
        data = [{k: p.get(k) for k in keep} for p in data if isinstance(p, dict)]   # drop free-text notes
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.state.setdefault("areas_listed", []).append(area)
        return data

    # ---- step 2: activation history (cached by activation count)
    def activations(self, ref, count_key):
        path = os.path.join(self.cache, "activations", f"{ref}.json")
        if os.path.exists(path):
            try:
                c = load_json(path)
                if c.get("count_key") == count_key or ref in self.done:
                    return c["rows"], False
            except Exception:  # noqa: BLE001
                pass
        rows = self.f.get_json(URL_ACTS.format(ref=urllib.parse.quote(ref)))
        if not isinstance(rows, list):
            raise ValueError("activation history is not a list")
        slim = []
        for r in rows:
            cs, d = r.get("activeCallsign"), str(r.get("qso_date", ""))
            if cs and re.fullmatch(r"\d{8}", d):
                slim.append([person_id(cs), d])
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"ref": ref, "count_key": count_key, "read_date": today(), "rows": slim}, f)
        os.replace(path + ".tmp", path)
        return slim, True

    def go(self):
        areas = self.areas()
        parks = {}          # ref -> {name, lat, lon, area, location}
        work_left = False
        pins = load_pins(self.a.parkinfo, self.log)
        keys = load_keys(self.a.keys, self.log)
        known, per_file = load_known_pairs(self.a.fers, self.log)
        self.log(f"areas={len(areas)} pins={len(pins)} keys={len(keys)} known_pairs={len(known)}")

        todo = []
        for area in areas:
            if not self.time_left():
                work_left = True
                break
            try:
                plist = self.park_list(area)
            except HostResting:
                work_left = True
                self.problem(area, "host resting (429/503), park list not read")
                continue
            except Exception as e:  # noqa: BLE001
                self.problem(area, f"park list not read: {e}")
                continue
            for p in plist:
                ref = str(p.get("reference", "")).upper()
                if not is_pota_ref(ref) or ref in parks:
                    continue
                n_act = int(p.get("activations") or 0)
                n_att = int(p.get("attempts") or 0)
                parks[ref] = {"name": p.get("name", ""), "lat": p.get("latitude"), "lon": p.get("longitude"),
                              "area": area, "count_key": f"{n_att}/{n_act}", "n_act": n_act}
                if n_act > 0:
                    todo.append(ref)
        if self.a.limit:
            todo = todo[: self.a.limit]
        self.save_state()

        hist = {}
        fetched = cached = 0
        for i, ref in enumerate(todo):
            if not self.time_left():
                work_left = True
                self.log(f"time is up after {i}/{len(todo)} parks")
                break
            try:
                rows, new = self.activations(ref, parks[ref]["count_key"])
                hist[ref] = rows
                fetched += new
                cached += not new
                self.done.add(ref)
                if new and fetched % 25 == 0:
                    self.save_state()
                    self.log(f"{i + 1}/{len(todo)} parks ({fetched} read, {cached} from cache)")
            except HostResting:
                work_left = True
                self.problem(ref, "host resting (429/503), history not read")
            except Exception as e:  # noqa: BLE001
                self.problem(ref, f"history not read: {e}")
        self.save_state()
        self.log(f"histories: {fetched} read, {cached} from cache, {len(todo) - len(hist)} missing")

        result = self.compute(parks, hist, pins, keys, known, per_file)
        self.write(result, areas, partial=work_left)
        self.state["finished"] = not work_left
        self.save_state()
        return EXIT_TIME if work_left else EXIT_DONE

    # ---- steps 3-6
    def compute(self, parks, hist, pins, keys, known, per_file):
        a = self.a
        index = defaultdict(set)                       # (callsign, date) -> parks
        for ref, rows in hist.items():
            for cs, d in rows:
                index[(cs, d)].add(ref)
        rove_days = sum(1 for v in index.values() if len(v) >= a.rove_parks)

        acts = defaultdict(set)                        # pair -> callsigns   (memory only)
        dates = defaultdict(set)                       # pair -> dates
        for (cs, d), refs in index.items():
            if len(refs) < 2 or len(refs) >= a.rove_parks:
                continue
            for x, y in combinations(sorted(refs), 2):
                acts[(x, y)].add(cs)
                dates[(x, y)].add(d)
        del index

        listed, below = [], defaultdict(int)
        raw_known_seen = 0
        for pk in acts:
            x, y = pk
            n_cs, n_d = len(acts[pk]), len(dates[pk])
            if pk in known:
                if n_cs >= a.min_activators:
                    raw_known_seen += 1
                below["known (already ours)"] += 1
                continue
            if country(x) != country(y):
                below["different countries"] += 1
                continue
            if n_cs < a.min_activators or n_d < a.min_dates:
                below["below thresholds"] += 1
                continue
            px, py = self.pin(x, parks, pins), self.pin(y, parks, pins)
            if px is None or py is None:
                below["no pin"] += 1
                self.problem(f"{x}+{y}", "no pin for one park; pair skipped")
                continue
            pin_km = round(haversine_km(px, py), 2)
            gx, gy = outline_status(keys, x), outline_status(keys, y)
            okm = None
            bx, by = (keys.get(x) or {}).get("bbox"), (keys.get(y) or {}).get("bbox")
            if bx and by and "official" in (gx, gy):
                okm = bbox_km(bx, by)
            near_pin = pin_km <= a.max_pin_km
            near_outline = okm is not None and okm <= a.max_outline_km
            if not (near_pin or near_outline):
                below["too far apart"] += 1
                continue
            tr = [r for r in (x, y) if self.is_trail_river(r, parks, pins)]
            if tr:
                route = ROUTE_TRAIL
            elif gx == "official" and gy == "official":
                route = ROUTE_RETEST
            else:
                route = ROUTE_MAP
            ds = sorted(dates[pk])
            fd, ld = f"{ds[0][:4]}-{ds[0][4:6]}-{ds[0][6:]}", f"{ds[-1][:4]}-{ds[-1][4:6]}-{ds[-1][6:]}"
            how = f"pins {pin_km} km apart" if near_pin else f"outlines {okm} km apart (pins {pin_km} km)"
            why = (f"{n_cs} different activators activated both parks on the same UTC day, on {n_d} different "
                   f"dates ({fd} to {ld}); {how}; not in any club 2-fer list. ")
            why += {ROUTE_TRAIL: f"{' and '.join(tr)} is a trail/river park: needs the 100 ft trail rule.",
                    ROUTE_RETEST: "Both parks have official outlines: re-test on the 2-fer line.",
                    ROUTE_MAP: "An outline is approximate or pin-only: check the official map."}[route]
            listed.append({
                "a": x, "b": y,
                "a_name": self.name(x, parks, pins), "b_name": self.name(y, parks, pins),
                "area": parks.get(x, {}).get("area") or parks.get(y, {}).get("area", ""),
                "activators": n_cs, "dates": n_d, "first_date": fd, "last_date": ld,
                "pin_km": pin_km, "outline_km": okm, "a_outline": gx, "b_outline": gy,
                "route": route,
                "source_url": URL_ACTS.format(ref=x) + " ; " + URL_ACTS.format(ref=y),
                "read_date": today(), "why": why,
            })
        listed.sort(key=lambda r: (-r["activators"], -r["dates"], r["a"], r["b"]))

        # acceptance helper: known pairs with >= MIN_ACTIVATORS joint activators seen in raw counts
        live = set()
        for fname, s in per_file.items():
            base = os.path.basename(fname)
            if re.fullmatch(r"[A-Z]{2}(-[A-Z0-9]{1,3})?\.json", base):
                live |= s
        seen = {pk for pk in live if len(acts.get(pk, ())) >= a.min_activators}
        stats = {"parks_with_history": len(hist), "rove_days_dropped": rove_days,
                 "pairs_raw": len(acts), "known_pairs_total": len(known),
                 "live_list_pairs_seen_with_3plus": len(seen), "rejected": dict(below),
                 "known_pairs_seen_any_list": raw_known_seen}
        # tool's own log of below-threshold pairs (no callsigns, counts only)
        with open(os.path.join(self.work, "below_threshold.json"), "w", encoding="utf-8") as f:
            json.dump([{"a": x, "b": y, "activators": len(acts[(x, y)]), "dates": len(dates[(x, y)])}
                       for (x, y) in sorted(acts) if (x, y) not in known
                       and (len(acts[(x, y)]) < a.min_activators or len(dates[(x, y)]) < a.min_dates)],
                      f, indent=0)
        return listed, stats

    @staticmethod
    def pin(ref, parks, pins):
        if ref in pins:
            return pins[ref]["lat"], pins[ref]["lon"]
        p = parks.get(ref)
        if p and p.get("lat") is not None and p.get("lon") is not None:
            return float(p["lat"]), float(p["lon"])
        return None

    @staticmethod
    def name(ref, parks, pins):
        return (pins.get(ref) or {}).get("name") or (parks.get(ref) or {}).get("name", "")

    @staticmethod
    def is_trail_river(ref, parks, pins):
        typ = (pins.get(ref) or {}).get("type", "") or ""
        nm = Run.name(ref, parks, pins)
        return bool(TRAIL_RIVER_TYPE.search(str(typ)) or TRAIL_RIVER_NAME.search(str(nm)))

    def write(self, result, areas, partial):
        listed, stats = result
        rd = today()
        doc = {"tool": "kpc_missed_fers", "read_date": rd, "partial": partial,
               "note": "Leads only. The official outlines and the club's 2-fer rules decide.",
               "thresholds": {"min_activators": self.a.min_activators, "min_dates": self.a.min_dates,
                              "max_pin_km": self.a.max_pin_km, "max_outline_km": self.a.max_outline_km,
                              "rove_parks": self.a.rove_parks},
               "source_url": API, "pairs": listed, "problems": self.problems}
        with open(os.path.join(self.out, "missed_fers.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False)

        by = defaultdict(lambda: defaultdict(int))
        for r in listed:
            by[r["area"]][r["route"]] += 1
        routes = [ROUTE_RETEST, ROUTE_MAP, ROUTE_TRAIL]
        L = [f"# Missed 2-fer leads ({rd}){' - PARTIAL, run not finished' if partial else ''}", "",
             "Leads only: the official outlines and the club's 2-fer rules decide. No callsigns are kept here.",
             "", f"Areas asked: {len(areas)}. Parks with history: {stats['parks_with_history']}. "
             f"Raw same-day pairs: {stats['pairs_raw']}. Rove days dropped: {stats['rove_days_dropped']}. "
             f"Pairs listed: {len(listed)}. Problems: {len(self.problems)}.", "",
             f"Known live-list pairs seen in raw counts with >= {self.a.min_activators} activators: "
             f"{stats['live_list_pairs_seen_with_3plus']} (all excluded from the list).", "",
             "Rejected: " + (", ".join(f"{k} {v}" for k, v in sorted(stats["rejected"].items())) or "none"), "",
             "## Counts per area and route", "", "| area | " + " | ".join(routes) + " | total |",
             "|---|" + "---|" * (len(routes) + 1)]
        for area in sorted(by):
            L.append(f"| {area} | " + " | ".join(str(by[area][r]) for r in routes) + f" | {sum(by[area].values())} |")
        tot = defaultdict(int)
        for r in listed:
            tot[r["route"]] += 1
        L.append("| **all** | " + " | ".join(str(tot[r]) for r in routes) + f" | {len(listed)} |")
        L += ["", "## Top 50 pairs by activators", "",
              "| # | a | b | names | area | activators | dates | pin km | outlines | route |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(listed[:50], 1):
            L.append(f"| {i} | {r['a']} | {r['b']} | {r['a_name']} / {r['b_name']} | {r['area']} | "
                     f"{r['activators']} | {r['dates']} | {r['pin_km']} | {r['a_outline']}/{r['b_outline']} | {r['route']} |")
        L += ["", f"Source: {API} (park lists and activation histories), read {rd}.", ""]
        with open(os.path.join(self.out, "summary.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L))


# ---------------------------------------------------------------- selftest
HERE = os.path.dirname(os.path.abspath(__file__))


def selftest():
    fx = os.path.join(HERE, "tests", "fixture")
    expected = load_json(os.path.join(HERE, "tests", "expected", "missed_fers.json"))
    tmp = tempfile.mkdtemp(prefix="kpc_missed_fers_selftest_")
    ok = True
    try:
        out = os.path.join(tmp, "out")
        args = parse_args(["--areas", "US-KY,CA-ON", "--parkinfo", os.path.join(fx, "data", "parkinfo"),
                           "--keys", os.path.join(fx, "data"), "--fers", os.path.join(fx, "data", "fers"),
                           "--cache", os.path.join(tmp, "cache"), "--out", out, "--quiet"])
        code = Run(args, FixtureFetcher(os.path.join(fx, "pota"))).go()
        got = load_json(os.path.join(out, "missed_fers.json"))
        strip = lambda rows: [{k: v for k, v in r.items() if k not in ("read_date",)} for r in rows]  # noqa: E731
        checks = [("exit code 0", code == 0),
                  ("pairs match tests/expected/missed_fers.json", strip(got["pairs"]) == strip(expected["pairs"]))]
        refs = {(r["a"], r["b"]) for r in got["pairs"]}
        checks += [
            ("known pair US-0050+US-10105 excluded", ("US-0050", "US-10105") not in refs),
            ("12-park rover creates no pair", not any(r["a"].startswith("US-90") or r["b"].startswith("US-90") for r in got["pairs"])),
            ("2-activator pair not listed", ("US-3001", "US-3002") not in refs),
            ("3x3 pair listed", ("US-4001", "US-4002") in refs),
            ("far-apart pair rejected", ("US-6001", "US-6002") not in refs),
            ("cross-country pair rejected", not any(r["a"].startswith("CA-") or r["b"].startswith("CA-") for r in got["pairs"])),
            ("live/missing/known-NO/dropped pairs excluded", not refs & {("US-8001", "US-8002"), ("US-8003", "US-8004"),
                                                                          ("US-8005", "US-8006"), ("US-8007", "US-8008")}),
            ("routes", {(r["a"], r["b"]): r["route"] for r in got["pairs"]} == {
                ("US-4001", "US-4002"): ROUTE_RETEST, ("US-5001", "US-5002"): ROUTE_MAP,
                ("US-7001", "US-7002"): ROUTE_TRAIL, ("US-6003", "US-6004"): ROUTE_RETEST}),
            ("every row has source_url/read_date/why", all(r.get("source_url") and r.get("read_date") and r.get("why") for r in got["pairs"])),
        ]
        # privacy grep: no callsign from the fixtures in any file written to --out
        calls = set()
        for p in glob.glob(os.path.join(fx, "pota", "activations", "*.json")):
            calls |= {r["activeCallsign"].upper() for r in load_json(p)}
        leaks = []
        for root, _, files in os.walk(out):
            for fn in files:
                text = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read().upper()
                leaks += [f"{fn}:{c}" for c in calls if re.search(r"(?<![A-Z0-9])" + re.escape(c) + r"(?![A-Z0-9])", text)]
        checks.append((f"no callsign in any output file ({len(calls)} callsigns grepped)", not leaks))
        # resume / cache: second run must make no activation requests (counts unchanged)
        ff = FixtureFetcher(os.path.join(fx, "pota"))
        Run(parse_args(["--areas", "US-KY,CA-ON", "--cache", os.path.join(tmp, "cache"), "--out", out, "--resume", "--quiet",
                        "--parkinfo", os.path.join(fx, "data", "parkinfo"), "--keys", os.path.join(fx, "data"),
                        "--fers", os.path.join(fx, "data", "fers")]), ff).go()
        checks.append(("resume + cache: no re-reads", ff.calls == 0))
        # time limit -> exit 3
        a3 = parse_args(["--areas", "US-KY", "--cache", os.path.join(tmp, "c3"), "--out", os.path.join(tmp, "o3"),
                         "--max-minutes", "0", "--quiet"])
        checks.append(("time out -> exit 3", Run(a3, FixtureFetcher(os.path.join(fx, "pota"))).go() == EXIT_TIME))
        for name, passed in checks:
            print(("ok   " if passed else "FAIL ") + name)
            ok &= bool(passed)
        if leaks:
            print("  leaks:", leaks[:10])
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"FAIL selftest crashed: {e}")
        ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


# ---------------------------------------------------------------- cli
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="KPC missed 2-fer finder (leads only, no callsigns in output).")
    p.add_argument("--areas", default="", help="US-KY,US-TN,... (default: every US + CA area, then the world)")
    p.add_argument("--parkinfo", default="data/parkinfo")
    p.add_argument("--keys", default="data", help="folder holding us-key/ ca-key/ world-key/")
    p.add_argument("--fers", default="data/fers")
    p.add_argument("--cache", default="", help="download cache kept between runs (default <out>/work/cache)")
    p.add_argument("--out", default="out")
    p.add_argument("--max-minutes", type=float, default=MAX_MINUTES)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--limit", type=int, default=0, help="only the first N parks with activations")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--min-activators", type=int, default=MIN_ACTIVATORS, help="G-M1")
    p.add_argument("--min-dates", type=int, default=MIN_DATES, help="G-M1")
    p.add_argument("--max-pin-km", type=float, default=MAX_PIN_KM, help="G-M2")
    p.add_argument("--max-outline-km", type=float, default=MAX_OUTLINE_KM)
    p.add_argument("--rove-parks", type=int, default=ROVE_PARKS)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.selftest:
        return selftest()
    contact = os.environ.get("KPC_CONTACT", "").strip() or "contact not set"
    run = Run(args, Fetcher(contact, lambda m: run.log(m)))
    if contact == "contact not set":
        run.log("warning: KPC_CONTACT is not set")
    code = run.go()
    run.log(f"exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
