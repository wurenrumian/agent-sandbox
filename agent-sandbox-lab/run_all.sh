#!/usr/bin/env bash
# 一键运行所有沙箱实验
set -uo pipefail
cd "$(dirname "$0")"

for f in exp/0*.sh; do
  echo "############################################################"
  echo "# $(basename "$f")"
  echo "############################################################"
  bash "$f" || echo "(实验返回非零: $?)"
  echo
done

echo "############################################################"
echo "# 附加：用 sandbox_run.py 运行「Agent 生成的代码」"
echo "############################################################"
python3 sandbox_run.py 'python3 /work/agent_code.py'
