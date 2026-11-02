# KPC park-outline puzzle: running notes (started 2026-10-31)

## Job
Fill yellow cols P-U in each tab of the workbook. Official government GIS only; never repeat col N layers or col O records; every URL verified with ?f=json. Order: tab 2, 1, 3, 4. One worker per tab; shared layers in shared_layers.md.

## Files
- Tab 2: KPC_parks_filled.xlsx (+ dated snapshots)
- Tab 1: sheet1.xlsx  (DONE)
- Tab 3: sheet3.xlsx
- Tab 4: sheet4.xlsx
- Shared layers: shared_layers.md

## Root causes found so far
- Tab 2: ~430 of 763 rows are BLM sites (Rec Mgmt Areas, SRMAs, historic sites, airstrips). Pins fall in huge field-office / SRMA polygons (Salt Lake FO 3.28M ac, Labyrinth Rims 300k ac). Likely individual sites mapped as points/lines, no area outline exists. Also: 0-acre records (bad geometry) and 86 rows with no 'inside' record even where col N says SURE (checker bugs, e.g. National Mall).
- Tab 1 (104 rows): never-tried layer 32; wrong name/name field 30; byway/tour not trail 21; pin off line 18; checker hit not accepted/error 13; split segments 9; wrong state 8; water trail 7; non-gov group 4.
  Results: 71 GIS, 17 NAME SOLVED, 7 PDF ONLY, 3 PARCEL, 6 NOT FOUND (r14,45,46,48,51,89).
  Needs human review: r54 Saracen, r88 Palmetto, r90 Jumbo Grade (reuse col O records).
  Broken services: Honolulu trails (fails every query), Truckee Meadows (needs token).
- Tab 4: ND statewide parcel layer (owner join) covers many ND rows.

## Status at last check (23:21)
Tab2 55 GIS/401 NOT FOUND (in progress); Tab3 95 GIS; Tab4 37 PARCEL.

## Tab 4 DONE (23:46) - sheet4.xlsx, 270 rows
Results: 134 PARCEL, 132 NOT FOUND, 3 NAME SOLVED, 1 GIS. Per-row causes in s4/results.json.
Root causes: history-agency sites not parks (~58; use parcels by owner; Indiana class 610 = State-owned); monument/marker only (36; NV 25 markers); other agency manages (~40: fish/wildlife, NRDs in NE 85-88, USACE, TVA, airstrips, land trusts, SFWMD); POTA pin off (~31: VT 8 in MA, MT 144 in Idaho, 12 in road right-of-way, pins in water); no open parcel layer (~45: Idaho 403, SC/TN need token, NH none, county gaps); region not a park (NY Adirondack/Catskill); WA layer has no owner field.
DECIDE: 12 PARCEL rows reuse a col N layer with a different record (AR 22,24,25,26,29; TX 66,68,69,73; MD 141,142; MA 148) - warning at start of col U.
Caveats: some NOT FOUND manager notes from background knowledge (marked 'not sure'); Sheridan Co WY layer on personal AGOL account; IN 129 coded park district.

## Tab 3 DONE (23:51) - sheet3.xlsx, 395 rows
Results: 182 GIS, 3 PARCEL (MI DNRLOTS), 4 NAME SOLVED, 206 NOT FOUND.
Root causes: checker never carried col N sure/likely hits forward (36 found); pin test false 'no hit' (23); name scorer too strict (12); national forests need USFS BasicOwnership; line parks (rivers via USFS WSR, byways FHWA, UT trails UGRC, CO trails COTREX); pins off >200 m (AK rivers 59-195 km, Hawaiian Islands NWR pin at Midway); real name/agency differs (40, e.g. Toronto SP = Cross Timbers, Bear Paw = Chief Joseph Battleground, several 'state' sites are USACE); only big parent covers pin (69 NF: Gateway NRA units, DC memorials, BLM field offices); point-only sites (88 NF); dead col N URLs (BLM_UT_RECS, old BLM AK).
DECIDE: club rule for big-parent rows (69) and point-only sites (88). Caveats: Davy Crockett lake, Fort DeRussy (military), Cypremort (private owner in PAD), Fontana Dam (likely).
Wrong place: Campobello (Canada), Snake row 69 (WY).

## Tab 2 DONE (23:58) - 763 rows: 102 GIS, 60 PARCEL, 18 NAME SOLVED, 8 PDF, 575 NOT FOUND
Causes: 401 BLM sites published only as points (55 BLM matched national rec polygons); BLM_Natl_SMA layer = whole-state manager polygons, never use for matching; pin inside bigger area ~183 (own parcel searched for VT, FL WMD, NY, NC, MI, OR, ID); checker bugs: 0-acre candidates ~168 (recompute acres), SURE match not written to col O (17), correct renamed records rejected (Yorktown, Jamestowne, Tobico, WWII Valor), wrong state's layer (IN vs IL), wrong layer (OR 452); wrong park type in name ~33; old names ~14; pin wrong spot ~24; different place ~15; data locked ~13 (TN login, Cassia Co ID 403).
DECIDE (12): 524, 522, 478, 543 new picks; 579, 559, 754 col O/N records; 758, 572, 553, 576 names; 493 needs MS data.
Weak: 712, 525 NAME SOLVED from col I only; 546 1.3 km from San Luis record.
## COMBINED: KPC_parks_ALL_TABS_done.xlsx
