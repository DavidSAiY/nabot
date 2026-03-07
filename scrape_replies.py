"""Scrape replies to your recent tweets on X.

Usage:
  python3 scrape_replies.py              — Uses X_HANDLE env var
  python3 scrape_replies.py your_handle  — Scrapes specific handle
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
REPLIES_FILE = BASE_DIR / "knowledge" / "engagement" / "replies.json"

HANDLE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("X_HANDLE", "your_handle")
MAX_TWEETS = 10
MAX_REPLIES_PER_TWEET = 20


def get_tweet_links(page):
    """Get links to individual tweets from the profile page."""
    tweets = page.locator('article[data-testid="tweet"]')
    count = tweets.count()
    links = []

    for i in range(min(count, MAX_TWEETS)):
        tweet_el = tweets.nth(i)
        try:
            # Get tweet text
            text_el = tweet_el.locator('[data-testid="tweetText"]')
            if text_el.count() == 0:
                continue
            text = text_el.first.inner_text(timeout=3000)

            # Get tweet link from the timestamp anchor
            time_link = tweet_el.locator('a[href*="/status/"]')
            if time_link.count() == 0:
                continue

            # Find the link that points to our own tweet (not quoted tweets)
            href = None
            for j in range(time_link.count()):
                h = time_link.nth(j).get_attribute("href") or ""
                if f"/{HANDLE}/" in h.lower() or f"/{HANDLE.lower()}/" in h.lower():
                    href = h
                    break

            if not href:
                # Fallback: take first status link
                href = time_link.first.get_attribute("href") or ""

            if "/status/" not in href:
                continue

            # Get reply count
            reply_count = 0
            reply_btn = tweet_el.locator('button[data-testid="reply"]')
            if reply_btn.count() > 0:
                aria = reply_btn.first.get_attribute("aria-label") or ""
                parts = aria.split()
                if parts and parts[0].isdigit():
                    reply_count = int(parts[0])

            if reply_count > 0:
                links.append({
                    "text": text[:100],
                    "url": f"https://x.com{href}" if href.startswith("/") else href,
                    "reply_count": reply_count,
                })

        except Exception as e:
            print(f"  Skipped tweet {i+1}: {e}")
            continue

    return links


def scrape_tweet_replies(page, tweet_url, tweet_text):
    """Navigate to a tweet and scrape the replies."""
    page.goto(tweet_url, wait_until="domcontentloaded")
    time.sleep(5)

    # Scroll to load replies
    page.evaluate("window.scrollBy(0, 800)")
    time.sleep(3)

    replies = []
    articles = page.locator('article[data-testid="tweet"]')
    count = articles.count()

    # Skip the first article (the original tweet itself)
    for i in range(1, min(count, MAX_REPLIES_PER_TWEET + 1)):
        reply_el = articles.nth(i)
        try:
            # Reply text
            text_el = reply_el.locator('[data-testid="tweetText"]')
            if text_el.count() == 0:
                continue
            reply_text = text_el.first.inner_text(timeout=3000)

            # Reply author
            author = ""
            user_link = reply_el.locator('a[href^="/"][role="link"] span')
            if user_link.count() > 0:
                for j in range(user_link.count()):
                    span_text = user_link.nth(j).inner_text(timeout=1000)
                    if span_text.startswith("@"):
                        author = span_text
                        break

            # Reply URL (from timestamp link)
            reply_url = ""
            status_link = reply_el.locator('a[href*="/status/"]')
            if status_link.count() > 0:
                href = status_link.first.get_attribute("href") or ""
                if "/status/" in href:
                    reply_url = f"https://x.com{href}" if href.startswith("/") else href

            # Reply time
            reply_time = ""
            time_el = reply_el.locator("time")
            if time_el.count() > 0:
                reply_time = time_el.first.get_attribute("datetime") or ""

            # Reply metrics
            metrics = {}
            for metric in ["reply", "retweet", "like"]:
                try:
                    btn = reply_el.locator(f'button[data-testid="{metric}"]')
                    if btn.count() > 0:
                        aria = btn.first.get_attribute("aria-label") or ""
                        parts = aria.split()
                        if parts and parts[0].isdigit():
                            metrics[metric] = int(parts[0])
                        else:
                            metrics[metric] = 0
                    else:
                        metrics[metric] = 0
                except Exception:
                    metrics[metric] = 0

            replies.append({
                "author": author,
                "text": reply_text,
                "url": reply_url,
                "time": reply_time,
                "metrics": metrics,
            })

            print(f"    {author}: \"{reply_text[:60]}{'...' if len(reply_text) > 60 else ''}\"")

        except Exception as e:
            continue

    return replies


def main():
    if not SESSION_FILE.exists():
        print("No session found. Run import_cookies.py first.")
        return

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

        if "/login" in page.url:
            print("Session expired!")
            return

        print(f"Scraping replies for @{HANDLE}...\n")

        # Get tweets with replies
        tweet_links = get_tweet_links(page)
        print(f"Found {len(tweet_links)} tweets with replies.\n")

        all_replies = []

        for tweet_info in tweet_links:
            print(f"Tweet: \"{tweet_info['text']}...\" ({tweet_info['reply_count']} replies)")

            replies = scrape_tweet_replies(page, tweet_info["url"], tweet_info["text"])

            if replies:
                all_replies.append({
                    "tweet_text": tweet_info["text"],
                    "tweet_url": tweet_info["url"],
                    "replies": replies,
                    "scraped_at": datetime.now().isoformat(),
                })

            print()

        # Save replies
        REPLIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPLIES_FILE, "w") as f:
            json.dump(all_replies, f, indent=2, ensure_ascii=False)

        print(f"Saved replies from {len(all_replies)} tweets to {REPLIES_FILE}")
        total_replies = sum(len(t["replies"]) for t in all_replies)
        print(f"Total replies scraped: {total_replies}")

        # Update session
        new_storage = context.storage_state()
        with open(SESSION_FILE, "w") as f:
            json.dump(new_storage, f, indent=2)


if __name__ == "__main__":
    main()
