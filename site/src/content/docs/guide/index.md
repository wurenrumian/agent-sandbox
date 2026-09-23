---
title: "教程导航"
description: "从心智模型到动手搭建的 Agent 沙箱系统教程，共 11 章 + 3 附录。"
---

> 一套从「概念」到「动手搭建」的 Agent 沙箱教程。
> 11 章 + 3 附录，每章都能单独阅读。最后更新：2026-09-23（第二版，系统性加厚）


## 这套教程讲什么

Agent 沙箱 = **Agent 的计算机**。它既是限制 Agent 的「笼子」，也是让 Agent 真正能「做事」的手脚。

本教程把这件事拆成 **11 章 + 3 个附录**，从心智模型一路讲到可运行的沙箱实现。

每一章都包含：

- **本章导读**：这一章要回答什么问题、预计读多久；
- **原理与取舍**：不只给结论，还讲「为什么」和「不这样做的后果」；
- **具体例子 / 代码**：表格、图示、可直接运行或改写的最小示例；
- **常见误区**：容易踩的坑；
- **动手练习**：把抽象概念落到你自己的系统上。

## 适合谁

- 做 AI Agent / LLM 应用，需要让模型真正「跑代码、动文件」的开发者
- 想搞清楚 E2B、Daytona、Modal 这类产品到底在解决什么的人
- 关心 Agent 安全（prompt injection、数据外泄）的工程 / 安全同学

## 前置知识

不需要沙箱基础。只需要：

- 基本了解什么是 LLM / Agent / 工具调用
- 会一点命令行（读得懂 `docker run`、`sh` 即可）
- 想做实验的话：Linux 环境 + `bwrap` + `python3`

## 读完你能做到

- 说清楚沙箱在 Agent 架构里的位置
- 根据场景选对隔离后端
- 用 bwrap / Docker 搭一个「默认断网」的最小沙箱
- 识别并防住 Agent 特有的安全风险

## 预计时间

| 目标 | 时间 |
|---|---|
| 通读一遍 | 约 120–150 分钟 |
| 只读核心（00/01/02/05/06/09） | 约 80 分钟 |
| 加上动手实验 | 再 +40 分钟 |

---

## 目录

| 章节 | 内容 | 你会得到 |
|---|---|---|
| [00 心智模型](/agent-sandbox/guide/00-mental-model/) | 先建立正确的心智模型 | 修正「沙箱 = 牢房」的误解；说清赋能与约束、沙箱与容器/VM 的区别 |
| [01 定位](/agent-sandbox/guide/01-positioning/) | 从「防御机制」到「Agent 的手脚」 | 可写进设计文档的定义；明确沙箱**不**负责什么 |
| [02 为什么需要沙箱](/agent-sandbox/guide/02-why-sandbox/) | Agent 的六个刚需 | 一个多步任务的逐步拆解；三个 Agent 独有变量 |
| [03 能力清单](/agent-sandbox/guide/03-capabilities/) | 一个沙箱应提供的能力 | 最小接口集合、P0–P2 优先级、每项的坑与做法 |
| [04 架构](/agent-sandbox/guide/04-architecture/) | 控制面与数据面 | 职责拆解、完整时序、预热池与会话粘性、反模式清单 |
| [05 隔离后端选型](/agent-sandbox/guide/05-isolation-backends/) | Docker / gVisor / microVM / VM / WASM | 决策树、选择口诀、gVisor vs microVM、升级路径 |
| [06 威胁模型](/agent-sandbox/guide/06-threat-model/) | Prompt Injection 与数据外泄 | 两类注入、STRIDE、纵深防御链、白名单代理设计 |
| [07 产品版图](/agent-sandbox/guide/07-landscape/) | 托管与自建选项 | 评估产品的 8 个问题、选型三问、自建 vs 托管 |
| [08 何时不需要沙箱](/agent-sandbox/guide/08-when-not-needed/) | 避免过度设计 | 决策树、L0–L3 分级、过度设计的代价 |
| [09 实战搭建](/agent-sandbox/guide/09-hands-on/) | bwrap 沙箱 → Docker → MCP 工具 | 可运行步骤、参数对照、防目录穿越的 MCP 封装 |
| [10 趋势与延伸](/agent-sandbox/guide/10-trends/) | 沙箱要往哪走 | 五个趋势、八条延伸轴、按角色的下一步 |
| [附录 A 速记](/agent-sandbox/guide/appendix-a-cheatsheet/) | 核心结论 | 分主题的一句话版本 + 30 秒决策流 |
| [附录 B 术语表](/agent-sandbox/guide/appendix-b-glossary/) | 术语解释 | 按主题分组的 40+ 术语，含「为什么重要」 |
| [附录 C 安全检查清单](/agent-sandbox/guide/appendix-c-security-checklist/) | 上线前逐条核对 | 带红线的清单 + 最小可执行配置 |

---

## 学习路径

```
00 心智模型 ─► 01 定位 ─► 02 为什么 ─► 03 能力 ─► 04 架构
   ─► 05 选型 ─► 06 威胁模型 ─► 07 产品版图 ─► 08 何时不需要
   ─► 09 实战搭建 ─► 10 趋势与延伸
```

**按角色选路径：**

| 你是 | 建议顺序 |
|---|---|
| 应用开发者 | 00 → 02 → 03 → 04 → 05 → 09 → 附录C |
| 架构 / 选型 | 00 → 01 → 04 → 05 → 07 → 08 |
| 安全同学 | 01 → 06 → 附录C |
| 快速了解 | 00 → 01 → 06 → 附录A |

---

## 如何使用本教程

1. **顺序读**：每章末尾都有「动手练习」，建议至少做一遍，把抽象概念落到你自己的系统上。
2. **跳读**：每章开头有「本章导读」，结尾有上一章 / 下一章导航，可按角色路径跳读。
3. **动手**：第 9 章配了可运行的实验，代码在 [`../agent-sandbox-lab/`](/agent-sandbox/lab/)。

配套代码与实验（含实测记录）：

```bash
cd ../agent-sandbox-lab
./run_all.sh | tee RESULTS.md
./sandbox_run.py 'python3 /work/agent_code.py'
```

---

## 相关文档

- [资料包总入口](/agent-sandbox/)
- [速查 / 参考版 `ai-agent-sandbox.md`](/agent-sandbox/reference/)
- [可运行实验 `agent-sandbox-lab/`](/agent-sandbox/lab/)

---

## 更新记录

| 日期 | 变更 |
|---|---|
| 2026-09-23 | 初版：11 章 + 3 附录，配套 bwrap 实验 |
| 2026-09-23 | 第二版：全部章节系统性加厚——新增本章导读、原理与取舍、代码示例、常见误区、小结；附录 A/B/C 扩充为分主题速记、40+ 术语、带红线的检查清单 |

---
