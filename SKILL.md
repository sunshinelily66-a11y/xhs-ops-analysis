---
name: xhs-ops-analysis
description: Analyze Xiaohongshu backend export files, account content memory, Xiaohongshu benchmarks, and public AI-tool trend signals; evaluate note performance, covers, titles, copywriting, persona fit, and produce Chinese Xiaohongshu content strategy, drafts, daily observation reports, guidelines, and reusable memory updates.
---

# 小红书运营分析与内容记忆

## Overview

Use this skill when the user wants to analyze Xiaohongshu performance, review existing notes, improve titles/covers/copy, generate new note ideas or drafts, maintain account memory, build Xiaohongshu platform benchmarks, or run recurring upstream market observation for AI tools, AI coding, and creator workflows.

This skill is optimized for Chinese output, daily/weekly review, and long-term account consistency.

## What To Read First

Choose the smallest useful set:

- Export analysis: read the export file(s), then [references/analysis_playbook.md](references/analysis_playbook.md).
- Content generation or account positioning: read [memory/account_profile.md](memory/account_profile.md) and [memory/content_guidelines.md](memory/content_guidelines.md).
- Using prior notes as examples: inspect [memory/posts/](memory/posts/) and load only relevant note memories.
- Adding new note copy: use [memory/posts/_template.md](memory/posts/_template.md).
- Memory maintenance rules: see [references/memory_playbook.md](references/memory_playbook.md).
- Daily upstream trend observation: read [references/market_observation_playbook.md](references/market_observation_playbook.md), [memory/market/queries.md](memory/market/queries.md), and [memory/market/sources.md](memory/market/sources.md).
- Xiaohongshu benchmark work: read [references/xhs_benchmark_playbook.md](references/xhs_benchmark_playbook.md), [memory/xhs_benchmark/benchmark_rules.md](memory/xhs_benchmark/benchmark_rules.md), and relevant files in [memory/xhs_benchmark/samples/](memory/xhs_benchmark/samples/).

If multiple exports are provided, compare them by default as separate cohorts, such as week-over-week, month-over-month, or top performers versus the rest.

## Export Analysis Workflow

1. Identify file type, date range, and dataset scope.
2. Build a column map for common Xiaohongshu fields such as title, content, cover, publish time, views, likes, comments, saves, shares, follows, and impressions.
3. Separate the dataset into meaningful groups:
   - top-performing notes
   - median or ordinary notes
   - underperforming notes
   - different time ranges or content themes when available
4. Analyze three core dimensions:
   - content: topic selection, structure, depth, hook, CTA, and repeatability
   - cover: clarity, visual hierarchy, text density, readability, and topic match
   - title: promise, curiosity, specificity, keyword coverage, and click appeal
5. Compare groups and summarize what patterns are associated with stronger results.
6. Turn findings into next-step recommendations: topic ideas, title formulas, cover templates, content experiments, and memory updates.

## Content Memory Workflow

When the user provides a note draft, published copy, or backend row:

1. Save or update one memory file in `memory/posts/` using the template.
2. Preserve the original copy where available; do not rewrite it inside the memory unless asked.
3. Add structured metadata: publish date, topic, content pillar, hook, title, cover text, metrics, audience, angle, and status.
4. Extract reusable learnings: what worked, what did not, which title/cover/copy pattern it represents, and whether it fits the account persona.
5. Update `memory/content_guidelines.md` only when a pattern repeats or the user explicitly confirms it as a rule.

## Daily Upstream Trend Observation Workflow

When asked to observe external trends or run a daily push, treat market signals as upstream topic radar, not as Xiaohongshu proof:

1. Search only public, accessible sources. Prefer search results, official blogs/changelogs, Hacker News, Reddit, GitHub, product communities, newsletters, and indexed public X/Twitter posts over direct scraping.
2. Use the queries in `memory/market/queries.md`, expanding them only when relevant.
3. Collect 8 to 20 useful signals, then deduplicate by event, product, and argument.
4. Classify each signal as one of: product update, user pain, workflow pattern, debate, tutorial angle, beginner anxiety, creator opportunity, or weak/noisy signal.
5. Translate market signals into possible Xiaohongshu-native ideas that fit the account profile, but do not treat them as validated Xiaohongshu benchmarks.
6. Save durable observations only when useful; use `memory/market/reports/_template.md` for report shape.
7. Do not store long copied posts. Store links, short summaries, observed patterns, and account-specific implications.

## Xiaohongshu Benchmark Workflow

When asked to judge what works on Xiaohongshu itself:

1. Use Xiaohongshu-native evidence whenever possible: same-platform notes, titles, covers, visible interaction signals, comment questions, and the user's own backend data.
2. Store competitor or reference samples in `memory/xhs_benchmark/samples/` using the sample template.
3. Score each sample on title clickability, cover clarity, body structure, save/comment triggers, persona fit, technical accessibility, and transfer risk.
4. Update `memory/xhs_benchmark/patterns.md` only when a pattern repeats across multiple Xiaohongshu samples.
5. Promote a benchmark pattern into `memory/content_guidelines.md` only when it also fits the user's account profile or is confirmed by the user's own data.

## Account Content Direction

The account's current proven direction is:

- personal, real-use AI tool experience, especially Codex
- pure beginner perspective learning technical tools
- practical workflow changes from AI, coding, Python, frontend, automation, and content operations
- honest before/after comparisons instead of generic AI trend commentary
- concrete scenes involving self-study, work, collaboration, or creator productivity

Prefer "I used X and my workflow changed" over "X is important". Prefer specific scenes, friction, and outcomes over broad opinions.

## Analysis Rules

- Prefer the actual exported fields over inferred meaning.
- If a column is missing, say so clearly and reduce confidence instead of guessing.
- If the cover image itself is not available, analyze cover text, thumbnail metadata, or image-related fields that are present, and state the limitation.
- Treat small datasets carefully; when the sample is too small to generalize, say that the conclusion is directional only.
- When performance metrics conflict, prioritize the user's goal:
  - exposure or views for reach
  - likes/comments/saves/shares for engagement
  - follows or profile visits for conversion intent
- Treat memory as user-owned source material. Do not invent past performance, note copy, or account facts.
- When generating content, keep the account voice consistent with `memory/account_profile.md` and `memory/content_guidelines.md`.
- If account memory conflicts with a new user instruction, follow the new instruction and mention the conflict briefly.

## Output Format

For analysis, return the result in Chinese with these sections when possible:

- 数据概览
- 核心结论
- 内容分析
- 封面分析
- 标题分析
- 对比结果
- 下轮建议
- 可执行选题/标题/封面方向
- 建议写入 memory 的内容

For content generation, use sections that fit the request, such as:

- 选题判断
- 标题备选
- 封面文案
- 正文草稿
- 发布前检查
- 可沉淀到 memory 的新规则

For daily market observation, use:

- 值得看的 8 条
- 匹配账号定位的内容建议

For Xiaohongshu benchmark analysis, use:

- 小红书样本概览
- 可复用的平台模式
- 和你账号的匹配度
- 不适合直接模仿的风险
- 可测试的标题/封面/正文方向

## Recommendation And Draft Style

Make the recommendation concrete and reusable:

- name the winning topic patterns
- point out what to stop doing
- provide title formula examples
- describe cover design direction
- suggest 3 to 10 follow-up content ideas
- include one or two low-risk experiments for the next batch
- draft in a sincere, first-person, specific, slightly reflective voice
- avoid empty AI hype, vague trend takes, and over-polished marketing language

## References And Memory

- Field mapping, scoring focus, and comparison logic: [references/analysis_playbook.md](references/analysis_playbook.md).
- Memory schema and update rules: [references/memory_playbook.md](references/memory_playbook.md).
- Upstream trend observation rules: [references/market_observation_playbook.md](references/market_observation_playbook.md).
- Xiaohongshu benchmark rules: [references/xhs_benchmark_playbook.md](references/xhs_benchmark_playbook.md).
- Account persona and boundaries: [memory/account_profile.md](memory/account_profile.md).
- Reusable content rules: [memory/content_guidelines.md](memory/content_guidelines.md).
- Upstream market queries and sources: [memory/market/queries.md](memory/market/queries.md), [memory/market/sources.md](memory/market/sources.md).
- Xiaohongshu benchmark memory: [memory/xhs_benchmark/](memory/xhs_benchmark/).

## Retrospective Files

Store saved review docs in the `复盘/` folder.

Use the filename pattern `时期+复盘.md`, for example `2026-01-20至2026-06-04复盘.md`.
