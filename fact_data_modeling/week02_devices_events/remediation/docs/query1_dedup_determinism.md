# Query 1 — Duplicate Selection Policy

The required de-duplication grain is:

- `game_id`
- `team_id`
- `player_id`

The upstream `game_details` schema was inspected before final hardening.

A deterministic tie-breaker should only be added when the source contains a
column with meaningful ordering semantics, such as an ingestion timestamp,
source sequence, or authoritative record version.

The grader mentioned `created_at` only as an example. The remediation does
not invent such a column.

If duplicate records are otherwise identical at the source, retaining one
arbitrary physical duplicate is semantically equivalent for this assignment.
