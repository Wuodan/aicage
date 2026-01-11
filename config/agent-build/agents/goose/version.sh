#!/usr/bin/env bash
set -euo pipefail


curl \
  -fsSL \
  --retry 8 \
  --retry-all-errors \
  --retry-delay 2 \
  --max-time 300 \
  https://api.github.com/repos/block/goose/releases/latest \
  | jq -r '.name | ltrimstr("v")'
