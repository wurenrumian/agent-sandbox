# AI Agent 沙箱（Sandbox）资料包

[![在线文档](https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF%E6%96%87%E6%A1%A3-wurenrumian.github.io-blue)](https://wurenrumian.github.io/agent-sandbox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 关于「AI Agent 执行沙箱」的一套完整资料：**概念参考 + 系统教程 + 可运行实验**。
> 最后更新：2026-09-23

---

## 这是什么

LLM 只能「说」，要真正「做」——跑代码、改文件、装依赖、发请求——就需要一个受控的执行环境，这就是 **Agent 沙箱**。

一句话：**Agent 沙箱 = Agent 的计算机**。它既是限制 Agent 的「笼子」，也是让 Agent 能干活的手脚。

本资料包从三个层次讲清楚它：

| 层次 | 目录 | 适合 |
|---|---|---|
| 📄 速查 / 参考 | [`ai-agent-sandbox.md`](ai-agent-sandbox.md) | 已有概念，想快速查 |
| 📚 系统教程 | [`agent-sandbox-tutorial/`](agent-sandbox-tutorial/README.md) | 想从零系统学习 |
| 🧪 可运行实验 | [`agent-sandbox-lab/`](agent-sandbox-lab/README.md) | 想动手验证 |
| 🌐 在线文档站 | [`site/`](site/README.md) | 想在浏览器里读 |

> 在线地址：**https://wurenrumian.github.io/agent-sandbox/**（由 `site/` 构建，Astro + Starlight）

---

## 目录结构

```
.
├── README.md                       # 本文件：总入口
├── ai-agent-sandbox.md             # 参考版：10 个主题速查
├── agent-sandbox-tutorial/         # 教程版：11 章 + 3 附录
│   ├── README.md                   # 教程导航
│   ├── 00-心智模型.md
│   ├── 01-定位.md
│   ├── 02-为什么需要沙箱.md
│   ├── 03-能力清单.md
│   ├── 04-架构.md
│   ├── 05-隔离后端选型.md
│   ├── 06-威胁模型.md
│   ├── 07-产品版图.md
│   ├── 08-何时不需要沙箱.md
│   ├── 09-实战搭建.md
│   ├── 10-趋势与延伸.md
│   ├── 附录A-速记.md
│   ├── 附录B-术语表.md
│   └── 附录C-安全检查清单.md
└── agent-sandbox-lab/              # 实验版：真实可跑的沙箱
    ├── README.md
    ├── sandbox_run.py              # bwrap 沙箱执行包装器
    ├── run_all.sh                  # 一键跑全部实验
    ├── RESULTS.md                  # 实测输出记录
    ├── exp/                        # 5 个隔离实验
    ├── code/sandbox_mcp.py         # 把沙箱包成 MCP server
    └── work/agent_code.py          # 模拟「Agent 生成的代码」

site/                               # Astro 文档站（部署到 GitHub Pages）
```

---

## 快速开始

**只想快速了解** → 读 [`ai-agent-sandbox.md`](ai-agent-sandbox.md)（约 10 分钟）。

**想系统学习** → 从 [`agent-sandbox-tutorial/00-心智模型.md`](agent-sandbox-tutorial/00-心智模型.md) 开始，按顺序读到第 10 章（全套约 120–150 分钟；每章含导读、原理取舍、代码示例、常见误区与动手练习）。

**想动手跑** → 直接进实验目录：

```bash
cd agent-sandbox-lab
chmod +x exp/*.sh run_all.sh sandbox_run.py
./run_all.sh | tee RESULTS.md          # 跑全部实验
./sandbox_run.py 'echo hello; id'      # 用沙箱执行任意命令
```

> 实验不需要 Docker、不需要 root，普通 Linux 用户即可运行（依赖 `bwrap` + `python3`）。

## 常用命令

根目录提供了 `Makefile`：

```bash
make help          # 显示所有命令
make lab           # 运行全部沙箱实验
make check-links   # 检查所有 markdown 链接
make site-sync     # 从仓库 markdown 重新生成站点内容
make site-dev      # 启动文档站开发服务器
make site-build    # 构建文档站
make clean         # 清理实验生成物与缓存
```

---

## 按角色的阅读路径

| 你是 | 建议路径 |
|---|---|
| 应用开发者 | 00 → 02 → 03 → 04 → 05 → 09 → 附录C |
| 架构 / 选型 | 00 → 01 → 04 → 05 → 07 → 08 |
| 安全同学 | 01 → 06 → 附录C → 实验 05 |
| 快速了解 | 参考版 `ai-agent-sandbox.md` + 附录A |
| 想动手 | 直接跑 `agent-sandbox-lab/`，再回头看第 9 章 |

---

## 核心观点速览

- 沙箱对 Agent 是**执行运行时**，不只是安全笼子。
- 隔离强度：Docker / bwrap < gVisor < microVM < 完整 VM；WASM 是另一条轻量路线。
- 头号风险是 **prompt injection 导致的数据外泄**，不是沙箱逃逸。
- 最重要的三个开关：**默认断网、不放长期凭据、短生命周期**。
- 判断是否需要沙箱：出现「**任意代码 / 任意 shell / 不可信输入驱动执行**」就上。
- 选型三问：**托管还是自建？隔离要多强？要 GPU 吗？**

---

## 实验环境

- 在 **Fedora Linux 44 (WSL2)** 上实测通过。
- 依赖：`bwrap`（bubblewrap）、`python3`；`unshare` 可选。
- 需要开启非特权 user namespace（`/proc/sys/user/max_user_namespaces > 0`）。
- 实测结果见 [`agent-sandbox-lab/RESULTS.md`](agent-sandbox-lab/RESULTS.md)。

---

## 说明

- 内容基于 2026-09 的知识整理；该领域（尤其产品版图）变化很快，选型前请核对最新信息。
- 实验中的沙箱是**教学实现**，生产环境请参考教程第 9.5 节与附录 C。
- 许可：[MIT](LICENSE)。
