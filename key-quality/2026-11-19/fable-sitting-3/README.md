# Fable's sitting, 19 Nov 2026 ~10 AM CST (key-quality.md section 19 item 20)
Read-only work: saved shapes (release boundary-cache), the published key (KPC-Links 8140d35), the run's files (main d5ae6ad3 +
release key-held), the run's fact check, kit C. No bot run, no key or rule changed. Acres measured here = TRUE UNION by raster
(scripts/measure.py: even-odd per record, OR across records; no shapely in the chat box), cell 10-160 m, good to about 1%.

- `pp1a-scan-13-states.txt`: #278 round 2, its own rule function on real shapes / rows / pins, all 13 scope states.
- `added-up-acres-116-parks.csv`: every park whose `ac` is `ac_how: measured` with 2+ rows: the key's figure (KR.measured_ac ADDS
  the rows) against the true union, the official size and the fact-check class. 84 of 116 are 1.10x or more over; 10 SIZE_BIG
  flags are false (FL US-6321 US-6328, CT US-7531, PA US-5473, WI US-4278 US-4311 US-4341 US-4348 US-9836 US-9867).
  Reproduced to the acre: US-6321 67,913, US-6328 189,872, US-4500 2,117,033 (scripts/replicate_ac.py).
- `idaho-forests-not-fs-land.csv`: the 11 parks in the Idaho key joined to USFS EDW_BasicOwnership records (sgidd): the largest
  record = the USFS report's NFS acres, the other record(s) = its other-ownership acres (gross minus NFS). About 2.9 M acres.
- `held-states-every-changed-park.csv`: all 302 parks whose joined records change in the 13 held states, old against new union,
  kind (outline -> pin / smaller / bigger / to the trail line / same land), the rule that removed the land.
- `held-states-records-added.csv`: the 46 parks that gain a record, with the new land drawn.
- `d7-dropped-copies-160-parks.csv` + `d7-against-agency-acres.txt`: every park with a 'check (D7): a compilation copy' row, all 50
  states: the copy, the joined records, the land left uncovered, any UNJOINED record of the same manager under the copy, and the
  agency's own acres (kit C). Confirmed: MT US-4501 Custer Gallatin NF (PAD-US 2660 'Gallatin National Forest', 1,850,408 ac, is in
  `nonum`). To look at: MT US-0399, US-0408; VA US-0563, US-0572.
Kit C is ONE outside-agent pass (the USFS file was downloaded by the owner): a witness here, not yet a saved answer.
