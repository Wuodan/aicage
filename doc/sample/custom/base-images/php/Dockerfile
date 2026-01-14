# check=skip=InvalidDefaultArgInFrom
ARG FROM_IMAGE

FROM ${FROM_IMAGE} AS from_image

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

RUN echo "Setup: Install cosign ..." && \
    mkdir -p "${AICAGE_IMAGE_BASE_DIR}" && \
    cd "${AICAGE_IMAGE_BASE_DIR}" && \
    arch=$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/') && \
    curl -fsSLo cosign "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-${arch}" && \
    install -m 0755 cosign /usr/local/bin/cosign && \
    rm cosign

RUN echo "Setup: Downloading installation scripts from 'github.com/aicage/aicage-image-base' ..." && \
    cd "${AICAGE_IMAGE_BASE_DIR}" && \
    for artifact in aicage-image-base.tar.gz SHA256SUMS SHA256SUMS.sigstore.json; do \
      curl -fsSLO https://github.com/aicage/aicage-image-base/releases/latest/download/${artifact}; \
    done

RUN echo "Setup: Verifying signature and checksums ..." && \
    cd "${AICAGE_IMAGE_BASE_DIR}" && \
    cosign verify-blob \
      --bundle SHA256SUMS.sigstore.json \
      --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
      --certificate-identity-regexp '^https://github\.com/aicage/aicage-image-base/\.github/workflows/release\.yml@refs/tags/.*$' \
      SHA256SUMS && \
    sha256sum -c SHA256SUMS

RUN echo "Setup: Unpacking ..." && \
    cd "${AICAGE_IMAGE_BASE_DIR}" && \
    tar -xzf aicage-image-base.tar.gz && \
    echo "Install: Running os-installer scripts ..."

# Install npm to install coding agents (most need node with npm)
# This example uses the installation scripts from aicage-image-base
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/generic/install_node.sh

# Recommended: Install Python
# Coding agents like using Python for their tasks
# Some MCP-servers are setup with (uvx)
# (assuming a Debian distro here, this includes Ubuntu)
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/distro/debian/install/20-python.sh

# Optional: Install Docker CLI and build essentials
# Needed if you want to use docker from inside the containers
# (assuming a Debian distro here, this includes Ubuntu)
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/distro/debian/install/40-docker.sh

# Copy aicage entrypoint.sh
RUN echo "Install: Copy aicage entrypoint.sh ..." && \
    cp "${AICAGE_IMAGE_BASE_DIR}"/os-installers/entrypoint.sh /usr/local/bin/entrypoint.sh

# Clean up apt and installation scripts from aicage-image-base
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf "${AICAGE_IMAGE_BASE_DIR}"

ENV AICAGE_ENTRYPOINT_CMD=bash

# Use tini and aicage entrypoint.sh
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
