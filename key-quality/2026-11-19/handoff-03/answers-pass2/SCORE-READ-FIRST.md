# Hand-off 03B, pass 2 (a fresh outside-agent session; zip from Brandon 19 Nov 10:06 AM CST; scored by Fable)
A row counts only where pass 1 (`../../handoff-02/answers-pass1/`) and pass 2 agree. Nothing here is a saved answer or a new layer yet.

**Planted answers: 3 of 5.** Job 2 B2-06 Great Sand Dunes NP: right (the park record apart from the preserve, both under unit
code GRSA). Job 4 B4-09 Aniakchak: right (US-0003 is the preserve, the monument is US-0902). Job 3: B3-20 Great Brook Farm right
(MassGIS open space, another address of the same layer); B3-42 Delaware Seashore left EMPTY (a firewall stopped it); **B3-57
Mount Magazine WRONG: it answered NOTHING where the Arkansas State Parks layer holds the park.** So a pass-2 NOTHING is not proof
that no layer exists; a pass-2 GIS is well shown (record name and acres copied from the layer).

**Job 2 (official acres): 9 of 9 real rows agree with pass 1.** Craters of the Moon NM 53,437.64 (the preserve is its own row,
698,939.69); Tallgrass Prairie 10,882.67 gross / 33.12 federal; Timucuan 46,262.76 gross / 17,122.67 federal; Osage WMA 7,329 +
3,722 (two units, no total published); Acadia Cliffs 273 on the page / 275.25 on the map; Diamond HMA 166,632 (145,341 BLM);
Longview Saline SNA 6,020 and the WMA on the same land (AGFC and ANHC pages say so); Tillamook SF 364,000 in the 2010 plan,
359,8xx as Board of Forestry land in the Tillamook + Forest Grove districts. New in pass 2: ODF's own zip
`gisapps.odf.oregon.gov/data/OwnershipManagedLands.Zip` (no forest-name field: districts), and the NPS Land Resources layer
record ids (CRMO 1181, GRSA park 960, TAPR 1085, TIMU 1047).

**Job 4 (POTA's own pages): both passes agree on every row.** Katmai, Lake Clark, Gates of the Arctic, Wrangell-St. Elias,
Craters of the Moon: no preserve number of its own, the page does NOT SAY the number covers the preserve; POTA's pins are the
ones we hold. Same for Denali, New River Gorge, Jean Lafitte, Oregon Caves (new rows). The agents cannot settle R-PP1a or G-PP2
from POTA's pages: only POTA can.

**Job 3 (is there an official GIS layer): 55 real rows, 51 parks** (`SCORE-job3-both-passes.csv`).
- Both say GIS: 21 rows, 18 parks. 8 parks at the same layer or host; the rest name another address of the agency's data.
  SIX of the 18 are Forest Service BOUNDARY layers (administrative or proclaimed: Pike, Ouachita, Cibola, Sawtooth, Custer
  Gallatin 3,412,203 ac = the report's GROSS, Columbia River Gorge): by the house rule a national forest is the land the agency
  owns, never those lines, so these six are not outlines to draw.
- Pass 1 GIS, pass 2 not: 24 rows (19 NOTHING, 5 undetermined). Pass 2's reasons are specific: six TVA dam parks have no record
  by the park's name in TVA's layers; Taunton, Wekiva, Farmington, Nashua have no boundary in the Park Service's own river layer;
  National Mall is a management grouping, not a record; several are a bigger area that only contains the park. These do NOT count.
- Pass 1 open, pass 2 NOTHING: 10 rows.

**For R-NET1 (the bot host rule): the two agents read ArcGIS differently.** Pass 1: services*.arcgis.com robots.txt = "User-agent: *
/ Disallow: /". Pass 2: the same address answers 403 "Invalid URL" (no robots file), re-checked, and its notes say the owner
checked too and approved; it then read layers on services, services1, 2, 6, 7 and 9 (about 120 requests in `fetchlog.txt`, none
refused). Our own bot got 403 there on 31 Oct. Two readings against one: the "published no" of R-NET1 point 3 is NOT shown.
