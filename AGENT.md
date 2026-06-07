# XHS Ops Analysis Agent Guide

## Purpose

This repository is an AI-assisted Xiaohongshu content operations system. It combines the user's own account memory, upstream AI-tool trend radar, Xiaohongshu benchmark samples, and automation scripts for Feishu pushes.

## Core Mental Model

Use three evidence layers:

1. `memory/posts/`: the user's own Xiaohongshu content and backend evidence. This is the strongest proof.
2. `memory/xhs_benchmark/`: Xiaohongshu-native benchmark evidence. Use it to judge title, cover, body structure, comments, save value, and platform fit.
3. `memory/market/`: upstream trend radar from HN, Reddit, GitHub, public X/Twitter-indexed content, official changelogs, and blogs. Use it to discover topics, not to prove Xiaohongshu fit.

Do not treat upstream market heat as Xiaohongshu benchmark evidence.

## Important Files

- `SKILL.md`: Codex skill entrypoint and operating instructions.
- `references/analysis_playbook.md`: Xiaohongshu export analysis.
- `references/memory_playbook.md`: memory rules and evidence hierarchy.
- `references/market_observation_playbook.md`: upstream trend observation rules.
- `references/xhs_benchmark_playbook.md`: Xiaohongshu benchmark rules.
- `memory/account_profile.md`: account persona and positioning.
- `memory/content_guidelines.md`: stable content guidelines.

## Automations

Daily upstream trend radar:

- Workflow: `.github/workflows/daily-market-observation.yml`
- Script: `scripts/daily_market_observer.py`
- Output: `memory/market/reports/`
- Purpose: discover AI-tool and AI-agent topics worth watching.

Weekly Xiaohongshu candidate discovery:

- Workflow: `.github/workflows/weekly-xhs-discovery.yml`
- Script: `scripts/xhs_benchmark_discover.py`
- Output: `memory/xhs_benchmark/candidates/`
- Purpose: find public-search candidates from Xiaohongshu-indexed results.
- Requires one search secret for useful results: `BRAVE_SEARCH_API_KEY`, `BING_SEARCH_API_KEY`, or `SERPAPI_API_KEY`.

Weekly Xiaohongshu benchmark synthesis:

- Workflow: `.github/workflows/weekly-xhs-benchmark.yml`
- Script: `scripts/weekly_xhs_benchmark.py`
- Output: `memory/xhs_benchmark/reports/`
- Purpose: summarize confirmed Xiaohongshu samples into platform packaging patterns.

## Candidate Confirmation Flow

1. Weekly discovery pushes candidate links to Feishu and saves `memory/xhs_benchmark/candidates/YYYY-Www.md`.
2. The user returns to Codex and says something like: `保留 1,3,7`.
3. Run:

```bash
python3 scripts/xhs_benchmark_promote.py --week YYYY-Www --keep 1,3,7
```

4. Review the generated files under `memory/xhs_benchmark/samples/`.
5. Commit and push the new samples.
6. Weekly benchmark synthesis uses those samples for platform benchmark reports.

Candidates are machine-discovered and shallow. Samples are human-confirmed and suitable for benchmark analysis.

## Secrets

Required for Feishu push:

- `FEISHU_WEBHOOK_URL`

Optional:

- `FEISHU_BOT_SECRET`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `BRAVE_SEARCH_API_KEY`
- `BING_SEARCH_API_KEY`
- `SERPAPI_API_KEY`
- `XHS_SEARCH_PROVIDER`

## Content Generation Rule

When generating Xiaohongshu content:

1. Read `memory/account_profile.md`.
2. Read `memory/content_guidelines.md`.
3. Search `memory/posts/` for related prior notes.
4. If packaging matters, read `memory/xhs_benchmark/patterns.md` and relevant samples.
5. If topic freshness matters, read recent `memory/market/reports/` or `memory/market/patterns.md`.
6. Draft in a sincere first-person beginner/practitioner voice.

## Safety Boundary

Do not bypass Xiaohongshu login walls, captchas, rate limits, or platform restrictions. The discovery script only uses public search API results. Full benchmark samples require user confirmation and, when needed, user-provided screenshots, links, or notes.
