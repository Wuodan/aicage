# check=skip=InvalidDefaultArgInFrom
ARG FROM_IMAGE

FROM ${FROM_IMAGE} AS from_image

ENV DEBIAN_FRONTEND=noninteractive \
    NPM_CONFIG_PREFIX=/usr/local \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/opt/pipx/bin \
    PATH="/opt/pipx/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"

# Install minimal requirements for aicage entrypoint
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      bash \
      gosu \
      tini

# Install minimal set of tools used below and in scripts
RUN apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      jq \
      tar \
      xz-utils

ARG AICAGE_IMAGE_BASE_DIR=/tmp/aicage-image-base

# Download installation scripts from aicage-image-base
RUN mkdir -p "${AICAGE_IMAGE_BASE_DIR}" && \
    curl -fsSL \
      https://github.com/aicage/aicage-image-base/releases/latest/download/os-installers.tar.gz \
      -o "${AICAGE_IMAGE_BASE_DIR}/os-installers.tar.gz" && \
    tar -xzf "${AICAGE_IMAGE_BASE_DIR}/os-installers.tar.gz" -C "${AICAGE_IMAGE_BASE_DIR}"

# Install npm to install coding agents (most need node with npm)
# This example uses the installation scripts from aicage-image-base
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/generic/install_node.sh

# Recommended: Install Python
# Coding agents like using Python for their tasks
# Some MCP-servers are setup with (uvx)
# (assuming a Debian distro here, this includes Ubuntu)
RUN apt-get install -y --no-install-recommends \
      gnupg && \
    "${AICAGE_IMAGE_BASE_DIR}"/os-installers/distro/debian/install/20-python.sh

# Optional: Install Docker CLI and build essentials
# Needed if you want to use docker from inside the containers
# (assuming a Debian distro here, this includes Ubuntu)
RUN apt-get install -y --no-install-recommends \
      gnupg && \
    "${AICAGE_IMAGE_BASE_DIR}"/os-installers/distro/debian/install/40-docker.sh

# Clean up apt
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clean up installation scripts from aicage-image-base
RUN rm -rf "${AICAGE_IMAGE_BASE_DIR}"

# Copy aicage entrypoint.sh
RUN curl -fsSL \
      https://github.com/aicage/aicage-image-base/releases/latest/download/entrypoint.sh \
      -o /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Use tini and aicage entrypoint.sh
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
