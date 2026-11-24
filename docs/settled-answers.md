# Settled joins and saved solver answers

One KPC-Data file, IDs first. The key, the solver, and the clean-up stage share it.

Each row has:

- `park` — the park id (for example `US-9001`)
- `status` — one of `settled`, `person-yes`, `person-no`, `solver-suggested`
- `record` — the record number, a hint only
- `fingerprint` — either `{ "kind": "agency-id", "id": "…" }` (LinkID, URL id, UniqueID, or an explicit agency id) or `{ "kind": "name-acres-box", "name": "…", "acres": 500.0, "box": [minx, miny, maxx, maxy] }` with the box rounded to 0.001°

Reuse an answer only when the fingerprint still matches and the named record is still in the saved copy. If the named record is missing, list it (S4); do not redo it and do not silently drop it. A same-fingerprint new number may be noted as a hint; it is not an auto-reuse.

This file must not carry a park display name on the row (`name` is only allowed inside a `name-acres-box` fingerprint, where the join needs it). Auto-apply is not part of this design step. Writing joins or overrides later is a signed rule change.

Helper: `.github/scripts/kpc_settled_answers.py`. Test: `tests/test_settled_answers_nov24.py` (invented parks only).
