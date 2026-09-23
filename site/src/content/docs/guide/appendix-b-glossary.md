---
title: "附录 B 术语表"
description: "microVM / gVisor / TEE / egress 等术语解释。"
---

| 术语 | 含义 |
|---|---|
| microVM | 轻量虚拟机，强隔离 + 快启动（如 Firecracker） |
| gVisor | 用户态内核，拦截并重新实现系统调用 |
| Kata Containers | 用 VM 承载容器的运行时 |
| WASM | WebAssembly，语言级沙箱，启动极快 |
| namespace | Linux 内核隔离机制（PID / 网络 / 挂载 / 用户等） |
| cgroup | Linux 资源限额机制（CPU / 内存 / 进程数） |
| bubblewrap (bwrap) | 非特权沙箱工具，Flatpak 用它隔离应用 |
| chroot | 改变根目录，**不是**安全边界 |
| capabilities | Linux 细粒度权限（可被 `--cap-drop` 移除） |
| seccomp | 系统调用过滤 |
| PTY | 伪终端，支持交互式 shell |
| egress | 出网流量 |
| ingress | 入网流量 |
| snapshot / fork | 快照 / 分叉，保存或复制环境状态 |
| 冷启动 | 从零拉起一个环境的时间 |
| warm pool | 预热池，提前起好环境以规避冷启动 |
| 逃逸 | sandbox escape，突破隔离边界 |
| MCP | Model Context Protocol，Agent 工具接入标准 |
| TEE | 可信执行环境（SGX / TDX / SEV） |
| RL rollout | 强化学习中用环境采样轨迹的过程 |
| computer-use | 让 Agent 像人一样操作电脑（含 GUI） |

---
