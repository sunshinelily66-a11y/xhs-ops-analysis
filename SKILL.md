---
name: xhs-ops-analysis
description: Analyze Xiaohongshu backend export files (CSV/XLSX/TSV/JSON), evaluate content, cover, and title performance, compare multiple exports, and produce Chinese recommendations for the next round of content.
---

# 小红书运营数据分析

## Overview

Use this skill when the user provides Xiaohongshu backend export data and wants to understand what content performs well, why certain covers or titles work, and what to publish next.

This skill is optimized for Chinese output and for daily or weekly content review.

## What To Read

Read the export file(s) first, then infer the available fields and the reporting period from file names, sheets, column names, and date columns.

If multiple exports are provided, compare them by default as separate cohorts, such as week-over-week, month-over-month, or top performers versus the rest.

## Analysis Workflow

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
6. Turn findings into next-step recommendations: topic ideas, title formulas, cover templates, and content experiments.

## Analysis Rules

- Prefer the actual exported fields over inferred meaning.
- If a column is missing, say so clearly and reduce confidence instead of guessing.
- If the cover image itself is not available, analyze cover text, thumbnail metadata, or image-related fields that are present, and state the limitation.
- Treat small datasets carefully; when the sample is too small to generalize, say that the conclusion is directional only.
- When performance metrics conflict, prioritize the user's goal:
  - exposure or views for reach
  - likes/comments/saves/shares for engagement
  - follows or profile visits for conversion intent

## Output Format

Return the result in Chinese with these sections when possible:

- 数据概览
- 核心结论
- 内容分析
- 封面分析
- 标题分析
- 对比结果
- 下轮建议
- 可执行选题/标题/封面方向

## Recommendation Style

Make the recommendation concrete and reusable:

- name the winning topic patterns
- point out what to stop doing
- provide title formula examples
- describe cover design direction
- suggest 3 to 10 follow-up content ideas
- include one or two low-risk experiments for the next batch

## Reference

For field mapping heuristics, scoring focus, and comparison logic, see [references/analysis_playbook.md](references/analysis_playbook.md).

## Retrospective Files

Store saved review docs in the `复盘/` folder.

Use the filename pattern `时期+复盘.md`, for example `2026-01-20至2026-06-04复盘.md`.
