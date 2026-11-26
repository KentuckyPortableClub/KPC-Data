# Handoff 5, Reviewer A: the US key, park by park

KPC owner review copy, Nov 17 2026. Prepared by Reviewer A (read-only).

Reviewed: KPC-Links main at 7cb77cb1 (Nov 17, 10:41 AM CT): the published data/us-key/US-*.json (13,107 parks, 11,685 joined), its overrides files, layers.json, data/state-gis.json and kpc_us_key.py / kpc_key_rules.py. I also read the tripwire bot's not-sure list (KPC-Data #118 run against this main) to see which problems the tripwires already catch. I only read things: nothing was pushed, no Actions were run, no comments were posted, and no web requests were made.

How I counted: small Python checks over the published key files and the saved map copies on the box (the same saved copies the key reads), plus offline rebuilds of single states with the key's own code (KPC_KEY_OFFLINE=1, saved copies only), once with every switch off and once with a switch on. Every count below comes from those files or runs. Each finding says how to check it yourself.

What I could not open: the handoff file itself was not on the box, so I worked from the six-part brief: Top 10 findings, fixes with proving tests, what the key does well, questions for you, CSVs, and what I did not get to. If the handoff had extra items, please compare them with section 6.

"Not sure" below means the park is on the tripwire bot's not-sure list (T1, T2 or T4), so D10 already keeps it out of 2-fers. Its outline is still drawn on the map.

## 1. Top 10 findings, worst first

### 1. A person's NO is tied to one record number, so the same land comes back from a twin copy
**What's wrong:** A NO in overrides.json blocks one record id. Many states are read from two copies of the same layer (Missouri 'sgmoc' and 'sgmoh', North Carolina 'ncg' and 'sgncb', North Dakota 'ndw' and 'sgnda'). When the Nov 2 map audit said "NO, make it a pin", the NO went on one copy, and the twin copy with the same name and acres is still joined. The park stays drawn as official. The NO-by-name switch (KPC_NO_BY_NAME) wouldn't fix this even if it were on: it only matches a renumbered record in the SAME layer family. Separately, 101 saved NOs already point at a record number whose acres have changed since the NO was given (70 by more than double). Those NOs now sit on different land from the land the person rejected. D1 only checks saved YES rows, not NOs.

**Real parks:**
- US-10211 Sunklands State Conservation Area (Missouri): NO on sgmoc829 'Sunklands CA' (41,941 ac). The twin sgmoh829 'Sunklands CA' (40,383 ac) is still joined.
- US-6503 Magnolia Hollow, US-6514 Big Buffalo Creek, US-6517 Diana Bend, US-12406 Poplar Bluff, US-12676 Holly Ridge CAs (Missouri): the same pattern.
- US-6880 Bachelor Bay and US-6901 Dover Bay State Game Lands (NC), US-7707 Maclean Bottoms WMA (ND), US-6730 Maple River State Game Land (MI). Drift: US-1573 Gambrill SP (Maryland) has its NO on 56638, saved at 1,219 ac; that number now holds 41 ac.

**How many (counted):** 29 parks (61 twin rows) where a NO'd record's same-name, same-acres (within 10%) twin is still joined. 15 of them are not on the not-sure list. And 101 NOs whose record id now carries different acres. How: for every 'nofp' entry in the overrides, I looked for a joined record of the same park with the same cleaned name and acres within 10%, then compared each NO's saved acres with the record's acres in today's saved copy.

**Confidence:** High for the bypass (the twins have the same name and the same acres). Medium on harm for the drift rows: the new land behind an old number may be right or wrong.

**Plain fix:** A NO is about the LAND: it blocks every record, in any layer, that carries the saved name with acres within 10%, unless a person joined that exact id. Turn this on together with D1.

**Check it yourself:** Open data/us-key/US-MO.json, find "US-10211" and read its 'm' list (sgmoh829 is there). Then search the overrides files for US-10211: the NO is on sgmoc829.

**CSV:** A1-person-no-bypassed-by-twin-copy.csv, A1b-person-no-number-now-holds-other-acres.csv

### 2. Rule D3 can't see the state-table copies of designation layers, so BLM areas become a state park's or refuge's "official" land
**What's wrong:** D3 ("a designation line is drawn only for the park that IS that designation") only recognises five federal layer prefixes (fsod, nca, wld, wbl, wsa) and PAD-US 'Designation' rows. The state-GIS-table layers that D11 itself labels 'designation' or 'register' are invisible to it: BLM Areas of Critical Environmental Concern (national and Nevada copies), the Nevada wild horse herd areas, BLM recreation-area polygons, and the NRHP / historic-landmark polygons. Their bare names ('Picacho', 'Hell Creek', 'Browns Park') join any park that starts with the same word.

**Real parks:**
- US-3532 Picacho State Recreation Area (California): its own land is 7,514 ac. It also takes the 197,148-acre BLM ACEC 'Picacho', which brings the park to 202,963 ac (27 times too big). The pin is 1.6 km outside the ACEC.
- US-2577 Hell Creek State Park (Montana): 339 ac of its own, plus the 37,534-acre ACEC 'Hell Creek' (pin 5.6 km outside). US-2237 Henrys Lake State Park (Idaho): 607 ac of its own, plus the 35,870-acre ACEC 'Henrys Lake'.
- US-0223 Browns Park NWR and US-9625 Browns Park State Wildlife Area (Colorado) both take the same 18,506-acre ACEC 'Browns Park' (pins 7.8 and 4.4 km outside). US-0464 Ash Meadows NWR (Nevada) takes the 115,783-acre BLM wild-horse area 'Ash Meadows'.

**How many (counted):** 139 parks take 175 name-only pieces from these state-table designation/register layers. 35 of the parks are not BLM parks at all (state parks, refuges, NPS units, state fishing lakes and wildlife areas), and 25 of those 35 are not on the not-sure list. By layer: Nevada herd areas 49 pieces, BLM OR/WA recreation areas 41, the BLM ACEC national layer 40, BLM Idaho recreation areas 11. How: I took every name or words join to an 'sg' layer whose D11 label is designation or register, then sorted out the parks that aren't BLM.

**Confidence:** High that D3 misses these layers (code: DESIG_PRE in kpc_us_key.py, about line 1161; _desig() at about line 2436). High for the 35 non-BLM parks. Medium for BLM parks, where an ACEC can really be part of the place.

**Plain fix:** Bug fix: D3's "is this a designation line?" reads the layer's D11 label (layers.json / state-gis.json 'what'), not a fixed prefix list. A 'register' layer (NRHP) never gives a park official land.

**Check it yourself:** Open data/us-key/US-CA.json, find "US-3532": the first 'm' row is sgakh637 'Picacho', 197,148 ac.

**CSV:** A2-designation-layers-d3-cannot-see.csv

### 3. A lakeside park takes the whole lake, even after a person said no to the lake
**What's wrong:** A 'water outline only' record (a lake surface from a state hydrography layer) joins by name to any park named after the lake. A state park on the shore of a Corps or utility lake then takes the entire lake. D4 ("who owns the water decides") is written to stop this, but it is OFF.

**Real parks:**
- US-1091 Lake Dardanelle State Park (Arkansas): its own land is 206 ac. With the lake 'Lake Dardanelle' it is 37,080 ac (180 times). A person said NO on Oct 29 and Nov 2 to "the Corps lake around the park". The NO was saved against the PAD-US copy, and the lake came back through the water layer.
- US-3213 Lake Chelan State Park (Washington): 286 ac becomes 32,639 ac. US-1094 Lake Ouachita State Park (Arkansas): 461 ac becomes 41,344 ac. US-2228 Bear Lake State Park (Idaho): 969 ac becomes 69,701 ac.
- US-0596 Umatilla NWR (Washington) takes 'Lake Umatilla', the Columbia River pool behind John Day Dam: 3,044 ac becomes 52,437 ac.

**How many (counted):** 104 parks take a lake surface while their type isn't a lake type (WA 42 pieces, AR 40, ID 28). For 17 of them the lake makes the park more than 3 times its own land. 74 of the 104 are not on the not-sure list. Offline Arkansas rebuild with D4 on: 21 parks give a lake surface back to check, including Lake Dardanelle SP. 10 parks become pins, and several of those are parks where the lake IS the park (US-9164 Lake Conway SRA, US-7190 Bull Shoals Lake SRA, US-10236 Lake Sylvia SRA, US-7524 Lake Greeson NRA).

**Confidence:** High on the counts and on the Arkansas run. Medium on which parks really own their water: that is your D4 call.

**Plain fix:** Turn D4 on one state at a time, Arkansas first. Before that, widen D4's "the park IS the water" test: the Arkansas Game and Fish lake areas POTA lists as 'State Recreation Area' are the lake itself.

**Check it yourself:** Open data/us-key/US-AR.json, find "US-1091": 'ac' is 37,080 and the 'm' list has sgarc26 'Lake Dardanelle', marked 'water outline only'.

**CSV:** A3-lake-surface-joined-to-non-lake-park.csv, A3b-arkansas-d4-offline-before-after.csv

### 4. A park takes a sibling park's own record when one name starts the other
**What's wrong:** The matcher accepts 'X' = 'X + more words'. When POTA also lists the longer-named park, the shorter park takes that park's own record (and sometimes the other way round). This is the US version of Reviewer B's finding 1.

**Real parks:**
- US-0208 San Diego NWR and US-0209 San Diego Bay NWR (California) take each other's records. The Bay refuge's record is 24.8 km from the San Diego NWR pin.
- US-0033 Great Sand Dunes National Park (Colorado) takes the 41,702-acre Great Sand Dunes National Preserve, a separate POTA park (US-8295). US-0902 Aniakchak National Monument and US-0003 Aniakchak National Preserve (Alaska) swap.
- US-3476 Monterey State Historical Park takes five Monterey State Beach records, and US-3595 Will Rogers SHP takes Will Rogers State Beach (California). US-12362 Buffalo Bill SRA, US-5628 Fort Kearny SRA and US-9366 Rock Creek Station SRA (Nebraska) each take the State Historical Park of the same name. US-2803 Sequoyah SP takes Sequoyah Bay SP (Oklahoma). US-9940 / US-9941 Brush Mountain and Brush Mountain East Wilderness (Virginia) swap.

**How many (counted):** 44 parks, 517 joins (WI 333 rows on one park, MA 71, NH 24, TN 22). 42 of the 44 are already on the not-sure list. A few rows are right, where one record really is both places (US-7949 Woodson State Wildlife Area and State Fishing Lake, Kansas; Tennessee's 'State Forest & WMA' records), so a person should skim the list. How: joins where the record's cleaned name is another POTA park's exact name in the same state and is longer than this park's name.

**Confidence:** High that the rule is wrong. Medium on single rows.

**Plain fix:** New rule: an exact name wins over a starts-with name (the same rule Reviewer B proposes for Canada and the world key, so one rule serves all three keys).

**Check it yourself:** Open data/us-key/US-CA.json, find "US-0208": record 167834 'San Diego Bay National Wildlife Refuge' is in its 'm' list.

**CSV:** A4-park-takes-a-sibling-parks-own-record.csv

### 5. D9 ("one record, one park") settles only about 1 in 7 shared records
**What's wrong:** D9 gives a shared record to the one park whose full name is the record's name. Most shared records carry a bare name ('Big Lake', 'Muddy Creek', 'Browns Park', 'Lake Greeson'), so no park "is" the record, D9 does nothing, and the record stays on every park.

**Real parks:**
- PAD-US 166827 'Big Lake' (10,804 ac) stays on both US-0163 Big Lake NWR and US-7265 Big Lake WMA (Arkansas).
- ACEC 'Muddy Creek' stays on both US-5896 Muddy Creek BLM Herd Management Area (pin 15.5 km outside) and US-5903 Muddy Creek BLM Wilderness (Utah).
- Where D9 does find an owner it works: Aniakchak, San Diego / San Diego Bay, Monterey and Will Rogers all go back to the right park.

**How many (counted):** 1,076 records are joined by name to two or more parks. D9 finds an owner for 166 of them, and 58 parks would give a record back (1 would become a pin). 910 shared records have no owner. Offline rebuilds with D9 on changed nothing in Utah or Florida (neither has a shared record with an owner). New Hampshire changed exactly as the count predicted: US-4944 Pine River SF, US-4952 Russell SF and US-4953 Russell-Abbott SF gave 29 records back. How: KR.d9_winner() run over every shared record in the published key, checked against the offline runs.

**Confidence:** High.

**Plain fix:** Add a second D9 step for a record with no owner: it goes to the park whose kind matches the record's kind (designation code, D11 label) and whose pin is inside it. If there is still no single park, it goes to check, not to every park.

**Check it yourself:** Open data/us-key/US-AR.json: "US-0163" and "US-7265" both list 166827.

**CSV:** A5-records-shared-by-two-parks-d9-result.csv

### 6. About 70 parks are pins even though their pin sits inside a record with their own name
**What's wrong:** The record is there, under the pin, and it is not used. The causes: the record's wording differs slightly and the similar-name test refuses it (43 parks); the kind tags disagree, so the record is never offered (28); or the record carries the name only in its second name field, which isn't tested (2). One clean bug: the Forest Service Wild and Scenic River layer writes names as 'Manistee, Michigan National Wild and Scenic River', and the ', Michigan' part stops the match.

**Real parks:**
- US-12792 Manistee, US-12798 Sturgeon (Hiawatha), US-12788 Black and US-12789 Carp National Wild and Scenic Rivers (Michigan): each pin is inside its official FS corridor.
- US-12234 Allegheny NWSR (Pennsylvania) and US-10709 Klickitat NWSR (Washington): the same.
- US-7208 / US-7209 Big Lake North and South State Recreation Sites (Alaska) sit inside 'Big Lake State Recreation Site'. US-6259 Ozone Falls State Natural Area (Tennessee) has 'Ozone Falls' only in the second name field.

**How many (counted):** 73 pins (plus 17 more where a person said NO, which are correctly left alone). 14 of the 73 are Wild and Scenic Rivers, and 13 of those have their pin inside a same-name FS or BLM corridor. How: every pin park, any record within 0.2 km of the pin whose cleaned name matches closely, then the key's own reason for refusing it.

**Confidence:** High for the Wild and Scenic Rivers. Medium for the rest (a person should look).

**Plain fix:** Bug fix: drop ', <State>' (and '(<forest> NF)') from FS river names before matching. Test the second name field. New rule: a near-identical name with the pin inside joins as 'approximate' and goes on a person's list.

**Check it yourself:** Open data/us-key/US-MI.json, find "US-12792": g is 'pin'. Then look for fwsr44 in the FS Wild and Scenic River layer.

**CSV:** A6-pins-with-their-own-record-under-the-pin.csv

### 7. Shared-words joins reach schools and county parks a few kilometres away
**What's wrong:** A 'words' join (sharing a place word) lets a record from a school, city or county join a state park. R-G8 checks the kind of place, but 'school', 'county park' and 'city beach' aren't treated as a different kind.

**Real parks:**
- US-2859 Tumalo State Park (Oregon) takes 'Tumalo Community School', 2.5 km away. US-9149 Ontario SRA (Oregon) takes 'Ontario High School', 2.1 km away.
- US-3445 Huntington State Beach (California) takes 'Huntington City Beach', 3.5 km away.
- US-3680 Barbour WMA (Alabama) takes 'Barbour County Public Fishing Lake', 4.9 km away. US-5740 Little River WMA and US-9315 Three Mile Lake WMA (Iowa) take county parks. US-7389 Cypress Creek Preserve (Florida) takes 'Cypress Creek Preserve (Pasco County)', 6.6 km away.

**How many (counted):** 8 parks with a clearly wrong record. None of the eight is on the not-sure list, so they would count for 2-fers. How: joins whose record name has school / high / city / county / town that the park's name doesn't, then the distance from the pin.

**Confidence:** High for these 8 (small, but none of them is caught today).

**Plain fix:** Bug fix in R-G8: school, college, city, county, town, cemetery, church and airport are 'another kind of place' unless the park's own name has that word, or the record's name holds the park's full name.

**Check it yourself:** Open data/us-key/US-OR.json, find "US-2859": sgore18080 'Tumalo Community School' is in its 'm' list.

**CSV:** A7-shared-words-joins-to-schools-and-county-parks.csv

### 8. The offline proof runs for the switches show far less than the changelog says
**What's wrong:** I rebuilt single states offline from the same saved copies, with each switch off and then on. Results:
- D1 (saved id is land) changed nothing in Florida, Utah or New York, against "32 Florida parks / 197 rows" in the changelog. D1 only acts on rows whose record changed since the last read, so on identical saved copies it can't show anything. Its proof needs a fresh read or a simulated renumber.
- D3 changed one park in Utah: US-5750 Black Ridge Canyons Wilderness lost two WSA pieces. Nothing changed in Florida or New York (and see finding 2 for what it misses).
- D4 changed 21 parks in Arkansas (finding 3), and none in Florida or Utah (no candidates).
- D5 had no candidates in Florida or Utah. Its candidates are in NC (15 name joins), MI (4), CT and OH (1 each); the NC run moved exactly those 15.
- D9: none in Utah or Florida; 3 parks and 29 records in New Hampshire (finding 5).
- An offline rebuild of Arkansas with every switch off is not identical to the published key either: US-7184 Moro Big Pine State Natural Area gains arw1769. So "off = today" is not exact, and a proof should compare two offline runs, never an offline run with the published file.

**How many (counted):** 23 offline single-state rebuilds: FL 7, UT 7, NY 3, AR 2, NC 2, NH 2. North Carolina with D5 on: 14 game lands and Carolina Beach SP each send a leased piece to check (15 pieces), and none of them becomes a pin.

**Confidence:** High (the runs are on the box).

**Plain fix:** Pick each switch's proof state from where its candidates are (D4: AR / WA / ID, D5: NC, D9: MA / NH / CA), and prove D1 with a test that renumbers a saved copy. Reviewer B's single switch file would make this repeatable.

**Check it yourself:** /workspace/revA_runs/out/*.json on the box. The FL files all have the same checksum.

**CSV:** A3b (Arkansas D4) and A8-offline-switch-runs.csv (every run, before/after).

### 9. One in five joined parks has no total acreage, so size checks skip it
**What's wrong:** Many state-table records carry 0 acres (no acreage field), so a park drawn only from them gets no 'ac'. Any check that compares sizes (a join 10 times bigger than the park, "3 times the park's land", T4's size slack) skips these parks without a word.

**Real parks:**
- The 312 trail parks drawn from trail lines.
- Parks drawn only from Wilderness Study Area, wilderness and herd-area pieces (wsa, wbl, sgakb) show 0 ac.
- US-1091 Lake Dardanelle SP: the lake row itself shows 0 ac, and the size blow-up only appears in the union 'ac'.

**How many (counted):** 2,266 of 11,685 joined parks have no 'ac'. 984 parks have at least one 0-acre record. How: counted from the published key.

**Confidence:** High on the count. Medium on how often this hides a real error.

**Plain fix:** Compute acres from the saved shape when a record has none (the key already holds the rings), and mark the 'ac' as measured.

**Check it yourself:** Count parks in any US-*.json where g is not 'pin' and 'ac' is missing.

**CSV:** none (the list is the key itself)

### 10. The 'designation code ignored' path lets one kind of park take another kind's record
**What's wrong:** When a PAD-US record's name matches but its designation code doesn't, the key can still join it ('name (designation code ignored)'). That's how a refuge ends up with state park pieces.

**Real parks:**
- US-0335 Susquehanna NWR (Maryland) is joined to 'Susquehanna Sp' (Susquehanna State Park) pieces 56734, 56736, mdd203 and sgmda203. A person already said NO to the big piece 56735 on Nov 2 ("WAY OFF: PIN until fixed").
- US-0163 Big Lake NWR and US-7265 Big Lake WMA (Arkansas) both take PAD-US 'Big Lake' (10,804 ac).
- US-11476 Mt. Tom WMA (Massachusetts) takes eight 'Mount Tom State Reservation' records.

**How many (counted):** 87 joins on 67 parks use this path. Not every one is wrong (US-3641 Okeechobee Battlefield SP is fine), so a person should skim them.

**Confidence:** High for the examples. Low-to-medium for the share that is wrong.

**Plain fix:** A 'designation code ignored' join is never 'official': it is 'approximate' and goes on a person's list, unless the record's designation is the park's kind.

**Check it yourself:** Open data/us-key/US-MD.json, find "US-0335".

**CSV:** A10-designation-code-ignored-joins.csv

## 2. The fixes: rule or bug fix, files, proving test

Safe order, the same one Reviewer B gives: D1 and the NO fix first (they protect a person's decisions), then exact-name-wins and the D9 second step, then D3 / D4 / D5, then the small bug fixes. One switch, one state at a time, smallest state with candidates first. Each step's proof is the before/after park list from two offline builds.

### Finding 1. Bug fix: a NO is about the land, not the number.
- What counts: a record whose cleaned name equals a NO's saved name and whose acres are within 10% (20-acre slack) is blocked, in any layer, for that park.
- What does not count: a record a person joined by its exact id (the Standing Boy Creek lesson, Nov 3).
- When unsure (no acres on one side): blocked, with the reason 'a person said NO to this land (twin copy)'.
- Also: a weekly report of NOs whose saved acres no longer match their id (the 101 in A1b).
- Files: kpc_key_rules.py (is_no, no_names: drop the same-family limit for name+acres matches), kpc_us_key.py (the NO check on every join path, which KPC_NO_ALL_PATHS already wires).
- Proving test: US-10211 Sunklands CA with NO on sgmoc829 must not join sgmoh829; US-7896 Standing Boy Creek SP keeps its hand-joined sggab59. The test fails on today's code.

### Finding 2. Bug fix: D3 reads the layer's D11 label.
- What counts: a name-only join to any layer labelled 'designation' (DESIG_PRE, PAD-US Designation, OR an 'sg' layer whose state-gis.json 'what' is designation) is kept only when the park IS that designation (today's _is_it test).
- A 'register' layer (NRHP, historic landmarks) never gives official land; at most a note.
- Files: kpc_us_key.py (_desig, about line 2436), data/state-gis.json (already has 'what'), the US scope file, the changelog.
- Proving test: US-3532 Picacho SRA loses sgakh637 and keeps its three own records; US-4548 Pompeys Pillar NM (a BLM monument whose ACEC is the monument) keeps its ACEC because it passes _is_it.

### Finding 3. Turn D4 on, after one widening.
- Widen LAKE_TYPE: a park whose name begins with the lake's own name and whose type is 'State Recreation Area' / 'Recreation Area' / 'Fish and Wildlife Area', AND which has no land record of its own, is the water (Arkansas AGFC lakes).
- What does not count: a state park with its own land on someone else's lake (Lake Dardanelle, Lake Ouachita, Lake Chelan, Bear Lake).
- Files: kpc_key_rules.py (LAKE_TYPE_RX, lake_inside_land), kpc_us_key.py (D4 block, about line 2399).
- Proving test: offline AR build: US-1091 Lake Dardanelle SP is about 206 ac with the lake in check; US-9164 Lake Conway SRA keeps its lake.

### Finding 4. New rule: an exact name wins.
- What counts: a record joins a park by a starts-with match only when no other POTA park in the same state has the record's exact cleaned name.
- When unsure: check, with the reason 'name also fits <other park>'.
- Files: kpc_us_key.py (the name join), kpc_key_rules.py (_full), the scope file.
- Proving test: US-0208 San Diego NWR loses 167834; US-0033 Great Sand Dunes NP loses 3303 (the Preserve); US-3476 Monterey SHP loses the five State Beach records.

### Finding 5. D9 second step for records with no owner.
- What counts: the park whose kind matches the record's (designation code or D11 label) and whose pin is inside the record keeps it.
- When unsure (zero or two such parks): the record goes to check for all of them, never to everyone.
- Files: kpc_us_key.py (D9 block, about line 2726), kpc_key_rules.py (d9_winner).
- Proving test: PAD-US 166827 'Big Lake' (Arkansas) ends on exactly one park or on neither, never on both.

### Finding 6. Bug fix plus a small rule: the Wild and Scenic River name format, and the second name field.
- Files: kpc_us_key.py / kpc_match.py name cleaning; the R-G1 similar-name test.
- Proving test: US-12792 Manistee NWSR joins fwsr44 as official; US-6259 Ozone Falls SNA joins 255603 by its second name field.

### Finding 7. Bug fix in R-G8: schools, cities and counties are another kind of place.
- Files: kpc_us_key.py (_g8des / the 'another kind of place' test).
- Proving test: US-2859 Tumalo SP loses 'Tumalo Community School'; US-3332 Watkins Lake SP keeps 'Watkins Lake State Park and County Preserve', because that record holds the park's full name.

### Finding 8. Proof process (no rule change).
- Each switch's proof uses a state with candidates; D1's proof is a test that renumbers a saved copy; a proof compares two offline runs, never offline against the published file.

### Finding 9. Bug fix: measured acres.
- Files: kpc_us_key.py (union acreage), kpc_key_facts.py.
- Proving test: a park drawn only from 0-acre WSA pieces gets an 'ac' within 5% of its shape's area.

### Finding 10. Rule: 'designation code ignored' joins are approximate.
- Files: kpc_us_key.py (where 'name (designation code ignored)' is written).
- Proving test: US-0335 Susquehanna NWR has no 'Susquehanna Sp' piece left as official.

## 3. What the key does well

- The tripwires work. 42 of the 44 parks in finding 4 and most of the big multi-park records are already on the not-sure list, so D10 keeps them out of 2-fers even before the rules are fixed.
- A person's work is everywhere and is respected: 12,870 joins are 'reviewed', overrides carry the reason and the date, and since Nov 2 a NO is checked on every join path (KPC_NO_ALL_PATHS, the one switch that is on by default).
- D1's code is careful: a saved row is kept only when the record still has the saved name and acres within 10%, and is looked for again in the same layer near the pin. It just needs a fresh read to show its effect, and a twin for NOs (finding 1).
- D3, D4 and D5 do exactly what their notes say when they have candidates: Utah D3 removed only the two WSA pieces; Arkansas D4 sent 21 lake surfaces to check and left everything else alone; North Carolina D5 sent 15 leased pieces to check without turning a single park into a pin.
- R-G8, G-1 and the 'held' rules stop many shared-words pieces: in Florida alone, 3 parks had shared-words pieces moved to check and 2 had similar-name pieces held.
- Rule 18 tracts and B12 ('only its own parts of a shared multipart record': 19 parks in New York) are good examples of fine-grained, explainable joins.
- Every park carries 'bk' (best record, distance, kind) and 'far' (pin inside/outside), so most of this review could be done from the published files alone.
- Fail-closed habits: a saved-copy-only run skips a state with no saved shapes rather than guessing, and a pass that errors only skips itself with a notice.

## 4. Questions for you

1. Lakes (finding 3): should an Arkansas Game and Fish lake area that POTA calls a 'State Recreation Area' keep the whole lake? My suggestion: yes when it has no land record of its own, no for state parks with their own land.
2. NPS monument and preserve pairs (Great Sand Dunes NP and Preserve, Aniakchak NM and Preserve, Craters of the Moon NM and Preserve, Glacier Bay NP and Preserve): POTA lists each one separately. OK for each to get only its own unit?
3. BLM ACECs on BLM parks (San Rafael Reef, Fiftymile Mountain, Canaan Mountain): an ACEC is a management overlay, not ownership. Keep them as part of the BLM park, or move them to the 'on' list?
4. Outer boundaries: US-2001 Adirondack and US-8070 Catskill (the Blue Line and the Catskill Park line), and the national forest administrative boundaries (US-4391 Humboldt-Toiyabe, 6.7 million ac) contain a lot of private land, and 23, 8 and 27 other POTA parks sit inside them. Keep them as official outlines, or mark them 'approximate' for 2-fers?
5. The NO fix (finding 1): OK for a NO to block every same-name, same-acres copy in any layer, unless a person joined that exact id?
6. Order: OK to fix finding 1 (the NOs) and switch on D1 in the same step, since both protect a person's decisions?

## 5. CSV files

Folder: /workspace/kpc_handoff/outbox/handoff5-A-csv/
- A1-person-no-bypassed-by-twin-copy.csv (61 rows, 29 parks)
- A1b-person-no-number-now-holds-other-acres.csv (103 NOs; 101 with acres changed)
- A2-designation-layers-d3-cannot-see.csv (175 rows, 139 parks; column 'park is a BLM-type park' separates the 35 that are not)
- A3-lake-surface-joined-to-non-lake-park.csv (110 rows, 104 parks)
- A3b-arkansas-d4-offline-before-after.csv (21 parks)
- A4-park-takes-a-sibling-parks-own-record.csv (517 rows, 44 parks)
- A5-records-shared-by-two-parks-d9-result.csv (1,076 shared records: 166 with an owner, 910 without)
- A6-pins-with-their-own-record-under-the-pin.csv (73 parks, 14 of them wild and scenic rivers)
- A7-shared-words-joins-to-schools-and-county-parks.csv (8 parks)
- A8-offline-switch-runs.csv (every offline run, before/after)
- A10-designation-code-ignored-joins.csv (87 rows, 67 parks)

Every CSV has an 'on not-sure list' column where it applies, so you can see what the tripwires already catch.

## 6. What I did not get to

- No full 50-state offline rebuild with every switch on. I rebuilt FL, UT, NY, AR, NC and NH, and counted the rest from the published key with the key's own code (for D9, the New Hampshire run matched the count exactly).
- The pins-that-could-join list (finding 6) and the 'designation code ignored' list (finding 10) need a person's skim; I didn't judge every row.
- Pin outside its land: the key's own Boundary check says 2,312 of 11,736 joined parks (19.7%) have their pin outside their land (worst: NY 130 of 830, MA 118 of 411, CO 112 of 266). I didn't sort these into 'POTA pin is off' and 'wrong land'.
- Federal parks drawn twice (a PAD-US copy plus a state-table copy of the same refuge or historic site, 134 parks) and parks drawn only from compilation layers (Florida's FNAI list, Delaware's DNREC protected lands and others: 96 parks): I didn't measure whether the copies disagree.
- Kentucky, the 2-fer side, Canada and the world key were out of scope (Reviewer B covers Canada and the world key).
- The handoff file itself was not on the box; see the note at the top.
