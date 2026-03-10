"""Scrape tweets and engagement from your X profile using twitter-cli.

Usage:
  python3 scrape_profile.py              — Uses X_HANDLE env var
  python3 scrape_profile.py your_handle  — Scrapes specific handle
"""
import sys
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
ENGAGEMENT_FILE = BASE_DIR / "knowledge" / "engagement" / "engagement_log.json"
TWITTER_CLI = Path.home() / "Library" / "Python" / "3.9" / "bin" / "twitter"

HANDLE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("X_HANDLE", "your_handle")
MAX_TWEETS = int(sys.argv[2]) if len(sys.argv) > 2 else 10


def scrape():
    result = subprocess.run(
        [str(TWITTER_CLI), "user-posts", HANDLE, "-n", str(MAX_TWEETS), "--json"],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    # Extract JSON from output (skip status lines)
    lines = result.stdout.strip().split("\n")
    json_start = next(i for i, line in enumerate(lines) if line.strip().startswith("["))
    raw = "\n".join(lines[json_start:])
    tweets = json.loads(raw)

    engagement_data = []
    ENGAGEMENT_FILE.parent.mkdir(parents=True, exist_ok=True)

    for tweet in tweets:
        if tweet.get("isRetweet"):
            continue

        text = tweet.get("text", "")
        metrics = tweet.get("metrics", {})
        created = tweet.get("createdAt", "")

        print(f"Tweet {len(engagement_data)+1}: \"{text[:70]}{'...' if len(text) > 70 else ''}\"")
        print(f"  Time: {created}")
        print(f"  Replies: {metrics.get('replies', 0)} | Retweets: {metrics.get('retweets', 0)} | Likes: {metrics.get('likes', 0)} | Views: {metrics.get('views', 0)}")
        print()

        engagement_data.append({
            "id": tweet.get("id"),
            "text": text,
            "tweet_time": created,
            "metrics": {
                "reply": metrics.get("replies", 0),
                "retweet": metrics.get("retweets", 0),
                "like": metrics.get("likes", 0),
                "views": metrics.get("views", 0),
                "bookmarks": metrics.get("bookmarks", 0),
                "quotes": metrics.get("quotes", 0),
            },
            "scraped_at": datetime.now().isoformat(),
        })

    with open(ENGAGEMENT_FILE, "w") as f:
        json.dump(engagement_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(engagement_data)} tweets to {ENGAGEMENT_FILE}")


if __name__ == "__main__":
    scrape()
