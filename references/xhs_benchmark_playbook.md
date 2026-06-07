# Xiaohongshu Benchmark Playbook

## Purpose

Use this workflow to build a same-platform benchmark for Xiaohongshu content. This layer answers how a topic should be packaged for Xiaohongshu: title, cover, body structure, comment triggers, save value, and persona fit.

This is separate from `memory/market/`, which tracks upstream AI-tool trends from technical and public web sources.

## Source Rules

Prefer Xiaohongshu-native evidence:

- same-topic Xiaohongshu notes
- similar-persona accounts
- visible engagement signals
- titles, cover text, first image style, body structure
- comment questions and user objections
- the user's own backend exports and note history

When direct Xiaohongshu access is limited, use user-provided links, screenshots, exports, or manually saved samples. Do not bypass login walls, captchas, rate limits, or platform restrictions.

## Sample Storage

Save reference samples in:

`memory/xhs_benchmark/samples/`

Use the template:

`memory/xhs_benchmark/samples/_template.md`

Use stable filenames:

`YYYY-MM-DD_platform-topic-author.md`

If date or author is unknown, use `unknown`.

## Benchmark Fields

Each sample should capture:

- source_url or source_note
- date_seen
- topic
- title
- cover_text
- cover_structure
- body_structure
- visible_metrics
- comment_signals
- audience
- hook_type
- save_value
- persona_style
- technical_accessibility
- transfer_risk
- account_fit
- reusable_pattern

Use `unknown` for missing fields rather than guessing.

## Scoring

Score each sample qualitatively:

- title_clickability: low / medium / high
- cover_clarity: low / medium / high
- save_value: low / medium / high
- comment_trigger: low / medium / high
- account_fit: low / medium / high
- technical_accessibility: low / medium / high
- transfer_risk: low / medium / high

High heat alone is not enough. A strong benchmark sample must also be understandable and transferable to the user's persona.

## Pattern Promotion

Add a pattern to `memory/xhs_benchmark/patterns.md` when:

- it appears in at least two Xiaohongshu benchmark samples, or
- it appears once in a strong benchmark sample and also matches the user's own successful content, or
- the user explicitly confirms it as a useful Xiaohongshu pattern.

Promote a pattern to `memory/content_guidelines.md` only when it fits the account profile and is safe to repeat.

## How To Use With Market Signals

Use market signals to discover what might be worth writing.

Use Xiaohongshu benchmarks to decide how to package it.

Use the user's own posts and backend data to decide whether to keep repeating it.

## Weekly Automation

For weekly candidate discovery:

- Workflow: `.github/workflows/weekly-xhs-discovery.yml`
- Script: `scripts/xhs_benchmark_discover.py`
- Schedule: Saturday 00:30 UTC, which is Saturday 08:30 in Asia/Shanghai.
- Input: public search API results for `site:xiaohongshu.com` queries.
- Output: `memory/xhs_benchmark/candidates/YYYY-Www.md` and Feishu push.
- Search secrets: one of `BRAVE_SEARCH_API_KEY`, `BING_SEARCH_API_KEY`, or `SERPAPI_API_KEY`.

For weekly benchmark synthesis:

- Workflow: `.github/workflows/weekly-xhs-benchmark.yml`
- Script: `scripts/weekly_xhs_benchmark.py`
- Schedule: Sunday 01:30 UTC, which is Sunday 09:30 in Asia/Shanghai.
- Input: saved files under `memory/xhs_benchmark/samples/`.
- Output: `memory/xhs_benchmark/reports/YYYY-Www.md` and Feishu push.

This job does not scrape Xiaohongshu. It summarizes saved same-platform samples. If there are too few samples, it should say so clearly and avoid pretending that benchmark evidence exists.

## Candidate Promotion

Discovery candidates are not benchmark samples until the user confirms them.

When the user says `保留 1,3,7`, run:

`python3 scripts/xhs_benchmark_promote.py --week YYYY-Www --keep 1,3,7`

This creates sample files under `memory/xhs_benchmark/samples/`. These promoted files still contain many `unknown` fields until the user provides screenshots, visible metrics, cover text, body structure, or comments.
