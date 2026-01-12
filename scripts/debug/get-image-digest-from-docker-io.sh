#!/usr/bin/env bash
set -euo pipefail

IMAGE="php:latest"   # change me

REPO="${IMAGE%%:*}"
TAG="${IMAGE##*:}"

TOKEN="$(curl -fsSL \
  "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/${REPO}:pull" \
  | jq -r .token)"

RAW="$(
  curl -fsSL -I \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.docker.distribution.manifest.list.v2+json" \
    "https://registry-1.docker.io/v2/library/${REPO}/manifests/${TAG}"
)"
DIGEST="$(
  echo "${RAW}" \
  | tr -d '\r' \
  | grep -i '^docker-content-digest:' \
  | cut -d' ' -f2
)"

echo "${IMAGE} -> ${DIGEST}"

echo "Raw curl result:"
echo "${RAW}"
