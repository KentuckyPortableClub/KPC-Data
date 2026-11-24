# Settled joins and saved solver answers

One KPC-Data file, IDs first. The key, the solver, and the clean-up stage share it.

Each row has:

- `park` — the park id (for example `US-9001`)
- `status` — one of `settled`, `person-yes`, `person-no`, `solver-suggested`
- `record` — the record number, a hint only
- `fingerprint` — either `{ "kind": "agency-id", "layer": "sgzza", "id": "…" }` (LinkID, URL id, UniqueID, or an explicit agency id, always with its layer) or `{ "kind": "name-acres-box", "name_hash": "…", "acres": 500.0, "box": [minx, miny, maxx, maxy] }`. The name hash is a short sha256 of the shared name key (letters and digits only, same as `kpc_store_attrs.name_key`). The file never stores a display name. Boxes match when they overlap, or when each side is within 0.002°.

Reuse an answer only when the fingerprint still matches and the named record is still in the saved copy. If the named record is missing, list it (S4); do not redo it and do not silently drop it. If several saved pieces share that fingerprint, return all of them (or none as a single pick). A `person-no` answer is never redone: it is listed for a person, and the block list still applies.

Auto-apply is not part of this design step. Writing joins or overrides later is a signed rule change.

Helper: `.github/scripts/kpc_settled_answers.py`. Test: `tests/test_settled_answers_nov24.py` (invented parks only).
