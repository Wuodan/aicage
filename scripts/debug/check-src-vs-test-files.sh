#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="${1:-src}"
TESTS_DIR="${2:-tests}"
had_errors=0

for module_path in $(find "${SRC_DIR}" -type f -name '*.py' -not -path '*/.venv/*'); do
  module_dir="$(dirname "${module_path}")"
  module_name="$(basename "${module_path}")"

  # Filter out known exceptions
  [[ "${module_name}" == '__init__.py' || "${module_name}" == '__main__.py' ]] && continue

  test_dir="${module_dir/#$SRC_DIR\//$TESTS_DIR/}"
  test_path="${test_dir}/test_${module_name}"
  # Remove leading `_` from module_name, search with wildcard
  test_path_wrong="${test_dir}/test+(_)${module_name#_}"

  if [[ ! -f "${test_path}" ]]; then
    echo "${module_path} misses test ${test_path}"
    had_errors=1
    shopt -s extglob
    if compgen -G "$test_path_wrong" > /dev/null; then
      echo "  -> test file seems to exist at: $(compgen -G "$test_path_wrong")"
      # git mv $(compgen -G "$test_path_wrong") "${test_path}"
    fi
    shopt -u extglob
  fi
done

if [[ "${had_errors}" -ne 0 ]]; then
  echo
  echo "Found problems, exiting with error 1" >&2
  exit 1
fi