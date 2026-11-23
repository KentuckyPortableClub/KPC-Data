@echo off
setlocal
cd /d "%~dp0"
title KPC tonight: read the park pages, find the own pages, read the slow sites, make the upload pack (one start, no questions)
set "PY="
py -3 -c "import sys" >/dev/null 2>/dev/null && set "PY=py -3"
if not defined PY python -c "import sys" >/dev/null 2>/dev/null && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist PRIVATE\priority-parks.csv (echo Run 1-MAKE-PRIVATE-LISTS.bat first. & pause & exit /b)
if not exist page-reader\scripts\kpc_park_pages_slow.py (echo The newest reader is not on this PC yet. Ask Claude to send it. & pause & exit /b)
if not exist SEND-BACK mkdir SEND-BACK
echo ONE start does all of tonight: 1 read the park pages that are due (the 2,200 numbered pages first read wrong are
echo read again), 2 look for the own pages, 3 read the slow sites, 4 make the upload pack. No questions. Leave it running.
echo You can close the window to stop: every step carries on where it stopped next time.
cd page-reader
set "RF=-I"
%PY% -I -c "import playwright" >/dev/null 2>/dev/null || (%PY% -E -P -c "import playwright" >/dev/null 2>/dev/null && set "RF=-E -P")
echo.
echo [1 of 4] Reading the park pages that are due...
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --priority-file ..\PRIVATE\priority-parks.csv --confirmed-file ..\PRIVATE\confirmed-parks.csv --max-minutes 300 --max-requests 30000
%PY% -I scripts\kpc_park_pages.py --pc report --out out >/dev/null 2>&1
%PY% -I ..\tools\kpc_sort_names.py --out out
echo.
echo [2 of 4] Looking for the own pages of parks with no link, a dead link or only the front page...
%PY% -I scripts\kpc_park_pages.py --pc find-links --data data --out out --state out\state.json --agency-table data\key-agency-table.json --priority-file ..\PRIVATE\priority-parks.csv --max-minutes 180 --max-requests 25000
type out\found-links-summary.txt
echo.
echo [3 of 4] Reading the parks that wait on slow sites (as slowly as each site asks)...
%PY% -I scripts\kpc_park_pages_slow.py --out out
set "KPC_MAX_CRAWL_DELAY=900"
set "KPC_SLOW_HOST_BUDGET=5000"
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --refs-file out\slow-refs.json --max-minutes 300 --max-requests 6000
set "KPC_MAX_CRAWL_DELAY="
set "KPC_SLOW_HOST_BUDGET="
%PY% -I scripts\kpc_park_pages.py --pc report --out out >/dev/null 2>&1
echo.
echo [4 of 4] Map points, then the upload pack...
%PY% -I ..\tools\kpc_geocode_addresses.py --out out --scripts scripts
cd ..
%PY% -I tools\kpc_upload_pack.py
echo.
echo All done. Tell Claude "tonight done": Claude takes the pack from SEND-BACK and uploads it.
pause
