# Outside research job B: national parks that are also preserves (Kentucky Portable Club, 19 Nov 2026)

Some National Park Service units have one code but TWO parts with different rules: a National Park (or Monument) and a National
Preserve (for example Denali National Park and Denali National Preserve). Our map tool needs to know, for each unit below, which
part POTA's park number covers and which boundary record is which part.

Fill in kitB-park-and-preserve.answers-template.csv: one row per NPS unit code (23 rows). Save it as kitB-park-and-preserve.answers.csv.
The first four columns are filled in from our data. Do not change them.

- one_unit_or_parts: PARTS (a park/monument part and a preserve part, each with its own acreage) or ONE (a single preserve, or a
  unit whose preserve is not a separate area).
- official_acres_park_part / official_acres_preserve_part: from the National Park Service's own figures. Best source: the NPS Land
  Resource Division "Summary of Acreage" report (irma.nps.gov/Stats, or the unit's nps.gov "Management > Statistics" page). Write
  the number exactly as published. Leave a cell empty when the part does not exist.
- acreage_source: the address of the page or report you opened, and its date.
- pota_ref_park_part / pota_ref_preserve_part: the POTA reference(s) (US-nnnn) from pota.app whose name is that part. POTA's own
  park pages are fine for THIS column only. 'none' when POTA has no number for that part.
- which_record_is_park / which_record_is_preserve: the record id(s) from column 4 that are that part, judged from the record's name
  and acres against the official acres. 'unsure' when you cannot tell.
- note: anything that does not fit, for example "POTA lists only the park; its page says the preserve also counts".

A similar name is not evidence. No source = leave the cell empty and say why in 'note'. Some rows are tests with known answers.
Return: the filled answers.csv only.
