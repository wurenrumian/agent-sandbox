---
title: "附录 D 证据与数据源"
description: "教程里每个易腐数字的出处、快照日期与自查方法。"
---

> 本教程里所有 star 数、版本、时间点都是**易腐数字**——你读到的时候，它们多半已经旧了。
> 这个附录只做一件事：把「这些数字什么时候采的、怎么来的、怎么自己复查一遍」变成你能直接执行的东西。
> ⚠️ 先记住一条：**冷启动、并发密度、快照恢复这些性能数字，全部是官方宣称值，本项目没有任何本地基准**（详见 D.5）。
> 读法：D.1 看数据是哪天采的 → D.2 学会自己查 → D.3–D.4 看每条数字的来源 → D.5–D.6 看哪些话最不可靠 → D.7 把它变成一句习惯。

## D.1 快照声明

| 项 | 值 |
|---|---|
| 采集日期 | 2026-10-21 |
| 复验日期 | 2026-10-22（只复验了下文列出的关键项） |
| 采集方式 | GitHub REST API 实查（`GET /repos/{owner}/{repo}`），不用网页缓存、不用博客转述 |
| 覆盖范围 | 只覆盖**开源**项目；闭源沙箱云（Modal、Blaxel、Runloop、Vercel Sandbox 等）没有 star 概念，不在盘点内 |
| star 数性质 | **单次快照，不是实时值**；没有历史曲线 |

一句话：**本教程的 star 数是 2026-10-21 的一张照片，不是实时读数。** 超过一两个月请按 D.2 自己重查一遍。

## D.2 怎么自己复查

### 查什么、看哪些字段

| 要查什么 | 用哪个端点 | 看哪些字段 |
|---|---|---|
| 单仓库的数字与状态 | `GET https://api.github.com/repos/{owner}/{repo}` | `stargazers_count`、`license.spdx_id`、`pushed_at`、`archived` |
| 补漏：还有哪些项目没进盘点 | `GET https://api.github.com/search/repositories?q=topic:agent-sandbox&sort=stars&order=desc` | `items[].full_name`、`stargazers_count` |
| 项目**到底做什么** | 仓库 README 原文（`raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md`） | 官方自己的定位句，不是别人的转述 |

判读只看三条：

- `archived=true` → 不再维护，直接淘汰。Daytona 就是栽在这一条上（见 D.4）。
- 许可为空或 `NOASSERTION` → 商用前必须读 `LICENSE` 原文。
- `pushed_at` 在近一两个月 → 才算活跃；几个月没动就要警惕。

### 单仓库，一行命令

```bash
curl -s https://api.github.com/repos/e2b-dev/E2B \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); \
      print(d["stargazers_count"], d["license"]["spdx_id"] if d["license"] else None, \
            d["archived"], d["pushed_at"])'
```

### 30 秒批量自查

把下面 `repos` 一行换成你自己的候选名单即可。脚本只用标准库，改一行就能跑：

```bash
python3 - <<'PY'
import json, urllib.request
repos = ["opensandbox-group/OpenSandbox", "e2b-dev/E2B",
         "microsandbox/microsandbox", "smol-machines/smolvm",
         "kubernetes-sigs/agent-sandbox", "daytonaio/daytona"]
for r in repos:
    d = json.load(urllib.request.urlopen(f"https://api.github.com/repos/{r}"))
    lic = (d.get("license") or {}).get("spdx_id", "-")
    print(f'{d["stargazers_count"]:>7}  {lic:<12} archived={str(d["archived"]):<5} {d["pushed_at"]}  {d["full_name"]}')
PY
```

两点提示：未认证的 GitHub API 请求有很低的速率上限（每小时几十次量级，具体数值以官方文档为准），查十几个仓库没问题，再多就带上 token；Windows 本机没有 `python3` 别名，把命令里的 `python3` 换成 `python`。

## D.3 来源等级表

本项目取信的顺序，从高到低：

| 等级 | 来源 | 怎么用 | 例子 |
|---|---|---|---|
| ① 首选 | 项目官方 README / 官网原文 | 直接引用，正文写出来源 | E2B 官网自列 5 类场景；microsandbox「secrets never enter the VM」 |
| ① 机器可复查 | 平台自己的记录（GitHub API） | star / 许可 / 归档状态一律走这条 | 30 个项目的 star 全部来自 `stargazers_count` |
| ② 次选 | 官方文档与发布说明（release notes、定价页、API 文档） | 补 README 没写的细节：上限、计费、版本 | E2B fork 上限 100；Vercel Sandbox 按 active CPU 计费 |
| ③ 标明可用 | 调研者（本项目）的归纳 | 正文必须写成「（这是归纳，不是来源的说法）」 | 「每个场景只有一个主导成本项」 |
| ✗ 不用 | 二手博客、对比软文、聚合站 | 只用来**发现**候选，不用来**取数** | Daytona 闭源时间点先用文章定位，再回仓库核对 `archived` / `pushed_at` |

一句话：**能机器复查的就机器复查，剩下的一律读原文；别人嚼过的数字不要直接抄。**

## D.4 分类清单（第 8 章产品版图用到哪些数据）

第 8 章的开源盘点表里，每条数字都能在这张表里找到出处。

| 项目 | 教程里的声称 | 来源 | 快照日期 |
|---|---|---|---|
| OpenSandbox | 16.0k ★ / Apache-2.0 / Firecracker；宣称 64ms P50、125ms P99（10 并发）；Credential Vault | GitHub API + README 原文 | 2026-10-21 |
| E2B | 14.5k ★ / Apache-2.0 / Firecracker；fork 上限 100；pause/resume；egress 按 CIDR/hostname；凭据在代理注入 | GitHub API + e2b.dev 官网 | 2026-10-21 |
| microsandbox | 8.8k ★ / libkrun；启动 <100ms；fork / snapshot；macOS / Linux / Windows | GitHub API + README 原文 | 2026-10-21 |
| smolvm | 6.8k ★ / libkrun；「可分支的 microVM」 | GitHub API + README 原文 | 2026-10-21 |
| agent-infra/sandbox | 6.2k ★；单容器塞齐 Browser + Shell + VSCode + Jupyter + MCP | GitHub API + README 原文 | 2026-10-21 |
| kubernetes-sigs/agent-sandbox | 4.3k ★；6 类 use case、40+ 示例、WarmPool | GitHub API + 官方 Use Cases 文档 | 2026-10-21 |
| Anthropic `srt` | 5.6k ★；macOS Seatbelt / Linux bubblewrap + 网络过滤代理 | GitHub API + README 原文 | 2026-10-21 |
| nono | 4.6k ★；进程级零信任 | GitHub API + README 原文 | 2026-10-21 |
| firecracker / gvisor | 37.5k / 19.7k ★；底座技术 | GitHub API 实查 | 2026-10-21 |
| daytonaio/daytona | 71.5k ★ 但 `archived`；最后推送 2026-07-24；2026-06 起闭源 | GitHub API 实查 + 对比文章交叉核对 | 2026-10-22 复验 |
| OpenHands / deer-flow / openclaw | 91.4k / 84.2k / 392.7k ★；是 agent 平台，不是沙箱方案 | GitHub API 实查 | 2026-10-21 |
| Modal Sandboxes | Lovable 48 小时 100 万+ 沙箱、约 25 万次应用创建；Ramp 的后台编码 agent | Modal 官方公开材料 | 2026-10-21 |
| Hugging Face / Groq | 前者用 E2B 复现 DeepSeek-R1 的 RL 管线，后者用 E2B 做实时代码执行 | E2B 官网与公开案例 | 2026-10-21 |

第 8 章盘点表里其余项目的 star / 许可 / 隔离方式**同源**：GitHub API 实查 + README 原文，快照均为 2026-10-21，不复述。其中两个项目返回 `NOASSERTION`（`cloudflare/sandbox-sdk`、`vercel-labs/coding-agent-template`），它们的许可**未核实**，商用判断前需读 `LICENSE` 原文。

复验（2026-10-22）还发现两处漂移：`microsandbox/microsandbox` 已归到 `superradcompany/microsandbox`，`anthropic-experimental/sandbox-runtime` 已归到 `anthropics/sandbox-runtime`——API 返回的 `full_name` 换了，旧地址靠 302 跳转仍能打开（本教程正文已改用新名）。**这类改名和归档一样，是 star 快照之外必须一起看的字段。**

## D.5 ⚠️ 未做实测的声明

这一节是全篇最该先读的。

**本项目没有跑过任何本地基准。** 下列数字全部是**厂商或项目自己的宣称值**，没有在本机复现过：

| 数字 | 教程里从哪来 | 性质 |
|---|---|---|
| 冷启动（Firecracker 64ms P50 / 125ms P99；microsandbox <100ms） | 各自 README / 官网 | 官方宣称，未复现 |
| 并发密度（一台机器能跑多少沙箱） | 各家文档，口径互不相同 | 官方宣称，且定义不统一 |
| 快照 / 恢复开销（「毫秒级恢复」） | 官方描述 | 官方宣称，未复现 |

把这几行当作**量级参考**，不要当作你环境里的承诺值。要落到自己的选型上，就用各项目的 quickstart 跑一次最小压测——这是唯一能把「官方宣称」变成「你的实测」的动作。

## D.6 已知薄弱处

| 薄弱处 | 具体是什么 | 影响 |
|---|---|---|
| 单一来源 | 项目定位大多只有 README 一个来源，没有第三方独立评测 | 若是营销口径，本教程无法证伪 |
| 依赖厂商自述 | 性能、上限、并发全由官方提供 | 见 D.5 |
| 可能已过时 | star / 归档状态是 2026-10-21 快照，项目活跃度每月都在变 | 超过 1–2 个月必须按 D.2 重查 |
| 闭源覆盖不足 | 只收开源；Modal、Blaxel、Runloop、Vercel Sandbox 无 star 可比 | 不能据此得出「开源更好」的结论 |
| 场景覆盖不均 | 安全分析、CI/CD 两个场景样本最少 | 这两处结论最弱 |
| 成本模型空白 | 「每千次执行多少钱」完全没有数据，需实测或厂商报价 | 本教程不给成本数字 |
| 许可细节未核 | 两个 `NOASSERTION` 项目的许可未读原文 | 商用判断前必须补 |

## D.7 引用前问三句

引用任何数字之前，先问：

1. **哪天采的？**（没有日期的一律不采信）
2. **谁说的？**（机器实查 / 官方宣称 / 作者归纳，三者必须能分开）
3. **我能不能自己再查一遍？**（能，就用 D.2 的命令查）

三句都有答案，这个数字才进得了自己的结论。

---
