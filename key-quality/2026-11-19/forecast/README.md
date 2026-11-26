# Forecast for the US key run on rules 7c6e01e1bc2b (Fable, 19 Nov 2026)
Published key against an offline build on main's merged rules, all 50 states: outlines 11,715 -> 11,626, 685 parks change.
- `cmp-pub-nps.txt`: one line per state. `cmp-pub-nps-parks.csv`: every park that changes and how.
- Use: hold the run's own files against this list (key-quality.md section 19, item 3c). A lost outline or a new hard flag
  that is NOT here goes on the STOP list.
- Limit: built without shapely, so SIZE_BIG and BIG_PIECE here mean nothing; read outlines, records, SHARED, OTHER_PARK, PIN_FAR.
- Does not hold evidence batch #277 (its 13 parks come back in the release run).
