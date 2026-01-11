#!/usr/bin/env bash
set -euo pipefail

BASE_URL=https://github.com/aicage/aicage-image/releases/latest/download

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

curl_download() {
  local source_file="$1"
  local target_file="$2"
  curl -fsSL \
    --retry 8 \
    --retry-all-errors \
    --retry-delay 2 \
    --max-time 600 \
    -o "${target_file}" \
    "${BASE_URL}/${source_file}"
}

echo "# Syncing with sub-project 'aicage-image'" >&2

echo "- Update config/images-metadata.yaml" >&2
curl_download images-metadata.yaml config/images-metadata.yaml

echo "- Update config/agent-build/Dockerfile" >&2
curl_download Dockerfile config/agent-build/Dockerfile

echo "- Update config/agent-build/agents/" >&2
rm -rf config/agent-build/agents/
TMPDIR="$(mktemp -d)" || (echo "Failed to create temp dir" >&2 && exit 1)
curl_download agents.tar.gz "${TMPDIR}"/agents.tar.gz
tar -xzf "${TMPDIR}"/agents.tar.gz -C config/agent-build
rm "${TMPDIR}"/agents.tar.gz

echo "Done syncing" >&2