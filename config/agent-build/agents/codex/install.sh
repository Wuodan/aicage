#!/usr/bin/env bash
set -euo pipefail

npm install -g @openai/codex

install -d /usr/share/licenses/codex
curl \
  -fsSL \
  --retry 8 \
  --retry-all-errors \
  --retry-delay 2 \
  --max-time 300 \
  https://raw.githubusercontent.com/openai/codex/main/LICENSE \
  -o /usr/share/licenses/codex/LICENSE
