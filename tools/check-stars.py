#!/usr/bin/env python3
"""批量复查教程里那些「易腐数字」：star 数、许可、归档状态、最后推送时间。

用法：
    python tools/check-stars.py                    # 跑默认清单
    python tools/check-stars.py --top 5            # 只看 star 最高的 5 个
    python tools/check-stars.py --repo owner/name  # 只查这几个（可重复）
    python tools/check-stars.py --json             # 机器可读
    python tools/check-stars.py --timeout 20       # 单个请求的上限秒数，默认 10

为什么存在：
    `agent-sandbox-tutorial/附录D-证据与数据源.md` 的 D.2 教了「30 秒批量自查」，
    但每次复验都要手抄一遍仓库名、手拼一遍命令。这个脚本把清单焊在代码里，
    「重查一遍」于是变成一条命令；清单要改也只有下面一处。
    本机没有 `python3` 这个别名，所以上面的命令一律写 `python`。

输出：
    一行一个项目，字段顺序为 stars / license / archived / pushed_at / full_name，按 stars 降序。
    行尾可能带标记：[archived]（仓库已归档）、[stale]（最后推送超过 60 天）、
    renamed: 旧名 → 新名（仓库改过名，API 返回的 full_name 与请求的不一致）。
    这三样才是复验时真正要看的：star 数是历史热度，活不活着看另外三个字段。
    数据行（以及 --json 的 JSON）走 stdout，失败明细与汇总走 stderr，
    所以 `python tools/check-stars.py --json > out.json` 拿到的是干净的 JSON。

退出码：
    0 正常；1 一个仓库都没查成；2 撞上 GitHub 的速率限制。

关于 token：
    GitHub REST API 对未认证请求的配额很低（每小时几十次量级），够跑一遍默认清单，再多就不够。
    脚本会读环境变量 GITHUB_TOKEN，有就带上，没有也能跑——别把 token 写进这个文件。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com/repos/"
USER_AGENT = "agent-sandbox-tutorial-check-stars"
STALE_AFTER_DAYS = 60
RATE_LIMIT_CODES = {403, 429}

# 默认清单：主检出这两份文件里出现过的 owner/repo，一个都没有编。
#   agent-sandbox-tutorial/附录D-证据与数据源.md  —— D.4 分类清单，以及 D.4 末尾的复验段落
#   agent-sandbox-tutorial/08-产品版图.md         —— 8.2.1–8.2.4 四张表，以及 8.1 / 8.3 正文
# 同一仓库在 D.4 和第 8 章各出现一次是常态，这里按名字去重。
# 唯一刻意保留的重复是改名前后两个地址各留一行：D.4 复验段（2026-10-22）记录了两起漂移，
# 这样一次普通运行就能看见 API 的 302 最终落在哪里——这正是复验时要盯的东西。
DEFAULT_REPOS: list[str] = [
    # —— 第 8 章 8.2.1：通用 agent 沙箱运行时 ——
    "opensandbox-group/OpenSandbox",
    "e2b-dev/E2B",
    # 8.2.1 表里用的还是旧地址；D.4 复验段说它已归到 superradcompany/microsandbox（见本清单末尾）
    "microsandbox/microsandbox",
    "smol-machines/smolvm",
    "agent-infra/sandbox",
    "rivet-dev/agentos",
    "strukto-ai/mirage",
    "earendil-works/gondolin",
    "perplexityai/SPACE",
    "BitMiracle-AI/Dormice",
    "langgenius/dify-sandbox",
    "cloudflare/sandbox-sdk",
    "agentbay-ai/wuying-agentbay-sdk",
    "vndee/llm-sandbox",
    "clawkwork/clawk",
    # —— 第 8 章 8.2.2：OS 级 / 进程级围栏 ——
    "anthropics/sandbox-runtime",
    "nolabs-ai/nono",
    # —— 第 8 章 8.2.3：coding agent 的编排层 ——
    "trycua/cua",
    "coder/coder",
    "gitpod-io/gitpod",
    "mattpocock/sandcastle",
    "dagger/container-use",
    "superagent-ai/vibekit",
    "vercel-labs/coding-agent-template",
    # —— 第 8 章 8.2.4：底座与执行引擎 ——
    "firecracker-microvm/firecracker",
    "google/gvisor",
    "judge0/judge0",
    "engineer-man/piston",
    # —— 附录 D.4 与第 8 章 8.1 / 8.3 点到、但没进 8.2 四张表的条目 ——
    "kubernetes-sigs/agent-sandbox",  # D.4 + 8.1；8.2 表里未列
    "daytonaio/daytona",  # D.4 + 8.3①：71.5k ★ 但已 archived，复验必看
    "bytedance/deer-flow",  # D.4 + 8.3②：agent 平台，不是沙箱方案
    "openclaw/openclaw",  # D.4 + 8.3②：同上
    # —— 附录 D.4 末尾的复验段（2026-10-22）：两起改名，旧地址靠 302 跳转仍能打开 ——
    "superradcompany/microsandbox",
    "anthropic-experimental/sandbox-runtime",
    # 注：D.4 与 8.3② 都提到 OpenHands（91.4k，MIT），但两处都只给了项目名、没给 owner，
    # 所以这里不收录——宁可少一行，也不替它编一个地址。
]


class RateLimited(Exception):
    """GitHub 的配额用完了：重试没有意义，得等窗口重置或者带上 token。"""


class RepoFailure(Exception):
    """单个仓库查不动（404 / 超时 / 网络抖动）：跳过它，别把整批拖下水。"""


# —— 默认清单之外的动静，只有这三件事 ——


def build_request(repo: str, token: str | None) -> urllib.request.Request:
    request = urllib.request.Request(API + repo.strip().strip("/"))
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", USER_AGENT)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    return request


def fetch_repo(repo: str, timeout: float, token: str | None) -> dict:
    """查一个仓库，返回 GitHub 的 JSON。失败时抛 RepoFailure 或 RateLimited。"""
    try:
        with urllib.request.urlopen(build_request(repo, token), timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in RATE_LIMIT_CODES:
            raise RateLimited(rate_limit_hint(error, token)) from None
        raise RepoFailure(f"HTTP {error.code}") from None
    except TimeoutError:
        raise RepoFailure(f"超时（超过 {timeout:g} 秒）") from None
    except urllib.error.URLError as error:
        raise RepoFailure(f"网络错误：{error.reason}") from None
    except json.JSONDecodeError:
        raise RepoFailure("返回的不是 JSON") from None


def rate_limit_hint(error: urllib.error.HTTPError, token: str | None) -> str:
    headers = error.headers or {}
    lines = [
        f"GitHub 拒绝了这次查询（HTTP {error.code}）：未认证请求的配额很低，一小时只有几十次，",
        "查大一批就会撞上。",
    ]
    remaining = headers.get("x-ratelimit-remaining")
    if remaining is not None:
        lines.append(f"配额剩余：{remaining}")
    reset = headers.get("x-ratelimit-reset") or ""
    if reset.isdigit():
        local = datetime.fromtimestamp(int(reset), timezone.utc).astimezone()
        lines.append(f"配额重置（本地时间）：{local:%Y-%m-%d %H:%M:%S}")
    if token:
        lines.append("你已经设了 GITHUB_TOKEN，这次还是被拦住了——多半要等窗口重置，或确认 token 没过期。")
    else:
        lines.append("想一次查更多，就设环境变量 GITHUB_TOKEN 再跑一遍；脚本会自动带上它。")
    lines.append("这次的结果不完整，别当成品用。")
    return "\n".join(lines)


# —— 一个查询循环 ——


def unique(names: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for name in names:
        seen.setdefault(name.strip().strip("/"), None)
    return list(seen)


def query_all(
    repos: list[str], timeout: float, token: str | None
) -> tuple[list[dict], list[tuple[str, str]], bool]:
    """逐个查询，返回（成功的行, 失败明细, 是否撞上速率限制）。

    撞上速率限制立刻停手：后面的请求只会同样失败，继续下去只是把失败列表拉长。
    """
    rows: list[dict] = []
    failures: list[tuple[str, str]] = []
    rate_limited = False

    for repo in repos:
        try:
            payload = fetch_repo(repo, timeout, token)
        except RateLimited as error:
            failures.append((repo, "速率限制"))
            rate_limited = True
            print(f"\n{error}\n", file=sys.stderr)
            break
        except RepoFailure as error:
            failures.append((repo, str(error)))
            continue

        rows.append(
            {
                "requested": repo,
                "full_name": payload.get("full_name") or repo,
                "stars": payload.get("stargazers_count", 0),
                "license": (payload.get("license") or {}).get("spdx_id") or "-",
                "archived": bool(payload.get("archived")),
                "pushed_at": payload.get("pushed_at") or "",
                "renamed_from": None,
                "stale": False,
            }
        )

    return rows, failures, rate_limited


def mark_staleness(rows: list[dict], now: datetime | None = None) -> None:
    """补上两个复验标记：改名 + 超过 60 天没推送。就地对行做标记。"""
    now = now or datetime.now(timezone.utc)
    for row in rows:
        if row["full_name"].lower() != row["requested"].lower():
            row["renamed_from"] = row["requested"]
        pushed = parse_time(row["pushed_at"])
        # 时间戳读不出来，比 60 天没动更该警惕，所以也算 stale。
        row["stale"] = pushed is None or now - pushed > timedelta(days=STALE_AFTER_DAYS)


# —— 一个渲染函数 ——


def render_line(row: dict) -> str:
    marks: list[str] = []
    if row["archived"]:
        marks.append("[archived]")
    if row["stale"]:
        marks.append("[stale]")
    if row["renamed_from"]:
        marks.append(f"renamed: {row['renamed_from']} → {row['full_name']}")
    tail = "  " + " ".join(marks) if marks else ""
    return (
        f"{row['stars']:>7}  {row['license']:<12} "
        f"archived={str(row['archived']):<5} {row['pushed_at']:<20}  {row['full_name']}{tail}"
    )


def payload_json(
    rows: list[dict], failures: list[tuple[str, str]], rate_limited: bool, shown: list[dict]
) -> dict:
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fetched": len(rows),
        "returned": len(shown),
        "rate_limited": rate_limited,
        "failed": [{"repo": repo, "error": reason} for repo, reason in failures],
        "repos": shown,
    }


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        # Python 3.10 的 fromisoformat 不认结尾的 Z，先换成 +00:00。
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


# —— 入口 ——


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="复查仓库的 star / 许可 / 归档 / 最后推送时间（GitHub REST API，无需第三方库）。",
        epilog="不带 --repo 时使用脚本内置的默认清单，来源见文件顶部说明。",
    )
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        metavar="OWNER/NAME",
        dest="repos",
        help="只查这些仓库，可重复；给了就完全覆盖默认清单。",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON，便于喂给别的脚本。")
    parser.add_argument("--top", type=int, metavar="N", help="只打印 star 最高的 N 个。")
    parser.add_argument(
        "--timeout", type=float, default=10.0, metavar="SECONDS", help="单个请求的超时秒数，默认 10。"
    )
    return parser.parse_args(argv)


def validate(names: list[str]) -> str | None:
    for name in names:
        if name.count("/") != 1 or any(ch.isspace() for ch in name):
            return name
    return None


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top is not None and args.top < 1:
        print("--top 要大于 0。", file=sys.stderr)
        return 1
    if args.timeout <= 0:
        print("--timeout 要大于 0。", file=sys.stderr)
        return 1

    bad = validate(args.repos)
    if bad:
        print(f"--repo 要写成 owner/name，这个不对：{bad}", file=sys.stderr)
        return 1

    token = os.environ.get("GITHUB_TOKEN") or None
    targets = unique(args.repos or DEFAULT_REPOS)

    rows, failures, rate_limited = query_all(targets, args.timeout, token)
    mark_staleness(rows)
    rows.sort(key=lambda row: (-row["stars"], row["full_name"]))
    shown = rows[: args.top] if args.top else rows

    if args.json:
        print(json.dumps(payload_json(rows, failures, rate_limited, shown), ensure_ascii=False, indent=2))
    else:
        for row in shown:
            print(render_line(row))

    if failures:
        print(f"\n跳过 {len(failures)} 个失败的仓库：", file=sys.stderr)
        for repo, reason in failures:
            print(f"  - {repo}: {reason}", file=sys.stderr)
    print(f"查到 {len(rows)} 个，显示 {len(shown)} 个，失败 {len(failures)} 个。", file=sys.stderr)
    if not token:
        print("（未设 GITHUB_TOKEN，用的是未认证配额。）", file=sys.stderr)

    if rate_limited:
        return 2
    if not rows:
        print("一个都没查成，检查网络或仓库名。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())