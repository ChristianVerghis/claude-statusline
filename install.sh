#!/bin/bash
# Install the status line into ~/.claude and register it in settings.json.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DST="$HOME/.claude/statusline-command.py"
SETTINGS="$HOME/.claude/settings.json"

command -v python3 >/dev/null || { echo "python3 not found on PATH" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq not found on PATH (brew install jq)" >&2; exit 1; }

mkdir -p "$HOME/.claude"
cp "$HERE/statusline.py" "$DST"
chmod +x "$DST"

[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.bak"
jq '.statusLine = {"type":"command","command":"python3 ~/.claude/statusline-command.py"}' "$SETTINGS" > "$SETTINGS.tmp"
mv "$SETTINGS.tmp" "$SETTINGS"

echo "Installed $DST"
echo "settings.json updated (backup at $SETTINGS.bak). Restart Claude Code or run /statusline to reload."
