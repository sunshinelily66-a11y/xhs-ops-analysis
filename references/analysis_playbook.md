# Xiaohongshu Analysis Playbook

## Common Field Mapping

Use the first matching field you can find from the export. Do not force a mapping when the data is absent.

- Title: `标题`, `笔记标题`, `note_title`, `title`
- Content: `正文`, `笔记内容`, `content`, `caption`
- Cover: `封面`, `cover`, `cover_text`, `thumbnail`, `首图`
- Publish time: `发布时间`, `发布日期`, `publish_time`, `created_at`
- Views / exposure: `浏览量`, `曝光`, `阅读量`, `views`, `impressions`
- Likes: `点赞`, `like_count`
- Comments: `评论`, `comment_count`
- Saves: `收藏`, `save_count`, `favorites`
- Shares: `分享`, `share_count`
- Follows / conversion: `关注`, `follow_count`, `new_followers`, `profile_visits`

## Grouping Logic

- Top performers: top 10% to 20% by the main KPI that best matches the user's goal.
- Median group: notes near the middle of the distribution for baseline comparison.
- Underperformers: lowest 20% when there are enough samples.
- If multiple exports are provided, compare by time range, campaign, or file naming convention.

## Content Review Focus

Judge each note on:

- topic clarity
- user pain point or benefit
- opening hook
- structure and readability
- specificity and practical value
- CTA strength
- repeatable template potential

## Cover Review Focus

Judge each cover on:

- whether the message is readable at a glance
- whether the visual hierarchy is clear
- whether the text is too dense or too empty
- whether the visual matches the title promise
- whether the style is consistent and recognizable

## Title Review Focus

Judge each title on:

- curiosity
- benefit promise
- specificity
- keyword density
- scene or audience clarity
- whether it avoids vague filler language

## Recommendation Rules

- Prefer recommendations that can be repeated across a content series.
- Convert findings into concrete next actions, not abstract praise.
- Give at least one title formula, one cover direction, and one content direction when the data supports it.
- If the sample size is small, mark recommendations as directional and suggest collecting more data before hard decisions.
