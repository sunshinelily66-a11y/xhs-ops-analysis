#!/usr/bin/env python3
"""Collect public AI-tool signals and push a concise report to Feishu.

This script is intentionally dependency-free so it can run on GitHub Actions
without setup friction. It uses public endpoints and stores only short summaries.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import pathlib
import re
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "memory" / "market" / "reports"
USER_AGENT = "xhs-ops-analysis-market-observer/1.0 (+https://github.com)"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"

CORE_KEYWORDS = {
    "codex",
    "claude code",
    "cursor",
    "ai coding",
    "coding agent",
    "agent",
    "python",
    "frontend",
    "automation",
    "workflow",
    "vibe coding",
}

PERSONA_KEYWORDS = {
    "beginner",
    "learn",
    "learning",
    "python",
    "workflow",
    "automation",
    "creator",
    "non developer",
    "小白",
    "学习",
    "工作流",
    "自动化",
}

RISK_KEYWORDS = {
    "funding",
    "valuation",
    "acquires",
    "stock",
    "rumor",
    "leak",
    "benchmark",
}

HEAT_SLOTS = 8
INTERESTING_SLOTS = 2


@dataclass
class Signal:
    source: str
    title: str
    url: str
    summary: str
    heat: str
    published: str
    signal_type: str
    relevance: str
    persona_fit: str
    migration_value: str
    risk: str


def fetch_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None, timeout: int = 60) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request_headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        response_body = response.read().decode("utf-8", errors="replace")
        if response.status >= 300:
            raise RuntimeError(f"POST {url} failed: {response.status} {response_body}")
        return json.loads(response_body)


def safe_fetch_json(url: str) -> dict | None:
    try:
        return fetch_json(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warn: failed to fetch {url}: {exc}")
        return None


def read_queries(limit: int = 14) -> list[str]:
    path = ROOT / "memory" / "market" / "queries.md"
    if not path.exists():
        return [
            "Codex AI coding agent workflow",
            "Claude Code vs Codex",
            "Cursor AI coding workflow",
            "AI coding agent beginner developer",
            "learn Python with AI tools",
        ]

    queries: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            query = line[2:].strip("` ")
            if query and "site:" not in query and query not in queries:
                queries.append(query)
        if len(queries) >= limit:
            break
    return queries


def read_optional(path: pathlib.Path, max_chars: int = 6000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")[:max_chars]


def clean(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def score_level(text: str, keywords: set[str]) -> str:
    lower = text.lower()
    hits = sum(1 for keyword in keywords if keyword in lower)
    if hits >= 3:
        return "high"
    if hits >= 1:
        return "medium"
    return "low"


def classify(title: str, summary: str) -> tuple[str, str, str, str, str]:
    text = f"{title} {summary}"
    lower = text.lower()
    relevance = score_level(text, CORE_KEYWORDS)
    persona_fit = score_level(text, PERSONA_KEYWORDS)
    risk = score_level(text, RISK_KEYWORDS)

    if any(word in lower for word in ["release", "launch", "changelog", "announcing", "update"]):
        signal_type = "product update"
    elif any(word in lower for word in ["how", "tutorial", "guide", "learn", "build"]):
        signal_type = "tutorial angle"
    elif any(word in lower for word in ["vs", "better", "worse", "debate", "why"]):
        signal_type = "debate"
    elif any(word in lower for word in ["problem", "pain", "struggle", "confusing", "hard"]):
        signal_type = "user pain"
    else:
        signal_type = "workflow pattern"

    if relevance == "high" and persona_fit in {"medium", "high"} and risk != "high":
        migration_value = "high"
    elif relevance in {"medium", "high"} and risk != "high":
        migration_value = "medium"
    else:
        migration_value = "low"

    return signal_type, relevance, persona_fit, migration_value, risk


def collect_hn(queries: list[str], per_query: int) -> list[Signal]:
    signals: list[Signal] = []
    for query in queries[:6]:
        url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
            {"query": query, "tags": "story", "hitsPerPage": per_query}
        )
        data = safe_fetch_json(url)
        if not data:
            continue
        for item in data.get("hits", []):
            title = clean(item.get("title") or item.get("story_title"))
            story_url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('objectID')}"
            points = item.get("points") or 0
            comments = item.get("num_comments") or 0
            summary = f"Hacker News discussion found for query '{query}'."
            fields = classify(title, summary)
            signals.append(
                Signal(
                    "Hacker News",
                    title,
                    story_url,
                    summary,
                    f"{points} points / {comments} comments",
                    clean(item.get("created_at")),
                    *fields,
                )
            )
        time.sleep(0.2)
    return signals


def collect_reddit(queries: list[str], per_query: int) -> list[Signal]:
    signals: list[Signal] = []
    for query in queries[:6]:
        url = "https://www.reddit.com/search.json?" + urllib.parse.urlencode(
            {"q": query, "sort": "new", "t": "week", "limit": per_query}
        )
        data = safe_fetch_json(url)
        if not data:
            continue
        for child in data.get("data", {}).get("children", []):
            item = child.get("data", {})
            title = clean(item.get("title"))
            permalink = item.get("permalink") or ""
            post_url = "https://www.reddit.com" + permalink if permalink.startswith("/") else item.get("url", "")
            summary = clean(item.get("selftext", ""))[:180] or f"Reddit discussion found for query '{query}'."
            score = item.get("score") or 0
            comments = item.get("num_comments") or 0
            created = item.get("created_utc")
            published = dt.datetime.utcfromtimestamp(created).isoformat() + "Z" if created else ""
            fields = classify(title, summary)
            signals.append(
                Signal(
                    "Reddit",
                    title,
                    post_url,
                    summary,
                    f"{score} score / {comments} comments",
                    published,
                    *fields,
                )
            )
        time.sleep(0.5)
    return signals


def collect_github(queries: list[str], per_query: int) -> list[Signal]:
    signals: list[Signal] = []
    for query in queries[:4]:
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {"q": query, "sort": "updated", "order": "desc", "per_page": per_query}
        )
        data = safe_fetch_json(url)
        if not data:
            continue
        for item in data.get("items", []):
            title = clean(item.get("full_name"))
            summary = clean(item.get("description")) or f"GitHub repository matched query '{query}'."
            fields = classify(title, summary)
            signals.append(
                Signal(
                    "GitHub",
                    title,
                    item.get("html_url", ""),
                    summary,
                    f"{item.get('stargazers_count', 0)} stars / {item.get('forks_count', 0)} forks",
                    clean(item.get("updated_at")),
                    *fields,
                )
            )
        time.sleep(0.6)
    return signals


def dedupe(signals: list[Signal]) -> list[Signal]:
    seen: set[str] = set()
    unique: list[Signal] = []
    for signal in signals:
        key = signal.url or signal.title.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(signal)
    return unique


def heat_metrics(signal: Signal) -> tuple[int, int]:
    numbers = [int(value) for value in re.findall(r"\d+", signal.heat)]
    first = numbers[0] if len(numbers) >= 1 else 0
    second = numbers[1] if len(numbers) >= 2 else 0
    return first, second


def heat_gate_pass(signal: Signal) -> bool:
    first, second = heat_metrics(signal)
    if signal.source == "Hacker News":
        return first >= 100 or second >= 20
    if signal.source == "Reddit":
        return first >= 50 or second >= 20
    if signal.source == "GitHub":
        return first >= 500 or second >= 50
    return first >= 50 or second >= 20


def heat_strength(signal: Signal) -> int:
    first, second = heat_metrics(signal)
    if signal.source == "GitHub":
        return first + second * 5
    return first + second * 4


def interesting_score(signal: Signal) -> tuple[int, int, int, int]:
    level = {"high": 3, "medium": 2, "low": 1}
    return (
        level.get(signal.persona_fit, 0),
        level.get(signal.relevance, 0),
        level.get(signal.migration_value, 0),
        heat_strength(signal),
    )


def selection_reason(signal: Signal) -> str:
    if heat_gate_pass(signal):
        return f"heat_gate: {signal.heat}"
    return f"interesting: 热度未过门槛，但 persona_fit={signal.persona_fit}, relevance={signal.relevance}"


def select_report_signals(signals: list[Signal]) -> list[Signal]:
    hot = [signal for signal in signals if heat_gate_pass(signal)]
    hot = sorted(hot, key=lambda signal: (heat_strength(signal), rank_signal(signal)), reverse=True)[:HEAT_SLOTS]

    hot_keys = {signal.url or signal.title.lower() for signal in hot}
    interesting_pool = [
        signal
        for signal in signals
        if (signal.url or signal.title.lower()) not in hot_keys and signal.risk != "high"
    ]
    interesting = sorted(interesting_pool, key=interesting_score, reverse=True)[:INTERESTING_SLOTS]

    selected = hot + interesting
    if len(selected) < HEAT_SLOTS + INTERESTING_SLOTS:
        selected_keys = {signal.url or signal.title.lower() for signal in selected}
        fillers = [
            signal
            for signal in sorted(signals, key=rank_signal, reverse=True)
            if (signal.url or signal.title.lower()) not in selected_keys
        ]
        selected.extend(fillers[: HEAT_SLOTS + INTERESTING_SLOTS - len(selected)])
    return selected[: HEAT_SLOTS + INTERESTING_SLOTS]


def rank_signal(signal: Signal) -> tuple[int, int, int]:
    level = {"high": 3, "medium": 2, "low": 1}
    return (
        level.get(signal.migration_value, 0),
        level.get(signal.relevance, 0),
        level.get(signal.persona_fit, 0),
    )


def chinese_label(signal: Signal) -> str:
    if signal.migration_value == "high":
        return "强推荐"
    if signal.migration_value == "medium":
        return "可实验"
    return "跳过"


def xhs_angle(signal: Signal) -> str:
    text = f"{signal.title} {signal.summary}".lower()
    if "codex" in text:
        return "把它写成一条 Codex 真实使用复盘，重点放在我怎么从不会到敢做。"
    if "python" in text:
        return "适合写小白学 Python 的卡点：AI 到底是在帮学，还是让人跳过基本功。"
    if "cursor" in text or "claude code" in text:
        return "适合做工具对比，但必须绑定一个具体任务，避免泛泛站队。"
    if "automation" in text or "workflow" in text:
        return "适合写一个手动流程被 AI 改造前后的真实变化。"
    return "可以观察，但需要先找到你的亲身使用场景再写。"


def topic_title(signal: Signal) -> str:
    text = signal.title
    if signal.migration_value == "high":
        return f"我从「{text[:24]}」里看到的一个 AI 工具真实变化"
    if signal.migration_value == "medium":
        return f"{text[:26]}：这件事适合小白跟吗？"
    return f"为什么我暂时不追：{text[:24]}"


def render_report(signals: list[Signal], now: dt.datetime) -> str:
    top = signals[: HEAT_SLOTS + INTERESTING_SLOTS]
    strong = [s for s in top if s.migration_value == "high"]
    experiments = [s for s in top if s.migration_value == "medium"]
    skip = [s for s in top if s.migration_value == "low"]

    if not top:
        return textwrap.dedent(
            f"""\
            # AI 工具观点日更观察 - {now.date().isoformat()}

            今天没有抓到足够高质量的公开信号。建议明天继续观察，不要为了日更硬追热点。
            """
        )

    lines: list[str] = []
    lines.append(f"# AI 工具观点日更观察 - {now.date().isoformat()}")
    lines.append("")
    lines.append("## 10 条洞察")
    heat_count = sum(1 for signal in top if heat_gate_pass(signal))
    interesting_count = len(top) - heat_count
    lines.append(
        f"> 目标结构：{HEAT_SLOTS} 条过热度门槛 + {INTERESTING_SLOTS} 条低热但值得观察；"
        f"今日实际：{heat_count} 条 heat_gate + {interesting_count} 条 interesting/补位。"
    )
    lines.append("")
    if len(top) < 10:
        lines.append(f"> 今天只抓到 {len(top)} 条可用公开信号，先不硬凑满 10 条。")
        lines.append("")
    for index, signal in enumerate(top, start=1):
        lines.append(
            f"{index}. [{chinese_label(signal)}] {signal.title}\n"
            f"   - 来源：[{signal.source}]({signal.url})\n"
            f"   - 入选理由：{selection_reason(signal)}\n"
            f"   - 信号：{signal.signal_type}\n"
            f"   - 一句话洞察：{xhs_angle(signal)}"
        )

    lines.append("")
    lines.append("## 共性速记")
    if strong:
        lines.append("- 今天更值得关注的是「具体工作流变化」而不是泛泛的 AI 能力讨论。")
    if any("python" in f"{s.title} {s.summary}".lower() for s in top):
        lines.append("- Python/学习类信号仍然适合用小白视角承接，重点是卡点和过程。")
    if any(s.signal_type == "debate" for s in top):
        lines.append("- 工具对比有讨论度，但直接站队风险较高，最好落到一个真实任务。")
    lines.append("- 可以优先寻找「我用了之后具体变了什么」的第一人称入口。")

    lines.append("")
    lines.append("## 最适合今天写的 3 个角度")
    candidate_topics = (strong or experiments or top)[:3]
    for signal in candidate_topics:
        lines.append(f"- [{chinese_label(signal)}] {topic_title(signal)}")

    lines.append("")
    lines.append("## 不建议追的热点")
    risky = [s for s in top if s.risk == "high"] or skip[:3]
    for signal in risky[:3]:
        lines.append(f"- {signal.title}：和你的人设/真实场景连接不够，容易写成泛 AI 观点。")

    lines.append("")
    lines.append("## 建议写入 market memory 的内容")
    lines.append("- 继续观察 AI coding 工具是否从「能力展示」转向「普通人工作流改造」叙事。")
    lines.append("- 工具对比内容只有绑定具体任务时，才适合迁移到这个账号。")

    lines.append("")
    return "\n".join(lines).strip() + "\n"


def signals_for_llm(signals: list[Signal]) -> list[dict]:
    rows = []
    for signal in signals:
        rows.append(
            {
                "source": signal.source,
                "title": signal.title,
                "url": signal.url,
                "summary": signal.summary,
                "heat": signal.heat,
                "published": signal.published,
                "signal_type": signal.signal_type,
                "relevance": signal.relevance,
                "persona_fit": signal.persona_fit,
                "migration_value": signal.migration_value,
                "risk": signal.risk,
                "selection_reason": selection_reason(signal),
                "passed_heat_gate": heat_gate_pass(signal),
                "suggested_xhs_angle": xhs_angle(signal),
            }
        )
    return rows


def build_deepseek_prompt(signals: list[Signal], now: dt.datetime) -> str:
    account_profile = read_optional(ROOT / "memory" / "account_profile.md")
    content_guidelines = read_optional(ROOT / "memory" / "content_guidelines.md")
    market_patterns = read_optional(ROOT / "memory" / "market" / "patterns.md")
    payload = {
        "date": now.date().isoformat(),
        "signals": signals_for_llm(signals),
        "account_profile": account_profile,
        "content_guidelines": content_guidelines,
        "market_patterns": market_patterns,
    }
    return textwrap.dedent(
        f"""\
        你是一个小红书 AI 工具账号的内容策略观察员。请基于下面的公开来源 signals，
        生成一份中文飞书日报。账号定位是：真实使用 AI 工具、纯小白技术学习、Codex/AI coding/
        Python/自动化/创作者工作流的第一人称复盘。

        规则：
        - 核心输出必须是 10 条洞察。不要只围绕 1 条观点展开。
        - 目标结构是 8 条 heat_gate + 2 条 interesting；实际以每条 signal 的 selection_reason 和 passed_heat_gate 为准。
        - 请按输入顺序输出，不要擅自重排。
        - 每条洞察必须来自不同或尽量不同的 signal，并且必须带来源 URL。
        - 如果可用 signals 少于 10 条，输出实际数量，并明确“今天只抓到 N 条，不硬凑”。
        - 不要编造 signal 之外的事实、热度、来源或链接。
        - 不要大段复述原文，每条只写 1 句观点 + 1 句为什么值得看/可写角度。
        - 输出要短、有判断，像给账号主理人的每日情报卡片。
        - 每条洞察标注：强推荐、可实验、跳过。
        - 每条必须写“入选理由”：heat_gate 使用 heat 字段；interesting 说明为什么虽然低热但值得观察。
        - 避免泛 AI 宏大叙事，优先转成“我用了之后发生了什么”的小红书角度。
        - 如果 signals 很弱，要明确说今天不建议硬追。

        输出结构：
        # AI 工具观点日更观察 - {now.date().isoformat()}
        ## 10 条洞察
        1. [强推荐/可实验/跳过] 洞察标题
           - 来源：[source](url)
           - 入选理由：heat_gate / interesting 的具体理由
           - 观点：一句话说明这个公开信号在说什么
           - 可写角度：一句话说明它怎么迁移到小红书
        ## 共性速记
        ## 最适合今天写的 3 个角度
        ## 不建议追的热点
        ## 建议写入 market memory 的内容

        数据：
        {json.dumps(payload, ensure_ascii=False, indent=2)}
        """
    )


def deepseek_endpoint(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def enhance_report_with_deepseek(signals: list[Signal], now: dt.datetime, fallback_report: str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return fallback_report

    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL).strip() or DEFAULT_DEEPSEEK_BASE_URL
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip() or DEFAULT_DEEPSEEK_MODEL
    max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2600"))
    temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.4"))

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是严谨的小红书内容策略编辑。只基于给定资料做趋势观察和选题转译。",
            },
            {"role": "user", "content": build_deepseek_prompt(signals, now)},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = post_json(deepseek_endpoint(base_url), payload, headers=headers, timeout=90)
        content = response["choices"][0]["message"]["content"].strip()
        if not content:
            raise RuntimeError("DeepSeek returned empty content")
        return content + "\n"
    except Exception as exc:
        print(f"warn: DeepSeek enhancement failed, using rule-based report: {exc}")
        return fallback_report


def feishu_payload(text: str, secret: str | None) -> dict:
    payload = {
        "msg_type": "text",
        "content": {"text": text[:18000]},
    }
    if secret:
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
        sign = base64.b64encode(hmac.new(string_to_sign, b"", hashlib.sha256).digest()).decode("utf-8")
        payload["timestamp"] = timestamp
        payload["sign"] = sign
    return payload


def send_feishu(webhook_url: str, text: str, secret: str | None) -> None:
    body = json.dumps(feishu_payload(text, secret), ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        response_body = response.read().decode("utf-8", errors="replace")
        if response.status >= 300:
            raise RuntimeError(f"Feishu webhook failed: {response.status} {response_body}")
        print(response_body)


def save_report(report: str, report_dir: pathlib.Path, now: dt.datetime) -> pathlib.Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{now.date().isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-signals", type=int, default=int(os.getenv("MAX_SIGNALS", "40")))
    parser.add_argument("--per-query", type=int, default=int(os.getenv("PER_QUERY", "5")))
    parser.add_argument("--save-report", action="store_true", default=os.getenv("SAVE_REPORT", "1") == "1")
    parser.add_argument("--no-feishu", action="store_true")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=8)))
    queries = read_queries()
    signals = []
    signals.extend(collect_hn(queries, args.per_query))
    signals.extend(collect_reddit(queries, args.per_query))
    signals.extend(collect_github(queries, args.per_query))

    candidate_signals = sorted(dedupe(signals), key=rank_signal, reverse=True)[: args.max_signals]
    report_signals = select_report_signals(candidate_signals)
    fallback_report = render_report(report_signals, now)
    report = enhance_report_with_deepseek(report_signals, now, fallback_report)

    if args.save_report:
        path = save_report(report, DEFAULT_REPORT_DIR, now)
        print(f"saved report: {path}")

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
