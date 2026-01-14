#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TMPDIR="$(mktemp -d)"

echo "# Syncing with sub-project 'aicage-image'" >&2
"${SCRIPT_DIR}"/get-aicage-release-artifact.sh aicage-image "${TMPDIR}"

echo "- Update config/images-metadata.yaml" >&2
cp "${TMPDIR}"/images-metadata.yaml config/images-metadata.yaml

echo "- Update config/agent-build/Dockerfile" >&2
cp "${TMPDIR}"/Dockerfile config/agent-build/Dockerfile

echo "- Update config/agent-build/agents/" >&2
rm -rf config/agent-build/agents/
cp -r "${TMPDIR}"/agents config/agent-build/

echo "- Clean up temp dir" >&2
rm -rf "${TMPDIR}"

echo "Done syncing" >&2