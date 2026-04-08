#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$PROJECT_ROOT/firmware"
DEST="/Volumes/CIRCUITPY"

SPLASH_A="$PROJECT_ROOT/midimal_splash_a.bmp"
SPLASH_B="$PROJECT_ROOT/midimal_splash_b.bmp"

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

  if [ -f "$SPLASH_A" ]; then
    cp "$SPLASH_A" "$DEST/"
  fi

  if [ -f "$SPLASH_B" ]; then
    cp "$SPLASH_B" "$DEST/"
  fi

  sync
  echo "Synced at $(date '+%H:%M:%S')"
}

echo "Watching $SRC and splash BMPs"
echo "Syncing to $DEST"

sync_files

/opt/homebrew/bin/fswatch -o \
  "$SRC" \
  "$SPLASH_A" \
  "$SPLASH_B" | while read; do
    sync_files
done