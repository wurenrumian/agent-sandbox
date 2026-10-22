#!/usr/bin/env python3
"""检查仓库内 markdown 文件里的相对链接是否有效。

用法：
    python3 tools/check_links.py

说明：
    - 跳过 site/node_modules、site/dist、site/.astro、.git
    - 跳过外链（http/https/mailto）、锚点（#）与站点绝对路径（/...）
    - 退出码：0 全部有效；1 存在断链或索引不一致
    - Windows 上没有 `python3` 别名就写 `python`；`make check-links` 会自动挑一个
"""
import pathlib
import re
import sys

LINK_RE = re.compile(r"\]\(([^)]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "/")
IGNORE_DIRS = {"node_modules", "dist", ".astro", ".git", "__pycache__"}
# 生成物与过程记忆：都不是「仓库文档」，不作为检查对象
#   site/src/content/docs —— sync-docs.py 的产物（且已不入版本库）
#   tmp                   —— 过程记忆，不进版本库（见 tmp/README.md），里面的路径常指向仓库外
IGNORE_PATHS = ("site/src/content/docs", "tmp")


def is_ignored(path: pathlib.Path, root: pathlib.Path) -> bool:
    rel = path.relative_to(root)
    if any(part in IGNORE_DIRS for part in rel.parts):
        return True
    posix = rel.as_posix()
    return any(posix == p or posix.startswith(p + "/") for p in IGNORE_PATHS)


TUTORIAL_DIR = "agent-sandbox-tutorial"
SYNC_DOCS = "site/scripts/sync-docs.py"
ASTRO_CONFIG = "site/astro.config.mjs"

# sync-docs.py 的 PAGES 表：("源文件", "目标路由文件", "标题", "描述")
PAGES_ENTRY_RE = re.compile(r'\(\s*"([^"]+?\.md)"\s*,\s*"([^"]+?\.md)"')
# astro.config.mjs 的 sidebar：{ label: '...', link: '/guide/xxx/' }
SIDEBAR_LINK_RE = re.compile(r"link:\s*'(/guide/[^']*)'")
# 教程 README 的目录表行：| [04 架构](04-架构.md) | ... |
README_ROW_RE = re.compile(r"^\|\s*\[[^\]]*\]\(([^)]+?\.md)\)", re.M)
# 章内导航：上一章 / 下一章
NAV_LINK_RE = re.compile(r"\[[^\]]*(?:上一章|下一章)[^\]]*\]\(([^)]+)\)")
SECTION_RE = re.compile(r"^## (\d+)\.", re.M)
EXERCISE_RE = re.compile(r"^## 动手练习 (\d+)", re.M)
APPENDIX_SECTION_RE = re.compile(r"^## ([A-D])\.", re.M)
APPENDIX_NAME_RE = re.compile(r"^附录([A-D])-")


def check_indexes(root: pathlib.Path) -> list[str]:
    """检查教程章节在四处索引里是否一致，以及重编号类错误。

    四处索引：① 教程目录里的文件本身 ② 教程 README 的目录表
    ③ sync-docs.py 的 PAGES ④ astro.config.mjs 的 sidebar。
    另外查两类历史高发错误：章内导航指向的邻居、章内小节号与练习编号。
    """
    problems: list[str] = []
    tutorial = root / TUTORIAL_DIR
    if not tutorial.is_dir():
        return problems

    files = sorted(p.name for p in tutorial.glob("*.md") if p.name != "README.md")
    if not files:
        return problems

    sync_text = (root / SYNC_DOCS).read_text(encoding="utf-8", errors="ignore")
    pages: dict[str, str] = {}
    for src, target in PAGES_ENTRY_RE.findall(sync_text):
        if src.startswith(TUTORIAL_DIR + "/") and target.startswith("guide/"):
            pages[src.split("/", 1)[1]] = target

    astro_text = (root / ASTRO_CONFIG).read_text(encoding="utf-8", errors="ignore")
    sidebar: set[str] = set()
    for link in SIDEBAR_LINK_RE.findall(astro_text):
        route = link[len("/guide/"):].strip("/")
        sidebar.add("guide/index.md" if route == "" else f"guide/{route}.md")

    readme_text = (tutorial / "README.md").read_text(encoding="utf-8", errors="ignore")
    readme = [link for link in README_ROW_RE.findall(readme_text)]

    # ① 文件 ↔ ③ PAGES
    for name in files:
        if name not in pages:
            problems.append(f"[索引] {TUTORIAL_DIR}/{name} 没有进 {SYNC_DOCS} 的 PAGES（站点不会生成这个页面）")
    for name, target in pages.items():
        if not (tutorial / name).exists():
            problems.append(f"[索引] {SYNC_DOCS} 的 PAGES 指向不存在的 {TUTORIAL_DIR}/{name}")

    # ③ PAGES ↔ ④ sidebar
    guide_pages = set(pages.values())
    for target in sorted(guide_pages - sidebar):
        problems.append(f"[索引] {SYNC_DOCS} 生成了 {target}，但 {ASTRO_CONFIG} 的 sidebar 里没有它")
    for target in sorted(sidebar - guide_pages):
        problems.append(f"[索引] {ASTRO_CONFIG} 的 sidebar 指向 {target}，但 PAGES 不会生成它")

    # ① 文件 ↔ ② 教程 README 目录表
    for name in files:
        if name not in readme:
            problems.append(f"[索引] {TUTORIAL_DIR}/{name} 不在教程 README 的目录表里")
    for link in readme:
        if link.startswith(("http", "#")) or not (tutorial / link).exists():
            problems.append(f"[索引] 教程 README 的目录表指向不存在的 {link}")

    # 章内导航 + 小节号 + 练习编号
    for i, name in enumerate(files):
        text = (tutorial / name).read_text(encoding="utf-8", errors="ignore")
        head = "\n".join(text.splitlines()[:8])

        for link in NAV_LINK_RE.findall(head):
            target = link.strip()
            if target == "README.md":
                continue
            want = files[i + 1] if i + 1 < len(files) else None
            if target not in files:
                problems.append(f"[导航] {name} 的章内导航指向不存在的 {target}")
            else:
                j = files.index(target)
                if abs(j - i) != 1:
                    problems.append(
                        f"[导航] {name} 指向 {target}，但按阅读顺序它{'前面' if j < i else '后面'}还有别的章节（重编号漏改？）"
                    )

        # 小节号与练习编号必须与章号一致
        chapter = re.match(r"^(\d\d)-", name)
        appendix = APPENDIX_NAME_RE.match(name)
        if chapter:
            num = int(chapter.group(1))
            for found in SECTION_RE.findall(text):
                if int(found) != num:
                    problems.append(f"[编号] {name} 里有 `## {found}.x` 小节，章号是 {num:02d}（重编号漏改？）")
            for found in EXERCISE_RE.findall(text):
                if int(found) != num:
                    problems.append(f"[编号] {name} 的「动手练习 {found}」与章号 {num:02d} 不符")
        elif appendix:
            letter = appendix.group(1)
            for found in APPENDIX_SECTION_RE.findall(text):
                if found != letter:
                    problems.append(f"[编号] {name} 里有 `## {found}.x` 小节，附录号是 {letter}")

    return problems


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    broken: list[str] = []
    checked = 0

    for md in sorted(root.rglob("*.md")):
        if is_ignored(md, root):
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        for match in LINK_RE.finditer(text):
            link = match.group(1).split("#")[0].strip()
            if not link or link.startswith(SKIP_PREFIX):
                continue
            checked += 1
            target = (md.parent / link).resolve()
            if not target.exists():
                broken.append(f"{md.relative_to(root)} -> {link}")

    if broken:
        print(f"发现 {len(broken)} 个断链：")
        for b in broken:
            print("  -", b)

    index_problems = check_indexes(root)
    if index_problems:
        print(f"发现 {len(index_problems)} 处索引不一致：")
        for p in index_problems:
            print("  -", p)

    if broken or index_problems:
        return 1

    print(f"检查了 {checked} 个相对链接与四处索引，全部一致 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
