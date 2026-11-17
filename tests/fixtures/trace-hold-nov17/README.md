# Trace hold + PDF finder fixtures (KPC owner, 2026-11-17)

Everything here is a TEST FIXTURE. Nothing in this folder is the store's file or the keeper's list.

- `fetch-settings.json`, `extra-blocked-hosts.txt`, `robots-disallowed-layers.csv`: stand-ins with Handoff 3's numbers. The real files live in KPC-Store and are passed by path.
- `agency/`, `saved/`: made-up agency pages on example.gov hosts (one with its Maps section filled in by script).
- `review-answers-SYNTHETIC.csv`: SYNTHETIC hand answers. They are NOT the Nov 16 hand-made answers (those are in KPC-Store / the manager session and were not reachable). They prove only that the comparison works and lists every disagreement. Drop the real public-safe copy in as `review-answers.csv` and the evidence-card test compares against it too.
- `stored/`: a small made-up stored tracer output (one picture trace, one parcel trace) for the hold test.
