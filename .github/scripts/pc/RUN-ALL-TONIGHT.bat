@echo off
setlocal
cd /d "%~dp0"
title KPC: page reader - all of tonight in one start
echo.
echo   ========================================================
echo     KPC: PAGE READER - ALL OF TONIGHT IN ONE START
echo   ========================================================
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist PRIVATE\priority-parks.csv (echo Run 1-MAKE-PRIVATE-LISTS.bat first. & pause & exit /b)
if not exist page-reader\scripts\kpc_park_pages_slow.py (echo The newest reader is not on this PC yet. Ask Claude to send it. & pause & exit /b)
if not exist SEND-BACK mkdir SEND-BACK
echo     ONE start does all of tonight, with no questions:
echo       1. read the park pages that are due. The 2,200 numbered pages
echo          that were first read wrong are read again.
echo       2. look for the own pages
echo       3. read the slow sites
echo       4. map points, then the upload pack
echo     Leave it running.
echo     You can close the window to stop. Every step carries on where it
echo     stopped next time.
cd page-reader
set "RF=-I"
set "BROWSER="
REM 27 Nov 2026: the page browser was never switched on here (only in 2-READ-PARK-PAGES.bat), so sites that need it were never read
%PY% -I -c "import playwright" >NUL 2>NUL && set "BROWSER=1"
if not defined BROWSER %PY% -E -P -c "import playwright" >NUL 2>NUL && set "BROWSER=1" && set "RF=-E -P"
if defined BROWSER (echo     The page browser is ON.) else (echo     The page browser is NOT installed. Run 0-INSTALL-PAGE-BROWSER.bat once, then start this again.)
echo.
echo   ------------------------------------------------------------
echo     Step 1 of 4: read the park pages that are due
echo   ------------------------------------------------------------
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --priority-file ..\PRIVATE\priority-parks.csv --confirmed-file ..\PRIVATE\confirmed-parks.csv --max-minutes 300 --max-requests 30000
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
%PY% -I ..\tools\kpc_sort_names.py --out out
echo.
echo   ------------------------------------------------------------
echo     Step 2 of 4: find the own pages
echo   ------------------------------------------------------------
echo     For parks with no link, a dead link or only the front page.
%PY% -I scripts\kpc_park_pages.py --pc find-links --data data --out out --state out\state.json --agency-table data\key-agency-table.json --priority-file ..\PRIVATE\priority-parks.csv --max-minutes 180 --max-requests 25000
type out\found-links-summary.txt
echo.
echo   ------------------------------------------------------------
echo     Step 3 of 4: read the parks that wait on slow sites
echo   ------------------------------------------------------------
echo     As slowly as each site asks.
%PY% -I scripts\kpc_park_pages_slow.py --out out
set "KPC_MAX_CRAWL_DELAY=900"
set "KPC_SLOW_HOST_BUDGET=5000"
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --refs-file out\slow-refs.json --max-minutes 300 --max-requests 6000
set "KPC_MAX_CRAWL_DELAY="
set "KPC_SLOW_HOST_BUDGET="
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
echo.
echo   ------------------------------------------------------------
echo     Step 4 of 4: map points, then the upload pack
echo   ------------------------------------------------------------
%PY% -I ..\tools\kpc_geocode_addresses.py --out out --scripts scripts
cd ..
%PY% -I tools\kpc_upload_pack.py
echo.
echo   ========================================================
echo     DONE. Next: tell Claude "tonight done".
echo     Claude takes the pack from SEND-BACK and uploads it.
echo   ========================================================
pause
