@echo off
schtasks /Delete /TN "KPC heartbeat" /F
echo  The heartbeat is off.
pause
