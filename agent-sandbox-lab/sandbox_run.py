#!/usr/bin/env python3
"""用 bubblewrap 在隔离沙箱里执行命令 —— Agent 沙箱的最小实现。

隔离手段：
  --unshare-all   用户 / IPC / PID / 网络 / UTS / cgroup 命名空间全部隔离
  --die-with-parent  父进程退出时沙箱一并结束
  --ro-bind       只读挂载系统目录（/usr、/etc）
  --bind          /work 为唯一可写工作区
  --tmpfs /tmp    临时可写目录
  --clearenv      清空环境变量，避免泄漏宿主凭据
"""
import os
import shutil
import subprocess
import sys
import time

WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")

BWRAP = [
    "bwrap",
    "--unshare-all",
    "--die-with-parent",
    # 只读挂载最小系统目录
    "--ro-bind", "/usr", "/usr",
    "--ro-bind", "/etc", "/etc",
    # 屏蔽敏感文件（用 /dev/null 覆盖）
    "--ro-bind", "/dev/null", "/etc/shadow",
    "--symlink", "usr/bin", "/bin",
    "--symlink", "usr/sbin", "/sbin",
    "--symlink", "usr/lib", "/lib",
    "--symlink", "usr/lib64", "/lib64",
    # 伪文件系统
    "--proc", "/proc",
    "--dev", "/dev",
    "--tmpfs", "/tmp",
    # 唯一可写工作区
    "--bind", WORK, "/work",
    "--chdir", "/work",
    # 干净环境
    "--clearenv",
    "--setenv", "PATH", "/usr/bin:/usr/sbin:/bin:/sbin",
    "--setenv", "HOME", "/work",
    "--setenv", "LANG", "C.UTF-8",
]


def run(cmd: str, timeout: int = 30, env: dict | None = None) -> dict:
    """在沙箱中执行 shell 命令，返回结构化结果。"""
    if shutil.which("bwrap") is None:
        return {
            "exit_code": 127,
            "stdout": "",
            "stderr": (
                "未找到 bwrap。请先安装 bubblewrap：\n"
                "  Fedora:  sudo dnf install bubblewrap\n"
                "  Debian:  sudo apt install bubblewrap\n"
                "  Arch:    sudo pacman -S bubblewrap"
            ),
            "elapsed": 0.0,
        }

    argv = list(BWRAP)
    for k, v in (env or {}).items():
        argv += ["--setenv", k, v]
    argv += ["--", "sh", "-lc", cmd]

    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return {
            "exit_code": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "elapsed": round(time.time() - t0, 3),
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"timeout after {timeout}s",
            "elapsed": timeout,
        }


if __name__ == "__main__":
    command = " ".join(sys.argv[1:]) or "echo 'hello from sandbox'; id"
    result = run(command)
    sys.stdout.write(result["stdout"])
    if result["stderr"]:
        sys.stderr.write(result["stderr"])
    sys.exit(result["exit_code"] if result["exit_code"] >= 0 else 1)
