#!/usr/bin/env bash
set -euo pipefail

curl \
  -fsSL \
  --retry 8 \
  --retry-all-errors \
  --retry-delay 2 \
  --max-time 300 \
  https://github.com/block/goose/releases/download/stable/download_cli.sh | \
  GOOSE_BIN_DIR=/usr/local/bin \
  CONFIGURE=false \
  bash
