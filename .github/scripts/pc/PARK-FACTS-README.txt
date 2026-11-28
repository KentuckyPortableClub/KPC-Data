PARK FACTS ON THIS PC (27 Nov 2026)
====================================

What it does
  PARK-FACTS-BUILD.bat makes a new park-facts.json.gz in this folder.
  The v2 keys read that file. It uses your page reader's newest reads.
  No internet. Nothing is uploaded.

Before you start
  - Put PARK-FACTS-BUILD.bat and the folder park-facts-tool here,
    beside park-facts.json.gz (C:\KPC\5-ANSWER-KEY-TEST).
  - The page reader must be in C:\KPC\6-TOOLS\PAGE-READER.
  - Python 3.12 (the button finds it).

What to do
  1. Double-click PARK-FACTS-BUILD.bat.
  2. Read the screen. It shows how many parks, the newest input,
     and what was missing.
  3. Press Y to put the new file in place, or N to leave it.

What it reads
  - Your page reader's reads and its parks list.
  - park-facts-inputs\ (optional, from GitHub): acres.json,
    keeper-sizes.json, crosswalk\*.json.
  - Anything it does not have here is kept from the park-facts.json.gz
    that is in this folder now. The new file says "carried" on it.

When it says STOP
  Something has fewer parks than last time. Your old file stays.
  Tell Claude "park facts STOP".

To undo
  The old file is kept as park-facts.before-<date>-<time>.json.gz.
  Rename it back to park-facts.json.gz.

Details for Claude: park-facts-work\park-facts-log.txt and
park-facts-work\out\summary.txt.
