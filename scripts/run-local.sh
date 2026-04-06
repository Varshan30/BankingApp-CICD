#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
python app/app.py