#!/usr/bin/env python3
"""Score creators against a brand brief using Gemini and generate personalized outreach."""

import argparse
import json
import os
import sys
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3-flash-preview"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
BATCH_SIZE = 10  # Score 10 creators per API call


def score_batch(creators: list[dict], brand_name: str, brand_context: str, campaign_goal: str) -> list[dict]:
    """Send a batch of creators to Gemini for scoring and outreach generation."""
    prompt = {
        "brand_brief": {
            "brand_name": brand_name,
            "brand_context": brand_context,
            "campaign_goal": campaign_goal,
        },
        "creators": [
            {
                "handle": c["handle"],
                "platform": c["platform"],
                "display_name": c.get("display_name", c["handle"]),
                "follower_count": c.get("follower_count"),
                "engagement_rate": c.get("engagement_rate"),
                "bio": c.get("bio", "")[:500],
                "profile_url": c.get("profile_url", ""),
                "sample_content_link": c.get("sample_content_link", ""),
            }
            for c in creators
        ],
    }

    system_prompt = """You are an influencer marketing expert. Score each creator's fit for the brand brief and write a personalized outreach DM.

Return ONLY valid JSON with this exact structure:
{
  "creators": [
    {
      "handle": "their_handle",
      "platform": "tiktok or instagram",
      "niche_fit_score": 7,
      "score_reasoning": "Brief explanation of why this score",
      "outreach_message": "Personalized DM referencing their actual content/bio"
    }
  ]
}

Scoring guidelines:
- 9-10: Perfect niche match, strong engagement, content style aligns with brand
- 7-8: Good fit, relevant content, audience likely overlaps
- 5-6: Moderate fit, some relevance but not core niche
- 3-4: Weak fit, tangential relevance
- 1-2: Poor fit, different niche entirely

Outreach DM guidelines:
- Keep it under 150 words
- Reference something specific from their bio or content
- Mention the brand naturally
- Include a clear value prop for the creator
- Sound human, not templated"""

    resp = requests.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": json.dumps(prompt)}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
            },
        },
        timeout=60,
    )

    if not resp.ok:
        print(f"[ERROR] Gemini API failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return []

    data = resp.json()
    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    if not content:
        print("[ERROR] Empty response from Gemini", file=sys.stderr)
        return []

    try:
        parsed = json.loads(content)
        return parsed.get("creators", [])
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse Gemini response: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Score creators against a brand brief using Gemini")
    parser.add_argument("--input", required=True, help="Path to raw_creators.json from source_creators.py")
    parser.add_argument("--brand-name", default="", help="Brand name")
    parser.add_argument("--brand-context", default="", help="Brand description, target audience, positioning")
    parser.add_argument("--campaign-goal", default="", help="What the campaign aims to achieve")
    parser.add_argument("--output", default="output/scored_creators.json")
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    with open(args.input) as f:
        creators = json.load(f)

    if not creators:
        print("[WARN] No creators to score")
        sys.exit(0)

    print(f"[Scoring] {len(creators)} creators against brand brief for {args.brand_name or 'unnamed brand'}...")

    # Score in batches
    all_scores = []
    for i in range(0, len(creators), BATCH_SIZE):
        batch = creators[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(creators) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"[Scoring] Batch {batch_num}/{total_batches} ({len(batch)} creators)...")

        scores = score_batch(batch, args.brand_name, args.brand_context, args.campaign_goal)
        all_scores.extend(scores)

        # Rate limit courtesy
        if i + BATCH_SIZE < len(creators):
            time.sleep(1)

    # Merge scores back into creator data
    score_map = {}
    for s in all_scores:
        key = f"{s.get('platform', '')}:{s.get('handle', '').lower()}"
        score_map[key] = s

    scored_creators = []
    for c in creators:
        key = f"{c['platform']}:{c['handle'].lower()}"
        score = score_map.get(key, {})
        scored_creators.append({
            **c,
            "niche_fit_score": score.get("niche_fit_score", 5),
            "score_reasoning": score.get("score_reasoning", "No scoring data available"),
            "outreach_message": score.get(
                "outreach_message",
                f"Hi {c.get('display_name', c['handle'])}, I came across your {c['platform']} content and think you'd be a great fit for a partnership. Would love to chat!",
            ),
        })

    # Sort by niche fit score descending
    scored_creators.sort(key=lambda x: x.get("niche_fit_score", 0), reverse=True)

    # Add rank
    for i, c in enumerate(scored_creators):
        c["rank"] = i + 1

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(scored_creators, f, indent=2)

    print(f"\n[DONE] Scored {len(scored_creators)} creators, saved to {args.output}")
    print("\nTop 5:")
    for c in scored_creators[:5]:
        print(f"  #{c['rank']} @{c['handle']} ({c['platform']}) — {c.get('follower_count', 'N/A')} followers, fit: {c['niche_fit_score']}/10")


if __name__ == "__main__":
    main()
