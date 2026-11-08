# kpc_pulloffs run report (2026-11-08)

- version 1.0.0; exit code 3; ran 50.1 min; 214 web requests
- parks in this input (after --areas / --limit): 190; done: 59; left for the next run: 131
- candidates for chat 11: 2293; kept out (log only, work/log/kept_out.jsonl): 6546

## Recall check (acceptance test only, before the duplicate drop)

Official access pins next to a public road (within 30 m) inside the search band: 206; found within 50 m: 48 (23%)

## Parks

- US-0019 Cumberland Gap National Historical Park: done; 101 candidate(s); 386 kept out; photo cells 125; points looked at {'entry': 81, 'road': 742, 'hint': 0}; roads {'public': 227, 'dropped (interstate/ramp/private/alley)': 22, 'lot-road hints': 2}; recall 0/2
- US-0050 Mammoth Cave National Park: done; 187 candidate(s); 646 kept out; photo cells 492; points looked at {'entry': 92, 'road': 2477, 'hint': 0}; roads {'public': 318, 'dropped (interstate/ramp/private/alley)': 72, 'lot-road hints': 0}; recall 1/4
  - problem (skipped, run went on): NAIP photo for cell 1167,8235 not read: HTTP 502
- US-0295 Clarks River National Wildlife Refuge: done; 30 candidate(s); 152 kept out; photo cells 149; points looked at {'entry': 136, 'road': 572, 'hint': 0}; roads {'public': 126, 'dropped (interstate/ramp/private/alley)': 6, 'lot-road hints': 0}; recall 0/2
- US-0538 Reelfoot National Wildlife Refuge: done; 9 candidate(s); 43 kept out; photo cells 28; points looked at {'entry': 6, 'road': 89, 'hint': 0}; roads {'public': 28, 'dropped (interstate/ramp/private/alley)': 6, 'lot-road hints': 0}; recall 0/0
- US-0608 Ohio River Islands National Wildlife Refuge: error; 0 candidate(s); 0 kept out; photo cells 0; points looked at {}; roads {}; recall 0/0
  - problem (skipped, run went on): road data not read: unexpected answer (application/json;charset=UTF-8): {"error":{"code":503,"message":"Error handling service request :Wait timeout for the request exceeded.","details":[]}}
- US-0686 Big South Fork National Recreation Area: done; 1017 candidate(s); 1808 kept out; photo cells 617; points looked at {'entry': 234, 'road': 2521, 'hint': 0}; roads {'public': 419, 'dropped (interstate/ramp/private/alley)': 12, 'lot-road hints': 0}; recall 2/3
- US-0703 Fort Donelson National Battlefield: done; 99 candidate(s); 225 kept out; photo cells 40; points looked at {'entry': 62, 'road': 369, 'hint': 0}; roads {'public': 135, 'dropped (interstate/ramp/private/alley)': 2, 'lot-road hints': 0}; recall 0/2
- US-0724 Abraham Lincoln Birthplace National Historic Site: done; 0 candidate(s); 17 kept out; photo cells 9; points looked at {'entry': 17, 'road': 83, 'hint': 0}; roads {'public': 32, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 1/3
- US-1251 Carr Creek State Park: done; 5 candidate(s); 8 kept out; photo cells 5; points looked at {'entry': 5, 'road': 23, 'hint': 0}; roads {'public': 9, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 1/2
- US-1252 Columbus Belmont State Park: done; 1 candidate(s); 17 kept out; photo cells 7; points looked at {'entry': 2, 'road': 54, 'hint': 0}; roads {'public': 34, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/0
- US-1253 Dawkins Line Rail Trail State Park: done; 34 candidate(s); 303 kept out; photo cells 148; points looked at {'entry': 252, 'road': 866, 'hint': 0}; roads {'public': 242, 'dropped (interstate/ramp/private/alley)': 16, 'lot-road hints': 0}; recall 1/3
- US-1254 E.P. 'Tom' Sawyer State Park: done; 4 candidate(s); 46 kept out; photo cells 16; points looked at {'entry': 6, 'road': 96, 'hint': 0}; roads {'public': 46, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
- US-1255 Fishtrap Lake Wildlife Management Area: done; 11 candidate(s); 67 kept out; photo cells 105; points looked at {'entry': 36, 'road': 537, 'hint': 0}; roads {'public': 81, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/5
- US-1256 Fort Boonesborough State Park: done; 3 candidate(s); 56 kept out; photo cells 8; points looked at {'entry': 4, 'road': 117, 'hint': 0}; roads {'public': 43, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/2
- US-1257 General Burnside State Park: done; 13 candidate(s); 32 kept out; photo cells 9; points looked at {'entry': 0, 'road': 54, 'hint': 0}; roads {'public': 16, 'dropped (interstate/ramp/private/alley)': 9, 'lot-road hints': 0}; recall 0/0
- US-1258 Grayson Lake State Park: done; 13 candidate(s); 45 kept out; photo cells 24; points looked at {'entry': 24, 'road': 108, 'hint': 0}; roads {'public': 23, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/3
- US-1259 Green River Lake State Park: done; 6 candidate(s); 58 kept out; photo cells 23; points looked at {'entry': 6, 'road': 116, 'hint': 0}; roads {'public': 17, 'dropped (interstate/ramp/private/alley)': 3, 'lot-road hints': 0}; recall 2/3
- US-1260 John James Audubon State Park: done; 9 candidate(s); 74 kept out; photo cells 34; points looked at {'entry': 13, 'road': 337, 'hint': 0}; roads {'public': 125, 'dropped (interstate/ramp/private/alley)': 3, 'lot-road hints': 0}; recall 2/11
- US-1261 Kincaid Lake State Park: done; 9 candidate(s); 49 kept out; photo cells 14; points looked at {'entry': 5, 'road': 185, 'hint': 0}; roads {'public': 77, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 1/3
- US-1262 Kingdom Come State Park: done; 5 candidate(s); 7 kept out; photo cells 24; points looked at {'entry': 31, 'road': 152, 'hint': 0}; roads {'public': 45, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/2
- US-1263 Lake Malone State Park: done; 3 candidate(s); 18 kept out; photo cells 9; points looked at {'entry': 6, 'road': 73, 'hint': 0}; roads {'public': 28, 'dropped (interstate/ramp/private/alley)': 5, 'lot-road hints': 0}; recall 2/3
- US-1264 Levi Jackson Wilderness Road State Park: done; 26 candidate(s); 64 kept out; photo cells 18; points looked at {'entry': 13, 'road': 139, 'hint': 0}; roads {'public': 46, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
- US-1265 Lincoln Homestead State Park: done; 7 candidate(s); 39 kept out; photo cells 6; points looked at {'entry': 20, 'road': 47, 'hint': 0}; roads {'public': 8, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
- US-1266 Mineral Mounds State Park: done; 7 candidate(s); 38 kept out; photo cells 13; points looked at {'entry': 6, 'road': 51, 'hint': 0}; roads {'public': 19, 'dropped (interstate/ramp/private/alley)': 8, 'lot-road hints': 0}; recall 0/0
- US-1267 My Old Kentucky Home State Park: done; 10 candidate(s); 35 kept out; photo cells 9; points looked at {'entry': 10, 'road': 114, 'hint': 0}; roads {'public': 44, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/2
- US-1268 Nolin Lake State Park: done; 1 candidate(s); 5 kept out; photo cells 2; points looked at {'entry': 2, 'road': 7, 'hint': 0}; roads {'public': 5, 'dropped (interstate/ramp/private/alley)': 2, 'lot-road hints': 0}; recall 0/0
- US-1269 Old Fort Harrod State Park: done; 3 candidate(s); 50 kept out; photo cells 4; points looked at {'entry': 1, 'road': 55, 'hint': 0}; roads {'public': 46, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
- US-1270 Paintsville Lake State Park: done; 8 candidate(s); 37 kept out; photo cells 9; points looked at {'entry': 4, 'road': 51, 'hint': 0}; roads {'public': 23, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 3/3
- US-1271 Taylorsville Lake State Park: done; 16 candidate(s); 72 kept out; photo cells 33; points looked at {'entry': 7, 'road': 188, 'hint': 0}; roads {'public': 38, 'dropped (interstate/ramp/private/alley)': 14, 'lot-road hints': 0}; recall 1/8
- US-1272 Yatesville Lake State Park: done; 10 candidate(s); 46 kept out; photo cells 28; points looked at {'entry': 21, 'road': 87, 'hint': 0}; roads {'public': 23, 'dropped (interstate/ramp/private/alley)': 6, 'lot-road hints': 0}; recall 1/1
- US-1273 Barren River Lake State Park: done; 5 candidate(s); 45 kept out; photo cells 18; points looked at {'entry': 7, 'road': 99, 'hint': 0}; roads {'public': 21, 'dropped (interstate/ramp/private/alley)': 7, 'lot-road hints': 0}; recall 0/2
- US-1274 Blue Licks Battlefield State Park: done; 8 candidate(s); 37 kept out; photo cells 13; points looked at {'entry': 6, 'road': 91, 'hint': 0}; roads {'public': 28, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 3/4
- US-1275 Buckhorn Lake State Park: done; 7 candidate(s); 26 kept out; photo cells 8; points looked at {'entry': 4, 'road': 36, 'hint': 0}; roads {'public': 9, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 2/5
- US-1276 Carter Caves State Park: done; 3 candidate(s); 14 kept out; photo cells 34; points looked at {'entry': 51, 'road': 240, 'hint': 0}; roads {'public': 49, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/11
- US-1277 Cumberland Falls State Park: done; 0 candidate(s); 20 kept out; photo cells 20; points looked at {'entry': 17, 'road': 124, 'hint': 0}; roads {'public': 18, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 2/7
- US-1278 Dale Hollow State Park: done; 39 candidate(s); 72 kept out; photo cells 24; points looked at {'entry': 12, 'road': 148, 'hint': 0}; roads {'public': 35, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 1/3
- US-1279 General Butler State Park: done; 16 candidate(s); 68 kept out; photo cells 19; points looked at {'entry': 3, 'road': 189, 'hint': 0}; roads {'public': 80, 'dropped (interstate/ramp/private/alley)': 2, 'lot-road hints': 0}; recall 0/4
- US-1280 Greenbo Lake State Park: done; 3 candidate(s); 41 kept out; photo cells 33; points looked at {'entry': 110, 'road': 240, 'hint': 0}; roads {'public': 48, 'dropped (interstate/ramp/private/alley)': 3, 'lot-road hints': 0}; recall 2/5
- US-1281 Jenny Wiley State Park: done; 24 candidate(s); 64 kept out; photo cells 32; points looked at {'entry': 10, 'road': 171, 'hint': 0}; roads {'public': 35, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/8
- US-1282 Kenlake State Park: done; 55 candidate(s); 134 kept out; photo cells 39; points looked at {'entry': 39, 'road': 317, 'hint': 0}; roads {'public': 120, 'dropped (interstate/ramp/private/alley)': 4, 'lot-road hints': 0}; recall 1/10
- US-1283 Kentucky Dam Village State Park: done; 81 candidate(s); 208 kept out; photo cells 30; points looked at {'entry': 39, 'road': 351, 'hint': 0}; roads {'public': 131, 'dropped (interstate/ramp/private/alley)': 18, 'lot-road hints': 0}; recall 2/6
- US-1284 Lake Barkley State Park: done; 26 candidate(s); 135 kept out; photo cells 44; points looked at {'entry': 16, 'road': 292, 'hint': 0}; roads {'public': 57, 'dropped (interstate/ramp/private/alley)': 29, 'lot-road hints': 0}; recall 0/1
- US-1285 Lake Cumberland State Park: done; 10 candidate(s); 35 kept out; photo cells 32; points looked at {'entry': 5, 'road': 162, 'hint': 0}; roads {'public': 36, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/7
- US-1286 Natural Bridge State Park: done; 6 candidate(s); 43 kept out; photo cells 20; points looked at {'entry': 28, 'road': 222, 'hint': 0}; roads {'public': 50, 'dropped (interstate/ramp/private/alley)': 15, 'lot-road hints': 0}; recall 3/11
  - problem (skipped, run went on): NAIP photo for cell 525,8370 not read: HTTP 502
  - problem (skipped, run went on): NAIP photo for cell 528,8369 not read: HTTP 502
- US-1287 Pennyrile Forest State Park: done; 6 candidate(s); 44 kept out; photo cells 20; points looked at {'entry': 18, 'road': 140, 'hint': 0}; roads {'public': 33, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 2/10
- US-1288 Pine Mountain State Park: done; 25 candidate(s); 76 kept out; photo cells 35; points looked at {'entry': 27, 'road': 271, 'hint': 0}; roads {'public': 47, 'dropped (interstate/ramp/private/alley)': 5, 'lot-road hints': 0}; recall 4/13
- US-1289 Rough River Dam State Park: done; 13 candidate(s); 34 kept out; photo cells 12; points looked at {'entry': 9, 'road': 83, 'hint': 0}; roads {'public': 25, 'dropped (interstate/ramp/private/alley)': 6, 'lot-road hints': 0}; recall 1/4
- US-3779 Big Bone Lick State Historic Site: done; 14 candidate(s); 54 kept out; photo cells 19; points looked at {'entry': 8, 'road': 94, 'hint': 0}; roads {'public': 15, 'dropped (interstate/ramp/private/alley)': 10, 'lot-road hints': 0}; recall 0/1
- US-3781 Breaks Interstate State Park: done; 111 candidate(s); 221 kept out; photo cells 44; points looked at {'entry': 23, 'road': 352, 'hint': 0}; roads {'public': 75, 'dropped (interstate/ramp/private/alley)': 2, 'lot-road hints': 0}; recall 2/7
- US-3782 Dr. Thomas Walker State Historic Site: done; 3 candidate(s); 3 kept out; photo cells 2; points looked at {'entry': 2, 'road': 8, 'hint': 0}; roads {'public': 3, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/1
- US-3783 Jefferson Davis State Historic Site: done; 4 candidate(s); 13 kept out; photo cells 2; points looked at {'entry': 0, 'road': 29, 'hint': 0}; roads {'public': 18, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
- US-3784 Old Mulkey Meetinghouse State Historic Site: done; 0 candidate(s); 5 kept out; photo cells 4; points looked at {'entry': 1, 'road': 27, 'hint': 0}; roads {'public': 9, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/0
- US-3785 Perryville Battlefield State Historic Site: done; 10 candidate(s); 61 kept out; photo cells 20; points looked at {'entry': 15, 'road': 117, 'hint': 0}; roads {'public': 28, 'dropped (interstate/ramp/private/alley)': 3, 'lot-road hints': 2}; recall 1/8
  - problem (skipped, run went on): NAIP photo for cell 1357,8344 not read: HTTP 504
  - problem (skipped, run went on): NAIP photo for cell 1359,8338 not read: HTTP 504
  - problem (skipped, run went on): NAIP photo for cell 1359,8342 not read: HTTP 502
- US-3786 Waveland State Historic Site: done; 2 candidate(s); 3 kept out; photo cells 4; points looked at {'entry': 0, 'road': 7, 'hint': 0}; roads {'public': 6, 'dropped (interstate/ramp/private/alley)': 1, 'lot-road hints': 0}; recall 0/1
  - note: NAIP photo-year list not read (HTTP 504); photo year looked up per candidate instead
- US-3787 White Hall State Historic Site: done; 2 candidate(s); 15 kept out; photo cells 5; points looked at {'entry': 1, 'road': 14, 'hint': 0}; roads {'public': 6, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
  - note: no official access point and no approved pull-off: looking up to 400 m outside (ruling G-P2)
  - problem (skipped, run went on): NAIP photo for cell 1465,8382 not read: HTTP 504
- US-3788 Wickliffe Mounds State Historic Site: done; 2 candidate(s); 8 kept out; photo cells 3; points looked at {'entry': 0, 'road': 24, 'hint': 0}; roads {'public': 15, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
  - problem (skipped, run went on): NAIP photo for cell 628,8187 not read: HTTP 504
- US-3789 William Whitley House State Historic Site: done; 2 candidate(s); 12 kept out; photo cells 5; points looked at {'entry': 2, 'road': 22, 'hint': 0}; roads {'public': 6, 'dropped (interstate/ramp/private/alley)': 3, 'lot-road hints': 0}; recall 0/0
  - note: no official access point and no approved pull-off: looking up to 400 m outside (ruling G-P2)
- US-3790 Fort Heiman National Battlefield: done; 1 candidate(s); 30 kept out; photo cells 18; points looked at {'entry': 12, 'road': 136, 'hint': 0}; roads {'public': 57, 'dropped (interstate/ramp/private/alley)': 0, 'lot-road hints': 0}; recall 0/0
  - note: no official access point and no approved pull-off: looking up to 400 m outside (ruling G-P2)
- US-3792 Land Between the Lakes National Recreation Area: done; 168 candidate(s); 582 kept out; photo cells 1000; points looked at {'entry': 42, 'road': 7303, 'hint': 0}; roads {'public': 749, 'dropped (interstate/ramp/private/alley)': 11, 'lot-road hints': 0}; recall 4/10
  - problem (skipped, run went on): NAIP photo for cell 823,8152 not read: HTTP 502
- US-3793 Ballard Wildlife Management Area: time ran out after 7 of 55 photo cells looked at; nothing written for it yet. Run again with --resume (downloads are cached).

## Web manners

- imagery.nationalmap.gov: no robots rules (HTTP 403); treated as allow-all (RFC 9309)
- tigerweb.geo.census.gov: no robots rules (it answered with a web page, not a robots file); treated as allow-all (RFC 9309)
- services2.arcgis.com: no robots rules (HTTP 403); treated as allow-all (RFC 9309)
