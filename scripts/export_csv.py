#!/usr/bin/env python3
"""Export scored creators to CSV."""

import argparse
import csv
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Export scored creators to CSV")
    parser.add_argument("--input", required=True, help="Path to scored_creators.json")
    parser.add_argument("--output", default="output/influencer_report.csv")
    args = parser.parse_args()

    with open(args.input) as f:
        creators = json.load(f)

    if not creators:
        print("[WARN] No creators to export")
        sys.exit(0)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    fields = [
        "rank",
        "handle",
        "platform",
        "display_name",
        "follower_count",
        "engagement_rate",
        "niche_fit_score",
        "score_reasoning",
        "bio",
        "profile_url",
        "sample_content_link",
        "outreach_message",
    ]

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for c in creators:
            # Clean up bio for CSV
            c["bio"] = (c.get("bio") or "")[:200].replace("\n", " ")
            c["outreach_message"] = (c.get("outreach_message") or "").replace("\n", " ")
            writer.writerow(c)

    print(f"[DONE] Exported {len(creators)} creators to {args.output}")


if __name__ == "__main__":
    main()
