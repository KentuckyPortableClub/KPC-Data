@echo off
setlocal
title KPC link ids self-test
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY goto nopython
%PY% "%~dp0kpc_link_ids.py" --selftest
goto done

:nopython
echo Python 3 was not found on this PC. Install it from python.org, then run this again.

:done
echo.
pause
endlocal
