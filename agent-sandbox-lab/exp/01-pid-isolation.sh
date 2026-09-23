#!/usr/bin/env bash
# 实验 01：PID 命名空间隔离
# 目标：证明沙箱内看不到宿主机的进程。
source "$(dirname "$0")/_common.sh"

count_procs() { ls /proc 2>/dev/null | grep -cE '^[0-9]+$'; }

echo "== 实验 01：PID 隔离 =="
echo "[宿主] 可见进程数: $(count_procs)"
echo "[宿主] 前几个进程:"
ps -eo pid,comm 2>/dev/null | head -6 || true
echo "---"
unshare --user --map-root-user --pid --fork --mount-proc --mount -- sh -c '
  n=$(ls /proc | grep -cE "^[0-9]+$")
  echo "[沙箱] 可见进程数: $n"
  echo "[沙箱] 进程列表:"
  ps -eo pid,comm 2>/dev/null | head -6 || ls /proc | grep -E "^[0-9]+$" | head
'
echo "---"
echo "结论：沙箱内 PID 命名空间独立，看不到宿主机进程。"
