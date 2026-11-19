@echo off
cd /d "%~dp0"
set LOG=run-log.txt
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.10 or newer was not found.>>"%LOG%"
  echo The details are in run-log.txt.
  exit /b 0
)
set /p STATE=Which state? (blank = continue the list) 
set PY=..\..\.github\scripts\kpc_park_pages.py
set DATA=..\..\data
if exist scripts\kpc_park_pages.py set PY=scripts\kpc_park_pages.py
if exist scripts\kpc_park_pages.py set DATA=data
if not exist out mkdir out
python "%PY%" --pc read --data "%DATA%" --out out --state out\state.json --areas "%STATE%" --max-minutes 50 >>"%LOG%" 2>&1
python -c "import datetime,zipfile; from pathlib import Path; day=datetime.date.today().isoformat(); z=zipfile.ZipFile('park-pages-'+day+'.zip','w',zipfile.ZIP_DEFLATED); [z.write(p, p.as_posix()) for p in Path('out').rglob('*') if p.is_file()]; print('Done. Send the file park-pages-'+day+'.zip to the chat.')"
