# Influencer Sourcing Plugin for Claude Code

Find, score, and rank influencer/creator candidates from Instagram and TikTok — powered by Apify scraping and Gemini AI scoring.

## What it does

- **Source creators** from TikTok and Instagram by niche keywords
- **AI-score** each creator's brand fit (1-10) using Gemini
- **Generate personalized outreach DMs** referencing each creator's actual content
- **Export to CSV** for your team

## Setup

### 1. Install the plugin

```bash
claude --plugin-dir /path/to/influencer-sourcing-plugin
```

Or install from GitHub:
```
/plugin install mikefutia/influencer-sourcing-plugin
```

### 2. Set environment variables

```bash
export APIFY_TOKEN="your_apify_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

- Get an Apify key at [apify.com](https://apify.com)
- Get a Gemini key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 3. Install Python dependency

```bash
pip install requests
```

## Usage

### Quick sourcing
```
/influencer-sourcing:source-influencers clean beauty skincare
```

### Score against a brand brief
```
/influencer-sourcing:score-creators GlowVita - clean beauty supplements for women 25-40, launching collagen product
```

### Export results
```
/influencer-sourcing:export-csv
```

### Or just ask naturally
> "Find me 20 TikTok creators in the fitness space with 50K-500K followers and at least 3% engagement"

The plugin triggers automatically on influencer sourcing requests.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/influencer-sourcing:source-influencers` | Find creators by niche from IG/TikTok |
| `/influencer-sourcing:score-creators` | Score creators against a brand brief |
| `/influencer-sourcing:export-csv` | Export scored results to CSV |

## How it works

1. **Sourcing** — Uses Apify actors (`clockworks~tiktok-scraper` for TikTok, `apify~instagram-hashtag-scraper` + `apify~instagram-profile-scraper` for Instagram) to find creators by niche
2. **Scoring** — Sends creator profiles to Gemini 3 Flash with the brand brief context. Gemini scores niche fit and writes personalized outreach DMs
3. **Export** — Generates a clean CSV with all data

## License

MIT
