# Xiaohongshu Memory Playbook

## Purpose

The `memory/` folder is the long-term source of truth for this Xiaohongshu account:

- `memory/account_profile.md`: persona, audience, boundaries, and durable positioning.
- `memory/content_guidelines.md`: reusable rules for topics, titles, covers, copy, and experiments.
- `memory/posts/`: one file per note or draft, preserving original copy and performance learnings.
- `memory/market/`: upstream trend radar from X/Twitter-indexed content, HN, Reddit, GitHub, official changelogs, and blogs. This is not Xiaohongshu benchmark evidence.
- `memory/xhs_benchmark/`: Xiaohongshu-native reference samples and platform patterns. This is the benchmark layer for titles, covers, body structures, and same-platform user reactions.

## When To Update Memory

Update memory when the user provides:

- a published note's title, cover, copy, or backend metrics
- a draft that should be saved for future reference
- a confirmed account rule, persona detail, content boundary, or stylistic preference
- a performance review that reveals repeatable patterns

Do not overwrite original note copy unless the user explicitly asks. Add analysis and learnings in separate fields.

## Post File Naming

Use stable, readable filenames:

`YYYY-MM-DD_short-topic.md`

If the publish date is unknown, use:

`undated_short-topic.md`

Keep the short topic lowercase ASCII when possible. If Chinese is clearer, Chinese filenames are acceptable in this repository.

## Required Post Fields

Each post memory should include:

- status: draft, published, archived, or idea
- publish_date
- title
- cover_text
- content_pillar
- topic_tags
- audience
- angle
- original_copy
- metrics
- performance_summary
- reusable_patterns
- follow_up_ideas

Use `unknown` for missing values rather than guessing.

## Guideline Promotion Rule

Only promote a learning into `memory/content_guidelines.md` when one of these is true:

- the user explicitly says it is a rule
- at least two notes show the same performance pattern
- it matches a strong account positioning decision in `memory/account_profile.md`

Mark uncertain ideas as experiments, not rules.

## Retrieval Rules For Generation

Before drafting new content:

1. Read the account profile.
2. Read content guidelines.
3. Search `memory/posts/` for similar topics or formats.
4. If the request is about a current AI-tool topic, optionally check `memory/market/patterns.md` or recent market reports for upstream trend context.
5. If the request is about Xiaohongshu packaging, benchmark, or platform fit, check `memory/xhs_benchmark/patterns.md` and relevant samples.
6. Reuse proven patterns, but avoid duplicating old titles or copy.
7. If no relevant memory exists, state that the draft is based on current guidelines only.

## Evidence Hierarchy

Use this hierarchy when judging whether a content pattern is reliable:

1. User's own Xiaohongshu backend performance.
2. Xiaohongshu-native benchmark samples from similar topics or personas.
3. Repeating upstream market signals.
4. One-off external opinions or low-heat observations.

Do not treat upstream market signals as proof that a Xiaohongshu title, cover, or copy structure will work.
