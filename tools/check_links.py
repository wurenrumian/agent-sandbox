#!/usr/bin/env python3
"""检查仓库内 markdown 文件里的相对链接是否有效。

用法：
    python3 tools/check_links.py

说明：
    - 跳过 site/node_modules、site/dist、site/.astro、.git
    - 跳过外链（http/https/mailto）、锚点（#）与站点绝对路径（/...）
    - 退出码：0 全部有效；1 存在断链
"""
import pathlib
import re
import sys

LINK_RE = re.compile(r"\]\(([^)]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "/")
IGNORE_DIRS = {"node_modules", "dist", ".astro", ".git", "__pycache__"}


def is_ignored(path: pathlib.Path, root: pathlib.Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.relative_to(root).parts)


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
        return 1

    print(f"检查了 {checked} 个相对链接，全部有效 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
