# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-31. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 100 | 51 | 35 | 3 | 0 | 0 | 0 | 0 | 11 | 22 | 51 | 96 |
| US-TN | 348 | 0 | 81 | 0 | 0 | 0 | 267 | 0 | 0 | 0 | 0 | 348 |
| US-IA | 125 | 0 | 32 | 0 | 0 | 0 | 93 | 0 | 0 | 0 | 0 | 0 |
| US-MA | 30 | 20 | 8 | 0 | 0 | 0 | 0 | 0 | 2 | 18 | 22 | 0 |
| US-CO | 605 | 102 | 339 | 0 | 0 | 164 | 0 | 0 | 0 | 0 | 266 | 1 |
| US-MT | 312 | 0 | 312 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Needs a secret / not built yet

- RIDB_API_KEY is not set in KPC-Data: every federal (Recreation.gov) row has status "needs RIDB_API_KEY secret in KPC-Data". Free key: ridb.recreation.gov, Profile. Add it under Settings -> Secrets and variables -> Actions.
- Cell coverage (one status per area; cell = null on every record until the point lookup exists): US-CO FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-IA FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-KY FCC as of 2025-12-31: 0 mobile coverage files for the state (point lookup = step 2, not built); US-MA FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-TN FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built); US-MT FCC as of 2026-06-30: 0 mobile coverage files for the state (point lookup = step 2, not built)

## Hosts that need a browser (403), say no in robots.txt, or are resting

- cpw.state.co.us: 164 campgrounds · host resting

## Needs a browser pass (the page opened but its text holds no campground facts: filled by script, most likely)

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

