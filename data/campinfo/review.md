# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-28. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 100 | 40 | 0 | 17 | 35 | 0 | 0 | 0 | 8 | 20 | 51 | 80 |

## Needs a secret / not built yet

- Cell coverage (one status per area; cell = null on every record until the point lookup exists): US-KY FCC as of 2025-12-31: 0 mobile coverage files for the state (point lookup = step 2, not built)

## Hosts that need a browser (403), say no in robots.txt, or are resting

- www.recreation.gov: 35 campgrounds · robots.txt says no

## Needs a browser pass (the page opened but its text holds no campground facts: filled by script, most likely)

- parks.ky.gov: 17 campgrounds

## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)

- 2026-10-28: 67 hand-checked campgrounds · fields agree 96 · DIFFER 9 · bot blank 204

**GATE=PASS** · FACTS vs hand key: 88/93 right = 95% (need 80%, at least 10 filled; sites 19/20, electric 26/28, water 15/16, sewer 7/8, dump_station 4/4, showers 17/17) · 0 fee/site values from the wrong page or sentence (need 0) · known answers 16 right of 16 read, 0 waiting on the secret, 0 warn · all-field agreement 96/105 = 91% ('some' = agree; KEY_WRONG left out)

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
- Carr Creek Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 39); electric bot blank (key: False); water bot blank (key: True)
- Carter Caves Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 128); amps bot blank (key: [20, 30, 50]); electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 286-4411)
- Columbus-Belmont Campground (ok, no campground facts even in a browser): sites bot blank (key: 35); amps bot blank (key: [50]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Ridgeline & Clifty Campgrounds (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 50); amps bot blank (key: [20, 30]); electric bot blank (key: False); water bot blank (key: True); phone bot blank (key: (800) 325-0063)
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
- Greenbo Lake Campground (ok (browser)): sites bot blank (key: 102); amps bot blank (key: [30]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Jenny Wiley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 118); electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 889-1790)
- John James Audubon Campground (ok (browser)): sites bot blank (key: 83); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True)
- Kenlake Campground (ok (browser)): sites bot blank (key: 63); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); phone bot blank (key: (270) 474-2211)
- Kentucky Dam Village Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 69); electric bot blank (key: True); water bot blank (key: True)
- Kincaid Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 159); electric bot blank (key: True)
- Lake Barkley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 79); amps bot blank (key: [30]); electric bot blank (key: True); water bot blank (key: True)
- Lake Cumberland Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 87); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); phone bot blank (key: (270) 343-3111)
- Lake Malone Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 25); amps bot blank (key: [30]); electric bot blank (key: True); water bot blank (key: True)
- Hillman Ferry Campground (ok): sites agree (368); amps agree ([30, 50]); electric agree (True); water agree (True); sewer agree (True); showers agree (True); phone bot blank (key: (270) 924-2181)
- Energy Lake Campground (ok): sites DIFFER bot 13 vs key 35; amps DIFFER bot [30, 50] vs key [50]; electric agree (True); phone bot blank (key: (270) 924-2270)
- Wranglers Campground (ok): sites agree (198); amps agree ([30, 50]); electric agree (True) [bot: some]; water agree (True); sewer agree (True); showers agree (True); phone bot blank (key: (270) 924-2200)
- Piney Campground (TN) (ok): sites agree (384); electric agree (True); water agree (True); sewer agree (True); phone bot blank (key: (931) 232-5331)
- Fenton Self-Service Campground (ok): amps agree ([30]); electric agree (True)
- Self-service lakeside campgrounds (10) (ok): electric DIFFER bot True vs key False; water bot blank (key: False); sewer bot blank (key: False)
- Mammoth Cave Campground (ok, no campground facts even in a browser): sites bot blank (key: 111); electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 758-2424)
- Maple Springs Group Campground (ok (browser)): sites bot blank (key: 7); electric agree (True); sewer bot blank (key: False); dump_station bot blank (key: True); phone DIFFER bot (270) 758-2166 vs key (270) 758-2180
- Houchin Ferry Campground (ok (browser)): sites bot blank (key: 12); electric agree (True); water bot blank (key: True); phone bot blank (key: (270) 758-2180)
- My Old Kentucky Home Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 49); amps bot blank (key: [50]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); phone bot blank (key: (502) 348-3502)
- Whittleton & Middle Fork Campgrounds (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 86); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True); phone bot blank (key: (606) 663-2214)
- Nolin Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 65); electric bot blank (key: False); showers bot blank (key: True)
- Otter Creek ORA Campground (ok, no campground facts even in a browser): electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 750-4257)
- Paintsville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 42); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Pennyrile Forest Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 63); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Taylorsville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 75); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Twin Knobs Campground (ok): sites agree (200); electric agree (True) [bot: some]; water agree (True) [bot: some]; sewer agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 780-7818)
- Yatesville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 47); electric bot blank (key: True); water bot blank (key: True)
- Yellowbank WMA primitive campground (Main Area) (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False); phone agree ((270) 547-6856)
- Zilpo Campground (ok): electric agree (True) [bot: some]; sewer bot blank (key: False); showers agree (True); phone bot blank (key: (606) 768-2722)
- Kentucky Horse Park Campground (ok (browser)): sites agree (257) [bot: 260]; amps agree ([20, 30, 50]); electric agree (True) [bot: some]; water agree (True); dump_station agree (True); showers agree (True); phone agree ((859) 259-4257)
- Levi Jackson Campground (ok): sites agree (146); amps bot blank (key: [30, 50]); electric agree (True); water agree (True); sewer bot blank (key: True); dump_station agree (True); showers agree (True); phone bot blank (key: (606) 330-2130)
- Breaks Interstate Park Campground (ok): sites agree (138); electric agree (True) [bot: some]; water agree (True); sewer agree (True); phone bot blank (key: (276) 865-4413)
- Kingdom Come primitive campsites (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- Higginson-Henry WMA designated campsites (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- West Kentucky WMA designated camping site (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)
- Rolling Fork WMA designated camping area (ok, no campground facts even in a browser): electric bot blank (key: False); water bot blank (key: False); sewer bot blank (key: False)

## US-KY: 12 random samples (records with facts; seed = the date)

- **Maple Springs Group Campground** (maple-springs-group-campground, KY (hand-checked list), status ok (browser), 16 facts) · [home.nps.gov](https://home.nps.gov/maca/planyourvisit/maplespringscg.htm)
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
- **West Kentucky WMA designated camping site** (west-kentucky-wma-designated-camping-site, KY (hand-checked list), status ok, no campground facts even in a browser, 3 facts) · [app.fw.ky.gov](https://app.fw.ky.gov/public_lands_search/detail.aspx?Kdfwr_id=137)
  - map.date_how = "PDF, no date in the link" · “link “View Detailed Map””
  - map.url = "https://fw.ky.gov/More/Documents/West_Kentucky_WMA.pdf" · “link “View Detailed Map” -> https://fw.ky.gov/More/Documents/West_Kentucky_WMA.pdf”
  - phone = "(270) 488-3233" · “WMA Overview Size: 4495 acres Location: McCracken Contact: (270) 488-3233 Elevation: minimum 297 feet, maximum 451 feet. Entrance GPS”
- **Breaks Interstate Park Campground** (breaks-interstate-park-campground, KY (hand-checked list), status ok, 16 facts) · [www.breakspark.com](https://www.breakspark.com/campground)
  - booking.how = "online: app.fireflyreservations.com" · “link “Book Your Campsite Here””
  - booking.url = "https://app.fireflyreservations.com/reserve/property/Breaks · “link “Book Your Campsite Here” -> https://app.fireflyreservations.com/reserve/property/BreaksInterstatePark”
  - checkin = "4:00 pm" · “eing you! KNOW BEFORE YOU GO: INFORMATION FOR FIRST TIME CAMPERS View Campground Map here Check-in: 4:00 pm Check-out: 1:00 pm Our 138 camp ”
  - checkout = "1:00 pm" · “ORE YOU GO: INFORMATION FOR FIRST TIME CAMPERS View Campground Map here Check-in: 4:00 pm Check-out: 1:00 pm Our 138 camp sites range from a”
  - hookups.electric = "some" · “ck-out: 1:00 pm Our 138 camp sites range from a great place to pitch your tent to full RV hook-ups. Most of these sites are wooded, but if y”
  - hookups.sewer = true · “0 plus tax Electric and Water Sites Nightly: $37.00 plus tax Electric Service, Water, and Sewer sites Nightly: $41.00 plus tax Group Camp Si”
  - hookups.water = true · “ink at the top of this page. Campsites and Rates Primitive Sites Nightly: $27.00 plus tax Electric and Water Sites Nightly: $37.00 plus tax ”
  - map.date_how = "web page, no date in the link" · “link “View Campground Map here””
  - map.url = "https://www.breakspark.com/s/BreaksCampground-Map-Optimized · “link “View Campground Map here” -> https://www.breakspark.com/s/BreaksCampground-Map-Optimized.jpg”
  - phone_hint = "(276) 865-4413" · “the front of the campground store. If you have questions regarding check-in, please call (276) 865-4413. Cancellation Policy Campground rese”
- **Twin Knobs Campground** (twin-knobs-campground, KY (hand-checked list), status ok, 17 facts, 789 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/twin-knobs-campground)
  - booking.how = "online: www.recreation.gov" · “link “Make Reservations Here””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/233782" · “link “Make Reservations Here” -> https://www.recreation.gov/camping/campgrounds/233782”
  - checkin = "2 p.m" · “your visit. Seasons of Use 2nd Friday in March - 1st Sunday in November Operational Hours Check-in: 2 p.m. Checkout: 11:00 a.m. Only registe”
  - checkout = "11:00 a.m" · “ns of Use 2nd Friday in March - 1st Sunday in November Operational Hours Check-in: 2 p.m. Checkout: 11:00 a.m. Only registered campers are a”
  - drinking_water = true · “available at this site. Facility and Amenity Information Restrooms Flush toilet(s) Water Potable water is available at this site. Drinking w”
  - dump_station = "some" · “a picnic table and campfire ring. RV sites range from electric-only to full hookups and a dump station is available. Bathhouses with showers”
  - features = "campfire ring" · “offers 200 campsites developed for tent and RV camping. Each site has a picnic table and campfire ring. RV sites range from electric-only to”
  - hookups.electric = "some" · “tent and RV camping. Each site has a picnic table and campfire ring. RV sites range from electric-only to full hookups and a dump station is”
  - hookups.sewer = "some" · “ing. Each site has a picnic table and campfire ring. RV sites range from electric-only to full hookups and a dump station is available. Bath”
  - hookups.water = "some" · “ing. Each site has a picnic table and campfire ring. RV sites range from electric-only to full hookups and a dump station is available. Bath”
- **Holly Bay Campground** (holly-bay-campground, KY (hand-checked list), status ok, 13 facts, 1092 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/holly-bay-campground)
  - booking.how = "online: www.recreation.gov" · “link “Make Reservations Here””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232259" · “link “Make Reservations Here” -> https://www.recreation.gov/camping/campgrounds/232259”
  - drinking_water = true · “s available at the site. Facility and Amenity Information Restrooms Flush toilet(s) Water Potable water is available at this site. Drinking ”
  - features = "fire ring, picnic table and lantern pole" · “mpsites are reservable and have electricity, water, a paved vehicle pad, gravel tent pad, fire ring, picnic table and lantern pole. The 19 w”
  - fees = "$46 per night | $92 per night | $32 per night | $63 per nig · “er 19th Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $46 per night Double Site: $92 per night Single Si”
  - hookups.electric = "some" · “it easy to wash off a day of adventure. The 75 drive-in campsites are reservable and have electricity, water, a paved vehicle pad, gravel te”
  - hookups.water = true · “it easy to wash off a day of adventure. The 75 drive-in campsites are reservable and have electricity, water, a paved vehicle pad, gravel te”
  - map.date_how = "web page, no date in the link" · “link “Holly Bay Campground Guide Map””
  - map.url = "https://usfs-public.box.com/s/53p80eudq3r20y7i4kjk8n3lb7sg9 · “link “Holly Bay Campground Guide Map” -> https://usfs-public.box.com/s/53p80eudq3r20y7i4kjk8n3lb7sg9jqn”
  - reservable = "mixed" · “ent pad, fire ring, picnic table and lantern pole. The 19 walk-in tent campsites are on a first-come, first-served basis and have access to ”
- **S-Tree Campground** (s-tree-campground, KY (hand-checked list), status ok, 6 facts, 1452 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/s-tree-campground)
  - drinking_water = false · “et accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is not available at this site. Picni”
  - features = "fire ring and lantern pole" · “unty, KY. Each of the 20 first-come, first-served campsites has a picnic table, tent pad, fire ring and lantern pole. The campground's small”
  - fees = "$15 per night | $20 per night" · “r-round Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $15 per night Double Site: $20 per night Pay at si”
  - reservable = false · “d sits on a ridge above Horse Lick Creek near McKee in Jackson County, KY. Each of the 20 first-come, first-served campsites has a picnic ta”
  - season = "year-round" · “isitor Use Monitoring, Oct 2026-Sept 2027 Reservations General Information Seasons of Use Open year-round Operational Hours Open 24 hours/da”
  - sites.total = 20 · “ound sits on a ridge above Horse Lick Creek near McKee in Jackson County, KY. Each of the 20 first-come, first-served campsites has a picnic”
- **Station Camp Campground (TN)** (station-camp-campground-tn, KY (hand-checked list), status ok (browser), 14 facts) · [home.nps.gov](https://home.nps.gov/biso/planyourvisit/station-camp-campground.htm)
  - booking.how = "online: www.recreation.gov" · “link “Start Your Reservation””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/10004358" · “link “Start Your Reservation” -> https://www.recreation.gov/camping/campgrounds/10004358”
  - checkin = "12:00 pm" · “ing 1-877-444-6777 or on the Recreation.Gov web site. Important Information Check-out and check-in time is 12:00 pm (ET) for all campsites i”
  - checkout = "12:00 pm" · “NRRA with the exception of Bandy Creek Group Camp where check-in time is 2:00 pm (ET) and check-out time is 12:00 pm (ET). . Campground Regu”
  - dump_station = true · “ers water and electricity, tables, grills, access to modern restrooms with hot showers, a dump station and access to miles of horse trails. ”
  - hookups.electric = true · “ns 24 campsites for equestrian and non-equestrian campers. Each campsite offers water and electricity, tables, grills, access to modern rest”
  - hookups.water = true · “und contains 24 campsites for equestrian and non-equestrian campers. Each campsite offers water and electricity, tables, grills, access to m”
  - map.date_how = "PDF, year 2024 in the link" · “link “Download your map here.””
  - map.url = "https://home.nps.gov/biso/planyourvisit/upload/Station-Camp · “link “Download your map here.” -> https://home.nps.gov/biso/planyourvisit/upload/Station-Camp-Campground-Map-and-Regs-2024.pdf”
  - reservable = true · “or Passes). Station Camp Campground is now operated by the National Park Service. Camping reservations can be made by calling 1-877-444-6777”
- **Barren River Lake State Resort Park Campground** (barren-river-lake-state-resort-park-campground, KY (hand-checked list), status ok (browser), 8 facts, 731 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/barren-river-lake-campground-7834)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/barre · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ll you to sleep in the campground. Utility hookups are available. For your convenience, a dump station and two central service buildings wit”
  - hookups.electric = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - hookups.water = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - rules.pets = "Pets are allowed if restrained" · “a dump station and two central service buildings with showers and rest rooms are offered. Pets are allowed if restrained. Laundry facilities”
  - showers = true · “re available. For your convenience, a dump station and two central service buildings with showers and rest rooms are offered. Pets are allow”
- **Kentucky Horse Park Campground** (kentucky-horse-park-campground, KY (hand-checked list), status ok (browser), 20 facts, 860 ft) · [kyhorsepark.com](https://kyhorsepark.com/campground/)
  - booking.how = "online: www.reserveamerica.com" · “link “Make a Reservation””
  - booking.url = "https://www.reserveamerica.com/explore/kentucky-horse-park/ · “link “Make a Reservation” -> https://www.reserveamerica.com/explore/kentucky-horse-park/KY/90800/overview”
  - checkin = "2 pm" · “SE PARK 4089 Iron Works Pike Lexington, Kentucky, 40511 Get Directions Ready to Check In? Check-in is after 2 pm. Check-out is before/by noo”
  - checkout = "12:00 noon" · “imum stay is 14 days unless approved by Campground management. Check in time is 2:00 p.m. Check out time is 12:00 noon. All guests are requi”
  - drinking_water = true · “yards away (groups of 25 or more are responsible for renting portable toilets). In-ground water hydrant available (renters must supply their”
  - dump_station = true · “water, our campground sites are 55’ paved back-ins with fire rings and picnic tables. Two dump stations are provided for your convenience as”
  - features = "fire rings and picnic tables" · “with 50/30/20 amp electricity and water, our campground sites are 55’ paved back-ins with fire rings and picnic tables. Two dump stations ar”
  - hookups.amps = [20, 30, 50] · “Countless Welcome to the Kentucky Horse Park Campground! Offering 260 spacious sites with 50/30/20 amp electricity and water, our campground”
  - hookups.electric = "some" · “come to the Kentucky Horse Park Campground! Offering 260 spacious sites with 50/30/20 amp electricity and water, our campground sites are 55”
  - hookups.sewer = "some" · “he campground store. The campground remains available to campers after hours. Do you have sewer at your sites? We do not have sewer hookups ”
- **Energy Lake Campground** (energy-lake-campground, KY (hand-checked list), status ok, 14 facts) · [www.landbetweenthelakes.us](https://www.landbetweenthelakes.us/visit/energy-lake-campground/)
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
- **Wilderness Road Campground** (wilderness-road-campground, KY (hand-checked list), status ok, 9 facts) · [www.nps.gov](https://www.nps.gov/cuga/planyourvisit/wilderness-road-campground.htm)
  - booking.url = "https://www.recreation.gov/camping/campgrounds/258617" · “booking link from our kpc-campgrounds.json row (official system www.recreation.gov)”
  - dump_station = true · “ccommodates different lengths. No full hookups (no sewer or water at individual sites). A dump station available near the campground entranc”
  - features = "fire ring, access to restrooms with flush toilets and showe · “a wooded area (no RV’s or camper trailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets a”
  - hookups.electric = "some" · “ayout & Features Loops A,D,E,and F: Non-electric sites set in a wooded area. Loops B & C: Electric sites available with asphalt pad set in a”
  - hookups.sewer = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - hookups.water = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - reservable = true · “r families, scout troops, and other large groups. Maximum Group Size: 25 people per site. Reservations Required: Can be booked up to 12 mont”
  - restrooms = "flush" · “ailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets and showers. RV Camping Each campsit”
  - showers = true · “All sites include: A picnic table, fire ring, access to restrooms with flush toilets and showers. RV Camping Each campsite accommodates diff”
