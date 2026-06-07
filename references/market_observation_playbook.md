# Market Observation Playbook

## Purpose

Use this workflow to collect upstream public market signals related to AI tools, AI coding, Codex, Claude Code, Cursor, Python learning, automation, frontend learning, and creator workflows, then convert those signals into possible Xiaohongshu content opportunities for this account.

This is an upstream trend radar, not a Xiaohongshu benchmark. Prefer small, high-signal samples with links and concise summaries.

## Source Rules

- Prefer public and indexed sources that can be accessed without logging in.
- Use official product blogs, changelogs, documentation, GitHub repositories, Hacker News, Reddit, newsletters, search results, and public web pages.
- For X/Twitter, prefer official API if credentials are available. Without API access, use search-engine-indexed public results or third-party article/newsletter summaries rather than browser automation scraping.
- Do not bypass login walls, captchas, rate limits, robots restrictions, or paywalls.
- Do not store large verbatim copies of posts. Save links, short summaries, themes, and account-specific implications.

## Daily Collection Scope

Target 20 to 40 candidate signals per run, then publish 10 insights:

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

## Relationship To Xiaohongshu Benchmarks

Market signals answer: "What is emerging upstream?"

They do not answer:

- whether a Xiaohongshu title will get clicks
- whether a Xiaohongshu cover format works
- whether Xiaohongshu users understand the topic
- whether the user's account can convert the topic into saves, follows, or comments

For those questions, use `references/xhs_benchmark_playbook.md` and `memory/xhs_benchmark/`.

## Report Rules

Daily reports should be concise and useful:

- Use two main sections only:
  - `值得看的 8 条`
  - `匹配账号定位的内容建议`
- The first section should include up to 8 heat-gated signals.
- Heat gates:
  - Hacker News: 100+ points or 20+ comments.
  - Reddit: 50+ score or 20+ comments.
  - GitHub: 500+ stars or 50+ forks.
- Each signal must include a source URL, heat evidence, and a short recommendation reason.
- High-heat signals can still be too technical; do not over-explain technical details. Translate them into account-fit angles.
- The second section should include 3 to 5 content ideas based on account fit.
- Do not include `不建议追的热点` or `market memory` in the daily Feishu push.

## Memory Rules

Save daily reports under:

`memory/market/reports/YYYY-MM-DD.md`

If a pattern repeats across multiple days, add it to `memory/market/patterns.md`.

If a pattern becomes important for the account's own publishing rules, suggest updating `memory/content_guidelines.md`.

Market memory is a background upstream archive, not a daily push section and not the Xiaohongshu benchmark layer. It exists so repeated external patterns can be reviewed later, then cross-checked against Xiaohongshu benchmark samples or the user's own data before being promoted into account guidelines.

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
