@echo off
setlocal
title KPC link ids
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY goto nopython

set "SRC=%~1"
if defined SRC goto havesrc
echo.
echo Drag the parkinfo folder (KPC-Data\data\parkinfo) onto this file next time, or type its path now.
echo.
set /p "SRC=Parks list folder: "
if not defined SRC goto nofolder
set "SRC=%SRC:"=%"

:havesrc
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"
set "KEY="
echo.
echo Optional: the key folder (KPC-Links\data\us-key), to also run the name check.
set /p "KEY=Key folder (press Enter to skip): "
if defined KEY set "KEY=%KEY:"=%"
if defined KEY if "%KEY:~-1%"=="\" set "KEY=%KEY:~0,-1%"
echo.
if defined KEY goto withkey
%PY% "%~dp0kpc_link_ids.py" --parkinfo "%SRC%" --areas "US CA" --out "%~dp0link-ids-out"
goto done

:withkey
%PY% "%~dp0kpc_link_ids.py" --parkinfo "%SRC%" --key "%KEY%" --areas "US CA" --out "%~dp0link-ids-out"
goto done

:nopython
echo Python 3 was not found on this PC. Install it from python.org, then run this again.
goto done

:nofolder
echo No folder was given. Nothing was done.

:done
echo.
pause
endlocal
