#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}

if [ "${ONUR_DRIVE_OFFLINE:-0}" = "1" ]; then
  # Fully offline LAB mode: use existing dependencies; never modify system Python.
  "$PYTHON" -c 'import cv2, numpy, fastapi, uvicorn, yaml, pytest'
  export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
  "$PYTHON" -m pytest -q
  exec "$PYTHON" -m onur_drive.cli --source multi-synthetic
fi

"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
exec python -m onur_drive.cli --source multi-synthetic
