---
title: agent sandbox 的使用场景（场景 → 硬需求 → 选型）
type: research
status: draft
created: 2026-10-21
updated: 2026-10-21
tags: [agent-sandbox, use-cases, scenario, code-interpreter, coding-agent, computer-use, rl-eval, mcp]
related: []
---

# agent sandbox 的使用场景

## 一句话

场景不按行业分，按四个属性分：**沙箱里跑什么 / 跑多久 / 要不要留状态 / 谁在指挥**。这四个定下来，选型基本被逼死；反过来，看一个沙箱项目 README 里"for AI agents"的泛泛描述没有信息量，要看它为哪个场景做了优化。

## 一、先分清两个架构分叉（比选项目更重要）

**分叉 A：agent 在沙箱里，还是在沙箱外？**

| | agent 在沙箱内 | agent 在沙箱外 |
|---|---|---|
| 沙箱角色 | 一整台机器，装着 harness + 模型凭据 | 只当工具执行器 |
| 出网要求 | 必须放行模型 API（provider 域名） | 沙箱本身可以完全断网 |
| 观测点 | 沙箱内（日志、PTY、屏幕） | 主服务侧（沙箱只回传结果） |
| 典型 | Upstash Box、clawk、vibekit、OpenClaw in Sandbox | E2B 的多数用法、agent-sandbox 的 "Sandboxed Tools" 模式 |

Upstash 在对比文章里把这条讲得最直白：一类产品是"安全边界"，另一类是"把整个 agent 塞进盒子，只给你一个 prompt"。两者的凭据模型、网络策略、计费方式都不同，混着比会得出错误结论。

**分叉 B：状态模型**

- **一次性（ephemeral）**：跑完即弃。实现最简单，成本最低。
- **工作区持久（workspace）**：文件、依赖、git 留存，跨会话继续。
- **快照分叉（snapshot / fork）**：从同一状态复制出 N 份并行尝试，或回滚到某一步。

E2B 的文档里 fork 上限写的是 100 份；smolvm 主打"branchable VM"；arrakis 做的是 backtracking。这三个不是同一件事，别混。

## 二、场景清单

### 1. 代码解释器 / 数据分析

- **谁**：ChatGPT 高级数据分析一类产品、BI 工具、报表生成、论文复现。
- **硬需求**：秒级冷启动、科学计算栈预装、富输出回传（图 / 表 / DataFrame）。
- **状态**：多为会话内 ephemeral。
- **命门**：**冷启动**。这是唯一一个把启动延迟当第一指标的场景。
- **推荐**：E2B Code Interpreter、microsandbox、llm-sandbox；只判题不要 agent 抽象就 judge0 / piston。
- **坑**：富输出序列化（图片怎么回传、大 DataFrame 怎么截断）通常比隔离本身更费工。

### 2. Coding agent（仓库编辑类）

- **谁**：Claude Code / Codex 一类、Aider、Ramp 的后台编码 agent、各家的"Devin 替代"。
- **硬需求**：持久工作区、git 操作、装依赖、跑测试、分钟到小时级运行、能暂停恢复。
- **状态**：workspace + snapshot。
- **命门**：**依赖安装与状态留存**。每步重装环境的 agent 会慢一个数量级，也没法迭代。
- **推荐**：vibekit、container-use、clawk、kubernetes-sigs/agent-sandbox（有现成的 Claude Code / Aider / Pi 示例）。
- **坑**：git 凭据（必须走代理注入，别把 token 写进沙箱）、PR 回写路径、测试环境的网络白名单。

### 3. 浏览器 / 桌面 computer-use

- **谁**：browser-use 类、GUI 操作 agent、Playwright 抓取与截图。
- **硬需求**：有头浏览器、CDP 或 VNC、固定分辨率、可选的 GPU（VLM 推理）。
- **状态**：多为会话级，但需要"上一次的页面还在"。
- **命门**：**内存密度**。一个 Chromium 就 1GB 起，并发的成本是纯线性的。
- **推荐**：agent-infra AIO Sandbox（Browser+Shell+VSCode+Jupyter 一容器）、trycua/cua（跨 OS 桌面）、agent-sandbox 的 Playwright / Chrome 示例。
- **坑**：反爬指纹、浏览器崩溃后的会话恢复、截图流带宽。

### 4. 评测与 RL 训练（需求最特殊）

- **谁**：SWE-bench / terminal-bench 一类评测、NVIDIA NeMo Gym、WebGym（29 万任务）、各家做 agent 训练的数据管线。
- **硬需求**：千级并行、完全可复现、固定或无外网、快速重置、批量调度与配额。
- **状态**：一次性，但**镜像必须完全确定**。
- **命门**：**调度与镜像分发**，不是隔离。
- **推荐**：kubernetes-sigs/agent-sandbox（WarmPool / Kueue / Ray / NeMo Gym 都有官方示例）、OpenSandbox 的批量创建。
- **坑**：环境漂移会让评测数字不可比；镜像拉取时间经常超过任务本身。
- **证据**：Hugging Face 用 E2B 复现 DeepSeek-R1 的 RL 管线，是这类场景被公开引用最多的案例。

### 5. 常驻 / agents-as-a-service（多租户托管）

- **谁**：托管型个人 agent（OpenClaw 类）、"AI 员工"、per-user 工作区。
- **硬需求**：按用户分配、预热池、suspend/resume 省闲置成本、状态在 PVC 上存活。
- **状态**：长期 workspace。
- **命门**：**闲置成本**。常驻但不干活的时间必须能被压到接近零。
- **推荐**：agent-sandbox（有 "Hermes Agents as a Service" 的完整模式：per-user claims + warm pool + suspend/resume + PVC 存活）、E2B 的 pause/resume。
- **坑**：状态迁移（节点下线时用户的文件怎么办）、配额与滥用。

### 6. 工具执行 / MCP server 隔离

- **谁**：第三方 MCP server、插件市场、把 tool call 当不可信输入的平台。
- **硬需求**：最小权限、每调用级策略、凭据不出沙箱、低延迟。
- **状态**：一次性，但沙箱要复用（每次起太慢）。
- **命门**：**策略粒度**。要能说清"这个工具只能读这个目录、只能连这个域名"。
- **推荐**：anthropic `srt`、nono（per-tool-call brokered sandboxing）、agent-sandbox 的 MCP Sandbox 示例。
- **坑**：复用沙箱 + 每次调用换策略，这两件事在实现上会打架。

### 7. 用户可编程平台 / AI app builder

- **谁**：低代码平台、内嵌代码执行的 SaaS、生成应用并预览的产品。
- **硬需求**：多租户强隔离、按租户配额、预览 URL、冷启动要快、防滥用（挖矿）。
- **状态**：项目级持久 + 会话级临时。
- **命门**：**计费与防滥用**。
- **推荐**：E2B、OpenSandbox、Vercel Sandbox（按 active CPU 计费，等模型时不计费）。
- **证据**：Modal 公开的 Lovable 案例——48 小时内 100 万+ 沙箱，约 25 万次应用创建，沙箱纯粹当"生成应用的预览环境"用。这是把沙箱当 CDN 级基础设施在跑。

### 8. 安全分析（沙箱的原始场景）

- **谁**：红队、恶意样本分析、渗透测试 agent。
- **硬需求**：强隔离、网络可完全切断或仿真、快照回滚、行为采集。
- **状态**：快照回滚为主。
- **命门**：**可观测性**（进程、文件、网络行为都要留痕）。
- **推荐**：arrakis（888★，低于 1k 线但功能最对：MicroVM + backtracking + REST API）、自建 Firecracker。
- **坑**：这个场景几乎不需要"agent 抽象"，反而需要完整的系统调用与网络行为记录，和 agent 沙箱的关注点正交。

### 9. CI/CD 里的 agent

- **谁**：GitHub Agentic Workflows 一类、自动修 PR 的流水线。
- **硬需求**：与 CI 集成、无状态、权限最小、审计留痕。
- **推荐**：Docker Sandboxes（2026-07 起被 GitHub Agentic Workflows 支持）、agent-sandbox 的 CI/CD 模式。
- **坑**：CI 本身已经有隔离，沙箱是第二层，别把两层的凭据搞混。

## 三、场景 → 主导成本（最容易记的一张表）

| 场景 | 主导成本 | 优化方向 |
|---|---|---|
| 代码解释器 | 冷启动 | 预热池、快照恢复 |
| Coding agent | 依赖安装与状态 | 持久工作区、模板镜像 |
| 浏览器 / 桌面 | 内存密度 | 共享浏览器进程、按需启停 |
| 评测 / RL | 调度与镜像分发 | WarmPool、批量创建、镜像懒加载 |
| 常驻 agent | 闲置成本 | suspend/resume、scale-to-zero |
| 工具执行 | 策略粒度 | 复用沙箱 + 每调用策略 |
| 用户可编程 | 计费与滥用 | 配额、active CPU 计费 |

每个场景只有一个主导成本项。选型时先问"我这个场景的账单会被什么撑爆"，答案通常直接指向该用哪类沙箱。

## 四、回到开源名单

| 场景 | 开源首选 | 备选 |
|---|---|---|
| 代码解释器 | llm-sandbox、microsandbox | dify-sandbox、judge0 |
| Coding agent | vibekit、container-use | clawk、agent-sandbox 示例 |
| 浏览器 / 桌面 | agent-infra AIO | trycua/cua |
| 评测 / RL | kubernetes-sigs/agent-sandbox | OpenSandbox 批量 |
| 常驻 / 多租户 | agent-sandbox + WarmPool | E2B pause/resume |
| 工具执行 / MCP | anthropic `srt`、nono | agent-sandbox MCP 示例 |
| 用户可编程 | OpenSandbox、E2B | — |
| 安全分析 | arrakis | 自建 Firecracker |

## 证据

- **原文事实**：E2B 官网 markdown（`e2b.dev/index.md`）自列 5 类场景：coding agents、code interpreters、computer-use/browser、deep-research/knowledge-work、RL/eval/benchmark 并行环境；并给出 pause/resume、fork 上限 100、egress 按 CIDR/hostname 控制、凭据在 egress 代理注入。
- **原文事实**：kubernetes-sigs/agent-sandbox 的 Use Cases 分 6 类：Code Execution、Coding Agents、Computer Use、CI/CD、Agents in Sandbox（OpenClaw）、Self-Hosted Sandboxes（Anthropic Managed Agents）；More Examples 下有 40+ 具体示例（RL、NeMo Gym、Ray、Kueue、KEDA、Hermes agents-as-a-service、MCP、Playwright、VSCode、JupyterLab 等）。
- **原文事实**：Upstash 对比文章明确区分"沙箱当安全边界"与"agent 整个塞进沙箱"两类产品。
- **原文事实**：Modal 公开数据——Lovable 48 小时 100 万+ 沙箱、约 25 万次应用创建；Ramp 的后台编码 agent 跑在 Modal Sandboxes 上。
- **原文事实**：Hugging Face 用 E2B 做 RL 管线（DeepSeek-R1 复现），Groq 用 E2B 做 compound AI 的实时代码执行。
- **推断**："每个场景只有一个主导成本项"是我的归纳，不是任何来源的说法；证据是各场景被公开强调的瓶颈不同（E2B 强调 fork/pause，agent-sandbox 强调 WarmPool/调度，Modal 强调并发数）。
- **待验证**：各场景的实际成本量级没有实测；WebGym 的 292,092 任务、NeMo Gym 的接入方式未逐条核对原始文档。

## 未决

- 没有真实业务场景，无法验证"四个属性定场景"这套分类在具体项目上的判别力。
- 场景 8（安全分析）与场景 9（CI/CD）的开源方案覆盖度最弱，样本少，结论偏弱。
- 各场景对应的成本模型（每千次执行多少钱）完全空白，需要实测或厂商报价。
