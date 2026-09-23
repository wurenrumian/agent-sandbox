# Agent 沙箱实验

> 用 **Linux namespaces** 和 **bubblewrap（bwrap）** 做的一组真实可跑的沙箱实验。
> 不需要 Docker、不需要 root，普通用户即可运行。最后更新：2026-09-23

[← 返回资料包总入口](../README.md) · 对应教程 [第 9 章：实战搭建](../agent-sandbox-tutorial/09-实战搭建.md)

---

## 这组实验做什么

把「Agent 沙箱」拆成 5 个可独立验证的隔离能力，逐个跑给你看：

- 沙箱内**看不到**宿主机进程
- 沙箱内**默认没有网络**
- 沙箱内**只能写工作区**，系统目录只读
- 沙箱内**资源受限**，无法滥用
- 恶意代码的**逃逸尝试全部失败**

## 环境要求

| 项 | 要求 |
|---|---|
| 系统 | Linux（本实验在 **Fedora Linux 44 WSL2** 上验证通过） |
| 内核 | 支持非特权 user namespace（`/proc/sys/user/max_user_namespaces` > 0） |
| 依赖 | `bwrap`（bubblewrap）、`python3` |
| 可选 | `unshare`（util-linux，实验 01/02 用） |
| 不需要 | Docker、root 权限 |

快速自检：

```bash
unshare --user --map-root-user echo "user-ns OK"
bwrap --unshare-all --ro-bind / / echo "bwrap OK"
```

---

## 目录结构

```
agent-sandbox-lab/
├── README.md                    # 本文件
├── sandbox_run.py               # 可复用的沙箱执行包装器（bwrap）★核心
├── run_all.sh                   # 一键跑所有实验
├── RESULTS.md                   # 实验输出记录（生成）
├── exp/
│   ├── _common.sh               # 公共 bwrap 参数
│   ├── 01-pid-isolation.sh      # PID 隔离
│   ├── 02-network-isolation.sh  # 网络隔离
│   ├── 03-filesystem-isolation.sh  # 文件系统隔离
│   ├── 04-resource-limits.sh    # 资源限额
│   └── 05-escape-attempt.sh     # 逃逸尝试
├── code/
│   ├── README.md
│   └── sandbox_mcp.py           # 把沙箱包成 MCP server
└── work/
    ├── agent_code.py            # 模拟「Agent 生成的代码」
    └── ...                      # 沙箱内可读写工作区（实验产物）
```

---

## 快速开始

```bash
cd agent-sandbox-lab
chmod +x exp/*.sh run_all.sh sandbox_run.py

# 跑单个实验
./exp/01-pid-isolation.sh

# 跑全部并生成记录
./run_all.sh | tee RESULTS.md

# 用包装器执行任意命令（这就是 Agent 沙箱的最小形态）
./sandbox_run.py 'echo hello; id; ls /'
./sandbox_run.py 'python3 /work/agent_code.py'
```

---

## 隔离原理

本实验用到的都是 Linux 原生机制，bwrap 把它们组合起来：

| 机制 | 作用 | 对应参数 |
|---|---|---|
| **user namespace** | 非特权创建隔离环境 | `--unshare-user`（含在 `--unshare-all`） |
| **PID namespace** | 独立进程树，看不到宿主进程 | `--unshare-pid` |
| **mount namespace** | 私有挂载表，只读挂载系统目录 | `--ro-bind` / `--bind` |
| **network namespace** | 独立网络栈，默认只有 `lo` | `--unshare-net` |
| **UTS / IPC / cgroup** | 隔离主机名 / IPC / cgroup 视图 | `--unshare-uts` 等 |
| **tmpfs** | 临时可写目录 | `--tmpfs /tmp` |
| **clearenv** | 清空环境变量，避免泄漏宿主凭据 | `--clearenv` |
| **die-with-parent** | 父进程退出时沙箱一并结束 | `--die-with-parent` |

> `--unshare-all` = 用户 / IPC / PID / 网络 / UTS / cgroup 全部隔离。
> bwrap 默认在沙箱内保持你的 uid；如需在沙箱内成为 root，可加 `--uid 0`（仅在该 namespace 内有效）。

---

## 实验详解

### 实验 01：PID 隔离

**验证**：沙箱内看不到宿主机进程。
**预期**：宿主可见几十个进程，沙箱内只剩个位数。

```bash
./exp/01-pid-isolation.sh
```

实测：宿主 36 个 → 沙箱 4 个。

### 实验 02：网络隔离

**验证**：沙箱默认没有网络，无法外泄数据。
**预期**：宿主可连外网，沙箱连接失败（`OSError`）。

```bash
./exp/02-network-isolation.sh
```

### 实验 03：文件系统隔离

**验证**：只读根 + 唯一可写工作区 `/work`。
**预期**：写 `/work` 成功；写 `/etc`、`/usr` 被拒（Read-only file system）。

```bash
./exp/03-filesystem-isolation.sh
```

### 实验 04：资源限额

**验证**：内存 / 文件大小受限，防资源滥用。
**预期**：分配 300MB（限额 200MB）报 `MemoryError`；写 2MB（限额 1MB）被截断。

```bash
./exp/04-resource-limits.sh
```

> 进程数限制用 `ulimit -u` 会**按用户全局**生效，直接调低会误伤宿主，因此实验只展示当前值并说明生产中应使用 cgroup 的 `pids.max`。

### 实验 05：逃逸尝试

**验证**：模拟恶意代码读宿主密钥、出网外泄、写系统目录。
**预期**：全部失败。

```bash
./exp/05-escape-attempt.sh
```

### 附加：运行「Agent 生成的代码」

`work/agent_code.py` 故意做了 5 件「坏事」，用沙箱跑一遍：

```bash
./sandbox_run.py 'python3 /work/agent_code.py'
```

实测结果：

| 尝试 | 结果 |
|---|---|
| 读环境变量 `API_KEY` | 读不到（`--clearenv`） |
| 读 `/home/wuren`、`/root` | `FileNotFoundError` |
| 读 `/etc/shadow` | `PermissionError`（已被屏蔽） |
| 出网 | `OSError` |
| 写 `/etc` | `OSError` |
| 正常写 `/work/result.txt` | 成功 ✅ |

---

## 自定义实验

想验证别的行为，直接用包装器：

```python
# 你的脚本
from sandbox_run import run

r = run("python3 -c 'print(open(\"/etc/hostname\").read())'")
print(r["exit_code"], r["stdout"], r["stderr"])
```

或用命令行：

```bash
./sandbox_run.py 'ls -la /; echo ---; cat /etc/os-release'
```

常用参数在 [`sandbox_run.py`](sandbox_run.py) 顶部的 `BWRAP` 列表里，可自行增删：

- 想放开某个只读目录 → 加 `--ro-bind /path /path`
- 想再屏蔽一个文件 → 加 `--ro-bind /dev/null /etc/xxx`
- 想调超时 → 命令里传 `timeout=` 或改 `run(..., timeout=60)`

---

## 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| `bwrap: Creating new namespace failed` | 非特权 user namespace 被禁用 | `sudo sysctl -w kernel.unprivileged_userns_clone=1`（Debian 系）；或检查 `/proc/sys/user/max_user_namespaces` |
| `unshare: Operation not permitted` | 同上，或容器内无 CAP_SYS_ADMIN | 在宿主机运行；WSL 需较新内核 |
| `bwrap: Can't bind mount ... /etc/shadow` | 某些发行版无 `/etc/shadow` | 删掉 `_common.sh` / `sandbox_run.py` 里对应的一行 |
| `python3: command not found` | 沙箱内 PATH 未包含 python | 调整 `--setenv PATH` |
| 沙箱内连不上网 | **这是预期行为** | 需要联网时走白名单代理（见教程 9.4） |
| 实验 03 在宿主看不到 `note.txt` | 工作区路径不对 | 确认 `$WORK` 指向 `agent-sandbox-lab/work` |

---

## 局限与生产建议

这是**教学用**的最小沙箱，与生产环境有差距：

| 维度 | 本实验 | 生产建议 |
|---|---|---|
| 隔离强度 | 共享内核的 namespace | microVM / gVisor |
| 网络 | 完全断网 | 白名单出网代理 + 审计 |
| 凭据 | 无 | 短期 token / 代理注入 |
| 生命周期 | 单次命令 | 会话级 + 预热池 |
| 可观测 | stdout/stderr | 全量命令审计 + 计量 |

详见教程 [附录 C：安全检查清单](../agent-sandbox-tutorial/附录C-安全检查清单.md)。

---

## 相关文档

- [资料包总入口](../README.md)
- [教程第 9 章：实战搭建](../agent-sandbox-tutorial/09-实战搭建.md)
- [实测输出记录 RESULTS.md](RESULTS.md)
- [MCP 配套代码](code/README.md)
