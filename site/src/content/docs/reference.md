---
title: "速查参考"
description: "10 个主题的速查版：定位、能力、架构、选型、威胁、产品、趋势。"
---

> 一份关于「AI Agent 执行沙箱」的概念、架构、选型与安全实践笔记。
> 整理日期：2026-09-23

---

## 目录

1. [定位：从「防御机制」到「Agent 的手脚」](#1-定位从防御机制到-agent-的手脚)
2. [为什么 Agent 特别需要沙箱](#2-为什么-agent-特别需要沙箱)
3. [一个 Agent 沙箱应提供的能力](#3-一个-agent-沙箱应提供的能力)
4. [典型架构](#4-典型架构)
5. [隔离后端怎么选](#5-隔离后端怎么选)
6. [Agent 特有的威胁模型](#6-agent-特有的威胁模型)
7. [产品与项目版图](#7-产品与项目版图)
8. [什么时候不需要沙箱](#8-什么时候不需要沙箱)
9. [自建的最小可用建议](#9-自建的最小可用建议)
10. [趋势](#10-趋势)

---

## 1. 定位：从「防御机制」到「Agent 的手脚」

传统沙箱是**防御性**的：别让坏代码破坏系统。

Agent 沙箱更多是**赋能性**的：**让 Agent 能安全地「做事」**。

- LLM 只能生成文本。要真正产生影响（改文件、跑脚本、装依赖、发请求），必须有地方执行。
- 那个地方就是沙箱。所以从 Agent 角度看，沙箱 ≈ **Agent 的执行运行时（execution runtime）**，是它的「手和脚」，而不只是「笼子」。

> **一句话定义**：Agent 沙箱 = 一个远程、可编程、一次性（或可持久）的计算环境，通过 API / MCP 暴露给 Agent 调用。

---

## 2. 为什么 Agent 特别需要沙箱

| 需求 | 说明 |
|---|---|
| 执行不可信代码 | LLM 会幻觉、会写错，也会被 prompt injection 操纵 |
| 有状态 | Agent 常要「改文件 → 再跑 → 看结果」的多步循环 |
| 可回滚 | 出错要能丢弃环境重来 |
| 可并行 | 多个子任务 / 分支同时跑 |
| 可观测 | 要看到 stdout / stderr、文件变化、耗时 |
| 可回收 | 任务结束就销毁，不留副作用 |

---

## 3. 一个 Agent 沙箱应提供的能力

- **文件系统**：读 / 写 / 上传 / 下载，最好支持挂载数据卷
- **Shell / PTY**：交互式终端（很多 Agent 依赖 bash）
- **多语言运行时**：Python、Node、Go……按需
- **包管理**：`pip install` / `npm i`（这也是风险源）
- **网络策略**：默认拒绝或白名单出网 —— **最关键的安全开关**
- **快照 / 分叉（snapshot & fork）**：保存状态、复制多份并行探索
- **生命周期管理**：超时、保活、暂停 / 恢复、持久卷
- **可观测 / 审计**：日志、命令记录、资源用量
- **接口层**：SDK（`exec`、`files.write`）、HTTP API，现在越来越多以 **MCP server** 形式接入

---

## 4. 典型架构

```
Agent Loop (LLM)
   │  tool call: run("python train.py")
   ▼
Sandbox Control Plane   ← 创建 / 路由 / 鉴权 / 配额 / 快照
   │
   ▼
隔离后端 (Container / microVM / gVisor / WASM)
   │
   ▼
返回 stdout / stderr / exit code / 文件 diff → 回到 Agent
```

- **控制面（Control Plane）**：负责「环境怎么来、活多久、能碰什么」。
- **数据面（Data Plane）**：负责「真正跑」。

很多产品把数据面做成 **microVM 池**，控制面做**秒级调度**，以兼顾隔离强度与冷启动速度。

---

## 5. 隔离后端怎么选

| 后端 | 隔离强度 | 冷启动 | 适合场景 |
|---|---|---|---|
| Docker 容器 | 弱（共享内核） | 快 | 单租户、可信代码、开发起步 |
| gVisor | 中 | 中 | 多租户但不想上 VM |
| Firecracker microVM | 强 | 快（~百 ms） | 生产多租户首选 |
| 完整 VM | 强 | 慢 | computer-use / 需要完整 OS |
| WASM | 中（语言级） | 极快 | 轻量函数、Edge 执行 |

> **结论**：单租户图省事用 Docker；面向不可信用户 / 多租户必须上 **microVM 或 gVisor**。

---

## 6. Agent 特有的威胁模型

头号风险不是「逃逸」，而是 **Prompt Injection → 借 Agent 之手外泄**：

1. Agent 读了恶意网页 / 文档 → 被注入指令
2. 在沙箱里执行 `curl`，把环境变量里的 API Key 发出去
3. 沙箱没逃逸，但**数据已经泄漏**

其它风险：

- **供应链**：`pip install` 一个恶意包，就在沙箱里跑起来了
- **凭据泄漏**：把生产 secret 塞进环境变量是常见错误
- **资源滥用**：挖矿、刷 API、无限循环烧钱
- **横向移动**：沙箱内网能碰到云元数据服务（`169.254.169.254`）

### 对应防护（按重要性排序）

- ✅ **默认断网**，出网走白名单 + 审计
- ✅ 沙箱内**不放长期凭据**，用短期 token / 代理注入
- ✅ 每会话独立、生命周期短、任务完即销毁
- ✅ 挂载**只读**，限制 CPU / 内存 / 磁盘 / 时长
- ✅ 阻断云元数据地址，限制内网访问
- ✅ 记录所有命令，便于事后追责

---

## 7. 产品与项目版图

> ⚠️ 该领域变化很快，选型时务必核对各家最新的隔离后端、冷启动数据与出网策略。

- **专用沙箱云**：E2B、Daytona、Modal Sandboxes、Cloudflare Sandbox、Vercel Sandbox、Runloop、Blaxel、Northflank 等
- **大厂内置**：OpenAI 的 Code Interpreter / AgentKit、Anthropic 的 code execution 工具、Google 的 code execution
- **Agent 框架自带**：OpenHands 的 runtime、AutoGen 的 code executor、LangChain 的各种 executor
- **自建路线**：Kubernetes + Firecracker / Kata / gVisor
- **浏览器 / computer-use**：容器里跑 Playwright、Browserbase、Steel —— 属于「操作整台电脑」型沙箱

---

## 8. 什么时候不需要沙箱

- 只是结构化函数调用（查天气、查数据库）→ 普通 tool 即可
- 只在自家可信环境跑固定流程 → 不用

**只有出现「任意代码 / 任意 shell / 不可信输入驱动执行」时，才必须上沙箱。**

---

## 9. 自建的最小可用建议

1. **起步**：Docker + `--network none`（默认断网）+ 只读根 + 临时卷 + 超时
2. **要联网**：加 **egress 白名单代理**，绝不直连
3. **多租户 / 不可信**：换 **Firecracker microVM**，每会话一个 VM
4. **接入层**：包成 **MCP server**，把 `exec / read_file / write_file / upload` 暴露给 Agent
5. **始终**：**不注入长期 secret**，用完即销毁

---

## 10. 趋势

- 沙箱正成为 **Agent 基础设施的「原语」**，类似「数据库之于后端」
- **快照 / 分叉**被用于并行探索和 RL 训练（同一状态复制多份跑不同分支）
- 从「跑代码」扩展到「**操作完整电脑**」（带 GUI 的 VM）
- **MCP** 让沙箱接入标准化
- 安全重心从「防逃逸」转向「**防数据外泄 + 供应链 + 成本控制**」

---

## 附：核心结论速记

- 沙箱对 Agent 是**执行运行时**，不只是安全笼子。
- 隔离强度排序：Docker < gVisor < microVM < 完整 VM；WASM 是另一条轻量路线。
- 头号风险是 **prompt injection 导致的数据外泄**，不是沙箱逃逸。
- 最重要的三个开关：**默认断网、不放长期凭据、短生命周期**。
- 接入选 **MCP / SDK**，生命周期管理选**快照 + 分叉**。

---

## 相关文档

- 教程（多文件版）：[`agent-sandbox-tutorial/`](/agent-sandbox/guide/)
- 可运行实验（bwrap + MCP 示例）：[`agent-sandbox-lab/`](/agent-sandbox/lab/)
