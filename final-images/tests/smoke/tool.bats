#!/usr/bin/env bats

setup() {
  TOOL="$(docker inspect --format '{{index .Config.Cmd 0}}' "${AICAGE_IMAGE}")"
  if [[ -z "${TOOL}" ]]; then
    echo "Could not determine tool name from image ${AICAGE_IMAGE}" >&2
    exit 1
  fi
}

@test "test_boots_container" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc "echo ${TOOL}-boot && whoami"
  [ "$status" -eq 0 ]
  [[ "$output" == *"${TOOL}-boot"* ]]
}

@test "test_agent_binary_present" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc "command -v ${TOOL}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"${TOOL}"* ]]
}

@test "test_required_packages" {
  run docker run --rm "${AICAGE_IMAGE}" /bin/bash -lc \
    "git --version >/dev/null && python3 --version >/dev/null && node --version >/dev/null && npm --version >/dev/null"
  [ "$status" -eq 0 ]
}
