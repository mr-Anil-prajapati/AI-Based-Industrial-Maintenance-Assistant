#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Environment created in .venv"
echo "Start desktop app with: source .venv/bin/activate && python desktop_app/main.py"
echo "Optional API mode: source .venv/bin/activate && uvicorn backend.main:app --reload"
