"""
NaBot - AI co-writing tweet bot
Generates tweets/day, queues for approval, posts approved ones.

Usage:
  python3 bot.py generate   — Generate tweets for today
  python3 bot.py approve    — Review and approve/reject queued tweets
  python3 bot.py post       — Post approved tweets to X.com
  python3 bot.py analyze    — Analyze engagement on recent tweets
  python3 bot.py status     — Show current queue status

Configuration:
  Set your X handle in config or pass as environment variable:
    export X_HANDLE=your_handle
"""
import json
import os
import sys
import time
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).parent
TWEETS_DIR = BASE_DIR / "tweets"
QUEUE_FILE = TWEETS_DIR / "queue.json"
POSTED_FILE = TWEETS_DIR / "posted.json"
ENGAGEMENT_FILE = BASE_DIR / "knowledge" / "engagement" / "engagement_log.json"
SESSION_FILE = BASE_DIR / "x_session.json"

X_HANDLE = os.environ.get("X_HANDLE", "your_handle")


def load_json(path, default=None):
    if default is None:
        default = []
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_tweets():
    """Generate tweets and add to queue for approval."""
    queue = load_json(QUEUE_FILE)
    today = date.today().isoformat()

    today_tweets = [t for t in queue if t.get("generated_date") == today]
    if today_tweets:
        print(f"Already generated {len(today_tweets)} tweets for today.")
        print("Run 'python3 bot.py approve' to review them.")
        return

    print("Generating tweets...")
    print("Use Claude Code to generate tweets with the x-tweet skill:")
    print()
    print('  Just tell Claude: "generate tweets for today"')
    print("  Claude will use the x-tweet skill and context profiles.")
    print()
    print("Then add them to the queue with:")
    print('  python3 bot.py add "tweet text here"')


def add_tweet(text):
    """Add a tweet to the approval queue."""
    queue = load_json(QUEUE_FILE)
    tweet = {
        "id": len(queue) + 1,
        "text": text,
        "status": "pending",
        "generated_date": date.today().isoformat(),
        "created_at": datetime.now().isoformat(),
    }
    queue.append(tweet)
    save_json(QUEUE_FILE, queue)
    print(f"Tweet #{tweet['id']} added to queue (pending approval).")
    print(f"  \"{text[:80]}{'...' if len(text) > 80 else ''}\"")


def approve_tweets():
    """Interactive approval of queued tweets."""
    queue = load_json(QUEUE_FILE)
    pending = [t for t in queue if t["status"] == "pending"]

    if not pending:
        print("No tweets pending approval.")
        return

    print(f"\n{len(pending)} tweet(s) pending approval:\n")

    for tweet in pending:
        print(f"--- Tweet #{tweet['id']} ({tweet['generated_date']}) ---")
        print(f"{tweet['text']}")
        print()

        while True:
            choice = input("[a]pprove / [r]eject / [e]dit / [s]kip? ").strip().lower()
            if choice == "a":
                tweet["status"] = "approved"
                tweet["approved_at"] = datetime.now().isoformat()
                print("Approved!")
                break
            elif choice == "r":
                tweet["status"] = "rejected"
                print("Rejected.")
                break
            elif choice == "e":
                new_text = input("New text: ").strip()
                if new_text:
                    tweet["text"] = new_text
                    tweet["status"] = "approved"
                    tweet["approved_at"] = datetime.now().isoformat()
                    tweet["edited"] = True
                    print("Edited and approved!")
                break
            elif choice == "s":
                print("Skipped.")
                break

        print()

    save_json(QUEUE_FILE, queue)
    approved = len([t for t in queue if t["status"] == "approved" and not t.get("posted")])
    print(f"\n{approved} tweet(s) ready to post. Run 'python3 bot.py post' to publish.")


def post_tweets():
    """Post approved tweets to X.com."""
    if not SESSION_FILE.exists():
        print("No session found. Run import_cookies.py first to save your X.com session.")
        return

    queue = load_json(QUEUE_FILE)
    posted = load_json(POSTED_FILE)
    to_post = [t for t in queue if t["status"] == "approved" and not t.get("posted")]

    if not to_post:
        print("No approved tweets to post.")
        return

    print(f"Posting {len(to_post)} tweet(s) to X.com...\n")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        page.goto("https://x.com/home", wait_until="domcontentloaded")
        time.sleep(5)

        if "/login" in page.url or "/flow" in page.url:
            print("Session expired! Run import_cookies.py to re-authenticate.")
            browser.close()
            return

        print("Session valid. Logged into X.com.\n")

        for tweet in to_post:
            print(f"Posting tweet #{tweet['id']}: \"{tweet['text'][:60]}...\"")

            try:
                page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
                time.sleep(3)

                tweet_box = page.locator('[data-testid="tweetTextarea_0"]')
                tweet_box.click()
                time.sleep(0.5)
                tweet_box.type(tweet["text"], delay=20)
                time.sleep(1)

                page.locator('[data-testid="tweetButton"]').click()
                time.sleep(3)

                tweet["posted"] = True
                tweet["posted_at"] = datetime.now().isoformat()
                tweet["status"] = "posted"

                posted.append(tweet)
                print(f"  Posted!")

                time.sleep(5)

            except Exception as e:
                print(f"  Failed to post: {e}")
                tweet["post_error"] = str(e)

        save_json(QUEUE_FILE, queue)
        save_json(POSTED_FILE, posted)

        storage = context.storage_state()
        with open(SESSION_FILE, "w") as f:
            json.dump(storage, f, indent=2)

        browser.close()

    print(f"\nDone. {len([t for t in to_post if t.get('posted')])} tweets posted.")


def analyze_engagement():
    """Scrape engagement metrics for posted tweets."""
    if not SESSION_FILE.exists():
        print("No session found. Run import_cookies.py first.")
        return

    posted = load_json(POSTED_FILE)
    if not posted:
        print("No posted tweets to analyze.")
        return

    print(f"Analyzing engagement for {len(posted)} posted tweets...\n")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        page.goto(f"https://x.com/{X_HANDLE}", wait_until="domcontentloaded")
        time.sleep(5)

        if "/login" in page.url:
            print("Session expired!")
            browser.close()
            return

        tweets = page.locator('article[data-testid="tweet"]')
        count = tweets.count()
        print(f"Found {count} tweets on profile.\n")

        engagement_data = load_json(ENGAGEMENT_FILE)

        for i in range(min(count, 10)):
            tweet_el = tweets.nth(i)
            try:
                text = tweet_el.locator('[data-testid="tweetText"]').inner_text(timeout=3000)
                metrics = {}
                for metric in ["reply", "retweet", "like"]:
                    try:
                        val = tweet_el.locator(f'[data-testid="{metric}"]').inner_text(timeout=2000)
                        metrics[metric] = val.strip() if val.strip() else "0"
                    except Exception:
                        metrics[metric] = "0"

                print(f"Tweet: \"{text[:60]}...\"")
                print(f"  Replies: {metrics['reply']} | Retweets: {metrics['retweet']} | Likes: {metrics['like']}")

                engagement_data.append({
                    "text": text,
                    "metrics": metrics,
                    "scraped_at": datetime.now().isoformat(),
                })
            except Exception:
                continue

        save_json(ENGAGEMENT_FILE, engagement_data)
        print(f"\nEngagement data saved to {ENGAGEMENT_FILE}")

        browser.close()


def show_status():
    """Show current queue status."""
    queue = load_json(QUEUE_FILE)
    posted = load_json(POSTED_FILE)

    pending = [t for t in queue if t["status"] == "pending"]
    approved = [t for t in queue if t["status"] == "approved" and not t.get("posted")]
    rejected = [t for t in queue if t["status"] == "rejected"]

    print(f"Queue Status:")
    print(f"  Pending approval: {len(pending)}")
    print(f"  Approved (ready to post): {len(approved)}")
    print(f"  Rejected: {len(rejected)}")
    print(f"  Posted (total): {len(posted)}")

    if approved:
        print(f"\nReady to post:")
        for t in approved:
            print(f"  #{t['id']}: \"{t['text'][:70]}...\"")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "generate":
        generate_tweets()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: python3 bot.py add \"tweet text\"")
            return
        add_tweet(sys.argv[2])
    elif cmd == "approve":
        approve_tweets()
    elif cmd == "post":
        post_tweets()
    elif cmd == "analyze":
        analyze_engagement()
    elif cmd == "status":
        show_status()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
