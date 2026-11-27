@echo off
setlocal
cd /d "%~dp0"
title KPC: page reader - find the real names (only the parks with a name problem)
echo.
echo   ========================================================
echo     KPC: FIND THE REAL NAMES
echo   ========================================================
echo     Reads the whole page again for every name it calls the park,
echo     but ONLY for parks with a possible name problem:
echo       - the page reader's own name questions, and
echo       - parks your newest key test did not confirm.
echo     It uses the pages already saved on this PC. No website is asked.
echo.
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo     Python was not found. & pause & exit /b)
if not exist page-reader\pages-kept\manifest.json (echo     No pages are saved yet. Run RUN-ALL-TONIGHT.bat first. & pause & exit /b)
cd page-reader
echo   ------------------------------------------------------------
echo     Step 1 of 3: make the list
echo   ------------------------------------------------------------
%PY% -I ..\tools\kpc_name_refs.py --out out
echo.
echo   ------------------------------------------------------------
echo     Step 2 of 3: read those saved pages again for names
echo   ------------------------------------------------------------
%PY% -I scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --reextract --refs-file out\name-refs.json --max-minutes 120
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
cd ..
echo.
echo   ------------------------------------------------------------
echo     Step 3 of 3: make the upload pack
echo   ------------------------------------------------------------
%PY% -I tools\kpc_upload_pack.py
echo.
echo   ========================================================
echo     DONE. Tell Claude "names done".
echo   ========================================================
echo.
pause
