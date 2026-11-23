@echo off
setlocal
cd /d "%~dp0"
title KPC: find the OWN page of each park with no link, a dead link or only the agency front page, then map points and the upload pack
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo Python was not found. & pause & exit /b)
if not exist page-reader\scripts\kpc_park_pages_find.py (echo The finder is not in page-reader\scripts yet. Ask Claude to send it. & pause & exit /b)
if not exist page-reader\out\facts (echo No page facts yet. Run RUN-OVERNIGHT.bat first. & pause & exit /b)
echo Run this only AFTER 2e-REREAD-KEPT-PAGES.bat has finished.
echo It looks on each agency's OWN site for the parks POTA gives no link, a dead link or only the front page.
echo Same manners as the reader: robots.txt always wins, slow, no search engine, no Wikipedia, tourism or trail sites.
echo A page is taken only when SURE (its own name and a second witness); the rest is listed for a person.
pause
if exist 0b-INSTALL-PDF-READER.bat (
  echo First, the PDF reader ^(pypdf^), once: it makes the next runs read PDF pages better...
  call 0b-INSTALL-PDF-READER.bat
  findstr /b RESULT pdf-install-log.txt
)
cd page-reader
set "ARGS=--data data --out out --state out\state.json --agency-table data\key-agency-table.json --priority-file ..\PRIVATE\priority-parks.csv"
echo.
echo FIRST a trial on one state (New Hampshire, about 100 parks)...
%PY% -I scripts\kpc_park_pages.py --pc find-links %ARGS% --areas US-NH --max-minutes 60 --max-requests 1500
echo.
type out\found-links-summary.txt
echo.
echo That was the trial. Press a key to look for ALL the other parks (it can take some hours; you can close the window
echo to stop early and run this file again later: it carries on where it stopped). Close the window now to stop after the trial.
pause
%PY% -I scripts\kpc_park_pages.py --pc find-links %ARGS% --max-minutes 600 --max-requests 25000
%PY% -I scripts\kpc_park_pages.py --pc report --out out >NUL 2>&1
echo.
type out\found-links-summary.txt
echo.
echo Turning the found pages' addresses and town lines into map points...
%PY% -I ..\tools\kpc_geocode_addresses.py --out out --scripts scripts
cd ..
echo.
echo Making the upload pack...
%PY% -I tools\kpc_upload_pack.py
echo.
echo To carry it up: on GitHub open KPC-Data, switch the branch to intake-files, open the folder pc-upload
echo (Add file, Upload files), drop the NEWEST zip in and commit. Then Actions, "KPC PC upload pack (by hand)", Run workflow,
echo and type pc-upload/ plus the zip's name.
echo.
echo Done. Tell Claude "own pages done" and the numbers above.
pause
