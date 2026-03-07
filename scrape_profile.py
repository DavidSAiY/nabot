"""Scrape tweets and engagement from your X profile.

Usage:
  python3 scrape_profile.py              — Uses X_HANDLE env var
  python3 scrape_profile.py your_handle  — Scrapes specific handle
"""
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path
from camoufox.sync_api import Camoufox

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "x_session.json"
ENGAGEMENT_FILE = BASE_DIR / "knowledge" / "engagement" / "engagement_log.json"

HANDLE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("X_HANDLE", "your_handle")

with Camoufox(headless=False) as browser:
    page = browser.new_page()
    context = page.context

    # Load session
    with open(SESSION_FILE) as f:
        storage = json.load(f)
    for cookie in storage.get("cookies", []):
        try:
            context.add_cookies([cookie])
        except Exception:
            pass

    # Go to profile
    page.goto(f"https://x.com/{HANDLE}", wait_until="domcontentloaded")
    time.sleep(8)

    print(f"URL: {page.url}")

    if "/login" in page.url:
        print("Session expired!")
        exit(1)

    # Scroll down to load more tweets
    page.evaluate("window.scrollBy(0, 500)")
    time.sleep(3)

    # Get tweet articles
    tweets = page.locator('article[data-testid="tweet"]')
    count = tweets.count()
    print(f"Found {count} tweets on profile.\n")

    engagement_data = []
    ENGAGEMENT_FILE.parent.mkdir(parents=True, exist_ok=True)

    for i in range(min(count, 20)):
        tweet_el = tweets.nth(i)
        try:
            text_el = tweet_el.locator('[data-testid="tweetText"]')
            if text_el.count() == 0:
                continue
            text = text_el.first.inner_text(timeout=3000)

            # Get time/date
            time_el = tweet_el.locator("time")
            tweet_time = ""
            if time_el.count() > 0:
                tweet_time = time_el.first.get_attribute("datetime") or ""

            # Get engagement metrics
            metrics = {}
            for metric in ["reply", "retweet", "like"]:
                try:
                    btn = tweet_el.locator(f'button[data-testid="{metric}"]')
                    if btn.count() > 0:
                        aria = btn.first.get_attribute("aria-label") or ""
                        # aria-label like "3 Likes" or "Reply"
                        parts = aria.split()
                        if parts and parts[0].isdigit():
                            metrics[metric] = int(parts[0])
                        else:
                            metrics[metric] = 0
                    else:
                        metrics[metric] = 0
                except Exception:
                    metrics[metric] = 0

            # Views
            try:
                view_btn = tweet_el.locator('a[href*="/analytics"]')
                if view_btn.count() > 0:
                    aria = view_btn.first.get_attribute("aria-label") or ""
                    parts = aria.split()
                    if parts and parts[0].replace(",", "").isdigit():
                        metrics["views"] = int(parts[0].replace(",", ""))
                    else:
                        metrics["views"] = 0
                else:
                    metrics["views"] = 0
            except Exception:
                metrics["views"] = 0

            print(f"Tweet {i+1}: \"{text[:70]}{'...' if len(text) > 70 else ''}\"")
            print(f"  Time: {tweet_time}")
            print(f"  Replies: {metrics.get('reply', 0)} | Retweets: {metrics.get('retweet', 0)} | Likes: {metrics.get('like', 0)} | Views: {metrics.get('views', 0)}")
            print()

            engagement_data.append({
                "text": text,
                "tweet_time": tweet_time,
                "metrics": metrics,
                "scraped_at": datetime.now().isoformat(),
            })
        except Exception as e:
            print(f"  Skipped tweet {i+1}: {e}")
            continue

    # Save engagement data
    with open(ENGAGEMENT_FILE, "w") as f:
        json.dump(engagement_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(engagement_data)} tweets to {ENGAGEMENT_FILE}")

    # Update session
    new_storage = context.storage_state()
    with open(SESSION_FILE, "w") as f:
        json.dump(new_storage, f, indent=2)
