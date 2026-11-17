# traces (held, not official)

Orphan branch for traces of parks with no official record. Written only by
`.github/scripts/kpc_trace_hold.py` from the by-hand workflow
`.github/workflows/kpc-trace-hold.yml` on main. Nothing here is official,
nothing here feeds the 2-fer line, and nothing here is copied to the store
or to any public file.

Layout, one folder per area (store hand-file format):

    <AREA>/<REF>.geojson            the held outline
    <AREA>/<REF>.kpc-source.json    kind "traced", the tracer, the source URL,
                                    the page and the terms
    <AREA>/<REF>.jpg or .svg        a small picture for review
    index.json                      review rows (one per held trace)
    receipts/                       one receipt per run

A trace leaves this branch only through a person's review in the store.
When a park gets an official outline in the key, the next run removes its
held trace here (prune).
