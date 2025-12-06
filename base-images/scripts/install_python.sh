#!/usr/bin/env bash
set -euo pipefail

: "${PIPX_HOME:?PIPX_HOME is required}"
: "${PIPX_BIN_DIR:?PIPX_BIN_DIR is required}"

python3 -m pip install --break-system-packages --ignore-installed --upgrade pip setuptools wheel

mkdir -p "${PIPX_HOME}" "${PIPX_BIN_DIR}"
PIPX_HOME=${PIPX_HOME} PIPX_BIN_DIR=${PIPX_BIN_DIR} pipx ensurepath

PIP_NO_CACHE_DIR=1 \
  PIPX_HOME=${PIPX_HOME} \
  PIPX_BIN_DIR=${PIPX_BIN_DIR} \
  pipx install uv \
    --pip-args="--no-cache-dir"
