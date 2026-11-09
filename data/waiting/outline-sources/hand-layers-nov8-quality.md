# Hand-downloaded layers — Quality regrade notes (Nov 8, 2026 evening)

Addressing the NO grade on PR #50 (head was 4a7beeba).

## Must-fix done
1. **Unjoined** US-2200 (Okefenokee ↛ Stephen C. Foster) and CA-2373 (Primrose Wayside ↛ Primrose Provincial Park) for Rule 18. Both restored to `none` and listed for the **pile solver** (bots first), not for Brandon by default.
2. **Provenance** on all 6 `hand-layers/*.geojson.about.json`: source URL, download date **2026-11-08**, downloaded by Brandon by hand, license, publisher. Manitoba file names **ECCC / CPCAD** as publisher; Manitoba is the managing agency in the records.

## Should-fix done
3. **US-3504** Hill Country: TPWD state-parks layer has only **Louise Merrick Unit** (OBJECTID 22). No other units in that official layer to add as tracts; noted on the override.
4. **US-12418** Tallulah Gorge WMA: already joins GA DNR WMA (`sggaa184`, 2267 ac). Hand-download OBJECTID 904 matches name/acres; fingerprint recorded. State park polygon `sggab12` stays **NO**.
5. **Stale Nov 7 tests** updated (not known-fail): `test_outline_sources_nov7.py` allows ledger growth and trail/river rows; `test_trail_load_nov7.py` accepts `kept current line` and checks wired CSV ⊇ 243-list wired parks. Removed from `known-fail-main.txt`.

## Joins now
**22** hand joins (was 24). Held for pile solver: the original 15 + US-2200 + CA-2373.

US / CA rules hashes unchanged (overrides + ledger + about files only).
