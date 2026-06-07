---
description: Re-score or deep-analyze previously sourced creators against a new or updated brand brief. Use when user wants to score, re-evaluate, or analyze creators they've already sourced.
---

# Score Creators

Re-analyze creators from a previous sourcing run against a brand brief.

Read `output/influencer_report.json` to load previously sourced creators. Then for each creator:

1. Use WebFetch to visit their profile URL and analyze recent content
2. Re-evaluate niche fit, content quality, and audience alignment against the brand brief provided in `$ARGUMENTS`
3. Update scores and rewrite outreach DMs with fresh context

Save updated results to `output/influencer_report.json` and re-export CSV.
