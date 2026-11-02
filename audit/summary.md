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
