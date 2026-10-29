# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-29. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 103 | 74 | 0 | 22 | 0 | 0 | 0 | 0 | 7 | 58 | 86 | 88 |

## Needs a secret / not built yet

- Cell coverage (one status per area; cell = null on every record until the point lookup exists): US-KY FCC as of 2025-12-31: 0 mobile coverage files for the state (point lookup = step 2, not built)

## Needs a browser pass (the page opened but its text holds no campground facts: filled by script, most likely)

- parks.ky.gov: 22 campgrounds

## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)

- 2026-10-29: 67 hand-checked campgrounds · fields agree 106 · DIFFER 11 · bot blank 192

**GATE=PASS** · FACTS vs hand key: 95/102 right = 93% (need 80%, at least 10 filled; sites 20/21, electric 26/29, water 17/18, sewer 9/11, dump_station 5/5, showers 18/18) · 0 fee/site values from the wrong page or sentence (need 0) · known answers 16 right of 16 read, 0 waiting on the secret, 0 warn · all-field agreement 106/117 = 91% ('some' = agree; KEY_WRONG left out)

- ok: Higginson-Henry WMA: no RV length (the page gives elevation 675 ft, not an RV length) · got None
- ok: Rolling Fork WMA: no RV length (elevation 980 ft is not an RV length) · got None
- ok: West Kentucky WMA: no RV length (elevation 451 ft is not an RV length) · got None
- ok: Yellowbank WMA: no RV length (elevation 872 ft is not an RV length) · got None
- ok: Yellowbank WMA: no camping season (Nov. 1-Dec. 31 is the rabbit / quail hunting season) · got None
- ok: Higginson-Henry WMA: no camping season (hunting season dates are not the camping season) · got None
- ok: Mammoth Cave: showers from a real sentence or null, never the 'Shower Types' menu heading · got True from “Site 82. Loop D: One restroom located near Site 108. Additional amenities; coin-operated s”
- ok: Twin Knobs: 'RV sites range from electric-only to full hookups' = sewer 'some' · got some
- ok: Bandy Creek: phone is not the (877) reservation line · got None
- ok: Bear Creek Horse Camp: phone is not the (877) reservation line · got (423) 286-7275
- ok: Blue Heron: phone is not the (877) reservation line · got (423) 286-7275
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
- Blue Heron Campground (KY) (ok): sites agree (45); electric agree (True); showers agree (True); phone agree ((423) 286-7275)
- Bear Creek Horse Camp (KY) (ok (browser)): sites agree (22) [bot: 23]; electric agree (True); showers agree (True); phone bot blank (key: (423) 286-7275)
- Alum Ford Campground (KY) (ok): sites agree (6); electric agree (False); water agree (False); sewer agree (False); phone agree ((423) 569-9778)
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
- Koomer Ridge Campground (ok): sites agree (54); electric KEY WRONG (bot False, key False): left out; water agree (False); sewer agree (False); showers agree (True); phone DIFFER bot (606) 663-8100 vs key (606) 784-6428
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
- Grayson Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 69); amps bot blank (key: [50]); electric bot blank (key: True); water bot blank (key: True); phone bot blank (key: (606) 474-6856)
- Green River Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 227); electric bot blank (key: True); water bot blank (key: True); phone bot blank (key: (270) 465-8255)
- Greenbo Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 102); amps bot blank (key: [30]); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True)
- Jenny Wiley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 118); electric bot blank (key: True); water bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 889-1790)
- John James Audubon Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 83); amps bot blank (key: [20]); electric bot blank (key: True); water bot blank (key: True)
- Kenlake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 63); electric bot blank (key: True); water bot blank (key: True); sewer bot blank (key: True); phone bot blank (key: (270) 474-2211)
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
- Mammoth Cave Campground (ok): sites agree (111); electric DIFFER bot True vs key False; water agree (False); sewer DIFFER bot True vs key False; dump_station agree (True); showers agree (True); phone agree ((270) 758-2424)
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

- **Mammoth Cave Campground** (232467, NPS, status ok, 25 facts, 580 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/232467)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232467" · “RIDB Reservable = true”
  - checkin = "1:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "11:00 AM" · “RIDB campsite attribute Checkout Time”
  - drinking_water = true · “ddy campsites, catch your drain water in buckets and empty into toilets in the restrooms. Water hydrants are for collection of water to be u”
  - dump_station = true · “itive campsites are arranged around 4 paved loops, surrounded by fragrant trees. Fill and dump stations are located in the Camp Store parkin”
  - hookups.amps = [20, 30, 50] · “RIDB campsites: 111 overnight sites (tent 10); electric at 2 (20/30/50 amp), water at 0, sewer at 2”
  - hookups.electric = true · “RIDB campsites: 111 overnight sites (tent 10); electric at 2 (20/30/50 amp), water at 0, sewer at 2”
  - hookups.sewer = true · “RIDB campsites: 111 overnight sites (tent 10); electric at 2 (20/30/50 amp), water at 0, sewer at 2”
  - hookups.water = false · “RIDB campsites: 111 overnight sites (tent 10); electric at 2 (20/30/50 amp), water at 0, sewer at 2”
- **Houchin Ferry Campground** (houchin-ferry-campground, KY (hand-checked list), status ok (browser), 15 facts) · [home.nps.gov](https://home.nps.gov/maca/planyourvisit/houchinferrycg.htm)
  - booking.how = "online: www.recreation.gov" · “link “Recreation.gov””
  - booking.url = "https://www.recreation.gov/camping/gateways/2818" · “link “Recreation.gov” -> https://www.recreation.gov/camping/gateways/2818”
  - checkin = "1 pm" · “Check-in time is after 1 pm at the Mammoth Cave, Houchin Ferry and Maple Springs Campground. If you arrive at your re”
  - drinking_water = true · “ddy campsites, catch your drain water in buckets and empty into toilets in the restrooms. Water hydrants are for collection of water to be u”
  - hookups.electric = true · “, these 12 tent-only campsites afford a quiet visit with drive-up access. TOTAL SITES: 12 Electric Hookups: 0 RV Only: 0 Tent Only: 12 Walk ”
  - map.date_how = "web page, no date in the link" · “link “Mammoth Cave Map & Guide””
  - map.url = "https://home.nps.gov/maca/planyourvisit/mammoth-cave-map-gu · “link “Mammoth Cave Map & Guide” -> https://home.nps.gov/maca/planyourvisit/mammoth-cave-map-guide.htm”
  - phone_hint = "(270) 758-2424" · “in person only on the day of your trip. Contact campground office for hours of operation. (270) 758-2424. Leave No Trace Seven Principles (U”
  - reservable = true · “TION & DIRECTIONS ADDITIONAL INFORMATION & REGULATIONS RESERVATIONS Campsites are through reservations only. IMAGE GALLERY Campsites with pi”
  - restrooms = "yes (kind not stated)" · “te unpleasant odors and muddy campsites, catch your drain water in buckets and empty into toilets in the restrooms. Water hydrants are for c”
- **Pikes Ridge** (233583, USACE, status ok, 13 facts, 709 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/233583)
  - checkin = "5:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "4:30 PM" · “RIDB campsite attribute Checkout Time”
  - fees = "$10 change fee | $20.00 fee plus the first nights use fee" · “r dates outside the original reservation date (i.e, different week or month) will incur a $10 change fee. No-Shows are charged a $20.00 fee ”
  - hookups.amps = [50] · “RIDB campsites: 60 overnight sites (rv 20); electric at 20 (50 amp), water at 20, sewer at 0”
  - hookups.electric = true · “RIDB campsites: 60 overnight sites (rv 20); electric at 20 (50 amp), water at 20, sewer at 0”
  - hookups.sewer = false · “RIDB campsites: 60 overnight sites (rv 20); electric at 20 (50 amp), water at 20, sewer at 0”
  - hookups.water = true · “RIDB campsites: 60 overnight sites (rv 20); electric at 20 (50 amp), water at 20, sewer at 0”
  - phone = "(270) 465-6488" · “RIDB FacilityPhone: 270-465-6488”
  - reservable = false · “RIDB Reservable = False”
  - rules.pets = "Pets Allowed = Yes at 60 of 60 sites" · “RIDB campsite attribute Pets Allowed”
- **Buckhorn Campground** (232566, USACE, status ok, 19 facts, 1016 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/232566)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232566" · “RIDB Reservable = true”
  - checkin = "4:30 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "4:00 PM" · “RIDB campsite attribute Checkout Time”
  - dump_station = true · “wireless internet, electric hookups, laundry facilities, hot showers, vending machines, a dump station and flush toilets. Natural Features B”
  - hookups.amps = [50] · “RIDB campsites: 35 overnight sites (tent 4, rv 28, primitive 2); electric at 29 (50 amp), water at 29, sewer at 1”
  - hookups.electric = true · “RIDB campsites: 35 overnight sites (tent 4, rv 28, primitive 2); electric at 29 (50 amp), water at 29, sewer at 1”
  - hookups.sewer = true · “RIDB campsites: 35 overnight sites (tent 4, rv 28, primitive 2); electric at 29 (50 amp), water at 29, sewer at 1”
  - hookups.water = true · “RIDB campsites: 35 overnight sites (tent 4, rv 28, primitive 2); electric at 29 (50 amp), water at 29, sewer at 1”
  - phone = "(606) 398-7220" · “RIDB FacilityPhone: 606-398-7220”
- **Waitsboro Campground** (232733, USACE, status ok, 20 facts, 735 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/232733)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232733" · “RIDB Reservable = true”
  - checkin = "3:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "12:00 PM" · “RIDB campsite attribute Checkout Time”
  - drinking_water = true · “ng them prime locations for weekend recreation. Amenities include flush toilets, showers, drinking water, laundry facilities and a dump stat”
  - dump_station = true · “ation. Amenities include flush toilets, showers, drinking water, laundry facilities and a dump station. A day-use area with a group picnic s”
  - hookups.amps = [30, 50] · “RIDB campsites: 23 overnight sites (tent 4, rv 17, group 1); electric at 20 (30/50 amp), water at 21, sewer at 0”
  - hookups.electric = true · “RIDB campsites: 23 overnight sites (tent 4, rv 17, group 1); electric at 20 (30/50 amp), water at 21, sewer at 0”
  - hookups.sewer = false · “RIDB campsites: 23 overnight sites (tent 4, rv 17, group 1); electric at 20 (30/50 amp), water at 21, sewer at 0”
  - hookups.water = true · “RIDB campsites: 23 overnight sites (tent 4, rv 17, group 1); electric at 20 (30/50 amp), water at 21, sewer at 0”
- **Smith Ridge** (233633, USACE, status ok, 19 facts, 831 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/233633)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/233633" · “RIDB Reservable = true”
  - checkin = "5:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "4:30 PM" · “RIDB campsite attribute Checkout Time”
  - drinking_water = true · “ave water and electric hookups. Amenities such as flush toilets, showers, fire rings, and drinking water provide a comfortable camping exper”
  - features = "fire rings, and drinking water provide a comfortable campin · “s, 62 of which have water and electric hookups. Amenities such as flush toilets, showers, fire rings, and drinking water provide a comfortab”
  - fees = "$10 change fee | $20.00 plus the first nights use fee" · “dates outside the original reservation date (i.e., different week or month) will incur a $10 change fee. No-Shows are charged a $20.00 plus ”
  - hookups.amps = [50] · “RIDB campsites: 80 overnight sites (rv 61); electric at 62 (50 amp), water at 66, sewer at 0”
  - hookups.electric = true · “RIDB campsites: 80 overnight sites (rv 61); electric at 62 (50 amp), water at 66, sewer at 0”
  - hookups.sewer = false · “RIDB campsites: 80 overnight sites (rv 61); electric at 62 (50 amp), water at 66, sewer at 0”
- **Dale Hollow Lake Campground** (dale-hollow-lake-campground, KY (hand-checked list), status ok (browser), 11 facts, 1034 ft) · [parks.ky.gov](https://parks.ky.gov/burkesville/parks/resort/dale-hollow-lake-state-resort-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/dale- · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - fees = "$10.00 per person | $8.00 for children 9 and under | $6/adu · “edgeable guide. You will get wet and dirty, but you'll have a great time doing it! Fee is $10.00 per person, $8.00 for children 9 and under.”
  - hookups.electric = true · “lling fairways, elevation changes, and beautiful woodland views that reward accuracy over power. The golf experience is enhanced by all the ”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Campground Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Campground Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-campground-map.pdf?”
  - phone = "(270) 433-6600" · “boating gear and apparel. Questions about the marina? Call (270) 433-6600. A gradually sloping concrete launching ramp is available.”
  - reservable = true · “te Resort Park 270-433-7431 jenny.boils@ky.gov 5970 State Park Rd., Burkesville, KY 42717 Reserve A Campsite Reserve A Lodge / Cottage View ”
  - restrooms = "yes (kind not stated)" · “cnicking Grills are located at all campsites and primitive cabins. A picnic shelter, with restrooms, is located in the picnic area and is av”
- **Blue Licks Battlefield Campground** (blue-licks-battlefield-campground, KY (hand-checked list), status ok, no campground facts even in a browser, 9 facts, 685 ft) · [parks.ky.gov](https://parks.ky.gov/carlisle/parks/historic/blue-licks-battlefield-state-resort-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/blue- · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - map.date_how = "PDF, no date in the link" · “link “Park Map””
  - map.url = "https://www.kentuckytourism.com/media/docs/default-source/l · “link “Park Map” -> https://www.kentuckytourism.com/media/docs/default-source/listing-documents/park-map9a72ac6f-42af-45”
  - phone = "(859) 289-5507" · “eation department to check on staff availability by calling (859) 289-5507, prompt #5, or by contacting the group sales office. Picnic”
  - reservable = true · “Resort Park 859-289-5507 melinda.lightner@ky.gov 10299 Maysville Rd., Carlisle, KY 40311 Reserve A Campsite Reserve A Lodge / Cottage View A”
  - restrooms = "yes (kind not stated)" · “mpt #5, or by contacting the group sales office. Picnicking Two picnic shelters (one with restrooms) are available for rental up to two year”
  - rules.pets = "pets are not allowed on any park trails that share land wit · “, jams, mustards, hot sauces, and a wide variety of sweets. Hiking Please be mindful that pets are not allowed on any park trails that share”
- **Barren River Lake State Resort Park Campground** (barren-river-lake-state-resort-park-campground, KY (hand-checked list), status ok (browser), 8 facts, 731 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/barren-river-lake-campground-7834)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/barre · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - dump_station = true · “ll you to sleep in the campground. Utility hookups are available. For your convenience, a dump station and two central service buildings wit”
  - hookups.electric = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - hookups.water = true · “eep closer to nature? Let the sounds of the outdoors lull you to sleep in the campground. Utility hookups are available. For your convenienc”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
  - rules.pets = "Pets are allowed if restrained" · “a dump station and two central service buildings with showers and rest rooms are offered. Pets are allowed if restrained. Laundry facilities”
  - showers = true · “re available. For your convenience, a dump station and two central service buildings with showers and rest rooms are offered. Pets are allow”
- **Bandy Creek Campground (TN)** (bandy-creek-campground-tn, KY (hand-checked list), status ok, 16 facts) · [home.nps.gov](https://home.nps.gov/biso/planyourvisit/bandycreekcampground.htm)
  - booking.how = "online: www.recreation.gov" · “link “Start Your Reservation””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232506" · “link “Start Your Reservation” -> https://www.recreation.gov/camping/campgrounds/232506”
  - checkin = "12:00 pm" · “es a bookstore and vending machines at this location. Important Information Check-out and check-in time is 12:00 pm (ET) for all campsites i”
  - checkout = "12:00 pm" · “NRRA with the exception of Bandy Creek Group Camp where check-in time is 2:00 pm (ET) and check-out time is 12:00 pm (ET). Note: Sites that ”
  - dump_station = true · “. All campsites include picnic tables, fire rings, and access to restrooms and showers. A dump station is located near the registration kios”
  - features = "fire rings, and access to restrooms and showers" · “with 19 sites in one loop and 16 sites in the other. All campsites include picnic tables, fire rings, and access to restrooms and showers. A”
  - hookups.amps = [50] · “check-in time is 2:00 pm (ET) and check-out time is 12:00 pm (ET). Note: Sites that have 50-amp power service are shaded in gray. Campground”
  - hookups.electric = "some" · “n. The campground offers a total of 181 campsites: 96 trailer sites which offer water and electric hook-ups, 49 sites for tent camping, and ”
  - hookups.sewer = false · “estrooms and showers. A dump station is located near the registration kiosk. There are no sewer hook-ups at individual trailer sites. The gr”
  - hookups.water = true · “f Jamestown. The campground offers a total of 181 campsites: 96 trailer sites which offer water and electric hook-ups, 49 sites for tent cam”
- **Alum Ford Campground** (10304520, NPS, status ok, 16 facts, 709 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/10304520)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/10304520" · “RIDB Reservable = true”
  - checkin = "12:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "12:00 PM" · “RIDB campsite attribute Checkout Time”
  - drinking_water = false · “of six campsites each with picnic table and fire ring. Pit toilets are available, but no drinking water. A map of the campground may be down”
  - features = "fire ring" · “e end of Highway 700. The campground consists of six campsites each with picnic table and fire ring. Recreation The campground is located ad”
  - fees = "$15 per night ($7 | $7.50 for holders of the Interagency Ag · “e, Cumberland Falls, & Pickett State Parks in Kentucky and Tennessee. The campsite fee is $15 per night ($7.50 for holders of the Interagenc”
  - hookups.electric = false · “RIDB campsites: 6 overnight sites (); electric at 0, water at 0, sewer at 0”
  - hookups.sewer = false · “RIDB campsites: 6 overnight sites (); electric at 0, water at 0, sewer at 0”
  - hookups.water = false · “RIDB campsites: 6 overnight sites (); electric at 0, water at 0, sewer at 0”
- **Craigs Creek Group Area** (232257, FS, status ok, 16 facts, 1061 ft) · [www.recreation.gov](https://www.recreation.gov/camping/campgrounds/232257)
  - booking.how = "online: Recreation.gov" · “RIDB Reservable = true”
  - booking.url = "https://www.recreation.gov/camping/campgrounds/232257" · “RIDB Reservable = true”
  - checkin = "2:00 PM" · “RIDB campsite attribute Checkin Time”
  - checkout = "11:00 AM" · “RIDB campsite attribute Checkout Time”
  - hookups.electric = false · “RIDB campsites: 3 overnight sites (tent 3, group 3); electric at 0, water at 0, sewer at 0”
  - hookups.sewer = false · “RIDB campsites: 3 overnight sites (tent 3, group 3); electric at 0, water at 0, sewer at 0”
  - hookups.water = false · “RIDB campsites: 3 overnight sites (tent 3, group 3); electric at 0, water at 0, sewer at 0”
  - phone = "(606) 528-6156" · “RIDB FacilityPhone: 606-528-6156”
  - reservable = true · “RIDB Reservable = True”
  - restrooms = "vault" · “area comes with a campfire circle, large grill, picnic tables and a lantern pole. Modern vault toilets and a shower house are available. Nat”
