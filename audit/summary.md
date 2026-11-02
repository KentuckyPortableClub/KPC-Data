# KPC 10 map audit: summary (2026-11-02)

It decides nothing: it ranks. Score 0 = all pass; +3 OUTSIDE / WAY OFF / MISMATCH / CONFLICT / SPILL, +5 FAR, +1 each softer flag.

## US-KY

- parks: 193 (192 with an outline graded, 1 with no outline, 0 with records this tool can't read)
- pass every test: 120; have flags: 73
- flags: NEAR 45, SELF-INTERSECTION 9, SLIVERS 7, CONFLICT 7, TINY HOLES 6, INVALID 4, OUTSIDE 3, MISMATCH 3, DUPLICATE 2, FAR 1, SPILL 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-4484 | Daniel Boone National Forest | CONFLICT: The record is a proclamation line, not the land the agency owns (+2 more flags). |
| 5 | US-10107 | Big South Fork National Wild and Scenic River | FAR: POTA's pin is 12.9 km outside the outline. |
| 4 | US-0295 | Clarks River National Wildlife Refuge | SELF-INTERSECTION: The shape has problems: Self-intersection[-88.303676 36.848219]; Too few points in geometry component[-88.28961 36.81352]; 1 piece(s) under 10 m wide; 7 hole(s) under 100 m2 (+3 more flags). |
| 4 | US-4526 | George Washington & Jefferson National Forest | MISMATCH: The record name 'Jefferson National Forest' does not match POTA's name 'George Washington & Jefferson National Forest' (score 0.33) (+1 more flag). |
| 4 | US-7958 | Kentucky River Palisades/Tom Dorman State Nature Preserve | MISMATCH: The record name 'Tom Dorman State Nature Preserve' does not match POTA's name 'Kentucky River Palisades/Tom Dorman State Nature Preserve' (score 0.50) (+1 more flag). |
| 3 | US-10103 | The Cumberland River Wilderness Area | OUTSIDE: POTA's pin is 5.5 km outside the outline. |
| 3 | US-10106 | The Rockcastle National Wild and Scenic River | OUTSIDE: POTA's pin is 1.3 km outside the outline. |
| 3 | US-10124 | Clay Wildlife Management Area | SELF-INTERSECTION: The shape has problems: Self-intersection[-83.916660695186 38.3593690229254]; 1 piece(s) under 10 m wide; 2 hole(s) under 100 m2 (+2 more flags). |
| 3 | US-1255 | Fishtrap Lake Wildlife Management Area | OUTSIDE: POTA's pin is 620 m outside the outline. |
| 3 | US-1259 | Green River Lake State Park | CONFLICT: The park is a state park but the record is a wma. |

## US-AK

- parks: 179 (144 with an outline graded, 35 with no outline, 0 with records this tool can't read)
- pass every test: 90; have flags: 89
- flags: TINY HOLES 33, SLIVERS 29, SELF-INTERSECTION 27, NEAR 26, SCATTERED 20, OFF 16, OUTSIDE 14, SPILL 12, MISMATCH 8, FAR 7, DUPLICATE 6, WAY OFF 2

| score | ref | park | why |
|---|---|---|---|
| 12 | US-4537 | Admiralty Island National Monument | FAR: POTA's pin is 877.2 km outside the outline (+3 more flags). |
| 11 | US-10281 | White Mountains National Recreation Area BLM Recreation Management Area | FAR: POTA's pin is 23.2 km outside the outline (+2 more flags). |
| 11 | US-7884 | Kenai Mountains-Turnagain Arm National Heritage Area | FAR: POTA's pin is 575.3 km outside the outline (+2 more flags). |
| 10 | US-0150 | Kodiak National Wildlife Refuge | FAR: POTA's pin is 24.5 km outside the outline (+5 more flags). |
| 10 | US-12708 | Kenai River State Conservation Area | OUTSIDE: POTA's pin is 632 m outside the outline (+3 more flags). |
| 8 | US-0143 | Alaska Maritime National Wildlife Refuge | SPILL: The outline covers 70% of US-7862 Aleutian Islands WW2 National Historic Site, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 8 | US-0144 | Alaska Peninsula National Wildlife Refuge | OUTSIDE: POTA's pin is 5.6 km outside the outline (+5 more flags). |
| 8 | US-0156 | Yukon Delta National Wildlife Refuge | OUTSIDE: POTA's pin is 541 m outside the outline (+5 more flags). |
| 7 | US-4447 | Chugach National Forest | SPILL: The outline covers 93% of US-4537 Admiralty Island National Monument, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4448 | Tongass National Forest | SPILL: The outline covers 100% of US-4538 Misty Fjords National Monument, with no 2-fer row (maybe the wrong record) (+4 more flags). |

## US-AL

- parks: 155 (136 with an outline graded, 19 with no outline, 0 with records this tool can't read)
- pass every test: 63; have flags: 92
- flags: NEAR 34, SELF-INTERSECTION 26, TINY HOLES 21, SLIVERS 15, OFF 11, MISMATCH 10, DUPLICATE 8, OUTSIDE 6, WEAK 2, SPILL 2, SCATTERED 2

| score | ref | park | why |
|---|---|---|---|
| 7 | US-11376 | USS Alabama Battleship Park | OUTSIDE: POTA's pin is 546 m outside the outline (+2 more flags). |
| 6 | US-12996 | Fowl River Access Site BLM Recreation Management Area | OUTSIDE: POTA's pin is 4.9 km outside the outline (+1 more flag). |
| 6 | US-3691 | Grand Bay Savanna Complex Wildlife Management Area | SPILL: The outline covers 98% of US-3692 Heron Bay and Portersville Bay State Fish and Wildlife Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-1043 | Joe Wheeler State Park | SPILL: The outline covers 58% of US-13083 TVA Wheeler Dam Public Park National Recreation Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0136 | Bon Secour National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 13,735 acres (6,982 ac drawn) (+3 more flags). |
| 4 | US-0161 | Wheeler National Wildlife Refuge | NEAR: POTA's pin is 6 m outside the outline (+3 more flags). |
| 4 | US-1040 | Lake Jackson RV Park at Florala State Park | MISMATCH: The record name 'Florala State Park' does not match POTA's name 'Lake Jackson RV Park at Florala State Park' (score 0.33) (+1 more flag). |
| 4 | US-13003 | TVA Little Bear Creek Dam Multiple Use Area | MISMATCH: The record name 'Little Bear Creek Reservoir Retained Land' does not match POTA's name 'TVA Little Bear Creek Dam Multiple Use Area' (score 0.50) (+1 more flag). |
| 4 | US-13004 | TVA Cedar Creek Dam Multiple Use Area | MISMATCH: The record name 'Cedar Creek Reservoir Retained Land' does not match POTA's name 'TVA Cedar Creek Dam Multiple Use Area' (score 0.40) (+1 more flag). |
| 4 | US-13005 | TVA Big Bear Creek Dam Multiple Use Area | MISMATCH: The record name 'Bear Creek Reservoir Retained Land' does not match POTA's name 'TVA Big Bear Creek Dam Multiple Use Area' (score 0.33) (+1 more flag). |

## US-AR

- parks: 306 (228 with an outline graded, 78 with no outline, 0 with records this tool can't read)
- pass every test: 141; have flags: 165
- flags: NEAR 83, TINY HOLES 41, STALE CHECK 38, OFF 32, DUPLICATE 30, SELF-INTERSECTION 20, SPILL 15, SLIVERS 14, MISMATCH 14, OUTSIDE 11, CONFLICT 9, WAY OFF 7, WEAK 4, SCATTERED 3, INVALID 2, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 11 | US-4373 | Blue Mountain Lake (Outlet Area and Waveland Park) National Recreation Area | MISMATCH: The record name 'Blue Mountain Recreation Area' does not match POTA's name 'Blue Mountain Lake (Outlet Area and Waveland Park) National Recreation Area' (score 0.50) (+4 more flags). |
| 10 | US-4425 | Ozark-St. Francis National Forest | MISMATCH: The record name 'Ozark Purchase Unit' does not match POTA's name 'Ozark-St. Francis National Forest' (score 0.33) (+5 more flags). |
| 8 | US-0171 | White River National Wildlife Refuge | SPILL: The outline covers 57% of US-11355 Cook’s Lake Nature Center Nature Recreation Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-0038 | Hot Springs National Park | SPILL: The outline covers 90% of US-7441 Gulpha Gorge National Recreation Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-0163 | Big Lake National Wildlife Refuge | OFF: The outline is 1.5 times smaller than the official 32,626 acres (21,738 ac drawn) (+6 more flags). |
| 7 | US-1092 | Lake Fort Smith State Park | WAY OFF: The outline is 6.3 times bigger than the official 257 acres (1,613 ac drawn) (+2 more flags). |
| 7 | US-11713 | Dale Bumpers White River National Wildlife Refuge National Wildlife Area | SPILL: The outline covers 57% of US-11355 Cook’s Lake Nature Center Nature Recreation Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-12331 | Greers Ferry Lake Tailwater State Recreation Area | MISMATCH: The record name 'Greers Ferry Recreation Area' does not match POTA's name 'Greers Ferry Lake Tailwater State Recreation Area' (score 0.67) (+2 more flags). |
| 7 | US-4424 | Ouachita National Forest | SPILL: The outline covers 100% of US-7274 Cedar Creek Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-7304 | McIlroy Madison County Wildlife Management Area | OUTSIDE: POTA's pin is 812 m outside the outline (+2 more flags). |

## US-AZ

- parks: 123 (95 with an outline graded, 28 with no outline, 0 with records this tool can't read)
- pass every test: 48; have flags: 75
- flags: STALE CHECK 46, SELF-INTERSECTION 15, NEAR 14, OFF 13, TINY HOLES 11, SLIVERS 9, SPILL 7, MISMATCH 5, OUTSIDE 3, DUPLICATE 2, WEAK 2, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-4432 | Tonto National Forest | OUTSIDE: POTA's pin is 3.9 km outside the outline (+3 more flags). |
| 7 | US-0771 | Coronado National Memorial | SPILL: The outline covers 99% of US-1055 Catalina State Park, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4427 | Apache-Sitgreaves National Forest | MISMATCH: The record name 'Sitgreaves National Forest' does not match POTA's name 'Apache-Sitgreaves National Forest' (score 0.50) (+2 more flags). |
| 6 | US-4429 | Coronado National Forest | SPILL: The outline covers 99% of US-1055 Catalina State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-11943 | Sonoita Creek State Natural Area | OUTSIDE: POTA's pin is 1.3 km outside the outline (+2 more flags). |
| 5 | US-4428 | Coconino National Forest | SPILL: The outline covers 34% of US-1068 Slide Rock State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-10513 | Granite Mountain Hotshots State Park | OUTSIDE: POTA's pin is 560 m outside the outline (+1 more flag). |
| 4 | US-1054 | Buckskin Mountain State Park | SPILL: The outline covers 71% of US-3390 River Island State Park, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-1067 | Roper Lake State Park | SPILL: The outline covers 43% of US-11944 Dankworth Pond State Park, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-13335 | Saddleback Mountain BLM Special Recreation Management Area | MISMATCH: The record name 'Saddleback Mountain Facility Area' does not match POTA's name 'Saddleback Mountain BLM Special Recreation Management Area' (score 0.50) (+1 more flag). |

## US-CA

- parks: 410 (391 with an outline graded, 19 with no outline, 0 with records this tool can't read)
- pass every test: 69; have flags: 341
- flags: STALE CHECK 239, TINY HOLES 101, NEAR 68, SELF-INTERSECTION 48, OFF 43, SLIVERS 40, DUPLICATE 21, MISMATCH 21, SPILL 18, OUTSIDE 17, SCATTERED 17, FAR 2, INVALID 1, WEAK 1, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-4457 | Klamath National Forest | SPILL: The outline covers 40% of US-12115 Sáttítla Highlands Natural Monument, with no 2-fer row (maybe the wrong record) (+6 more flags). |
| 8 | US-4458 | Lake Tahoe Basin Management Unit National Forest | MISMATCH: The record name 'Tahoe National Forest' does not match POTA's name 'Lake Tahoe Basin Management Unit National Forest' (score 0.50) (+5 more flags). |
| 8 | US-4462 | Plumas National Forest | OUTSIDE: POTA's pin is 1.4 km outside the outline (+5 more flags). |
| 8 | US-4468 | Stanislaus National Forest | SPILL: The outline covers 33% of US-0894 Tuolumne National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-0208 | San Diego National Wildlife Refuge | OUTSIDE: POTA's pin is 4.5 km outside the outline (+4 more flags). |
| 7 | US-3525 | Old Sacramento State Historical Park | SPILL: The outline covers 100% of US-3415 California State Railroad Museum State Park, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4461 | Modoc National Forest | SPILL: The outline covers 36% of US-12115 Sáttítla Highlands Natural Monument, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4465 | Shasta-Trinity National Forest | MISMATCH: The record name 'Trinity National Forest' does not match POTA's name 'Shasta-Trinity National Forest' (score 0.50) (+4 more flags). |
| 7 | US-4466 | Sierra National Forest | SPILL: The outline covers 100% of US-0884 Kings River National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-0197 | Kern National Wild and Scenic River | FAR: POTA's pin is 60.5 km outside the outline (+1 more flag). |

## US-CO

- parks: 276 (265 with an outline graded, 11 with no outline, 0 with records this tool can't read)
- pass every test: 89; have flags: 187
- flags: NEAR 73, TINY HOLES 46, OUTSIDE 46, SELF-INTERSECTION 31, MISMATCH 22, OFF 20, SLIVERS 16, DUPLICATE 15, SCATTERED 12, SPILL 8, WEAK 3, CONFLICT 2, WAY OFF 2, INVALID 1, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-4404 | Pike National Forest | FAR: POTA's pin is 18.8 km outside the outline (+4 more flags). |
| 8 | US-12140 | Spinney Mountain State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+3 more flags). |
| 7 | US-11897 | Beaver Creek BLM Wilderness Area | OUTSIDE: POTA's pin is 818 m outside the outline (+2 more flags). |
| 7 | US-1208 | Arkansas River Headwaters Recreation Park | OUTSIDE: POTA's pin is 3.7 km outside the outline (+4 more flags). |
| 7 | US-4403 | Medicine Bow - Routt National Forest | MISMATCH: The record name 'Medicine Bow National Forest' does not match POTA's name 'Medicine Bow - Routt National Forest' (score 0.67) (+4 more flags). |
| 7 | US-4405 | Rio Grande National Forest | SPILL: The outline covers 100% of US-9614 Big Meadows Reservoir State Wildlife Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4406 | Roosevelt National Forest | SPILL: The outline covers 99% of US-12106 Brainard Lake Recreation Area National Forest, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4407 | San Isabel National Forest | SPILL: The outline covers 55% of US-4411 Browns Canyon National Monument, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4408 | San Juan National Forest | SPILL: The outline covers 100% of US-9606 Andrews Lake State Wildlife Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-0185 | Hugo State Wildlife Area | OUTSIDE: POTA's pin is 2.3 km outside the outline (+1 more flag). |

## US-CT

- parks: 157 (152 with an outline graded, 5 with no outline, 0 with records this tool can't read)
- pass every test: 76; have flags: 81
- flags: TINY HOLES 43, NEAR 23, SPILL 18, SELF-INTERSECTION 17, SLIVERS 12, OFF 8, MISMATCH 4, DUPLICATE 4, CONFLICT 2, WAY OFF 2, OUTSIDE 2, SCATTERED 2, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-12459 | Housatonic River Southern Fields Wildlife Management Area | MISMATCH: The record name 'Housatonic River Wildlife Management Area' does not match POTA's name 'Housatonic River Southern Fields Wildlife Management Area' (score 0.33) (+2 more flags). |
| 7 | US-7541 | Salmon River State Forest | SPILL: The outline covers 99% of US-1660 Day Pond State Park, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-1658 | Connecticut Valley Railroad State Park | SPILL: The outline covers 100% of US-1664 Eagle Landing State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-7531 | Cockaponset State Forest | SPILL: The outline covers 57% of US-1656 Chatfield Hollow State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-10961 | Mattatuck State Forest | SPILL: The outline covers 64% of US-13483 Humaston Brook State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-12092 | Nipmuck State Forest | SPILL: The outline covers 93% of US-1648 Bigelow Hollow State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-12604 | Meshomasic State Forest | SPILL: The outline covers 40% of US-1669 Gay City State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-4369 | Shenipsit State Forest | SPILL: The outline covers 35% of US-6867 Nye Holman State Forest, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-7530 | Centennial Watershed State Forest | NEAR: POTA's pin is 23 m outside the outline (+4 more flags). |
| 5 | US-7548 | Pachaug State Forest | SPILL: The outline covers 38% of US-7537 Natchaug State Forest, with no 2-fer row (maybe the wrong record) (+2 more flags). |

## US-DC

- parks: 35 (29 with an outline graded, 6 with no outline, 0 with records this tool can't read)
- pass every test: 23; have flags: 12
- flags: NEAR 7, SLIVERS 7, MISMATCH 2, SELF-INTERSECTION 2, TINY HOLES 2, DUPLICATE 2, SPILL 1

| score | ref | park | why |
|---|---|---|---|
| 10 | US-0654 | National Capital Parks - East Park | MISMATCH: The record name 'National Capital Parks' does not match POTA's name 'National Capital Parks - East Park' (score 0.50) (+5 more flags). |
| 7 | US-13543 | US National Arboretum Botanical Gardens | MISMATCH: The record name 'National Arboretum' does not match POTA's name 'US National Arboretum Botanical Gardens' (score 0.25) (+4 more flags). |
| 2 | US-0814 | Ford's Theatre National Historic Site | NEAR: POTA's pin is 13 m outside the outline (+1 more flag). |
| 2 | US-0848 | Mary McLeod Bethune Council House National Historic Site | NEAR: POTA's pin is 4 m outside the outline (+1 more flag). |
| 1 | US-0656 | Rock Creek Park | SLIVERS: The shape has problems: 1 piece(s) under 10 m wide. |
| 1 | US-0670 | George Washington Memorial Parkway | SLIVERS: The shape has problems: 60 piece(s) under 10 m wide. |
| 1 | US-0795 | World War I National Memorial | DUPLICATE: Another park number uses the same record: US-0796. |
| 1 | US-0796 | World War II National Memorial | DUPLICATE: Another park number uses the same record: US-0795. |
| 1 | US-0805 | Carter G. Woodson Home National Historic Site | NEAR: POTA's pin is 2 m outside the outline. |
| 1 | US-0853 | Pennsylvania Avenue National Historic Site | SLIVERS: The shape has problems: 2 piece(s) under 10 m wide. |

## US-DE

- parks: 89 (85 with an outline graded, 4 with no outline, 0 with records this tool can't read)
- pass every test: 28; have flags: 61
- flags: TINY HOLES 31, OFF 18, SELF-INTERSECTION 11, NEAR 11, SPILL 10, SLIVERS 10, DUPLICATE 6, MISMATCH 5, WAY OFF 3, OUTSIDE 2, STALE CHECK 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-1734 | Delaware Seashore State Park | WAY OFF: The outline is 8.5 times bigger than the official 232 acres (1,972 ac drawn) (+2 more flags). |
| 7 | US-7648 | Chesapeake and Delaware Canal Conservation Area | MISMATCH: The record name 'C&D Canal Wildlife Area' does not match POTA's name 'Chesapeake and Delaware Canal Conservation Area' (score 0.33) (+4 more flags). |
| 6 | US-0898 | White Clay Creek National Wild and Scenic River | SPILL: The outline covers 41% of US-9881 Pomeroy and Newark National Recreation Trail, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-7653 | Tony Florio Woodland Beach State Wildlife Area | MISMATCH: The record name 'Woodland Beach Wildlife Area' does not match POTA's name 'Tony Florio Woodland Beach State Wildlife Area' (score 0.50) (+3 more flags). |
| 5 | US-1743 | White Clay Creek State Park | SPILL: The outline covers 93% of US-9881 Pomeroy and Newark National Recreation Trail, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-7645 | Assawoman Bay State Wildlife Area | MISMATCH: The record name 'Assawoman Wildlife Area' does not match POTA's name 'Assawoman Bay State Wildlife Area' (score 0.50) (+2 more flags). |
| 5 | US-9890 | James Branch State Nature Preserve | SPILL: The outline covers 35% of US-10670 Chipmans Pond State Fishing Lake, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-10688 | Tubmill Pond State Fishing Lake | MISMATCH: The record name 'Tub Mill Pond and Access Site' does not match POTA's name 'Tubmill Pond State Fishing Lake' (score 0.53) (+1 more flag). |
| 4 | US-11812 | Trap Pond State Fishing Lake | SPILL: The outline covers 33% of US-10687 Trussum Pond State Fishing Lake, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-1730 | Alapocas Run State Park | SPILL: The outline covers 55% of US-9878 Northern Delaware Greenway National Recreation Trail, with no 2-fer row (maybe the wrong record) (+1 more flag). |

## US-FL

- parks: 460 (442 with an outline graded, 18 with no outline, 0 with records this tool can't read)
- pass every test: 251; have flags: 209
- flags: TINY HOLES 89, STALE CHECK 71, SLIVERS 61, SELF-INTERSECTION 51, SPILL 33, OFF 26, NEAR 25, DUPLICATE 13, SCATTERED 11, MISMATCH 10, WAY OFF 5, OUTSIDE 4, FAR 1, INVALID 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-0245 | Lake Wales Ridge Wildlife Management Area | SPILL: The outline covers 99% of US-5624 Jack Creek State Conservation Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-12126 | Stormwater Treatment Area 5/6 State Conservation Area | MISMATCH: The record name 'Stormwater Treatment Areas' does not match POTA's name 'Stormwater Treatment Area 5/6 State Conservation Area' (score 0.50) (+2 more flags). |
| 7 | US-12127 | Stormwater Treatment Area 1 West State Conservation Area | MISMATCH: The record name 'Stormwater Treatment Areas' does not match POTA's name 'Stormwater Treatment Area 1 West State Conservation Area' (score 0.50) (+2 more flags). |
| 7 | US-12128 | Stormwater Treatment Area 1 East State Conservation Area | MISMATCH: The record name 'Stormwater Treatment Areas' does not match POTA's name 'Stormwater Treatment Area 1 East State Conservation Area' (score 0.50) (+2 more flags). |
| 7 | US-4614 | Blackwater River State Forest | SPILL: The outline covers 37% of US-8335 Yellow River Water Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4646 | Withlacoochee State Forest | SPILL: The outline covers 100% of US-7879 Citrus Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-6744 | Terra Ceia Preserve Frog Creek State Conservation Area | OUTSIDE: POTA's pin is 1.6 km outside the outline (+2 more flags). |
| 6 | US-12122 | S-65E Impoundment and Paradise Run State Conservation Area | OUTSIDE: POTA's pin is 844 m outside the outline (+1 more flag). |
| 6 | US-3637 | Marjorie Harris Carr Cross State Park | SPILL: The outline covers 56% of US-6295 Caravelle Ranch Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-6288 | Apalachicola River Wildlife Area | WAY OFF: The outline is 6.8 times bigger than the official 100,581 acres (684,707 ac drawn) (+3 more flags). |

## US-GA

- parks: 237 (221 with an outline graded, 16 with no outline, 0 with records this tool can't read)
- pass every test: 112; have flags: 125
- flags: STALE CHECK 41, TINY HOLES 28, NEAR 27, DUPLICATE 18, OFF 17, SELF-INTERSECTION 16, SPILL 16, SLIVERS 12, MISMATCH 7, SCATTERED 2, INVALID 1, WAY OFF 1, OUTSIDE 1, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-4473 | Chattahoochee-Oconee National Forest | MISMATCH: The record name 'Chattahoochee National Forest' does not match POTA's name 'Chattahoochee-Oconee National Forest' (score 0.50) (+4 more flags). |
| 8 | US-7914 | Sandhills East Wildlife Management Area | MISMATCH: The record name 'SANDHILLS WMA' does not match POTA's name 'Sandhills East Wildlife Management Area' (score 0.50) (+3 more flags). |
| 7 | US-9795 | Sandhills West Wildlife Management Area | MISMATCH: The record name 'SANDHILLS WMA' does not match POTA's name 'Sandhills West Wildlife Management Area' (score 0.50) (+2 more flags). |
| 7 | US-9797 | Chattahoochee Fall Line Hilliard Tract Wildlife Management Area | SPILL: The outline covers 99% of US-7906 Chattahoochee Fall Line Almo Tract Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-3741 | Coosawattee Wildlife Management Area | SPILL: The outline covers 47% of US-7899 Carter's Lake Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-7906 | Chattahoochee Fall Line Almo Tract Wildlife Management Area | SPILL: The outline covers 94% of US-9797 Chattahoochee Fall Line Hilliard Tract Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-9793 | Ball's Ferry Property Wildlife Management Area | MISMATCH: The record name 'Balls Ferry State Park' does not match POTA's name 'Ball's Ferry Property Wildlife Management Area' (score 0.67) (+1 more flag). |
| 5 | US-7138 | Chestatee Wildlife Management Area | SPILL: The outline covers 100% of US-7473 DeSoto Falls National Recreation Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-7899 | Carter's Lake Wildlife Management Area | SPILL: The outline covers 39% of US-3741 Coosawattee Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0261 | Bond Swamp National Wildlife Refuge | NEAR: POTA's pin is 6 m outside the outline (+3 more flags). |

## US-HI

- parks: 102 (92 with an outline graded, 10 with no outline, 0 with records this tool can't read)
- pass every test: 30; have flags: 72
- flags: STALE CHECK 41, NEAR 19, TINY HOLES 14, DUPLICATE 8, OFF 7, SLIVERS 7, OUTSIDE 5, SPILL 4, SELF-INTERSECTION 3, MISMATCH 2, WAY OFF 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-10914 | Ka‘ena Point State Trail | OUTSIDE: POTA's pin is 1.9 km outside the outline (+3 more flags). |
| 5 | US-2209 | Ahupua'a O Kahana State Park | SPILL: The outline covers 96% of US-10916 Kapaʻeleʻele State Trail, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-2215 | Koke`e State Park | MISMATCH: The record name 'Koke'e State Park' does not match POTA's name 'Koke`e State Park' (score 0.50) (+2 more flags). |
| 5 | US-2226 | Wailua River State Park | OUTSIDE: POTA's pin is 1.1 km outside the outline (+2 more flags). |
| 5 | US-6420 | Kiholo  Reserve State Reserve | WAY OFF: The outline is 448.4 times bigger than the official 10 acres (4,484 ac drawn) (+2 more flags). |
| 4 | US-10913 | Diamond Head Summit State Trail | MISMATCH: The record name 'Diamond Head State Monument' does not match POTA's name 'Diamond Head Summit State Trail' (score 0.67) (+1 more flag). |
| 4 | US-10918 | Waʻahila Ridge State Trail | OUTSIDE: POTA's pin is 1.5 km outside the outline (+1 more flag). |
| 4 | US-2212 | Ka'ena Point State Park | SLIVERS: The shape has problems: 1 piece(s) under 10 m wide; 1 hole(s) under 100 m2 (+3 more flags). |
| 4 | US-4565 | Ala Kahakai National Historic Trail | SPILL: The outline covers 54% of US-6421 Kohala Historical Sites State Preserve, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-6413 | Keawa Heiau State Recreation Area | SPILL: The outline covers 39% of US-10917 ʻAiea Loop State Trail, with no 2-fer row (maybe the wrong record) (+1 more flag). |

## US-IA

- parks: 181 (180 with an outline graded, 1 with no outline, 0 with records this tool can't read)
- pass every test: 122; have flags: 59
- flags: TINY HOLES 23, NEAR 19, SELF-INTERSECTION 12, OFF 6, MISMATCH 4, SLIVERS 4, DUPLICATE 4, SPILL 3, CONFLICT 3, OUTSIDE 2, SCATTERED 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 13 | US-0270 | Iowa Wetland Management District | OUTSIDE: POTA's pin is 2.6 km outside the outline (+6 more flags). |
| 5 | US-0272 | Port Louisa National Wildlife Refuge | SPILL: The outline covers 74% of US-9975 Iowa River Corridor Wildlife Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-2281 | Big Creek State Park | CONFLICT: The park is a state park but the record is a wma (+1 more flag). |
| 4 | US-5735 | Lower Gar State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+1 more flag). |
| 4 | US-9975 | Iowa River Corridor Wildlife Area | SPILL: The outline covers 55% of US-0272 Port Louisa National Wildlife Refuge, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 3 | US-10174 | Marble Beach State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it. |
| 3 | US-2309 | Okamanpedan (Tuttle) State Park | MISMATCH: The record name 'Okamanpedan State Park' does not match POTA's name 'Okamanpedan (Tuttle) State Park' (score 0.50). |
| 3 | US-2329 | Wild Cat Den State Park | MISMATCH: The record name 'Wildcat Den State Park' does not match POTA's name 'Wild Cat Den State Park' (score 0.50). |
| 3 | US-4236 | Upper Mississippi River National Wildlife Refuge | SELF-INTERSECTION: The shape has problems: Self-intersection[-91.1624204015247 43.1481017249954]; 1 piece(s) under 10 m wide; 11 hole(s) under 100 m2 (+2 more flags). |
| 3 | US-4661 | Shimek State Forest | NEAR: POTA's pin is 410 m outside the outline (+2 more flags). |

## US-ID

- parks: 362 (228 with an outline graded, 134 with no outline, 0 with records this tool can't read)
- pass every test: 176; have flags: 186
- flags: STALE CHECK 92, TINY HOLES 37, MISMATCH 35, NEAR 34, SPILL 29, SELF-INTERSECTION 23, SLIVERS 20, DUPLICATE 16, OFF 13, SCATTERED 10, OUTSIDE 8, CONFLICT 7, WEAK 4, INVALID 1, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 13 | US-4478 | Nez Perce National Forest | OUTSIDE: POTA's pin is 980 m outside the outline (+6 more flags). |
| 11 | US-13296 | Upper Salmon River Access BLM Recreation Management Area | FAR: POTA's pin is 29.9 km outside the outline (+2 more flags). |
| 10 | US-11251 | Magic Reservoir BLM Recreation Management Area | MISMATCH: The record name 'Magic Reservoir' does not match POTA's name 'Magic Reservoir BLM Recreation Management Area' (score 0.50) (+3 more flags). |
| 10 | US-4475 | Caribou-Targhee National Forest | MISMATCH: The record name 'Targhee National Forest' does not match POTA's name 'Caribou-Targhee National Forest' (score 0.50) (+5 more flags). |
| 9 | US-4477 | Idaho Panhandle National Forest | MISMATCH: The record name 'Kaniksu National Forest' does not match POTA's name 'Idaho Panhandle National Forest' (score 0.00) (+4 more flags). |
| 9 | US-4480 | Salmon-Challis National Forest | MISMATCH: The record name 'Salmon National Forest' does not match POTA's name 'Salmon-Challis National Forest' (score 0.50) (+4 more flags). |
| 8 | US-12180 | Owyhee Front BLM Recreation Management Area | MISMATCH: The record name 'Owyhee Front Trails - South Zone' does not match POTA's name 'Owyhee Front BLM Recreation Management Area' (score 0.67) (+3 more flags). |
| 8 | US-4474 | Boise National Forest | SPILL: The outline covers 100% of US-11391 Deadwood Reservoir State Fishing Lake, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 8 | US-4479 | Payette National Forest | SPILL: The outline covers 100% of US-7828 Reed Ranch Airstrip State Recreation Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 8 | US-4481 | Sawtooth National Forest | SPILL: The outline covers 33% of US-10383 Jim McClure-Jerry Peak Wilderness Wilderness Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |

## US-IL

- parks: 219 (208 with an outline graded, 11 with no outline, 0 with records this tool can't read)
- pass every test: 22; have flags: 197
- flags: STALE CHECK 186, NEAR 38, TINY HOLES 18, SLIVERS 16, SELF-INTERSECTION 15, OFF 8, MISMATCH 8, DUPLICATE 7, CONFLICT 6, SPILL 4, OUTSIDE 4, WEAK 2, SCATTERED 2

| score | ref | park | why |
|---|---|---|---|
| 8 | US-0990 | Donnelley/DePue State Park | MISMATCH: The record name 'Lake DePue State Fish and Wildlife Area' does not match POTA's name 'Donnelley/DePue State Park' (score 0.50) (+3 more flags). |
| 8 | US-11351 | Weinberg-King Spunky Bottoms Unit State Park | MISMATCH: The record name 'Weinberg-King State Fish and Wildlife Area' does not match POTA's name 'Weinberg-King Spunky Bottoms Unit State Park' (score 0.50) (+3 more flags). |
| 8 | US-4482 | Shawnee National Forest | SPILL: The outline covers 100% of US-10661 Oakwood Bottoms USFS Recreation Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-10787 | Weinberg-King Scripps Unit State Park | MISMATCH: The record name 'Weinberg-King State Fish and Wildlife Area' does not match POTA's name 'Weinberg-King Scripps Unit State Park' (score 0.67) (+2 more flags). |
| 7 | US-4134 | Kaskaskia River State Fish and Wildlife Area | OUTSIDE: POTA's pin is 652 m outside the outline (+4 more flags). |
| 7 | US-4138 | Manito PHA State Park | MISMATCH: The record name 'Manito State Habitat Area' does not match POTA's name 'Manito PHA State Park' (score 0.50) (+2 more flags). |
| 5 | US-1015 | Pere Marquette State Park | SPILL: The outline covers 100% of US-4118 Copperhead Hollow State Wildlife Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-10786 | Siloam Springs Buckhorn Unit State Park | MISMATCH: The record name 'Siloam Springs State Park' does not match POTA's name 'Siloam Springs Buckhorn Unit State Park' (score 0.67) (+2 more flags). |
| 5 | US-4092 | Salem Unit of Apple River Canyon State Park | MISMATCH: The record name 'Apple River Canyon State Park' does not match POTA's name 'Salem Unit of Apple River Canyon State Park' (score 0.67) (+2 more flags). |
| 5 | US-4106 | Weinberg-King State Park | CONFLICT: The park is a state park but the record is a wma (+2 more flags). |

## US-IN

- parks: 229 (189 with an outline graded, 20 with no outline, 20 with records this tool can't read)
- pass every test: 161; have flags: 68; source down (retry): 81
- flags: TINY HOLES 20, NEAR 20, SPILL 17, MISMATCH 15, DUPLICATE 10, SELF-INTERSECTION 9, SLIVERS 9, OUTSIDE 9, OFF 2, SCATTERED 2

| score | ref | park | why |
|---|---|---|---|
| 9 | US-4170 | Hardin Ridge on Monroe Lake State Recreation Area | MISMATCH: The record name 'Monroe Recreation Area' does not match POTA's name 'Hardin Ridge on Monroe Lake State Recreation Area' (score 0.33) (+4 more flags). |
| 9 | US-4171 | Paynetown on Monroe Lake State Recreation Area | MISMATCH: The record name 'Monroe Recreation Area' does not match POTA's name 'Paynetown on Monroe Lake State Recreation Area' (score 0.50) (+4 more flags). |
| 9 | US-4483 | Hoosier National Forest | OUTSIDE: POTA's pin is 1.5 km outside the outline (+4 more flags). |
| 8 | US-4168 | Frances Slocum on Mississinewa Lake State Recreation Area | MISMATCH: The record name 'Mississinewa Recreation Area' does not match POTA's name 'Frances Slocum on Mississinewa Lake State Recreation Area' (score 0.33) (+3 more flags). |
| 8 | US-4169 | Miami on Mississinewa Lake State Recreation Area | MISMATCH: The record name 'Mississinewa Recreation Area' does not match POTA's name 'Miami on Mississinewa Lake State Recreation Area' (score 0.50) (+3 more flags). |
| 7 | US-12020 | Prophetstown Fen State Nature Preserve | OUTSIDE: POTA's pin is 3.2 km outside the outline (+2 more flags). |
| 7 | US-4182 | Trine at Pokagon State Recreation Area | SOURCE DOWN: OUTSIDE: POTA's pin is 606 m outside the outline (+2 more flags). |
| 6 | US-10179 | Ten O' Clock Line State Nature Preserve | OUTSIDE: POTA's pin is 1.0 km outside the outline (+1 more flag). |
| 6 | US-4161 | Quakertown on Brookville Lake State Recreation Area | OUTSIDE: POTA's pin is 641 m outside the outline (+1 more flag). |
| 5 | US-4186 | Big Walnut - Tall Timbers Trail State Nature Preserve | MISMATCH: The record name 'Big Walnut Nature Preserve - Tract 1' does not match POTA's name 'Big Walnut - Tall Timbers Trail State Nature Preserve' (score 0.50) (+2 more flags). |

## US-KS

- parks: 145 (123 with an outline graded, 20 with no outline, 2 with records this tool can't read)
- pass every test: 30; have flags: 115; source down (retry): 23
- flags: STALE CHECK 100, DUPLICATE 20, TINY HOLES 15, NEAR 15, OFF 7, OUTSIDE 6, SELF-INTERSECTION 4, MISMATCH 3, WAY OFF 2, WEAK 1, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-7397 | Pottawatomie No 2 State Fishing Lake | OUTSIDE: POTA's pin is 510 m outside the outline (+2 more flags). |
| 6 | US-7406 | Mined Land State Fishing Lake | WAY OFF: The outline is 10.3 times bigger than the official 1,436 acres (14,846 ac drawn) (+3 more flags). |
| 5 | US-2330 | Cedar Bluff State Park | SOURCE DOWN: OUTSIDE: POTA's pin is 1.1 km outside the outline (+2 more flags). |
| 5 | US-7399 | Tuttle Creek Willow State Fishing Lake | MISMATCH: The record name 'Tuttle Creek State Parks' does not match POTA's name 'Tuttle Creek Willow State Fishing Lake' (score 0.67) (+2 more flags). |
| 5 | US-7925 | El Dorado State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 4 | US-12398 | Olathe Prairie Center State Preserve | MISMATCH: The record name 'Prairie Center' does not match POTA's name 'Olathe Prairie Center State Preserve' (score 0.67) (+1 more flag). |
| 4 | US-7396 | Pottawatomie No 1 State Fishing Lake | WAY OFF: The outline is 11.0 times bigger than the official 17 acres (187 ac drawn) (+1 more flag). |
| 4 | US-7924 | Council Grove State Wildlife Area | OUTSIDE: POTA's pin is 1.2 km outside the outline (+1 more flag). |
| 4 | US-7928 | Glen Elder State Wildlife Area | NEAR: POTA's pin is 296 m outside the outline (+3 more flags). |
| 4 | US-7934 | Lovewell State Wildlife Area | NEAR: POTA's pin is 222 m outside the outline (+3 more flags). |

## US-LA

- parks: 123 (116 with an outline graded, 7 with no outline, 0 with records this tool can't read)
- pass every test: 69; have flags: 54
- flags: TINY HOLES 22, OFF 21, SELF-INTERSECTION 19, NEAR 13, STALE CHECK 12, SLIVERS 3, MISMATCH 2, OUTSIDE 1, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 4 | US-0296 | Atchafalaya National Wildlife Refuge | OUTSIDE: POTA's pin is 1.6 km outside the outline (+1 more flag). |
| 4 | US-0302 | Bogue Chitto National Wildlife Refuge | NEAR: POTA's pin is 475 m outside the outline (+3 more flags). |
| 4 | US-0305 | Cat Island National Wildlife Refuge | NEAR: POTA's pin is 32 m outside the outline (+3 more flags). |
| 4 | US-10097 | Queen Bess Island Wildlife Refuge | MISMATCH: The record name 'Queen Bess Wildlife Refuge' does not match POTA's name 'Queen Bess Island Wildlife Refuge' (score 0.67) (+1 more flag). |
| 4 | US-4064 | Lake Ramsey Savannah Wildlife Management Area | MISMATCH: The record name 'Lake Ramsay Savannah Wildlife Management Area' does not match POTA's name 'Lake Ramsey Savannah Wildlife Management Area' (score 0.50) (+1 more flag). |
| 3 | US-0297 | Bayou Cocodrie National Wildlife Refuge | NEAR: POTA's pin is 310 m outside the outline (+2 more flags). |
| 3 | US-0298 | Bayou Sauvage National Wildlife Refuge | OFF: The outline is 1.9 times smaller than the official 52,736 acres (27,655 ac drawn) (+2 more flags). |
| 3 | US-0307 | D'Arbonne National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 35,278 acres (17,646 ac drawn) (+2 more flags). |
| 3 | US-0311 | Lacassine National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 66,509 acres (33,272 ac drawn) (+2 more flags). |
| 3 | US-0312 | Lake Ophelia National Wildlife Refuge | NEAR: POTA's pin is 108 m outside the outline (+2 more flags). |

## US-MA

- parks: 421 (413 with an outline graded, 8 with no outline, 0 with records this tool can't read)
- pass every test: 169; have flags: 252
- flags: TINY HOLES 160, NEAR 93, OFF 33, SELF-INTERSECTION 27, SLIVERS 22, STALE CHECK 12, OUTSIDE 8, SPILL 4, WAY OFF 4, DUPLICATE 4, FAR 2, MISMATCH 2, CONFLICT 1, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-0672 | Cape Cod National Seashore | SPILL: The outline covers 100% of US-11638 Marconi Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+6 more flags). |
| 6 | US-11473 | Montague Wildlife Management Area | OUTSIDE: POTA's pin is 508 m outside the outline (+3 more flags). |
| 5 | US-0322 | Mashpee National Wildlife Refuge | OUTSIDE: POTA's pin is 1.3 km outside the outline (+2 more flags). |
| 5 | US-0897 | Westfield National Wild and Scenic River | FAR: POTA's pin is 28.0 km outside the outline. |
| 5 | US-11401 | Cummington Wildlife Management Area | FAR: POTA's pin is 15.4 km outside the outline. |
| 5 | US-8405 | Charles River State Reserve | OFF: The outline is 4.0 times bigger than the official 971 acres (3,904 ac drawn) (+4 more flags). |
| 5 | US-8421 | Neponset River State Reserve | SPILL: The outline covers 65% of US-8385 Farnham-Connolly State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-11400 | Chalet Wildlife Management Area | OUTSIDE: POTA's pin is 1.1 km outside the outline (+1 more flag). |
| 4 | US-11447 | Stage Brook Wildlife Management Area | WAY OFF: The outline is 5.2 times bigger than the official 148 acres (777 ac drawn) (+1 more flag). |
| 4 | US-11476 | Mt. Tom Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+1 more flag). |

## US-MD

- parks: 186 (175 with an outline graded, 11 with no outline, 0 with records this tool can't read)
- pass every test: 69; have flags: 117
- flags: CONFLICT 54, TINY HOLES 29, DUPLICATE 27, NEAR 21, SPILL 20, OFF 17, SELF-INTERSECTION 15, SLIVERS 13, WAY OFF 12, MISMATCH 4, OUTSIDE 4, SCATTERED 1, INVALID 1

| score | ref | park | why |
|---|---|---|---|
| 10 | US-7760 | Nanjemoy Creek Wildlife Management Area | OUTSIDE: POTA's pin is 2.1 km outside the outline (+3 more flags). |
| 9 | US-7779 | Pocomoke River Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+4 more flags). |
| 7 | US-6384 | Pocomoke River State Park | SPILL: The outline covers 96% of US-10762 Furnace Natural Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-7740 | Fishing Bay Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+4 more flags). |
| 7 | US-7741 | Idylwild Wildlife Management Area | WAY OFF: The outline is 38.6 times bigger than the official 96 acres (3,702 ac drawn) (+2 more flags). |
| 7 | US-7782 | Ben Doane Parcel of Nanjemoy Wildlife Management Area | MISMATCH: The record name 'Nanjemoy Wma' does not match POTA's name 'Ben Doane Parcel of Nanjemoy Wildlife Management Area' (score 0.25) (+2 more flags). |
| 6 | US-0335 | Susquehanna National Wildlife Refuge | WAY OFF: The outline is 46.7 times bigger than the official 59 acres (2,755 ac drawn) (+3 more flags). |
| 6 | US-0670 | George Washington Memorial Parkway | SPILL: The outline covers 77% of US-7776 Oxon Cove Park & Farm National Historical Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-1566 | Cunningham Falls State Park | WAY OFF: The outline is 13.7 times bigger than the official 469 acres (6,410 ac drawn) (+1 more flag). |
| 6 | US-1601 | Susquehanna State Park | WAY OFF: The outline is 48.3 times bigger than the official 57 acres (2,754 ac drawn) (+3 more flags). |

## US-ME

- parks: 148 (140 with an outline graded, 8 with no outline, 0 with records this tool can't read)
- pass every test: 48; have flags: 100
- flags: TINY HOLES 59, NEAR 34, OFF 30, SLIVERS 17, MISMATCH 12, SELF-INTERSECTION 9, SCATTERED 6, OUTSIDE 4, SPILL 3, CONFLICT 3, WEAK 3, INVALID 2, DUPLICATE 2

| score | ref | park | why |
|---|---|---|---|
| 8 | US-8443 | Seboomook Lake Property State Preserve | MISMATCH: The record name 'Seboomook' does not match POTA's name 'Seboomook Lake Property State Preserve' (score 0.50) (+3 more flags). |
| 8 | US-8492 | Cobscook Bay Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+5 more flags). |
| 6 | US-0341 | Moosehorn National Wildlife Refuge | SPILL: The outline covers 95% of US-2385 Cobscook Bay State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-2381 | Baxter State Park | CONFLICT: The park is a state park but the record is a wma (+3 more flags). |
| 5 | US-0343 | Rachel Carson National Wildlife Refuge | NEAR: POTA's pin is 471 m outside the outline (+4 more flags). |
| 5 | US-8451 | Major Gregory Sanborn Wildlife Management Area | MISMATCH: The record name 'Maj. Gregory Sanborn (Brownfield Bog) Wildlife Management Area' does not match POTA's name 'Major Gregory Sanborn Wildlife Management Area' (score 0.67) (+2 more flags). |
| 5 | US-9170 | Machias River Corridor State Conservation Area | MISMATCH: The record name 'Machias River Watershed - MDOC' does not match POTA's name 'Machias River Corridor State Conservation Area' (score 0.50) (+2 more flags). |
| 5 | US-9175 | Holeb State Conservation Area | OUTSIDE: POTA's pin is 3.0 km outside the outline (+2 more flags). |
| 4 | US-0001 | Acadia National Park | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-68.2435671836458 44.3102054542673]; 1 piece(s) under 10 m wide; 3 hole(s) under 100 m2; 51 pieces spread over 69 km (+3 more flags). |
| 4 | US-2378 | Allagash Wilderness Waterway State Park | OFF: The outline is 2.0 times smaller than the official 40,969 acres (20,830 ac drawn) (+3 more flags). |

## US-MI

- parks: 388 (358 with an outline graded, 30 with no outline, 0 with records this tool can't read)
- pass every test: 249; have flags: 139
- flags: TINY HOLES 44, SELF-INTERSECTION 42, SLIVERS 26, NEAR 23, SPILL 22, DUPLICATE 19, MISMATCH 16, OFF 14, SCATTERED 5, OUTSIDE 5, CONFLICT 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-4263 | Piers Gorge Unit of Menominee River State Recreation Area | MISMATCH: The record name 'Menominee River State Recreation Area' does not match POTA's name 'Piers Gorge Unit of Menominee River State Recreation Area' (score 0.33) (+3 more flags). |
| 7 | US-4488 | Huron National Forest | SPILL: The outline covers 100% of US-12786 Au Sable National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4489 | Ottawa National Forest | SPILL: The outline covers 100% of US-10718 Sturgeon River Gorge Wilderness Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4583 | Manistee National Forest | SPILL: The outline covers 91% of US-12796 Pine National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-0350 | Michigan Wetland Management District | MISMATCH: The record name 'VAN BUREN COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Michigan Wetland Management District' (score 0.00) (+1 more flag). |
| 6 | US-4264 | Quiver Falls Unit of Menominee River State Recreation Area | MISMATCH: The record name 'Menominee River State Recreation Area' does not match POTA's name 'Quiver Falls Unit of Menominee River State Recreation Area' (score 0.33) (+3 more flags). |
| 6 | US-4487 | Hiawatha National Forest | SPILL: The outline covers 100% of US-13170 Bay De Noc/Grand Island National Recreation Trail, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-6619 | Bakale Wildlife Management Area | OUTSIDE: POTA's pin is 1.5 km outside the outline (+1 more flag). |
| 5 | US-6730 | Maple River State Game Land | OUTSIDE: POTA's pin is 656 m outside the outline (+2 more flags). |
| 5 | US-6787 | St. Clair Flats State Wildlife Area | OUTSIDE: POTA's pin is 2.3 km outside the outline (+2 more flags). |

## US-MN

- parks: 298 (290 with an outline graded, 8 with no outline, 0 with records this tool can't read)
- pass every test: 88; have flags: 210
- flags: STALE CHECK 79, TINY HOLES 63, SELF-INTERSECTION 40, NEAR 34, OFF 25, MISMATCH 24, OUTSIDE 24, SLIVERS 18, SPILL 18, SCATTERED 12, WEAK 12, WAY OFF 11, DUPLICATE 2, CONFLICT 2, FAR 1, INVALID 1

| score | ref | park | why |
|---|---|---|---|
| 10 | US-4490 | Chippewa National Forest | OUTSIDE: POTA's pin is 690 m outside the outline (+5 more flags). |
| 10 | US-4491 | Superior National Forest | OUTSIDE: POTA's pin is 545 m outside the outline (+5 more flags). |
| 9 | US-0365 | Minnesota Valley Wetland Management District | FAR: POTA's pin is 48.7 km outside the outline (+2 more flags). |
| 9 | US-11023 | Egret Island SNA State Conservation Area | OUTSIDE: POTA's pin is 2.1 km outside the outline (+2 more flags). |
| 8 | US-0067 | Voyageurs National Park | SPILL: The outline covers 37% of US-11699 Savage FEN SNA State Sanctuary, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-0362 | Litchfield Wetland Management District | MISMATCH: The record name 'WRIGHT COUNTY WATERFOWL PRODUCTION AREA OF MN' does not match POTA's name 'Litchfield Wetland Management District' (score 0.00) (+4 more flags). |
| 7 | US-12396 | Sam Brown Memorial Unique Area | WAY OFF: The outline is 41.8 times bigger than the official 1 acres (45 ac drawn) (+2 more flags). |
| 6 | US-0359 | Fergus Falls Wetland Management District | MISMATCH: The record name 'WILKIN COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Fergus Falls Wetland Management District' (score 0.00) (+3 more flags). |
| 6 | US-0373 | Windom Wetland Management District | MISMATCH: The record name 'WATONWAN COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Windom Wetland Management District' (score 0.00) (+3 more flags). |
| 6 | US-2513 | Myre-Big Island State Park | SPILL: The outline covers 56% of US-9377 Blazing Star State Trail, with no 2-fer row (maybe the wrong record) (+3 more flags). |

## US-MO

- parks: 561 (555 with an outline graded, 6 with no outline, 0 with records this tool can't read)
- pass every test: 440; have flags: 121
- flags: NEAR 55, TINY HOLES 21, SELF-INTERSECTION 18, OUTSIDE 13, OFF 13, DUPLICATE 12, SLIVERS 7, MISMATCH 5, WEAK 5, SPILL 3, SCATTERED 2, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-0831 | Harry S. Truman Family Farm National Historic Site | MISMATCH: The record name 'Harry S Truman National Historic Site' does not match POTA's name 'Harry S. Truman Family Farm National Historic Site' (score 0.60) (+2 more flags). |
| 7 | US-4492 | Mark Twain National Forest | OUTSIDE: POTA's pin is 1.1 km outside the outline (+4 more flags). |
| 5 | US-10211 | Sunklands State Conservation Area | OUTSIDE: POTA's pin is 696 m outside the outline (+2 more flags). |
| 5 | US-11015 | Harry S Truman Home National Historical Site | SPILL: The outline covers 100% of US-0831 Harry S. Truman Family Farm National Historic Site, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-4009 | Ozark National Wild and Scenic River | OUTSIDE: POTA's pin is 2.6 km outside the outline (+2 more flags). |
| 5 | US-7836 | Ozark State Trail | FAR: POTA's pin is 22.4 km outside the outline. |
| 4 | US-0374 | Big Muddy National Wildlife Refuge | OUTSIDE: POTA's pin is 700 m outside the outline (+1 more flag). |
| 4 | US-12406 | Poplar Bluff State Conservation Area | OUTSIDE: POTA's pin is 1.1 km outside the outline (+1 more flag). |
| 3 | US-10387 | Joe Crighton Beach Access State Conservation Area | MISMATCH: The record name 'Crighton (Joe) Access' does not match POTA's name 'Joe Crighton Beach Access State Conservation Area' (score 0.67). |
| 3 | US-10958 | Tywappity Community Lake State Conservation Area | MISMATCH: The record name 'Tywappity Conservation Land' does not match POTA's name 'Tywappity Community Lake State Conservation Area' (score 0.50). |

## US-MS

- parks: 155 (89 with an outline graded, 54 with no outline, 12 with records this tool can't read)
- pass every test: 101; have flags: 54; source down (retry): 26
- flags: NEAR 27, SELF-INTERSECTION 23, TINY HOLES 15, OFF 14, SPILL 8, OUTSIDE 4, SCATTERED 4, SLIVERS 3, DUPLICATE 2, MISMATCH 1, CONFLICT 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-4493 | Bienville National Forest | SPILL: The outline covers 100% of US-7116 Caney Creek Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4494 | De Soto National Forest | SPILL: The outline covers 100% of US-7106 Leaf River Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4496 | Holly Springs National Forest | SPILL: The outline covers 99% of US-7630 Chewalla Lake State Recreation Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 5 | US-0642 | Natchez Trace Parkway National Parkway | SPILL: The outline covers 30% of US-11883 Emerald Mound National Historical Site, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-4560 | Natchez Trace Trail National Scenic Trail | SPILL: The outline covers 30% of US-11883 Emerald Mound National Historical Site, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0390 | Noxubee National Wildlife Refuge | NEAR: POTA's pin is 189 m outside the outline (+3 more flags). |
| 4 | US-12639 | Pelahatchie Shore State Recreation Area | MISMATCH: The record name 'Pelahatchie Recreation Area' does not match POTA's name 'Pelahatchie Shore State Recreation Area' (score 0.50) (+1 more flag). |
| 4 | US-4495 | Delta National Forest | OUTSIDE: POTA's pin is 808 m outside the outline (+1 more flag). |
| 4 | US-4498 | Tombigbee National Forest | SPILL: The outline covers 58% of US-7097 Chickasaw Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-7079 | Twin Oaks Wildlife Management Area | OUTSIDE: POTA's pin is 1.4 km outside the outline (+1 more flag). |

## US-MT

- parks: 254 (233 with an outline graded, 21 with no outline, 0 with records this tool can't read)
- pass every test: 168; have flags: 86
- flags: TINY HOLES 30, NEAR 28, SELF-INTERSECTION 24, OFF 19, MISMATCH 18, SLIVERS 13, SCATTERED 7, SPILL 6, OUTSIDE 5, DUPLICATE 4, WEAK 3, STALE CHECK 1

| score | ref | park | why |
|---|---|---|---|
| 11 | US-12630 | Upper Missouri River BLM Wild and Scenic River | MISMATCH: The record name 'Upper Missouri River Breaks National Monument Field Office' does not match POTA's name 'Upper Missouri River BLM Wild and Scenic River' (score 0.67) (+6 more flags). |
| 11 | US-4499 | Beaverhead-Deerlodge National Forest | MISMATCH: The record name 'Deerlodge National Forest' does not match POTA's name 'Beaverhead-Deerlodge National Forest' (score 0.50) (+6 more flags). |
| 7 | US-12632 | Sleeping Giant BLM Wilderness Area | MISMATCH: The record name 'Sleeping Giant' does not match POTA's name 'Sleeping Giant BLM Wilderness Area' (score 0.67) (+2 more flags). |
| 7 | US-4501 | Custer Gallatin National Forest | MISMATCH: The record name 'Custer National Forest' does not match POTA's name 'Custer Gallatin National Forest' (score 0.50) (+2 more flags). |
| 7 | US-4502 | Flathead National Forest | OUTSIDE: POTA's pin is 7.3 km outside the outline (+4 more flags). |
| 7 | US-4504 | Helena - Lewis and Clark National Forest | MISMATCH: The record name 'Lewis & Clark National Forest' does not match POTA's name 'Helena - Lewis and Clark National Forest' (score 0.67) (+4 more flags). |
| 7 | US-4507 | Lolo National Forest | SPILL: The outline covers 96% of US-4574 Nez Perce National Historic Trail, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4549 | Upper Missouri River Breaks National Monument | SPILL: The outline covers 100% of US-12941 Judith Landing State Park, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 5 | US-12702 | MT Fish Creek Wildlife Management Area | MISMATCH: The record name 'Fish Creek Wildlife Management Area' does not match POTA's name 'MT Fish Creek Wildlife Management Area' (score 0.50) (+2 more flags). |
| 5 | US-6441 | Ear Mountain Wildlife Management Area | OUTSIDE: POTA's pin is 1.2 km outside the outline (+2 more flags). |

## US-NC

- parks: 253 (227 with an outline graded, 26 with no outline, 0 with records this tool can't read)
- pass every test: 97; have flags: 156
- flags: TINY HOLES 61, OFF 55, NEAR 50, SELF-INTERSECTION 41, SLIVERS 24, SPILL 17, OUTSIDE 13, DUPLICATE 10, MISMATCH 8, SCATTERED 8, CONFLICT 2, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-3845 | Kerr Lake State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+4 more flags). |
| 9 | US-6936 | Pisgah State Game Land | OUTSIDE: POTA's pin is 564 m outside the outline (+4 more flags). |
| 8 | US-4511 | Uwharrie National Forest | SPILL: The outline covers 98% of US-10260 Birkhead Mountains Wilderness Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-4509 | Nantahala National Forest | SPILL: The outline covers 72% of US-9758 Chattooga National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4510 | Pisgah National Forest | SPILL: The outline covers 100% of US-8011 Bobby N. Setzer State Fish Hatchery, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-6931 | Nicholson Creek State Game Land | OUTSIDE: POTA's pin is 785 m outside the outline (+2 more flags). |
| 7 | US-6937 | Pisgah WRC State Game Land | SPILL: The outline covers 100% of US-8011 Bobby N. Setzer State Fish Hatchery, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-6947 | Sandhills State Game Land | SPILL: The outline covers 100% of US-8010 McKinney Lake State Fish Hatchery, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-6962 | Uwharrie State Game Land | SPILL: The outline covers 97% of US-10260 Birkhead Mountains Wilderness Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-0412 | Currituck National Wildlife Refuge | OUTSIDE: POTA's pin is 507 m outside the outline (+3 more flags). |

## US-ND

- parks: 155 (112 with an outline graded, 43 with no outline, 0 with records this tool can't read)
- pass every test: 103; have flags: 52
- flags: NEAR 25, OFF 18, TINY HOLES 11, MISMATCH 5, SCATTERED 5, SELF-INTERSECTION 5, SLIVERS 3, OUTSIDE 3, DUPLICATE 2, FAR 2, SPILL 1

| score | ref | park | why |
|---|---|---|---|
| 9 | US-0428 | J. Clark Salyer Wetland Management District | FAR: POTA's pin is 15.3 km outside the outline (+2 more flags). |
| 5 | US-0421 | Arrowwood Wetland Management District | MISMATCH: The record name 'FOSTER COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Arrowwood Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-0425 | Devils Lake Wetland Management District | MISMATCH: The record name 'WALSH COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Devils Lake Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-0430 | Kulm Wetland Management District | MISMATCH: The record name 'MCINTOSH COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Kulm Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-0440 | Valley City Wetland Management District | MISMATCH: The record name 'TRAILL COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Valley City Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-7707 | Maclean Bottoms Wildlife Management Area | FAR: POTA's pin is 11.9 km outside the outline. |
| 4 | US-2764 | Lake Sakakawea State Park | SPILL: The outline covers 84% of US-4239 North Country Trail National Scenic Trail, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-7486 | Sheyenne National Grassland | OUTSIDE: POTA's pin is 772 m outside the outline (+1 more flag). |
| 3 | US-0422 | Audubon National Wildlife Refuge | OFF: The outline is 1.7 times bigger than the official 14,778 acres (25,559 ac drawn) (+2 more flags). |
| 3 | US-0434 | Long Lake National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 27,889 acres (14,057 ac drawn) (+2 more flags). |

## US-NE

- parks: 201 (185 with an outline graded, 16 with no outline, 0 with records this tool can't read)
- pass every test: 100; have flags: 101
- flags: OFF 61, DUPLICATE 21, TINY HOLES 15, NEAR 11, MISMATCH 8, STALE CHECK 7, CONFLICT 7, SPILL 5, OUTSIDE 3, SLIVERS 2, SELF-INTERSECTION 2, WEAK 1, WAY OFF 1, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-3486 | Moger National Waterfowl Production Area | MISMATCH: The record name 'Clay County Waterfowl Production Area Of Ne' does not match POTA's name 'Moger National Waterfowl Production Area' (score 0.67) (+2 more flags). |
| 7 | US-3489 | Massie National Waterfowl Production Area | MISMATCH: The record name 'Clay County Waterfowl Production Area Of Ne' does not match POTA's name 'Massie National Waterfowl Production Area' (score 0.67) (+2 more flags). |
| 7 | US-3490 | Smith Lagoon National Waterfowl Production Area | MISMATCH: The record name 'Clay County Waterfowl Production Area Of Ne' does not match POTA's name 'Smith Lagoon National Waterfowl Production Area' (score 0.50) (+2 more flags). |
| 6 | US-3483 | Atlanta National Waterfowl Production Area | MISMATCH: The record name 'Phelps County Waterfowl Production Area' does not match POTA's name 'Atlanta National Waterfowl Production Area' (score 0.67) (+1 more flag). |
| 5 | US-5629 | Sherman Reservoir State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+2 more flags). |
| 5 | US-9356 | Willow Lake Wildlife Management Area | FAR: POTA's pin is 52.4 km outside the outline. |
| 4 | US-0442 | Crescent Lake National Wildlife Refuge | OUTSIDE: POTA's pin is 1.6 km outside the outline (+1 more flag). |
| 4 | US-3487 | DeSoto (NE) National Wildlife Refuge | MISMATCH: The record name 'Desoto National Wildlife Refuge' does not match POTA's name 'DeSoto (NE) National Wildlife Refuge' (score 0.50) (+1 more flag). |
| 4 | US-5631 | Merritt Reservoir State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+1 more flag). |
| 4 | US-5642 | Swanson Reservoir State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+1 more flag). |

## US-NH

- parks: 206 (197 with an outline graded, 9 with no outline, 0 with records this tool can't read)
- pass every test: 101; have flags: 105
- flags: NEAR 45, OUTSIDE 24, TINY HOLES 22, OFF 10, SELF-INTERSECTION 8, SLIVERS 5, MISMATCH 5, SPILL 4, FAR 4, DUPLICATE 4, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-4512 | White Mountain National Forest | SPILL: The outline covers 95% of US-4959 Sentinel Mountain State Forest, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-4894 | Davis-White State Forest | FAR: POTA's pin is 55.5 km outside the outline. |
| 5 | US-4905 | Gile State Forest | SPILL: The outline covers 100% of US-2685 Winslow State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-4933 | Merrimack River State Forest | FAR: POTA's pin is 26.3 km outside the outline. |
| 5 | US-4934 | Merriman State Forest | FAR: POTA's pin is 21.2 km outside the outline. |
| 5 | US-4955 | Saltmarsh Pond State Forest | FAR: POTA's pin is 22.1 km outside the outline. |
| 4 | US-0329 | Silvio O Conte National Wildlife Refuge | OFF: The outline is 1.9 times smaller than the official 15,389 acres (7,909 ac drawn) (+3 more flags). |
| 4 | US-2650 | Eisenhower Memorial Wayside State Park | MISMATCH: The record name 'Eisenhower Memorial Area' does not match POTA's name 'Eisenhower Memorial Wayside State Park' (score 0.50) (+1 more flag). |
| 4 | US-4868 | Annett State Forest | OUTSIDE: POTA's pin is 9.4 km outside the outline (+1 more flag). |
| 4 | US-4886 | Connecticut Lakes State Forest | OUTSIDE: POTA's pin is 5.8 km outside the outline (+1 more flag). |

## US-NJ

- parks: 134 (129 with an outline graded, 5 with no outline, 0 with records this tool can't read)
- pass every test: 28; have flags: 106
- flags: OFF 59, TINY HOLES 56, NEAR 29, SELF-INTERSECTION 25, SLIVERS 20, SPILL 6, MISMATCH 4, SCATTERED 3, STALE CHECK 3, WEAK 2, CONFLICT 2, INVALID 2, OUTSIDE 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-11964 | Peaslee Wildlife Management Area | SPILL: The outline covers 74% of US-13256 Menantico Ponds Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-13061 | Gum Tree Corner Wildlife Management Area | MISMATCH: The record name 'Gumtree Corner Wildlife Management Area' does not match POTA's name 'Gum Tree Corner Wildlife Management Area' (score 0.67) (+3 more flags). |
| 5 | US-0453 | Edwin B. Forsythe National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 87,467 acres (44,472 ac drawn) (+4 more flags). |
| 5 | US-11988 | Cohansey River Wildlife Management Area | OUTSIDE: POTA's pin is 1.1 km outside the outline (+2 more flags). |
| 5 | US-5000 | Wharton State Forest | SPILL: The outline covers 98% of US-6609 Pinelands Preserve National Conservation Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-8037 | Dix Wildlife Management Area | OFF: The outline is 2.1 times smaller than the official 11,216 acres (5,253 ac drawn) (+4 more flags). |
| 5 | US-8042 | Heislerville Wildlife Management Area | NEAR: POTA's pin is 7 m outside the outline (+4 more flags). |
| 4 | US-0452 | Cape May National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 25,727 acres (13,075 ac drawn) (+3 more flags). |
| 4 | US-0677 | Great Egg Harbor National Wild and Scenic River | SPILL: The outline covers 41% of US-8060 Winslow Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-0888 | Musconetcong River National Wild and Scenic River | SPILL: The outline covers 52% of US-1631 Stephens State Park, with no 2-fer row (maybe the wrong record) (+1 more flag). |

## US-NM

- parks: 123 (105 with an outline graded, 18 with no outline, 0 with records this tool can't read)
- pass every test: 67; have flags: 56
- flags: NEAR 16, SELF-INTERSECTION 14, MISMATCH 14, OFF 12, TINY HOLES 11, SLIVERS 8, SPILL 7, WEAK 7, OUTSIDE 4, DUPLICATE 3, SCATTERED 2, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-0961 | Salinas Pueblo Missions, Gran Quivira Unit, National Monument | MISMATCH: The record name 'Salinas Pueblo Missions National Monument' does not match POTA's name 'Salinas Pueblo Missions, Gran Quivira Unit, National Monument' (score 0.60) (+2 more flags). |
| 6 | US-0459 | Las Vegas National Wildlife Refuge | OUTSIDE: POTA's pin is 635 m outside the outline (+3 more flags). |
| 6 | US-11791 | Santa Cruz Lake BLM Recreation Management Area | MISMATCH: The record name 'Santa Cruz Lake' does not match POTA's name 'Santa Cruz Lake BLM Recreation Management Area' (score 0.67) (+1 more flag). |
| 6 | US-11814 | Salinas Pueblo Missions, Quarai unit, National Monument | SPILL: The outline covers 100% of US-11813 Salinas Pueblo Missions, Abo Unit National Monument, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-11866 | Rio Bonito Acquired Lands: Salazar Tract, BLM Recreation Management Area | MISMATCH: The record name 'Rio Bonito Acquired Lands Tract 4' does not match POTA's name 'Rio Bonito Acquired Lands: Salazar Tract, BLM Recreation Management Area' (score 0.60) (+1 more flag). |
| 6 | US-4517 | Santa Fe National Forest | SPILL: The outline covers 85% of US-8227 Jemez National Recreation Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-4551 | Organ Mountains-Desert Peaks National Monument | OUTSIDE: POTA's pin is 1.5 km outside the outline (+1 more flag). |
| 5 | US-11813 | Salinas Pueblo Missions, Abo Unit National Monument | SPILL: The outline covers 100% of US-11814 Salinas Pueblo Missions, Quarai unit, National Monument, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-12746 | Aden Hills Off-Highway Vehicle Area BLM Recreation Management Area | MISMATCH: The record name 'Aden Hills' does not match POTA's name 'Aden Hills Off-Highway Vehicle Area BLM Recreation Management Area' (score 0.33) (+2 more flags). |
| 4 | US-11816 | Hackberry Lake OHV Use Area BLM Recreation Management Area | MISMATCH: The record name 'Hackberry Lake OHV Area' does not match POTA's name 'Hackberry Lake OHV Use Area BLM Recreation Management Area' (score 0.67) (+1 more flag). |

## US-NV

- parks: 367 (221 with an outline graded, 146 with no outline, 0 with records this tool can't read)
- pass every test: 168; have flags: 199
- flags: MISMATCH 131, SPILL 44, OUTSIDE 41, NEAR 28, SELF-INTERSECTION 17, TINY HOLES 17, SLIVERS 13, DUPLICATE 12, WEAK 12, OFF 11, STALE CHECK 10, FAR 6, CONFLICT 5, WAY OFF 3, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 10 | US-4391 | Humboldt-Toiyabe National Forest | MISMATCH: The record name 'Toiyabe National Forest' does not match POTA's name 'Humboldt-Toiyabe National Forest' (score 0.50) (+5 more flags). |
| 10 | US-9254 | High Rock Canyon BLM Special Recreation Management Area | WAY OFF: The outline is 8.9 times bigger than the official 5,665 acres (50,268 ac drawn) (+3 more flags). |
| 10 | US-9285 | Avi Kwa Ame (Spirit Mountain) National Monument | OUTSIDE: POTA's pin is 2.4 km outside the outline (+3 more flags). |
| 9 | US-13018 | Black Rock Range East/West BLM Herd Management Area | OUTSIDE: POTA's pin is 2.8 km outside the outline (+2 more flags). |
| 9 | US-13019 | Buffalo Hills BLM Herd Management Area | OUTSIDE: POTA's pin is 4.6 km outside the outline (+2 more flags). |
| 9 | US-13042 | Montezuma Peak BLM Herd Management Area | OUTSIDE: POTA's pin is 4.4 km outside the outline (+2 more flags). |
| 9 | US-13044 | Palmetto BLM Herd Management Area | OUTSIDE: POTA's pin is 766 m outside the outline (+2 more flags). |
| 9 | US-13128 | Jackson Mountains BLM Herd Management Area | OUTSIDE: POTA's pin is 7.2 km outside the outline (+2 more flags). |
| 9 | US-13129 | Lahontan BLM Herd Management Area | OUTSIDE: POTA's pin is 688 m outside the outline (+2 more flags). |
| 9 | US-13135 | Seven Troughs BLM Herd Management Area | OUTSIDE: POTA's pin is 1.2 km outside the outline (+2 more flags). |

## US-NY

- parks: 851 (829 with an outline graded, 22 with no outline, 0 with records this tool can't read)
- pass every test: 628; have flags: 223; source down (retry): 200
- flags: NEAR 97, SELF-INTERSECTION 49, TINY HOLES 44, MISMATCH 32, DUPLICATE 23, OFF 22, SPILL 20, SLIVERS 19, OUTSIDE 8, SCATTERED 2, WEAK 2

| score | ref | park | why |
|---|---|---|---|
| 9 | US-5106 | Bear Swamp(Otsego County) State Forest | MISMATCH: The record name 'Bear Swamp State Forest' does not match POTA's name 'Bear Swamp(Otsego County) State Forest' (score 0.67) (+4 more flags). |
| 8 | US-5107 | Bear Swamp(Cayuga County) State Forest | MISMATCH: The record name 'Bear Swamp State Forest' does not match POTA's name 'Bear Swamp(Cayuga County) State Forest' (score 0.67) (+3 more flags). |
| 8 | US-5110 | Beaver Creek(St Lawrence County) State Forest | MISMATCH: The record name 'Beaver Creek State Forest' does not match POTA's name 'Beaver Creek(St Lawrence County) State Forest' (score 0.50) (+3 more flags). |
| 8 | US-5249 | Pine Hill (Delaware County) State Forest | MISMATCH: The record name 'Pine Hill State Forest' does not match POTA's name 'Pine Hill (Delaware County) State Forest' (score 0.67) (+3 more flags). |
| 7 | US-10284 | Lost Nation (St. Lawrence County) State Forest | MISMATCH: The record name 'Lost Nation State Forest' does not match POTA's name 'Lost Nation (St. Lawrence County) State Forest' (score 0.50) (+2 more flags). |
| 7 | US-12030 | Pine Hill (Cattaraugus County) State Forest | MISMATCH: The record name 'Pine Hill State Forest' does not match POTA's name 'Pine Hill (Cattaraugus County) State Forest' (score 0.67) (+2 more flags). |
| 7 | US-12778 | Tracy Creek (Steuben County) State Forest | MISMATCH: The record name 'Tracy Creek State Forest' does not match POTA's name 'Tracy Creek (Steuben County) State Forest' (score 0.67) (+2 more flags). |
| 7 | US-2128 | Robert Moses (Long Island) State Park | MISMATCH: The record name 'Robert Moses State Park' does not match POTA's name 'Robert Moses (Long Island) State Park' (score 0.50) (+2 more flags). |
| 7 | US-4374 | Robert Moses (Thousand Islands) State Park | MISMATCH: The record name 'Robert Moses State Park' does not match POTA's name 'Robert Moses (Thousand Islands) State Park' (score 0.50) (+2 more flags). |
| 7 | US-5111 | Beaver Creek (Madison County) State Forest | MISMATCH: The record name 'Beaver Creek State Forest' does not match POTA's name 'Beaver Creek (Madison County) State Forest' (score 0.67) (+2 more flags). |

## US-OH

- parks: 276 (271 with an outline graded, 1 with no outline, 4 with records this tool can't read)
- pass every test: 155; have flags: 121; source down (retry): 259
- flags: TINY HOLES 58, NEAR 44, DUPLICATE 38, SELF-INTERSECTION 22, SLIVERS 12, CONFLICT 10, OUTSIDE 5, SPILL 4, MISMATCH 3, OFF 2, SCATTERED 1, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-1947 | Dillon State Park | SOURCE DOWN: SPILL: The outline covers 30% of US-9393 Blackhand Gorge State Nature Preserve, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-1986 | Pymatuning of Ohio State Park | SOURCE DOWN: OUTSIDE: POTA's pin is 1.3 km outside the outline (+1 more flag). |
| 6 | US-9456 | Delaware State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+3 more flags). |
| 6 | US-9499 | Salt Fork State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+3 more flags). |
| 5 | US-3516 | Wingfoot Lake State Park | SOURCE DOWN: CONFLICT: The park is a state park but the record is a wma (+2 more flags). |
| 5 | US-7850 | Caesar Creek Lake State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-8114 | East Fork State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-8636 | Paint Creek State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-8637 | Deer Creek State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 5 | US-9458 | Dillon State Wildlife Area | SOURCE DOWN: CONFLICT: The park is a wma but the record is a state park (+2 more flags). |

## US-OK

- parks: 205 (149 with an outline graded, 52 with no outline, 4 with records this tool can't read)
- pass every test: 144; have flags: 61; source down (retry): 114
- flags: NEAR 29, SPILL 12, OUTSIDE 11, SELF-INTERSECTION 10, TINY HOLES 7, OFF 6, DUPLICATE 4, FAR 3, MISMATCH 2, SLIVERS 2

| score | ref | park | why |
|---|---|---|---|
| 6 | US-6352 | Honobia Creek Wildlife Management Area | SOURCE DOWN: FAR: POTA's pin is 19.6 km outside the outline (+1 more flag). |
| 6 | US-6353 | Hugo Wildlife Management Area | SOURCE DOWN: FAR: POTA's pin is 12.4 km outside the outline (+1 more flag). |
| 6 | US-6366 | Ouachita Leflore Unit Wildlife Management Area | SOURCE DOWN: SPILL: The outline covers 100% of US-11322 Beech Creek National Scenic Reserve, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-12028 | Barren Fork Wildlife Management Area | FAR: POTA's pin is 28.0 km outside the outline. |
| 5 | US-6347 | Copan Wildlife Management Area | SOURCE DOWN: SPILL: The outline covers 100% of US-6346 Hal and Fern Cooper Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0492 | Washita National Wildlife Refuge | OUTSIDE: POTA's pin is 752 m outside the outline (+1 more flag). |
| 4 | US-12027 | Altus-Lugert State Fishing Lake | SOURCE DOWN: OUTSIDE: POTA's pin is 4.9 km outside the outline (+1 more flag). |
| 4 | US-2802 | Sequoyah Bay State Park | SOURCE DOWN: OUTSIDE: POTA's pin is 761 m outside the outline (+1 more flag). |
| 4 | US-2803 | Sequoyah State Park | SOURCE DOWN: OUTSIDE: POTA's pin is 2.6 km outside the outline (+1 more flag). |
| 4 | US-6340 | Black Kettle Wildlife Management Area | SOURCE DOWN: SPILL: The outline covers 91% of US-12739 Skipout Lake Recreation Site, with no 2-fer row (maybe the wrong record) (+1 more flag). |

## US-OR

- parks: 440 (389 with an outline graded, 51 with no outline, 0 with records this tool can't read)
- pass every test: 167; have flags: 273
- flags: MISMATCH 109, TINY HOLES 67, NEAR 54, OFF 46, STALE CHECK 46, SELF-INTERSECTION 33, SPILL 27, SLIVERS 26, DUPLICATE 19, WEAK 14, SCATTERED 7, OUTSIDE 6, CONFLICT 5, WAY OFF 3, FAR 2

| score | ref | park | why |
|---|---|---|---|
| 10 | US-4387 | Wallowa-Whitman National Forest | MISMATCH: The record name 'Whitman National Forest' does not match POTA's name 'Wallowa-Whitman National Forest' (score 0.50) (+5 more flags). |
| 9 | US-10485 | Saddle Butte BLM Wilderness Area | WAY OFF: The outline is 12.3 times bigger than the official 7,061 acres (86,745 ac drawn) (+2 more flags). |
| 9 | US-10744 | Pokegama BLM Herd Management Area | WAY OFF: The outline is 5.0 times bigger than the official 16,863 acres (85,022 ac drawn) (+2 more flags). |
| 9 | US-4390 | Newberry Crater Volcanic National Monument | FAR: POTA's pin is 249.1 km outside the outline (+2 more flags). |
| 8 | US-13068 | Honeycombs BLM Wilderness Area | MISMATCH: The record name 'Honeycombs WSA' does not match POTA's name 'Honeycombs BLM Wilderness Area' (score 0.50) (+3 more flags). |
| 8 | US-4381 | Mount Hood National Forest | SPILL: The outline covers 100% of US-10249 Salmon River National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 8 | US-9159 | Lower Deschutes National Wild and Scenic River | FAR: POTA's pin is 13.0 km outside the outline (+3 more flags). |
| 7 | US-0502 | Malheur National Wildlife Refuge | SPILL: The outline covers 100% of US-9157 Donner und Blitzen National Wild and Scenic River, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-10025 | Lost Forest/Dunes/Fossil BLM Special Recreation Management Area | MISMATCH: The record name 'Lost Forest-Sand Dunes-Fossil Lake' does not match POTA's name 'Lost Forest/Dunes/Fossil BLM Special Recreation Management Area' (score 0.60) (+2 more flags). |
| 7 | US-10741 | Murderer's Creek BLM Herd Management Area | MISMATCH: The record name 'Murderers Creek' does not match POTA's name 'Murderer's Creek BLM Herd Management Area' (score 0.50) (+2 more flags). |

## US-PA

- parks: 494 (488 with an outline graded, 6 with no outline, 0 with records this tool can't read)
- pass every test: 118; have flags: 376
- flags: MISMATCH 309, SELF-INTERSECTION 59, TINY HOLES 54, OFF 39, NEAR 21, SLIVERS 19, SPILL 6, OUTSIDE 3, SCATTERED 2, STALE CHECK 1, INVALID 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-8946 | PA 251 State Game Land | MISMATCH: The record name 'State Game Land 251' does not match POTA's name 'PA 251 State Game Land' (score 0.50) (+3 more flags). |
| 7 | US-6433 | White Clay Creek State Preserve | SPILL: The outline covers 100% of US-9721 Big Elk Creek State Park, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-8735 | PA 036 State Game Land | MISMATCH: The record name 'State Game Land 036' does not match POTA's name 'PA 036 State Game Land' (score 0.50) (+3 more flags). |
| 6 | US-8743 | PA 044 State Game Land | MISMATCH: The record name 'State Game Land 044' does not match POTA's name 'PA 044 State Game Land' (score 0.50) (+3 more flags). |
| 6 | US-8856 | PA 158 State Game Land | MISMATCH: The record name 'State Game Land 158' does not match POTA's name 'PA 158 State Game Land' (score 0.50) (+3 more flags). |
| 6 | US-8866 | PA 168 State Game Land | MISMATCH: The record name 'State Game Land 168' does not match POTA's name 'PA 168 State Game Land' (score 0.50) (+3 more flags). |
| 6 | US-8884 | PA 187 State Game Land | MISMATCH: The record name 'State Game Land 187' does not match POTA's name 'PA 187 State Game Land' (score 0.50) (+1 more flag). |
| 6 | US-8908 | PA 211 State Game Land | MISMATCH: The record name 'State Game Land 211' does not match POTA's name 'PA 211 State Game Land' (score 0.50) (+3 more flags). |
| 6 | US-9005 | PA 314 State Game Land | MISMATCH: The record name 'State Game Land 314' does not match POTA's name 'PA 314 State Game Land' (score 0.50) (+3 more flags). |
| 5 | US-5467 | Elk State Forest | OUTSIDE: POTA's pin is 2.0 km outside the outline (+2 more flags). |

## US-RI

- parks: 61 (57 with an outline graded, 4 with no outline, 0 with records this tool can't read)
- pass every test: 24; have flags: 37
- flags: TINY HOLES 13, NEAR 10, OFF 6, SELF-INTERSECTION 6, SPILL 4, OUTSIDE 3, CONFLICT 2, DUPLICATE 2, SLIVERS 1, WEAK 1, MISMATCH 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-5484 | George Washington Memorial State Forest | OUTSIDE: POTA's pin is 747 m outside the outline (+1 more flag). |
| 5 | US-6991 | Rockville Wildlife Management Area | CONFLICT: The park is a wma but the record is a state park (+2 more flags). |
| 4 | US-2873 | Fishermen's Memorial State Park | SPILL: The outline covers 42% of US-2870 Brenton Point State Park, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-6979 | Arcadia Management Area | SPILL: The outline covers 33% of US-6980 Beach Pond Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 4 | US-7722 | Scarborough North State Beach | MISMATCH: The record name 'Scarborough State Beach' does not match POTA's name 'Scarborough North State Beach' (score 0.67) (+1 more flag). |
| 3 | US-10546 | Eight Rod Farm Wildlife Management Area | OUTSIDE: POTA's pin is 661 m outside the outline. |
| 3 | US-10548 | Barber Pond State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it. |
| 3 | US-2870 | Brenton Point State Park | SPILL: The outline covers 46% of US-2873 Fishermen's Memorial State Park, with no 2-fer row (maybe the wrong record). |
| 3 | US-6986 | Simmons Mill Wildlife Management Area | OUTSIDE: POTA's pin is 820 m outside the outline. |
| 2 | US-2869 | Blackstone River State Park | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-71.4007116162651 41.9027719521636]; 2 hole(s) under 100 m2 (+1 more flag). |

## US-SC

- parks: 167 (161 with an outline graded, 6 with no outline, 0 with records this tool can't read)
- pass every test: 50; have flags: 117
- flags: STALE CHECK 73, TINY HOLES 34, NEAR 30, SELF-INTERSECTION 18, SLIVERS 13, OFF 11, SPILL 4, DUPLICATE 4, OUTSIDE 3, MISMATCH 3, WEAK 1, FAR 1, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-3917 | Little Pee Dee Bay Heritage Preserve | FAR: POTA's pin is 21.2 km outside the outline (+1 more flag). |
| 6 | US-5486 | Manchester State Forest | SPILL: The outline covers 71% of US-8149 Oak Lea Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-2888 | Cheraw State Park | NEAR: POTA's pin is 6 m outside the outline (+4 more flags). |
| 5 | US-4522 | Francis Marion National Forest | SPILL: The outline covers 100% of US-9203 Palmetto State Trail, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-5488 | Sand Hills State Forest | SPILL: The outline covers 100% of US-3874 H. Cooper Black Jr. Memorial State Recreation Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-9202 | Santee Coastal Reserve Wildlife Management Area | SPILL: The outline covers 100% of US-9208 Santee-Delta Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0518 | Cape Romain National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 70,297 acres (35,204 ac drawn) (+3 more flags). |
| 4 | US-0519 | Carolina Sandhills National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 91,834 acres (45,935 ac drawn) (+3 more flags). |
| 4 | US-0520 | Ernest F. Hollings ACE Basin National Wildlife Refuge | NEAR: POTA's pin is 17 m outside the outline (+3 more flags). |
| 4 | US-0522 | Savannah National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 30,520 acres (15,268 ac drawn) (+3 more flags). |

## US-SD

- parks: 120 (119 with an outline graded, 1 with no outline, 0 with records this tool can't read)
- pass every test: 72; have flags: 48
- flags: NEAR 14, MISMATCH 9, CONFLICT 9, OFF 8, SELF-INTERSECTION 8, TINY HOLES 7, SCATTERED 5, OUTSIDE 2, DUPLICATE 2, SPILL 2, WEAK 1, SLIVERS 1, WAY OFF 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-8155 | Angostura State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+3 more flags). |
| 7 | US-0525 | Huron Wetland Management District | OUTSIDE: POTA's pin is 9.8 km outside the outline (+2 more flags). |
| 5 | US-0529 | Madison Wetland Management District | MISMATCH: The record name 'YANKTON COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Madison Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-0532 | Waubay Wetland Management District | MISMATCH: The record name 'ROBERTS COUNTY WATERFOWL PRODUCTION AREA' does not match POTA's name 'Waubay Wetland Management District' (score 0.00) (+2 more flags). |
| 5 | US-4524 | Black Hills National Forest | NEAR: POTA's pin is 16 m outside the outline (+4 more flags). |
| 4 | US-7489 | Grand River National Grassland | OUTSIDE: POTA's pin is 3.0 km outside the outline (+1 more flag). |
| 4 | US-8192 | Shadehill State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+1 more flag). |
| 3 | US-0527 | Lacreek National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 33,142 acres (16,579 ac drawn) (+2 more flags). |
| 3 | US-10319 | South Scalp Creek State Recreation Area | MISMATCH: The record name 'S. Scalp Creek Recreation Area' does not match POTA's name 'South Scalp Creek State Recreation Area' (score 0.67). |
| 3 | US-10330 | Newell Lake State Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it. |

## US-TN

- parks: 277 (262 with an outline graded, 15 with no outline, 0 with records this tool can't read)
- pass every test: 99; have flags: 178
- flags: NEAR 77, TINY HOLES 61, STALE CHECK 45, SELF-INTERSECTION 33, SLIVERS 28, DUPLICATE 24, SPILL 20, OFF 19, OUTSIDE 8, CONFLICT 5, MISMATCH 4, SCATTERED 2, WEAK 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-2955 | Wilson Cumberland Trail State Park | SPILL: The outline covers 100% of US-6243 Falling Water Falls State Natural Area, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 8 | US-3928 | Bridgestone/firestone Centennial Wilderness Wildlife Management Area | MISMATCH: The record name 'Bridgestone/Firestone Wildlife Management Area' does not match POTA's name 'Bridgestone/firestone Centennial Wilderness Wildlife Management Area' (score 0.67) (+3 more flags). |
| 6 | US-3960 | Reelfoot State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+3 more flags). |
| 6 | US-5498 | Pickett State Forest | SPILL: The outline covers 44% of US-6261 Pogue Creek Canyon State Natural Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-7581 | Cordell Hull Waterfowl Refuge Wildlife Management Area | MISMATCH: The record name 'Cordell Hull Wildlife Management Area' does not match POTA's name 'Cordell Hull Waterfowl Refuge Wildlife Management Area' (score 0.67) (+3 more flags). |
| 6 | US-7622 | Tellico Lake Wildlife Management Area | SPILL: The outline covers 42% of US-2946 Fort Loudon State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-0533 | Chickasaw National Wildlife Refuge | OFF: The outline is 1.6 times smaller than the official 42,895 acres (26,905 ac drawn) (+4 more flags). |
| 5 | US-0686 | Big South Fork National Recreation Area | SPILL: The outline covers 100% of US-6248 Honey Creek State Natural Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-13563 | Bear Hollow Mountain Wildlife Management Area | SPILL: The outline covers 100% of US-6275 Walls of Jericho State Natural Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-2956 | Long Hunter State Park | SPILL: The outline covers 97% of US-6240 Couchville Cedar Glade State Natural Area, with no 2-fer row (maybe the wrong record) (+2 more flags). |

## US-TX

- parks: 222 (208 with an outline graded, 14 with no outline, 0 with records this tool can't read)
- pass every test: 112; have flags: 110; source down (retry): 3
- flags: STALE CHECK 70, TINY HOLES 31, NEAR 24, SELF-INTERSECTION 24, DUPLICATE 13, SPILL 12, OFF 11, WAY OFF 7, SLIVERS 4, OUTSIDE 4, MISMATCH 3, SCATTERED 2, CONFLICT 2, INVALID 1

| score | ref | park | why |
|---|---|---|---|
| 8 | US-0541 | Aransas National Wildlife Refuge | WAY OFF: The outline is 30.2 times smaller than the official 2,739,879 acres (90,789 ac drawn) (+3 more flags). |
| 8 | US-6550 | Cooper Wildlife Management Area | OUTSIDE: POTA's pin is 1.5 km outside the outline (+3 more flags). |
| 8 | US-6571 | Las Palomas , Anacua Unit Wildlife Management Area | OUTSIDE: POTA's pin is 1.4 km outside the outline (+3 more flags). |
| 8 | US-6572 | Las Palomas , Lower Rio Grande Valley Units Wildlife Management Area | MISMATCH: The record name 'Las Palomas Wildlife Management Area' does not match POTA's name 'Las Palomas , Lower Rio Grande Valley Units Wildlife Management Area' (score 0.33) (+3 more flags). |
| 7 | US-0550 | Lower Rio Grande Valley National Wildlife Refuge | SOURCE DOWN: SPILL: The outline covers 88% of US-10274 Palmito Ranch Battlefield State Historic Site, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-0553 | San Bernard National Wildlife Refuge | WAY OFF: The outline is 35.1 times smaller than the official 2,394,728 acres (68,194 ac drawn) (+4 more flags). |
| 7 | US-11268 | Neches River National Wildlife Refuge | WAY OFF: The outline is 548.2 times smaller than the official 5,117,867 acres (9,336 ac drawn) (+4 more flags). |
| 6 | US-0546 | Buffalo Lake National Wildlife Refuge | WAY OFF: The outline is 10.3 times smaller than the official 79,544 acres (7,738 ac drawn) (+3 more flags). |
| 6 | US-0549 | Laguna Atascosa National Wildlife Refuge | WAY OFF: The outline is 67.5 times smaller than the official 7,279,444 acres (107,906 ac drawn) (+3 more flags). |
| 6 | US-4414 | Angelina National Forest | SPILL: The outline covers 93% of US-6537 Bannister Wildlife Management Area, with no 2-fer row (maybe the wrong record) (+3 more flags). |

## US-UT

- parks: 692 (414 with an outline graded, 278 with no outline, 0 with records this tool can't read)
- pass every test: 368; have flags: 324
- flags: MISMATCH 164, SPILL 84, SELF-INTERSECTION 79, NEAR 61, TINY HOLES 59, STALE CHECK 58, WEAK 38, DUPLICATE 29, OUTSIDE 25, SLIVERS 22, OFF 21, FAR 9, WAY OFF 6, SCATTERED 1, CONFLICT 1

| score | ref | park | why |
|---|---|---|---|
| 13 | US-5869 | 9 Mile Canyon BLM Recreation Management Area | FAR: POTA's pin is 21.9 km outside the outline (+4 more flags). |
| 12 | US-11748 | Cedar Mesa BLM Special Recreation Management Area | FAR: POTA's pin is 31.4 km outside the outline (+3 more flags). |
| 12 | US-5782 | Indian Creek BLM Special Recreation Management Area | FAR: POTA's pin is 33.7 km outside the outline (+3 more flags). |
| 11 | US-5896 | Muddy Creek BLM Herd Management Area | OUTSIDE: POTA's pin is 652 m outside the outline (+4 more flags). |
| 10 | US-10990 | Topaz Mountain BLM Special Recreation Management Area | OUTSIDE: POTA's pin is 2.3 km outside the outline (+3 more flags). |
| 10 | US-4398 | Uinta-Wasatch-Cache National Forest | MISMATCH: The record name 'Cache National Forest' does not match POTA's name 'Uinta-Wasatch-Cache National Forest' (score 0.33) (+5 more flags). |
| 10 | US-5774 | Canyon Rims BLM Recreation Management Area | OUTSIDE: POTA's pin is 2.9 km outside the outline (+3 more flags). |
| 10 | US-5828 | Dark Canyon BLM Special Recreation Management Area | OUTSIDE: POTA's pin is 9.3 km outside the outline (+3 more flags). |
| 10 | US-6027 | Topaz Mountain Rockhound Area BLM Recreation Management Area | OUTSIDE: POTA's pin is 1.9 km outside the outline (+3 more flags). |
| 9 | US-10974 | Deep Creek BLM Wild and Scenic River | MISMATCH: The record name 'Deep Creek' does not match POTA's name 'Deep Creek BLM Wild and Scenic River' (score 0.67) (+4 more flags). |

## US-VA

- parks: 184 (177 with an outline graded, 7 with no outline, 0 with records this tool can't read)
- pass every test: 43; have flags: 141
- flags: OFF 87, TINY HOLES 42, NEAR 27, SPILL 16, SLIVERS 13, SELF-INTERSECTION 11, DUPLICATE 8, OUTSIDE 8, MISMATCH 4, INVALID 3, CONFLICT 1, SCATTERED 1, WAY OFF 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-0561 | Chincoteague National Wildlife Refuge | SPILL: The outline covers 44% of US-0671 Assateague Island National Seashore, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4526 | George Washington & Jefferson National Forest | SPILL: The outline covers 100% of US-9920 Mount Rogers National Recreation Trail, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 6 | US-5503 | Appomattox-Buckingham State Forest | SPILL: The outline covers 81% of US-1302 Holliday Lake State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 6 | US-5512 | Cumberland State Forest | SPILL: The outline covers 98% of US-1290 Bear Creek Lake State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-0016 | Colonial National Historical Park | SPILL: The outline covers 75% of US-9897 Jamestowne National Historical Site, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-0573 | Wallops Island National Wildlife Refuge | OUTSIDE: POTA's pin is 3.3 km outside the outline (+2 more flags). |
| 5 | US-3378 | Blue Ridge National Parkway | SPILL: The outline covers 51% of US-10507 Rock Castle Gorge National Recreation Trail, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 5 | US-9902 | Colonial National Parkway | SPILL: The outline covers 64% of US-9897 Jamestowne National Historical Site, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-0572 | Rappahannock River Valley National Wildlife Refuge | OFF: The outline is 1.6 times smaller than the official 15,282 acres (9,760 ac drawn) (+3 more flags). |
| 4 | US-0577 | Clinch River State Park | SPILL: The outline covers 34% of US-7790 Cleveland Barrens State Natural Area, with no 2-fer row (maybe the wrong record) (+1 more flag). |

## US-VT

- parks: 109 (93 with an outline graded, 16 with no outline, 0 with records this tool can't read)
- pass every test: 67; have flags: 42
- flags: TINY HOLES 20, NEAR 8, SELF-INTERSECTION 7, OUTSIDE 6, INVALID 4, DUPLICATE 4, MISMATCH 4, SPILL 3, SLIVERS 3, OFF 2, SCATTERED 1

| score | ref | park | why |
|---|---|---|---|
| 6 | US-5552 | Groton State Forest | SPILL: The outline covers 100% of US-3142 Seyon Lodge State Park, with no 2-fer row (maybe the wrong record) (+3 more flags). |
| 5 | US-5541 | Calvin Coolidge State Forest | MISMATCH: The record name 'Coolidge State Forest' does not match POTA's name 'Calvin Coolidge State Forest' (score 0.50) (+2 more flags). |
| 5 | US-5555 | Mount Mansfield State Forest | SPILL: The outline covers 100% of US-3129 Little River State Park, with no 2-fer row (maybe the wrong record) (+2 more flags). |
| 4 | US-3101 | Bomoseen State Park | SPILL: The outline covers 73% of US-3118 Halfmoon Pond State Park, with no 2-fer row (maybe the wrong record) (+1 more flag). |
| 3 | US-0329 | Silvio O Conte National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 54,180 acres (27,098 ac drawn) (+2 more flags). |
| 3 | US-3133 | Mount Ascutney State Park | MISMATCH: The record name 'Ascutney State Park' does not match POTA's name 'Mount Ascutney State Park' (score 0.50). |
| 3 | US-3138 | Quechee State Park | OUTSIDE: POTA's pin is 643 m outside the outline. |
| 3 | US-3148 | Townshend State Park | OUTSIDE: POTA's pin is 908 m outside the outline. |
| 3 | US-4527 | Green Mountain National Forest | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-72.8558190520403 44.0624197173004]; 5 hole(s) under 100 m2; 89 pieces spread over 176 km (+2 more flags). |
| 3 | US-5531 | William C. Putnam State Forest | MISMATCH: The record name 'W.C. Putnam State Forest' does not match POTA's name 'William C. Putnam State Forest' (score 0.33). |

## US-WA

- parks: 536 (487 with an outline graded, 49 with no outline, 0 with records this tool can't read)
- pass every test: 239; have flags: 297
- flags: STALE CHECK 98, NEAR 67, TINY HOLES 65, SPILL 57, SELF-INTERSECTION 52, CONFLICT 44, OFF 40, SLIVERS 34, DUPLICATE 30, MISMATCH 27, WAY OFF 14, SCATTERED 10, OUTSIDE 8, INVALID 6, WEAK 3

| score | ref | park | why |
|---|---|---|---|
| 15 | US-12488 | Columbia Basin Upland Restoration State Wildlife Area | MISMATCH: The record name 'Upland Restoration' does not match POTA's name 'Columbia Basin Upland Restoration State Wildlife Area' (score 0.50) (+8 more flags). |
| 12 | US-4531 | Okanogan-Wenatchee National Forest | OUTSIDE: POTA's pin is 875 m outside the outline (+5 more flags). |
| 11 | US-12575 | Johns River State Wildlife Area | WAY OFF: The outline is 8.9 times bigger than the official 1,358 acres (12,080 ac drawn) (+4 more flags). |
| 10 | US-12243 | Sherman Creek Wildlife Area State Fish and Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+5 more flags). |
| 10 | US-4530 | Mount Baker-Snoqualmie National Forest | MISMATCH: The record name 'Mt. Baker National Forest' does not match POTA's name 'Mount Baker-Snoqualmie National Forest' (score 0.67) (+5 more flags). |
| 10 | US-8666 | Whatcom Wildlife Area/Lake Terrell State Wildlife Area | MISMATCH: The record name 'Whatcom Wildlife Area Complex' does not match POTA's name 'Whatcom Wildlife Area/Lake Terrell State Wildlife Area' (score 0.50) (+3 more flags). |
| 9 | US-0596 | Umatilla National Wildlife Refuge | WAY OFF: The outline is 16.9 times bigger than the official 3,044 acres (51,567 ac drawn) (+4 more flags). |
| 9 | US-12322 | L.T. Murray State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+4 more flags). |
| 9 | US-12323 | Quilomene State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+4 more flags). |
| 9 | US-12552 | Skagit Bay Estuary State Wildlife Area | CONFLICT: The park is a wma but the record is a state park (+4 more flags). |

## US-WI

- parks: 348 (332 with an outline graded, 16 with no outline, 0 with records this tool can't read)
- pass every test: 184; have flags: 164
- flags: TINY HOLES 79, SELF-INTERSECTION 69, SLIVERS 39, NEAR 34, DUPLICATE 26, MISMATCH 18, OFF 16, SCATTERED 11, SPILL 11, OUTSIDE 5, CONFLICT 5, WEAK 2, STALE CHECK 1, FAR 1

| score | ref | park | why |
|---|---|---|---|
| 11 | US-4263 | Piers Gorge Unit of Menominee River State Recreation Area | MISMATCH: The record name 'Menominee River State Recreation Area' does not match POTA's name 'Piers Gorge Unit of Menominee River State Recreation Area' (score 0.33) (+6 more flags). |
| 10 | US-4262 | Pemene Falls Unit of Menominee River State Recreation Area | MISMATCH: The record name 'Menominee River State Recreation Area' does not match POTA's name 'Pemene Falls Unit of Menominee River State Recreation Area' (score 0.33) (+5 more flags). |
| 10 | US-7260 | Northern Highland American Legion State Forest | MISMATCH: The record name 'Northern Highland State Forest' does not match POTA's name 'Northern Highland American Legion State Forest' (score 0.50) (+5 more flags). |
| 8 | US-4236 | Upper Mississippi River National Wildlife Refuge | SPILL: The outline covers 48% of US-11955 Genoa National Fish Hatchery, with no 2-fer row (maybe the wrong record) (+5 more flags). |
| 7 | US-1457 | Kinnickinnic State Park | CONFLICT: The park is a state park but the record is a wma (+2 more flags). |
| 7 | US-4238 | Ice Age National Scenic Trail | SPILL: The outline covers 49% of US-8363 Gibraltar Rock State Natural Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4342 | Herb Behnke Unit of Wolf River Bottoms State Wildlife Area | MISMATCH: The record name 'Wolf River Bottoms Wildlife Area' does not match POTA's name 'Herb Behnke Unit of Wolf River Bottoms State Wildlife Area' (score 0.50) (+2 more flags). |
| 7 | US-4343 | LaSage Unit of Wolf River Bottoms State Wildlife Area | MISMATCH: The record name 'Wolf River Bottoms Wildlife Area' does not match POTA's name 'LaSage Unit of Wolf River Bottoms State Wildlife Area' (score 0.67) (+2 more flags). |
| 7 | US-4533 | Chequamegon-Nicolet National Forest | MISMATCH: The record name 'Chequamegon National Forest' does not match POTA's name 'Chequamegon-Nicolet National Forest' (score 0.50) (+4 more flags). |
| 6 | US-0602 | Leopold Wetland Management District | MISMATCH: The record name 'WINNEBAGO COUNTY WATERFOWL PRODUCTION AREA OF WI' does not match POTA's name 'Leopold Wetland Management District' (score 0.00) (+3 more flags). |

## US-WV

- parks: 172 (165 with an outline graded, 7 with no outline, 0 with records this tool can't read)
- pass every test: 52; have flags: 120
- flags: STALE CHECK 104, TINY HOLES 16, SELF-INTERSECTION 13, NEAR 9, SLIVERS 8, OFF 7, SCATTERED 3, OUTSIDE 3, SPILL 1, MISMATCH 1

| score | ref | park | why |
|---|---|---|---|
| 7 | US-0632 | Monongahela National Forest | SPILL: The outline covers 100% of US-12436 Big Draft Wilderness Area, with no 2-fer row (maybe the wrong record) (+4 more flags). |
| 7 | US-4526 | George Washington & Jefferson National Forest | MISMATCH: The record name 'George Washington National Forest' does not match POTA's name 'George Washington & Jefferson National Forest' (score 0.67) (+4 more flags). |
| 5 | US-7027 | Slatyfork Wildlife Management Area | OUTSIDE: POTA's pin is 5.9 km outside the outline (+2 more flags). |
| 4 | US-7043 | Tate Lohr Wildlife Management Area | OUTSIDE: POTA's pin is 2.4 km outside the outline (+1 more flag). |
| 3 | US-0608 | Ohio River Islands National Wildlife Refuge | OFF: The outline is 2.0 times smaller than the official 5,468 acres (2,743 ac drawn) (+2 more flags). |
| 3 | US-0696 | New River Gorge National Park | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-80.9237665219749 37.7561387567045]; 4 piece(s) under 10 m wide; 115 pieces spread over 55 km (+2 more flags). |
| 3 | US-12442 | Roaring Plains West Wilderness Area | OUTSIDE: POTA's pin is 725 m outside the outline. |
| 3 | US-7002 | Lewis Wetzel Wildlife Management Area | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-80.702877241717 39.4826422075845]; 1 hole(s) under 100 m2 (+2 more flags). |
| 3 | US-7024 | Elk River Wildlife Management Area | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-80.6598976299176 38.620640714525]; 2 hole(s) under 100 m2 (+2 more flags). |
| 3 | US-7044 | Tug Fork Wildlife Management Area | SELF-INTERSECTION: The shape has problems: Ring Self-intersection[-81.6552318831789 37.4372274713279]; 1 hole(s) under 100 m2 (+2 more flags). |

## US-WY

- parks: 294 (212 with an outline graded, 82 with no outline, 0 with records this tool can't read)
- pass every test: 142; have flags: 152
- flags: MISMATCH 83, NEAR 41, SPILL 35, SELF-INTERSECTION 23, OUTSIDE 19, TINY HOLES 15, OFF 12, DUPLICATE 10, SLIVERS 9, WEAK 7, SCATTERED 4, FAR 3, CONFLICT 2, STALE CHECK 1

| score | ref | park | why |
|---|---|---|---|
| 11 | US-6204 | Little Colorado BLM Herd Management Area | FAR: POTA's pin is 11.8 km outside the outline (+2 more flags). |
| 10 | US-10897 | Greater Sand Dunes BLM Special Recreation Management Area | OUTSIDE: POTA's pin is 1.9 km outside the outline (+3 more flags). |
| 10 | US-13245 | Flaming Gorge - Green River Basin Scenic Byway - All-American Road National Parkway | OUTSIDE: POTA's pin is 1.6 km outside the outline (+3 more flags). |
| 10 | US-4403 | Medicine Bow - Routt National Forest | MISMATCH: The record name 'Medicine Bow National Forest' does not match POTA's name 'Medicine Bow - Routt National Forest' (score 0.67) (+5 more flags). |
| 9 | US-10810 | Green Mountain BLM Herd Management Area | OUTSIDE: POTA's pin is 905 m outside the outline (+2 more flags). |
| 9 | US-10930 | Devil's Playground BLM WSA Wilderness Area | MISMATCH: The record name 'Devil's Playground-Twin Buttes' does not match POTA's name 'Devil's Playground BLM WSA Wilderness Area' (score 0.50) (+4 more flags). |
| 9 | US-10944 | Twin Buttes BLM WSA Wilderness Area | MISMATCH: The record name 'Devil's Playground-Twin Buttes' does not match POTA's name 'Twin Buttes BLM WSA Wilderness Area' (score 0.50) (+4 more flags). |
| 9 | US-4475 | Caribou-Targhee National Forest | MISMATCH: The record name 'Targhee National Forest' does not match POTA's name 'Caribou-Targhee National Forest' (score 0.50) (+4 more flags). |
| 9 | US-4535 | Bridger-Teton National Forest | MISMATCH: The record name 'Teton National Forest' does not match POTA's name 'Bridger-Teton National Forest' (score 0.50) (+4 more flags). |
| 9 | US-6221 | Fontenelle Creek BLM Recreation Management Area | OUTSIDE: POTA's pin is 1.1 km outside the outline (+2 more flags). |

## CA-AB

- parks: 459 (398 with an outline graded, 61 with no outline, 0 with records this tool can't read)
- pass every test: 282; have flags: 177
- flags: OFF 74, NEAR 55, CONFLICT 25, DUPLICATE 23, INVALID 20, SPILL 14, TINY HOLES 12, TOO COARSE 6, MISMATCH 5, OUTSIDE 5, SLIVERS 4, WAY OFF 4, FAR 3, SCATTERED 2, WEAK 2

| score | ref | park | why |
|---|---|---|---|
| 12 | CA-0109 | Waterton Biosphere Reserve | FAR: POTA's pin is 29.0 km outside the outline (+3 more flags). |
| 8 | CA-6112 | Kananaskis Country Provincial Park | FAR: POTA's pin is 12.4 km outside the outline (+1 more flag). |
| 7 | CA-1164 | Beaver Lake Provincial Recreation Area | OUTSIDE: POTA's pin is 5.1 km outside the outline (+2 more flags). |
| 6 | CA-1194 | Sylvan Lake Provincial Park | FAR: POTA's pin is 13.4 km outside the outline (+1 more flag). |
| 6 | CA-6125 | Porcupine Hills Public Land Use Zone Other Conservation Area | MISMATCH: The record name 'Porcupine Hills' does not match POTA's name 'Porcupine Hills Public Land Use Zone Other Conservation Area' (score 0.67) (+3 more flags). |
| 5 | CA-1174 | Crow Lake Provincial Park | NEAR: POTA's pin is 180 m outside the outline (+4 more flags). |
| 5 | CA-1197 | Victoria Settlement Provincial Park | OUTSIDE: POTA's pin is 3.6 km outside the outline (+2 more flags). |
| 5 | CA-2958 | Buck Lake Provincial Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+2 more flags). |
| 5 | CA-3117 | Travers Reservoir Provincial Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+2 more flags). |
| 5 | CA-6588 | Barrier Lake Provincial Recreation Area | CONFLICT: The record is the whole lake but the park is a recreation area on it (+2 more flags). |
