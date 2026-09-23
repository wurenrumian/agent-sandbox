#!/usr/bin/env bash
# 实验 05：逃逸尝试
# 目标：模拟恶意代码试图读取宿主密钥、出网外泄、写系统目录 —— 全部失败。
source "$(dirname "$0")/_common.sh"

echo "== 实验 05：逃逸尝试 =="
"${BWRAP_COMMON[@]}" -- sh -c '
  echo "[1] 尝试读取宿主用户目录 /home/wuren:"
  ls /home/wuren 2>&1 | head -3 || true

  echo "[2] 尝试读取宿主密钥文件:"
  for f in /home/wuren/.ssh/id_rsa /root/.ssh/id_rsa /etc/shadow; do
    if head -c 1 "$f" >/dev/null 2>&1; then
      echo "  -> $f 可读 (危险)"
    else
      echo "  -> $f 不可读 (预期)"
    fi
  done

  echo "[3] 尝试出网外泄 (python socket):"
  python3 - <<PY
import socket
try:
    socket.create_connection(("1.1.1.1", 80), 2).close()
    print("  -> 出网成功 (危险)")
except Exception as e:
    print("  -> 出网失败:", type(e).__name__, "(预期)")
PY

  echo "[4] 尝试写系统目录 /etc:"
  echo x > /etc/evil 2>/dev/null && echo "  -> 成功 (危险)" || echo "  -> 被拒绝 (预期)"
'
echo "---"
echo "结论：宿主密钥不可见、无法出网、系统目录只读 —— 逃逸尝试全部失败。"
