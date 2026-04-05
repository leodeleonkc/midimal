#!/bin/bash
set -e

SRC="$(cd "$(dirname "$0")/firmware" && pwd)"
DEST="/Volumes/CIRCUITPY"

if [ ! -d "$DEST" ]; then
  echo "CIRCUITPY not found at $DEST"
  exit 1
fi

sync_files() {
  rsync -a --delete \
    --exclude ".DS_Store" \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    --exclude "._*" \
    --exclude ".Trashes" \
    --exclude ".Spotlight-V100" \
    "$SRC"/ "$DEST"/
  echo "Synced at $(date '+%H:%M:%S')"
}

echo "Watching $SRC"
echo "Syncing to $DEST"

sync_files

/opt/homebrew/bin/fswatch -o "$SRC" | while read; do  sync_files

done