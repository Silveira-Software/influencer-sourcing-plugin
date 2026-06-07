#!/usr/bin/env python3
"""Source influencer/creator candidates from Instagram and TikTok via Apify."""

import argparse
import json
import os
import sys
import time
import requests

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
BASE_URL = "https://api.apify.com/v2"

# Actor IDs
TIKTOK_SCRAPER = "clockworks~tiktok-scraper"
IG_HASHTAG_SCRAPER = "apify~instagram-hashtag-scraper"
IG_PROFILE_SCRAPER = "apify~instagram-profile-scraper"


def run_actor_sync(actor_id: str, input_data: dict, timeout: int = 300) -> list:
    """Run an Apify actor synchronously and return dataset items."""
    url = f"{BASE_URL}/acts/{actor_id}/run-sync-get-dataset-items"
    resp = requests.post(
        url,
        params={"token": APIFY_TOKEN},
        json=input_data,
        timeout=timeout,
    )
    if not resp.ok:
        print(f"[ERROR] Actor {actor_id} failed ({resp.status_code}): {resp.text[:500]}", file=sys.stderr)
        return []
    return resp.json()


def to_number(value) -> float | None:
    if isinstance(value, (int, float)) and not (value != value):  # not NaN
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").replace("%", ""))
        except ValueError:
            return None
    return None


def search_tiktok(niche: str, max_results: int) -> list[dict]:
    """Search TikTok for creators in a niche."""
    print(f"[TikTok] Searching for '{niche}' creators...")
    results = run_actor_sync(TIKTOK_SCRAPER, {
        "searchQueries": [niche],
        "resultsPerPage": min(max_results * 5, 100),
        "searchSection": "/user",
    })

    # Extract unique authors from video results
    authors = {}
    for item in results:
        author = item.get("authorMeta", {})
        if not author:
            continue
        handle = str(author.get("name", "")).strip()
        if not handle or handle in authors:
            continue

        fans = to_number(author.get("fans") or author.get("followers"))
        hearts = to_number(author.get("heart"))
        video_count = to_number(author.get("video"))

        # Calculate engagement rate
        engagement = None
        diggs = to_number(item.get("diggCount"))
        comments = to_number(item.get("commentCount"))
        plays = to_number(item.get("playCount"))
        if diggs is not None and plays and plays > 0:
            engagement = ((diggs + (comments or 0)) / plays) * 100
        elif hearts and fans and fans > 0 and video_count and video_count > 0:
            engagement = ((hearts / video_count) / fans) * 100

        authors[handle] = {
            "handle": handle,
            "platform": "tiktok",
            "display_name": str(author.get("nickName", handle)),
            "follower_count": fans,
            "engagement_rate": round(engagement, 2) if engagement else None,
            "bio": str(author.get("signature", "")),
            "profile_url": str(author.get("profileUrl", f"https://www.tiktok.com/@{handle}")),
            "avatar_url": str(author.get("avatar", "")),
            "sample_content_link": str(item.get("webVideoUrl", f"https://www.tiktok.com/@{handle}")),
        }

    print(f"[TikTok] Found {len(authors)} unique creators")
    return list(authors.values())


def search_instagram(niche: str, max_results: int) -> list[dict]:
    """Search Instagram for creators in a niche via hashtag discovery + profile enrichment."""
    # Step 1: Find creators via hashtag posts
    hashtags = [w for w in niche.lower().replace(",", " ").split() if w.isalnum()][:3]
    print(f"[Instagram] Searching hashtags: {hashtags}")

    posts = run_actor_sync(IG_HASHTAG_SCRAPER, {
        "hashtags": hashtags,
        "resultsLimit": min(max_results * 5, 200),
    })

    # Extract unique usernames
    usernames = list(dict.fromkeys(
        str(p.get("ownerUsername", "")).strip()
        for p in posts
        if p.get("ownerUsername")
    ))[:min(max_results * 2, 40)]

    if not usernames:
        print("[Instagram] No usernames found from hashtag search")
        return []

    print(f"[Instagram] Found {len(usernames)} usernames, fetching profiles...")

    # Step 2: Get full profiles
    profiles = run_actor_sync(IG_PROFILE_SCRAPER, {"usernames": usernames})

    creators = []
    for p in profiles:
        handle = str(p.get("username", "")).strip()
        if not handle:
            continue

        followers = to_number(p.get("followersCount") or p.get("followers"))
        engagement = None

        # Try direct engagement fields
        avg_likes = to_number(p.get("avgLikes"))
        avg_comments = to_number(p.get("avgComments"))
        if avg_likes is not None and followers and followers > 0:
            engagement = ((avg_likes + (avg_comments or 0)) / followers) * 100

        # Fallback: calculate from latest posts
        if engagement is None and followers and followers > 0:
            latest = p.get("latestPosts", [])
            if latest:
                total_eng = sum(
                    (to_number(post.get("likesCount")) or 0) + (to_number(post.get("commentsCount")) or 0)
                    for post in latest[:12]
                )
                avg_eng = total_eng / min(len(latest), 12)
                engagement = (avg_eng / followers) * 100

        latest_posts = p.get("latestPosts", [])
        first_post_url = latest_posts[0].get("url", "") if latest_posts else ""

        creators.append({
            "handle": handle,
            "platform": "instagram",
            "display_name": str(p.get("fullName", handle)),
            "follower_count": followers,
            "engagement_rate": round(engagement, 2) if engagement else None,
            "bio": str(p.get("biography", "")),
            "profile_url": str(p.get("url", f"https://www.instagram.com/{handle}/")),
            "avatar_url": str(p.get("profilePicUrl") or p.get("profilePicUrlHD", "")),
            "sample_content_link": first_post_url or str(p.get("url", "")),
        })

    print(f"[Instagram] Got {len(creators)} profiles with data")
    return creators


def filter_creators(creators: list[dict], min_followers: int, max_followers: int, min_engagement: float) -> list[dict]:
    """Filter creators by follower range and engagement rate."""
    with_data = [c for c in creators if c.get("follower_count") is not None]
    without_data = [c for c in creators if c.get("follower_count") is None]

    matched = [
        c for c in with_data
        if min_followers <= (c["follower_count"] or 0) <= max_followers
        and (c.get("engagement_rate") or 0) >= min_engagement
    ]

    # Include unknowns as fallback
    return matched + without_data


def main():
    parser = argparse.ArgumentParser(description="Source influencer candidates from Instagram/TikTok")
    parser.add_argument("--niche", required=True, help="Niche keywords (e.g., 'clean beauty skincare')")
    parser.add_argument("--platform", choices=["instagram", "tiktok", "both"], default="both")
    parser.add_argument("--min-followers", type=int, default=10000)
    parser.add_argument("--max-followers", type=int, default=250000)
    parser.add_argument("--min-engagement", type=float, default=2.0)
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--output", default="output/raw_creators.json")
    args = parser.parse_args()

    if not APIFY_TOKEN:
        print("[ERROR] APIFY_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    platforms = ["instagram", "tiktok"] if args.platform == "both" else [args.platform]
    all_creators = []

    for platform in platforms:
        if platform == "tiktok":
            all_creators.extend(search_tiktok(args.niche, args.max_results))
        else:
            all_creators.extend(search_instagram(args.niche, args.max_results))

    # Deduplicate
    seen = set()
    unique = []
    for c in all_creators:
        key = f"{c['platform']}:{c['handle']}"
        if key not in seen:
            seen.add(key)
            unique.append(c)

    # Filter
    filtered = filter_creators(unique, args.min_followers, args.max_followers, args.min_engagement)
    result = filtered[:args.max_results]

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n[DONE] {len(result)} creators saved to {args.output}")
    print(f"  Total sourced: {len(unique)} | After filtering: {len(filtered)} | Returned: {len(result)}")


if __name__ == "__main__":
    main()
