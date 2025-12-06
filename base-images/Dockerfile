# syntax=docker/dockerfile:1.7-labs
ARG BASE_IMAGE=ubuntu:24.04
ARG NODEJS_VERSION=20.17.0

FROM ${BASE_IMAGE} AS base

ARG TARGETARCH
ARG NODEJS_VERSION

LABEL org.opencontainers.image.title="aicage-base" \
      org.opencontainers.image.description="Prebuilt base layer for agent images" \
      org.opencontainers.image.source="https://github.com/Wuodan/aicage" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive \
    AGENT_TARGETARCH=${TARGETARCH} \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    AICAGE_USER=aicage \
    AICAGE_UID=1000 \
    AICAGE_GID=1000 \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/opt/pipx/bin \
    PATH="/opt/pipx/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin" \
    NPM_CONFIG_PREFIX=/usr/local

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN --mount=type=bind,source=scripts,target=/tmp/install,readonly \
    /tmp/install/install_os_packages.sh

# Install Node.js 20.x (cline core requires >=20).
RUN --mount=type=bind,source=scripts,target=/tmp/install,readonly \
    /tmp/install/install_node.sh

# Add new base tweaks here (e.g., base-specific packages or config overrides).

RUN --mount=type=bind,source=scripts,target=/tmp/install,readonly \
    /tmp/install/install_python.sh
