> Rules: all club defaults (config/rules.json). Locked safety rules: honest_user_agent, no_bypass, no_found_tokens, tls_verified.

# Grades, one per kind (for chat 11)

The engine decides nothing; this is its self-check against the bar.

## outline: FAIL

**Bar:** Rule G: SURE only when pin inside (or <= 150 m with a name match, R-G12), names equal once kind words are stripped, kinds match, not line vs polygon, not a container, size within 1.5x or unknown; LIKELY goes to chat 11; UNLIKELY is evidence only, never a question. Whole key file: chat 11 samples 30 joins, needs 30/30. Finder: >= 95% of past YES re-found, >= 25% more parks, >= 85% YES in a sample of 40; every open park has a why-not.

**Measured:** rows 12871, parks 4427, parks_with_hit 593, SURE 477, LIKELY 751, UNLIKELY_evidence 4705, strong 267, already_approved 616, open_without_whynot 458, non_official_candidates 1, unlikely_as_questions 0, strong_but_not_sure 0, questions_beyond_150m 0, size_way_off_questions 0

**Top reasons for misses:**
- not found: no-layer: no official record at the pin or by name (2571)
- blocked: source could not be read (2226)
- evidence: UNLIKELY only : name: none word in common (1982)
- evidence: UNLIKELY only : pin not inside nor within m with a name match (951)
- evidence: UNLIKELY only : surface-manager layer: never matched against parks (688)

**Why it fails:**
- open parks without a why-not: 458
- non-official publishers: 1

**5 example parks:**

| ref | park | status | band | link / why |
|---|---|---|---|---|
| CA-4864 | Fort Henry National Historic Site | found | STRONG | https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html |
| CA-4866 | Fort Mississauga National Historic Site | found | STRONG | https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html |
| CA-4868 | Fort Wellington National Historic Site | candidate | CONFLICT | https://idgsi-rpgdi-arcgis.spac-pspc.gc.ca/gisserver/rest/services/Hosted/DFRP_PUBLIC/FeatureServer/4?f=html |
| CA-5137 |  | None |  |  |
| CA-4809 |  | None |  |  |

**Still needs:** chat 11: 30 sampled joins per key file (30/30); the finder bars need the side-by-side run (95% re-found, +25% parks) and a 40-row sample (85% YES)
