# Campground info bot: review (facts only; nothing here decides anything)

Updated 2026-10-28. Every fact in <area>.json carries its source url, read date and quoted line (facts_src). Unknown = null, never guessed.
ℹ️ Maps and park info are a planning aid, not a guarantee. Always check the official agency map and rules before you go.

| area | campgrounds | read ok | needs RIDB key | needs browser (403) | robots no | host resting | no page on file | not official host | other | with site count | with booking link | with elevation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-KY | 106 | 65 | 41 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 58 | 83 |

## Needs a secret / not built yet

- RIDB_API_KEY is not set in KPC-Data: every federal (Recreation.gov) row has status "needs RIDB_API_KEY secret in KPC-Data". Free key: ridb.recreation.gov, Profile. Add it under Settings -> Secrets and variables -> Actions.
- FCC_BDC_USERNAME + FCC_BDC_TOKEN are not set: cell coverage stays blank with status "needs FCC token". Free account at broadbandmap.fcc.gov; the public data API gives per-state bulk coverage files (step 2, point lookup, is not built yet).

## Kentucky answer-key check (R5: the bot vs kpc-campgrounds.json, hand-checked)

- 2026-10-28: 67 hand-checked campgrounds · fields agree 40 · DIFFER 21 · bot blank 152

- Barren River Lake State Resort Park Campground (ok): sites bot blank (key: 101); amps bot blank (key: [30, 50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Big Bone Lick Campground (ok): sites bot blank (key: 62); amps bot blank (key: [30]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Blue Heron Campground (KY) (ok): sites bot blank (key: 45); electric agree (True); showers agree (True); phone DIFFER bot (877) 444-6777 vs key (423) 286-7275
- Bear Creek Horse Camp (KY) (ok): sites DIFFER bot 23 vs key 22; electric agree (True); showers agree (True); phone DIFFER bot (877) 444-6777 vs key (423) 286-7275
- Alum Ford Campground (KY) (ok): sites bot blank (key: 6); electric bot blank (key: False); phone bot blank (key: (423) 569-9778)
- Bandy Creek Campground (TN) (ok): electric DIFFER bot some vs key True; showers agree (True); phone DIFFER bot (877) 444-6777 vs key (423) 286-7275
- Station Camp Campground (TN) (ok): sites agree (24); electric agree (True); showers agree (True); phone DIFFER bot (877) 444-6777 vs key (423) 286-7275
- Blue Licks Battlefield Campground (ok): sites bot blank (key: 55); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (859) 289-3653)
- Carr Creek Campground (ok): sites bot blank (key: 39); electric bot blank (key: True)
- Carter Caves Campground (ok): sites bot blank (key: 128); amps bot blank (key: [20, 30, 50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 286-4411)
- Columbus-Belmont Campground (ok): sites bot blank (key: 35); amps bot blank (key: [50]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Ridgeline & Clifty Campgrounds (ok): sites bot blank (key: 50); amps bot blank (key: [20, 30]); electric bot blank (key: True); phone bot blank (key: (800) 325-0063)
- Wilderness Road Campground (ok): sites bot blank (key: 151); amps bot blank (key: [20, 30, 50]); electric DIFFER bot some vs key True; dump_station agree (True); showers agree (True); phone bot blank (key: (606) 248-2817)
- Dale Hollow Lake Campground (ok): sites bot blank (key: 151); amps bot blank (key: [50]); electric bot blank (key: True)
- Twin Knobs Campground (ok): sites agree (200); electric DIFFER bot some vs key True; showers agree (True); phone bot blank (key: (606) 780-7818)
- Clear Creek Campground (ok): sites bot blank (key: 20); electric DIFFER bot False vs key True; phone bot blank (key: (606) 784-6428)
- White Sulphur Horse Camp (ok): electric DIFFER bot False vs key True; phone bot blank (key: (606) 784-6428)
- Holly Bay Campground (ok): sites bot blank (key: 94); electric DIFFER bot some vs key True; showers agree (True); phone bot blank (key: (606) 864-4163)
- Grove Drive-In Campground (ok): sites bot blank (key: 44); electric DIFFER bot some vs key True; phone bot blank (key: (606) 864-4163)
- Bee Rock Campground (ok): sites bot blank (key: 25); electric bot blank (key: True); phone bot blank (key: (606) 864-4163)
- Great Meadows Campground (ok): sites bot blank (key: 18); electric DIFFER bot False vs key True; phone bot blank (key: (606) 376-5323)
- Barren Fork Horse Camp (ok): sites agree (41); electric bot blank (key: True); phone bot blank (key: (606) 376-5323)
- Turkey Foot Campground (ok): sites bot blank (key: 15); electric DIFFER bot False vs key True; phone bot blank (key: (606) 864-4163)
- S-Tree Campground (ok): sites bot blank (key: 20); phone bot blank (key: (606) 864-4163)
- Fort Boonesborough Campground (ok): sites bot blank (key: 163); electric bot blank (key: True); phone bot blank (key: (859) 527-3454)
- General Burnside Island Campground (ok): sites bot blank (key: 101); electric bot blank (key: True); phone bot blank (key: (606) 561-3625)
- General Butler Campground (ok): sites bot blank (key: 104); electric bot blank (key: True)
- Grayson Lake Campground (ok): sites bot blank (key: 69); amps bot blank (key: [50]); electric bot blank (key: True); phone bot blank (key: (606) 474-6856)
- Green River Lake Campground (ok): sites bot blank (key: 227); electric bot blank (key: True); phone bot blank (key: (270) 465-8255)
- Greenbo Lake Campground (ok): sites bot blank (key: 102); amps bot blank (key: [30]); electric bot blank (key: True)
- Jenny Wiley Campground (ok): sites bot blank (key: 118); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (606) 889-1790)
- John James Audubon Campground (ok): sites bot blank (key: 83); amps bot blank (key: [20]); electric bot blank (key: True)
- Kenlake Campground (ok): sites bot blank (key: 63); electric bot blank (key: True); phone bot blank (key: (270) 474-2211)
- Kentucky Dam Village Campground (ok): sites bot blank (key: 69); electric bot blank (key: True)
- Kincaid Lake Campground (ok): sites bot blank (key: 159); electric bot blank (key: True)
- Lake Barkley Campground (ok): sites bot blank (key: 79); amps bot blank (key: [30]); electric bot blank (key: True)
- Lake Cumberland Campground (ok): sites bot blank (key: 87); electric bot blank (key: True); phone bot blank (key: (270) 343-3111)
- Lake Malone Campground (ok): sites bot blank (key: 25); amps bot blank (key: [30]); electric bot blank (key: True)
- Hillman Ferry Campground (ok): sites bot blank (key: 368); amps agree ([30, 50]); electric agree (True); showers agree (True); phone agree ((270) 924-2181)
- Energy Lake Campground (ok): sites bot blank (key: 35); amps DIFFER bot [30, 50] vs key [50]; electric agree (True); phone agree ((270) 924-2270)
- Wranglers Campground (ok): sites bot blank (key: 198); amps agree ([30, 50]); electric DIFFER bot some vs key True; showers agree (True); phone agree ((270) 924-2200)
- Piney Campground (TN) (ok): sites DIFFER bot 44 vs key 384; electric agree (True); phone agree ((931) 232-5331)
- Fenton Self-Service Campground (ok): amps agree ([30]); electric agree (True)
- Self-service lakeside campgrounds (10) (ok): electric agree (True)
- Mammoth Cave Campground (ok): sites bot blank (key: 111); electric bot blank (key: True); dump_station bot blank (key: True); showers agree (True); phone bot blank (key: (270) 758-2424)
- Maple Springs Group Campground (ok): sites bot blank (key: 7); electric bot blank (key: True); dump_station bot blank (key: True); phone bot blank (key: (270) 758-2180)
- Houchin Ferry Campground (ok): sites bot blank (key: 12); electric bot blank (key: True); phone bot blank (key: (270) 758-2180)
- My Old Kentucky Home Campground (ok): sites bot blank (key: 49); amps bot blank (key: [50]); electric bot blank (key: True); phone bot blank (key: (502) 348-3502)
- Whittleton & Middle Fork Campgrounds (ok): sites bot blank (key: 86); amps bot blank (key: [20]); electric bot blank (key: True); phone bot blank (key: (606) 663-2214)
- Nolin Lake Campground (ok): sites bot blank (key: 65); electric bot blank (key: True); showers bot blank (key: True)
- Otter Creek ORA Campground (ok): electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True); phone bot blank (key: (270) 750-4257)
- Paintsville Lake Campground (ok): sites bot blank (key: 42); electric bot blank (key: True)
- Pennyrile Forest Campground (ok): sites bot blank (key: 63); electric bot blank (key: True)
- Taylorsville Lake Campground (ok): sites bot blank (key: 75); amps bot blank (key: [20]); electric bot blank (key: True); dump_station bot blank (key: True); showers bot blank (key: True)
- Yatesville Lake Campground (ok): sites bot blank (key: 47); electric bot blank (key: True)
- Yellowbank WMA primitive campground (Main Area) (ok): electric bot blank (key: False); phone agree ((270) 547-6856)
- Zilpo Campground (ok): electric DIFFER bot some vs key True; showers agree (True); phone bot blank (key: (606) 768-2722)
- Kentucky Horse Park Campground (ok): sites DIFFER bot 260 vs key 257; amps agree ([20, 30, 50]); electric DIFFER bot some vs key True; dump_station agree (True); showers agree (True); phone agree ((859) 259-4257)
- Levi Jackson Campground (ok): sites agree (146); amps bot blank (key: [30, 50]); electric agree (True); dump_station agree (True); showers agree (True); phone bot blank (key: (606) 330-2130)
- Breaks Interstate Park Campground (ok): sites agree (138); electric DIFFER bot some vs key True; phone bot blank (key: (276) 865-4413)
- Kingdom Come primitive campsites (ok): electric bot blank (key: False)
- Higginson-Henry WMA designated campsites (ok): electric bot blank (key: False)
- West Kentucky WMA designated camping site (ok): electric bot blank (key: False)
- Rolling Fork WMA designated camping area (ok): electric bot blank (key: False)
- … 3 hand-checked campgrounds not read yet (next chunk)

## US-KY: 12 random samples (records with facts; seed = the date)

- **Fort Boonesborough Campground** (fort-boonesborough-campground, KY (hand-checked list), status ok, 2 facts, 589 ft) · [parks.ky.gov](https://parks.ky.gov/explore/fort-boonesborough-state-park-7811)
  - booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Rolling Fork WMA designated camping area** (rolling-fork-wma-designated-camping-area, KY (hand-checked list), status ok, 5 facts) · [app.fw.ky.gov](https://app.fw.ky.gov/Public_Lands_Search/detail.aspx?Kdfwr_id=9219)
  - map.date_how = "PDF, no date in the link" · “link “View Detailed Map””
  - map.url = "https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf" · “link “View Detailed Map” -> https://fw.ky.gov/More/Documents/RollingForkWMA_all.pdf”
  - phone = "(502) 477-9024" · “Overview Size: 2896 acres Location: Nelson, Larue Contact: (502) 477-9024 Elevation: minimum 520 feet, maximum 980 feet. Entrance GPS”
  - rules.stay_limit = "14 days" · “Camping is allowed in designated area only and only during Turkey and Deer Seasons with a 14-day limit. No ATV’s, camping, horseback riding,”
  - rv_max_ft = 980 · “: 2896 acres Location: Nelson, Larue Contact: (502) 477-9024 Elevation: minimum 520 feet, maximum 980 feet. Entrance GPS coordinates: Latitu”
- **Kingdom Come primitive campsites** (kingdom-come-primitive-campsites, KY (hand-checked list), status ok, 2 facts) · [parks.ky.gov](https://parks.ky.gov/cumberland/parks/recreation/kingdom-come-state-park)
  - booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Nolin Lake Campground** (nolin-lake-campground, KY (hand-checked list), status ok, 2 facts, 540 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/nolin-lake-campground-8135)
  - booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Lake Cumberland Campground** (lake-cumberland-campground, KY (hand-checked list), status ok, 2 facts, 911 ft) · [parks.ky.gov](https://parks.ky.gov/parks/find-a-park/lake-cumberland-campground-8084)
  - booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Taylorsville Lake Campground** (taylorsville-lake-campground, KY (hand-checked list), status ok, 2 facts, 758 ft) · [parks.ky.gov](https://parks.ky.gov/explore/taylorsville-lake-campground-8219)
  - booking.how = "online: parks.ky.gov" · “link “Reservations Online””
  - booking.url = "https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-c · “link “Reservations Online” -> https://parks.ky.gov/things-to-do/lodging/reserve-a-lodge-cottage”
- **Barren Fork Horse Camp** (barren-fork-horse-camp, KY (hand-checked list), status ok, 9 facts, 1294 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/barren-fork-horse-camp)
  - booking.how = "online: recreation.gov" · “link “Recreation.gov””
  - booking.url = "https://recreation.gov" · “link “Recreation.gov” -> https://recreation.gov”
  - drinking_water = true · “ts accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is available at this site. Drinking ”
  - fees = "$15 per night" · “er 15th Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $15 per night Pay at site using fee envelope with ”
  - map.date_how = "web page, no date in the link" · “link “View Guide/Map””
  - map.url = "https://usfs-public.box.com/s/jp0e6xw1cv8jjryh53x3k3ixmkyhw · “link “View Guide/Map” -> https://usfs-public.box.com/s/jp0e6xw1cv8jjryh53x3k3ixmkyhwggg”
  - restrooms = "vault" · “rs must park in the overflow parking area. Facility and Amenity Information Accessibility Vault toilet meets accessibility standards for per”
  - rv_max_ft = 35 · “al Company. Today, the campground offers 41 campsites that accommodate horse trailers and RVs up to 35 feet. A picnic shelter at the campgro”
  - sites.total = 41 · “ng town operated by the Barren Fork Mining and Coal Company. Today, the campground offers 41 campsites that accommodate horse trailers and R”
- **Houchin Ferry Campground** (houchin-ferry-campground, KY (hand-checked list), status ok, 4 facts) · [home.nps.gov](https://home.nps.gov/maca/planyourvisit/houchinferrycg.htm)
  - booking.url = "https://www.recreation.gov/camping/campgrounds/258992" · “booking link from our kpc-campgrounds.json row (official system www.recreation.gov)”
  - restrooms = "yes (kind not stated)" · “Campground. Loading... Basic Information Campground Features Amenities Fire/Stove Policy Toilet Types Shower Types Operating Hours & Seasons”
  - rules.fires = "FIREWOOD QUARANTINE: Firewood from a number of states is qu · “t Additional Information Regulations Reservations Image Gallery Accessibility Information FIREWOOD QUARANTINE: Firewood from a number of sta”
  - showers = true · “Loading... Basic Information Campground Features Amenities Fire/Stove Policy Toilet Types Shower Types Operating Hours & Seasons Weather Fee”
- **Clear Creek Campground** (clear-creek-campground, KY (hand-checked list), status ok, 9 facts, 758 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/clear-creek-campground)
  - booking.how = "online: recreation.gov" · “link “Recreation.gov””
  - booking.url = "https://recreation.gov" · “link “Recreation.gov” -> https://recreation.gov”
  - drinking_water = true · “ts accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is available at this site. Drinking ”
  - fees = "$20 per night | $25 per night" · “r-round Operational Hours Open 24 hours/day Fee Site and Info Overnight Use: Single Site: $20 per night Double Site: $25 per night Pay at si”
  - hookups.electric = false · “mpsites include tent or RV pads, picnic tables, fire rings and lantern poles. There is no electricity or shower facilities. Active Alerts Na”
  - restrooms = "vault" · “ng Parking is available at the campground. Facility and Amenity Information Accessibility Vault toilet meets accessibility standards for per”
  - rules.fires = "fire rings and lantern poles" · “t can run swiftly during rainy seasons. Campsites include tent or RV pads, picnic tables, fire rings and lantern poles. There is no electric”
  - season = "year-round" · “nitoring, Oct 2026-Sept 2027 General Lake Prohibitions General Information Seasons of Use Open year-round Operational Hours Open 24 hours/da”
  - showers = false · “tent or RV pads, picnic tables, fire rings and lantern poles. There is no electricity or shower facilities. Active Alerts National Visitor U”
- **Turkey Foot Campground** (turkey-foot-campground, KY (hand-checked list), status ok, 11 facts, 868 ft) · [www.fs.usda.gov](https://www.fs.usda.gov/r08/danielboone/recreation/turkey-foot-campground)
  - booking.how = "online: recreation.gov" · “link “Recreation.gov””
  - booking.url = "https://recreation.gov" · “link “Recreation.gov” -> https://recreation.gov”
  - drinking_water = false · “et accessibility standards for persons with disabilities. Restrooms Vault toilet(s) Water Potable water is not available at this site. Picni”
  - dump_station = false · “h a picnic table, fire ring, tent pad and lantern pole. There is no water, electricity or dump station available in the campground. A playfi”
  - hookups.electric = false · “re equipped with a picnic table, fire ring, tent pad and lantern pole. There is no water, electricity or dump station available in the campg”
  - map.date_how = "web page, no date in the link" · “link “View Guide/Map””
  - map.url = "https://usfs-public.box.com/s/9cpbos54l97s0vqkhihkaqz0ua8vl · “link “View Guide/Map” -> https://usfs-public.box.com/s/9cpbos54l97s0vqkhihkaqz0ua8vlt61”
  - reservable = false · “s a low water ford across the creek at the campground entrance. Each of the 15 primitive, first come, first served sites are equipped with a”
  - restrooms = "vault" · “ccessibility Campsites do not meet accessibility standards for persons with disabilities. Vault toilets meet accessibility standards for per”
  - rules.fires = "fire ring, tent pad and lantern pole" · “ach of the 15 primitive, first come, first served sites are equipped with a picnic table, fire ring, tent pad and lantern pole. There is no ”
- **Energy Lake Campground** (energy-lake-campground, KY (hand-checked list), status ok, 15 facts) · [www.landbetweenthelakes.us](https://www.landbetweenthelakes.us/visit/energy-lake-campground/)
  - booking.how = "online: lblweb.usedirect.com" · “link “Reservations””
  - booking.url = "https://lblweb.usedirect.com/camplbl/" · “link “Reservations” -> https://lblweb.usedirect.com/camplbl/”
  - checkin = "4:30 p.m" · “Lake Campground The Gatehouse is open from 9:00am until 5:00pm during the camping season. Check-in is 4:30 p.m. , you may check in anytime o”
  - checkout = "3:30 p.m" · “ck-in is 4:30 p.m. , you may check in anytime of your arrival date if the site is vacant. Check-out is 3:30 p.m. A 1 night late fee will be ”
  - fees = "$12 | $26 | $28 | $75 | $5" · “* reservations can be made 2 days to 6 months in advance Type of Site Basic Nightly Rate $12 30 Amp Electric Nightly Rate $26 50 Amp Electri”
  - hookups.amps = [30, 50] · “eservations can be made 2 days to 6 months in advance Type of Site Basic Nightly Rate $12 30 Amp Electric Nightly Rate $26 50 Amp Electric N”
  - hookups.electric = true · “by an earthen dam. It offers 13 cabins and 35 well-defined sites in a wooded area with 33 electrical hookups capable of handling tents to mo”
  - map.date_how = "PDF, year 2025 in the link" · “link “Energy Lake Campground Map””
  - map.url = "https://www.landbetweenthelakes.us/wp-content/uploads/2025/ · “link “Energy Lake Campground Map” -> https://www.landbetweenthelakes.us/wp-content/uploads/2025/04/FINAL_PRINT_-EnergyLakeCampgroundMap_2”
  - phone = "(270) 924-2270" · “t. Address: 5501 Energy Lk Rd, Golden Pond, KY 42211 Phone: 270-924-2270 Maps LBL Maps Energy Lake Campground Map Brochures & Resour”
- **Wilderness Road Campground** (wilderness-road-campground, KY (hand-checked list), status ok, 9 facts) · [www.nps.gov](https://www.nps.gov/cuga/planyourvisit/wilderness-road-campground.htm)
  - booking.url = "https://www.recreation.gov/camping/campgrounds/258617" · “booking link from our kpc-campgrounds.json row (official system www.recreation.gov)”
  - dump_station = true · “ccommodates different lengths. No full hookups (no sewer or water at individual sites). A dump station available near the campground entranc”
  - hookups.electric = "some" · “ayout & Features Loops A,D,E,and F: Non-electric sites set in a wooded area. Loops B & C: Electric sites available with asphalt pad set in a”
  - hookups.sewer = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - hookups.water = false · “th flush toilets and showers. RV Camping Each campsite accommodates different lengths. No full hookups (no sewer or water at individual site”
  - reservable = true · “r families, scout troops, and other large groups. Maximum Group Size: 25 people per site. Reservations Required: Can be booked up to 12 mont”
  - restrooms = "flush" · “ailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets and showers. RV Camping Each campsit”
  - rules.fires = "fire ring, access to restrooms with flush toilets and showe · “a wooded area (no RV’s or camper trailers permitted). All sites include: A picnic table, fire ring, access to restrooms with flush toilets a”
  - showers = true · “Campground Basic Information Campground Features Amenities Fire/Stove Policy Toilet Types Shower Types Operating Hours & Seasons Weather Fee”
