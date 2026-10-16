@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto failure
call .venv\Scripts\activate.bat
python -m pip install -e ".[test]"
if errorlevel 1 goto failure
python -m pytest -q
if errorlevel 1 goto failure
python -m onur_drive.cli --source multi-synthetic
exit /b %errorlevel%
:failure
echo Setup failed. Check Python 3.10+ and internet access for dependencies.
pause
exit /b 1
