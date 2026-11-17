# Handoff 5, Reviewer B: Canada key, world key, and the rebuild machinery

KPC owner review copy, Nov 17 2026. Prepared by Reviewer B (read-only).

Reviewed: KPC-Links main at 7cb77cb1 (Nov 17, 10:41 AM CT), which comes after 712558ab. I only read things. Nothing was pushed, no Actions were run and no comments were posted. I sent three plain web requests: two to North Macedonia's public map service and one to Japan's MLIT code-list page.

How I counted: I read the published key files (data/ca-key/CA-*.json, data/world-key/*.json, their overrides and tracts files) and ran small Python checks that reuse the keys' own name code. Every count below comes from those files. I did not do a full offline rebuild; the time went into counting. Each finding says how to check it yourself.

What I could not open: the handoff file itself was not on the box (the attachment path came up empty), so I worked from the six-point brief I was given. If the handoff had extra items, please compare them with section 6.

## 1. Top 10 findings, worst first

### 1. A park can take a neighbouring park's land because its name is the start of the other park's name
**What's wrong:** The name matcher accepts 'A' = 'A + more words' (Canada: a word-start match of 60% or more; world: even part of a word, e.g. 'watagan' inside 'watagans'). When a sibling park with the longer name exists, the shorter park takes the sibling's land, and often the sibling takes the shorter one's too.

**Real parks:**
- CA-0304 Mississagi Provincial Park (Ontario) is joined to Mississagi River PP and Mississagi Delta PP records; CA-0305 and CA-0306 each take Mississagi PP's record back.
- CA-0162 Bonnechere PP and CA-0163 Bonnechere River PP (Ontario) swap land; CA-1064 Pinawa Dam PP and CA-6605 Pinawa PP (Manitoba) do the same.
- AU-0564 Mount Barrow State Reserve and AU-0565 Mount Barrow Falls State Reserve (Tasmania) swap. AU-1656 Watagans National Park (NSW) takes Watagan State Forest. IT-2159 Torrente Vasi (Italy) takes Torrente Lago's Natura 2000 site, because 'lago' is treated as a filler word and gets dropped.

**How many (counted):** Canada: 56 joins on 32 parks (ON 19, BC 17, MB 7, NB 5, AB 3, SK 3, QC 2 joins). World: 438 joins on 222 parks (AU 267 joins, GB 54, FR 53, NZ 17, IT 11, ES 10). Removing them would leave 47 parks as pins (4 in Canada). How: I counted each name join where the matched record's own name equals another POTA park's name in the same province or country, and where that record shares more words with the other park than with this one.

**Confidence:** High that the rule is wrong. Medium for each single row: a few rows are right, for example where POTA shortened a park's own name, so a person should skim the CSV.

**Plain fix:** Port D9 (one record, one park) to Canada and the world key, and add the 'exact name wins' rule in section 2.

**Check it yourself:** Open data/ca-key/CA-ON.json, find "CA-0304" and read its 'm' list: the River and Delta class records are there.

**CSV:** F1-name-starts-with-takes-a-neighbours-land.csv

### 2. Japan: the national park-name list is read wrong, so about 140 parks find no outline at all
**What's wrong:** The world key reads Japan's national A10 file, where each area carries a park-name code, and looks the code up in MLIT's code list. The reader keeps only list entries whose name contains 公園 ('park'), but the list gives bare names (for example 阿寒, 'Akan'). Only 3 of 397 codes get read, so the national file names almost nothing.

**Real parks:**
- JP-0102 Abashiri Quasi-National Park (Hokkaido): no candidate at all; the code list has 102 網走 (Abashiri).
- JP-0132 Biwako Quasi-National Park (Shiga): no candidate; the code list has 132 琵琶湖 (Biwako).
- JP-0116 Minami-Boso Quasi-National Park (Chiba): no candidate; the code list has 117 南房総 (Minami-Boso).

**How many (counted):** 45 of 58 Quasi-National Parks and 218 of 306 Prefectural Nature Parks have no join. 141 of the unjoined parks match a code-list name once it is read correctly (31 Quasi-National, 103 Prefectural Nature, 6 Prefectural, 1 National). How: I parsed the code list, turned each name into romaji with the key's own converter, and compared it with the key's own Japan name test.

**Confidence:** High for the bug (3 of 397 codes is easy to check). Medium for the gain: each park still has to pass the pin-distance check in a real build, and the FY2010 outlines are old.

**Plain fix:** Bug fix in kpc_world_key.py pull_a10n(): take the name cell next to the code whether or not it contains 公園. One licence question has to come first (owner question 1).

**Check it yourself:** Open https://nlftp.mlit.go.jp/ksj/gml/codelist/NaturalParkNameCd-v3_0.html: row 003 says 阿寒, with no 公園. Then look at line ~1054 of kpc_world_key.py.

**CSV:** F2-japan-parks-the-national-A10-file-could-name.csv (and F2b: the 124 Japan parks drawn only from A10 data today)

### 3. Canada keeps a person's hand joins and NOs as bare record numbers, with no name check
**What's wrong:** In data/ca-key/overrides.json, 86 hand joins and 6 NOs are stored as record numbers ('21900', 'Québec prote:2496'). The build joins whatever record has that number within about 60 km of the pin, without checking its name. Canada's record numbers are the map server's own numbers (CPCAD OBJECTID), which change when Environment Canada republishes CPCAD. This is the US D1 problem. Canada fixed it for the hard-look path on Nov 2 (name check), but not for overrides.

**Real parks:**
- CA-3297 Queen Charlotte Sound Glass Sponge Reefs MPA (BC): saved as 21900 and 21901.
- CA-2375 Asatiwisipe Aki WMA (Manitoba): saved as 17886 and 17887.
- CA-2227 Rivière Malbaie Nature Reserve (Quebec): its NOs are 'Québec prote:2496' and 5246. After a renumber the NO points at nothing and the rejected record can come back.

**How many (counted):** 92 saved numbers on 52 parks (86 joins on 49 parks, 6 NOs on 3 parks; 57 are bare CPCAD numbers). By province: QC 26, ON 16, NS 12, MB 10, BC 9, NB 8, PE 8, YT 2, NL 1. Today all 86 still point at the right names (I checked each one), so nothing is wrong yet. The risk starts at the next CPCAD release.

**Confidence:** High (code line ~814 of kpc_ca_key.py; it only compares the number and a 0.6-degree box).

**Plain fix:** Port D1 to Canada: save CPCAD's own stable ZONE_ID with the name and hectares, which the tracts files already carry as 'sid'.

**Check it yourself:** Open data/ca-key/overrides.json and search for "CA-3297".

**CSV:** F3-canada-hand-decisions-saved-as-bare-record-numbers.csv

### 4. In Canada, a person's 'this is a different place' decision is quietly overruled
**What's wrong:** When a reviewer said a same-name record was 'a different place, not this park', Canada stored it as 'none' (no outline). 'none' only empties the to-check list; it does not block a name join. A layer added later with the same name joins anyway, and nothing records that a person said no.

**Real parks:**
- CA-0485 Trout Brook Provincial Park (Nova Scotia): reviewed Oct 22 as a different place, now joined to 'Trout Brook Provincial Park' from NS Lands Proposed or Pending Protection.
- CA-6371 Cedar Creek Conservation Area (Ontario): now joined to Essex Region CA's 'Cedar Creek'.
- CA-5201 Ministers Island NHS (New Brunswick): now joined to GeoNB's 'Minister's Island'.

**How many (counted):** 9 of the 171 'none' parks (BC 2, NB 2, NS 3, ON 1, PE 1). How: parks with none=true in overrides.json that have a non-empty 'm' list in the key.

**Confidence:** High that the decision is being overruled. Some of the new joins may be right, which is exactly why a person should see them again.

**Plain fix:** Bug fix in kpc_ca_key.py: a 'none' park takes no name join until a person clears it, and a 'different place' review is saved as a 'no' with the record's name.

**Check it yourself:** Search data/ca-key/overrides.json for "CA-0485", then look at CA-0485 in data/ca-key/CA-NS.json.

**CSV:** F4-canada-person-said-not-this-park-but-joined-now.csv

### 5. World key: flagship national parks get no outline when a Natura 2000 site has the same name
**What's wrong:** When two records share a park's name but are different kinds (the national park and the EU Natura 2000 bird or habitat site), the world key refuses both and parks the case as 'same name, more than one kind of area'. Most of the time one of the two plainly is the park.

**Real parks:**
- ES-0001 Doñana National Park, ES-0002 Sierra Nevada National Park and ES-0210 Teide National Park (Spain).
- SK-0002 Nízke Tatry National Park and SK-0003 Slovenský raj National Park (Slovakia).
- SE-0006 Muddus/Muottos National Park and SE-0011 Sonfjället National Park (Sweden).

**How many (counted):** 250 parks have no join for this reason (FR 110, ES 52, SE 26, PL 20, FI 10, SK 10, AT 7, BE 5, PT 4, NO 3, SI 2, LU 1); 27 of them are named national parks. How: unjoined parks whose check list holds a 'more than one kind of area' row.

**Confidence:** High on the count. Medium on how many the fix would settle without a person.

**Plain fix:** New rule (section 2, 'the park's own kind picks between two same-name records').

**Check it yourself:** Open data/world-key/ES.json and find "ES-0001": 'm' is empty and 'c' lists Doñana twice.

**CSV:** F5-world-same-name-two-kinds-left-unjoined.csv

### 6. The 'never worse' guard will throw back correct fixes that remove wrong land
**What's wrong:** When the keys run in saved-copy mode (KPC_KEY_SOURCE=store), kpc_key_never_worse.py compares each area with main. If an area has fewer joined or fewer 'official' parks, the area is kept from main, and for Canada the whole key is kept. Fewer joins is exactly what a correct fix produces when it removes wrong land (findings 1, 3 and 4, and the D1/D4/D5/D9 switches).

**Real parks:**
- Fixing finding 1 makes CA-3496 Exchamsiks PA, CA-6131 Cowichan River Heritage River (BC), CA-5991 Beachville CA (Ontario) and CA-2549 Antelope Park (Saskatchewan) pins. Each province's joined count drops, so the whole Canada key would be refused.
- Fixing finding 4 drops CA-0485 Trout Brook PP (Nova Scotia) to a pin, and Nova Scotia gets refused the same way.
- On the world side, the 43 parks that would become pins under finding 1 (mostly Australia) would hold back AU.

**How many (counted):** Every Canada and world rule change that removes joins. Finding 1 alone: 47 parks become pins. How: the counts() function in kpc_key_never_worse.py only compares totals.

**Confidence:** High. The error is loud (an ::error line), but the correct result never lands, and the easy 'fix' is to switch the guard off.

**Plain fix:** Bug fix: the guard accepts a drop when the change's scope entry lists the expected lost joins and the owner signed it (the same pattern as no-result-change.json).

**Check it yourself:** Read kpc_key_never_worse.py compare() and the 'never worse' step in kpc-ca-key.yml (about line 240).

**CSV:** none (the parks are in F1 and F4)

### 7. The rule switches cannot be turned on from GitHub, and switching them would not move any fingerprint
**What's wrong:** The 14 US rule switches (D1 KPC_SAVED_ID_LAND, D9 KPC_ONE_RECORD_ONE_PARK, D4, D5, D3, plus the nine from Nov 2) are read from the build's environment. No workflow passes them: there is no 'vars.KPC_ONE_RECORD_ONE_PARK' anywhere in .github/workflows. A repo variable set in GitHub settings is never seen, so 'turning a switch on' silently does nothing. The switches are also not in the rules hash or the area hash, so if they were wired up, flipping one would neither move a fingerprint nor trigger a rebuild. And if kpc_key_rules.py ever fails to import, every switch goes off, including the default-ON bug fix KPC_NO_ALL_PATHS (a person's NO checked on every path), with no message.

**Real parks:**
- D9: 169 shared records, 167 parks waiting (changelog, Nov 17).
- D4: 87 parks; D5: 21 joins; D1: 32 Florida parks / 197 rows (changelog, Nov 17).
- CA and world have no switches at all; their only switch-like setting, KPC_JP_A10_CROSSWALK, IS passed and hashed, which is the pattern to copy.

**How many (counted):** 14 switches, 0 wired. How: searched every workflow for each switch name; checked kpc_area_hash.py for which variables are hashed (only KPC_SAVED_ONLY_HOSTS and KPC_JP_A10_CROSSWALK).

**Confidence:** High (a plain text search; it does not depend on GitHub settings I can't see).

**Plain fix:** The switch file in section 2.

**Check it yourself:** Search .github/workflows for KPC_ONE_RECORD_ONE_PARK: there are no hits. Then search kpc_us_key.py for "except Exception: KR = None".

**CSV:** none (US-wide; the park lists are already in the D1/D4/D5/D9 proof notes)

### 8. North Macedonia: the key reads the wrong one of two twin layers and misses the three national parks
**What's wrong:** The government map has two layers with the same title, 'Заштитени подрачја' (protected areas). The key reads layer 94, which holds only small 'natural rarities'. Layer 93, which it skips, holds the national parks, nature parks and landscapes. Both layers also hold 'proposed' sites that are not protected yet.

**Real parks:**
- MK-0002 Galichica National Park, MK-0003 Mavrovo National Park and MK-0004 Pelister National Park: no candidate today; layer 93 has all three, 'protected'.
- MK-0005 Ezerani Nature Park and MK-0016 Matka Canyon: in layer 93, 'protected'.
- MK-0074 Mariovo and MK-0101 Skopska Crna Gora: in layer 93 but only 'proposed'.

**How many (counted):** 17 of the 104 unjoined MK parks match a layer-93 name with the key's own name test (13 protected, 4 proposed). Today only 6 of 116 MK parks are joined. How: one read of layer 93's names, compared with the key's same_name().

**Confidence:** High.

**Plain fix:** Bug fix in data/world-key/sheet-countries.json: add layer 93. New rule: a record marked proposed is never official land (section 2).

**Check it yourself:** Open https://portal.app.gov.mk/arcgis/rest/services/PPRSM/karta37_PPRSM_namena_na_zemjiste_WMS_novo/MapServer/93/query?where=1%3D1&outFields=SiteName,Category,Prot_Stat&returnGeometry=false&f=json

**CSV:** F8-north-macedonia-parks-in-the-unread-layer-93.csv

### 9. Canada draws land from proposal layers and from a different program's layer
**What's wrong:** Canada's layer list has no 'what kind of layer' label (the US got one in D11). Two layers are being joined as if they were the park's own land: Nova Scotia's 'Lands Proposed or Pending Protection' (proposals, not legal boundaries), and BC Recreation Sites (a separate Forests-ministry program), which gets joined to BC provincial parks of the same name.

**Real parks:**
- CA-0479 Sherbrooke Provincial Park (Nova Scotia): drawn only from pending-protection records, including 'Sherbrooke Lake Provincial Park'.
- CA-0704 Bear Creek Provincial Park (BC): also takes recreation sites 'Bear Creek Aspen' and 'Bear Creek Burke'.
- CA-0708 Bonaparte Provincial Park (BC): also takes the 'Bonaparte Lake' recreation site.

**How many (counted):** 159 parks: Nova Scotia 73 (31 of them have no other land), BC 86 (all also have their own land, so these add extra pieces). How: joins whose source is NS_Lands_Proposed_or_Pending_Protection, or 'BC recreatio…' on a park that is not a recreation site.

**Confidence:** High on the counts. Medium on harm for BC (some recreation sites may sit inside the park).

**Plain fix:** Port D11 to data/ca-key/layers.json (owned / designation / proposal / other-program / compilation), plus the 'proposed is never official' rule and the 'land comes from a layer of the park's own kind' rule.

**Check it yourself:** Look at CA-0479 in data/ca-key/CA-NS.json and CA-0704 in CA-BC.json.

**CSV:** F9-canada-land-from-proposed-or-other-program-layers.csv

### 10. World key: one-letter spelling differences and grammatical endings block good joins, and non-Latin names can never match
**What's wrong:** The world matcher needs the cleaned names to be equal, or one to start with the other. A POTA typo ('Gibralter') or a Finnish or Slavic case ending ('Kolin' vs 'Koli', 'Bieszczadzki' vs 'Bieszczady', 'Plitvička jezera' vs 'Plitvice Lakes') sends a park to check, even when its pin sits inside the right area. Separately, the cleaner throws away every letter that isn't a-z, so a Greek, Cyrillic or Arabic name becomes empty and can never match. That is harmless today only because the GR and MK layers happen to carry Latin names, and it will block any future source that doesn't.

**Real parks:**
- GB-0081 Gibralter Point NNR (England): its pin is inside 'GIBRALTAR POINT'.
- FI-0240 Koli National Park (Finland): its pin is inside 'Kolin kansallispuisto'.
- AU-1702 Timmalallie National Park (NSW): its pin is inside 'Timmallallie'. DE-0393 Dresdener Heide: its pin is inside 'Dresdner Heide'.

**How many (counted):** 98 unjoined parks whose pin is inside a record whose cleaned name is at most one or two letters off (FI 15, GB 14, SE 13, AU 10, FR 8, and others). How: the key's own norm(), an edit distance of 15% or less, and the key's own 'pin is inside' reason. A few rows are wrong (DE-0402 Stadtwald vs Stadtrand), so the rule in section 2 keeps a person in the loop.

**Confidence:** High on the count. Medium on the gain.

**Plain fix:** New rule in section 2 ('near-identical name with the pin inside'), plus a transliteration step (Greek / Cyrillic / Arabic to Latin) before cleaning.

**Check it yourself:** Look at GB-0081 in data/world-key/GB.json: 'm' is empty and 'c' says 'the POTA pin is inside it'.

**CSV:** F10-world-one-letter-off-names-with-pin-inside.csv

## 2. The fixes: rule or bug fix, files, proving test

### Finding 1. New rule: an exact name wins over a starts-with name (Canada + world).
- What counts: a record joins by a starts-with match only when no other POTA park in the same province or country has that record's exact cleaned name, and the match ends on a whole word.
- What does not count: part of a word ('watagan' inside 'watagans'), or a starts-with match that leaves an extra place word ('River', 'Delta', 'Falls', 'Creek', 'Hemlock', 'Dam') on one side only. A filler word that is part of a real name ('lago', 'lac', 'lake') may not be dropped if that leaves just the start of the other name.
- When unsure: the record goes to check with the reason 'name also fits <other park>'.
- Files: kpc_ca_key.py (same_name/_pre), kpc_world_key.py (same_name), the scope files, the changelog. Also port KPC_ONE_RECORD_ONE_PARK (D9) to both.
- Proving test: CA-0304, CA-0305 and CA-0306 Mississagi each end with only their own class record; AU-0564 and AU-0565 Mount Barrow each keep their own; IT-2159 loses Torrente Lago. The test fails on today's code.

### Finding 2. Bug fix: read MLIT's park-name code list correctly.
- Files: kpc_world_key.py pull_a10n(): take the cell next to the code, and add 国立公園 / 国定公園 from A10_003 yourself.
- Proving test: a saved copy of the code-list page gives at least 390 codes, not 3, and JP-0102 Abashiri gets a candidate in an offline JP build. Hold this until owner question 1 is answered.

### Finding 3. Port D1 to Canada: a saved id is the land.
- What counts: a hand join or NO is kept while the record still carries the saved name and hectares within 10%. A renumbered record is found again in the same layer by name, hectares and the pin.
- What does not count: a record that has the saved number but a different name.
- When unsure: check, with the reason 'saved id now points at <name>'.
- Files: kpc_ca_key.py (the overrides join and no paths, ~lines 806-846), data/ca-key/overrides.json (rewrite the ids as CPCAD ZONE_ID + name + ha; the tracts files already hold 'sid'), the CA scope file.
- Proving test: give CA-3297's saved id 21900 to a fake record named 'Something Else' 5 km away; the build must not join it and must list CA-3297 for check.

### Finding 4. Bug fix: 'none' blocks name joins.
- Files: kpc_ca_key.py (where ov.get('none') is read), overrides.json (turn each Oct 22 'different place' note into a 'no' by name).
- Proving test: CA-0485 Trout Brook PP with none=true stays a pin even when a same-name record exists.

### Finding 5. New rule: the park's own kind picks between two same-name records (world).
- What counts: the park's name or POTA type says national park / nature reserve / and so on, and exactly ONE same-name record carries that designation (EEA CDDA code, or the national layer's type). That record joins; the Natura 2000 twin goes in the park's 'on' list.
- What does not count: two records that both carry the park's kind, or neither.
- When unsure: check, as today.
- Files: kpc_world_key.py (the join that writes 'same name, more than one kind of area'), data/world-key/eea-designations.json, the world scope file.
- Proving test: ES-0001 Doñana and SK-0003 Slovenský raj each join only their national-park record.

### Finding 6. Bug fix: never-worse accepts declared drops.
- Files: kpc_key_never_worse.py, the workflow steps, and a signed 'expected drops' list next to each scope entry.
- Proving test: a key that loses exactly the listed joins passes; a key that loses one unlisted join is still refused.

### Finding 7. Bug fix plus a simpler design: one committed switch file.
- Design: .github/key-switches.json, in each key's rules hash, holding {switch: {on: [areas or park refs], since: date, approved: ...}}. The builder reads only this file, never the environment, and prints one line, 'switches seen: D9 on for US-FL', on every run. Turning a switch on for one area is then a reviewed one-line change that moves that area's hash and nothing else.
- Safe order (the same everywhere): D1 (saved id is land) first, because the others trust saved rows; then D9 (one record, one park); then D5 (leases), D4 (lakes) and D3 (designations); last the old Nov 2 switches. One switch, one area at a time, smallest area first. Each step's proof is the before/after park list from an offline build, signed like a no-result-change record.
- Also: if kpc_key_rules.py fails to import, the build stops; it should never run with every switch silently off.
- Files: kpc_key_rules.py, kpc_us_key.py, kpc_key_freeze.py (RULE_FILES), kpc_area_hash.py.
- Proving test: with the file saying D9 is on for US-FL only, a build changes FL and nothing else; deleting kpc_key_rules.py makes the build fail, not pass.

### Finding 8. Bug fix + new rule (North Macedonia, and any layer with a status field).
- Add MapServer/93 to data/world-key/sheet-countries.json for MK.
- What counts: a record whose status says protected / designated.
- What does not count: proposed, pending or planned. Those never make an outline; they can be a note.
- When unsure (no status field): as today.
- Proving test: MK-0002 Galichica joins 'Galichica'; MK-0074 Mariovo (proposed) stays a pin with a note.

### Finding 9. Port D11 to Canada: one label per layer.
- Add 'what' to every row of data/ca-key/layers.json: owned / designation / proposal / other-program / compilation (CPCAD).
- What counts: a proposal layer never gives official land. An other-program layer (BC Recreation Sites) joins only a park of that program (POTA type 'Recreation Site').
- When unsure: check.
- Put layers.json under the CA rules hash like state-gis.json.
- Proving test: CA-0479 Sherbrooke PP drops the pending records; CA-0704 Bear Creek PP keeps only its BC Parks record.

### Finding 10. New rule: near-identical name with the pin inside (world).
- What counts: the pin is inside the record, the record is the same kind, the cleaned names differ by 1 letter (2 letters if 10 or more long), and no other record nearby has the exact name. It joins as 'approximate (spelling)', never 'official', and shows on a person's list.
- What does not count: a different word ('Stadtwald' vs 'Stadtrand'), or a record without the pin inside.
- When unsure: check, as today.
- Also: turn Greek / Cyrillic / Arabic into Latin letters before cleaning, so such names stop becoming empty.
- Files: kpc_world_key.py (norm, same_name), kpc_match.py.
- Proving test: GB-0081 Gibralter Point and FI-0240 Koli join; DE-0402 Stadtwald does not.

### Machinery: can a script find which areas a rule change touches?
- Yes, and it is simpler than hand-written scopes. kpc_key_proof.py already builds areas offline with old and new code from identical saved copies. Run it on EVERY area, not a sample, and write the areas whose output changed as the scope. A scope of 'none' then becomes a measured fact rather than a claim. Today nothing checks a 'none' claim except the proof job's sample.
- Files read by a key but kept out of its fingerprint, worth a second look: kpc_overrides.py (loads the US overrides parts), kpc_area_hash.py (decides how each file is sliced per area; a slicing change moves no hash), kpc_master.py read_complete (decides how many records a read returns). Each 'never decides a join' claim in NOT_RULES would be proven by the same all-area A/B run.

## 3. What the keys do well

- The hard-look path in Canada already does what D1 asks for (a name check after a renumber, since Nov 2): Butler's Barracks and L'Anse aux Meadows were caught. It is a good template for finding 3.
- The world NO list wins on every join path (Nov 16), and the world overrides are saved by NAME (all 304 hand joins and 1,605 of 1,609 NOs), so a world renumber can't move a person's decision onto other land.
- Fingerprints are honest about line endings (Nov 16), per-area hashes slice the shared tables, and the one switch-like world setting (KPC_JP_A10_CROSSWALK) is passed AND hashed. That is the model for finding 7.
- Upper / Lower / North / South words, one-side numbers ('Mount Stanley State Forest 1') and map codes ('Nullan I106') are already guarded in many languages.
- Fail-closed habits are everywhere: a short hand file is not used, a missing overrides part stops the build, and a stopped Canada build keeps main.
- The Canada tracts side files already carry CPCAD's stable ZONE_ID and owner type for every joined record, so ports of D1 and D5 have the data they need.

## 4. Questions for you

1. Japan A10 licence: A10 outlines already draw 124 Japan parks while the A10 crosswalk is held 'until the licence is signed'. Is A10 OK for public use (area-tables.json says non-commercial, and KPC is non-commercial)? If yes, finding 2 can go ahead; if not, those 124 parks need another source.
2. Should a 'proposed' or 'pending protection' area ever give a POTA park its outline (Nova Scotia 73 parks, North Macedonia 4)? My suggestion is no: pin plus a note.
3. BC Recreation Sites joined to BC provincial parks (86 parks): keep them as extra pieces, or only for parks POTA lists as recreation sites?
4. Field's Lease and Hayne's Lease Ecological Reserves (BC, CA-3500 and CA-3593) have 'Lease' in their real names. If D5 is ported to Canada, may a park's own name exempt it?
5. For the never-worse guard: OK for a signed 'expected drops' list to let a smaller key through?
6. Switch order: OK to make D1 always first, one area at a time, with the before/after list as the proof?
7. Private land in Canada: 18 parks (mostly Montreal parcs-nature, CA-0877 Strathgartney PP in PEI, CA-1241 Irving Nature Park in NB) are drawn from records whose CPCAD owner is 'Private' or a company. They were all reviewed by hand. Keep them, or mark them 'partial'?

## 5. CSV files (one per finding that touches more than 10 parks)

Folder: /workspace/kpc_handoff/outbox/handoff5-B-csv/

- F1-name-starts-with-takes-a-neighbours-land.csv (494 rows, 254 parks)
- F2-japan-parks-the-national-A10-file-could-name.csv (141 parks)
- F2b-japan-parks-drawn-only-from-A10.csv (124 parks)
- F3-canada-hand-decisions-saved-as-bare-record-numbers.csv (92 rows, 52 parks)
- F4-canada-person-said-not-this-park-but-joined-now.csv (9 parks, included anyway)
- F5-world-same-name-two-kinds-left-unjoined.csv (250 parks)
- F8-north-macedonia-parks-in-the-unread-layer-93.csv (17 parks)
- F9-canada-land-from-proposed-or-other-program-layers.csv (256 rows, 159 parks)
- F10-world-one-letter-off-names-with-pin-inside.csv (98 parks)

## 6. What I did not get to

- No full offline rebuild of CA or world on the proposed rules; the counts come from the published keys and the keys' own name code.
- Compilation copies: 2,714 Canada parks draw from both CPCAD and a provincial layer, and Ontario's 'federal protected areas' is a third copy (CA-0010 Bruce Peninsula NP has three copies of the same land). I didn't measure whether the copies disagree. That is the next thing to look at with the D11 port.
- World licence-limited and privately held sources beyond Japan (RSPB reserves in GB: 183 joins, NGO reserves) were not checked one by one.
- The 2-fer side and the KY key were out of scope.
