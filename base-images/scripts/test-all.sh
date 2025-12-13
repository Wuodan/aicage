#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"
BATS_ARGS=()

die() {
  echo "[base-test-all] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/test-all.sh [options] [-- <bats-args>]

Runs smoke tests for every base image. Image references are derived from repository/version values.
Bats args after -- are forwarded to each base-images/scripts/test.sh invocation.

Options:
  -h, --help      Show this help and exit

Examples:
  base-images/scripts/test-all.sh
  base-images/scripts/test-all.sh -- --filter base
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
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
}

main() {
  parse_args "$@"
  load_env_file

  local repository="${AICAGE_BASE_REPOSITORY}"
  local version="${AICAGE_VERSION}"

  for base_dir in "${BASE_DIR}/bases"/*; do
    base_alias="$(basename "${base_dir}")"
    local image="${repository}:${base_alias}-${version}"
    echo "[base-test-all] Testing ${image}" >&2
    "${BASE_DIR}/scripts/test.sh" --image "${image}" -- "${BATS_ARGS[@]}"
  done
}

main "$@"
