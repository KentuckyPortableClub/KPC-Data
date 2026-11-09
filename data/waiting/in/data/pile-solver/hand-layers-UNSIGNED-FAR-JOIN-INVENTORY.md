# Far-join inventory (unsigned overrides, pin_km > 5) — Nov 8 2026

Parks whose overrides.json join has no `decided_by`, with live key pin_km over 5 km and id overlap.

## Brandon OK by name — keep live (t792u, 6:49 PM CST Nov 8)

Brandon (t792u): "If the name and boundary match names then leave them." Research far-join-check-20261108-1845-CST found full name matches. No `decided_by` added — current join check already keeps these live via the builder's `reviewed` / unsigned-override path; build does not need a signature to keep them.

| ref | pin_km | join ids | note | evidence |
|---|---|---|---|---|
| **US-0329** | 22.33 | 5300 | Silvio O. Conte NWR — **joined piece is NH Pondicherry Division** (PAD-US 5300); **POTA pin is at Nulhegan Basin VT** (multi-division FWS refuge; same official name). Name match → leave live. | https://www.fws.gov/refuge/silvio-o-conte |
| **US-1208** | 7.38 | cow29, 184168 | Arkansas Headwaters Recreation Area — CPW linear corridor; name match; override already `approx`. Leave live. | https://cpw.state.co.us/state-parks/arkansas-headwaters-recreation-area |

## Left as-is, live

| ref | pin_km | join ids | note | evidence |
|---|---|---|---|---|
| **CA-2450** | 5.35 | 17890 | Little Grand Rapids FN Traditional Use — POTA says WMA; CPCAD 17890 is Traditional Use **Planning Area** (Manitoba M.R. 154/2012). Partial match; **left as-is, live** (no change). | https://web2.gov.mb.ca/laws/regs/current/154-2012.php?lang=en |

## Notes
- Links #100 (stricter unsigned-far hold) is parked by Brandon's request (t793u) — not merged; idea noted for a later careful pass.
- #52's 8 signed (`decided_by`) overrides are unaffected.
- US-2200 sggab60 (0 m) and CA-2373 Manitoba Par:32 (~47 m) stay as unsigned applies (not far).
- US-2200 sggab32 (~25 km) remains a labeled-tract proposal only.
