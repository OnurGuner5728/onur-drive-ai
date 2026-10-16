@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%\src
python -m onur_drive.cli --source multi-synthetic --port 8765
pause
