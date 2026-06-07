#!/usr/bin/env python3
"""Promote reviewed Xiaohongshu benchmark candidates into sample files."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
CANDIDATE_DIR = ROOT / "memory" / "xhs_benchmark" / "candidates"
SAMPLE_DIR = ROOT / "memory" / "xhs_benchmark" / "samples"


def current_week() -> str:
    now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=8)))
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def parse_keep(value: str) -> set[int]:
    return {int(item) for item in re.findall(r"\d+", value)}


def parse_candidates(path: pathlib.Path) -> dict[int, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n###\s+", "\n" + text)
    candidates: dict[int, dict[str, str]] = {}
    for block in blocks:
        header = re.match(r"(\d+)\.\s+(.+)", block.strip())
        if not header:
            continue
        index = int(header.group(1))
        title = header.group(2).strip()
        fields = {"title": title}
        for line in block.splitlines():
            match = re.match(r"-\s+([a-z_]+):\s*(.*)", line.strip())
            if match:
                fields[match.group(1)] = match.group(2).strip()
        candidates[index] = fields
    return candidates


def slugify(value: str) -> str:
    cleaned = re.sub(r"https?://", "", value.lower())
    cleaned = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", cleaned).strip("-")
    return cleaned[:48] or "xhs-sample"


def sample_text(candidate: dict[str, str], week: str, index: int) -> str:
    title = candidate.get("title", "unknown")
    url = candidate.get("url", "unknown")
    snippet = candidate.get("snippet", "unknown")
    reason = candidate.get("reason", "unknown")
    query = candidate.get("query", "unknown")
    return f"""---
status: promoted_from_candidate
date_seen: {week}
source_url: {url}
platform: xiaohongshu
topic: {query}
author_or_account_type: unknown
benchmark_weight: low_to_medium
sample_role: tutorial_utility_reference
---

# Xiaohongshu Benchmark Sample

## Basic Info

- title: {title}
- cover_text: unknown
- cover_structure: unknown
- body_structure: unknown
- visible_metrics: unknown
- comment_signals: unknown
- search_snippet: {snippet}
- candidate_reason: {reason}
- candidate_index: {index}
- benchmark_weight: low_to_medium
- sample_role: tutorial_utility_reference
- usage_note: 这类样本主要用于提炼教程标题、工具性承诺、步骤表达和低门槛包装；不要直接当作观点型爆款 benchmark。

## Benchmark Scores

- title_clickability: unknown
- cover_clarity: unknown
- save_value: unknown
- comment_trigger: unknown
- account_fit: unknown
- technical_accessibility: unknown
- transfer_risk: unknown

## Reusable Pattern

- 教程型低门槛承诺：用“保姆级 / 零基础 / X 分钟 / 安装使用 / 第一个作品”降低进入门槛。
- 工具性价值：强调学会一个具体工具或完成一个具体任务，而不是表达观点。

## Why It Matters For This Account

可作为后续教程类小红书的参考：如何把技术工具拆成小白能理解的入口、步骤和结果。但权重低于有完整封面、正文、互动数据、评论区反馈的同平台爆款样本。

## What Not To Copy

不要照搬纯教程口吻，也不要把教程标题误判为观点型内容规律。需要结合账号的真实体验、过程变化和个人复盘来改写。
"""


def promote(week: str, keep: set[int]) -> list[pathlib.Path]:
    candidate_path = CANDIDATE_DIR / f"{week}.md"
    if not candidate_path.exists():
        raise FileNotFoundError(f"candidate file not found: {candidate_path}")

    candidates = parse_candidates(candidate_path)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for index in sorted(keep):
        if index not in candidates:
            print(f"warn: candidate {index} not found in {candidate_path}")
            continue
        candidate = candidates[index]
        stem = slugify(candidate.get("title", f"candidate-{index}"))
        path = SAMPLE_DIR / f"{week}-{index:02d}-{stem}.md"
        path.write_text(sample_text(candidate, week, index), encoding="utf-8")
        created.append(path)
    return created


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", default=current_week())
    parser.add_argument("--keep", required=True, help="Candidate numbers to promote, e.g. '1,3,7'.")
    args = parser.parse_args()

    created = promote(args.week, parse_keep(args.keep))
    if not created:
        print("No samples created.")
    for path in created:
        print(f"created sample: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
