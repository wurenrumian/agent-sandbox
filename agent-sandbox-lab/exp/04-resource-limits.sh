#!/usr/bin/env bash
# 实验 04：资源限额
# 目标：内存与进程数受限，防止资源滥用。
source "$(dirname "$0")/_common.sh"

echo "== 实验 04：资源限额 =="

echo "[限额] 地址空间上限 200MB，尝试分配 300MB:"
sh -c 'ulimit -v 204800; python3 - <<PY
try:
    a = bytearray(300 * 1024 * 1024)
    print("  -> 分配成功 (危险，限额未生效)")
except MemoryError:
    print("  -> 被拒绝: MemoryError (预期)")
PY'

echo "[限额] 当前进程数上限 (ulimit -u): $(ulimit -u)"
echo "  说明：RLIMIT_NPROC 按用户全局统计，直接调低会误伤宿主；"
echo "        生产中更精确的做法是用 cgroup 的 pids.max。"

echo "[限额] 文件大小上限 1MB，尝试写 2MB:"
sh -c 'ulimit -f 1024; head -c 2097152 /dev/zero > /tmp/big 2>/dev/null && echo "  -> 写入成功 (危险)" || echo "  -> 被截断/拒绝 (预期)"'

echo "---"
echo "结论：ulimit / cgroup 可在沙箱层限制内存、进程数、磁盘写入。"
