#!/usr/bin/env bash
set -euo pipefail

npm install -g @charmland/crush

install -d /usr/share/licenses/crush
curl \
  -fsSL \
  --retry 8 \
  --retry-all-errors \
  --retry-delay 2 \
  --max-time 300 \
  https://raw.githubusercontent.com/charmbracelet/crush/main/LICENSE.md \
  -o /usr/share/licenses/crush/LICENSE.md
