# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-28. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 103 | 23 | 0 | 42 | 38 | 0 | 0 | 0 | 0 | 8 | 49 | 83 |

## Hosts that need a browser (403), say no in robots.txt, or are resting

- www.recreation.gov: 38 campgrounds · robots.txt says no

## Needs a browser pass (the page opened but its text holds no campground facts: filled by script, most likely)

- parks.ky.gov: 30 campgrounds
- home.nps.gov: 5 campgrounds
- app.fw.ky.gov: 4 campgrounds
- www.fs.usda.gov: 1 campgrounds
- kyhorsepark.com: 1 campgrounds
- fw.ky.gov: 1 campgrounds

## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)

- 2026-10-28: 67 hand-checked campgrounds · fields agree 42 · DIFFER 2 · bot blank 175

**GATE=PASS** · known answers: 15 right of 15 read, 0 waiting on the secret, 1 warn · hand-key agreement 42/44 = 95% (need 70%; 'some' = agree; KEY_WRONG rows left out)

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
- WARN: Fort Boonesborough: site count read from the state park page (key 163, so >= 100) · got no count in the page text; read https://parks.ky.gov/explore/fort-boonesborough-state-park-7811 + None -> parks.ky.gov: needs browser?

**KEY_WRONG (hand-key rows the checkers found wrong; left out of the count; Brandon fixes the key):**

| campground | field | bot | key | why |
|---|---|---|---|---|
| Clear Creek Campground | electric | False | True | agency words say no hookups (chat 11 regrade); key says electric True |
| White Sulphur Horse Camp | electric | False | True | agency words say no hookups (chat 11 regrade); key says electric True |
| Koomer Ridge Campground | electric | False | True | agency page says 'no hookups' (chat 8 grade); key says electric True |
| Great Meadows Campground | electric | False | True | agency words say no hookups (chat 11 regrade); key says electric True |
| Turkey Foot Campground | electric | False | True | agency page: 'There is no water, electricity or dump station available' (chat 8); key says electric True |

- Barren River Lake State Resort Park Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 101); amps bot blank (key: [30, 50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Big Bone Lick Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 62); amps bot blank (key: [30]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Blue Heron Campground (KY) (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 45); electric bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (423) 286-7275)
- Bear Creek Horse Camp (KY) (ok): sites bot blank (key: 22); electric agree (True); showers bot blank (key: True); phone bot blank (key: (423) 286-7275)
- Alum Ford Campground (KY) (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 6); electric bot blank (key: False); phone bot blank (key: (423) 569-9778)
- Bandy Creek Campground (TN) (ok): electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (423) 286-7275)
- Station Camp Campground (TN) (ok): sites bot blank (key: 24); electric bot blank (key: True); showers agree (True); phone bot blank (key: (423) 286-7275)
- Blue Licks Battlefield Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 55); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (859) 289-3653)
- Carr Creek Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 39); electric bot blank (key: True)
- Carter Caves Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 128); amps bot blank (key: [20, 30, 50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 286-4411)
- Columbus-Belmont Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 35); amps bot blank (key: [50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Ridgeline & Clifty Campgrounds (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 50); amps bot blank (key: [20, 30]); electric bot blank (key: True); phone bot blank (key: (800) 325-0063)
- Wilderness Road Campground (ok): sites bot blank (key: 151); amps bot blank (key: [20, 30, 50]); electric agree (True) [bot: some]; dump_station agree (True); showers agree (True); phone bot blank (key: (606) 248-2817)
- Dale Hollow Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 151); amps bot blank (key: [50]); electric bot blank (key: True)
- Twin Knobs Campground (ok): sites agree (200); electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 780-7818)
- Zilpo Campground (ok): electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 768-2722)
- Clear Creek Campground (ok): sites bot blank (key: 20); electric KEY WRONG (bot False, key True): left out; phone bot blank (key: (606) 784-6428)
- White Sulphur Horse Camp (ok): electric KEY WRONG (bot False, key True): left out; phone bot blank (key: (606) 784-6428)
- Koomer Ridge Campground (ok): sites agree (54); electric KEY WRONG (bot False, key True): left out; showers agree (True); phone bot blank (key: (606) 784-6428)
- Holly Bay Campground (ok): sites bot blank (key: 94); electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 864-4163)
- Grove Drive-In Campground (ok): sites bot blank (key: 44); electric agree (True) [bot: some]; phone bot blank (key: (606) 864-4163)
- Bee Rock Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 25); electric bot blank (key: True); phone bot blank (key: (606) 864-4163)
- Great Meadows Campground (ok): sites bot blank (key: 18); electric KEY WRONG (bot False, key True): left out; phone bot blank (key: (606) 376-5323)
- Barren Fork Horse Camp (ok): sites agree (41); electric bot blank (key: True); phone bot blank (key: (606) 376-5323)
- Turkey Foot Campground (ok): sites bot blank (key: 15); electric KEY WRONG (bot False, key True): left out; phone bot blank (key: (606) 864-4163)
- S-Tree Campground (ok): sites agree (20); phone bot blank (key: (606) 864-4163)
- Fort Boonesborough Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 163); electric bot blank (key: True); phone bot blank (key: (859) 527-3454)
- General Burnside Island Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 101); electric bot blank (key: True); phone bot blank (key: (606) 561-3625)
- General Butler Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 104); electric bot blank (key: True)
- Grayson Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 69); amps bot blank (key: [50]); electric bot blank (key: True); phone bot blank (key: (606) 474-6856)
- Green River Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 227); electric bot blank (key: True); phone bot blank (key: (270) 465-8255)
- Greenbo Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 102); amps bot blank (key: [30]); electric bot blank (key: True)
- Jenny Wiley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 118); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 889-1790)
- John James Audubon Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 83); amps bot blank (key: [20]); electric bot blank (key: True)
- Kenlake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 63); electric bot blank (key: True); phone bot blank (key: (270) 474-2211)
- Kentucky Dam Village Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 69); electric bot blank (key: True)
- Kincaid Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 159); electric bot blank (key: True)
- Lake Barkley Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 79); amps bot blank (key: [30]); electric bot blank (key: True)
- Lake Cumberland Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 87); electric bot blank (key: True); phone bot blank (key: (270) 343-3111)
- Lake Malone Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 25); amps bot blank (key: [30]); electric bot blank (key: True)
- Hillman Ferry Campground (ok): sites bot blank (key: 368); amps agree ([30, 50]); electric agree (True); showers agree (True); phone bot blank (key: (270) 924-2181)
- Energy Lake Campground (ok): sites bot blank (key: 35); amps DIFFER bot [30, 50] vs key [50]; electric agree (True); phone bot blank (key: (270) 924-2270)
- Wranglers Campground (ok): sites bot blank (key: 198); amps agree ([30, 50]); electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (270) 924-2200)
- Piney Campground (TN) (ok): sites DIFFER bot 44 vs key 384; electric agree (True); phone bot blank (key: (931) 232-5331)
- Fenton Self-Service Campground (ok): amps agree ([30]); electric agree (True)
- Self-service lakeside campgrounds (10) (ok): electric agree (True)
- Mammoth Cave Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 111); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 758-2424)
- Maple Springs Group Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 7); electric bot blank (key: True); dump_station bot blank (key: True); phone bot blank (key: (270) 758-2180)
- Houchin Ferry Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 12); electric bot blank (key: True); phone bot blank (key: (270) 758-2180)
- My Old Kentucky Home Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 49); amps bot blank (key: [50]); electric bot blank (key: True); phone bot blank (key: (502) 348-3502)
- Whittleton & Middle Fork Campgrounds (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 86); amps bot blank (key: [20]); electric bot blank (key: True); phone bot blank (key: (606) 663-2214)
- Nolin Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 65); electric bot blank (key: True); showers bot blank (key: True)
- Otter Creek ORA Campground (ok, no campground facts in the page text: needs browser?): electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 750-4257)
- Paintsville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 42); electric bot blank (key: True)
- Pennyrile Forest Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 63); electric bot blank (key: True)
- Taylorsville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 75); amps bot blank (key: [20]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Twin Knobs Campground (ok): sites agree (200); electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 780-7818)
- Yatesville Lake Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 47); electric bot blank (key: True)
- Yellowbank WMA primitive campground (Main Area) (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False); phone agree ((270) 547-6856)
- Zilpo Campground (ok): electric agree (True) [bot: some]; showers agree (True); phone bot blank (key: (606) 768-2722)
- Kentucky Horse Park Campground (ok, no campground facts in the page text: needs browser?): sites bot blank (key: 257); amps bot blank (key: [20, 30, 50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (859) 259-4257)
- Levi Jackson Campground (ok): sites agree (146); amps bot blank (key: [30, 50]); electric agree (True); dump_station agree (True); showers agree (True); phone bot blank (key: (606) 330-2130)
- Breaks Interstate Park Campground (ok): sites agree (138); electric agree (True) [bot: some]; phone bot blank (key: (276) 865-4413)
- Kingdom Come primitive campsites (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False)
- Higginson-Henry WMA designated campsites (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False)
- West Kentucky WMA designated camping site (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False)
- Rolling Fork WMA designated camping area (ok, no campground facts in the page text: needs browser?): electric bot blank (key: False)

## US-KY: 12 random samples (records with facts; seed = the date)

- **General Burnside Island Campground** (general-burnside-island-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 837 ft) · [parks.ky.gov](https://parks.ky.gov/burnside/parks/recreation/general-burnside-island-state-park)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/gener · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Rolling Fork WMA designated camping area** (rolling-fork-wma-designated-camping-area, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 4 facts) · [app.fw.ky.gov](https://app.fw.ky.gov/Public_Lands_Search/detail.aspx?Kdfwr_id=9219)
  - map.date_how = "PDF, no date in the link" · “link “View Detailed Map””
  - map.url = "https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf" · “link “View Detailed Map” -> https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf”
  - phone = "(502) 477-9024" · “Overview Size: 2896 acres Location: Nelson, Larue Contact: (502) 477-9024 Elevation: minimum 520 feet, maximum 980 feet. Entrance GPS”
  - rules.stay_limit = "14 days" · “Camping is allowed in designated area only and only during Turkey and Deer Seasons with a 14-day limit. No ATV’s, camping, horseback riding,”
- **Koomer Ridge Campground** (koomer-ridge-campground, KY (hand-checked list), status ok, 13 facts, 1255 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/koomer-ridge-campground)
  - booking.how = "online: www.recreation.gov" · “link “Make Reservations Here””
  - booking.url = "https://www.recreation.gov/camping/campgrounds/10311270" · “link “Make Reservations Here” -> https://www.recreation.gov/camping/campgrounds/10311270”
  - drinking_water = true · “et accessibility standards for persons with disabilities. Restrooms Flush toilet(s) Water Potable water is available at this site. Drinking ”
  - dump_station = false · “s. Campground facilities include an amphitheater and bath house with seasonal showers. No dump station available. The area serves as a trail”
  - fees = "$35 per night | $45 per night | $27 per night | $10 per nig · “Open 24 hours/day Fee Site and Info Spring - Fall (March 14 - Nov 1, 2026): Single Site: $35 per night Double Site: $45 per night Walk in te”
  - hookups.electric = false · “provides 54 campsites suitable for tent camping, 19 of which may accommodate RVs with no hookups. Campground facilities include an amphithea”
  - map.date_how = "web page, no date in the link" · “link “View Guide/Map””
  - map.url = "https://usfs-public.box.com/s/uv28hc08gky5zkaw4bzowmqk1jbiq · “link “View Guide/Map” -> https://usfs-public.box.com/s/uv28hc08gky5zkaw4bzowmqk1jbiqgs3”
  - reservable = "mixed" · “Sept 2027 Reservations Make Reservations Here Reservations available. Sites are available first-come, first-served unless reserved. General ”
  - restrooms = "flush" · “Parking Parking is available at the site. Facility and Amenity Information Accessibility Flush toilets and showers meet accessibility standa”
- **Nolin Lake Campground** (nolin-lake-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 540 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/nolin-lake-campground-8135)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/nolin · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Lake Cumberland Campground** (lake-cumberland-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 911 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/lake-cumberland-campground-8084)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/lake- · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Taylorsville Lake Campground** (taylorsville-lake-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 758 ft) · [parks.ky.gov](https://parks.ky.gov/explore/taylorsville-lake-campground-8219)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/taylo · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Barren River Lake State Resort Park Campground** (barren-river-lake-state-resort-park-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 731 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/barren-river-lake-campground-7834)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/barre · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Jenny Wiley Campground** (jenny-wiley-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 670 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/jenny-wiley-state-resort-park-7791)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/jenny · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Columbus-Belmont Campground** (columbus-belmont-campground, KY (hand-checked list), status ok, no campground facts in the page text: needs browser?, 3 facts, 446 ft) · [parks.ky.gov](https://parks.ky.gov/explore/columbus-belmont-state-park-7809)
  - booking.url = "https://kentuckystateparks.reserveamerica.com/camping/colum · “booking link from our kpc-campgrounds.json row (official system kentuckystateparks.reserveamerica.com)”
  - lodging_booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - lodging_booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Turkey Foot Campground** (turkey-foot-campground, KY (hand-checked list), status ok, 9 facts, 868 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/turkey-foot-campground)
  - drinking_water = false · “et accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is not available at this site. Picni”
  - dump_station = false · “h a picnic table, fire ring, tent pad and lantern pole. There is no water, electricity or dump station available in the campground. A playfi”
  - features = "fire ring, tent pad and lantern pole" · “ach of the 15 primitive, first come, first served sites are equipped with a picnic table, fire ring, tent pad and lantern pole. There is no ”
  - hookups.electric = false · “re equipped with a picnic table, fire ring, tent pad and lantern pole. There is no water, electricity or dump station available in the campg”
  - map.date_how = "web page, no date in the link" · “link “View Guide/Map””
  - map.url = "https://usfs-public.box.com/s/9cpbos54l97s0vqkhihkaqz0ua8vl · “link “View Guide/Map” -> https://usfs-public.box.com/s/9cpbos54l97s0vqkhihkaqz0ua8vlt61”
  - reservable = false · “s a low water ford across the creek at the campground entrance. Each of the 15 primitive, first come, first served sites are equipped with a”
  - restrooms = "vault" · “ccessibility Campsites do not meet accessibility standards for persons with disabilities. Vault toilets meet accessibility standards for per”
  - season = "year-round" · “ts National Visitor Use Monitoring, Oct 2026-Sept 2027 General Information Seasons of Use Open year-round Operational Hours Open 24 hours/da”
- **Fenton Self-Service Campground** (fenton-self-service-campground, KY (hand-checked list), status ok, 6 facts) · [www.landbetweenthelakes.us](https://www.landbetweenthelakes.us/facility/self-service-camping/)
  - fees = "$12 per night | $26 per night | $10 per night" · “rash pickup, lake access, and boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per n”
  - hookups.amps = [30] · “ss, and boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per night Turkey Bay Off-Hi”
  - hookups.electric = true · “boat ramps. Self-Service Campgrounds include: Cravens Bay – $12 per night Fenton (30 amp electric) – $26 per night Turkey Bay Off-Highway Ve”
  - restrooms = "vault" · “er basic amenities including designated campsite pads, picnic tables, grills, fire rings, vault toilets, trash pickup, lake access, and boat”
  - rules.fires = "firewood at home – do not transport it to campgrounds" · “$10 per night Boswell Landing – $10 per night Gatlin Point – $10 per night Firewood Leave firewood at home – do not transport it to campgrou”
  - season = "year-round" · “atives to the more developed campgrounds. We have 11 self-service campgrounds which offer year-round lakeside camping. Although these areas ”
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
