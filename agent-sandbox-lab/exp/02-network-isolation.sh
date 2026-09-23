#!/usr/bin/env bash
# 实验 02：网络命名空间隔离
# 目标：证明沙箱默认没有网络，无法外泄数据。
source "$(dirname "$0")/_common.sh"

echo "== 实验 02：网络隔离 =="

echo "[宿主] 尝试连接 1.1.1.1:80"
python3 - <<'PY' || echo "[宿主] 连接失败（宿主本身可能无外网）"
import socket
try:
    socket.create_connection(("1.1.1.1", 80), 3).close()
    print("[宿主] 连接成功 -> 宿主有网络")
except Exception as e:
    print("[宿主] 连接失败:", type(e).__name__)
PY

echo "---"
unshare --user --map-root-user --net -- python3 - <<'PY'
import socket
try:
    socket.create_connection(("1.1.1.1", 80), 3).close()
    print("[沙箱] 连接成功 (危险，不该发生)")
except Exception as e:
    print("[沙箱] 连接失败 -> 已隔离:", type(e).__name__)
PY

echo "---"
echo "结论：沙箱处于独立网络命名空间，只有 lo，默认无法出网。"
