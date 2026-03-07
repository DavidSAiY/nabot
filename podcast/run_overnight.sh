#!/bin/bash
# Overnight pipeline: download → transcribe → delete (per episode), then analyze
# Run with: nohup bash podcast/run_overnight.sh > podcast/overnight.log 2>&1 &

cd "$(dirname "$0")/.."

echo "=== PODCAST VOICE DNA PIPELINE (last 50 episodes) ==="
echo "Started: $(date)"
echo ""

# Run the combined pipeline
python3 -u podcast/pipeline.py

echo ""
echo "=== PIPELINE COMPLETE ==="
echo "Finished: $(date)"
