---
title: "07 产品版图"
description: "六类产品分类、1k+ stars 开源项目盘点（含快照日期）、尽调 8 问、选型三问与自建 vs 托管。"
---

> **本章导读**｜预计 15 分钟
>
> 知道「要什么」之后，只剩一个问题：**自己造，还是买？买哪家？**
> ⚠️ 产品名录变化极快，所以本节的所有数字都带**快照日期**；但**评估维度与选型方法不会过时**——请把重点放在「怎么判断」而不是「记住名单」。
> 本章分三段：先给一张**分类图**（7.1），再给一份**带 star 实查的开源盘点**（7.2–7.3），最后是**尽调与决策方法**（7.4–7.7）。

## 7.1 分类一览

先分清六类东西。它们的**交付形态**完全不同，混着比价一定会得出错误结论。

| 类别 | 代表 | 交付形态 | 适合 |
|---|---|---|---|
| **闭源沙箱云** | E2B Cloud、Modal Sandboxes、Cloudflare Sandbox、Vercel Sandbox、Runloop、Blaxel、Northflank、阿里云无影 | 按用量付费的 API | 快速验证、中小规模、不想运维 |
| **大厂内置** | OpenAI Code Interpreter / AgentKit、Anthropic code execution、Google code execution | 模型生态里的一项能力 | 已在用该模型生态 |
| **Agent 框架自带** | OpenHands runtime、AutoGen code executor、LangChain executors | 跟着框架走的运行时 | 已选定框架 |
| **开源 · 通用运行时** | OpenSandbox、E2B（自托管）、microsandbox、smolvm、agent-infra AIO Sandbox | 可自托管的运行时 / SDK | 要自主可控、要嵌入自己的程序 |
| **开源 · 平台化 / K8s** | kubernetes-sigs/agent-sandbox、OpenSandbox 集群模式 | CRD + 控制器 + 编排 | 已有 K8s、规模大、要统一治理 |
| **开源 · 进程级围栏** | anthropic-experimental/sandbox-runtime（`srt`）、nono | 一条命令给已有进程加围栏 | 只想给现有 agent 加边界，不想上容器 |
| **浏览器 / computer-use** | Playwright in container、Browserbase、Steel、trycua/cua | 带 GUI 的环境 | GUI 自动化 |
| **本地 / 教学** | Docker、bubblewrap、Linux namespaces | 零依赖、本机 | 学习、原型、本机隔离 |

> 关键区别：**闭源沙箱云卖的是「服务」，开源项目卖的是「你要自己运维的实现」。** 拿云的价格直接对比开源的 star 数或功能表，是选型里最常见的错。

## 7.2 开源项目盘点（1k+ stars）

> **数据快照：2026-10-21**，star / 许可 / 归档状态取自 GitHub REST API 实查（`repos/{owner}/{repo}`），2026-10-22 复验了本表关键项。**star 会变**，超过一两个月请重查（方法见 7.3）。

### 7.2.1 通用 agent 沙箱运行时

| 项目 | Stars | 许可 | 隔离方式 | 定位 |
|---|---|---|---|---|
| [opensandbox-group/OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) | 16.0k | Apache-2.0 | Firecracker microVM + Docker | 在自有基础设施上跑沙箱；本地 Docker 起步、K8s 扩展；pause/resume 保留内存与磁盘、出网策略、凭据保险箱；在 CNCF Landscape。宣称 Firecracker 冷启动 64ms P50 / 125ms P99（10 并发） |
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | 14.5k | Apache-2.0 | Firecracker microVM | 生态最成熟、SDK 最完善（Python / TS），Code Interpreter 开箱即用；云服务强，也可自托管 |
| [microsandbox/microsandbox](https://github.com/microsandbox/microsandbox) | 8.8k | Apache-2.0 | libkrun microVM | Rust 写的本地优先运行时，启动 <100ms，支持 fork / snapshot、OCI 镜像，macOS / Linux / Windows 全支持，可嵌进代码、可 detached 长跑 |
| [smol-machines/smolvm](https://github.com/smol-machines/smolvm) | 6.8k | Apache-2.0 | libkrun microVM | 「可分支的 microVM」，可嵌入 + 便携 + 本地隔离，带 npm / PyPI / crates 绑定 |
| [agent-infra/sandbox](https://github.com/agent-infra/sandbox)（AIO Sandbox） | 6.2k | Apache-2.0 | 单 Docker 容器 | 一个容器塞齐 Browser + Shell + File + VSCode Server + Jupyter + MCP，agent 上手最快 |
| [rivet-dev/agentos](https://github.com/rivet-dev/agentos) | 4.8k | Apache-2.0 | WebAssembly | 用 WASM 做 Linux 兼容沙箱，体积极小、启动快，适合嵌到服务端 |
| [strukto-ai/mirage](https://github.com/strukto-ai/mirage) | 3.7k | Apache-2.0 | 虚拟终端 + VFS | 给 agent 一个「虚拟终端」，文件系统是虚拟的，适合怕 agent 碰真机的场景 |
| [earendil-works/gondolin](https://github.com/earendil-works/gondolin) | 2.3k | Apache-2.0 | Linux microVM + TS 控制面 | 实验性质，TypeScript 控制面有特色 |
| [perplexityai/SPACE](https://github.com/perplexityai/SPACE) | 1.8k | Apache-2.0 | 可插拔 runtime | Perplexity 开源，Rust，强调 runtime 可替换 |
| [BitMiracle-AI/Dormice](https://github.com/BitMiracle-AI/Dormice) | 1.6k | Apache-2.0 | gVisor / Docker | 自称「沙箱界的 SQLite」，**E2B 兼容**、自托管、空闲零成本，定位替换 E2B |
| [langgenius/dify-sandbox](https://github.com/langgenius/dify-sandbox) | 1.3k | Apache-2.0 | seccomp + chroot | 极轻量，只做多语言代码执行，Dify 生态在用 |
| [cloudflare/sandbox-sdk](https://github.com/cloudflare/sandbox-sdk) | 1.2k | 自定义（NOASSERTION） | Cloudflare Containers | 跑在 Cloudflare 边缘，绑定其平台 |
| [agentbay-ai/wuying-agentbay-sdk](https://github.com/agentbay-ai/wuying-agentbay-sdk) | 1.1k | Apache-2.0 | 云沙箱（无影） | 阿里云无影的 agent 云沙箱 SDK |
| [vndee/llm-sandbox](https://github.com/vndee/llm-sandbox) | 1.1k | MIT | Docker / Podman | 最省事的 Python 库，几行代码起一个隔离执行环境 |
| [clawkwork/clawk](https://github.com/clawkwork/clawk) | 1.0k | Apache-2.0 | microVM | 「给 coding agent 一台一次性 Linux VM，而不是你的笔记本」 |

### 7.2.2 OS 级 / 进程级围栏

不用容器、不用 VM，直接给进程套**系统调用与文件系统策略**。适合「给已有的 agent 加边界」。

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [anthropic-experimental/sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime) | 5.6k | Apache-2.0 | Anthropic 官方 `srt`：macOS 用 Seatbelt、Linux 用 bubblewrap，外加网络过滤代理；不依赖容器即可限制任意进程的文件系统与网络。给 Claude Code 一类工具加围栏的底层设施 |
| [nolabs-ai/nono](https://github.com/nolabs-ai/nono) | 4.6k | Apache-2.0 | Sigstore 团队出品，主打 agent 运行时安全、零配置零延迟，偏安全向 |

### 7.2.3 coding agent 的编排层（有沙箱，但更偏「工作环境」）

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [trycua/cua](https://github.com/trycua/cua) | 30.5k | MIT | 跨 OS 桌面 / computer-use 沙箱 + 评测基准，做 GUI agent 绕不开 |
| [coder/coder](https://github.com/coder/coder) | 17.1k | AGPL-3.0 | 自托管开发环境平台，现明确面向「开发者和他们的 agent」 |
| [gitpod-io/gitpod](https://github.com/gitpod-io/gitpod) | 13.8k | AGPL-3.0 | 云开发环境，agent 执行环境常建在其上 |
| [mattpocock/sandcastle](https://github.com/mattpocock/sandcastle) | 8.6k | MIT | TS 里 `sandcastle.run()` 编排沙箱化 coding agent |
| [dagger/container-use](https://github.com/dagger/container-use) | 4.1k | Apache-2.0 | 多个 coding agent 各自在独立容器里改代码、互不干扰 |
| [superagent-ai/vibekit](https://github.com/superagent-ai/vibekit) | 1.9k | MIT | 把 Claude Code / Codex / Gemini 塞进干净沙箱，带敏感信息脱敏与可观测性 |
| [vercel-labs/coding-agent-template](https://github.com/vercel-labs/coding-agent-template) | 1.8k | 自定义（NOASSERTION） | 多 agent 编码平台模板，后端是 Vercel Sandbox（**闭源**） |

### 7.2.4 底座与执行引擎（选型时你多半不会直接用，但决定上限）

| 项目 | Stars | 许可 | 说明 |
|---|---|---|---|
| [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | 37.5k | Apache-2.0 | microVM 事实标准，E2B / OpenSandbox 都建在它上面 |
| [google/gvisor](https://github.com/google/gvisor) | 19.7k | Apache-2.0 | 用户态内核，容器级隔离的另一条路 |
| [judge0/judge0](https://github.com/judge0/judge0) | 4.5k | GPL-3.0 | 多语言判题 / 执行系统，48 种语言 |
| [engineer-man/piston](https://github.com/engineer-man/piston) | 2.8k | MIT | 高性能通用代码执行引擎 |

## 7.3 两个别踩的坑

**① star 最高 ≠ 能用。** [daytonaio/daytona](https://github.com/daytonaio/daytona) 有 **71.5k stars**，但仓库状态是 **archived**（最后推送 2026-07-24），2026-06 起生产代码库转闭源，只剩旧代码与 SDK。这是「开源沙箱」选型时最容易误列的一项——**star 数是历史热度的化石，不代表项目还活着。**

**② Agent 平台 ≠ 沙箱项目。** OpenHands（91.4k，MIT）、bytedance/deer-flow（84.2k，MIT）、openclaw/openclaw（392.7k，MIT）都是 **agent 平台 / 框架**，内部**自带**沙箱，但它们本身不是沙箱方案。你要么整栈选它，要么从别处挑沙箱——别把它塞进候选对比表。

> **怎么自查一件事**（30 秒，比读博客可靠）：
> ```bash
> curl -s https://api.github.com/repos/<owner>/<repo> \
>   | python3 -c 'import sys,json; d=json.load(sys.stdin); \
>       print(d["stargazers_count"], d["license"]["spdx_id"] if d["license"] else None, \
>             d["archived"], d["pushed_at"])'
> ```
> `archived=false` 且 `pushed_at` 在近一两个月，才算「活跃」。项目定位请读 README 原文，不要信二手博客转述。

## 7.4 评估一个沙箱产品的 8 个问题

不要只看功能列表，用下面这组问题做尽调：

| # | 问题 | 为什么重要 |
|---|---|---|
| 1 | 隔离后端是什么？ | 决定多租户安全上限（见第 5 章） |
| 2 | 冷启动实测多少？ | 决定能否做交互式体验 |
| 3 | 网络默认策略是什么？白名单粒度多细？ | 决定外泄风险（见第 6 章） |
| 4 | 支持快照 / 分叉吗？快照怎么加密与隔离？ | 决定高级场景与数据安全 |
| 5 | 支持持久卷 / 会话粘性吗？ | 决定能否做多步有状态任务 |
| 6 | 凭据怎么注入？能不能不放长期 secret？ | 决定泄漏面 |
| 7 | 有 GPU 吗？按什么计费？ | 决定成本模型 |
| 8 | 审计日志 / 用量计量开放到什么程度？ | 决定可治理性与成本归因 |

> 提示：把这些问题做成一张表，对 2–3 家候选打勾。**第 1、3、6 项是安全红线，不满足直接淘汰。**

## 7.5 选型三问

先用三个问题砍掉大部分选项：

1. **托管还是自建？** 想快 / 团队小 → 托管；要可控 / 数据合规要求高 → 自建。
2. **隔离要多强？** 多租户、不可信输入 → microVM / gVisor；单租户可信 → 容器即可。
3. **要 GPU 吗？** 要 → 先确认候选是否支持 GPU 直通，这往往直接决定名单。

## 7.6 自建 vs 托管对比

| 维度 | 自建 | 托管 |
|---|---|---|
| 上手速度 | 慢（周～月） | 快（小时～天） |
| 运维成本 | 高（需专人） | 低（交给厂商） |
| 可控性 | 高（任意定制） | 中（受 API 限制） |
| 数据合规 | 完全自控 | 看厂商与区域 |
| 成本结构 | 前期投入高，边际成本低 | 按用量付费，规模大后可能更贵 |
| 故障责任 | 自己扛 | 厂商 SLA |
| 适合 | 规模大、合规严、需深度定制 | 快速验证、中小规模、团队小 |

**一个务实建议**：**先用托管跑通业务，把「沙箱接口」封装成自己的抽象层**。等用量 / 合规压力上来了，再把数据面换成自建（Firecracker），控制面接口保持不变——继续复用第 4 章的「控制面 / 数据面分离」红利。

> 这也是为什么 **E2B 兼容的 REST API 已经成了事实标准**：多家自建方案（如 Dormice）直接打「E2B 兼容」牌，让你换后端时不用重写业务代码。选型时优先选接口语义与主流一致的那个。

## 7.7 一个决策示例

> 场景：一个面向公众的在线代码运行平台，需要 GPU，数据需留在境内。

1. 托管还是自建？→ 目标市场规模大、数据需境内 → 倾向自建或私有化托管。
2. 隔离多强？→ 面向公众、互不信任 → microVM。
3. 要 GPU？→ 要 → 过滤掉不支持 GPU 的候选。

结论：**GPU 计算用 QEMU/KVM 完整 VM（或支持 GPU 的 Kata Containers / 托管 GPU 沙箱）承载；非 GPU 的不可信执行再用 Firecracker microVM**。也可选择支持境内区域 + GPU 的托管厂商做过渡。这个例子说明：**三问的顺序是先安全 / 合规红线，再功能，最后才是价格。**

> ⚠️ 注意：Firecracker 的设备模型极简，**不支持 GPU 直通**——需要 GPU 时应选完整 VM / Kata / 支持 GPU 的托管沙箱，别把「强隔离」和「GPU」默认绑在同一个后端上。

## 常见误区

| 误区 | 问题 | 正确做法 |
|---|---|---|
| 「star 多就是好项目」 | star 反映历史热度，可能已归档或闭源 | 查 `archived` / `pushed_at` / LICENSE（见 7.3） |
| 「agent 平台自带沙箱，直接拿来用」 | 平台 ≠ 沙箱，会锁死整栈 | 分清「整栈选平台」还是「单独选沙箱」 |
| 「开放沙箱云 vs 自建，比功能表」 | 一个是服务、一个是你要运维的实现 | 用 7.4 的 8 问按同一标准尽调 |
| 「先把最强隔离上了再说」 | 拖慢交付、增加复杂度 | 按第 8 章的分级，需要时再升级后端 |

## 动手练习 7

1. 用「选型三问」给 [第 5 章练习](/agent-sandbox/guide/05-isolation-backends/) 里的三个场景各挑一个具体产品。
2. 用 7.4 的 8 个问题，对两个候选产品各查一次官方文档，填一张对比表。
3. 从 7.2 的表里挑三个项目，用 7.3 的自查命令跑一遍，记录它们的 `archived` / `pushed_at` / LICENSE，判断哪个还值得进候选名单。

---
