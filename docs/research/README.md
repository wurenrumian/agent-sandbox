---
title: 调研档案：agent sandbox 的两个问题
type: research
status: draft
created: 2026-10-21
updated: 2026-10-22
tags: [agent-sandbox, research, index]
related: []
---

# agent sandbox 调研（两份原文）

## 一句话

这里是本项目自己做的两份调研原文。教程里那些带日期的数字和结论就是从这里摘的：第 7 章直接点名引用了 use-cases（正文里的「经调研 `agent-sandbox-use-cases.md`」），第 8 章的盘点表与附录 D 的数据和 survey 同源——这一条是核对得出的（教程正文并没有点名引用 survey，但第 8 章与附录 D 的 star / 许可逐条与它一致），属于本档案的归纳。它们不是第三方评测，是一次**固定日期**的 GitHub 实查加官方原文阅读，所以会随时间腐坏。

## 这两份是什么

| 文件 | 回答什么 | 教程里对应哪里 |
|---|---|---|
| [agent-sandbox-use-cases.md](./agent-sandbox-use-cases.md) | 场景怎么分类、每个场景的硬需求和主导成本是什么 | 第 7 章「场景与成本」 |
| [agent-sandbox-projects-survey.md](./agent-sandbox-projects-survey.md) | 开源项目有哪些、各自怎么隔离、怎么选 | 第 8 章「产品与项目版图」与 [附录 D「证据与数据源」](../../agent-sandbox-tutorial/附录D-证据与数据源.md) |

**谁写的**：本项目自己整理，不是厂商材料，也不是第三方评测机构的报告。写法是「机器能查的就查机器，剩下的读官方原文」，取信顺序写在附录 D 的 [D.3 来源等级表](../../agent-sandbox-tutorial/附录D-证据与数据源.md) 里。

## 采集时间与证据等级

- **采集日期 2026-10-21**。star 数、许可证（`license.spdx_id`）、归档状态（`archived`）全部来自 GitHub REST API 实查（`GET /repos/{owner}/{repo}`），不用网页缓存，不用博客转述。
- **复验日期 2026-10-22**，只复验了教程列出的关键项。复验发现两处仓库改名：`microsandbox/microsandbox` → `superradcompany/microsandbox`，`anthropic-experimental/sandbox-runtime` → `anthropics/sandbox-runtime`（旧地址靠 302 跳转仍能打开）。**下面两份原文停留在 2026-10-21 的旧名**，教程正文已改用新名，完整记录见附录 D 的 D.4。
- **star 数是单次快照，不是实时值**，也没有历史曲线。
- **性能数字（冷启动、并发密度、快照恢复开销）全部是官方宣称值，本项目没有本地基准**。这条口径和附录 D 的 [D.5 未做实测的声明](../../agent-sandbox-tutorial/附录D-证据与数据源.md) 一致：microVM 的「64ms P50 / 125ms P99」、microsandbox 的「<100ms」都属这一类，只当量级参考，不要当成自己环境里的承诺值。

一句话：**可信的是「当天实查到的数字」和「官方原文的说法」；不可信的是把它们当成今天的现状。**

## 这些数字会腐，怎么复查

star、许可、归档状态每月都在变。引用之前请照附录 D 的 [D.2 怎么自己复查](../../agent-sandbox-tutorial/附录D-证据与数据源.md) 跑一遍：一条 `curl` 查单仓库，一段标准库脚本批量查候选名单。判读只看三条：

- `archived=true` → 不再维护，直接淘汰；
- 许可为空或 `NOASSERTION` → 商用前必须读 `LICENSE` 原文；
- `pushed_at` 在近一两个月 → 才算活跃。

批量查 star 的脚本 `tools/check-stars.py` 也快有了；在它落地之前，先用附录 D.2 里的两段命令。