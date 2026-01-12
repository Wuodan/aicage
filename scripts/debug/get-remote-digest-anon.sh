#!/usr/bin/env bash
set -euo pipefail

# get-remote-digest-anon.sh
#
# Goal: Given a full image ref (name[:tag] or name@sha256:...), print the REMOTE digest.
# Covers:
#   - Anonymous registries (no auth needed)
#   - Bearer-token registries where the token can be fetched anonymously (Docker Hub, GHCR public, Quay public, many others)
# Intentionally NOT covered:
#   - Registries that require real credentials (Basic or Bearer-with-creds)
#
# Usage:
#   ./get-remote-digest-anon.sh ubuntu:latest
#   ./get-remote-digest-anon.sh docker.io/library/ubuntu:latest
#   ./get-remote-digest-anon.sh ghcr.io/rblaine95/debian:latest

IMAGE_REF="${1:-}"
if [[ -z "${IMAGE_REF}" ]]; then
  echo "Usage: $0 <image-ref>" >&2
  exit 2
fi

# If already pinned by digest, just echo it.
if [[ "${IMAGE_REF}" == *@sha256:* ]]; then
  echo "${IMAGE_REF##*@}"
  exit 0
fi

DEFAULT_REGISTRY="registry-1.docker.io"

# Parse out tag (default: latest)
ref="${IMAGE_REF}"
tag="latest"

# Split on last ":" in the last path segment (so host:port stays intact)
last_segment="${ref##*/}"
if [[ "${last_segment}" == *:* ]]; then
  tag="${last_segment##*:}"
  ref="${ref%:*}"
fi

# Determine registry vs repo
first="${ref%%/*}"
if [[ "${ref}" == */* && ( "${first}" == *.* || "${first}" == *:* || "${first}" == "localhost" ) ]]; then
  registry="${first}"
  repo="${ref#*/}"
else
  registry="${DEFAULT_REGISTRY}"
  repo="${ref}"
fi

# Docker Hub normalization
if [[ "${registry}" == "docker.io" || "${registry}" == "index.docker.io" ]]; then
  registry="${DEFAULT_REGISTRY}"
fi
if [[ "${registry}" == "${DEFAULT_REGISTRY}" && "${repo}" != */* ]]; then
  repo="library/${repo}"
fi

accept="application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json"
manifest_url="https://${registry}/v2/${repo}/manifests/${tag}"

extract_digest() {
  tr -d '\r' | grep -i '^docker-content-digest:' | head -n1 | cut -d' ' -f2
}

# 1) Try anonymous HEAD directly to the manifest endpoint.
set +e
anon_headers="$(curl -fsSIL -H "Accept: ${accept}" "${manifest_url}" 2>/dev/null)"
anon_rc=$?
set -e
if [[ $anon_rc -eq 0 ]]; then
  digest="$(printf '%s\n' "${anon_headers}" | extract_digest || true)"
  if [[ -n "${digest}" ]]; then
    echo "${digest}"
    exit 0
  fi
fi

# 2) If unauthorized, discover auth challenge (prefer manifest endpoint; fallback /v2/)
get_www_auth() {
  local h
  set +e
  h="$(curl -sSIL -H "Accept: ${accept}" "${manifest_url}" | tr -d '\r')"
  set -e
  printf '%s\n' "$h" | grep -i '^www-authenticate:' | head -n1 || true
}

www_auth="$(get_www_auth)"
if [[ -z "${www_auth}" ]]; then
  set +e
  v2h="$(curl -sSIL "https://${registry}/v2/" | tr -d '\r')"
  set -e
  www_auth="$(printf '%s\n' "$v2h" | grep -i '^www-authenticate:' | head -n1 || true)"
fi

if [[ -z "${www_auth}" ]]; then
  echo "ERROR: Could not determine auth method (no WWW-Authenticate)." >&2
  exit 1
fi

www_auth_lc="$(printf '%s' "${www_auth}" | tr '[:upper:]' '[:lower:]')"
if [[ "${www_auth_lc}" != www-authenticate:\ bearer* ]]; then
  echo "ERROR: Registry does not support anonymous Bearer flow (challenge: ${www_auth})" >&2
  exit 3
fi

# Parse Bearer challenge params: realm="...", service="...", scope="..."
get_param() {
  local key="$1"
  printf '%s' "${www_auth}" | sed -nE "s/.*${key}=\"([^\"]+)\".*/\1/p"
}
realm="$(get_param realm)"
service="$(get_param service)"
scope_from_challenge="$(get_param scope)"

if [[ -z "${realm}" ]]; then
  echo "ERROR: Bearer auth advertised but no realm provided." >&2
  exit 1
fi

# Scope handling varies:
# - Some registries include scope in the challenge. Use it if present.
# - Otherwise, request the standard pull scope for this repo.
scope="${scope_from_challenge:-repository:${repo}:pull}"

# Build token URL. Some realms may already include query params, so append with & if needed.
sep='?'
if [[ "${realm}" == *\?* ]]; then sep='&'; fi

token_url="${realm}${sep}scope=${scope}"
if [[ -n "${service}" ]]; then
  # token services typically require the service parameter
  token_url="${realm}${sep}service=${service}&scope=${scope}"
fi

# Fetch token anonymously; support both .token and .access_token
token_json="$(curl -fsSL "${token_url}")"
token="$(printf '%s' "${token_json}" | jq -r '.token // .access_token // empty')"
if [[ -z "${token}" || "${token}" == "null" ]]; then
  echo "ERROR: Failed to obtain anonymous Bearer token from ${token_url}" >&2
  exit 1
fi

# 3) HEAD again with the Bearer token to get Docker-Content-Digest
auth_headers="$(curl -fsSIL \
  -H "Accept: ${accept}" \
  -H "Authorization: Bearer ${token}" \
  "${manifest_url}" \
  | tr -d '\r'
)"

digest="$(printf '%s\n' "${auth_headers}" | extract_digest || true)"
if [[ -z "${digest}" ]]; then
  echo "ERROR: Auth succeeded but no Docker-Content-Digest returned." >&2
  exit 1
fi

echo "${digest}"
