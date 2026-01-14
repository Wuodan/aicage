#!/usr/bin/env bash
set -euo pipefail

BASE_URL=https://github.com/aicage/aicage-image/releases/latest/download

_die() {
  if command -v die >/dev/null 2>&1; then
    die "$@"
  else
    echo "[common] $*" >&2
    exit 1
  fi
}

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

TMPDIR="$(mktemp -d)" || _die "Failed to create temp dir"
pushd "${TMPDIR}"
  
for artifact in aicage-image.tar.gz SHA256SUMS SHA256SUMS.sigstore.json; do
  curl_download "${artifact}" ./"${artifact}"
done

if ! cosign verify-blob \
  --bundle SHA256SUMS.sigstore.json \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  --certificate-identity-regexp '^https://github\.com/aicage/aicage-image/\.github/workflows/release\.yml@refs/tags/.*$' \
  SHA256SUMS; then
  _die "Failed to verify signature of SHA256SUMS"
fi

if ! sha256sum -c SHA256SUMS; then
  _die "Failed to verify artifact checksums with SHA256SUMS"
fi

if ! tar -xzf aicage-image.tar.gz; then
  _die "Failed to unpack aicage-image.tar.gz"
fi

popd

echo "- Update config/images-metadata.yaml" >&2
cp "${TMPDIR}"/images-metadata.yaml config/images-metadata.yaml

echo "- Update config/agent-build/Dockerfile" >&2
cp "${TMPDIR}"/Dockerfile config/agent-build/Dockerfile

echo "- Update config/agent-build/agents/" >&2
rm -rf config/agent-build/agents/
cp -r "${TMPDIR}"/agents config/agent-build/

echo "Done syncing" >&2