#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_DIR="${ROOT_DIR}/base-images"

die() {
  echo "[build-base] $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: base-images/scripts/build.sh [--base <alias>] [options]

Options:
  --base <value>       Base alias (required; must match a base-images/bases folder)
  --platform <value>   Override platform list (default: env or linux/amd64,linux/arm64)
  --push               Push the image instead of loading it locally
  --version <value>    Override AICAGE_VERSION for this build
  -h, --help           Show this help and exit

Examples:
  base-images/scripts/build.sh --base ubuntu:24.04
  base-images/scripts/build.sh --base ghcr.io/catthehacker/ubuntu:act-latest --platform linux/amd64
USAGE
  exit 1
}

# shellcheck source=../../scripts/common.sh
source "${ROOT_DIR}/scripts/common.sh"

validate_base_settings() {
  [[ -n "${AICAGE_BASE_REPOSITORY:-}" ]] || die "AICAGE_BASE_REPOSITORY is empty."
  [[ -n "${AICAGE_VERSION:-}" ]] || die "AICAGE_VERSION is empty."
  if [[ "${AICAGE_BASE_REPOSITORY}" == "${AICAGE_REPOSITORY}" ]]; then
    die "AICAGE_BASE_REPOSITORY must differ from AICAGE_REPOSITORY to keep base images separate."
  fi
}

parse_args() {
  PLATFORM_OVERRIDE=""
  PUSH_MODE="--load"
  VERSION_OVERRIDE=""
  BASE_ALIAS=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --base)
        [[ $# -ge 2 ]] || die "--base requires a value"
        BASE_ALIAS="$2"
        shift 2
        ;;
      --platform)
        [[ $# -ge 2 ]] || die "--platform requires a value"
        PLATFORM_OVERRIDE="$2"
        shift 2
        ;;
      --push)
        PUSH_MODE="--push"
        shift
        ;;
      --version)
        [[ $# -ge 2 ]] || die "--version requires a value"
        VERSION_OVERRIDE="$2"
        shift 2
        ;;
      -h|--help)
        usage
        ;;
      --)
        shift
        break
        ;;
      *)
        die "Unknown option '$1'"
        ;;
    esac
  done

  if [[ -z "${BASE_ALIAS}" ]]; then
    die "--base is required"
  fi
}

main() {
  parse_args "$@"
  load_env_file
  if [[ -n "${VERSION_OVERRIDE}" ]]; then
    AICAGE_VERSION="${VERSION_OVERRIDE}"
  fi
  validate_base_settings
  # Validate alias by loading its fields directly.
  local base_image
  base_image="$(get_base_field "${BASE_ALIAS}" base_image)"
  local os_installer
  os_installer="$(get_base_field "${BASE_ALIAS}" os_installer)"
  local os_installer_path="${BASE_DIR}/${os_installer}"
  [[ -f "${os_installer_path}" ]] || die "OS installer not found for '${BASE_ALIAS}': ${os_installer}"

  local raw_platforms="${PLATFORM_OVERRIDE:-${AICAGE_PLATFORMS:-${PLATFORMS:-}}}"
  [[ -n "${raw_platforms}" ]] || die "Platform list is empty; set AICAGE_BASE_PLATFORMS or use --platform."
  local platform_list=()
  split_list "${raw_platforms}" platform_list
  [[ ${#platform_list[@]} -gt 0 ]] || die "Platform list is empty; set AICAGE_BASE_PLATFORMS or use --platform."
  local platforms_str="${platform_list[*]}"

  local target="base-${BASE_ALIAS}"
  local version_tag="${AICAGE_BASE_REPOSITORY}:${BASE_ALIAS}-${AICAGE_VERSION}"
  local latest_tag="${AICAGE_BASE_REPOSITORY}:${BASE_ALIAS}-latest"
  local description="Base image for aicage (${BASE_ALIAS})"
  local env_prefix=(
    AICAGE_BASE_REPOSITORY="${AICAGE_BASE_REPOSITORY}"
    AICAGE_VERSION="${AICAGE_VERSION}"
    AICAGE_PLATFORMS="${platforms_str}"
  )

  local cmd=("env" "${env_prefix[@]}" \
    docker buildx bake \
      -f "${BASE_DIR}/docker-bake.hcl" \
      base \
      --set "base.args.BASE_IMAGE=${base_image}" \
      --set "base.args.OS_INSTALLER=${os_installer}" \
      --set "base.tags=${version_tag}" \
      --set "base.tags+=${latest_tag}" \
      --set "base.labels.org.opencontainers.image.description=${description}" \
      "${PUSH_MODE}"
  )

  echo "[build-base] Target=${target} Platforms=${platforms_str} Repo=${AICAGE_BASE_REPOSITORY} Version=${AICAGE_VERSION} UpstreamBase=${base_image} Installer=${os_installer} Tags=${version_tag},${latest_tag} Mode=${PUSH_MODE}" >&2
  "${cmd[@]}"
}

main "$@"
