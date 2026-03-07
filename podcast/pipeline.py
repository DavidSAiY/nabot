"""Pipeline: download → transcribe → delete audio, one episode at a time.

Only processes the last 50 episodes. Deletes audio after transcription to save disk.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

import feedparser
import whisper

RSS_URL = os.environ.get("PODCAST_RSS_URL", "https://your-podcast-rss-feed-url")
MAX_EPISODES = 50
MODEL_SIZE = "small"

BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audio"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
MANIFEST_FILE = BASE_DIR / "manifest.json"


def sanitize_filename(title):
    match = re.search(r'פרק\s*(\d+)', title)
    if match:
        return f"ep{match.group(1)}"
    if 'בזק' in title or 'bonus' in title.lower():
        return f"bonus_{re.sub(r'[^a-zA-Z0-9]', '_', title[:30])}"
    if 'טיזר' in title or 'trailer' in title.lower():
        return "trailer"
    return re.sub(r'[^a-zA-Z0-9]', '_', title[:40])


def get_episodes():
    """Fetch RSS and return last MAX_EPISODES with audio URLs."""
    print(f"Fetching RSS feed...")
    feed = feedparser.parse(RSS_URL)
    print(f"Found {len(feed.entries)} total episodes. Using last {MAX_EPISODES}.\n")

    episodes = []
    for entry in feed.entries:
        title = entry.get("title", "unknown")
        date = entry.get("published", "")
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
        if audio_url:
            episodes.append({
                "filename": sanitize_filename(title),
                "title": title,
                "date": date,
                "audio_url": audio_url,
            })

    # RSS feed is newest-first; take first MAX_EPISODES (most recent)
    return episodes[:MAX_EPISODES]


def download_episode(ep):
    """Download a single episode. Returns path or None."""
    filepath = AUDIO_DIR / f"{ep['filename']}.mp3"
    if filepath.exists():
        return filepath
    try:
        urllib.request.urlretrieve(ep["audio_url"], str(filepath))
        size_mb = filepath.stat().st_size // (1024 * 1024)
        print(f"  Downloaded ({size_mb}MB)")
        return filepath
    except Exception as e:
        print(f"  Download FAILED: {e}")
        return None


def transcribe_episode(model, audio_path, ep):
    """Transcribe a single episode. Returns True on success."""
    transcript_file = TRANSCRIPT_DIR / f"{ep['filename']}.json"
    txt_file = TRANSCRIPT_DIR / f"{ep['filename']}.txt"

    if transcript_file.exists():
        print(f"  Already transcribed")
        return True

    try:
        result = model.transcribe(
            str(audio_path),
            language="he",
            task="transcribe",
            verbose=False,
        )

        with open(transcript_file, "w") as f:
            json.dump({
                "text": result["text"],
                "segments": [
                    {"start": s["start"], "end": s["end"], "text": s["text"]}
                    for s in result["segments"]
                ],
                "language": result.get("language", "he"),
            }, f, indent=2, ensure_ascii=False)

        with open(txt_file, "w") as f:
            f.write(result["text"])

        duration_min = result["segments"][-1]["end"] / 60 if result["segments"] else 0
        print(f"  Transcribed: {len(result['segments'])} segments, ~{duration_min:.0f} min")
        return True

    except Exception as e:
        print(f"  Transcription FAILED: {e}")
        return False


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    episodes = get_episodes()

    # Save manifest
    with open(MANIFEST_FILE, "w") as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)

    # Load Whisper model once
    print(f"Loading Whisper model: {MODEL_SIZE}...")
    model = whisper.load_model(MODEL_SIZE)
    print("Model loaded.\n")

    success = 0
    for i, ep in enumerate(episodes):
        print(f"[{i+1}/{len(episodes)}] {ep['filename']} - {ep['title'][:50]}")

        # Skip if already transcribed
        if (TRANSCRIPT_DIR / f"{ep['filename']}.json").exists():
            print(f"  Already transcribed, skipping")
            success += 1
            continue

        # Download
        audio_path = download_episode(ep)
        if not audio_path:
            continue

        # Transcribe
        ok = transcribe_episode(model, audio_path, ep)
        if ok:
            success += 1

        # Delete audio to save disk
        try:
            audio_path.unlink()
            print(f"  Audio deleted")
        except Exception:
            pass

        print()

    print(f"\n=== Done: {success}/{len(episodes)} episodes transcribed ===")
    print(f"Transcripts in: {TRANSCRIPT_DIR}")
    print(f"\nRun 'python3 podcast/analyze_voice.py' to extract voice patterns.")


if __name__ == "__main__":
    main()
