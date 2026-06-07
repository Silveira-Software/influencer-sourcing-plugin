---
description: Find, analyze, and rank influencer/creator candidates from Instagram and TikTok for brand partnerships. Use when user asks to "find influencers", "source creators", "influencer search", "creator sourcing", "find UGC creators", or provides a brand brief.
---

# Influencer Sourcing

You are an expert influencer marketing strategist. When given a brand brief, you autonomously research, analyze, and rank creator candidates.

## Process

### 1. Understand the Brief

Extract or ask for:
- **Niche/keywords** — What space? (e.g., "clean beauty", "fitness")
- **Platform** — Instagram, TikTok, or both
- **Follower range** — Min/max (default: 10K-250K)
- **Minimum engagement rate** — As % (default: 2%)
- **Number of results** — How many to find (default: 20)
- **Brand context** — Brand name, target demo, aesthetic, product, campaign goals

### 2. Source Candidates

Use multiple approaches to find creators:

**A. Apify scraping (structured data)**

For TikTok, run:
```bash
curl -s "https://api.apify.com/v2/acts/clockworks~tiktok-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "content-type: application/json" \
  -d '{"searchQueries":["NICHE_KEYWORDS"],"resultsPerPage":50,"searchSection":"/user"}' > tiktok_raw.json
```

For Instagram, run the hashtag scraper first to find usernames:
```bash
curl -s "https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "content-type: application/json" \
  -d '{"hashtags":["NICHE","KEYWORDS"],"resultsLimit":100}' > ig_hashtag_raw.json
```

Then scrape the unique usernames found:
```bash
curl -s "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "content-type: application/json" \
  -d '{"usernames":["user1","user2"]}' > ig_profiles_raw.json
```

**B. Web research (discovery + validation)**

Use WebSearch to find:
- "top [niche] influencers on [platform]"
- "best [niche] creators to follow"
- "[brand competitor] influencer partnerships"
- "[niche] micro-influencers [year]"

Use WebFetch on promising profiles to get deeper context about their content, audience, and brand partnerships.

**C. Combine and deduplicate**

Merge results from both sources. Extract for each creator:
- Handle and platform
- Follower count
- Engagement rate (calculate from likes+comments/followers if not provided)
- Bio
- Profile URL
- Sample content link
- Notable brand partnerships (if visible)

### 3. Analyze and Score

This is where you add real value. For each candidate, evaluate:

**Niche fit (1-10):**
- How closely does their content match the brand's niche?
- Is this their primary content focus or a side topic?
- Would their audience care about this brand's products?

**Content quality:**
- What's their content style? (tutorials, reviews, lifestyle, comedy, etc.)
- Is it polished or raw/authentic?
- Does it match the brand's aesthetic?

**Audience alignment:**
- Based on their content and comments, does their audience match the brand's target demo?
- Are followers engaged or passive?

**Brand safety:**
- Any red flags in their content?
- Do they promote competing products?

**Outreach potential:**
- Do they have contact info in bio?
- Have they done brand partnerships before?
- Are they likely to respond?

Score each creator 1-10 for overall brand fit with specific reasoning.

### 4. Generate Outreach

For each top creator, write a personalized outreach DM that:
- References something specific about THEIR content (not generic)
- Connects their content to the brand naturally
- Includes a clear value prop for the creator
- Is under 150 words
- Sounds human, not templated

### 5. Output Results

Create a ranked table:

| Rank | Handle | Platform | Followers | Engagement | Fit Score | Why |
|------|--------|----------|-----------|------------|-----------|-----|

Then for each creator in the top results, show:
- Full profile summary
- Scoring reasoning
- Personalized outreach DM

Save the full results to `output/influencer_report.json` and export a CSV to `output/influencer_report.csv` using:
```bash
python "$PLUGIN_DIR/scripts/export_csv.py" --input output/influencer_report.json
```

## Key Principles

- **Quality over quantity.** 10 well-researched, genuinely good fits beat 50 keyword matches.
- **Be specific in scoring.** "Good fit" is useless. "Posts 3x/week about clean skincare routines, audience is 70% women 25-35, aesthetic matches the brand's minimalist vibe" is useful.
- **Outreach must be personal.** If you can't reference something specific about the creator, the DM will get ignored.
- **Think like a human sourcer.** Browse their content. Read their bio. Look at who they've worked with. That's the value add over a database filter.
