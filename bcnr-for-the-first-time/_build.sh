#!/bin/bash
set -e
cd "$(dirname "$0")"
BODY="$1"; STEM="${2:-song}"
cat _eng.txt "$BODY" > "$STEM.py"
python3 "$STEM.py" 2>&1 | tail -6
# engine writes .wav -> encode .mp3, drop wavs
for w in "$STEM.wav" "$STEM-instrumental.wav"; do
  [ -f "$w" ] || continue
  ffmpeg -y -loglevel error -i "$w" -codec:a libmp3lame -b:a 192k "${w%.wav}.mp3"
  rm "$w"
done
