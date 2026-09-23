#!/usr/bin/env bash
# 实验 03：文件系统隔离
# 目标：只读根 + 唯一可写工作区 /work。
source "$(dirname "$0")/_common.sh"

echo "== 实验 03：文件系统隔离 =="
"${BWRAP_COMMON[@]}" -- sh -c '
  echo "[沙箱] 当前目录: $(pwd)"
  echo "[沙箱] 尝试写 /work:"
  echo "agent-was-here" > /work/note.txt && echo "  -> 成功 (预期)"
  echo "[沙箱] 尝试写 /etc/evil:"
  echo x > /etc/evil 2>/dev/null && echo "  -> 成功 (危险)" || echo "  -> 被拒绝 (预期)"
  echo "[沙箱] 尝试写 /usr/evil:"
  echo x > /usr/evil 2>/dev/null && echo "  -> 成功 (危险)" || echo "  -> 被拒绝 (预期)"
  echo "[沙箱] /home 内容:"; ls -a /home 2>/dev/null || echo "  (无 /home)"
'
echo "---"
echo "宿主侧确认工作区文件已写入:"
ls -l "$WORK/note.txt" 2>/dev/null || echo "(未找到)"
echo "结论：根文件系统只读，仅 /work 与 /tmp 可写。"
