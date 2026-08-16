#!/usr/bin/env bash
set -euo pipefail

WEEK2="fact_data_modeling/week02_devices_events"
REM="$WEEK2/remediation"
BASELINE="week02-graded-a"

PASS_COUNT=0
FAIL_COUNT=0

pass() {
    printf 'PASS: %s\n' "$1"
    ((PASS_COUNT+=1))
}

fail() {
    printf 'FAIL: %s\n' "$1"
    ((FAIL_COUNT+=1))
}

echo "======================================================================"
echo " WEEK 2 FACT DATA MODELING REMEDIATION VALIDATION"
echo "======================================================================"

echo
echo "===== BASELINE ====="

if git rev-parse "$BASELINE" >/dev/null 2>&1; then
    pass "baseline tag exists: $BASELINE"
else
    fail "baseline tag missing: $BASELINE"
fi

if git diff --quiet "$BASELINE" -- "$WEEK2/submission"; then
    pass "original B-grade submission remains unchanged"
else
    fail "original B-grade submission differs from baseline"
fi

echo
echo "===== REMEDIATION FILE COUNT ====="

QUERY_COUNT="$(
    find "$REM/sql" \
      -maxdepth 1 \
      -type f \
      -name 'query_*.sql' \
      | wc -l \
      | tr -d ' '
)"

if [[ "$QUERY_COUNT" == "8" ]]; then
    pass "exactly eight remediation SQL files exist"
else
    fail "expected 8 remediation SQL files; found $QUERY_COUNT"
fi

echo
echo "===== QUERY 4 ====="

Q4="$REM/sql/query_4.sql"

if grep -qF 'AS gs(valid_date)' "$Q4"; then
    pass "Query 4 explicitly aliases generate_series column"
else
    fail "Query 4 generate_series column alias missing"
fi

if grep -vE '^[[:space:]]*--' "$Q4" | grep -qF '1::BIGINT'; then
    pass "Query 4 uses BIGINT bit-shift implementation"
else
    fail "Query 4 BIGINT bit-shift implementation missing"
fi

if grep -vE '^[[:space:]]*--' "$Q4" | grep -qF 'BIT(32)'; then
    fail "Query 4 still returns BIT(32)"
else
    pass "Query 4 executable SQL does not return BIT(32)"
fi

if grep -qF 'WITH parameters AS' "$Q4"; then
    pass "Query 4 snapshot date is parameterized"
else
    fail "Query 4 parameters CTE missing"
fi

echo
echo "===== SOURCE TABLE NAME EVIDENCE ====="

HOMEWORK_FILE="upstream/data-engineer-handbook/intermediate-bootcamp/materials/2-fact-data-modeling/homework/homework.md"

if grep -qF '`devices` and `events`' "$HOMEWORK_FILE"; then
    pass "upstream Week 2 homework explicitly uses devices and events"
else
    fail "could not verify devices/events naming in upstream homework"
fi

if grep -qF 'deduplicate `game_details`' "$HOMEWORK_FILE"; then
    pass "upstream Week 2 homework explicitly uses game_details"
else
    fail "could not verify game_details naming in upstream homework"
fi

for table_file in \
    upstream/data-engineer-handbook/intermediate-bootcamp/materials/2-fact-data-modeling/tables/game_details.sql \
    upstream/data-engineer-handbook/intermediate-bootcamp/materials/2-fact-data-modeling/tables/events.sql \
    upstream/data-engineer-handbook/intermediate-bootcamp/materials/2-fact-data-modeling/tables/devices.sql
do
    if [[ -f "$table_file" ]]; then
        pass "upstream table definition exists: $(basename "$table_file")"
    else
        fail "missing upstream table definition: $table_file"
    fi
done

echo
echo "===== GIT DIFF CHECK ====="

if git diff --check; then
    pass "git diff --check"
else
    fail "git diff --check"
fi

echo
echo "===== SUMMARY ====="
printf 'PASS=%d\n' "$PASS_COUNT"
printf 'FAIL=%d\n' "$FAIL_COUNT"

if (( FAIL_COUNT > 0 )); then
    exit 1
fi

echo
echo "Week 2 remediation validation completed successfully."
