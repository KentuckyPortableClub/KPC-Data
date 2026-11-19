@echo off
setlocal
cd /d "%~dp0"
set PYW=pythonw
where %PYW% >nul 2>nul || set PYW=pyw
echo ==========================================================
echo  KPC HEARTBEAT: turn it ON (every 20 minutes, no window)
echo ==========================================================
schtasks /Create /TN "KPC heartbeat" /SC MINUTE /MO 20 /TR "%PYW% \"%~dp0kpc_heartbeat.py\"" /F
echo.
echo  Done. It writes one line per look to kpc-heartbeat.log in this folder.
echo  To turn it off, run 3-HEARTBEAT-OFF.bat
pause
