#!/usr/bin/env bash
set -euo pipefail

if ! command -v dnf >/dev/null; then
  echo "Unsupported base image for aicage; dnf required" >&2
  exit 1
fi

dnf -y makecache
dnf -y group install development-tools
dnf -y install \
  bash \
  bash-completion \
  ca-certificates \
  curl \
  git \
  gnupg2 \
  jq \
  nano \
  openssh-clients \
  pipx \
  python3 \
  python3-pip \
  python3-virtualenv \
  ripgrep \
  tar \
  tini \
  unzip \
  xz \
  zip \
  glibc-langpack-en \
  glibc-locale-source \
  shadow-utils
dnf clean all

localedef -i en_US -f UTF-8 /usr/lib/locale/en_US.UTF-8

if ! command -v gosu >/dev/null 2>&1; then
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) ARCH="amd64" ;;
    aarch64) ARCH="arm64" ;;
    *)
      echo "Unsupported architecture for gosu: $ARCH" >&2
      exit 1
      ;;
  esac

  GOSU_VERSION="$(curl -fsSL https://api.github.com/repos/tianon/gosu/releases/latest | jq -r '.tag_name')"
  url="https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-${ARCH}"
  curl -fsSL "${url}" -o /usr/local/bin/gosu
  chmod +x /usr/local/bin/gosu
fi
