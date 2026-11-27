@echo off
setlocal
cd /d "%~dp0"
title KPC: page reader - one button
rem 26 Nov 2026: ONE button with numbered choices. The old buttons still work as before.
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist SEND-BACK mkdir SEND-BACK
:menu
echo.
echo   ========================================================
echo     KPC: PAGE READER
echo   ========================================================
echo     1  Status: what is read, what is not and why. No internet.
echo     2  Read the KEPT pages again with the newest rules. No internet.
echo        Do this first after Claude sends a fix.
echo     3  Read ONLY what is missing: pages not read yet, pages that failed,
echo        and the slow sites (as slowly as each site asks). Uses the internet.
echo        It can run all night. Close the window to stop; it carries on next time.
echo     Q  Quit
echo.
rem 27 Nov 2026: one key press, no Enter (the same way the store room button asks). Typed answers were not taken on the owner's PC.
choice /c 123Q /n /m "    Press 1, 2, 3 or Q (no Enter needed): "
if errorlevel 4 exit /b
if errorlevel 3 goto missing
if errorlevel 2 goto reread
if errorlevel 1 goto status
goto menu

:status
cd page-reader
%PY% -I scripts\kpc_park_pages.py --pc status --out out
cd ..
pause
goto menu

:reread
if not exist page-reader\pages-kept\manifest.json if not exist page-reader\pages-kept\manifest.journal (echo     No pages are kept on this PC yet. Choice 3 keeps every page it reads. & pause & goto menu)
cd page-reader
echo     Reading the kept pages again. No website is asked.
%PY% -I scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --reextract --max-minutes 240
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
%PY% -I ..\tools\kpc_sort_names.py --out out
cd ..
%PY% -I tools\kpc_upload_pack.py
type PAGE-READER-STATUS.txt
pause
goto menu

:missing
if not exist PRIVATE\priority-parks.csv (echo     Run 1-MAKE-PRIVATE-LISTS.bat first. & pause & goto menu)
cd page-reader
set "RF=-I"
set "BROWSER="
rem 27 Nov 2026: the page browser was never switched on here, so pages that need it were never read
%PY% -I -c "import playwright" >NUL 2>NUL && set "BROWSER=1"
if not defined BROWSER %PY% -E -P -c "import playwright" >NUL 2>NUL && set "BROWSER=1" && set "RF=-E -P"
if defined BROWSER (echo     The page browser is ON.) else (echo     The page browser is NOT installed. Run 0-INSTALL-PAGE-BROWSER.bat once, then start this again.)
%PY% -I ..\tools\kpc_reread_garbled.py --out out
echo.
echo     Step 1 of 2: the pages not read yet or that failed (a page already read is not asked again)
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --priority-file ..\PRIVATE\priority-parks.csv --confirmed-file ..\PRIVATE\confirmed-parks.csv --max-minutes 300 --max-requests 30000
echo.
echo     Step 2 of 2: the slow sites, as slowly as each one asks (never skipped)
%PY% -I scripts\kpc_park_pages_slow.py --out out
set "KPC_SLOW_PASS=1"
set "KPC_SLOW_HOST_BUDGET=100000"
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --refs-file out\slow-refs.json --max-minutes 600 --max-requests 100000
set "KPC_SLOW_PASS="
set "KPC_SLOW_HOST_BUDGET="
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
%PY% -I ..\tools\kpc_sort_names.py --out out
%PY% -I ..\tools\kpc_geocode_addresses.py --out out --scripts scripts
cd ..
%PY% -I tools\kpc_upload_pack.py
type PAGE-READER-STATUS.txt
echo     Next: tell Claude "pages done". The pack is in SEND-BACK.
pause
goto menu
