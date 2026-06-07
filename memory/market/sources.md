# Market Observation Sources

## Preferred Sources

- Hacker News Algolia public search
- Reddit public JSON search
- GitHub Search API
- OpenAI official blog, docs, and changelog
- Anthropic official blog and Claude Code docs
- Cursor official site and changelog
- GitHub trending repositories, issues, discussions, and release notes
- Hacker News discussions
- Reddit communities related to AI coding, Python learning, productivity, and creator workflows
- Public newsletters and blogs about AI tooling
- Search-engine-indexed public X/Twitter posts or summaries
- Xiaohongshu public search results when accessible

## Useful Communities And Areas

- AI coding agents
- Python beginners
- frontend learning
- automation and scripting
- creator productivity
- no-code/low-code workflows
- content operations with AI

## Avoid Or Treat Carefully

- login-only pages
- captcha-gated pages
- paywalled newsletters
- raw scraped social timelines
- posts with no date, no source, or no clear claim
- large copied text dumps

## Storage Policy

Keep:

- source name
- URL
- date seen
- short summary
- observed pattern
- implication for this account

Do not keep:

- long verbatim social posts
- personal data beyond public handle/source names when not necessary
- private or login-gated content

## LLM Synthesis

DeepSeek can be used as a low-cost synthesis layer after public signals are collected.

Environment variables:

- `DEEPSEEK_API_KEY`: enables DeepSeek report generation.
- `DEEPSEEK_BASE_URL`: defaults to `https://api.deepseek.com`.
- `DEEPSEEK_MODEL`: defaults to `deepseek-v4-flash`.

If DeepSeek fails or the key is absent, the script falls back to a rule-based report.
