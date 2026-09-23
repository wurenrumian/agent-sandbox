---
title: "附录 B 术语表"
description: "microVM / gVisor / TEE / egress 等术语解释。"
---

> 按主题分组。每条给出「是什么」，并用「⟶」补充「为什么重要 / 关联」。

## B.1 隔离与内核机制

| 术语 | 含义 |
|---|---|
| **namespace** | Linux 内核隔离机制（PID / 网络 / 挂载 / 用户 / UTS / IPC / cgroup）。⟶ 容器与 bwrap 的隔离基础 |
| **cgroup** | Linux 资源限额机制（CPU / 内存 / 进程数 / IO）。⟶ 沙箱「限额」的实现手段 |
| **seccomp** | 系统调用过滤，可限制进程能调用哪些 syscall。⟶ 容器安全加固常用 |
| **capabilities** | Linux 细粒度权限（如 `CAP_NET_ADMIN`）。⟶ `--cap-drop ALL` 用来去权 |
| **chroot** | 改变根目录。⚠️ **不是**安全边界，可被绕过。⟶ 别拿它当沙箱 |
| **user namespace** | 让非特权用户创建隔离环境、在内部成为（伪）root。⟶ bwrap 零 root 运行的关键 |
| **bubblewrap (bwrap)** | 非特权沙箱工具，Flatpak 用它隔离应用。⟶ 本教程方案 A 的核心 |
| **unshare** | util-linux 提供的命名空间操作命令。⟶ bwrap 的底层同类工具 |

## B.2 隔离后端

| 术语 | 含义 |
|---|---|
| **容器 (container)** | 共享宿主内核的轻量隔离。⟶ 弱隔离，单租户可用 |
| **microVM** | 轻量虚拟机，独立内核 + 强隔离 + 快启动（如 Firecracker）。⟶ 生产多租户首选 |
| **Firecracker** | AWS 开源的 microVM 监视器，冷启动约百毫秒。⟶ serverless / 沙箱基础设施常客 |
| **gVisor** | Google 的用户态内核，拦截并重新实现系统调用。⟶ 多租户但不想上 VM |
| **Kata Containers** | 用 VM 承载容器的运行时。⟶ 保留容器工具链 + VM 隔离 |
| **WASM** | WebAssembly，语言级沙箱，启动极快、可移植。⟶ 轻量函数 / Edge |
| **hypervisor** | 虚拟机监视器（KVM / Firecracker / QEMU）。⟶ microVM 的隔离边界 |
| **TEE** | 可信执行环境（SGX / TDX / SEV）。⟶ 可验证、抗篡改，用于高合规场景 |

## B.3 运行与生命周期

| 术语 | 含义 |
|---|---|
| **PTY** | 伪终端，支持交互式 shell。⟶ 很多 Agent 依赖 bash 交互 |
| **冷启动** | 从零拉起一个环境的时间。⟶ 决定体验与是否需要预热池 |
| **warm pool** | 预热池，提前起好环境以规避冷启动。⟶ 把秒级压到百毫秒 |
| **会话粘性 (session affinity)** | 同一会话路由到同一环境。⟶ 有状态任务的前提 |
| **snapshot / fork** | 快照 / 分叉：保存或复制环境状态。⟶ 并行探索、RL rollout |
| **持久卷 (persistent volume)** | 跨会话保留的数据卷。⟶ 长任务 / 工作区 |
| **TTL** | 存活时间上限，到期自动回收。⟶ 防僵尸环境堆积 |

## B.4 网络与安全

| 术语 | 含义 |
|---|---|
| **egress** | 出网流量。⟶ 数据外泄的通道，重点管控 |
| **ingress** | 入网流量。⟶ 相对次要，但也要限制 |
| **白名单代理 (allowlist proxy)** | 只放行指定域名的出网代理，是沙箱唯一出口。⟶ 第 6 章核心防护 |
| **prompt injection** | 通过输入诱导模型执行攻击者指令。⟶ Agent 头号风险 |
| **间接注入 (indirect injection)** | 恶意指令藏在 Agent 会读取的外部内容里。⟶ 网页 / 文档 / 工具返回值 |
| **数据外泄 (exfiltration)** | 把敏感数据送出边界。⟶ 沙箱场景最该防的损失 |
| **逃逸 (sandbox escape)** | 突破隔离边界。⟶ 传统沙箱头号风险，Agent 场景降为次要 |
| **横向移动 (lateral movement)** | 从沙箱触达内网 / 其他服务。⟶ 需阻断内网与云元数据地址 |
| **云元数据服务** | `169.254.169.254`，云主机凭据端点。⟶ 必须阻断，否则可窃取云凭据 |
| **DNS rebinding** | 利用 DNS 解析变化绕过域名白名单。⟶ DNS 也要受控 |
| **供应链攻击** | 通过恶意依赖包入侵。⟶ `pip install` 是典型入口 |

## B.5 接入与生态

| 术语 | 含义 |
|---|---|
| **MCP** | Model Context Protocol，Agent 工具接入标准。⟶ 让沙箱可插拔 |
| **控制面 / 数据面** | 调度与管理 / 真正执行的两层。⟶ 生产架构的基本划分 |
| **配额 (quota)** | 每用户 / 会话的资源上限。⟶ 防资源滥用与成本失控 |
| **审计日志 (audit log)** | 全量记录命令、会话、发起者。⟶ 追责与计费基础 |
| **human-in-the-loop** | 高风险操作需人工审批。⟶ 最后一道治理防线 |
| **熔断 / kill switch** | 异常时自动停止执行。⟶ 成本与风险兜底 |
| **RL rollout** | 强化学习中用环境采样轨迹的过程。⟶ 沙箱分叉的核心用途 |
| **computer-use** | 让 Agent 像人一样操作电脑（含 GUI）。⟶ 沙箱从跑代码扩展到操作整机 |

---
