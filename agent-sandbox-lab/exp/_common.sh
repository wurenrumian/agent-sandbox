#!/usr/bin/env bash
# 公共 bwrap 参数与路径（被 exp/*.sh 引用）
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT_DIR/work"
mkdir -p "$WORK"

BWRAP_COMMON=(
  bwrap --unshare-all --die-with-parent
  --ro-bind /usr /usr
  --ro-bind /etc /etc
  --ro-bind /dev/null /etc/shadow
  --symlink usr/bin /bin
  --symlink usr/sbin /sbin
  --symlink usr/lib /lib
  --symlink usr/lib64 /lib64
  --proc /proc
  --dev /dev
  --tmpfs /tmp
  --bind "$WORK" /work
  --chdir /work
  --setenv HOME /work
)
