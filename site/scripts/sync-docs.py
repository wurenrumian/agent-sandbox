#!/usr/bin/env python3
"""把仓库根目录的 markdown 文档同步到 Astro Starlight 的内容目录。

做三件事：
  1. 复制正文（去掉重复的 H1 与手工导航行）
  2. 补上 Starlight 需要的 frontmatter（title / description）
  3. 把仓库内的相对链接改写为站点路由；指向代码文件的链接改到 GitHub

用法（在 site/ 目录下）：
    python3 scripts/sync-docs.py
    # Windows 上没有 python3 别名就写 python；仓库根的 make site-sync 会自动挑一个
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
REPO = SITE.parent
DOCS = SITE / "src" / "content" / "docs"

# 必须与 astro.config.mjs 的 base 保持一致
BASE = "/agent-sandbox"

GITHUB_BLOB = "https://github.com/wurenrumian/agent-sandbox/blob/main"

# (源文件, 目标路由文件, 标题, 描述)
PAGES = [
    ("README.md", "index.md", "AI Agent 沙箱",
     "关于 AI Agent 执行沙箱的一套完整资料：概念参考、系统教程与可运行实验。"),
    ("agent-sandbox-tutorial/README.md", "guide/index.md", "教程导航",
     "从心智模型到动手搭建的 Agent 沙箱系统教程，共 12 章 + 4 附录。"),
    ("agent-sandbox-tutorial/00-心智模型.md", "guide/00-mental-model.md", "00 心智模型",
     "先建立正确的心智模型：沙箱是 Agent 的计算机。"),
    ("agent-sandbox-tutorial/01-定位.md", "guide/01-positioning.md", "01 定位",
     "从防御机制到 Agent 的手脚：赋能与约束。"),
    ("agent-sandbox-tutorial/02-为什么需要沙箱.md", "guide/02-why-sandbox.md", "02 为什么需要沙箱",
     "Agent 的六个刚需：执行不可信代码、有状态、可回滚、可并行、可观测、可回收。"),
    ("agent-sandbox-tutorial/03-能力清单.md", "guide/03-capabilities.md", "03 能力清单",
     "一个 Agent 沙箱应提供的文件、Shell、网络、快照等能力，及优先级排序。"),
    ("agent-sandbox-tutorial/04-架构.md", "guide/04-architecture.md", "04 架构",
     "控制面与数据面，以及快照与分叉、pause / resume、出网控制、凭据保险箱与编排接入。"),
    ("agent-sandbox-tutorial/05-隔离后端选型.md", "guide/05-isolation-backends.md", "05 隔离后端选型",
     "五类隔离边界（microVM / 用户态内核 / 容器+加固 / OS 系统调用策略 / WASM）与四个配套机制。"),
    ("agent-sandbox-tutorial/06-威胁模型.md", "guide/06-threat-model.md", "06 威胁模型",
     "Prompt Injection 与数据外泄、STRIDE 视角与防护清单。"),
    ("agent-sandbox-tutorial/07-场景与成本.md", "guide/07-scenario-cost.md", "07 场景与成本",
     "按四个属性描述场景，九个场景的硬需求与主导成本，场景→成本矩阵与开源首选。"),
    ("agent-sandbox-tutorial/08-产品版图.md", "guide/08-landscape.md", "08 产品版图",
     "八类产品分类、1k+ stars 开源项目盘点（含快照日期）、尽调 8 问、选型三问与自建 vs 托管。"),
    ("agent-sandbox-tutorial/09-何时不需要沙箱.md", "guide/09-when-not-needed.md", "09 何时不需要沙箱",
     "避免过度设计的决策树与代价分析。"),
    ("agent-sandbox-tutorial/10-实战搭建.md", "guide/10-hands-on.md", "10 实战搭建",
     "用 bwrap 与 Docker 搭建可运行的沙箱，并封装为 MCP 工具。"),
    ("agent-sandbox-tutorial/11-趋势与延伸.md", "guide/11-trends.md", "11 趋势与延伸",
     "沙箱的五个趋势、八条延伸轴与四个最有价值的方向。"),
    ("agent-sandbox-tutorial/附录A-速记.md", "guide/appendix-a-cheatsheet.md", "附录 A 速记",
     "核心结论速记，一句话版本。"),
    ("agent-sandbox-tutorial/附录B-术语表.md", "guide/appendix-b-glossary.md", "附录 B 术语表",
     "microVM / gVisor / TEE / egress 等术语解释。"),
    ("agent-sandbox-tutorial/附录C-安全检查清单.md", "guide/appendix-c-security-checklist.md", "附录 C 安全检查清单",
     "上线前的隔离、网络、凭据、资源、可观测与合规核对清单。"),
    ("agent-sandbox-tutorial/附录D-证据与数据源.md", "guide/appendix-d-evidence.md", "附录 D 证据与数据源",
     "教程里每个易腐数字的出处、快照日期与自查方法。"),
    ("agent-sandbox-lab/README.md", "lab/index.md", "实验说明",
     "用 Linux namespaces 与 bubblewrap 做的真实可跑沙箱实验。"),
    ("agent-sandbox-lab/RESULTS.md", "lab/results.md", "实测结果",
     "五个隔离实验的真实输出记录。"),
    ("agent-sandbox-lab/code/README.md", "lab/code.md", "配套代码",
     "沙箱执行包装器与 MCP server 示例。"),
    ("ai-agent-sandbox.md", "reference.md", "速查参考",
     "10 个主题的速查版：定位、能力、架构、选型、威胁、产品、趋势。"),
]

NAV_RE = re.compile(r"^\s*(\[←|\[下一章|\[返回目录)")
H1_RE = re.compile(r"^#\s+\S")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def build_route_map() -> dict[Path, str]:
    routes: dict[Path, str] = {}
    for src, target, _title, _desc in PAGES:
        route = "/" + target[:-3] + "/"          # 去掉 .md
        route = route.replace("/index/", "/")     # index → 目录首页
        routes[(REPO / src).resolve()] = route
    return routes


def resolve_link(raw: str, src_file: Path, routes: dict[Path, str]) -> str:
    """把仓库内相对链接改写为站点路由或 GitHub 链接。"""
    if raw.startswith(("http://", "https://", "mailto:", "#")):
        return raw

    path_part, _, anchor = raw.partition("#")
    if not path_part:
        return raw

    target = (src_file.parent / path_part).resolve()

    # 目录 → 其 README
    if target.is_dir():
        target = (target / "README.md").resolve()

    if target in routes:
        return BASE + routes[target] + (f"#{anchor}" if anchor else "")

    # 指向仓库内其它文件（代码等）→ GitHub
    try:
        # as_posix()：Windows 上 Path 会给出反斜杠，链接里必须用正斜杠
        rel = target.relative_to(REPO).as_posix()
        return f"{GITHUB_BLOB}/{rel}" + (f"#{anchor}" if anchor else "")
    except ValueError:
        return raw


def clean_body(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if NAV_RE.match(line):
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            if i < len(lines) and lines[i].strip() == "---":
                i += 1
            continue
        out.append(line)
        i += 1

    # 去掉开头重复的 H1（标题由 frontmatter 提供）
    while out and out[0].strip() == "":
        out.pop(0)
    if out and H1_RE.match(out[0]):
        out.pop(0)
    while out and out[0].strip() == "":
        out.pop(0)

    # 去掉正文最开始的连续分隔线
    while out and out[0].strip() == "---":
        out.pop(0)
        while out and out[0].strip() == "":
            out.pop(0)

    return "\n".join(out).rstrip() + "\n"


def rewrite_links(text: str, src_file: Path, routes: dict[Path, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        return "](" + resolve_link(m.group(1).strip(), src_file, routes) + ")"

    return LINK_RE.sub(repl, text)


def quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def main() -> None:
    routes = build_route_map()
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    for src, target, title, desc in PAGES:
        src_file = (REPO / src).resolve()
        text = src_file.read_text(encoding="utf-8")

        frontmatter = ["---", f"title: {quote(title)}", f"description: {quote(desc)}"]
        if target == "index.md":
            frontmatter += [
                "template: splash",
                "hero:",
                f"  tagline: {quote(desc)}",
                "  actions:",
                "    - text: 开始阅读教程",
                f"      link: {BASE}/guide/",
                "      icon: right-arrow",
                "    - text: 运行实验",
                f"      link: {BASE}/lab/",
                "      icon: external",
                "      variant: minimal",
            ]
        frontmatter.append("---")

        body = clean_body(text)
        body = rewrite_links(body, src_file, routes)
        if target == "lab/results.md":
            # 终端输出用代码块包裹，保留原始排版
            body = "```text\n" + body.rstrip("\n") + "\n```\n"

        dest = DOCS / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(frontmatter) + "\n\n" + body, encoding="utf-8")
        print(f"  {src:45s} -> src/content/docs/{target}")

    # 自定义 404 页（非仓库文档，由脚本生成）
    not_found = DOCS / "404.md"
    not_found.write_text(
        "---\n"
        'title: "页面不存在"\n'
        "template: splash\n"
        "editUrl: false\n"
        "---\n\n"
        "你访问的页面不存在。\n\n"
        f"[返回首页]({BASE}/) · [开始阅读教程]({BASE}/guide/)\n",
        encoding="utf-8",
    )
    print(f"  {'(generated)':45s} -> src/content/docs/404.md")

    print(f"\n同步完成：{len(PAGES)} 个页面 + 404 -> {DOCS}")


if __name__ == "__main__":
    main()
