"""Transcribe podcast episodes using local Whisper."""
import json
import sys
from pathlib import Path

import whisper

AUDIO_DIR = Path(__file__).parent / "audio"
TRANSCRIPT_DIR = Path(__file__).parent / "transcripts"
MANIFEST_FILE = Path(__file__).parent / "manifest.json"

# Use "small" model for Hebrew - good balance of speed vs accuracy
# Options: tiny, base, small, medium, large
MODEL_SIZE = "small"


def main():
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    # Optionally transcribe a specific episode
    target = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"Loading Whisper model: {MODEL_SIZE}...")
    model = whisper.load_model(MODEL_SIZE)
    print("Model loaded.\n")

    audio_files = sorted(AUDIO_DIR.glob("*.mp3"))
    if target:
        audio_files = [f for f in audio_files if target in f.stem]

    existing = {f.stem for f in TRANSCRIPT_DIR.glob("*.json")}

    for i, audio_file in enumerate(audio_files):
        name = audio_file.stem
        if name in existing:
            print(f"[{i+1}/{len(audio_files)}] SKIP (already transcribed): {name}")
            continue

        print(f"[{i+1}/{len(audio_files)}] Transcribing: {name}...")
        try:
            result = model.transcribe(
                str(audio_file),
                language="he",
                task="transcribe",
                verbose=False,
            )

            # Save full result
            transcript_file = TRANSCRIPT_DIR / f"{name}.json"
            with open(transcript_file, "w") as f:
                json.dump({
                    "text": result["text"],
                    "segments": [
                        {
                            "start": s["start"],
                            "end": s["end"],
                            "text": s["text"],
                        }
                        for s in result["segments"]
                    ],
                    "language": result.get("language", "he"),
                }, f, indent=2, ensure_ascii=False)

            # Also save plain text
            txt_file = TRANSCRIPT_DIR / f"{name}.txt"
            with open(txt_file, "w") as f:
                f.write(result["text"])

            duration_min = result["segments"][-1]["end"] / 60 if result["segments"] else 0
            print(f"  Done: {len(result['segments'])} segments, ~{duration_min:.0f} min")

        except Exception as e:
            print(f"  FAILED: {e}")

    print(f"\nTranscription complete. Files in: {TRANSCRIPT_DIR}")


if __name__ == "__main__":
    main()
