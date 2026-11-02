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
