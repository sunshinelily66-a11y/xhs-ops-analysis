# Market Observation Playbook

## Purpose

Use this workflow to collect public market signals related to AI tools, AI coding, Codex, Claude Code, Cursor, Python learning, automation, frontend learning, and creator workflows, then convert those signals into Xiaohongshu content opportunities for this account.

This is an observation system, not a bulk scraper. Prefer small, high-signal samples with links and concise summaries.

## Source Rules

- Prefer public and indexed sources that can be accessed without logging in.
- Use official product blogs, changelogs, documentation, GitHub repositories, Hacker News, Reddit, newsletters, search results, and public web pages.
- For X/Twitter, prefer official API if credentials are available. Without API access, use search-engine-indexed public results or third-party article/newsletter summaries rather than browser automation scraping.
- Do not bypass login walls, captchas, rate limits, robots restrictions, or paywalls.
- Do not store large verbatim copies of posts. Save links, short summaries, themes, and account-specific implications.

## Daily Collection Scope

Target 20 to 40 candidate signals per run, then publish the best 10 insights:

- 3 to 5 product or tool updates
- 3 to 6 user opinions, debates, or pain points
- 2 to 5 tutorials, workflows, or examples
- 1 to 3 weak signals worth watching

Stop early if the search results are repetitive or low quality.

## Signal Fields

Capture these fields when possible:

- source
- url
- date_seen
- topic
- original_claim_summary
- signal_type
- heat_signal
- relevance
- persona_fit
- migration_value
- risk
- xhs_angle

Use low/medium/high for subjective scores.

## Evaluation Criteria

High-value signals usually have at least two:

- directly related to Codex, AI coding, Python learning, frontend learning, automation, or creator workflows
- contains a concrete user experience, not just a product announcement
- reveals confusion, fear, excitement, debate, or unmet need
- can become a first-person Xiaohongshu note without pretending to be an expert
- connects to the account's proven themes in `memory/account_profile.md`

Low-value signals:

- generic AI hype
- investor or company news with no user scene
- arguments that require expert authority the account does not claim
- trend claims that cannot become a concrete note

## Report Rules

Daily reports should be concise and useful:

- Start with exactly 10 insights when at least 10 useful signals are available.
- Each insight must include a source URL.
- Keep each insight short: one sentence for the observation and one sentence for the Xiaohongshu angle.
- Translate each observation into a Xiaohongshu angle.
- Include 3 possible titles or topics after the 10 insights.
- Mark ideas as strong, experimental, or skip.
- Recommend only durable memory updates; do not promote one-off noise into guidelines.

## Memory Rules

Save daily reports under:

`memory/market/reports/YYYY-MM-DD.md`

If a pattern repeats across multiple days, add it to `memory/market/patterns.md`.

If a pattern becomes important for the account's own publishing rules, suggest updating `memory/content_guidelines.md`.

## Cloud Automation

For stable daily delivery, prefer GitHub Actions over Codex thread heartbeats.

- Workflow: `.github/workflows/daily-market-observation.yml`
- Script: `scripts/daily_market_observer.py`
- Schedule: daily at 01:10 UTC, which is 09:10 in Asia/Shanghai.
- Required secret: `FEISHU_WEBHOOK_URL`
- Optional secret: `FEISHU_BOT_SECRET` when the Feishu custom bot enables signature verification.
- Optional secret: `DEEPSEEK_API_KEY` to turn on LLM-enhanced Chinese synthesis.
- Optional secret: `DEEPSEEK_BASE_URL`, default `https://api.deepseek.com`.
- Optional secret: `DEEPSEEK_MODEL`, default `deepseek-v4-flash`.

The script should run without paid APIs. It uses public endpoints such as Hacker News Algolia, Reddit public JSON, and GitHub Search. If `DEEPSEEK_API_KEY` is present, the script sends only structured signals, account profile, guidelines, and market patterns to DeepSeek for summary generation. If no Feishu webhook is configured, it prints the report in the workflow log.
