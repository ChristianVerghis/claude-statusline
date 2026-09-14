# claude-statusline

A three-line status line for [Claude Code](https://claude.com/claude-code) showing the things you actually glance at mid-session: how much context is left, how close you are to the 5-hour and weekly rate limits, and when they reset.

```
Fable 5.1 (1.0m context) | 200.0k / 1.0m (20% used) | 800.0k 80% free
current: ●●○○○○○○○○ 18% | weekly: ●○○○○○○○○○ 8% | main
resets 5:50pm (1h29m) | resets Tue, 8:00am
```

- **Line 1** model, context window size, tokens used and free.
- **Line 2** 5-hour ("current") and 7-day ("weekly") quota bars, plus the git branch of the current directory.
- **Line 3** reset times. Same-day resets show a countdown; later ones show the weekday.

Segments are dropped when Claude Code doesn't send the data (for example, rate limits on API-key billing), so it never breaks.

## Install

Requires `python3` and `jq`.

```bash
./install.sh
```

This copies `statusline.py` to `~/.claude/statusline-command.py` and sets `statusLine` in `~/.claude/settings.json` (a backup is written to `settings.json.bak`). Restart Claude Code or run `/statusline` to pick it up.

Manual equivalent:

```json
"statusLine": { "type": "command", "command": "python3 ~/.claude/statusline-command.py" }
```

## Test

```bash
./test.sh
```

Renders the fixture payload in `fixtures/sample.json`, an empty payload, and a synthetic one with reset times relative to now.

## How it works

Claude Code pipes a JSON document to the status line command on every refresh. The script reads `model.display_name`, `context_window`, `rate_limits.five_hour`, `rate_limits.seven_day`, and `workspace.current_dir`, then runs `git symbolic-ref --short HEAD` (falling back to a short SHA) with `--no-optional-locks` so it never contends with your own git commands. No network, no files written.

## Credits

Based on a script shared by a colleague, Bernardo Xavier. Windows shims removed and the per-refresh debug dump stripped.
