#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"
SMOKE_DIR="${BASE_DIR}/tests/smoke"
BATS_ARGS=()
IMAGE_REF=""

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/test.sh --image <image-ref> [-- <bats-args>]

Options:
  -h, --help      Show this help and exit

Examples:
  base-images/scripts/test.sh --image wuodan/aicage-base:ubuntu-base-dev
  base-images/scripts/test.sh --image wuodan/aicage-base:act-base-dev -- --filter base
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

log() {
  printf '[base-test] %s\n' "$*" >&2
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
  log "Running base smoke tests via bats"
  AICAGE_BASE_IMAGE="${IMAGE_REF}" bats "${SMOKE_DIR}" "${BATS_ARGS[@]}"
}

parse_args "$@"
run_tests
