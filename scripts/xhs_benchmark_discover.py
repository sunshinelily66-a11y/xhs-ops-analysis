#!/usr/bin/env python3
"""Discover Xiaohongshu benchmark candidates via public search APIs.

This script does not scrape Xiaohongshu pages. It searches indexed public
results and saves candidate links for human review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import textwrap
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from daily_market_observer import fetch_json, post_json, read_optional, send_feishu  # noqa: E402


CANDIDATE_DIR = ROOT / "memory" / "xhs_benchmark" / "candidates"
QUERY_PATH = ROOT / "memory" / "xhs_benchmark" / "discovery_queries.md"
DEFAULT_QUERIES = [
    "site:xiaohongshu.com Codex",
    "site:xiaohongshu.com AI工具",
    "site:xiaohongshu.com AI编程",
    "site:xiaohongshu.com 小白学Python",
    "site:xiaohongshu.com AI工作流",
    "site:xiaohongshu.com Cursor",
    "site:xiaohongshu.com Claude Code",
    "site:xiaohongshu.com 自动化 工作流",
]

ACCOUNT_KEYWORDS = {
    "codex",
    "cursor",
    "claude",
    "python",
    "ai",
    "agent",
    "自动化",
    "工作流",
    "小白",
    "编程",
    "工具",
    "前端",
    "学习",
}


def week_id(now: dt.datetime) -> str:
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def clean(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def read_queries(limit: int) -> list[str]:
    if not QUERY_PATH.exists():
        return DEFAULT_QUERIES[:limit]
    queries = []
    for line in QUERY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            query = line[2:].strip()
            if query:
                queries.append(query)
        if len(queries) >= limit:
            break
    return queries or DEFAULT_QUERIES[:limit]


def search_brave(query: str, limit: int) -> list[dict]:
    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    if not api_key:
        return []
    url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(
        {"q": query, "count": limit}
    )
    data = fetch_json_with_headers(url, {"X-Subscription-Token": api_key})
    results = []
    for item in data.get("web", {}).get("results", []):
        results.append(
            {
                "title": clean(item.get("title")),
                "url": item.get("url", ""),
                "snippet": clean(item.get("description")),
                "source": "brave",
                "query": query,
            }
        )
    return results


def search_bing(query: str, limit: int) -> list[dict]:
    api_key = os.getenv("BING_SEARCH_API_KEY", "").strip()
    if not api_key:
        return []
    url = "https://api.bing.microsoft.com/v7.0/search?" + urllib.parse.urlencode(
        {"q": query, "count": limit}
    )
    data = fetch_json_with_headers(url, {"Ocp-Apim-Subscription-Key": api_key})
    results = []
    for item in data.get("webPages", {}).get("value", []):
        results.append(
            {
                "title": clean(item.get("name")),
                "url": item.get("url", ""),
                "snippet": clean(item.get("snippet")),
                "source": "bing",
                "query": query,
            }
        )
    return results


def search_serpapi(query: str, limit: int) -> list[dict]:
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        return []
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(
        {"engine": "google", "q": query, "api_key": api_key, "num": limit}
    )
    data = fetch_json(url)
    results = []
    for item in data.get("organic_results", [])[:limit]:
        results.append(
            {
                "title": clean(item.get("title")),
                "url": item.get("link", ""),
                "snippet": clean(item.get("snippet")),
                "source": "serpapi",
                "query": query,
            }
        )
    return results


def fetch_json_with_headers(url: str, headers: dict[str, str]) -> dict:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "xhs-benchmark-discover/1.0", **headers})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def discover(query: str, limit: int) -> list[dict]:
    provider = os.getenv("XHS_SEARCH_PROVIDER", "").strip().lower()
    providers = [provider] if provider else ["brave", "bing", "serpapi"]
    for name in providers:
        try:
            if name == "brave":
                results = search_brave(query, limit)
            elif name == "bing":
                results = search_bing(query, limit)
            elif name == "serpapi":
                results = search_serpapi(query, limit)
            else:
                results = []
            if results:
                return results
        except Exception as exc:
            print(f"warn: {name} search failed for {query}: {exc}")
    return []


def score_candidate(candidate: dict) -> tuple[int, int]:
    text = f"{candidate.get('title', '')} {candidate.get('snippet', '')}".lower()
    keyword_hits = sum(1 for keyword in ACCOUNT_KEYWORDS if keyword.lower() in text)
    xhs_bonus = 1 if "xiaohongshu.com" in candidate.get("url", "") else 0
    return keyword_hits + xhs_bonus, len(candidate.get("snippet", ""))


def dedupe(candidates: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for candidate in candidates:
        url = candidate.get("url", "")
        title = candidate.get("title", "")
        key = url or title
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def candidate_reason(candidate: dict) -> str:
    text = f"{candidate.get('title', '')} {candidate.get('snippet', '')}"
    hits = [keyword for keyword in sorted(ACCOUNT_KEYWORDS) if keyword.lower() in text.lower()]
    if hits:
        return "匹配关键词：" + "、".join(hits[:5])
    return "小红书同平台候选，需人工确认是否同赛道。"


def render_candidates(candidates: list[dict], now: dt.datetime, queries: list[str]) -> str:
    lines = [f"# 小红书 Benchmark 候选 - {week_id(now)}", ""]
    lines.append("## 说明")
    lines.append("- 这些是公开搜索发现的候选，不是已确认 benchmark 样本。")
    lines.append("- 看到飞书后，回到 Codex 里说：`保留 1,3,7`。")
    lines.append("- 我会把你确认的编号转入 `memory/xhs_benchmark/samples/`。")
    lines.append("")
    lines.append("## 搜索范围")
    for query in queries:
        lines.append(f"- `{query}`")
    lines.append("")

    if not candidates:
        lines.append("## 候选列表")
        lines.append("没有发现候选。请配置一个搜索 API secret：`BRAVE_SEARCH_API_KEY`、`BING_SEARCH_API_KEY` 或 `SERPAPI_API_KEY`。")
        return "\n".join(lines).strip() + "\n"

    lines.append("## 候选列表")
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            f"### {index}. {candidate.get('title') or 'unknown'}\n"
            f"- url: {candidate.get('url') or 'unknown'}\n"
            f"- source: {candidate.get('source') or 'unknown'}\n"
            f"- query: {candidate.get('query') or 'unknown'}\n"
            f"- snippet: {candidate.get('snippet') or 'unknown'}\n"
            f"- reason: {candidate_reason(candidate)}\n"
            f"- status: candidate\n"
        )
    return "\n".join(lines).strip() + "\n"


def save_candidates(report: str, now: dt.datetime) -> pathlib.Path:
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    path = CANDIDATE_DIR / f"{week_id(now)}.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-limit", type=int, default=int(os.getenv("XHS_QUERY_LIMIT", "8")))
    parser.add_argument("--per-query", type=int, default=int(os.getenv("XHS_RESULTS_PER_QUERY", "5")))
    parser.add_argument("--max-candidates", type=int, default=int(os.getenv("XHS_MAX_CANDIDATES", "20")))
    parser.add_argument("--save-report", action="store_true", default=os.getenv("SAVE_REPORT", "1") == "1")
    parser.add_argument("--no-feishu", action="store_true")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=8)))
    queries = read_queries(args.query_limit)
    candidates = []
    for query in queries:
        candidates.extend(discover(query, args.per_query))
    candidates = sorted(dedupe(candidates), key=score_candidate, reverse=True)[: args.max_candidates]
    report = render_candidates(candidates, now, queries)

    if args.save_report:
        path = save_candidates(report, now)
        print(f"saved candidates: {path}")

    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    secret = os.getenv("FEISHU_BOT_SECRET", "").strip() or None
    if webhook_url and not args.no_feishu:
        send_feishu(webhook_url, report, secret)
    else:
        print("FEISHU_WEBHOOK_URL not set; printing report only.")
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
