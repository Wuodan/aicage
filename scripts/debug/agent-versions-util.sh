#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="ghcr.io/aicage/aicage-image-util:agent-version"

for agent_dir in "${ROOT_DIR}/aicage-image/agents/"*; do
  agent_name="$(basename "${agent_dir}")"
  echo "${agent_name}"
  docker run --rm \
    -v "${agent_dir}:/agent:ro" \
    "${IMAGE}" \
    /bin/bash /agent/version.sh
done
