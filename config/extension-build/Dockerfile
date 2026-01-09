ARG BASE_IMAGE=base
FROM ${BASE_IMAGE} AS runtime

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN --mount=type=bind,source=scripts,target=/tmp/aicage/scripts,readonly \
    set -e; \
    shopt -s nullglob; \
    mkdir -p /tmp/aicage/scripts-run; \
    for script in /tmp/aicage/scripts/*.sh; do cp "$script" /tmp/aicage/scripts-run/; done; \
    for script in /tmp/aicage/scripts-run/*.sh; do chmod +x "$script"; "$script"; done; \
    rm -rf /tmp/aicage/scripts-run
