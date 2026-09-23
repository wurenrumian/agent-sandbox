---
title: "配套代码"
description: "沙箱执行包装器与 MCP server 示例。"
---

> 沙箱的最小实现与 MCP 封装。最后更新：2026-09-23


## 文件说明

| 文件 | 说明 |
|---|---|
| [`../sandbox_run.py`](https://github.com/wurenrumian/agent-sandbox/blob/main/agent-sandbox-lab/sandbox_run.py) | 沙箱执行包装器（bwrap），**最核心的一个文件** |
| [`sandbox_mcp.py`](https://github.com/wurenrumian/agent-sandbox/blob/main/agent-sandbox-lab/code/sandbox_mcp.py) | 把沙箱包成 MCP server，暴露 `exec / read_file / write_file / list_files` |

---

## 1. 试运行 sandbox_run.py

```bash
cd ..                       # 进入 agent-sandbox-lab
./sandbox_run.py 'echo hello; id; ls /'
./sandbox_run.py 'python3 /work/agent_code.py'
```

也可以作为库调用：

```python
from sandbox_run import run

result = run("python3 /work/agent_code.py", timeout=30)
print(result["exit_code"])
print(result["stdout"])
```

返回结构：

```python
{
    "exit_code": 0,
    "stdout": "...",
    "stderr": "...",
    "elapsed": 0.123,   # 秒
}
```

---

## 2. 试运行 MCP server

```bash
pip install mcp
python3 sandbox_mcp.py
```

在支持 MCP 的客户端（如 Claude Desktop、各类 Agent 框架）里把它配置为 server：

```json
{
  "mcpServers": {
    "sandbox": {
      "command": "python3",
      "args": ["/home/wuren/sandbox/agent-sandbox-lab/code/sandbox_mcp.py"]
    }
  }
}
```

配置后，Agent 就能调用这些工具：

| 工具 | 作用 |
|---|---|
| `exec(cmd, timeout)` | 在沙箱内执行 shell 命令 |
| `read_file(path)` | 读取工作区文件 |
| `write_file(path, content)` | 写入工作区文件 |
| `list_files(path)` | 列出工作区文件 |

---

## 3. 安全设计

`sandbox_mcp.py` 里做了**目录穿越防护**（`_safe_path`）：

```python
def _safe_path(path: str) -> Path:
    p = (Path(WORK) / path).resolve()
    root = Path(WORK).resolve()
    if root != p and root not in p.parents:
        raise ValueError(f"path escapes workspace: {path}")
    return p
```

防止 Agent 用 `../../etc/passwd` 之类的方式逃出工作区。

---

## 注意

- 这是**教学实现**。生产环境请替换为 microVM 隔离 + 出网白名单 + 短期凭据。
- `sandbox_run.py` 使用 `--clearenv`，沙箱内默认没有你的环境变量；需要时用 `run(..., env={"K": "V"})` 显式注入。
- 沙箱内工作区映射为 `/work`，宿主侧对应 `agent-sandbox-lab/work/`。
