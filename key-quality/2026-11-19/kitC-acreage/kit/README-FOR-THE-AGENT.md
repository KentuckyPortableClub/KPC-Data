# Outside research job C: official acreage tables (Kentucky Portable Club, 19 Nov 2026)

We need the agencies' OWN published acreage for every unit, as plain tables. They let our map tool check whether an outline is
the right size. Three tables, one per agency. Copy the numbers as published: do not round, convert or add them up.

1. kitC-nps-acres.answers.csv: National Park Service, every unit.
   Source: the NPS Land Resource Division "Summary of Acreage" (Listing of Acreage by park), the newest year
   (irma.nps.gov/Stats or nps.gov/subjects/lwcf / land resources pages). One row per unit and per PART when the report lists
   parts (Denali: a park row and a preserve row). acres_kind = 'gross area' or 'federal', as the report names its column (give both
   as two rows if the report has both).
2. kitC-fws-acres.answers.csv: U.S. Fish & Wildlife Service, every National Wildlife Refuge, Wetland Management District and
   Fish Hatchery. Source: the FWS "Annual Report of Lands Under Control of the U.S. Fish and Wildlife Service", newest year
   (fws.gov). acres_kind = the report's column name (for example 'total acres' or 'fee acres').
3. kitC-usfs-acres.answers.csv: U.S. Forest Service, every National Forest, Grassland, Recreation Area, Monument and Scenic Area.
   Source: the Forest Service "Land Areas Report" (LAR), newest year (fs.usda.gov). acres_kind = 'NFS acres' or 'gross acres'
   (give both when the report has both).

Columns (keep them exactly): agency, unit_name, unit_code (the agency's own code if the report has one, else empty), unit_type
(as the report says: National Park, National Preserve, NWR, National Forest ...), state (as the report gives it; several states
'AK;WA' is fine), official_acres, acres_kind, report_name, report_date, source_url (the file or page you took it from).

If a report is a PDF, extracting its table is the job: every row, not a sample. If a report cannot be opened, write one row with
the unit_name 'REPORT NOT REACHED' and the address you tried in source_url.
Return: the three filled answers.csv files only.
