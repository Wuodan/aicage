#!/usr/bin/env bash
set -euo pipefail

# Dummy debugging entrypoint to stay root
# Use to debug by mounting it instead of entrypoint.sh like:
# docker run --rm -it -v <path>/entrypoint-root.sh:/usr/local/bin/entrypoint.sh <image>

exec gosu root "$@"
