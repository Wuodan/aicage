#!/usr/bin/env bash
set -euo pipefail

if command -v cosign >/dev/null 2>&1; then
  echo "cosign already installed"
  exit
fi

echo "Installing cosign ..."

ARCH=$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
curl -fsSLo cosign "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-${ARCH}"
install -m 0755 cosign /usr/local/bin/cosign
rm cosign

echo "Done installing cosign"