---
title: 开源 agent sandbox 项目盘点（1k+ stars）
type: research
status: draft
created: 2026-10-21
updated: 2026-10-21
tags: [agent-sandbox, sandbox, code-execution, microvm, firecracker, gvisor, survey]
related: []
---

# 开源 agent sandbox 项目盘点（1k+ stars）

## 一句话

开源 agent 沙箱已经分层：**通用沙箱运行时**（OpenSandbox / E2B / microsandbox / smolvm）、**K8s 与平台化**（agent-sandbox、agent-infra AIO）、**OS 进程级围栏**（Anthropic srt）、**底座技术**（Firecracker / gVisor）。选型先定隔离层级和部署形态，再看 star。

> **数据快照：2026-10-21**，star 数取自 GitHub REST API 实查，不是网页缓存或博客转述。star 会变，超过 1–2 个月请重查。

## 一、通用 agent 沙箱运行时

| 项目 | Stars | 许可 | 隔离方式 | 定位 |
|---|---|---|---|---|
| [opensandbox-group/OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) | 16.0k | Apache-2.0 | Firecracker microVM + Docker | 自有基础设施上跑沙箱；本地 Docker 起步、K8s 扩展；pause/resume 保留内存与磁盘、出网策略、凭据保险箱；在 CNCF Landscape。宣称 Firecracker 创建 64ms P50 / 125ms P99（10 并发） |
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 14.5k | Apache-2.0 | Firecracker microVM | 生态最成熟、SDK 最完善（Python/TS），Code Interpreter 开箱即用；云服务强，也可自托管 |
| [microsandbox/microsandbox](https://github.com/microsandbox/microsandbox) | 8.8k | Apache-2.0 | libkrun microVM | Rust 写的本地优先运行时，启动 <100ms，支持 fork/snapshot、OCI 镜像，macOS/Linux/Windows 全支持，可嵌进代码、可 detached 长跑 |
| [smol-machines/smolvm](https://github.com/smol-machines/smolvm) | 6.8k | Apache-2.0 | libkrun microVM | "可分支的 microVM"，可嵌入 + 便携 + 本地隔离，带 npm/PyPI/crates 绑定 |
| [agent-infra/sandbox](https://github.com/agent-infra/sandbox)（AIO Sandbox） | 6.2k | Apache-2.0 | 单 Docker 容器 | 一个容器塞齐 Browser + Shell + File + VSCode Server + Jupyter + MCP，agent 上手最快，有论文与评测 |
| [rivet-dev/agentos](https://github.com/rivet-dev/agentos) | 4.8k | Apache-2.0 | WebAssembly | 用 WASM 做 Linux 兼容沙箱，体积极小、启动快，适合嵌到服务端 |
| [nolabs-ai/nono](https://github.com/nolabs-ai/nono) | 4.6k | Apache-2.0 | 进程级零信任 | Sigstore 团队出品，主打 agent 运行时安全、零配置零延迟，偏安全向 |
| [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | 4.3k | Apache-2.0 | K8s CRD + 控制器 | k8s-sigs 官方项目，用 `Sandbox` CRD 管理有状态单例工作负载，K8s 原生团队首选 |
| [strukto-ai/mirage](https://github.com/strukto-ai/mirage) | 3.7k | Apache-2.0 | 虚拟终端 + VFS | 给 agent 一个"虚拟终端"，文件系统是虚拟的，适合怕 agent 碰真机的场景 |
| [earendil-works/gondolin](https://github.com/earendil-works/gondolin) | 2.3k | Apache-2.0 | Linux microVM + TS 控制面 | 实验性质，TypeScript 控制面有特色 |
| [perplexityai/SPACE](https://github.com/perplexityai/SPACE) | 1.8k | Apache-2.0 | 可插拔 runtime | Perplexity 开源，Rust，强调 runtime 可替换 |
| [BitMiracle-AI/Dormice](https://github.com/BitMiracle-AI/Dormice) | 1.6k | Apache-2.0 | gVisor / Docker | 自称"沙箱界的 SQLite"，**E2B 兼容**、自托管、空闲零成本，定位替换 E2B |
| [langgenius/dify-sandbox](https://github.com/langgenius/dify-sandbox) | 1.3k | Apache-2.0 | seccomp + chroot | 极轻量，只做多语言代码执行，Dify 生态在用 |
| [cloudflare/sandbox-sdk](https://github.com/cloudflare/sandbox-sdk) | 1.2k | 自定义（NOASSERTION） | Cloudflare Containers | 跑在 Cloudflare 边缘，绑定其平台 |
| [agentbay-ai/wuying-agentbay-sdk](https://github.com/agentbay-ai/wuying-agentbay-sdk) | 1.1k | Apache-2.0 | 云沙箱（无影） | 阿里云无影的 agent 云沙箱 SDK |
| [vndee/llm-sandbox](https://github.com/vndee/llm-sandbox) | 1.1k | MIT | Docker/Podman | 最省事的 Python 库，几行代码起一个隔离执行环境 |
| [clawkwork/clawk](https://github.com/clawkwork/clawk) | 1.0k | Apache-2.0 | microVM | "给 coding agent 一台一次性 Linux VM，而不是你的笔记本" |

## 二、OS 级 / 进程级沙箱

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [anthropic-experimental/sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime) | 5.6k | Apache-2.0 | Anthropic 官方 `srt`：macOS 用 Seatbelt、Linux 用 bubblewrap，外加网络过滤代理；不依赖容器即可限制任意进程的文件系统与网络。给 Claude Code 一类工具加围栏的底层设施，2026 年热度上升快 |

## 三、coding agent 的沙箱编排层（有沙箱，但更偏"工作环境"）

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [trycua/cua](https://github.com/trycua/cua) | 30.5k | MIT | 跨 OS 桌面 / computer-use 沙箱 + 评测基准，做 GUI agent 绕不开 |
| [coder/coder](https://github.com/coder/coder) | 17.1k | AGPL-3.0 | 自托管开发环境平台，现明确面向"开发者和他们的 agent" |
| [gitpod-io/gitpod](https://github.com/gitpod-io/gitpod) | 13.8k | AGPL-3.0 | 云开发环境，agent 执行环境常建在其上 |
| [mattpocock/sandcastle](https://github.com/mattpocock/sandcastle) | 8.6k | MIT | TS 里 `sandcastle.run()` 编排沙箱化 coding agent |
| [dagger/container-use](https://github.com/dagger/container-use) | 4.1k | Apache-2.0 | 多个 coding agent 各自在独立容器里改代码、互不干扰 |
| [superagent-ai/vibekit](https://github.com/superagent-ai/vibekit) | 1.9k | MIT | 把 Claude Code / Codex / Gemini 塞进干净沙箱，带敏感信息脱敏与可观测性 |
| [vercel-labs/coding-agent-template](https://github.com/vercel-labs/coding-agent-template) | 1.8k | 自定义（NOASSERTION） | 多 agent 编码平台模板，后端是 Vercel Sandbox（**闭源**） |

## 四、底座与执行引擎

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | 37.5k | Apache-2.0 | microVM 事实标准，E2B / OpenSandbox 都建在它上面 |
| [google/gvisor](https://github.com/google/gvisor) | 19.7k | Apache-2.0 | 用户态内核，容器级隔离的另一条路 |
| [judge0/judge0](https://github.com/judge0/judge0) | 4.5k | GPL-3.0 | 多语言判题 / 执行系统，48 种语言 |
| [engineer-man/piston](https://github.com/engineer-man/piston) | 2.8k | MIT | 高性能通用代码执行引擎 |

## 五、两个别踩的坑

1. **Daytona**：[daytonaio/daytona](https://github.com/daytonaio/daytona) 71.5k stars，但仓库 **archived**，2026-06 起生产代码库转闭源，只剩旧代码与 SDK。star 最高却不是"开源沙箱"选项。
2. **agent 平台 ≠ 沙箱项目**：OpenHands（91.4k，MIT）、bytedance/deer-flow（84.2k，MIT）、openclaw/openclaw（392.7k，MIT）都是 agent 平台 / 框架，内部**自带**沙箱，但本身不是沙箱方案，别拿来当选型对象。

## 六、怎么选

| 需求 | 首选 |
|---|---|
| 云上多租户、生产级、要自主可控 | OpenSandbox |
| 想要成熟 SDK、少折腾 | E2B |
| 单机 / 本地 / 嵌进自己程序 | microsandbox、smolvm |
| K8s 原生、用 CRD 管生命周期 | kubernetes-sigs/agent-sandbox |
| 只给现有 agent 加围栏、不碰容器 | anthropic-experimental/sandbox-runtime |
| 给 coding agent 一次性干净环境 | vibekit、clawk、container-use |
| 要浏览器 / 桌面操作 | agent-infra AIO Sandbox、trycua/cua |
| 想零成本替换 E2B | Dormice |
| 只要能跑多语言代码、越轻越好 | llm-sandbox、dify-sandbox、judge0 |

## 七、典型技术栈

沙箱 = **一条隔离边界** + **四个配套机制**。先选边界，配套机制基本是被边界倒逼出来的。

### 7.1 五类隔离边界（互斥，选一个）

| 边界 | 怎么隔离 | 代表项目 | 代价 |
|---|---|---|---|
| **microVM**（Firecracker / libkrun / Cloud Hypervisor） | 每个沙箱一台轻量虚拟机，独立 guest 内核，走 KVM（Linux）或 Hypervisor.framework（macOS） | E2B、OpenSandbox、microsandbox、smolvm、gondolin、clawk | 需要 KVM/HVF；每实例有 guest 内核内存开销；GPU 透传麻烦 |
| **用户态内核**（gVisor） | `runsc` 用一个 Go 写的 Sentry 进程接管 guest 的系统调用，宿主内核只看到极少接口 | Dormice、GKE Sandbox、Isola | ptrace 模式下 syscall 密集负载明显变慢；部分 syscall/ioctl 不支持 |
| **容器 + 加固** | namespaces + cgroups v2 + seccomp-bpf + capabilities 裁剪 + 只读 rootfs + AppArmor/SELinux | Daytona（旧版 Sysbox）、dify-sandbox、多数"能跑就行"的方案 | 共享宿主内核，内核漏洞即逃逸；强度取决于配置，不是默认安全 |
| **OS 系统调用策略** | 不用容器，直接给进程套策略：macOS Seatbelt、Linux bubblewrap（user namespace + bind mount + seccomp）、Landlock | Anthropic `srt`、nono、hivebox、yoloai | 仍是同一内核；策略写错就是漏，且难审计 |
| **WASM** | 代码编译成 wasm，在 Wasmtime/V8 isolate 里跑，能力靠 host 显式授予 | rivet-dev/agentos、Cloudflare 系 | 跑不了原生二进制、syscall 面不全，生态兼容性最差 |

### 7.2 四个配套机制

1. **快照 / 分叉（snapshot & fork）**：Firecracker 存"内存 + 设备状态"文件、恢复毫秒级；容器侧靠 CRIU；磁盘靠 overlayfs / dm-snapshot / reflink 做 COW。用途是**预热池**（warm pool，避免冷启动）、**回溯**（arrakis 的 backtracking）、**分支**（smolvm 的 branchable VM，同一状态分叉出多条尝试）。这是 microVM 系对容器系最大的功能优势。
2. **网络控制**：TAP/NAT 或 vsock 做宿主-沙箱通道；出网走 **egress 代理 + 域名白名单**（HTTP CONNECT/SOCKS5/DNS 三层过滤）；入站走**每沙箱子域名**的反向代理（E2B 的 `3000-{id}.e2b.app` 就是这个）；更激进的用 eBPF 做 L3/L4 策略。
3. **凭据隔离**：真 key 不进沙箱。做法是 vault 存明文、代理在出网时注入 header，沙箱内只有一个占位符。OpenSandbox 的 Credential Vault、microsandbox 的 "secrets never enter the VM" 都是这个思路。
4. **编排与接入**：K8s 侧用 CRD + controller 管生命周期（agent-sandbox）、RuntimeClass 选 gVisor/Kata、镜像懒加载（overlaybd/Nydus）压冷启动；接入侧是 REST/gRPC + **E2B 兼容 API**（已成事实标准，Dormice 直接打兼容牌）、MCP server、PTY over WebSocket、浏览器用 CDP、桌面用 VNC/RDP。

### 7.3 典型组合

- **生产云**：Firecracker + warm pool + snapshot + egress 代理 + K8s → OpenSandbox、E2B
- **本地/嵌入式**：libkrun + HVF/KVM + OCI 拉镜像 + 无 daemon → microsandbox、smolvm
- **给已有 agent 加围栏**：进程级策略 + 网络代理，一行命令 → anthropic `srt`、nono
- **K8s 平台化**：CRD + RuntimeClass + 镜像懒加载 → kubernetes-sigs/agent-sandbox

## 证据

- 数据源：GitHub REST API
  - `GET https://api.github.com/repos/{owner}/{repo}` → `stargazers_count`、`license.spdx_id`、`pushed_at`、`archived`
  - `GET https://api.github.com/search/repositories?q=...` 用于补齐遗漏（`topic:agent-sandbox`、`agent+sandbox in:description stars:>800` 等）
- 项目定位取自各自 README 原文（OpenSandbox、E2B、microsandbox、smolvm、agent-infra/sandbox、nono 均已直接读 README 核对），非二手博客。
- 交叉验证来源：e2b.dev、blaxel.ai 与 northflank.com 的 sandbox 对比文章（用于 Daytona 闭源时间点与 E2B/BYOC 情况）。
- star 数为**单次快照**，无历史曲线；如需趋势需另做时间序列采集。

## 未决

- 未做实测：各项目的冷启动时间、并发密度、快照恢复开销均引用官方宣称值，没有本地基准。
- 未核对许可证细节：`cloudflare/sandbox-sdk`、`vercel-labs/coding-agent-template` 返回 NOASSERTION，需读 LICENSE 原文才能商用判断。
- 未覆盖闭源但流行的选项（Modal、Blaxel、Runloop、Vercel Sandbox），本盘点只针对开源。
- 选型目标场景未确认，尚未收敛到具体 2–3 个候选。
