ARG FROM_IMAGE

FROM ${FROM_IMAGE} AS from_image

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/pipx/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin" \
    NPM_CONFIG_PREFIX=/usr/local

# Install minimal requirements for aicage entrypoint plus curl and tar
RUN apt-get install -y --no-install-recommends \
      bash \
      curl \
      gosu \
      tini

# Install curl and tar, used below and in scripts
RUN apt-get install -y --no-install-recommends \
      curl \
      tar

ARG AICAGE_IMAGE_BASE_DIR=/tmp/aicage-image-base

# Download installation scripts from aicage-image-base
RUN mkdir -p "${AICAGE_IMAGE_BASE_DIR}" && \
    curl -fsSL \
      https://github.com/aicage-image-base/releases/latest/download/os-installers.tar.gz \
      -o "${AICAGE_IMAGE_BASE_DIR}/os-installers.tar.gz" && \
    tar -xzf ""${AICAGE_IMAGE_BASE_DIR}/os-installers.tar.gz" -C "${AICAGE_IMAGE_BASE_DIR}"

# Install npm to install coding agents (most need node with npm)
# This example uses the installation scripts from aicage-image-base
RUN "${AICAGE_IMAGE_BASE_DIR}"/os-installers/generic/install_node.sh

# Optional: Install docker
# Needed if you want to use docker from inside the containers
# (assuming a Debian distro here)
RUN apt-get install -y --no-install-recommends \
      ca-certificates \
      gnupg && \
    "${AICAGE_IMAGE_BASE_DIR}"/os-installers/distro/debian/install/40-docker.sh

# Clean up installation scripts from aicage-image-base
RUN rm -rf "${AICAGE_IMAGE_BASE_DIR}"

# Copy aicage entrypoint.sh
RUN curl -fsSL \
      https://github.com/aicage-image-base/releases/latest/download/entrypoint.sh \
      -o /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Use tini and aicage entrypoint.sh
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
