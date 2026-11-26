@echo off
setlocal
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py
echo ==========================================================
echo  KPC HEARTBEAT: one look, by hand (starts nothing: dry run)
echo ==========================================================
%PY% kpc_heartbeat.py --dry-run
echo.
echo  If the line above shows two repos and minutes, the setup works.
echo  If it says "could not look", open a command window and run:  gh auth status
pause
