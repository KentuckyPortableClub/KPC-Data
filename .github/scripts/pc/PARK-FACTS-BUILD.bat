@echo off
setlocal
cd /d "%~dp0"
title KPC: build the park facts on this PC
echo.
echo   ========================================================
echo     KPC: BUILD THE PARK FACTS ON THIS PC
echo   ========================================================
echo     It makes a new park-facts.json.gz from what this PC has:
echo       - the page reader's own page reads
echo       - the parks list the page reader uses
echo       - the files in park-facts-inputs, if you have them
echo     Anything this PC does not have is kept from the park facts
echo     file that is here now. Nothing is downloaded or uploaded.
echo.
rem Python 3.12 first: GitHub builds the park facts with 3.12. -B: no .pyc files in the page reader's folder.
set "PY="
py -3.12 -c "import sys" >NUL 2>NUL && set "PY=py -3.12"
if not defined PY py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3" && echo     NOTE: Python 3.12 was not found, so the newest Python is used.
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo     Python was not found. Install Python 3.12 from python.org first. & pause & exit /b)
rem Where the page reader is: C:\KPC\6-TOOLS\PAGE-READER, or a PAGE-READER folder beside this one.
set "PR="
if exist "%~dp0..\6-TOOLS\PAGE-READER\page-reader\scripts\kpc_park_pages_rules.py" set "PR=%~dp0..\6-TOOLS\PAGE-READER\page-reader"
if not defined PR if exist "%~dp0..\PAGE-READER\page-reader\scripts\kpc_park_pages_rules.py" set "PR=%~dp0..\PAGE-READER\page-reader"
if not defined PR (echo     The page reader was not found in ..\6-TOOLS\PAGE-READER. Nothing was changed. & pause & exit /b)
if not exist "%PR%\data\parkinfo" (echo     The page reader has no parks list ^(data\parkinfo^). Nothing was changed. & pause & exit /b)
if not exist "%PR%\out\facts" (echo     The page reader has no page reads yet ^(out\facts^). Nothing was changed. & pause & exit /b)
if not exist park-facts.json.gz (echo     park-facts.json.gz is not in this folder. Nothing was changed. & pause & exit /b)
if not exist park-facts-tool\kpc_park_facts.py (echo     The folder park-facts-tool is missing. Nothing was changed. & pause & exit /b)
rem The optional files from GitHub (a kit snapshot): sizes, agency lists, the keeper's sizes.
set "IN=%~dp0park-facts-inputs"
set "EXTRA="
if exist "%IN%\acres.json" set "EXTRA=%EXTRA% --acres "%IN%\acres.json""
if exist "%IN%\keeper-sizes.json" set "EXTRA=%EXTRA% --keeper-sizes "%IN%\keeper-sizes.json""
if exist "%IN%\crosswalk\*.json" set "EXTRA=%EXTRA% --crosswalk "%IN%\crosswalk""
if exist park-facts-work rmdir /s /q park-facts-work
mkdir park-facts-work
echo     Step 1 of 2: the link ids, from the parks list...
%PY% -I -B -X utf8 -c "import sys; sys.path[:0] = [r'%PR%\scripts', r'%~dp0park-facts-tool']; import kpc_link_ids as L; L.main(sys.argv[1:])" --parkinfo "%PR%\data\parkinfo" --areas "US CA" --out park-facts-work\links >park-facts-work\link-ids-log.txt 2>&1
set "L="
for /f "delims=" %%F in ('dir /b /s park-facts-work\links\link-ids.csv 2^>NUL') do set "L=%%F"
if not defined L (echo     The link ids could not be made. See park-facts-work\link-ids-log.txt. Nothing was changed. & pause & exit /b)
echo     Step 2 of 2: the park facts...
%PY% -I -B -X utf8 park-facts-tool\kpc_park_facts.py --parkinfo "%PR%\data\parkinfo" --pages "%PR%\out\facts" --links "%L%" %EXTRA% --previous park-facts.json.gz --carry-missing --tools "%PR%\scripts" --tools park-facts-tool --out park-facts-work\out >park-facts-work\park-facts-log.txt 2>&1
set "RC=%ERRORLEVEL%"
if not exist park-facts-work\out\summary.txt (echo     The build failed. See park-facts-work\park-facts-log.txt. Nothing was changed. & pause & exit /b)
cls
echo.
echo   ========================================================
echo     WHAT WAS BUILT
echo   ========================================================
%PY% -I -B -X utf8 -c "import sys; L = open(sys.argv[1], encoding='utf-8').read().split('\n'); top = L[:L.index('', 7)]; stop = L[L.index('STOP: an input shrank since the previous file. Do not use this file:'):] if 'STOP: an input shrank since the previous file. Do not use this file:' in L else []; print('\n'.join('    ' + x[:150] for x in top + [''] + stop))" park-facts-work\out\summary.txt
echo.
if "%RC%"=="3" (echo     NOT PUT IN PLACE: something shrank since the last file ^(see STOP above^). & echo     Your park-facts.json.gz is unchanged. Tell Claude "park facts STOP". & pause & exit /b)
if not "%RC%"=="0" (echo     The build ended with an error. See park-facts-work\park-facts-log.txt. & echo     Your park-facts.json.gz is unchanged. & pause & exit /b)
%PY% -I -c "import gzip, shutil; g = gzip.GzipFile(r'park-facts-work\out\park-facts.json.gz', 'wb', 9, mtime=0); shutil.copyfileobj(open(r'park-facts-work\out\park-facts.json', 'rb'), g); g.close()"
choice /c YN /m "    Put the new park facts in place now (the old file is kept as a backup)"
if errorlevel 2 (echo     Not put in place. The new file is in park-facts-work\out. & pause & exit /b)
for /f %%S in ('%PY% -I -c "import datetime; print(datetime.datetime.now().strftime('%%Y%%m%%d-%%H%%M'))"') do set "STAMP=%%S"
copy /y park-facts.json.gz "park-facts.before-%STAMP%.json.gz" >NUL
copy /y park-facts-work\out\park-facts.json.gz park-facts.json.gz >NUL
copy /y park-facts-work\out\summary.txt park-facts-summary.txt >NUL
echo.
echo   ========================================================
echo     DONE. The new park-facts.json.gz is in place.
echo     The old one is park-facts.before-%STAMP%.json.gz.
echo     Next: tell Claude "park facts built on the PC".
echo   ========================================================
pause
