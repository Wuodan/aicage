#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

yamllint .
pymarkdown \
  --config .pymarkdown.json scan \
  --recurse \
  --exclude './.venv/' \
  --exclude './aicage-custom-samples/' \
  --exclude './aicage-image/' \
  --exclude './aicage-image-base/' \
  --exclude './aicage-image-util/' \
  --exclude './github-actions/' \
  .
ruff check .
pyright .
# Ignore generated version metadata from setuptools-scm.
if rg -n --glob '*.py' --glob '!src/aicage/_version.py' '__all__' src; then
  echo "Found __all__ usage in src; remove it to satisfy visibility checks."
  exit 1
fi
