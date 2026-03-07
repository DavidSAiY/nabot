"""Analyze all transcripts to extract voice patterns for voice.json."""
import json
import re
from collections import Counter
from pathlib import Path

TRANSCRIPT_DIR = Path(__file__).parent / "transcripts"
OUTPUT_FILE = Path(__file__).parent / "voice_analysis.json"


# Hebrew colloquialisms and markers to track
MARKERS = {
    "בקיצור": "in short / anyway",
    "כאילו": "like (filler)",
    "באמת": "really/actually",
    "וואלה": "honestly (Arabic-origin)",
    "יאללה": "come on (Arabic-origin)",
    "רגע": "wait (pause)",
    "חבר'ה": "guys (group address)",
    "סבבה": "okay/fine/cool",
    "האמת הפשוטה": "the simple truth",
    "לא... אלא": "not... but rather",
    "כסף על הרצפה": "money on the floor",
    "והכל התחבר": "and it all connected",
    "הדבר הכי מדהים": "the most amazing thing",
    "חד משמעית": "absolutely",
    "השם ישמור": "God forbid",
    "אכילת ראש": "overthinking/headache",
    "נראה אותך": "let's see you try",
    "תרשמו אותי": "note this",
    "חוק מספר": "rule number",
    "מתחפשים": "cosplaying/pretending",
    "באהבה": "with love",
}

# Rhetorical patterns to detect
PATTERNS = {
    "לא_אלא": r"לא\s+\S+[\.,]\s*(אלא|אבל|זה)",
    "triple_repeat": r"(\S+)\.\s*\1\.\s*\1",
    "rhetorical_question": r"[?؟]\s",
    "english_terms": r"[A-Za-z]{3,}",
    "rule_number": r"חוק\s*(מספר\s*)?\d|rule\s*#?\d",
}


def analyze_transcript(text):
    """Analyze a single transcript for voice markers."""
    results = {
        "word_count": len(text.split()),
        "markers": {},
        "patterns": {},
        "english_terms": [],
    }

    # Count markers
    for marker, desc in MARKERS.items():
        count = text.count(marker)
        if count > 0:
            results["markers"][marker] = {
                "count": count,
                "description": desc,
            }

    # Detect patterns
    for name, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            if name == "english_terms":
                results["english_terms"] = [m for m in set(matches) if len(m) > 2]
            else:
                results["patterns"][name] = len(matches)

    return results


def main():
    transcripts = sorted(TRANSCRIPT_DIR.glob("*.txt"))
    if not transcripts:
        print("No transcripts found. Run transcribe.py first.")
        return

    print(f"Analyzing {len(transcripts)} transcripts...\n")

    all_results = []
    total_markers = Counter()
    total_patterns = Counter()
    all_english = Counter()
    total_words = 0

    for t_file in transcripts:
        text = t_file.read_text()
        result = analyze_transcript(text)
        result["episode"] = t_file.stem

        all_results.append(result)
        total_words += result["word_count"]

        for marker, data in result["markers"].items():
            total_markers[marker] += data["count"]

        for pattern, count in result["patterns"].items():
            total_patterns[pattern] += count

        for term in result["english_terms"]:
            all_english[term] += 1

    # Aggregate analysis
    analysis = {
        "summary": {
            "episodes_analyzed": len(transcripts),
            "total_words": total_words,
            "avg_words_per_episode": total_words // len(transcripts) if transcripts else 0,
        },
        "marker_frequency": {
            marker: {
                "total_count": count,
                "per_episode": round(count / len(transcripts), 1),
                "description": MARKERS.get(marker, ""),
            }
            for marker, count in total_markers.most_common()
        },
        "pattern_frequency": {
            pattern: {
                "total_count": count,
                "per_episode": round(count / len(transcripts), 1),
            }
            for pattern, count in total_patterns.most_common()
        },
        "top_english_terms": [
            {"term": term, "episodes": count}
            for term, count in all_english.most_common(50)
        ],
        "per_episode": all_results,
    }

    # Print summary
    print(f"Episodes: {len(transcripts)}")
    print(f"Total words: {total_words:,}")
    print(f"Avg words/episode: {total_words // len(transcripts):,}\n")

    print("Top Hebrew markers (across all episodes):")
    for marker, count in total_markers.most_common(15):
        per_ep = round(count / len(transcripts), 1)
        print(f"  {marker} ({MARKERS.get(marker, '')}): {count} total, {per_ep}/episode")

    print(f"\nTop English terms embedded in Hebrew:")
    for term, count in all_english.most_common(20):
        print(f"  {term}: in {count} episodes")

    print(f"\nRhetorical patterns:")
    for pattern, count in total_patterns.most_common():
        per_ep = round(count / len(transcripts), 1)
        print(f"  {pattern}: {count} total, {per_ep}/episode")

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\nFull analysis saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
