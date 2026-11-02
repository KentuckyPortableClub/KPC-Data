"""Offline unit tests (no network): python -m pytest -q tests/  or  python tests/test_offline.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import kpc_map_links as k


def toks(s):
    return k.norm_tokens(s, drop_generic=True)[0]


def test_normalise_types_and_initials():
    assert k.norm_tokens("R. F. Tarter Wildlife Management Area")[0] == ["rf", "tarter"]
    assert k.norm_tokens("Devil's Hopyard SP")[0] == ["devils", "hopyard"]
    assert toks(k.filename_text("https://x/More/Documents/RFTarterWMA_ALL.pdf")) == ["rf", "tarter"]
    assert k.norm_tokens("Scanlo\u200bn Creek C.A.")[0][:2] == ["scanlon", "creek"]


def test_score_gate():
    park = k.norm_tokens("Kentucky River WMA")[0]
    assert k.score_name_vs_field(park, toks("Kentucky Lake WMA")) < k.POSSIBLE
    assert k.score_name_vs_field(park, toks(k.filename_text("https://x/KentuckyRiverWMA_All.pdf"))) == 1.0
    # a field that is a subset of the park name must NOT score 1.0
    assert k.score_name_vs_field(k.norm_tokens("Lake Cumberland WMA")[0], toks("Lake")) < k.POSSIBLE


def test_robots_longest_match():
    txt = "User-agent: *\nDisallow: /\nAllow: /s/\nDisallow: /places\nAllow: /places/*\n"
    r = k.Robots(txt)
    assert r.allowed("https://h/s/abc")
    assert not r.allowed("https://h/public/static/abc")
    assert not r.allowed("https://h/places-to-go/x")
    assert r.allowed("https://h/places/bashakill")


def test_forbidden_hosts():
    for h in ("www.google.com", "maps.googleapis.com", "www.openstreetmap.org", "www.alltrails.com",
              "en.wikipedia.org", "www.tripadvisor.com"):
        assert k.host_forbidden(h)
    p = k.HostPolicy("app.fw.ky.gov", {"usfs-public.box.com"})
    assert p.ok("fw.ky.gov") and p.ok("app.fw.ky.gov") and not p.ok("ky.gov") and not p.ok("maps.google.com")


def _cand(url, text, heading="", ph="", page="https://h/p"):
    return k.Candidate(url, "PDF", text, heading, ph, "", page, 0)


def test_shared_and_possible():
    parks = {f"R{i}": {"name": f"Alpha{i} State Park"} for i in range(5)}
    parks["X"] = {"name": "Gamma Hollow State Park"}
    statewide = "https://h/all-parks.pdf"
    cands = [_cand(statewide, "Map", heading=f"Alpha{i} State Park", page=f"https://h/p{i}") for i in range(5)]
    cands.append(_cand("https://h/gamma.pdf", "Gamma Holow"))  # typo -> fuzzy
    res = k.match_agency(parks, list(parks), cands)
    assert all(res[f"R{i}"]["status"] == "SHARED" for i in range(5))
    assert res["X"]["status"] in ("OK", "POSSIBLE")


def test_type_conflict_held_possible():
    parks = {"F": {"name": "Partridge Run State Forest", "type": "State Forest"}}
    res = k.match_agency(parks, ["F"], [_cand("https://h/partridgerunwma.pdf", "Partridge Run WMA Map")])
    assert res["F"]["status"] == "POSSIBLE"


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("ok", n)
