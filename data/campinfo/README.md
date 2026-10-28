# data/campinfo: campground facts (the campground info bot, HQ job 4)

Built by `.github/scripts/kpc_campinfo_bot.py` (workflow `kpc-campinfo.yml`, run by hand; no schedule until chat 8 grades it).
**It gathers facts and decides nothing.** Every fact comes from the agency that runs the campground and carries the source url,
the read date and the quoted line, so a person can check it in seconds. Unknown = `null`, never guessed, never a third-party site.

ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

## Files
- `<area>.json` (US-KY, US-TN … CA-ON …): `{area, about, read, counts, camps: {id: record}}`. The id is the row id from the
  campground list it came from (`list`: campfed = Recreation.gov facility id, campstate / campstate-manual = state row id,
  kpc-campgrounds.json = Kentucky hand-checked id).
- `review.md`: the per-area counts, the secrets still missing, the hosts that need a browser, the Kentucky answer-key check,
  and 12 sample records per area with their facts and source lines (for chat 8 to grade).
- `state.json`: resume data (`areas` status per area, `hosts` resting after three strikes, `fcc` file listings, `ky_check`, `last`).
- `sources.json`: which hosts count as official per state (any .gov / state host always does) + the booking systems.

## A record (one campground)
| field | what |
|---|---|
| name, lat, lon, park, agency, kind, list | from our campground list (park = the park ref when the list knows it) |
| official_page | the page the facts were read from (RIDB facility for federal) |
| booking {url, how} | the official booking page (Recreation.gov / ReserveAmerica / the state system); never availability |
| map {url, date_how} | the campground map link, PDF first, and how its date was judged |
| sites {total, tent, rv, cabin, group, primitive} | counts as the page states them (parts are never summed into a total) |
| rv_max_ft | maximum RV / trailer length in feet |
| hookups {electric, amps [30, 50], water, sewer} | true / false / null |
| dump_station, showers, drinking_water | true / false / null |
| restrooms | 'flush', 'vault', 'flush + vault', 'none', 'yes (kind not stated)' or null |
| fees | the amounts as published, with their words ('$26 per night | $32 per night for electric sites') |
| reservable | true / false / 'mixed' / null |
| season, checkin, checkout | as published ('April 1 through October 31', 'year-round', '3:00 pm') |
| rules {pets, generators, quiet_hours, fires, stay_limit} | the sentence or phrase from the page |
| phone | the office number nearest 'phone / office / information' (toll-free numbers are usually the booking line) |
| elevation_ft {value, src} | USGS Elevation Point Query Service (US) / NRCan CDEM (Canada), feet |
| cell {status, carriers, src} | FCC National Broadband Map: blank with status 'needs FCC token' until the secrets exist; step 2 (point lookup in the bulk files) is not built |
| facts_src {field: {url, date, line}} | the source of EVERY fact above, by field name ('hookups.amps', 'rules.pets' …) |
| status | 'ok', 'needs RIDB_API_KEY secret in KPC-Data', 'HTTP 403 -> needs browser', 'robots.txt says no', 'host resting', 'soft 404', 'no official page on file', 'page not on an official host: …', 'bot error: …' |
| checked, ver | read date; a record checked within 30 days is skipped next run |

## How to read review.md
1. The table: per area, how many campgrounds were read ok and how many wait on a secret, a browser or a page.
2. "Needs a secret / not built yet": what Brandon must add in GitHub -> Settings -> Secrets and variables -> Actions.
3. The hosts list: pages that answered 403 (a browser bot's job), said no in robots.txt, or struck out three times.
4. The Kentucky answer-key check: field by field, 'agree' / 'DIFFER bot x vs key y' / 'bot blank' against kpc-campgrounds.json.
   DIFFER rows are the ones to look at first: either the page changed since Oct 14 or the regex read the wrong number.
5. The samples: 12 records per area with each fact and its quoted source line; grade whether the line really says that.
