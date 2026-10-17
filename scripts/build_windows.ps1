# Standalone Windows LAB bundle, no Python required on the end user's PC.
$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
python -m pip install -e ".[test]" "pyinstaller>=6.10,<7"
if ($LASTEXITCODE -ne 0) { throw "install failed" }
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "unit tests failed" }
python -m PyInstaller --noconfirm --clean --onedir --console --name OnurDriveAI-Lab `
  --collect-all cv2 --collect-all uvicorn `
  --collect-submodules fastapi --collect-submodules pydantic --collect-submodules anyio `
  src/onur_drive/launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
