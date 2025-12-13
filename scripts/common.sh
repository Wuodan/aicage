#!/usr/bin/env bash
set -euo pipefail

BASE_DEFINITIONS_DIR="${ROOT_DIR}/base-images/bases"

_die() {
  if command -v die >/dev/null 2>&1; then
    die "$@"
  else
    echo "[common] $*" >&2
    exit 1
  fi
}

contains() {
  local needle=$1; shift
  local item
  for item in "$@"; do
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

load_env_file() {
  local env_file="${ROOT_DIR}/.env"

  # The read condition handles files that omit a trailing newline.
  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
    if [[ "${line}" =~ ^([^=]+)=(.*)$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local value="${BASH_REMATCH[2]}"
      if [[ -z ${!key+x} ]]; then
        if [[ "${value}" =~ ^\".*\"$ ]]; then
          value="${value:1:${#value}-2}"
        fi
        export "${key}=${value}"
      fi
    fi
  done < "${env_file}"
}

split_list() {
  local raw="$1"
  local -n out=$2
  read -r -a out <<< "${raw}"
}

get_base_field() {
  local alias="$1"
  local field="$2"
  local base_dir="${BASE_DEFINITIONS_DIR}/${alias}"
  local definition_file="${base_dir}/base.yaml"

  [[ -d "${base_dir}" ]] || _die "Base alias '${alias}' not found under ${BASE_DEFINITIONS_DIR}"
  [[ -f "${definition_file}" ]] || _die "Missing base.yaml for '${alias}'"

  local value
  value="$(yq -er ".${field}" "${definition_file}")" || _die "Failed to read ${field} from ${definition_file}"
  [[ -n "${value}" && "${value}" != "null" ]] || _die "${field} missing in ${definition_file}"
  printf '%s\n' "${value}"
}
