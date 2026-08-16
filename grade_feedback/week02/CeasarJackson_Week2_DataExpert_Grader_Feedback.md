# DataExpert.io Community Academy — Week 2 Fact Data Modeling Grader Feedback

## Student
**Name:** Ceasar Jackson

## Final Grade
**B**

## Overall Assessment
Thanks for the thorough submission. You completed all eight prompts with clear, well-linted SQL and thoughtful comments explaining grain, behavior, and edge cases. Overall, your modeling choices are sound and consistent, and your incremental patterns are correct.

# Global Strengths
- Clear headers and rationale in every file; consistent casing and formatting.
- Correct grains defined and enforced with primary keys.
- Incremental logic covers carry-forward, new entities, and no-activity days.
- Good use of array operations and `GROUP BY` to prevent double-appending of the same day.
- Sensible pre-deduplication of devices to avoid join fan-out.

# Global Opportunities
- **Table naming alignment:** Prompt references `nba_game_details` and `web_events`; submission uses `game_details` and `events`. Verify against the actual bootcamp schema.
- Parameterize `current_date` / `snapshot_date` for reusable, idempotent jobs.
- Consider renaming `date` to `snapshot_date` in cumulative tables.
- Consider `ON CONFLICT DO UPDATE` for cumulative inserts where reruns should be safe.

# Query 1 — De-duplication
## Strengths
- Correct partitioning by `(game_id, team_id, player_id)`.
- Clean expected-column selection, including quoted `"TO"`.
- Readable `ROW_NUMBER()` approach.

## Improvements
- Verify `game_details` versus required `nba_game_details`.
- Add a deterministic tie-breaker when duplicate rows differ. Ordering only by partition keys can select an arbitrary duplicate.
- PostgreSQL `DISTINCT ON` could also simplify the pattern.

# Query 2 — user_devices_cumulated DDL
## Strengths
- Correct grain: user + browser + snapshot date.
- `DATE[]` is an appropriate activity-date representation.
- Primary key enforces the intended grain.

## Improvements
- Prefer `snapshot_date` over `date`.
- Optionally prevent unexpected NULL activity arrays with an appropriate constraint/default.

# Query 3 — user_devices_cumulated Incremental Population
## Strengths
- Deduplicates `devices`, preventing join fan-out.
- `FULL OUTER JOIN` handles carry-forward and new combinations.
- Today is grouped to one `(user, browser)` row, preventing duplicate date appends.

## Improvements
- Verify `events` versus `web_events`.
- Consider `ON CONFLICT` upsert behavior for idempotent reruns.

# Query 4 — User Devices Activity Integer Datelist
## Strengths
- Correct conceptual 32-day window.
- Correct bit direction, with current date at the highest-order bit.
- Avoiding array `UNNEST` is acceptable.

## Important Functional Fix 1 — generate_series alias
The grader identified an aliasing problem. Prefer an explicit column alias:

```sql
CROSS JOIN LATERAL generate_series(
    DATE '2023-01-31' - INTERVAL '31 day',
    DATE '2023-01-31',
    INTERVAL '1 day'
) AS gs(valid_date)
```

Then use `gs.valid_date`.

## Important Functional Fix 2 — Integer type
The requirement calls for a base-2 **integer representation**. The submitted `BIT(32)` result should instead be a `BIGINT`, for example:

```sql
SUM(
    CASE
        WHEN is_active
            THEN (1::BIGINT << (31 - days_since))
        ELSE 0::BIGINT
    END
) AS datelist_int
```

## Additional improvement
Parameterize the snapshot date so the 32-day calculation is reusable.

# Query 5 — hosts_cumulated DDL
## Strengths
- Correct grain and primary key.
- `DATE[]` fits the requirement.

## Improvement
Prefer `snapshot_date` to the generic `date` column name.

# Query 6 — hosts_cumulated Incremental
## Strengths
- Correct carry-forward and new-host handling.
- Correct current-date append behavior.
- `FULL OUTER JOIN` covers expected states.

## Improvements
- Verify `events` versus `web_events`.
- Consider `ON CONFLICT` handling for idempotent reruns.

# Query 7 — host_activity_reduced DDL
## Strengths
- Correct `(month, host)` grain and primary key.
- `hit_array` and `unique_visitors` use required `BIGINT[]`.
- Array semantics are clearly documented.

# Query 8 — host_activity_reduced Incremental
## Strengths
- Excellent day alignment and zero-filling.
- `ARRAY_FILL` correctly creates leading zeros for hosts first appearing after day one.
- `FULL OUTER JOIN` preserves inactive-but-known hosts with zero appends.
- `ON CONFLICT` makes this fact-table process idempotent.
- Date parameterization is already used here.

## Improvement
Verify `events` versus `web_events`.

# Schema and Environment Confirmation
The grader requested confirmation of:
- `nba_game_details` versus `game_details`
- `web_events` versus `events`
- DDL/columns for the game-details, web-events, and devices sources
- Target warehouse/SQL dialect
- Intended snapshot-date and rerun policy

# Verdict
All eight prompts were implemented with strong clarity and largely correct logic. The main functional issue is Query 4's aliasing/type implementation, plus possible source-table naming misalignment.

**Final Grade: B**

# Remediation Priorities
1. Correct Query 4 `generate_series` aliasing.
2. Change Query 4 output from `BIT(32)` to `BIGINT`.
3. Verify/align `nba_game_details` versus `game_details`.
4. Verify/align `web_events` versus `events`.
5. Parameterize snapshot dates consistently.
6. Add explicit rerun/idempotency handling where appropriate.
7. Re-run SQL validation and preserve evidence.
8. Build and integrity-check a fresh eight-query resubmission ZIP.
