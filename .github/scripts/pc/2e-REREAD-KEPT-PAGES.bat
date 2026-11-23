@echo off
setlocal
cd /d "%~dp0"
title KPC: read the KEPT park pages again with the newest reader (no web), then map points and the upload pack
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist page-reader\pages-kept\manifest.json (echo No pages are kept yet. Run RUN-OVERNIGHT.bat first. & pause & exit /b)
echo Run this only AFTER RUN-OVERNIGHT has finished (its window says "All three steps are done").
echo It reads the pages kept on this PC again with the newest reader. No website is asked.
pause
if exist 0b-INSTALL-PDF-READER.bat (
  echo First, the PDF reader, once...
  call 0b-INSTALL-PDF-READER.bat
  findstr /b RESULT pdf-install-log.txt
)
cd page-reader
echo Reading the kept pages again...
%PY% -I scripts\kpc_park_pages.py --pc read --data data --out out --state out\state.json --reextract --max-minutes 600
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
echo.
echo Turning the addresses and town lines into map points...
%PY% -I ..\tools\kpc_geocode_addresses.py --out out --scripts scripts
cd ..
echo.
echo Making the upload pack...
%PY% -I tools\kpc_upload_pack.py
echo.
echo To carry it up: on GitHub open KPC-Data, switch the branch to intake-files, open the folder pc-upload
echo (Add file, Upload files), drop the zip in and commit. Then Actions, "KPC PC upload pack (by hand)", Run workflow,
echo and type pc-upload/ plus the zip's name.
echo.
echo Done. Tell Claude "kept pages done".
pause
