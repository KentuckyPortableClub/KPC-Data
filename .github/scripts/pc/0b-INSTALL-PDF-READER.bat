@echo off
setlocal
cd /d "%~dp0"
title KPC page reader: install the PDF reader (pypdf, one time)
set "LOG=%~dp0pdf-install-log.txt"
echo KPC: installing pypdf (the PDF reader), %date% %time% > "%LOG%"
set "PY="
py -3 -c "import sys" >NUL 2>NUL && set "PY=py -3"
if not defined PY python -c "import sys" >NUL 2>NUL && set "PY=python"
if not defined PY (echo Python was not found.>> "%LOG%" & exit /b)
%PY% -m pip install pypdf >> "%LOG%" 2>&1
rem the kit runs Python with -I, which does not see a per-user install: then pypdf goes next to the reader's own scripts
%PY% -I -c "import pypdf" >NUL 2>NUL || %PY% -m pip install --target page-reader\scripts pypdf >> "%LOG%" 2>&1
cd page-reader
%PY% -I -c "import sys; sys.path.insert(0, 'scripts'); import pypdf; print('RESULT: pypdf works for the page reader, version', pypdf.__version__)" >> "%LOG%" 2>&1 || echo RESULT: pypdf did not install.>> "%LOG%"
exit /b
