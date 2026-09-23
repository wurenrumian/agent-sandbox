#!/usr/bin/env python3
"""检查所有 markdown 文件里的相对链接是否有效。

用法：
    python3 tools/check_links.py

退出码：0 全部有效；1 存在断链。
"""
import pathlib
import re
import sys

LINK_RE = re.compile(r"\]\(([^)]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#")


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    broken: list[str] = []
    checked = 0

    for md in sorted(root.rglob("*.md")):
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
