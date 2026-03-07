"""Download podcast episodes from RSS feed."""
import os
import re
import json
import urllib.request
from pathlib import Path

import feedparser

RSS_URL = os.environ.get("PODCAST_RSS_URL", "https://your-podcast-rss-feed-url")
AUDIO_DIR = Path(__file__).parent / "audio"
MANIFEST_FILE = Path(__file__).parent / "manifest.json"


def sanitize_filename(title):
    """Create a safe filename from episode title."""
    # Extract episode number if present
    match = re.search(r'פרק\s*(\d+)', title)
    if match:
        num = match.group(1)
        return f"ep{num}"
    # Bonus/trailer
    if 'בזק' in title or 'bonus' in title.lower():
        return f"bonus_{re.sub(r'[^a-zA-Z0-9]', '_', title[:30])}"
    if 'טיזר' in title or 'trailer' in title.lower():
        return "trailer"
    return re.sub(r'[^a-zA-Z0-9]', '_', title[:40])


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching RSS feed: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    print(f"Found {len(feed.entries)} episodes in feed.\n")

    manifest = []
    existing = {f.stem for f in AUDIO_DIR.glob("*.mp3")}

    for entry in feed.entries:
        title = entry.get("title", "unknown")
        date = entry.get("published", "")

        # Get audio URL
        audio_url = None
        for link in entry.get("links", []):
            if link.get("type", "").startswith("audio"):
                audio_url = link["href"]
                break
        if not audio_url:
            for enc in entry.get("enclosures", []):
                if enc.get("type", "").startswith("audio"):
                    audio_url = enc["href"]
                    break

        if not audio_url:
            print(f"  SKIP (no audio): {title}")
            continue

        filename = sanitize_filename(title)
        manifest.append({
            "filename": filename,
            "title": title,
            "date": date,
            "audio_url": audio_url,
        })

        filepath = AUDIO_DIR / f"{filename}.mp3"
        if filename in existing:
            print(f"  EXISTS: {filename} - {title[:50]}")
            continue

        print(f"  Downloading: {filename} - {title[:50]}...")
        try:
            urllib.request.urlretrieve(audio_url, str(filepath))
            print(f"    OK ({filepath.stat().st_size // (1024*1024)}MB)")
        except Exception as e:
            print(f"    FAILED: {e}")

    # Save manifest
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(manifest)} episodes in manifest.")
    print(f"Audio files in: {AUDIO_DIR}")


if __name__ == "__main__":
    main()
