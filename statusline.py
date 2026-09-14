#!/usr/bin/env python3
"""Claude Code status line: multi-line w/ model, context, 5h + 7d quota bars."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GREEN = "\033[92m"
DIM_GRAY = "\033[90m"
DIM = "\033[2m"
RESET = "\033[0m"

SEP = f" {DIM_GRAY}|{RESET} "


def fmt_tokens(n):
    if n is None:
        return "?"
    n = float(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}m"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(int(n))


def fmt_context_total(n):
    if n is None:
        return "?"
    n = float(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}m"
    if n >= 1_000:
        return f"{int(round(n / 1_000))}k"
    return str(int(n))


def bar(pct, width=10):
    pct = max(0.0, min(100.0, float(pct or 0)))
    filled = int(pct / 100 * width + 0.5)
    return (
        f"{GREEN}" + "●" * filled + f"{RESET}"
        f"{DIM_GRAY}" + "○" * (width - filled) + f"{RESET}"
    )


def fmt_reset(epoch):
    """Return (short_time_or_day_time, duration_str_or_None)."""
    if not epoch:
        return None, None
    now = time.time()
    dt = datetime.fromtimestamp(epoch)
    now_dt = datetime.fromtimestamp(now)
    h = dt.hour % 12 or 12
    ap = "am" if dt.hour < 12 else "pm"
    short_time = f"{h}:{dt.minute:02d}{ap}"
    if dt.date() == now_dt.date():
        delta = int(epoch - now)
        if delta <= 0:
            return short_time, "now"
        hrs = delta // 3600
        mins = (delta % 3600) // 60
        dur = f"{hrs}h{mins:02d}m" if hrs else f"{mins}m"
        return short_time, dur
    return f"{dt.strftime('%a')}, {short_time}", None


def to_native_path(p):
    if not p:
        return p
    if sys.platform.startswith("win") and len(p) >= 3 and p[0] == "/" and p[2] == "/":
        return p[1].upper() + ":\\" + p[3:].replace("/", "\\")
    return p


def get_branch(cwd):
    cwd = to_native_path(cwd)
    if cwd and not os.path.isdir(cwd):
        return None
    try:
        r = subprocess.run(
            ["git", "--no-optional-locks", "symbolic-ref", "--short", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=1,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        r = subprocess.run(
            ["git", "--no-optional-locks", "rev-parse", "--short", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=1,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        return None
    return None


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}


    model = (data.get("model") or {}).get("display_name") or "Claude"

    ctx = data.get("context_window") or {}
    ctx_size = ctx.get("context_window_size")
    ctx_used_pct = ctx.get("used_percentage")
    used = remaining = remaining_pct = None
    if ctx_size and ctx_used_pct is not None:
        used = ctx_size * (ctx_used_pct / 100.0)
        remaining = ctx_size - used
        remaining_pct = 100 - ctx_used_pct

    rl = data.get("rate_limits") or {}
    fh = rl.get("five_hour") or {}
    sd = rl.get("seven_day") or {}
    fh_pct = fh.get("used_percentage")
    sd_pct = sd.get("used_percentage")
    fh_reset = fh.get("resets_at")
    sd_reset = sd.get("resets_at")

    ws = data.get("workspace") or {}
    cwd = ws.get("current_dir") or data.get("cwd") or os.getcwd()
    branch = get_branch(cwd)

    # Line 1: model + context usage
    l1 = []
    if ctx_size and "context" not in model.lower() and "(" not in model:
        l1.append(f"{GREEN}{model} ({fmt_context_total(ctx_size)} context){RESET}")
    else:
        l1.append(f"{GREEN}{model}{RESET}")
    if used is not None:
        l1.append(
            f"{GREEN}{fmt_tokens(used)} / {fmt_context_total(ctx_size)} "
            f"({int(round(ctx_used_pct))}% used){RESET}"
        )
        l1.append(
            f"{GREEN}{fmt_tokens(remaining)} {int(round(remaining_pct))}% free{RESET}"
        )

    # Line 2: quota bars + branch
    l2 = []
    if fh_pct is not None:
        l2.append(
            f"{DIM_GRAY}current:{RESET} {bar(fh_pct)} "
            f"{DIM_GRAY}{int(round(fh_pct))}%{RESET}"
        )
    if sd_pct is not None:
        l2.append(
            f"{DIM_GRAY}weekly:{RESET} {bar(sd_pct)} "
            f"{DIM_GRAY}{int(round(sd_pct))}%{RESET}"
        )
    if branch:
        l2.append(f"{GREEN}{branch}{RESET}")

    # Line 3: reset times
    l3 = []
    if fh_reset:
        t, dur = fmt_reset(fh_reset)
        if t:
            l3.append(f"{DIM_GRAY}resets {t}" + (f" ({dur})" if dur else "") + RESET)
    if sd_reset:
        t, dur = fmt_reset(sd_reset)
        if t:
            suffix = f" ({dur})" if dur and dur != "now" else ""
            l3.append(f"{DIM_GRAY}resets {t}{suffix}{RESET}")

    lines = [SEP.join(l1)]
    if l2:
        lines.append(SEP.join(l2))
    if l3:
        lines.append(SEP.join(l3))
    sys.stdout.write("\n".join(lines))


if __name__ == "__main__":
    main()
