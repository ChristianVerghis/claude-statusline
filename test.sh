#!/bin/bash
# Render the status line against the fixture and against empty input.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "--- fixture ---"
python3 "$HERE/statusline.py" < "$HERE/fixtures/sample.json"; echo
echo "--- empty input ---"
echo '{}' | python3 "$HERE/statusline.py"; echo
echo "--- live-ish (resets relative to now) ---"
now=$(date +%s)
printf '{"model":{"display_name":"Fable 5.1"},"workspace":{"current_dir":"%s"},"context_window":{"context_window_size":1000000,"used_percentage":3},"rate_limits":{"five_hour":{"used_percentage":42,"resets_at":%d},"seven_day":{"used_percentage":12,"resets_at":%d}}}' "$HERE" $((now+5400)) $((now+300000)) | python3 "$HERE/statusline.py"; echo
