@echo off
setlocal
cd /d "%~dp0"
title KPC: read the parks waiting on SLOW sites (long Crawl-delay), waiting as long as each site asks
set "PY="
py -3 -c "import sys" >/dev/null 2>/dev/null && set "PY=py -3"
if not defined PY python -c "import sys" >/dev/null 2>/dev/null && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist page-reader\scripts\kpc_park_pages_slow.py (echo The slow-sites lister is not in page-reader\scripts yet. Ask Claude to send it. & pause & exit /b)
if not exist page-reader\out\facts (echo No page facts yet. Run RUN-OVERNIGHT.bat first. & pause & exit /b)
echo Some agency sites ask robots to wait a long time between pages (New York State Parks, Utah State Parks ...).
echo The nightly walk skips them. This reads ONLY the parks waiting on those sites, and waits as long as each
echo site asks (up to 15 minutes a page; robots.txt always wins). It can take all night: close the window to stop,
echo run it again later, it carries on.
pause
cd page-reader
%PY% -I scripts\kpc_park_pages_slow.py --out out
set "BROWSER="
set "RF=-I"
%PY% -I -c "import playwright" >/dev/null 2>/dev/null && set "BROWSER=1"
if not defined BROWSER %PY% -E -P -c "import playwright" >/dev/null 2>/dev/null && set "BROWSER=1" && set "RF=-E -P"
set "KPC_MAX_CRAWL_DELAY=900"
set "KPC_SLOW_HOST_BUDGET=5000"
%PY% %RF% scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --refs-file out\slow-refs.json --max-minutes 720 --max-requests 6000
%PY% -I scripts\kpc_park_pages.py --pc report --out out >/dev/null 2>&1
echo.
echo What is still waiting:
%PY% -I scripts\kpc_park_pages_slow.py --out out
cd ..
echo.
echo Making the upload pack...
%PY% -I tools\kpc_upload_pack.py
echo.
echo Done. Tell Claude "slow sites done" and the numbers above.
pause
