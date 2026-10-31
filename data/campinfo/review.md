# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-31. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 100 | 51 | 35 | 3 | 0 | 0 | 0 | 0 | 11 | 22 | 51 | 96 |
| US-TN | 348 | 0 | 81 | 0 | 0 | 0 | 267 | 0 | 0 | 0 | 0 | 348 |
| US-SC | 63 | 20 | 26 | 17 | 0 | 0 | 0 | 0 | 0 | 17 | 23 | 0 |
| US-IA | 125 | 0 | 32 | 0 | 0 | 0 | 93 | 0 | 0 | 0 | 0 | 0 |
| US-MA | 30 | 20 | 8 | 0 | 0 | 0 | 0 | 0 | 2 | 18 | 22 | 0 |
| US-CO | 605 | 102 | 339 | 0 | 0 | 164 | 0 | 0 | 0 | 0 | 266 | 1 |
| US-MT | 312 | 0 | 312 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| US-NV | 63 | 15 | 34 | 0 | 0 | 0 | 0 | 0 | 14 | 7 | 29 | 0 |
| US-WA | 280 | 0 | 214 | 0 | 0 | 0 | 66 | 0 | 0 | 0 | 0 | 0 |

## Needs a secret / not built yet

- RIDB_API_KEY is not set in KPC-Data: every federal (Recreation.gov) row has status "needs RIDB_API_KEY secret in KPC-Data". Free key: ridb.recreation.gov, Profile. Add it under Settings -> Secrets and variables -> Actions.
- Cell coverage (one status per area; cell = null on every record until the point lookup exists): US-CO FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-IA FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-KY FCC as of 2025-12-31: 0 mobile coverage files for the state (point lookup = step 2, not built); US-MA FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-MT FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-NV FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-SC FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-TN FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built)

## Hosts that need a browser (403), say no in robots.txt, or are resting

- cpw.state.co.us: 164 campgrounds · host resting

## Needs a browser pass (the page opened but its text holds no campground facts: filled by script, most likely)

- southcarolinaparks.com: 17 campgrounds
- parks.ky.gov: 3 campgrounds

## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)

- 2026-10-30: 67 hand-checked campgrounds · fields agree 111 · DIFFER 12 · bot blank 186

**GATE=PASS** · FACTS vs hand key: 103/111 right = 93% (need 80%, at least 10 filled; sites 20/22, electric 32/36, water 20/21, sewer 7/8, dump_station 4/4, showers 20/20) · 0 fee/site values from the wrong page or sentence (need 0) · known answers 16 right of 16 read, 0 waiting on the secret, 0 warn · all-field agreement 111/123 = 90% ('some' = agree; KEY_WRONG left out)

- ok: Higginson-Henry WMA: no RV length (the page gives elevation 675 ft, not an RV length) · got None
- ok: Rolling Fork WMA: no RV length (elevation 980 ft is not an RV length) · got None
- ok: West Kentucky WMA: no RV length (elevation 451 ft is not an RV length) · got None
- ok: Yellowbank WMA: no RV length (elevation 872 ft is not an RV length) · got None
- ok: Yellowbank WMA: no camping season (Nov. 1-Dec. 31 is the rabbit / quail hunting season) · got None
- ok: Higginson-Henry WMA: no camping season (hunting season dates are not the camping season) · got None
- ok: Mammoth Cave: showers from a real sentence or null, never the 'Shower Types' menu heading · got None from “”
- ok: Twin Knobs: 'RV sites range from electric-only to full hookups' = sewer 'some' · got some
- ok: Bandy Creek: phone is not the (877) reservation line · got None
- ok: Bear Creek Horse Camp: phone is not the (877) reservation line · got None
- ok: Blue Heron: phone is not the (877) reservation line · got None
- ok: Station Camp: phone is not the (877) reservation line · got None
- ok: White Sulphur Horse Camp: booking link is a campground page, not a bare domain · got None
- ok: S-Tree: booking link is a campground page, not a bare domain · got None
- ok: Mammoth Cave Campground: one record only (duplicates merged) · got 1 record(s)
- ok: Fort Boonesborough: site count read from the state park page (key 163, so >= 100) · got 166

**KEY_WRONG (hand-key rows the checkers found wrong; left out of the count; Brandon fixes the key):**

| campground | field | bot | key | why |
|---|---|---|---|---|
| Clear Creek Campground | electric | False | False | agency words say no hookups (chat 11 regrade); key says electric True |
| White Sulphur Horse Camp | electric | False | False | agency words say no hookups (chat 11 regrade); key says electric True |
| Koomer Ridge Campground | electric | False | False | agency page says 'no hookups' (chat 8 grade); key says electric True |
| Great Meadows Campground | electric | False | False | agency words say no hookups (chat 11 regrade); key says electric True |
| Turkey Foot Campground | electric | False | False | agency page: 'There is no water, electricity or dump station available' (chat 8); key says electric True |

- Barren River Lake State Resort Park Campground (ok (browser)): amps bot blank (key: [30, 50]); dump_station agree (True); electric DIFFER bot True vs key False; sewer bot blank (key: False); showers agree (True); sites bot blank (key: 101); water DIFFER bot True vs key False
- Big Bone Lick Campground (ok (browser)): amps bot blank (key: [30]); dump_station bot blank (key: True); electric agree (True); showers agree (True); sites agree (62); water agree (True)
- Blue Heron Campground (KY) (ok (browser)): electric agree (True); phone bot blank (key: (423) 286-7275); showers agree (True); sites agree (45)
- Bear Creek Horse Camp (KY) (ok (browser)): electric agree (True); phone bot blank (key: (423) 286-7275); showers agree (True); sites agree (22) [bot: 23]
- Alum Ford Campground (KY) (ok (browser)): electric bot blank (key: False); phone bot blank (key: (423) 569-9778); sewer bot blank (key: False); sites bot blank (key: 6); water bot blank (key: False)
- Bandy Creek Campground (TN) (ok): electric agree (True) [bot: some]; phone bot blank (key: (423) 286-7275); showers agree (True)
- Station Camp Campground (TN) (ok (browser)): electric agree (True); phone bot blank (key: (423) 286-7275); showers agree (True); sites agree (24)
- Blue Licks Battlefield Campground (ok, no campground facts even in a browser): dump_station bot blank (key: True); electric bot blank (key: True); phone DIFFER bot (859) 289-5507 vs key (859) 289-3653; showers bot blank (key: True); sites bot blank (key: 55); water bot blank (key: False)
- Carr Creek Campground (ok (browser)): electric DIFFER bot True vs key False; sites bot blank (key: 39); water agree (True)
- Carter Caves Campground (ok (browser)): amps bot blank (key: [20, 30, 50]); dump_station bot blank (key: True); electric bot blank (key: True); phone bot blank (key: (606) 286-4411); showers agree (True); sites bot blank (key: 128); water bot blank (key: True)
- Columbus-Belmont Campground (ok, no campground facts even in a browser): amps bot blank (key: [50]); dump_station bot blank (key: True); electric bot blank (key: True); sewer bot blank (key: True); showers bot blank (key: True); sites bot blank (key: 35); water bot blank (key: True)
- Ridgeline & Clifty Campgrounds (ok, no campground facts even in a browser): amps bot blank (key: [20, 30]); electric bot blank (key: False); phone bot blank (key: (800) 325-0063); sites bot blank (key: 50); water bot blank (key: True)
- Wilderness Road Campground (ok): amps bot blank (key: [20, 30, 50]); dump_station agree (True); electric agree (True) [bot: some]; phone bot blank (key: (606) 248-2817); sewer DIFFER bot False vs key True; showers agree (True); sites bot blank (key: 151); water agree (False)
- Dale Hollow Lake Campground (ok (browser)): amps bot blank (key: [50]); electric agree (True); sewer bot blank (key: True); sites bot blank (key: 151); water bot blank (key: True)
- Twin Knobs Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 780-7818); sewer agree (True) [bot: some]; showers agree (True); sites agree (200); water agree (True) [bot: some]
- Zilpo Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 768-2722); sewer bot blank (key: False); showers agree (True)
- Clear Creek Campground (ok): electric KEY WRONG (bot False, key False): left out; phone bot blank (key: (606) 784-6428); sites bot blank (key: 20); water bot blank (key: True)
- White Sulphur Horse Camp (ok): electric KEY WRONG (bot False, key False): left out; phone bot blank (key: (606) 784-6428); water bot blank (key: True)
- Koomer Ridge Campground (ok): electric KEY WRONG (bot False, key False): left out; phone bot blank (key: (606) 784-6428); sewer bot blank (key: False); showers agree (True); sites agree (54); water bot blank (key: False)
- Holly Bay Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 864-4163); showers agree (True); sites bot blank (key: 94); water agree (True)
- Grove Drive-In Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 864-4163); sites bot blank (key: 44); water agree (True)
- Bee Rock Campground (ok (browser)): electric bot blank (key: False); phone bot blank (key: (606) 864-4163); sewer bot blank (key: False); sites bot blank (key: 25); water bot blank (key: False)
- Great Meadows Campground (ok): electric KEY WRONG (bot False, key False): left out; phone bot blank (key: (606) 376-5323); sewer bot blank (key: False); sites agree (18); water bot blank (key: False)
- Barren Fork Horse Camp (ok): electric bot blank (key: True); phone bot blank (key: (606) 376-5323); sites agree (41); water bot blank (key: True)
- Turkey Foot Campground (ok): electric KEY WRONG (bot False, key False): left out; phone bot blank (key: (606) 864-4163); sites bot blank (key: 15); water bot blank (key: False)
- S-Tree Campground (ok): phone bot blank (key: (606) 864-4163); sites agree (20); water bot blank (key: True)
- Fort Boonesborough Campground (ok (browser)): electric agree (True); phone agree ((859) 527-3454); sewer agree (True); sites agree (163) [bot: 166]; water agree (True)
- General Burnside Island Campground (ok (browser)): electric agree (True); phone agree ((606) 561-3625); sewer bot blank (key: True); sites agree (101) [bot: 102]; water agree (True)
- General Butler Campground (ok (browser)): electric bot blank (key: True); sites bot blank (key: 104); water bot blank (key: True)
- Grayson Lake Campground (ok (browser)): amps bot blank (key: [50]); electric agree (True); phone DIFFER bot (606) 474-4513 vs key (606) 474-6856; sites agree (69) [bot: 71]; water agree (True)
- Green River Lake Campground (ok (browser)): electric bot blank (key: True); phone bot blank (key: (270) 465-8255); sites bot blank (key: 227); water bot blank (key: True)
- Greenbo Lake Campground (ok, no campground facts in the page text: needs browser?): amps bot blank (key: [30]); electric bot blank (key: True); sewer bot blank (key: True); sites bot blank (key: 102); water bot blank (key: True)
- Jenny Wiley Campground (ok, no campground facts in the page text: needs browser?): dump_station bot blank (key: True); electric bot blank (key: True); phone bot blank (key: (606) 889-1790); showers bot blank (key: True); sites bot blank (key: 118); water bot blank (key: True)
- John James Audubon Campground (ok (browser)): amps bot blank (key: [20]); electric bot blank (key: True); sites bot blank (key: 83); water bot blank (key: True)
- Kenlake Campground (ok (browser)): electric bot blank (key: True); phone bot blank (key: (270) 474-2211); sewer bot blank (key: True); sites bot blank (key: 63); water bot blank (key: True)
- Kentucky Dam Village Campground (ok, no campground facts even in a browser): electric bot blank (key: True); sites bot blank (key: 69); water bot blank (key: True)
- Kincaid Lake Campground (ok (browser)): electric agree (True); sites DIFFER bot 84 vs key 159
- Lake Barkley Campground (ok (browser)): amps bot blank (key: [30]); electric agree (True); sites bot blank (key: 79); water agree (True)
- Lake Cumberland Campground (ok (browser)): electric agree (True); phone bot blank (key: (270) 343-3111); sewer bot blank (key: True); sites bot blank (key: 87); water agree (True)
- Lake Malone Campground (ok (browser)): amps bot blank (key: [30]); electric agree (True); sites bot blank (key: 25); water agree (True)
- Hillman Ferry Campground (ok): amps agree ([30, 50]); electric agree (True); phone bot blank (key: (270) 924-2181); sewer agree (True); showers agree (True); sites agree (368); water agree (True)
- Energy Lake Campground (ok): amps DIFFER bot [30, 50] vs key [50]; electric agree (True); phone bot blank (key: (270) 924-2270); sites DIFFER bot 13 vs key 35
- Wranglers Campground (ok): amps agree ([30, 50]); electric agree (True) [bot: some]; phone bot blank (key: (270) 924-2200); sewer agree (True); showers agree (True); sites agree (198); water agree (True)
- Piney Campground (TN) (ok): electric agree (True); phone bot blank (key: (931) 232-5331); sewer agree (True); sites agree (384); water agree (True)
- Fenton Self-Service Campground (ok): amps agree ([30]); electric agree (True)
- Self-service lakeside campgrounds (10) (ok): electric DIFFER bot True vs key False; sewer bot blank (key: False); water bot blank (key: False)
- Mammoth Cave Campground (ok, no campground facts even in a browser): dump_station bot blank (key: True); electric bot blank (key: False); phone bot blank (key: (270) 758-2424); sewer bot blank (key: False); showers bot blank (key: True); sites bot blank (key: 111); water bot blank (key: False)
- Maple Springs Group Campground (ok (browser)): dump_station bot blank (key: True); electric agree (True); phone DIFFER bot (270) 758-2166 vs key (270) 758-2180; sewer bot blank (key: False); sites bot blank (key: 7)
- Houchin Ferry Campground (ok (browser)): electric agree (True); phone bot blank (key: (270) 758-2180); sites bot blank (key: 12); water bot blank (key: True)
- My Old Kentucky Home Campground (ok (browser)): amps bot blank (key: [50]); electric agree (True); phone bot blank (key: (502) 348-3502); sewer bot blank (key: True); sites bot blank (key: 49); water agree (True)
- Whittleton & Middle Fork Campgrounds (ok (browser)): amps bot blank (key: [20]); electric agree (True); phone bot blank (key: (606) 663-2214); sites bot blank (key: 86); water bot blank (key: True)
- Nolin Lake Campground (ok (browser)): electric DIFFER bot True vs key False; showers agree (True); sites bot blank (key: 65)
- Otter Creek ORA Campground (ok, no campground facts even in a browser): dump_station bot blank (key: True); electric bot blank (key: True); phone bot blank (key: (270) 750-4257); showers bot blank (key: True); water bot blank (key: True)
- Paintsville Lake Campground (ok, no campground facts in the page text: needs browser?): electric bot blank (key: True); sewer bot blank (key: True); sites bot blank (key: 42); water bot blank (key: True)
- Pennyrile Forest Campground (ok, no campground facts even in a browser): electric bot blank (key: True); sewer bot blank (key: True); sites bot blank (key: 63); water bot blank (key: True)
- Taylorsville Lake Campground (ok (browser)): amps bot blank (key: [20]); dump_station bot blank (key: True); electric bot blank (key: True); sewer bot blank (key: True); showers agree (True); sites bot blank (key: 75); water bot blank (key: True)
- Twin Knobs Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 780-7818); sewer agree (True) [bot: some]; showers agree (True); sites agree (200); water agree (True) [bot: some]
- Yatesville Lake Campground (ok (browser)): electric bot blank (key: True); sites agree (47); water bot blank (key: True)
- Yellowbank WMA primitive campground (Main Area) (ok, no campground facts even in a browser): electric bot blank (key: False); phone agree ((270) 547-6856); sewer bot blank (key: False); water bot blank (key: False)
- Zilpo Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (606) 768-2722); sewer bot blank (key: False); showers agree (True)
- Kentucky Horse Park Campground (ok (browser)): amps agree ([20, 30, 50]); dump_station agree (True); electric agree (True) [bot: some]; phone agree ((859) 259-4257); showers agree (True); sites agree (257) [bot: 260]; water agree (True)
- Levi Jackson Campground (ok): amps bot blank (key: [30, 50]); dump_station agree (True); electric agree (True); phone bot blank (key: (606) 330-2130); sewer bot blank (key: True); showers agree (True); sites agree (146); water agree (True)
- Breaks Interstate Park Campground (ok): electric agree (True) [bot: some]; phone bot blank (key: (276) 865-4413); sewer agree (True); sites agree (138); water agree (True)
- Kingdom Come primitive campsites (ok (browser)): electric bot blank (key: False); sewer bot blank (key: False); water bot blank (key: False)
- Higginson-Henry WMA designated campsites (ok, no campground facts even in a browser): electric bot blank (key: False); sewer bot blank (key: False); water bot blank (key: False)
- West Kentucky WMA designated camping site (ok, no campground facts even in a browser): electric bot blank (key: False); sewer bot blank (key: False); water bot blank (key: False)
- Rolling Fork WMA designated camping area (ok, no campground facts even in a browser): electric bot blank (key: False); sewer bot blank (key: False); water bot blank (key: False)

## US-KY: 12 random samples (records with facts; seed = the date)

- **Bee Rock Campground** (bee-rock-campground, KY (hand-checked list), status ok (browser), 8 facts, 741 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/bee-rock-campground)
  - drinking_water = true · “ilable at the campsites. Facility and Amenity Information Restrooms Vault toilet(s) Water Potable water is available at this site. Drinking ”
  - features = "fire ring and lantern post with access to many shared picni · “travel only. The campground features sites for both small RVs and tents. Each site has a fire ring and lantern post with access to many shar”
  - fees = "$15 per night | $20 per night" · “vember. Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $15 per night Double Site: $20 per night A fee is ”
  - map.date_how = "web page, no date in the link" · “link “Bee Rock Campground Map Guide””
  - map.url = "https://usfs-public.box.com/s/yfegub8ltz7ye6uudxt0nxmss8tth · “link “Bee Rock Campground Map Guide” -> https://usfs-public.box.com/s/yfegub8ltz7ye6uudxt0nxmss8tthe7o”
  - reservable = false · “Bee Rock Recreation Area along the banks of the Rockcastle River and features 25 wooded, first-come, first-served campsites with scenic view”
  - restrooms = "vault" · “are available at this site. Picnic tables are available at each campsite. Other Amenities Vault toilets meet accessibility standards for per”
  - season = "year-round" · “ee Rock Camping Prohibitions General Information Seasons of Use The Laurel County side is open year-round. The Pulaski County side is open f”
- **Kentucky Dam Village Campground** (kentucky-dam-village-campground, KY (hand-checked list), status ok, no campground facts even in a browser, 7 facts, 350 ft) · [parks.ky.gov](https://parks.ky.gov/explore/kentucky-dam-village-state-resort-park-7793)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/kentu · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-mapa1d96cf9-4bbf-40”
  - phone = "(270) 362-8386" · “open seasonally. Contact the marina directly for pricing at (270) 362-8386 or visit www.kydammarina.com. Eagle Watching Make your own”
  - reservable = true · “t Park 270-362-4271 scot.ratzlaff@ky.gov 166 Upper Village Drive, Gilbertsville, KY 42044 Reserve A Campsite Reserve A Lodge / Cottage View ”
- **Energy Lake Campground** (energy-lake-campground, KY (hand-checked list), status ok, 14 facts, 377 ft) · [www.landbetweenthelakes.us](https://www.landbetweenthelakes.us/visit/energy-lake-campground/)
  - booking.how = "online: lblweb.usedirect.com" · “link “Reservations””
  - booking.url = "https://lblweb.usedirect.com/camplbl/" · “link “Reservations” -> https://lblweb.usedirect.com/camplbl/”
  - checkin = "4:30 p.m" · “Lake Campground The Gatehouse is open from 9:00am until 5:00pm during the camping season. Check-in is 4:30 p.m. , you may check in anytime o”
  - checkout = "3:30 p.m" · “ck-in is 4:30 p.m. , you may check in anytime of your arrival date if the site is vacant. Check-out is 3:30 p.m. A 1 night late fee will be ”
  - features = "fire ring" · “lows, etc. They are not provided. There is a covered porch with a nearby picnic table and fire ring. There is not a boat ramp in Energy Lake”
  - hookups.amps = [30, 50] · “eservations can be made 2 days to 6 months in advance Type of Site Basic Nightly Rate $12 30 Amp Electric Nightly Rate $26 50 Amp Electric N”
  - hookups.electric = true · “by an earthen dam. It offers 13 cabins and 35 well-defined sites in a wooded area with 33 electrical hookups capable of handling tents to mo”
  - map.date_how = "PDF, year 2025 in the link" · “link “Energy Lake Campground Map””
  - map.url = "https://www.landbetweenthelakes.us/wp-content/uploads/2025/ · “link “Energy Lake Campground Map” -> https://www.landbetweenthelakes.us/wp-content/uploads/2025/04/FINAL_PRINT_-EnergyLakeCampgroundMap_2”
  - phone_hint = "(800) 525-7077" · “ley. There is a courtesy dock there as well. Additional Information Reserve Online Phone: 1800-525-7077 The call center is open weekdays fro”
- **Kincaid Lake Campground** (kincaid-lake-campground, KY (hand-checked list), status ok (browser), 15 facts, 695 ft) · [parks.ky.gov](https://parks.ky.gov/falmouth/parks/recreation/kincaid-lake-state-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/kinca · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - fees = "$3.00 charged each game" · “hole, miniature golf course near the camping area. Open daily from April through October. $3.00 charged each game. Picnicking Pristine groun”
  - hookups.electric = true · “stars at Kincaid Lake! The campground features 84 RV sites nestled in open woodland, with electric and water hookups, a grocery, playground,”
  - hookups.water = true · “stars at Kincaid Lake! The campground features 84 RV sites nestled in open woodland, with electric and water hookups, a grocery, playground,”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-map711472d8-e0ef-4c”
  - reservable = true · “State Park 859-654-3531 samantha.webster@ky.gov 749 Kincaid Park Rd., Falmouth, KY 41040 Reserve A Campsite View All Photos Have an adventur”
  - restrooms = "yes (kind not stated)" · “electric and water hookups, a grocery, playground, and two central service buildings with restrooms and showers. We also feature 75 primitve”
- **Maple Springs Group Campground** (maple-springs-group-campground, KY (hand-checked list), status ok (browser), 16 facts, 773 ft) · [home.nps.gov](https://home.nps.gov/maca/planyourvisit/maplespringscg.htm)
  - booking.how = "online: www.recreation.gov" · “link “Recreation.gov””
  - booking.url = "https://www.recreation.gov/camping/gateways/2818" · “link “Recreation.gov” -> https://www.recreation.gov/camping/gateways/2818”
  - checkin = "1 pm" · “Check-in time is after 1 pm at the Mammoth Cave, Houchin Ferry and Maple Springs Campground. If you arrive at your re”
  - drinking_water = true · “ddy campsites, catch your drain water in buckets and empty into toilets in the restrooms. Water hydrants are for collection of water to be u”
  - hookups.electric = true · “luded sites ideal for larger groups of campers and their horse companions. All sites have electric and water hookups for RVs. This campgroun”
  - hookups.water = true · “luded sites ideal for larger groups of campers and their horse companions. All sites have electric and water hookups for RVs. This campgroun”
  - map.date_how = "web page, no date in the link" · “link “Mammoth Cave Map & Guide””
  - map.url = "https://home.nps.gov/maca/planyourvisit/mammoth-cave-map-gu · “link “Mammoth Cave Map & Guide” -> https://home.nps.gov/maca/planyourvisit/mammoth-cave-map-guide.htm”
  - phone = "(270) 758-2166" · “information, schedules, and trailer standards, please call (270) 758-2166 or visit Directions and Transportation. OPEN BASIC INFORMAT”
  - phone_hint = "(270) 758-2424" · “in person only on the day of your trip. Contact campground office for hours of operation. (270) 758-2424. Leave No Trace Seven Principles (U”
- **Lake Malone Campground** (lake-malone-campground, KY (hand-checked list), status ok (browser), 14 facts, 572 ft) · [parks.ky.gov](https://parks.ky.gov/explore/lake-malone-state-park-7818)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/lake- · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - hookups.electric = true · “4 primitive sites are available for tent camping. Twenty-five campsites are equipped with electric and water hookups to accommodate recreati”
  - hookups.water = true · “4 primitive sites are available for tent camping. Twenty-five campsites are equipped with electric and water hookups to accommodate recreati”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Campground Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Campground Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/campground-mapfa9aeaf8-1”
  - phone = "(270) 657-2111" · “llowed if restrained. Call the park for more information at 270-657-2111. Fishing "An angler's delight" describes the 788-acre Lake”
  - phone_hint = "(270) 657-2111" · “and picnic tables. Pets are allowed if restrained. Call the park for more information at 270-657-2111. Fishing "An angler's delight" describ”
  - reservable = true · “alone State Park 270-657-2111 teresaj.wells@ky.gov 331 State Route 8001, Dunmor, KY 42339 Reserve A Campsite View All Photos There’s somethi”
- **Whittleton & Middle Fork Campgrounds** (whittleton-middle-fork-campgrounds, KY (hand-checked list), status ok (browser), 7 facts, 775 ft) · [parks.ky.gov](https://parks.ky.gov/explore/whittleton-campground-8107)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/natur · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ide sites with utilities at Natural Bridge State Park. Tent campsites are also available. Dump stations and two central service buildings wi”
  - hookups.electric = true · “te. Two campgrounds, Whittleton Campground and Middle Fork Campground, provide sites with utilities at Natural Bridge State Park. Tent camps”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - restrooms = "yes (kind not stated)" · “. Tent campsites are also available. Dump stations and two central service buildings with restrooms and showers are furnished for your conve”
  - showers = true · “es are also available. Dump stations and two central service buildings with restrooms and showers are furnished for your convenience.Â Reser”
- **Self-service lakeside campgrounds (10)** (self-service-lakeside-campgrounds-10, KY (hand-checked list), status ok, 6 facts) · [www.landbetweenthelakes.us](https://www.landbetweenthelakes.us/facility/self-service-camping/)
  - fees = "$12 per night | $26 per night | $10 per night" · “rash pickup, lake access, and boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per n”
  - hookups.amps = [30] · “ss, and boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per night Turkey Bay Off-Hi”
  - hookups.electric = true · “boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per night Turkey Bay Off-Highway Ve”
  - restrooms = "vault" · “er basic amenities including designated campsite pads, picnic tables, grills, fire rings, vault toilets, trash pickup, lake access, and boat”
  - rules.fires = "firewood at home – do not transport it to campgrounds" · “$10 per night Boswell Landing – $10 per night Gatlin Point – $10 per night Firewood Leave firewood at home – do not transport it to campgrou”
  - season = "year-round" · “atives to the more developed campgrounds. We have 11 self-service campgrounds which offer year-round lakeside camping. Although these areas ”
- **Rolling Fork WMA designated camping area** (rolling-fork-wma-designated-camping-area, KY (hand-checked list), status ok, no campground facts even in a browser, 4 facts, 587 ft) · [app.fw.ky.gov](https://app.fw.ky.gov/Public_Lands_Search/detail.aspx?Kdfwr_id=9219)
  - map.date_how = "PDF, no date in the link" · “link “View Detailed Map””
  - map.url = "https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf" · “link “View Detailed Map” -> https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf”
  - phone = "(502) 477-9024" · “Overview Size: 2896 acres Location: Nelson, Larue Contact: (502) 477-9024 Elevation: minimum 520 feet, maximum 980 feet. Entrance GPS”
  - rules.stay_limit = "14 days" · “Camping is allowed in designated area only and only during Turkey and Deer Seasons with a 14-day limit. No ATV’s, camping, horseback riding,”
- **White Sulphur Horse Camp** (white-sulphur-horse-camp, KY (hand-checked list), status ok, 5 facts, 856 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/white-sulphur-horse-camp)
  - drinking_water = false · “rs up to 50ft in length. Facility and Amenity Information Restrooms Vault toilet(s) Water Potable water is not available at this site. Picni”
  - fees = "$20 per night Peak Season (March 20 - October 26) | $15 per · “r-round Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $20 per night Peak Season (March 20 - October 26) ”
  - hookups.electric = false · “White Sulphur Horse Camp, located near Cave Run Lake, is a primitive campground (without electricity) designed for horseback riders. The cam”
  - rv_max_ft = 50 · “d continue for 2.5 miles. Parking The parking area can accommodate up to 30 vehicles with trailers up to 50ft in length. Facility and Amenit”
  - season = "year-round" · “nitoring, Oct 2026-Sept 2027 General Lake Prohibitions General Information Seasons of Use Open year-round Operational Hours Open 24 hours/da”
- **Blue Heron Campground (KY)** (blue-heron-campground-ky, KY (hand-checked list), status ok (browser), 15 facts, 1276 ft) · [home.nps.gov](https://home.nps.gov/biso/planyourvisit/blueheroncampground.htm)
  - booking.how = "online: www.recreation.gov" · “link “Start Your Reservation””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232505" · “link “Start Your Reservation” -> https://www.recreation.gov/camping/campgrounds/232505”
  - checkin = "12:00 pm" · “ly from April through mid-to-late December each year. Important Information Check-out and check-in time is 12:00 pm (ET) for all campsites i”
  - checkout = "12:00 pm" · “NRRA with the exception of Bandy Creek Group Camp where check-in time is 2:00 pm (ET) and check-out time is 12:00 pm (ET). Notice: Sites wit”
  - dump_station = true · “r and electric hook-ups, picnic tables, fire-rings, access to restrooms and showers and a dump station. A map of the Blue Heron Campground m”
  - hookups.amps = [50] · “ere check-in time is 2:00 pm (ET) and check-out time is 12:00 pm (ET). Notice: Sites with 50-amp electric service are shaded in gray. . Camp”
  - hookups.electric = true · “of Stearns off Highway 742. The campground offers a total of 45 sites all with water and electric hook-ups, picnic tables, fire-rings, acces”
  - hookups.water = true · “miles west of Stearns off Highway 742. The campground offers a total of 45 sites all with water and electric hook-ups, picnic tables, fire-r”
  - map.date_how = "PDF, year 2024 in the link" · “link “map of the Blue Heron Campground””
  - map.url = "https://home.nps.gov/biso/planyourvisit/upload/Blue-Heron-C · “link “map of the Blue Heron Campground” -> https://home.nps.gov/biso/planyourvisit/upload/Blue-Heron-Campground-Map-and-Regs-2024.pdf”
- **Carter Caves Campground** (carter-caves-campground, KY (hand-checked list), status ok (browser), 12 facts, 1035 ft) · [parks.ky.gov](https://parks.ky.gov/olive-hill/parks/resort/carter-caves-state-resort-park)
  - booking.how = "online: kentuckystateparks.reserveamerica.com" · “link “CLICK HERE””
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/carte · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - fees = "$5, Children | $4, Mondays | $3 for all | $6 for Adults" · “campground registration building and the Lodge front desk. Open seasonally. Fees: Adults $5, Children $4, Mondays $3 for all. Campers pay $4”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-map3d3eab0a-2c5a-42”
  - phone_hint = "(606) 286-7009" · “am, meals, and lodging into one reasonable price. Contact park interpreter Coy Ainsley at 1-606-286-7009 for information or email cartercave”
  - reservable = true · “e Resort Park (606) 286-4411 paul.tierney@ky.gov 344 Caveland Drive, Olive Hill, KY 41164 Reserve A Campsite Reserve A Lodge / Cottage View ”
  - restrooms = "yes (kind not stated)" · “ions to enhance facilities and visitor experiences. LEARN MORE ALERT: Currently the lower bathhouse at the Carter Caves Campgound is under r”

## US-TN: 12 random samples (records with facts; seed = the date)


## US-SC: 12 random samples (records with facts; seed = the date)

- **Dreher Island State Park** (US-2893, state, status ok, 12 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/dreher-island/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/dreher-island" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/dreher-island”
  - fees = "$11 -13.50 which allows up to 10 campers | $5-6.50 incremen · “To make a primitive group camping reservation, contact the park directly. Minimum rate is $11 -13.50 which allows up to 10 campers. The rate”
  - hookups.electric = true · “by both RVs and tents, while 15 sites are for tent campers only. Each site has water and electrical hook-ups and a picnic table. Many sites ”
  - hookups.water = true · “ay be used by both RVs and tents, while 15 sites are for tent campers only. Each site has water and electrical hook-ups and a picnic table. ”
  - phone_hint = "(803) 364-4152" · “arks Official Site Dreher Island DIRECTIONS 3677 State Park RD Prosperity, SC 29127 PHONE 803.364.4152 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - reservable = true · “ficer or elected/appointed officials.) The area includes central water and picnic tables. Reservations are accepted. To make a primitive gro”
  - restrooms = "yes (kind not stated)" · “date RVs up to 45 feet, others up to 30 feet. All sites are convenient to hot showers and restrooms. Camping Reservations: To make a camping”
  - rules.pets = "Pets are not allowed in the villas or the villa areas" · “& under free. PETS Beginning January 1, 2020, pets will be allowed in camper cabins 2-5. Pets are not allowed in the villas or the villa are”
  - rv_max_ft = 45 · “y. Each site has water and electrical hook-ups and a picnic table. Many sites accommodate RVs up to 45 feet, others up to 30 feet. All sites”
- **Lake Warren State Park** (US-2903, state, status ok, 9 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/lake-warren/faqs)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/lake-warren" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/lake-warren”
  - drinking_water = true · “e 2 weeks in advance by calling or visiting the park. The only convenience in the area is potable water, the day use public restrooms are av”
  - fees = "$22 a night, and reservations for individual use can only b · “groups. If no group is using the area, we do allow individuals to camp there. The cost is $22 a night, and reservations for individual use c”
  - hookups.electric = true · “Lake Warren has three jon boats for rent, for $25 per day which includes life jackets, an electric trolling motor and battery. The boats are”
  - reservable = true · “adults and fishing equipment. There is a third seat that can accommodate a child. You can reserve a boat up to 3 days in advance by calling ”
  - restrooms = "yes (kind not stated)" · “visiting the park. The only convenience in the area is potable water, the day use public restrooms are available but are about 900 yards fro”
  - rules.pets = "Pets are allowed in most outdoor areas provided they are ke · “S HOURS 9 a.m. - 6 p.m., daily OFFICE 11 a.m. - noon, daily ADMISSION Free admission PETS Pets are allowed in most outdoor areas provided th”
  - rules.stay_limit = "3 days" · “ing equipment. There is a third seat that can accommodate a child. You can reserve a boat up to 3 days in advance by calling the park (803) ”
- **Black River State Park** (US-13198, state, status ok, no campground facts in the page text: needs browser?, 1 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/)
  - rules.pets = "Pet Friendly" · “n Ultimate Outsider. GET THE GUIDE PICK UP A PARK PASSPORT Come Out & Play 5K Race Series Pet Friendly Lodging Fall Foliage Report EXPLORE M”
- **Calhoun Falls State Park** (US-2887, state, status ok, 11 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/calhoun-falls/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/calhoun-falls" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/calhoun-falls”
  - hookups.electric = true · “ted along the shores of Lake Russell. Two of the campgrounds provide individual water and electrical hookups. Some of these sites accommodat”
  - hookups.water = true · “s are located along the shores of Lake Russell. Two of the campgrounds provide individual water and electrical hookups. Some of these sites ”
  - phone_hint = "(864) 447-8267" · “ficial Site Calhoun Falls DIRECTIONS 46 Maintenance Shop RD Calhoun Falls, SC 29628 PHONE 864.447.8267 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - restrooms = "yes (kind not stated)" · “centralized water. All but one tent site is waterfront. Each campground is convenient to restrooms with hot showers. Camping Reservations: T”
  - rules.pets = "Pets are allowed in most outdoor areas provided they are ke · “ly ADMISSION $3 adults; $1.50 SC seniors; $1 children age 6-15; age 5 & younger free PETS Pets are allowed in most outdoor areas provided th”
  - rv_max_ft = 40 · “pgrounds provide individual water and electrical hookups. Some of these sites accommodate RVs up to 40 feet, others up to 30 feet. While ten”
  - showers = true · “All but one tent site is waterfront. Each campground is convenient to restrooms with hot showers. Camping Reservations: To make a camping re”
  - sites.tent = 14 · “ing the park directly. Standard Sites with Elec. & Water: 86 sites Designated Tent Sites: 14 walk-in tent sites Laundry Facilities: Yes Dump”
- **Edisto Beach State Park** (US-2894, state, status ok, 12 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/edisto-beach/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/edisto-beach" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/edisto-beach”
  - dump_station = true · “a.m. - 6 p.m. daily (extended to 8 p.m. during Daylight Savings Time) OFFICE M-F 9am-5pm Dump Station Gate Hours: 8:00 a.m. to 6:00 p.m., da”
  - hookups.amps = [20, 30, 50] · “reservation by contacting the park directly. Standard Sites with Elec. & Water: 112 sites 50 Amp Service Sites: All of the standard campsite”
  - hookups.electric = true · “tations and grocery stores. Camping Information: There are two campgrounds with water and electrical hookups that are available ocean-side o”
  - hookups.water = true · “filling stations and grocery stores. Camping Information: There are two campgrounds with water and electrical hookups that are available oce”
  - phone_hint = "(843) 869-2156" · “s Official Site Edisto Beach DIRECTIONS 8377 State Cabin RD Edisto Island, SC 29438 PHONE 843.869.2156 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - restrooms = "yes (kind not stated)" · “ated areas. Several sites accommodate RVs up to 40 feet. Each campground is convenient to restrooms with hot showers. Camping Reservations: ”
  - rules.pets = "Pets are not allowed in the cabins or the cabin areas" · “ISSION $8/adult; $5 SC seniors; $4/ child age 6-15; Free for children 5 and younger. PETS Pets are not allowed in the cabins or the cabin ar”
  - rv_max_ft = 40 · “ar the salt marsh. Camping is only allowed in designated areas. Several sites accommodate RVs up to 40 feet. Each campground is convenient t”
- **Devil's Fork State Park** (US-2892, state, status ok, 19 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/devils-fork/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/devils-fork" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/devils-fork”
  - checkin = "2pm" · “parking for campers is located at the entrance of the non-motorized access area. Camping check in time is 2pm and check out time is 12pm. La”
  - checkout = "12pm" · “ocated at the entrance of the non-motorized access area. Camping check in time is 2pm and check out time is 12pm. Late arrival instructions ”
  - drinking_water = true · “include a picnic table and a fire ring, but do not include electrical or water hook-ups. Water spigots and restrooms are located adjacent to”
  - dump_station = true · “tents may be placed on the ground. Each site has a picnic table and fire ring. A central dump station is available along the main campground”
  - fees = "$20.00 per vehicle per day to park in the overflow parking  · “te. One vehicle per designated tent and boat in site. Additional vehicles will be charged $20.00 per vehicle per day to park in the overflow”
  - hookups.electric = "some" · “main lakeside campground at Devils Fork State Park features 59 paved sites with water and electrical hook-ups. Some of these sites accommoda”
  - hookups.water = "some" · “ater: The main lakeside campground at Devils Fork State Park features 59 paved sites with water and electrical hook-ups. Some of these sites”
  - phone_hint = "(864) 944-2639" · “arolina Parks Official Site Devils Fork DIRECTIONS 161 Holcombe CIR Salem, SC 29676 PHONE 864.944.2639 EMAIL MAKE A RESERVATION TOP 5 THINGS”
- **Baker Creek State Park** (US-2884, state, status ok, 13 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/baker-creek/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/baker-creek" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/baker-creek”
  - hookups.amps = [50] · “PARK ADVISORY THE CAMPGROUND IS NOW OPEN! With two new family-style comfort stations and 50-amp service. All trails are currently closed due”
  - hookups.electric = true · “ion by contacting the park directly. Standard Sites with Elec. & Water: 30 standard sites Full Hookup Sites with Elec, Water, Sewer: 2 full ”
  - hookups.sewer = true · “ion by contacting the park directly. Standard Sites with Elec. & Water: 30 standard sites Full Hookup Sites with Elec, Water, Sewer: 2 full ”
  - hookups.water = true · “ion by contacting the park directly. Standard Sites with Elec. & Water: 30 standard sites Full Hookup Sites with Elec, Water, Sewer: 2 full ”
  - phone_hint = "(864) 443-2457" · “a Parks Official Site Baker Creek DIRECTIONS 863 Baker Creek RD McCormick, SC 29835 PHONE 864.443.2457 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - restrooms = "yes (kind not stated)" · “ENTLY ASKED QUESTIONS PARK ADVISORY THE CAMPGROUND IS NOW OPEN! With two new family-style comfort stations and 50-amp service. All trails ar”
  - rules.pets = "Pets are allowed in most outdoor areas provided they are ke · “m. ADMISSION $3 adults; $1.50 SC seniors; $1 children age 6-15; age 5 & younger free PETS Pets are allowed in most outdoor areas provided th”
  - showers = true · “ong the shores of Strom Thurmond Lake. The campground is convenient to restrooms with hot showers. Camping Reservations: To make a camping r”
- **Main campground (sites 1–25); Trailside walk-in tent/hammock sites (sites 26–35); Primitive group camping area** (US-2895:hq0, state, status ok, 14 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/givhans-ferry/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/givhans-ferry" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/givhans-ferry”
  - features = "fire ring, picnic table and storage box for food and suppli · “arking area. These tent/hammock sites have water and 20 amp electric, as well as a grill, fire ring, picnic table and storage box for food a”
  - fees = "$13 -$15.50 which allows up to ten campers | $5-6.25 increm · “To make a primitive group camping reservation, contact the park directly. Minimum rate is $13 -$15.50 which allows up to ten campers. The ra”
  - hookups.amps = [20, 30, 50] · “rk Coast Camping Camping Information: Sites 1 – 25 are full service with water, sewer and 50/30/20 amp power. Many sites can accommodate 40’”
  - hookups.electric = true · “ing Camping Information: Sites 1 – 25 are full service with water, sewer and 50/30/20 amp power. Many sites can accommodate 40’ RVs, others ”
  - hookups.sewer = true · “y State Park Coast Camping Camping Information: Sites 1 – 25 are full service with water, sewer and 50/30/20 amp power. Many sites can accom”
  - hookups.water = true · “cking in on today, Friday, you must make the reservation by contacting the park directly. Full Hookup Sites with Elec, Water, Sewer: 25 site”
  - phone_hint = "(843) 873-0692" · “ks Official Site Givhans Ferry DIRECTIONS 746 Givhans Ferry RD Ridgeville, SC 29472 PHONE 843.873.0692 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - reservable = true · “nted officials. The area includes central water, fire ring and nearby restoom facilities. Reservations are accepted. To make a primitive gro”
- **Family campground; Equestrian campground; Primitive group camping area** (US-2905:hq0, state, status ok, 14 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/lee/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/lee" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/lee”
  - fees = "$14.50 which allows up to ten campers | $6.50 increments fo · “To make a primitive group camping reservation, contact the park directly. Minimum rate is $14.50 which allows up to ten campers. The rate in”
  - hookups.electric = true · “Camping Information: The park campground is open year round. Each campsite has water and electrical hookups and is convenient to restrooms w”
  - hookups.sewer = true · “s are available for family camping, while 18 sites are designated for equestrian campers. Full Hookup Sites with Elec, Water, Sewer: Sites 1”
  - hookups.water = true · “ds Camping Camping Information: The park campground is open year round. Each campsite has water and electrical hookups and is convenient to ”
  - phone_hint = "(803) 428-5307" · “South Carolina Parks Official Site Lee DIRECTIONS 487 Loop RD Bishopville, SC 29010 PHONE 803.428.5307 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - reservable = true · “The area has 3 designated sites (25 people per site). There is central water and a privy. Reservations are accepted. To make a primitive gro”
  - restrooms = "vault" · “ials.) The area has 3 designated sites (25 people per site). There is central water and a privy. Reservations are accepted. To make a primit”
  - rules.pets = "Pets are allowed in most outdoor areas provided they are ke · “-Thursday 11am-12pm, Friday-Sunday 10am-5pm, closed Monday. ADMISSION Free admission PETS Pets are allowed in most outdoor areas provided th”
- **Hamilton Branch State Park** (US-2897, state, status ok, 11 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/hamilton-branch/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/hamilton-branch" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/hamilton-branch”
  - dump_station = true · “ch include restroom facilities with hot showers are also located throughout the park. Two dump stations are available for RVs. Camping Reser”
  - hookups.electric = true · “contacting the park directly. Standard Sites with Elec. & Water: 173 sites with water and electricity Designated Tent Sites: 11 sites are av”
  - hookups.water = true · “vation by contacting the park directly. Standard Sites with Elec. & Water: 173 sites with water and electricity Designated Tent Sites: 11 si”
  - phone_hint = "(864) 333-2223" · “ks Official Site Hamilton Branch DIRECTIONS 111 Campground RD Plum Branch, SC 29845 PHONE 864.333.2223 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - restrooms = "yes (kind not stated)" · “Lake is available. Some sites accommodate RVs up to 40 feet, others up to 35 feet. Eight comfort stations which include restroom facilities ”
  - rules.pets = "Pets are allowed in most outdoor areas provided they are ke · “m. ADMISSION $3 adults; $1.50 SC seniors; $1 children age 6-15; age 5 & younger free PETS Pets are allowed in most outdoor areas provided th”
  - rv_max_ft = 40 · “ion: Camping along the shores of Strom Thurmond Lake is available. Some sites accommodate RVs up to 40 feet, others up to 35 feet. Eight com”
  - showers = true · “, others up to 35 feet. Eight comfort stations which include restroom facilities with hot showers are also located throughout the park. Two ”
- **H. Cooper Black Jr. Memorial State Recreation Area** (US-3874, state, status ok, 11 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/h-cooper-black/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/h-cooper-black" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/h-cooper-black”
  - dump_station = true · “e campsites available on the park. There are two comfort stations with hot showers and an RV dump station. Camping Reservations: To make a c”
  - hookups.electric = true · “Area Midlands Camping Campground Map Camping Information: The park has 27 campsites with electricity and water. There are also some primitiv”
  - hookups.water = true · “Area Midlands Camping Campground Map Camping Information: The park has 27 campsites with electricity and water. There are also some primitiv”
  - map.date_how = "PDF, no date in the link" · “link “Campground Map””
  - map.url = "https://embed.widencdn.net/pdf/plus/scprt/cmtxtlns4d/24-SCP · “link “Campground Map” -> https://embed.widencdn.net/pdf/plus/scprt/cmtxtlns4d/24-SCP-5435-H-Cooper-Black-Jr-Campground-Map.pd”
  - phone_hint = "(843) 253-5124" · “arks Official Site H. Cooper Black DIRECTIONS 279 Sporting Dog TRL Cheraw, SC 29520 PHONE 843.253.5124 EMAIL MAKE A RESERVATION TOP 5 THINGS”
  - restrooms = "yes (kind not stated)" · “y and water. There are also some primitive campsites available on the park. There are two comfort stations with hot showers and an RV dump s”
  - showers = true · “o some primitive campsites available on the park. There are two comfort stations with hot showers and an RV dump station. Camping Reservatio”
- **Huntington Beach State Park** (US-2900, state, status ok, 12 facts) · [southcarolinaparks.com](https://southcarolinaparks.com/huntington-beach/camping)
  - booking.how = "online: reserve.southcarolinaparks.com" · “link “MAKE A RESERVATION””
  - booking.url = "https://reserve.southcarolinaparks.com/huntington-beach" · “link “MAKE A RESERVATION” -> https://reserve.southcarolinaparks.com/huntington-beach”
  - hookups.electric = "some" · “amping Camping Information: Each site, excluding the designated tent sites, has water and electrical hookups and is convenient to hot shower”
  - hookups.sewer = "some" · “er and electrical hookups and is convenient to hot showers and restrooms. Some sites have sewer hookups. Several sites accommodate RVs up to”
  - hookups.water = true · “rk Coast Camping Camping Information: Each site, excluding the designated tent sites, has water and electrical hookups and is convenient to ”
  - phone_hint = "(843) 237-4440" · “Official Site Huntington Beach DIRECTIONS 16148 Ocean HWY Murrells Inlet, SC 29576 PHONE 843.237.4440 EMAIL MAKE A RESERVATION TOP 5 THINGS ”
  - restrooms = "yes (kind not stated)" · “ignated tent sites, has water and electrical hookups and is convenient to hot showers and restrooms. Some sites have sewer hookups. Several ”
  - rules.pets = "Dogs are allowed on the south end of the beach" · “t remain on a leash no longer than six feet at all times. Please clean up after your pet. Dogs are allowed on the south end of the beach. Do”
  - rv_max_ft = 40 · “nt to hot showers and restrooms. Some sites have sewer hookups. Several sites accommodate RVs up to 40 feet, others up to 30 feet. While ten”
  - showers = true · “ding the designated tent sites, has water and electrical hookups and is convenient to hot showers and restrooms. Some sites have sewer hooku”

## US-IA: 12 random samples (records with facts; seed = the date)


## US-MA: 12 random samples (records with facts; seed = the date)

- **Willard Brook State Forest** (US-4752, state, status ok, 9 facts) · [www.mass.gov](https://www.mass.gov/locations/willard-brook-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/willard-b · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/willard-brook-state-forest/r/campgroundDetails.do?”
  - fees = "$14/night for Massachusetts residents and | $40/night for n · “allowed at yurt campsites Read the rules for hunting in state parks More info Camping is $14/night for Massachusetts residents and $40/night”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/willard-brook-state-forest-trail-m · “link “Download a trail map” -> https://www.mass.gov/doc/willard-brook-state-forest-trail-map/download”
  - reservable = true · “more less contact info Online willard.brook@state.ma.us Dogs Allowed Download a trail map Reserve a campsite Self-guided opportunities Get D”
  - rules.pets = "Dogs Allowed" · “4 Directions Phone (978) 597-8802 more less contact info Online willard.brook@state.ma.us Dogs Allowed Download a trail map Reserve a campsi”
  - season = "late May through early September" · “, including, hiking, and cross-country skiing. Hours Sunrise to sunset Campground office (late May to early September) Sunday - Saturday: 9:”
  - sites.total = 21 · “urday: 9:00 am-10:00 pm Parking Parking available Activities Camping Willard Brook offers 21 campsites and one group yurt Hiking Try the Fri”
- **Mohawk Trail State Forest** (US-4747, state, status ok, 10 facts) · [www.mass.gov](https://www.mass.gov/locations/mohawk-trail-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a Campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/unifSearchResults · “link “Reserve a Campsite” -> https://massdcrcamping.reserveamerica.com/unifSearchResults.do”
  - fees = "$17/night for Massachusetts residents and | $54/night non-r · “ough mid-October. Pets are prohibited from cabins. Reservations required. Tent camping is $17/night for Massachusetts residents and $54/nigh”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/mohawk-trail-state-forest-trail-ma · “link “Download a trail map” -> https://www.mass.gov/doc/mohawk-trail-state-forest-trail-map/download”
  - reservable = true · “lowed Historic site Download a trail map Self-guided opportunities Mohican - Mohawk Trail Reserve a Campsite October Programs Get Directions”
  - rules.pets = "Dogs Allowed" · “13) 339-5504 more less contact info Online mohawk.trail@state.ma.us Wheelchair Accessible Dogs Allowed Historic site Download a trail map Se”
  - season = "mid-May through mid-October" · “cabins Picnicking Restrooms Restrictions No alcohol No littering More info Campsites are available mid-May through mid-October. Pets are pro”
  - sites.cabin = 6 · “rs Sunrise to sunset Parking Parking available Activities Camping 53 wooded campsites and 6 overnight log cabins available Fishing You can f”
  - sites.total = 53 · “ant and animal life. Hours Sunrise to sunset Parking Parking available Activities Camping 53 wooded campsites and 6 overnight log cabins ava”
- **Lorraine Park Campground** (US-4746:hq1, state, status ok, 6 facts) · [www.mass.gov](https://www.mass.gov/locations/harold-parker-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/harold-pa · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/harold-parker-state-forest/r/campgroundDetails.do?”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “Beach wheelchairs available Restrictions No alcohol No littering More info Camping costs $17/night for Massachusetts residents and $54/night”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/harold-parker-state-forest-trail-m · “link “Download a trail map” -> https://www.mass.gov/doc/harold-parker-state-forest-trail-map/download”
  - sites.total = 89 · “The Lorraine Park Campground offers 89 campsites for tents, trailers, or R.V.s. All Activities Hiking Camping Canoeing and kayaking Fishin”
- **Lorraine Park Campground** (US-4746:hq0, state, status ok, 6 facts) · [www.mass.gov](https://www.mass.gov/locations/harold-parker-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/harold-pa · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/harold-parker-state-forest/r/campgroundDetails.do?”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “Beach wheelchairs available Restrictions No alcohol No littering More info Camping costs $17/night for Massachusetts residents and $54/night”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/harold-parker-state-forest-trail-m · “link “Download a trail map” -> https://www.mass.gov/doc/harold-parker-state-forest-trail-map/download”
  - sites.total = 89 · “The Lorraine Park Campground offers 89 campsites for tents, trailers, or R.V.s. All Activities Hiking Camping Canoeing and kayaking Fishin”
- **Shawme-Crowell campground** (US-4697:hq0, state, status ok, 7 facts) · [www.mass.gov](https://www.mass.gov/locations/shawme-crowell-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/shawme-cr · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/shawme-crowell-state-forest/r/campgroundDetails.do”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “ility Camping Parking Restrooms Restrictions No alcohol No littering More info Camping is $17/night for Massachusetts residents and $54/nigh”
  - phone_hint = "(781) 233-0834" · “about the local habitat. Explore a variety of nature and wildlife across 65 acres. Phone (781) 233-0834 Open Thursday, Friday, and Saturday ”
  - reservable = true · “t info Online shawme.crowell@state.ma.us Wheelchair Accessible Dogs Allowed Historic site Reserve a campsite Southeastern MA Adult Walking C”
  - rules.pets = "Dogs Allowed" · “) 888-0351 more less contact info Online shawme.crowell@state.ma.us Wheelchair Accessible Dogs Allowed Historic site Reserve a campsite Sout”
  - sites.total = 27 · “ng State Forest, Erving, MA 01344 Directions Visit for a swim or hike, camp at one of our 27 sites, or kayak on Laurel Lake. Phone (978) 544”
- **Wells State Park campground** (US-2462:hq0, state, status ok, 7 facts) · [www.mass.gov](https://www.mass.gov/locations/wells-state-park)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/wells-sta · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/wells-state-park/r/campgroundDetails.do?contractCo”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/wells-state-park-trail-map/downloa · “link “Download a trail map” -> https://www.mass.gov/doc/wells-state-park-trail-map/download”
  - reservable = true · “22-6762 Wheelchair Accessible Dogs Allowed Download a trail map Self-guided opportunities Reserve a campsite Sign Up for DCR Central Valley ”
  - rules.pets = "Dogs Allowed" · “tions Phone Headquarters (508) 347-9257 Reservations (877) 422-6762 Wheelchair Accessible Dogs Allowed Download a trail map Self-guided oppo”
  - sites.total = 60 · “me senior parking pass Activities Camping Bring your tent, trailer, or R.V. to any of the 60 sites located near Walker Pond Hiking Hike up C”
- **Granville State Forest campground** (US-4703:hq0, state, status ok, 10 facts) · [www.mass.gov](https://www.mass.gov/locations/granville-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/granville · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/granville-state-forest/r/campgroundDetails.do?cont”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “ed off-road vehicles No wilderness camping Dogs must remain on-leash More info Camping is $17/night for Massachusetts residents and $54/nigh”
  - hookups.electric = false · “/night for Massachusetts residents and $54/night for non-residents. Campsites do not have electric hookups. Learn more about camping at Gran”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/granville-state-forest-trail-map" · “link “Download a trail map” -> https://www.mass.gov/doc/granville-state-forest-trail-map”
  - phone_hint = "(781) 233-0834" · “about the local habitat. Explore a variety of nature and wildlife across 65 acres. Phone (781) 233-0834 Open Thursday, Friday, and Saturday ”
  - reservable = true · “rections Phone (413) 357-6611 Dogs Allowed Download a trail map Self-guided opportunities Reserve a campsite Get Directions to Granville Sta”
  - rules.pets = "Dogs Allowed" · “orest Address 323 West Hartland Road, Granville, MA 01034 Directions Phone (413) 357-6611 Dogs Allowed Download a trail map Self-guided oppo”
  - sites.total = 27 · “ng State Forest, Erving, MA 01344 Directions Visit for a swim or hike, camp at one of our 27 sites, or kayak on Laurel Lake. Phone (978) 544”
- **Wellfleet Hollow State Campground** (US-8381:hq0, state, status ok, 5 facts) · [www.mass.gov](https://www.mass.gov/locations/wellfleet-hollow-state-campground)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/wellfleet · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/wellfleet-hollow-state-campground/r/campgroundDeta”
  - phone_hint = "(508) 349-3007" · “llow State Campground Address 180 Old Kings Highway, Wellfleet, MA 02667 Directions Phone (508) 349-3007 Reserve a campsite Get Directions t”
  - reservable = true · “ground Address 180 Old Kings Highway, Wellfleet, MA 02667 Directions Phone (508) 349-3007 Reserve a campsite Get Directions to Wellfleet Hol”
  - sites.total = 27 · “ng State Forest, Erving, MA 01344 Directions Visit for a swim or hike, camp at one of our 27 sites, or kayak on Laurel Lake. Phone (978) 544”
- **Clarksburg State Park campground** (US-2426:hq0, state, status ok, 16 facts) · [www.mass.gov](https://www.mass.gov/locations/clarksburg-state-park)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/clarksbur · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/clarksburg-state-park/r/campgroundDetails.do?contr”
  - dump_station = false · “lable. Campsites accommodate tents, pop-up trailer and small RV. No electrical hook up or dump station. Hiking & walking 4.5 miles of foot t”
  - features = "fire ring" · “awme Crowell State Forest. Each accessible campsite is equipped with a picnic table and a fire ring. The parking areas are crushed stone and”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “cted to designated areas only Dogs on leash. Clean up after your pet More info Camping is $17/night for Massachusetts residents and $54/nigh”
  - hookups.electric = false · “ilets and showers available. Campsites accommodate tents, pop-up trailer and small RV. No electrical hook up or dump station. Hiking & walki”
  - hookups.water = true · “de paved area for parking, and a hard crushed stone surface in the rest of the camp site. Water and electricity hookups are provided on an a”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/clarksburg-state-park-trail-map/do · “link “Download a trail map” -> https://www.mass.gov/doc/clarksburg-state-park-trail-map/download”
  - reservable = true · “ass.gov Wheelchair Accessible Dogs Allowed Self-guided opportunities Download a trail map Reserve a campsite Get Directions to Clarksburg St”
- **Charge Pond; Curlew Pond; Fearing Pond; Barretts Pond campgrounds** (US-4700:hq0, state, status ok, no campground facts even in a browser, 7 facts) · [www.mass.gov](https://www.mass.gov/locations/myles-standish-state-forest)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/myles-sta · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/myles-standish-state-forest/r/campgroundDetails.do”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/myles-standish-trail-map/download" · “link “Download a trail map” -> https://www.mass.gov/doc/myles-standish-trail-map/download”
  - reservable = true · “Rd., Carver, MA 02330 Directions Phone (508) 866-2526 Wheelchair Accessible Dogs Allowed Reserve a campsite Download a trail map Self-guided”
  - restrooms = "none" · “ring Pond Accessible restrooms Beach wheelchairs available (please note that College Pond restrooms are not accessible) Beach mat Restrictio”
  - rules.pets = "Dogs Allowed" · “194 Cranberry Rd., Carver, MA 02330 Directions Phone (508) 866-2526 Wheelchair Accessible Dogs Allowed Reserve a campsite Download a trail m”
- **Federated Women's Club State Forest** (US-4729, state, status ok, 6 facts) · [www.mass.gov](https://www.mass.gov/locations/federated-womens-club-state-forest)
  - booking.url = "https://www.mass.gov/how-to/reserve-a-campsite" · “booking link from our campstate-manual row (official system www.mass.gov)”
  - phone = "(978) 544-3939" · “. Before camping, contact park staff at Erving State Forest (978) 544-3939 Related parks Erving State Forest More parks Visit Massachu”
  - phone_hint = "(978) 544-3939" · “s are first come, first served. Before camping, contact park staff at Erving State Forest (978) 544-3939 Related parks Erving State Forest M”
  - reservable = false · “info Campground closed for the season. Primitive camping 15 campsites available Sites are first come, first served. Before camping, contact ”
  - rules.pets = "No pets allowed on Department of Conservation and Recre" · “kiing Fishing Hunting Facilities Scenic viewing area Restrictions No alcohol No littering No pets allowed on Department of Conservation and ”
  - sites.total = 15 · “operty No off-road vehicles More info Campground closed for the season. Primitive camping 15 campsites available Sites are first come, first”
- **Pearl Hill campground** (US-2452:hq0, state, status ok, 10 facts) · [www.mass.gov](https://www.mass.gov/locations/pearl-hill-state-park)
  - booking.how = "online: massdcrcamping.reserveamerica.com" · “link “Reserve a campsite””
  - booking.url = "https://massdcrcamping.reserveamerica.com/camping/pearl-hil · “link “Reserve a campsite” -> https://massdcrcamping.reserveamerica.com/camping/pearl-hill-state-park/r/campgroundDetails.do?contr”
  - fees = "$17/night for Massachusetts residents and | $54/night for n · “Dogs must remain on-leash Read the rules for hunting in state parks More info Camping is $17/night for Massachusetts residents and $54/night”
  - map.date_how = "web page, no date in the link" · “link “Download a trail map””
  - map.url = "https://www.mass.gov/doc/willard-brook-state-forest-trail-m · “link “Download a trail map” -> https://www.mass.gov/doc/willard-brook-state-forest-trail-map/download”
  - reservable = true · “ine willard.brook@state.ma.us Dogs Allowed Self-guided opportunities Download a trail map Reserve a campsite Get Directions to Pearl Hill St”
  - restrooms = "yes (kind not stated)" · “Activities Camping Visitors can choose from more than 50 campsites, which are served by a bathhouse. Swimming Cool off with a dip in Pearl H”
  - rules.pets = "Dogs Allowed" · “bor Day weekend 9 a.m. - 10 p.m.. more less contact info Online willard.brook@state.ma.us Dogs Allowed Self-guided opportunities Download a ”
  - showers = true · “Activities Camping Visitors can choose from more than 50 campsites, which are served by a bathhouse. Swimming Cool off with a dip in Pearl H”
  - sites.total = 50 · “to sunset Parking Parking available Activities Camping Visitors can choose from more than 50 campsites, which are served by a bathhouse. Swi”

## US-CO: 12 random samples (records with facts; seed = the date)

- **Campsite(s) 233** (US-1243:64, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Campsite(s) 205** (US-1243:40, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Campsite(s) 431** (US-1243:29, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Cherokee** (US-1213:3, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Campsite(s) 402** (US-1243:22, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Bald Eagle Point** (US-1241:6, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Bookcliff** (US-1221:1, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Cabin #2** (US-1219:15, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Campsites** (US-1219:18, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Arapahoe** (US-1213:2, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **215 T** (US-1243:75, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”
- **Campsite(s) 210** (US-1243:46, state, status ok, 4 facts) · [cpw.state.co.us](https://cpw.state.co.us/state-parks)
  - booking.how = "online: www.cpwshop.com" · “link “Make a Reservation””
  - booking.url = "https://www.cpwshop.com/campinghome.page" · “link “Make a Reservation” -> https://www.cpwshop.com/campinghome.page”
  - restrooms = "some" · “Parks also feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting sp”
  - showers = true · “feature accessible facilities such as fishing piers, campsites, cabins, yurts, restrooms, showers, visitor centers and meeting spaces. Find ”

## US-MT: 12 random samples (records with facts; seed = the date)


## US-NV: 12 random samples (records with facts; seed = the date)

- **Wild Horse State Recreation Area** (US-4446, state, status ok, 15 facts) · [parks.nv.gov](https://parks.nv.gov/parks/wild-horse)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - dump_station = true · “but restrooms and showers are available year round. Centrally located water faucets and a dump station are available during summer months on”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “nd on the Owyhee Desert west of Wild Horse. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - hookups.electric = false · “pground has 34 sites with a table, shade, a fire pit and a camp pad at each. There are no hookups, but restrooms and showers are available y”
  - map.date_how = "PDF, year 2014 in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/Wild_Horse_SRA_1_Beach_Trail_NET · “link “Trails / Map” -> https://parks.nv.gov/forms/Wild_Horse_SRA_1_Beach_Trail_NET_otln_reduced_2014-02-10.pdf”
  - restrooms = "yes (kind not stated)" · “4 sites with a table, shade, a fire pit and a camp pad at each. There are no hookups, but restrooms and showers are available year round. Ce”
  - rules.fires = "fire pits" · “s for the exit and re-entry of the park only. Ground fires are allowed only in designated fire pits. Removing, disturbing or damaging any hi”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “other feature is prohibited. State and federal laws protect this area and its resources. Pets are welcome, but they must be kept on a leash ”
- **Kershaw-Ryan State Park** (US-2632, state, status ok, 16 facts) · [parks.nv.gov](https://parks.nv.gov/parks/kershaw-ryan)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - dump_station = true · “Camping : The park has a 16-unit campground with a restroom, coin-operated showers and an RV dump station. Each site has a shade ramada, pic”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “;Kershaw Gardens&rdquo; by local residents. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - hookups.amps = [30, 50] · “site has a shade ramada, picnic table, fire ring and grill. Each of the 16 campsites has 30 amp and 50 amp power and water hookups. The camp”
  - hookups.electric = true · “ramada, picnic table, fire ring and grill. Each of the 16 campsites has 30 amp and 50 amp power and water hookups. The camping limit is seve”
  - hookups.water = true · “cnic table, fire ring and grill. Each of the 16 campsites has 30 amp and 50 amp power and water hookups. The camping limit is seven days in ”
  - map.date_how = "PDF, no date in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/KershawRyan_4.pdf" · “link “Trails / Map” -> https://parks.nv.gov/forms/KershawRyan_4.pdf”
  - reservable = false · “rom frost free hydrants available all year long. RV Dump station available all year long. First Come, First Serve Camping : Within the campg”
- **Washoe Lake State Park** (US-2640, state, status ok, 15 facts) · [parks.nv.gov](https://parks.nv.gov/parks/washoe-lake)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - dump_station = true · “eet in length. Campground Loop A offers water and utility hook-ups at all 24 sites, and a dump station is available. The camping limit is se”
  - features = "fire ring" · “tions FACILITES & AMENITIES Camping : The park has 49 sites, each with a table, grill and fire ring. The campground is open year round and a”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “other tools used for hunting and gathering. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - hookups.electric = true · “e. Several sites can hold RVs up to 45 feet in length. Campground Loop A offers water and utility hook-ups at all 24 sites, and a dump stati”
  - hookups.water = true · “e. Several sites can hold RVs up to 45 feet in length. Campground Loop A offers water and utility hook-ups at all 24 sites, and a dump stati”
  - map.date_how = "PDF, no date in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/washoe_trail_map.pdf" · “link “Trails / Map” -> https://parks.nv.gov/forms/washoe_trail_map.pdf”
  - restrooms = "yes (kind not stated)" · “ar round and available by reservation. Some sites are equipped with shade structures. Two comfort stations, one with a shower, are available”
- **Big Bend campground; first-come, first-served sites behind campground loop** (US-4437:hq0, state, status ok, 15 facts) · [parks.nv.gov](https://parks.nv.gov/parks/big-bend-of-the-colorado)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - features = "fire pit" · “commodate any size RV. The sites also have a tent pad, a shade ramada, barbecue grill and fire pit. Three of the sites are ADA equipped and ”
  - fees = "$10.00 per vehicle (Non-NV Vehicles: | $15.00 per vehicle)  · “the valley and within the recreation area. ( READ MORE ) Park Fees Day use entrance fee: $10.00 per vehicle (Non-NV Vehicles: $15.00 per veh”
  - hookups.electric = true · “d. All sites are available by reservation. All sites are designed to accommodate RVs with hook-ups for water, electric and sewer. In additio”
  - hookups.sewer = true · “ervation. All sites are designed to accommodate RVs with hook-ups for water, electric and sewer. In addition, most of the sites have pull-th”
  - map.date_how = "PDF, year 2014 in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/Big_Bend_of_the_Colorado_1_Range · “link “Trails / Map” -> https://parks.nv.gov/forms/Big_Bend_of_the_Colorado_1_Ranger_NET_otln_reduced_2014-02-09.pdf”
  - reservable = "mixed" · “y have to request yours be unloacked upon arival if it has not already been done for you. First Come, First Serve Camping : Behind the campg”
  - restrooms = "yes (kind not stated)" · “pped and available for those visitors with the proper ADA permit. Other amenities include restroom and shower facilities. Camping is limited”
- **Dayton State Park** (US-2629, state, status ok, 9 facts) · [parks.nv.gov](https://parks.nv.gov/parks/dayton)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - dump_station = true · “n campsites at the park that can accommodate 34' RVs, with picnic tables and barbecues. A dump station and restrooms with flush toilets are ”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “a beckoned, Abner and his friends moved on. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - hookups.electric = true · “sh. Group Area : The park features a shaded group-use area with 10 picnic tables, a sink, electricity, a large barbecue, a lawn area and ple”
  - restrooms = "flush" · “accommodate 34' RVs, with picnic tables and barbecues. A dump station and restrooms with flush toilets are also available. The camping limit”
  - rules.fires = "firewood within the park is not allowed" · “come, but they must be kept on a leash of not more than six feet in length. Collection of firewood within the park is not allowed. Fires are”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “can be arranged for groups. Hours : Open seven days a week, 365 days a year. FIELD NOTES Pets are welcome, but they must be kept on a leash ”
  - rules.quiet_hours = "10 p.m. to 7 a.m" · “d federal laws protect this area and its resources. Hunting is not permitted in the park. Quiet hours are from 10 p.m. to 7 a.m. The use of ”
- **Ward Charcoal Ovens State Park** (US-2639, state, status ok (browser), 8 facts) · [parks.nv.gov](https://parks.nv.gov/parks/ward-charcoal-ovens)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “built smelters (furnaces) for melting ores. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - map.date_how = "PDF, year 2014 in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/Ward_Charcoal_Ovens_1_Ridgeline_ · “link “Trails / Map” -> https://parks.nv.gov/forms/Ward_Charcoal_Ovens_1_Ridgeline_Loop_NET_otln_reduced_2014-02-10.pdf”
  - restrooms = "yes (kind not stated)" · “eas that provide a great spot for a day hike and picnic. These areas have covered tables, restrooms, grills and wonderful views. Fishing : T”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “other feature is prohibited. State and federal laws protect this area and its resources. Pets are welcome, but they must be kept on a leash ”
  - season = "year-round" · “n425___ View More Photos push your boundaries Explore More Nevada State Parks Cave Lake A year-round park, Cave Lake features a 32-acre rese”
- **Berlin-Ichthyosaur State Park** (US-2626, state, status ok, 13 facts) · [parks.nv.gov](https://parks.nv.gov/parks/berlin-ichthyosaur)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - drinking_water = true · “round), some suitable for RVs up to 25 feet, with fire rings, BBQ grills, covered tables, drinking water (typically available from mid-April”
  - dump_station = true · “(typically available from mid-April through the end of October) and restrooms nearby. An RV dump station is also available. Camping is limit”
  - features = "fire rings, BBQ grills, covered tables, drinking water (typ · “ontains 14 well-spaced units (open year-round), some suitable for RVs up to 25 feet, with fire rings, BBQ grills, covered tables, drinking w”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “town of Berlin, as well as the Diana Mine. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehic”
  - map.date_how = "PDF, no date in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/Berlin-Ichthyosaur_State_Park_Re · “link “Trails / Map” -> https://parks.nv.gov/forms/Berlin-Ichthyosaur_State_Park_Reduced_Pedestal_(002).pdf”
  - restrooms = "yes (kind not stated)" · “ables, drinking water (typically available from mid-April through the end of October) and restrooms nearby. An RV dump station is also avail”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “ilable in the nearby town of Gabbs. No services are available at the nearby town of Ione. Pets are welcome, but they must be kept on a leash”
- **Spooner Lake and Backcountry State Park** (US-3389, state, status ok (browser), 9 facts) · [parks.nv.gov](https://parks.nv.gov/parks/spooner-lake)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - fees = "$10.00 per vehicle (Non-NV Vehicles: | $15.00 per vehicle)  · “the original inverted siphons and is still in use today. Park Fees Day use entrance fee: $10.00 per vehicle (Non-NV Vehicles: $15.00 per veh”
  - map.date_how = "PDF, no date in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/uploads/documents/Spooner_Trail_Closer · “link “Trails / Map” -> https://parks.nv.gov/uploads/documents/Spooner_Trail_Closers_Hobart_Dam_Repair.pdf”
  - phone = ["(775) 831-0494", "(775) 588-0686"] · “eer opportunities are available. Contact the park office at (775) 831-0494 or the Tahoe Rim Trail Association at 775-588-0686. Program | ice”
  - restrooms = "vault" · “people comfortably and Wildcat Cabin sleeps two. Both cabins have basic amenities such as composting toilets, beds, cook stoves and wood bur”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “other feature is prohibited. State and federal laws protect this area and its resources. Pets are welcome, but they must be kept on a leash ”
  - season = "July 15 through September 30" · “e at ndow.org . At Spooner Lake, the limit is five and bait is allowed. The Marlette Lake season runs July 15 through September 30 and is ca”
- **Spring Valley State Park** (US-2636, state, status ok (browser), 7 facts) · [parks.nv.gov](https://parks.nv.gov/parks/spring-valley)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “en used as a lookout for these inhabitants. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - reservable = false · “g : Ranch Campground is located two miles north of the main campground. This area remains first come, first served. This facility has seven ”
  - restrooms = "yes (kind not stated)" · “rst served. This facility has seven campsites with tables and grills. Water and primitive restrooms are available. The camping limit is 7 da”
  - rules.fires = "fire rings and grills provided" · “campgrounds. Camping is allowed only in designated areas. Fires are permitted only in the fire rings and grills provided. Collection of fire”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “other feature is prohibited. State and federal laws protect this area and its resources. Pets are welcome, but they must be kept on a leash ”
- **Rye Patch campground** (US-4444:hq0, state, status ok, 12 facts) · [parks.nv.gov](https://parks.nv.gov/parks/rye-patch)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - drinking_water = true · “has 25 units, a restroom with flush toilets and hot showers. A sanitary dump station with potable water is located on the dam's west side. A”
  - dump_station = true · “the reservoir's west side has 25 units, a restroom with flush toilets and hot showers. A sanitary dump station with potable water is located”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “of water covering most of the Great Basin. ( READ MORE ) Park Fees Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehic”
  - map.date_how = "PDF, year 2012 in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/forms/Rye_Patch_State_Recreation_Area_ · “link “Trails / Map” -> https://parks.nv.gov/forms/Rye_Patch_State_Recreation_Area_1_Westside_Campground_NET_otln_reduced_20”
  - restrooms = "flush" · “MENITIES Camping : The river campground below Rye Patch Dam has 22 units, a restroom with flush toilets and hot showers. The campground on t”
  - rules.pets = "Pets are welcome, but they must be kept on a leash of not m · “e headgear. OHV use is allowed on existing roads to access adjacent federal public lands. Pets are welcome, but they must be kept on a leash”
  - rules.quiet_hours = "10 p.m. - 7 a.m" · “sives are prohibited. The use of drones or any remote controlled aircraft is not allowed. Quiet hours are from 10 p.m. - 7 a.m. Visitors are”
- **Atlatl Rock Campground; Arch Rock Campground; group-use campsites** (US-2637:hq0, state, status ok, 12 facts) · [parks.nv.gov](https://parks.nv.gov/parks/valley-of-fire)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - dump_station = true · “al of 72 units. Campsites are equipped with shaded tables, grills, water and restrooms. A dump station and showers are available. All campsi”
  - fees = "$20/vehicle/night for Nevada residents, or | $25/vehicle/ni · “ites are available for overnight camping by reservation only. Camping and day-use fees of $20/vehicle/night for Nevada residents, or $25/veh”
  - hookups.electric = true · “pon request, special presentations can be arranged for groups. RV Camping : RV sites with power and water hookups are available. Visitor Inf”
  - hookups.water = true · “t, special presentations can be arranged for groups. RV Camping : RV sites with power and water hookups are available. Visitor Information :”
  - map.date_how = "PDF, no date in the link" · “link “Trails / Map””
  - map.url = "https://parks.nv.gov/uploads/documents/Valley_of_Fire_Broch · “link “Trails / Map” -> https://parks.nv.gov/uploads/documents/Valley_of_Fire_Brochure_Map.pdf”
  - reservable = true · “s, each accommodating up to 45 people. These sites are available for overnight camping by reservation only. Camping and day-use fees of $20/”
  - restrooms = "yes (kind not stated)" · “combined total of 72 units. Campsites are equipped with shaded tables, grills, water and restrooms. A dump station and showers are available”
- **Fort Churchill State Park** (US-2631, state, status ok, 14 facts) · [parks.nv.gov](https://parks.nv.gov/parks/fort-churchill)
  - booking.how = "online: parks.nv.gov" · “link “Reservations””
  - booking.url = "https://parks.nv.gov/about/reservations" · “link “Reservations” -> https://parks.nv.gov/about/reservations”
  - drinking_water = true · “king : A tree-shaded picnic area along the Carson River provides tables, charcoal grills, drinking water and a restroom. Buckland Station Pi”
  - dump_station = true · “ill, and all are shaded by large cottonwood trees. There are no hook-ups available, but a dump station is located near the entrance to the c”
  - fees = "$5.00 per vehicle (Non-NV Vehicles | $10.00 per vehicle) |  · “om survived into adulthood. ( READ MORE) Park Fees Fort Churchill : Day use entrance fee: $5.00 per vehicle (Non-NV Vehicles $10.00 per vehi”
  - hookups.electric = false · “fire ring and charcoal grill, and all are shaded by large cottonwood trees. There are no hook-ups available, but a dump station is located n”
  - map.date_how = "PDF, year 2022 in the link" · “link “Hunting Boundary Map””
  - map.url = "https://parks.nv.gov/uploads/documents/Fort_Churchill_Hunti · “link “Hunting Boundary Map” -> https://parks.nv.gov/uploads/documents/Fort_Churchill_Hunting_Zone_Jan_2022.pdf”
  - reservable = true · “A group area accomodating up to 60 people for group camping or picnicking is available by reservation only. The area includes a covered pavi”
  - restrooms = "vault" · “rsed camping or day-use area that includes picnic tables, fire rings with grill tops, one vault toilet, and multiple horse corrals. Scout Ca”

## US-WA: 12 random samples (records with facts; seed = the date)

