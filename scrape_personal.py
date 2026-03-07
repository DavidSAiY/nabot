"""Scrape tweets from a personal X account to analyze voice patterns.

Usage:
  python3 scrape_personal.py              — Uses X_PERSONAL_HANDLE env var
  python3 scrape_personal.py your_handle  — Scrapes specific handle
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
HANDLE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("X_PERSONAL_HANDLE", "your_handle")
OUTPUT_FILE = BASE_DIR / "knowledge" / "engagement" / f"{HANDLE}_tweets.json"

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

    # Go to personal profile
    page.goto(f"https://x.com/{HANDLE}", wait_until="domcontentloaded")
    time.sleep(8)

    print(f"URL: {page.url}")
    if "/login" in page.url:
        print("Session expired!")
        exit(1)

    all_tweets = []
    seen_texts = set()
    scroll_count = 0
    max_scrolls = 40  # ~200 tweets

    while scroll_count < max_scrolls:
        tweets = page.locator('article[data-testid="tweet"]')
        count = tweets.count()

        for i in range(count):
            try:
                tweet_el = tweets.nth(i)
                text_el = tweet_el.locator('[data-testid="tweetText"]')
                if text_el.count() == 0:
                    continue
                text = text_el.first.inner_text(timeout=2000)

                if text in seen_texts:
                    continue
                seen_texts.add(text)

                # Get time
                time_el = tweet_el.locator("time")
                tweet_time = ""
                if time_el.count() > 0:
                    tweet_time = time_el.first.get_attribute("datetime") or ""

                # Get metrics
                metrics = {}
                for metric in ["reply", "retweet", "like"]:
                    try:
                        btn = tweet_el.locator(f'button[data-testid="{metric}"]')
                        if btn.count() > 0:
                            aria = btn.first.get_attribute("aria-label") or ""
                            parts = aria.split()
                            if parts and parts[0].replace(",", "").isdigit():
                                metrics[metric] = int(parts[0].replace(",", ""))
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
                except Exception:
                    metrics["views"] = 0

                all_tweets.append({
                    "text": text,
                    "time": tweet_time,
                    "metrics": metrics,
                })

            except Exception:
                continue

        print(f"Scroll {scroll_count + 1}: {len(all_tweets)} unique tweets collected")

        # Scroll down
        page.evaluate("window.scrollBy(0, 2000)")
        time.sleep(3)
        scroll_count += 1

        # Check if we hit the end
        end_el = page.locator('text="These posts are protected"')
        if end_el.count() > 0:
            break

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_tweets, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_tweets)} tweets to {OUTPUT_FILE}")

    # Update session
    new_storage = context.storage_state()
    with open(SESSION_FILE, "w") as f:
        json.dump(new_storage, f, indent=2)
