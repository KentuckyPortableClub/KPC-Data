# Outside research, hand-off 04 (pass 1): official sizes and "is this the park?" (Kentucky Portable Club, 19 Nov 2026)

We build park boundary maps for a ham radio club. Five answer sheets below (`*.answers-template.csv`). Fill them in and save each as
`<same name>.answers.csv` (drop "-template"). The first columns come from our data: do not change them. **Do job F first**, then
A, C, E and B. Inside each sheet the busiest parks come first. Stop when your time is up: a partial sheet is fine.

**This is a CHECK. Be hard to convince.** Write numbers exactly as the agency publishes them, with the page or table and its date.
An acre figure you cannot point to is worse than an empty cell: leave it empty and say why in `note`. A similar name is not
evidence. Some rows are tests with known answers. Another person does the same sheets on their own; do not look for their work.

**Official** = published by the agency that manages the land (its own park page, its annual land report, its GIS layer), or the
state GIS office for it. **NOT official:** PAD-US, OpenStreetMap, Google, Wikipedia, protectedplanet / WDPA, tourism and hobby sites,
news. **Where to look, in this order:** (1) the agency's own park page and its annual acreage report or table; (2) the state's or
agency's open-data portal (ArcGIS Hub, Socrata, CKAN); (3) only then a general web search.

**Manners:** read each site's robots.txt first and obey it, redirects included; ArcGIS is like any other site (robots.txt is the
only test). At least 2 seconds between requests to one site. Contact nobody. If a site refuses you, say so in `note` and move on.

## Job F, FIRST: official sizes (`jobF-official-sizes-FIRST`, 37 parks)
For each park: its official page and its official acres. Give the WHOLE unit as published, and where the agency splits it, the
parts: owned in fee, held as an easement (private land the public may or may not enter), and other agencies' land inside the
boundary. Wildlife refuges usually publish these in the Fish and Wildlife Service's "Annual Report of Lands" tables; say which table
and row. `open_to_public_note`: what the agency says about public access, in a few words. If the agency's own boundary layer is
easy to find, give its address and this park's record name and acres as the layer shows them.

## Job A: is this record the park? (`jobA-is-this-record-the-park`, 35 rows)
Each row names one map record (its id, name, acres and source as WE read them). Find the park's official page and official acres,
then answer: YES = this record is the park's land (about the same size and place); NO = it is other land; PART = it is only part of
the park, or a bigger area that only contains the park; CANNOT TELL = the official sources do not settle it. Say in `why` what the
official source shows (acres, a map, a sentence). The record's name matching the park is NOT enough on its own.

## Job C: does the managing agency publish its own outline? (`jobC-does-the-agency-publish-its-own-outline`, 6 parks)
Who manages the land; GIS = the agency's own boundary layer holds this park (layer address, record name and acres as shown, who
publishes it, licence line); PICTURE = only a picture map (PDF, brochure); NOTHING = neither. Plus the official acres.

## Job E: busy parks that now show as a pin (`jobE-busiest-new-pins`, 26 parks)
For each: official page, official acres with source and date, where the official outline lives (layer address or file) and that
record's name and acres, the outline's date and licence line.

## Job B: the Forest Service's own acres (`jobB-forest-service-acres`, 7 rows)
The Forest Service's "Land Areas of the National Forest System" report, newest edition (tell us which). For each row: the table
named, the row exactly as shown, its NFS acres and gross acres, and a link to the report file.

Return the five answers.csv files and a short NOTES file (method, anything you were blocked from, anything you are unsure of).
