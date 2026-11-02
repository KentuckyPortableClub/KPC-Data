# KPC 11 Boundary Change Watcher: test report

Tested 2026-10-31 on the box: Python 3.13.5, shapely 2.2.0, pyproj 3.8.0, rapidfuzz 3.14.6, pytest 9.2.0.
Club files were read from a read-only copy of `sample-data/`. All output went to a scratch folder. Nothing was
pushed or posted, and no live file was edited.

## 1. Offline unit tests (made-up shapes, pretend ArcGIS server): 18 passed, 0 failed

    python -m pytest -q tests      ->  18 passed in 0.25s

| test | what it proves |
|---|---|
| test_round_rel_keeps_0_1_percent, test_compare_fp_rules | fingerprints are rounded to 0.1 %; GREW / SHRANK / MOVED / SAME rules |
| test_kept_share | "still inside" % of the old outline |
| test_first_run_then_same | 1st run = FIRST LOOK, 2nd run = SAME using only 2 web requests (layer not edited) |
| test_changes_are_found | GREW, SHRANK, MOVED, RECORD GONE, RENAMED, SAME, each with the 2-fer rows and live flag |
| test_layer_moved_gives_leads | a 404 layer gives LAYER MOVED plus leads from the service listing |
| test_source_down_is_not_a_change | server down = SOURCE DOWN; the next good run is SAME, not a change |
| test_bad_input_exit_2 | missing folder, bad --max-minutes, and output inside the club folder all exit 2 |
| test_out_of_time_then_resume | runs out of time, exits 3, and `--resume` finishes with exit 0 |
| test_renumbered_record_gets_a_lead | a gone record whose name is on the layer under a new number is named as a lead |
| test_unknown_layer_is_cant_tell_not_source_down | a park with no layer address is CAN'T TELL, and its other pieces are still fingerprinted |
| test_user_agent, test_backs_off..., test_one_request_per_second_per_host, test_robots_txt..., test_offline... | polite fetching rules |
| test_404_and_service_not_found_mean_layer_moved | how a moved layer is spotted |
| test_tract_piece_is_picked | a "(X tract)" KY row takes only the matching piece of a multi-part record (Fort Heiman) |

## 2. Real data: US-KY, US-TN, CA-ON (live official layers)

Command: `python kpc_boundary_watch.py --data sample-data --out watch --cache cache --areas US-KY,US-TN,CA-ON`

| run | time | web requests | result |
|---|---|---|---|
| run 1 (empty state) | 9 min 48 s | 532 | KY: 190 FIRST LOOK, 2 CAN'T TELL. TN: 256 FIRST LOOK, 1 RECORD GONE. ON: 814 FIRST LOOK, 1 RECORD GONE, 117 CAN'T TELL. Exit 0 |
| run 2 (straight after) | about 5 min | not logged | same counts with FIRST LOOK turned into SAME. Exit 0 (see note) |
| run 3 (straight after) | 5 min 13 s | 268 | KY 190 SAME / 2 CAN'T TELL; TN 256 SAME / 1 RECORD GONE; ON 814 SAME / 1 RECORD GONE / 117 CAN'T TELL. 15 of 26 layers skipped as "not edited". Exit 0 |

So the watcher gives no false changes on back-to-back runs. Because of the layer edit-date check, the repeat run
needs about half the requests.

Real findings, both checked by hand with curl against the live layer:
- **US-2958 Montgomery Bell State Park (TN)**: record 260 on the TN state-lands layer (sgtnj) is gone. The same
  name is now record **480**, and 100 % of the old outline is inside the new one. RECORD GONE with a "probably
  renumbered" lead.
- **CA-1643 St. Williams Conservation Reserve (ON)**: record 20801 on the Ontario conservation reserves layer is
  gone. The same name is now record **22081**, with 100 % still inside. Same verdict and lead.

Could not check (119, tried again every run):
- 117 Ontario conservation-authority parks (18 authority prefixes such as ON-NPCA, ON-GSCA, ON-GRCA, ON-CH, ON-TRCA).
  Neither `layers.json` nor the spec gives a layer address for them. They can be added with `--sources`.
- US-10099 Wolf Creek National Fish Hatchery and US-3802 Clyde E Buckley Sanctuary (KY): no record with that name
  on the layer the KY code points to.

Size: `state.json` is 548 KB (numbers only). The `outlines/` working copy is 20 MB, which is why it belongs on a
throwaway branch or in a scratch folder (README says so).

Note on run 2: its log file was cut off by the box session ending, but `state.json` records it as finished
(started 18:29 CDT) with the same counts. Run 3 repeated it with a clean log.

Earlier build (before the OID, layer-key and CAN'T TELL fixes below): `--max-minutes 4` stopped with exit 3, and
`--resume` finished with exit 0 (5 min 32 s), carrying on from the saved areas.

## 3. Bugs found by the real-data runs and fixed
- Servers leave the record-number field out unless it is asked for, so every park first came out RECORD GONE. The
  tool now reads the layer's objectIdField and always asks for it. The pretend server now behaves the same way, so a
  test catches this.
- The same park name looked up on two KY layers shared one cache key. The lookup is now keyed by layer.
- A park with no layer address was reported as SOURCE DOWN. It is now CAN'T TELL.
- Fort Heiman (a KY "tract" row) was measured against the whole Fort Donelson record (TN-KY). Now only the
  matching piece is used.
- Repeated reasons in "could not check" lines are now shown once.

## 4. Not tested
- A real GREW / SHRANK / MOVED / RENAMED / LAYER MOVED. None happened on the live layers in these runs, so these
  are covered only by the unit tests on made-up shapes.
- SOURCE DOWN on a real server (only simulated).
- robots.txt on a real web page (the tool only reads ArcGIS REST endpoints, which have no robots rules to apply).
- Areas other than US-KY, US-TN and CA-ON.
- Windows/macOS. Only tested on Linux.
- Other agents on the same box were reading some of the same servers at the same time. Each tool keeps to 1
  request per second per server by itself, but they cannot pace each other.
