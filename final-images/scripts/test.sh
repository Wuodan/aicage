#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SMOKE_DIR="${ROOT_DIR}/final-images/tests/smoke"
BATS_ARGS=()
IMAGE_REF=""
BATS_TOOL_FILE="${SMOKE_DIR}/tool.bats"

usage() {
  cat <<'USAGE'
Usage: final-images/scripts/test.sh --image <image-ref> [options] [-- <bats-args>]

Options:
  --image <ref>   Image reference to test (required)
  -h, --help      Show this help and exit

Examples:
  final-images/scripts/test.sh --image example/aicage:codex-ubuntu-24.04-latest
USAGE
  exit 1
}

log() {
  printf '[test] %s\n' "$*" >&2
}

require_cmd() {
  local bin=$1
  if ! command -v "$bin" >/dev/null 2>&1; then
    log "Missing dependency: $bin"
    if [[ "$bin" == "bats" ]]; then
      log "Install via 'npm install -g bats' or 'brew install bats-core'."
    fi
    exit 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --image)
        [[ $# -ge 2 ]] || usage
        IMAGE_REF="$2"
        shift 2
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        BATS_ARGS=("$@")
        break
        ;;
      *)
        usage
        ;;
    esac
  done

  if [[ -z "${IMAGE_REF}" ]]; then
    log "--image is required"
    usage
  fi
}

run_tests() {
  require_cmd docker
  require_cmd bats

  if [[ ! -e "${BATS_TOOL_FILE}" ]]; then
    log "Smoke tests not found at ${BATS_TOOL_FILE}."
    exit 1
  fi

  log "Running smoke tests via bats"
  AICAGE_IMAGE="${IMAGE_REF}" bats "${BATS_TOOL_FILE}" "${BATS_ARGS[@]}"
}

parse_args "$@"
run_tests
