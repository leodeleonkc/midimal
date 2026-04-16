#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$PROJECT_ROOT/firmware"
DEST="/Volumes/CIRCUITPY"

SPLASH_A="$PROJECT_ROOT/midimal_splash_a.bmp"
SPLASH_B="$PROJECT_ROOT/midimal_splash_b.bmp"

FSWATCH="/opt/homebrew/bin/fswatch"

if [ ! -d "$DEST" ]; then
  echo "CIRCUITPY not found at $DEST"
  exit 1
fi

if [ ! -x "$FSWATCH" ]; then
  echo "fswatch not found at $FSWATCH"
  exit 1
fi

full_sync() {
  rsync -a --delete \
    --exclude ".DS_Store" \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    --exclude "._*" \
    --exclude ".Trashes" \
    --exclude ".Spotlight-V100" \
    "$SRC"/ "$DEST"/

  if [ -f "$SPLASH_A" ]; then
    cp -f "$SPLASH_A" "$DEST/"
  fi

  if [ -f "$SPLASH_B" ]; then
    cp -f "$SPLASH_B" "$DEST/"
  fi

  sync
  echo "Full sync at $(date '+%H:%M:%S')"
}

sync_single_file() {
  local changed_path="$1"

  if [ ! -d "$DEST" ]; then
    echo "CIRCUITPY not mounted, skipping: $changed_path"
    return
  fi

  case "$changed_path" in
    "$SPLASH_A")
      if [ -f "$SPLASH_A" ]; then
        cp -f "$SPLASH_A" "$DEST/"
        sync
        echo "Updated midimal_splash_a.bmp at $(date '+%H:%M:%S')"
      fi
      return
      ;;
    "$SPLASH_B")
      if [ -f "$SPLASH_B" ]; then
        cp -f "$SPLASH_B" "$DEST/"
        sync
        echo "Updated midimal_splash_b.bmp at $(date '+%H:%M:%S')"
      fi
      return
      ;;
  esac

  if [[ "$changed_path" == "$SRC/"* ]]; then
    local rel_path="${changed_path#$SRC/}"
    local dest_path="$DEST/$rel_path"
    local dest_dir
    dest_dir="$(dirname "$dest_path")"

    if [ -f "$changed_path" ]; then
      mkdir -p "$dest_dir"
      cp -f "$changed_path" "$dest_path"
      sync
      echo "Updated $rel_path at $(date '+%H:%M:%S')"
    else
      rm -f "$dest_path"
      sync
      echo "Removed $rel_path at $(date '+%H:%M:%S')"
    fi
  fi
}

echo "Watching $SRC and splash BMPs"
echo "Syncing to $DEST"

full_sync

"$FSWATCH" -0 \
  "$SRC" \
  "$SPLASH_A" \
  "$SPLASH_B" | while IFS= read -r -d '' changed; do
    sync_single_file "$changed"
done