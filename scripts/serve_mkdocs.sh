#!/bin/bash
# Локальний перегляд сайту курсу.
set -euo pipefail

cd "$(dirname "$0")/.."
pip install -q -r requirements-docs.txt
python3 scripts/prepare_docs.py
mkdocs serve -f .mkdocs-build/mkdocs.yml
