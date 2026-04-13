#!/bin/bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.nadia.dutchword.plist"
PLIST_SRC="$APP_DIR/$PLIST_NAME"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Dutch Word of the Day — Installer ==="
echo ""

# 1. Verify files exist
for f in dutch_word.py vocabulary.json "$PLIST_NAME"; do
    if [ ! -f "$APP_DIR/$f" ]; then
        echo "ERROR: Missing file: $APP_DIR/$f"
        exit 1
    fi
done
echo "[ok] All required files found."

# 2. Make script executable
chmod +x "$APP_DIR/dutch_word.py"
echo "[ok] dutch_word.py is now executable."

# 3. Unload old plist if already installed
if launchctl list 2>/dev/null | grep -q "com.nadia.dutchword"; then
    echo "[..] Unloading existing schedule..."
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

# 4. Copy plist to LaunchAgents
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"
echo "[ok] Plist copied to $PLIST_DST"

# 5. Load the schedule
launchctl load "$PLIST_DST"
echo "[ok] Daily schedule loaded (every day at 9:00 AM)."

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Test it now with:  python3 \"$APP_DIR/dutch_word.py\""
echo "Or trigger via:    launchctl start com.nadia.dutchword"
echo ""
echo "To uninstall later:"
echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
echo "  rm ~/Library/LaunchAgents/$PLIST_NAME"
