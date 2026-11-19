# Key review packet, part 2

Added a `run` mode to the existing review-packet script and workflow. It does not build any state. The old side is KPC-Links `data/us-key` at a commit. The new side is `data/us-key` at the published commit, with the `key-held` release file laid over the states that run held back. The packet goes to `tools-out` at `key-quality/review-packets/run-<date>/`. A pull request is still the default, and that path is unchanged.

Outline acres are the true union of a park's joined records (overlapping copies counted once). Shapely does that measurement when it is installed, the same library the fact check already uses. The pull-request path does not load it. A park whose shape could not be measured is named. No acre figure is guessed.

## Offline test

Not today's main. KPC-Links `data/us-key` at `8140d35e14923e7fa17cc25254c854d78e3a86c2` (old) and `d5ae6ad340eedbc609707e13c809ca23b5927ccf` (new), with `known-answers/key-held-run-44528656941.tar.gz` (US key run 44528656941) laid over the new side. Saved shapes from the `boundary-cache` release. Activations from KPC-Data `data/parkinfo`. Command: `kpc_key_review_packet.py run` on this machine. It finished in about 35 seconds. No park was skipped for time. No workflow was started and nothing was merged.

The hand acres were measured on a grid (about 10 to 160 m). These acres are the polygon outline. Where a figure differs by more than 2%, it is left as it came out.

## Known answers

**Shrinks (keeps an outline, loses 20% or more), the 13 held states.** 60 parks, the same 60 as `held-states-every-changed-park.csv`. Counts: AK 4, AR 10, DE 2, FL 8, ID 8, MT 15, OR 5, UT 3, VA 4, WY 1. 36 of the 60 are within 2% on both the old and the new acres. 24 differ by more than 2% on at least one side, usually the smaller remnant. None of those 24 moved across the 20% line, so the list is the same. The large ones called out in the brief:

- MT US-0070: 2,183,799 to 158,302, against 2,187,128 to 160,257 (inside 2%).
- MT US-4501: 3,309,424 to 1,107,363, against 3,399,571 to 1,143,001 (2.7% and 3.1% low).
- AR US-1091: 34,711 to 202, against 35,540 to 218 (2.3% and 7.7% low).

**New land, the 13 held states.** The four parks of 100 acres or more are the same four, and no others:

- ID US-10429: 41,608 acres added, against 44,581 (6.7% low). The old union is 5.0% low and the new union is 6.1% low.
- ID US-0890: 14,414 acres added, against 15,257 (5.5% low).
- AR US-7184: 209 acres added, against 190. The two unions are within 0.4% (15,728 against 15,783, and 15,938 against 15,973). The added-land figure is the small gap between those two, so its percent is wider.
- MT US-0054: a new outline of 194 acres, against 196 (1.1% low).

OR US-0054 is a new outline of 5.1 acres, against 5.4. It is under 100 acres, so it is in `new-land.csv` as a new outline and not in the "100+" count.

**Lost outlines.** 126 parks, the same 126 as `lost.json`, and the same cause on every one (Q1 89, contest 17, NONE 16, D3 4). The reason text matches the hand file except three parks, OR US-10487, OR US-10483, and UT US-11746, where the same short reason was written on several check rows. The packet keeps each distinct reason once. The cause on those three is still Q1.

## The other three checks

**Acres added up.** 90 parks whose key says `ac_how: measured`, with two or more joined records, and whose key acres are at least 1.10 times the true outline. The hand sheet's 84 parks at 1.10 times are all in that 90. The six extras each have a key acre of 1 and an outline measured here under half an acre (DE US-10683, DE US-9883, MT US-10176, NY US-10039, UT US-11172, UT US-5778). The hand grid rounded those outlines to 0 or 1 acre, so the ratio stayed near 1.

**Unused record under a dropped copy.** The same three parks the hand sheet marks as clear. MT US-4501, record 2660 Gallatin National Forest, 1,835,034 acres under the copy (the hand raster says 1,901,515, and the brief said about 1,900,000; this is 3.5% low). TX US-4415, record 154025 Boggy Slough, 19,798 against 19,963. IA US-0273, two Kossuth County Waterfowl Production Area records, 149 and 148 acres (the hand sheet combines them at 322).

**The agencies' own acres** were not built. That check was optional, and only after the four above, and it needs the three kit C tables.

## Not done in this offline test

The workflow still runs the fact check and the gold score on a live key run, after the comparison is already written, and with the token removed before any KPC-Links code. Those two were not run here, so this packet's verified column says "not checked". A few parks (mostly trail lines) were not measured because a record was not in the saved shape file. They are named in the packet. None of those skips removed a park from the 60 or from the four new-land parks.

On a live run the workflow reads whatever the `key-held` release holds at that moment and records its `created_at`. The release asset was replaced later on 19 Nov, which is why this test used the saved tar of run 44528656941.
