#!/usr/bin/env bash
set -euo pipefail

IMAGE="php:latest"   # change me

REPO="${IMAGE%%:*}"
TAG="${IMAGE##*:}"

TOKEN="$(curl -fsSL \
  "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/${REPO}:pull" \
  | jq -r .token)"

DIGEST="$(curl -fsSL -I \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.docker.distribution.manifest.list.v2+json" \
  "https://registry-1.docker.io/v2/library/${REPO}/manifests/${TAG}" \
  | tr -d '\r' \
  | awk -F': ' 'tolower($1)=="docker-content-digest"{print $2}')"

echo "${IMAGE} -> ${DIGEST}"
