# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-30. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 100 | 51 | 35 | 3 | 0 | 0 | 0 | 0 | 11 | 22 | 51 | 96 |

## Needs a secret / not built yet

- RIDB_API_KEY is not set in KPC-Data: every federal (Recreation.gov) row has status "needs RIDB_API_KEY secret in KPC-Data". Free key: ridb.recreation.gov, Profile. Add it under Settings -> Secrets and variables -> Actions.
- Cell coverage (one status per area; cell = null on every record until the point lookup exists): US-KY FCC as of 2025-12-31: 0 mobile coverage files for the state (point lookup = step 2, not built)

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

- Barren River Lake State Resort Park Campground (ok (browser)): sites bot blank (key: 101); amps bot blank (key: [30, 50]); electric DIFFER bot True vs key False; water DIFFER bot True vs key False; sewer bot blank (key: False); dump_station agree (True); showers agree (True)
- Big Bone Lick Campground (ok (browser)): sites agree (62); amps bot blank (key: [30]); electric agree (True); water agree (True); dump_station bot blank (key: True); showers agree (True)
- Blue Heron Campground (KY) (ok (browser)): sites agree (45); electric agree (True); showers agree (True); phone bot blank (key: (423) 286-7275)
- Bear Creek Horse Camp (KY) (ok (browser)): sites agree (22) [bot: 23]; electric agree (True); showers agree (True); phone bot blank (key: (423) 286-7275)
- Alum Ford Campground (KY) (ok (browser)): sites bot blank (key: 6); electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); phone bot blank (key: (423) 569-9778)
- Bandy Creek Campground (TN) (ok): electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (423) 286-7275)
- Station Camp Campground (TN) (ok (browser)): sites agree (24); electric agree (True); showers agree (True); phone bot blank (key: (423) 286-7275)
- Blue Licks Battlefield Campground (ok, no campground facts even in a browser): sites bot blank (key: 55); electric bot blank (key: True); water bot blank (key: False); dump_station bot blank (key: True); showers bot blank (key: True); phone DIFFER bot (859) 289-5507 vs key (859) 289-3653
- Carr Creek Campground (ok (browser)): sites bot blank (key: 39); electric DIFFER bot True vs key False; water agree (True)
- Carter Caves Campground (ok (browser)): sites bot blank (key: 128); amps bot blank (key: [20, 30, 50]); electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers agree (True); phone bot blank (key: (606) 286-4411)
- Columbus-Belmont Campground (ok, no campground facts even in a browser): sites bot blank (key: 35); amps bot blank (key: [50]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Ridgeline & Clifty Campgrounds (ok, no campground facts even in a browser): sites bot blank (key: 50); amps bot blank (key: [20, 30]); electric bot blank (key: False); water bot blank (key: True); phone bot blank (key: (800) 325-0063)
- Wilderness Road Campground (ok): sites bot blank (key: 151); amps bot blank (key: [20, 30, 50]); electric agree (True) [bot: some]; water agree (False); sewer DIFFER bot False vs key True; dump_station agree (True); showers agree (True); phone bot blank (key: (606) 248-2817)
- Dale Hollow Lake Campground (ok (browser)): sites bot blank (key: 151); amps bot blank (key: [50]); electric agree (True); water bot blank (key: True); sewer bot blank (key: True)
- Twin Knobs Campground (ok): sites agree (200); electric agree (True) [bot: some]; water agree (True) [bot: some]; sewer agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 780-7818)
- Zilpo Campground (ok): electric agree (True) [bot: some]; sewer bot blank (key: False); showers agree (True); phone bot blank (key: (606) 768-2722)
- Clear Creek Campground (ok): sites bot blank (key: 20); electric KEY WRONG (bot False, key False): left out; water bot blank (key: True); phone bot blank (key: (606) 784-6428)
- White Sulphur Horse Camp (ok): electric KEY WRONG (bot False, key False): left out; water bot blank (key: True); phone bot blank (key: (606) 784-6428)
- Koomer Ridge Campground (ok): sites agree (54); electric KEY WRONG (bot False, key False): left out; water bot blank (key: False); sewer bot blank (key: False); showers agree (True); phone bot blank (key: (606) 784-6428)
- Holly Bay Campground (ok): sites bot blank (key: 94); electric agree (True) [bot: some]; water agree (True); showers agree (True); phone bot blank (key: (606) 864-4163)
- Grove Drive-In Campground (ok): sites bot blank (key: 44); electric agree (True) [bot: some]; water agree (True); phone bot blank (key: (606) 864-4163)
- Bee Rock Campground (ok (browser)): sites bot blank (key: 25); electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); phone bot blank (key: (606) 864-4163)
- Great Meadows Campground (ok): sites agree (18); electric KEY WRONG (bot False, key False): left out; water bot blank (key: False); sewer bot blank (key: False); phone bot blank (key: (606) 376-5323)
- Barren Fork Horse Camp (ok): sites agree (41); electric bot blank (key: True); water bot blank (key: True); phone bot blank (key: (606) 376-5323)
- Turkey Foot Campground (ok): sites bot blank (key: 15); electric KEY WRONG (bot False, key False): left out; water bot blank (key: False); phone bot blank (key: (606) 864-4163)
- S-Tree Campground (ok): sites agree (20); water bot blank (key: True); phone bot blank (key: (606) 864-4163)
- Fort Boonesborough Campground (ok (browser)): sites agree (163) [bot: 166]; electric agree (True); water agree (True); sewer agree (True); phone agree ((859) 527-3454)
- General Burnside Island Campground (ok (browser)): sites agree (101) [bot: 102]; electric agree (True); water agree (True); sewer bot blank (key: True); phone agree ((606) 561-3625)
- General Butler Campground (ok (browser)): sites bot blank (key: 104); electric bot blank (key: True); water bot blank (key: True)
- Grayson Lake Campground (ok (browser)): sites agree (69) [bot: 71]; amps bot blank (key: [50]); electric agree (True); water agree (True); phone DIFFER bot (606) 474-4513 vs key (606) 474-6856
- Green River Lake Campground (ok (browser)): sites bot blank (key: 227); electric bot blank (key: True); water bot blank (key: True); phone bot blank (key: (270) 465-8255)
- Greenbo Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 102); amps bot blank (key: [30]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Jenny Wiley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 118); electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 889-1790)
- John James Audubon Campground (ok (browser)): sites bot blank (key: 83); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True)
- Kenlake Campground (ok (browser)): sites bot blank (key: 63); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); phone bot blank (key: (270) 474-2211)
- Kentucky Dam Village Campground (ok, no campground facts even in a browser): sites bot blank (key: 69); electric bot blank (key: True); water bot blank (key: True)
- Kincaid Lake Campground (ok (browser)): sites DIFFER bot 84 vs key 159; electric agree (True)
- Lake Barkley Campground (ok (browser)): sites bot blank (key: 79); amps bot blank (key: [30]); electric agree (True); water agree (True)
- Lake Cumberland Campground (ok (browser)): sites bot blank (key: 87); electric agree (True); water agree (True); sewer bot blank (key: True); phone bot blank (key: (270) 343-3111)
- Lake Malone Campground (ok (browser)): sites bot blank (key: 25); amps bot blank (key: [30]); electric agree (True); water agree (True)
- Hillman Ferry Campground (ok): sites agree (368); amps agree ([30, 50]); electric agree (True); water agree (True); sewer agree (True); showers agree (True); phone bot blank (key: (270) 924-2181)
- Energy Lake Campground (ok): sites DIFFER bot 13 vs key 35; amps DIFFER bot [30, 50] vs key [50]; electric agree (True); phone bot blank (key: (270) 924-2270)
- Wranglers Campground (ok): sites agree (198); amps agree ([30, 50]); electric agree (True) [bot: some]; water agree (True); sewer agree (True); showers agree (True); phone bot blank (key: (270) 924-2200)
- Piney Campground (TN) (ok): sites agree (384); electric agree (True); water agree (True); sewer agree (True); phone bot blank (key: (931) 232-5331)
- Fenton Self-Service Campground (ok): amps agree ([30]); electric agree (True)
- Self-service lakeside campgrounds (10) (ok): electric DIFFER bot True vs key False; water bot blank (key: False); sewer bot blank (key: False)
- Mammoth Cave Campground (ok, no campground facts even in a browser): sites bot blank (key: 111); electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 758-2424)
- Maple Springs Group Campground (ok (browser)): sites bot blank (key: 7); electric agree (True); sewer bot blank (key: False); dump_station bot blank (key: True); phone DIFFER bot (270) 758-2166 vs key (270) 758-2180
- Houchin Ferry Campground (ok (browser)): sites bot blank (key: 12); electric agree (True); water bot blank (key: True); phone bot blank (key: (270) 758-2180)
- My Old Kentucky Home Campground (ok (browser)): sites bot blank (key: 49); amps bot blank (key: [50]); electric agree (True); water agree (True); sewer bot blank (key: True); phone bot blank (key: (502) 348-3502)
- Whittleton & Middle Fork Campgrounds (ok (browser)): sites bot blank (key: 86); amps bot blank (key: [20]); electric agree (True); water bot blank (key: True); phone bot blank (key: (606) 663-2214)
- Nolin Lake Campground (ok (browser)): sites bot blank (key: 65); electric DIFFER bot True vs key False; showers agree (True)
- Otter Creek ORA Campground (ok, no campground facts even in a browser): electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 750-4257)
- Paintsville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 42); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Pennyrile Forest Campground (ok, no campground facts even in a browser): sites bot blank (key: 63); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Taylorsville Lake Campground (ok (browser)): sites bot blank (key: 75); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); dump_station bot blank (key: True); showers agree (True)
- Twin Knobs Campground (ok): sites agree (200); electric agree (True) [bot: some]; water agree (True) [bot: some]; sewer agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 780-7818)
- Yatesville Lake Campground (ok (browser)): sites agree (47); electric bot blank (key: True); water bot blank (key: True)
- Yellowbank WMA primitive campground (Main Area) (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); phone agree ((270) 547-6856)
- Zilpo Campground (ok): electric agree (True) [bot: some]; sewer bot blank (key: False); showers agree (True); phone bot blank (key: (606) 768-2722)
- Kentucky Horse Park Campground (ok (browser)): sites agree (257) [bot: 260]; amps agree ([20, 30, 50]); electric agree (True) [bot: some]; water agree (True); dump_station agree (True); showers agree (True); phone agree ((859) 259-4257)
- Levi Jackson Campground (ok): sites agree (146); amps bot blank (key: [30, 50]); electric agree (True); water agree (True); sewer bot blank (key: True); dump_station agree (True); showers agree (True); phone bot blank (key: (606) 330-2130)
- Breaks Interstate Park Campground (ok): sites agree (138); electric agree (True) [bot: some]; water agree (True); sewer agree (True); phone bot blank (key: (276) 865-4413)
- Kingdom Come primitive campsites (ok (browser)): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- Higginson-Henry WMA designated campsites (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- West Kentucky WMA designated camping site (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- Rolling Fork WMA designated camping area (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)

## US-KY: 12 random samples (records with facts; seed = the date)

- **Big Bone Lick Campground** (big-bone-lick-campground, KY (hand-checked list), status ok (browser), 15 facts, 647 ft) · [parks.ky.gov](https://parks.ky.gov/union/parks/historic/big-bone-lick-state-historic-site)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/big-b · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - checkin = "2 p.m" · “grocery store on-site for your convenience, which is open mid-March through mid-November. Check-in time begins at 2 p.m., and check-out time”
  - checkout = "1 p.m" · “nience, which is open mid-March through mid-November. Check-in time begins at 2 p.m., and check-out time is at 1 p.m. Gift Shop The park's g”
  - hookups.electric = true · “n the park for year-round birding. Camping Spacious campground features 62 campsites with utility hookups, grills, a swimming pool, and play”
  - hookups.water = true · “n the park for year-round birding. Camping Spacious campground features 62 campsites with utility hookups, grills, a swimming pool, and play”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-map8929d877-a36c-45”
  - phone_hint = "(859) 384-3522" · “o Do Events Golf Gatherings Park Finder Book Now ‹ Back Big Bone Lick State Historic Site 859-384-3522 greta.gay@ky.gov 3380 Beaver Road, Un”
- **Grayson Lake Campground** (grayson-lake-campground, KY (hand-checked list), status ok (browser), 14 facts, 739 ft) · [parks.ky.gov](https://parks.ky.gov/explore/grayson-lake-state-park-7813)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/grays · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ng Pick your spot under the stars in the spacious, 71-site campground. Utility hookups, a dump station, and two central service buildings wi”
  - hookups.electric = true · “606-474-4513 Camping Pick your spot under the stars in the spacious, 71-site campground. Utility hookups, a dump station, and two central se”
  - hookups.water = true · “606-474-4513 Camping Pick your spot under the stars in the spacious, 71-site campground. Utility hookups, a dump station, and two central se”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Campground Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Campground Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/campground-mapd052fb15-5”
  - phone = "(606) 474-4513" · “open year-round; fee for boat rentals. Marina phone number: 606-474-4513 Camping Pick your spot under the stars in the spacious, 71-”
  - reservable = true · “606-474-9727 steven.kennedy@ky.gov 314 Grayson Lake State Park Rd., Olive Hill, KY 41164 Reserve A Campsite View All Photos Sheer sandstone ”
- **Whittleton & Middle Fork Campgrounds** (whittleton-middle-fork-campgrounds, KY (hand-checked list), status ok (browser), 7 facts, 775 ft) · [parks.ky.gov](https://parks.ky.gov/explore/whittleton-campground-8107)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/natur · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ide sites with utilities at Natural Bridge State Park. Tent campsites are also available. Dump stations and two central service buildings wi”
  - hookups.electric = true · “te. Two campgrounds, Whittleton Campground and Middle Fork Campground, provide sites with utilities at Natural Bridge State Park. Tent camps”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - restrooms = "yes (kind not stated)" · “. Tent campsites are also available. Dump stations and two central service buildings with restrooms and showers are furnished for your conve”
  - showers = true · “es are also available. Dump stations and two central service buildings with restrooms and showers are furnished for your convenience.Â Reser”
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
- **Barren River Lake State Resort Park Campground** (barren-river-lake-state-resort-park-campground, KY (hand-checked list), status ok (browser), 8 facts, 731 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/barren-river-lake-campground-7834)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/barre · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ll you to sleep in the campground. Utility hookups are available. For your convenience, a dump station and two central service buildings wit”
  - hookups.electric = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - hookups.water = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - rules.pets = "Pets are allowed if restrained" · “a dump station and two central service buildings with showers and rest rooms are offered. Pets are allowed if restrained. Laundry facilities”
  - showers = true · “re available. For your convenience, a dump station and two central service buildings with showers and rest rooms are offered. Pets are allow”
- **General Burnside Island Campground** (general-burnside-island-campground, KY (hand-checked list), status ok (browser), 15 facts, 837 ft) · [parks.ky.gov](https://parks.ky.gov/burnside/parks/recreation/general-burnside-island-state-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/gener · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “tes with utility hookups, two central service buildings with showers and restrooms, and a dump station. The campground is open mid-March to ”
  - hookups.electric = true · “s make camping at General Burnside a great getaway. The campground features 94 sites with utility hookups, two central service buildings wit”
  - hookups.water = true · “s make camping at General Burnside a great getaway. The campground features 94 sites with utility hookups, two central service buildings wit”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Campground Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Campground Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/campground-map1332fc6b-2”
  - phone = "(606) 561-3625" · “ion. The campground is open mid-March to mid-November. Call 606-561-3625 for more information. Golf An 18-hole regulation golf cours”
  - phone_hint = "(606) 561-3625" · “and restrooms, and a dump station. The campground is open mid-March to mid-November. Call 606-561-3625 for more information. Golf An 18-hole”
- **Higginson-Henry WMA designated campsites** (higginson-henry-wma-designated-campsites, KY (hand-checked list), status ok, no campground facts even in a browser, 3 facts, 457 ft) · [app.fw.ky.gov](https://app.fw.ky.gov/public_lands_search/detail.aspx?Kdfwr_id=132)
  - map.date_how = "PDF, no date in the link" · “link “View Detailed Map””
  - map.url = "https://fw.ky.gov/More/Documents/Higginson-HenryWMA_ALL.pdf · “link “View Detailed Map” -> https://fw.ky.gov/More/Documents/Higginson-HenryWMA_ALL.pdf”
  - phone = "(270) 389-3580" · “A Overview Size: 5446 acres Location: Union Contact: Office (270) 389-3580 Elevation: minimum 396 feet, maximum 675 feet. Entrance GPS”
- **Wilderness Road Campground** (wilderness-road-campground, KY (hand-checked list), status ok, 9 facts, 1376 ft) · [www.nps.gov](https://www.nps.gov/cuga/planyourvisit/wilderness-road-campground.htm)
  - booking.url = "https://www.recreation.gov/camping/campgrounds/258617" · “booking link from our kpc-campgrounds.json row (official system www.recreation.gov)”
  - dump_station = true · “ccommodates different lengths. No full hookups (no sewer or water at individual sites). A dump station available near the campground entranc”
  - features = "fire ring, access to restrooms with flush toilets and showe · “a wooded area (no RV’s or camper trailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets a”
  - hookups.electric = "some" · “ayout & Features Loops A,D,E,and F: Non-electric sites set in a wooded area. Loops B & C: Electric sites available with asphalt pad set in a”
  - hookups.sewer = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - hookups.water = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - reservable = true · “r families, scout troops, and other large groups. Maximum Group Size: 25 people per site. Reservations Required: Can be booked up to 12 mont”
  - restrooms = "flush" · “ailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets and showers. RV Camping Each campsit”
  - showers = true · “All sites include: A picnic table, fire ring, access to restrooms with flush toilets and showers. RV Camping Each campsite accommodates diff”
- **Barren Fork Horse Camp** (barren-fork-horse-camp, KY (hand-checked list), status ok, 7 facts, 1294 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/barren-fork-horse-camp)
  - drinking_water = true · “ts accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is available at this site. Drinking ”
  - fees = "$15 per night" · “er 15th Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $15 per night Pay at site using fee envelope with ”
  - map.date_how = "web page, no date in the link" · “link “View Guide/Map””
  - map.url = "https://usfs-public.box.com/s/jp0e6xw1cv8jjryh53x3k3ixmkyhw · “link “View Guide/Map” -> https://usfs-public.box.com/s/jp0e6xw1cv8jjryh53x3k3ixmkyhwggg”
  - restrooms = "vault" · “rs must park in the overflow parking area. Facility and Amenity Information Accessibility Vault toilet meets accessibility standards for per”
  - rv_max_ft = 35 · “al Company. Today, the campground offers 41 campsites that accommodate horse trailers and RVs up to 35 feet. A picnic shelter at the campgro”
  - sites.total = 41 · “ng town operated by the Barren Fork Mining and Coal Company. Today, the campground offers 41 campsites that accommodate horse trailers and R”
- **Carr Creek Campground** (carr-creek-campground, KY (hand-checked list), status ok (browser), 9 facts, 1067 ft) · [parks.ky.gov](https://parks.ky.gov/explore/carr-creek-campground-7869)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/carr- · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - checkin = "2 p.m" · “. Showers, restrooms, and laundry facilities are available at a central service building. Check-in time begins 2 p.m. and check-out time is ”
  - checkout = "1 p.m" · “y facilities are available at a central service building. Check-in time begins 2 p.m. and check-out time is 1 p.m. Reservations Online Conta”
  - hookups.electric = true · “ate Park, Sassafras, KY 41759 View All Photos Spacious campground features campsites with utility hookups, grills, a beach and playground. S”
  - hookups.water = true · “ate Park, Sassafras, KY 41759 View All Photos Spacious campground features campsites with utility hookups, grills, a beach and playground. S”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - restrooms = "yes (kind not stated)" · “pground features campsites with utility hookups, grills, a beach and playground. Showers, restrooms, and laundry facilities are available at”
  - showers = true · “cious campground features campsites with utility hookups, grills, a beach and playground. Showers, restrooms, and laundry facilities are ava”
- **Yatesville Lake Campground** (yatesville-lake-campground, KY (hand-checked list), status ok (browser), 11 facts, 727 ft) · [parks.ky.gov](https://parks.ky.gov/louisa/parks/recreation/yatesville-lake-state-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/yates · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “mpground also has a playground, nature trails, a laundry room, restrooms & showers, and a dump station. The campground was named among the b”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-map10d06200-bfed-4f”
  - reservable = true · “e State Park 606-673-1492 missy.kennedy@ky.gov 2667 Pleasant Ridge Road, Louisa, KY 41230 Reserve A Campsite View All Photos Yatesville Lake”
  - restrooms = "yes (kind not stated)" · “ed lakeside camping. The campground also has a playground, nature trails, a laundry room, restrooms & showers, and a dump station. The campg”
  - season = "year-round" · “uipment. Golf packages and season passes are offered. Tee time reservations are accepted. Open year-round. For more info on this course CLIC”
  - showers = true · “camping. The campground also has a playground, nature trails, a laundry room, restrooms & showers, and a dump station. The campground was na”
- **Grove Drive-In Campground** (grove-drive-in-campground, KY (hand-checked list), status ok, 10 facts, 1198 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/grove-drive-campground)
  - booking.how = "online: www.recreation.gov" · “link “Make Reservations Here””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232258" · “link “Make Reservations Here” -> https://www.recreation.gov/camping/campgrounds/232258”
  - drinking_water = true · “lot for walk-in campers. Facility and Amenity Information Restrooms Flush toilet(s) Water Potable water is available at this site. Drinking ”
  - features = "fire ring, picnic table and lantern pole" · “r and five have water only. All drive-in sites have a paved vehicle pad, gravel tent pad, fire ring, picnic table and lantern pole. The four”
  - hookups.electric = "some" · “B is reservable, and Loop A is first come, first served. Thirty-five drive-in sites have electricity and water and five have water only. All”
  - hookups.water = true · “B is reservable, and Loop A is first come, first served. Thirty-five drive-in sites have electricity and water and five have water only. All”
  - map.date_how = "web page, no date in the link" · “link “Grove Drive-In Campground Map Guide””
  - map.url = "https://usfs-public.box.com/s/wmwd44d3zi74a1whm9cf7o30v1vmg · “link “Grove Drive-In Campground Map Guide” -> https://usfs-public.box.com/s/wmwd44d3zi74a1whm9cf7o30v1vmgnys”
  - reservable = "mixed" · “Grove Boat Ramp and Marina. Of the 40 drive-in sites, Loop B is reservable, and Loop A is first come, first served. Thirty-five drive-in sit”
  - restrooms = "yes (kind not stated)" · “ic tables are available at this site. Picnic tables are at the campsites. Other Amenities Toilets meet accessibility standards for persons w”
