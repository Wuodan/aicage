#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt-get >/dev/null; then
  echo "Unsupported base image for aicage; apt-get required" >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends \
  bash \
  bash-completion \
  build-essential \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  locales \
  nano \
  openssh-client \
  pipx \
  python3 \
  python3-pip \
  python3-venv \
  gosu \
  ripgrep \
  tar \
  tini \
  unzip \
  xz-utils \
  zip
rm -rf /var/lib/apt/lists/*

locale-gen en_US.UTF-8
