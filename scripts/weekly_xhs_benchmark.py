#!/usr/bin/env python3
"""Create a weekly Xiaohongshu benchmark synthesis from saved samples.

This job does not scrape Xiaohongshu. It summarizes same-platform samples that
have already been saved under memory/xhs_benchmark/samples/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import sys
import textwrap


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from daily_market_observer import (  # noqa: E402
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODEL,
    deepseek_endpoint,
    post_json,
    read_optional,
    send_feishu,
)


SAMPLE_DIR = ROOT / "memory" / "xhs_benchmark" / "samples"
REPORT_DIR = ROOT / "memory" / "xhs_benchmark" / "reports"


def week_id(now: dt.datetime) -> str:
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def read_samples(limit: int) -> list[tuple[pathlib.Path, str]]:
    if not SAMPLE_DIR.exists():
        return []
    samples = []
    for path in sorted(SAMPLE_DIR.glob("*.md"), reverse=True):
        if path.name == "_template.md":
            continue
        samples.append((path, path.read_text(encoding="utf-8")[:8000]))
        if len(samples) >= limit:
            break
    return samples


def build_prompt(samples: list[tuple[pathlib.Path, str]], now: dt.datetime) -> str:
    account_profile = read_optional(ROOT / "memory" / "account_profile.md")
    content_guidelines = read_optional(ROOT / "memory" / "content_guidelines.md")
    benchmark_rules = read_optional(ROOT / "memory" / "xhs_benchmark" / "benchmark_rules.md")
    existing_patterns = read_optional(ROOT / "memory" / "xhs_benchmark" / "patterns.md")
    formatted_samples = [
        {"file": str(path.relative_to(ROOT)), "content": content}
        for path, content in samples
    ]
    return textwrap.dedent(
        f"""\
        你是小红书同平台 benchmark 分析员。请只基于已保存的小红书样本做周度沉淀，
        不要使用 X/Twitter、HN、Reddit、GitHub 的热度作为小红书证明。

        账号定位：
        {account_profile}

        现有内容规则：
        {content_guidelines}

        benchmark 规则：
        {benchmark_rules}

        已有 benchmark patterns：
        {existing_patterns}

        本周样本：
        {formatted_samples}

        输出要求：
        - 输出中文。
        - 如果样本少于 3 条，先说明样本不足，只给方向性观察。
        - 不要编造样本中没有的标题、数据、封面、评论。
        - 重点回答“小红书怎么包装”，不是外部趋势是否热。
        - 不要写长文，给账号主理人可执行的 benchmark 周报。

        固定模板：
        # 小红书 Benchmark 周报 - {week_id(now)}

        ## 样本概览
        - 样本数：
        - 主要主题：
        - 证据质量：

        ## 本周可复用的平台模式
        1. 模式：
           - 证据：
           - 适合你账号的原因：

        ## 标题/封面/正文启发
        - 标题：
        - 封面：
        - 正文：

        ## 下周可测试内容方向
        - [强推荐/可实验] 选题：

        ## 可沉淀到 benchmark patterns 的候选
        - 仅列候选，不要直接改写为长期规则。
        """
    )


def rule_based_report(samples: list[tuple[pathlib.Path, str]], now: dt.datetime) -> str:
    lines = [f"# 小红书 Benchmark 周报 - {week_id(now)}", ""]
    lines.append("## 样本概览")
    lines.append(f"- 样本数：{len(samples)}")
    lines.append("- 主要主题：需要基于已保存样本进一步分析")
    if len(samples) < 3:
        lines.append("- 证据质量：样本不足，只适合做方向性观察")
    else:
        lines.append("- 证据质量：可做初步模式整理")

    lines.append("")
    lines.append("## 本周可复用的平台模式")
    if not samples:
        lines.append("- 暂无样本。请先在 `memory/xhs_benchmark/samples/` 保存小红书参考样本。")
    else:
        lines.append("- 需要 DeepSeek 根据样本提炼标题、封面、正文模式。")

    lines.append("")
    lines.append("## 标题/封面/正文启发")
    lines.append("- 标题：unknown")
    lines.append("- 封面：unknown")
    lines.append("- 正文：unknown")

    lines.append("")
    lines.append("## 下周可测试内容方向")
    lines.append("- [可实验] 补充 5-10 条同赛道小红书样本后再生成测试方向。")

    lines.append("")
    lines.append("## 可沉淀到 benchmark patterns 的候选")
    lines.append("- unknown")
    return "\n".join(lines).strip() + "\n"


def enhance_with_deepseek(samples: list[tuple[pathlib.Path, str]], now: dt.datetime, fallback: str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return fallback

    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL).strip() or DEFAULT_DEEPSEEK_BASE_URL
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip() or DEFAULT_DEEPSEEK_MODEL
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是严谨的小红书 benchmark 分析员。只基于给定样本总结平台包装模式。",
            },
            {"role": "user", "content": build_prompt(samples, now)},
        ],
        "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.35")),
        "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKENS", "2600")),
    }
    try:
        response = post_json(
            deepseek_endpoint(base_url),
            payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=90,
        )
        content = response["choices"][0]["message"]["content"].strip()
        if not content:
            raise RuntimeError("DeepSeek returned empty content")
        return content + "\n"
    except Exception as exc:
        print(f"warn: DeepSeek benchmark synthesis failed, using fallback: {exc}")
        return fallback


def save_report(report: str, now: dt.datetime) -> pathlib.Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{week_id(now)}.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-limit", type=int, default=int(os.getenv("XHS_SAMPLE_LIMIT", "30")))
    parser.add_argument("--save-report", action="store_true", default=os.getenv("SAVE_REPORT", "1") == "1")
    parser.add_argument("--no-feishu", action="store_true")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=8)))
    samples = read_samples(args.sample_limit)
    fallback = rule_based_report(samples, now)
    report = enhance_with_deepseek(samples, now, fallback)

    if args.save_report:
        path = save_report(report, now)
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
