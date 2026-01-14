# check=skip=InvalidDefaultArgInFrom

# ## Installation reduced to aicage builtin base-images ##
#
# Download os-installer scripts from `aicage-image-base` and run a reduced set of them
#
# Simply set this variable below to match a folder in:
# https://github.com/aicage/aicage-image-base/tree/main/scripts/os-installers/distro

ARG AICAGE_INSTALL_DISTRO=debian

ARG FROM_IMAGE

FROM ${FROM_IMAGE} AS from_image

ARG AICAGE_INSTALL_DISTRO

ENV DEBIAN_FRONTEND=noninteractive \
    AICAGE_USER=aicage \
    AICAGE_UID=1000 \
    AICAGE_GID=1000 \
    AICAGE_WORKSPACE=/workspace \
    NPM_CONFIG_PREFIX=/usr/local \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/opt/pipx/bin \
    PATH="/opt/pipx/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"

RUN echo "Setup: Install minimal requirements for aicage entrypoint ..." && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      bash \
      gosu \
      tini

RUN echo "Setup: Install minimal set of tools used below and in scripts ..." && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      gnupg \
      jq \
      tar \
      xz-utils

ARG AICAGE_IMAGE_BASE_DIR=/tmp/aicage-image-base

RUN --mount=type=bind,source=helpers,target=/tmp/aicage/helpers,readonly \
    echo "Setup: Downloading installation scripts from 'github.com/aicage/aicage-image-base' ..." && \
    /tmp/aicage/helpers/install-cosign.sh && \
    /tmp/aicage/helpers/get-aicage-release-artifact.sh aicage-image-base "${AICAGE_IMAGE_BASE_DIR}" && \
    echo "Install: Running os-installer scripts ..."

# Install npm to install coding agents (most need node with npm)
# This example uses the installation scripts from aicage-image-base
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/generic/install_node.sh

# Recommended: Install Python
# Coding agents like using Python for their tasks
# Some MCP-servers are setup with (uvx)
RUN "${AICAGE_IMAGE_BASE_DIR}/os-installers/distro/${AICAGE_INSTALL_DISTRO}/install/20-python.sh"

# Optional: Install Docker CLI and build essentials
# Needed if you want to use docker from inside the containers
RUN "${AICAGE_IMAGE_BASE_DIR}/os-installers/distro/${AICAGE_INSTALL_DISTRO}/install/40-docker.sh"

# Copy aicage entrypoint.sh
RUN echo "Install: Copy aicage entrypoint.sh ..." && \
    cp "${AICAGE_IMAGE_BASE_DIR}"/entrypoint.sh /usr/local/bin/entrypoint.sh

# Clean up apt and installation scripts from aicage-image-base
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf "${AICAGE_IMAGE_BASE_DIR}"

ENV AICAGE_ENTRYPOINT_CMD=bash

# Use tini and aicage entrypoint.sh
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
