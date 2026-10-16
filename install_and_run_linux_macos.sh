#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest -q
python -m onur_drive.cli --source multi-synthetic
