#!/usr/bin/env python3
"""把 bwrap 沙箱包装成 MCP server，供 Agent 通过工具调用使用。

依赖：
    pip install mcp

运行：
    python3 code/sandbox_mcp.py

暴露的工具：
    exec(cmd, timeout)      —— 在沙箱内执行 shell 命令
    read_file(path)         —— 读取沙箱工作区文件
    write_file(path, content) —— 写入沙箱工作区文件
    list_files(path)        —— 列出沙箱工作区文件
"""
import os
import sys
from pathlib import Path

# 让本脚本能 import 上级目录的 sandbox_run
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sandbox_run import run, WORK  # noqa: E402

from mcp.server.fastmcp import FastMCP  # noqa: E402

mcp = FastMCP("sandbox")


def _safe_path(path: str) -> Path:
    """确保访问不越出工作区（防目录穿越）。"""
    p = (Path(WORK) / path).resolve()
    root = Path(WORK).resolve()
    if root != p and root not in p.parents:
        raise ValueError(f"path escapes workspace: {path}")
    return p


@mcp.tool()
def exec(cmd: str, timeout: int = 30) -> dict:
    """在沙箱里执行 shell 命令，返回 exit_code / stdout / stderr / elapsed。"""
    return run(cmd, timeout=timeout)


@mcp.tool()
def read_file(path: str) -> str:
    """读取沙箱工作区里的文件。"""
    return _safe_path(path).read_text()


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """写入沙箱工作区里的文件（自动创建父目录）。"""
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"written {len(content)} bytes to {path}"


@mcp.tool()
def list_files(path: str = ".") -> list[str]:
    """列出沙箱工作区里的文件。"""
    p = _safe_path(path)
    return sorted(x.name for x in p.iterdir())


if __name__ == "__main__":
    mcp.run()
