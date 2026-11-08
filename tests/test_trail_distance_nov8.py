import importlib.util, pathlib
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / ".github/scripts/draft/tools/kpc_layers_nov7"))
P = pathlib.Path(__file__).resolve().parents[1] / ".github/scripts/draft/tools/kpc_layers_nov7/match_trails.py"
spec = importlib.util.spec_from_file_location("mt", P); mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)


def test_long_exact_same_state_line_not_downgraded_for_distance():
    assert mt.confidence(1.0, False, True) == "high"


def test_far_line_other_state_or_fuzzy_stays_medium():
    assert mt.confidence(1.0, False, False) == "medium"
    assert mt.confidence(0.9, False, True) == "medium"


def test_spatial_is_5km_line_buffer():
    src = P.read_text(encoding="utf-8")
    assert '"distance": "5000"' in src and "centroid" not in src.split("def query_layer")[1].split("def confidence")[0]


def test_us6057_stays_rejected_same_name_other_trail():
    import csv
    todo = pathlib.Path(__file__).resolve().parents[1] / "data/waiting/outline-sources/trail-parks-todo-nov7.csv"
    rows = {r[0]: r for r in csv.reader(open(todo, encoding="utf-8"))}
    assert rows["US-6057"][3] == "rejected" and "Prospector Trail System" in rows["US-6057"][5]
