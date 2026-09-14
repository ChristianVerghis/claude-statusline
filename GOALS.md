# Goals

- Keep the status line fast (< 50 ms) and dependency-free (stdlib Python only).
- Show context, quota, and reset info at a glance; never crash on missing fields.
- Stay in sync with whatever fields Claude Code adds to the status line payload.

## Ideas

- Colour the quota bars amber/red past thresholds.
- Show session cost (`cost.total_cost_usd`) when present.
- Warm/cold prompt-cache indicator from `prompt_cache`.
