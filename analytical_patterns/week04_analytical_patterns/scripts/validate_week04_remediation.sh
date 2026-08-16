#!/usr/bin/env bash

set -euo pipefail

BASELINE_TAG="week04-graded-a"
GRADED_DIR="homework/knucknuclear"
ROOT="analytical_patterns/week04_analytical_patterns"
REMEDIATION_DIR="${ROOT}/remediation"

PASS_COUNT=0
FAIL_COUNT=0

pass() {
    printf 'PASS: %s\n' "$1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

echo "======================================================================"
echo " WEEK 4 GRADE REMEDIATION VALIDATION"
echo "======================================================================"

echo
echo "===== BASELINE PRESERVATION ====="

if git diff --quiet "$BASELINE_TAG" -- "$GRADED_DIR"; then
    pass "original B-grade submission matches $BASELINE_TAG"
else
    fail "original B-grade submission differs from $BASELINE_TAG"
fi

echo
echo "===== ORIGINAL REQUIRED OUTPUTS ====="

original_files=(
    "${GRADED_DIR}/01_player_state_change_tracking.sql"
    "${GRADED_DIR}/02_grouping_sets_game_details.sql"
    "${GRADED_DIR}/03_window_functions_game_details.sql"
)

for file in "${original_files[@]}"; do
    if [[ -f "$file" ]]; then
        pass "original SQL exists: $(basename "$file")"
    else
        fail "original SQL missing: $(basename "$file")"
    fi
done

echo
echo "===== REMEDIATION OUTPUTS ====="

remediation_files=(
    "${REMEDIATION_DIR}/query_3_most_points_single_team.sql"
    "${REMEDIATION_DIR}/query_4_most_points_single_season.sql"
    "${REMEDIATION_DIR}/query_5_team_most_wins.sql"
)

for file in "${remediation_files[@]}"; do
    if [[ -f "$file" ]]; then
        pass "remediation SQL exists: $(basename "$file")"
    else
        fail "remediation SQL missing: $(basename "$file")"
    fi
done

echo
echo "===== QUERY 3 SEMANTICS ====="

q3="${REMEDIATION_DIR}/query_3_most_points_single_team.sql"

if grep -Fq "WHERE aggregation_level = 'player_team'" "$q3"; then
    pass "Query 3 filters player_team"
else
    fail "Query 3 missing player_team filter"
fi

if grep -Fq "total_points DESC" "$q3"; then
    pass "Query 3 orders by total_points DESC"
else
    fail "Query 3 missing total_points DESC ordering"
fi

echo
echo "===== QUERY 4 SEMANTICS ====="

q4="${REMEDIATION_DIR}/query_4_most_points_single_season.sql"

if grep -Fq "WHERE aggregation_level = 'player_season'" "$q4"; then
    pass "Query 4 filters player_season"
else
    fail "Query 4 missing player_season filter"
fi

if grep -Fq "total_points DESC" "$q4"; then
    pass "Query 4 orders by total_points DESC"
else
    fail "Query 4 missing total_points DESC ordering"
fi

echo
echo "===== QUERY 5 SEMANTICS ====="

q5="${REMEDIATION_DIR}/query_5_team_most_wins.sql"

if grep -Fq "WHERE aggregation_level = 'team'" "$q5"; then
    pass "Query 5 filters team"
else
    fail "Query 5 missing team filter"
fi

if grep -Fq "team_wins DESC" "$q5"; then
    pass "Query 5 orders by team_wins DESC"
else
    fail "Query 5 missing team_wins DESC ordering"
fi

echo
echo "===== QUERY 6 SEMANTICS ====="

q6="${GRADED_DIR}/03_window_functions_game_details.sql"

if grep -Fq "ROWS BETWEEN 89 PRECEDING AND CURRENT ROW" "$q6"; then
    pass "Query 6 uses complete 90-row window definition"
else
    fail "Query 6 missing 90-game window frame"
fi

if grep -Fq "WHERE team_game_number >= 90" "$q6"; then
    pass "Query 6 filters incomplete windows"
else
    fail "Query 6 missing complete-window filter"
fi

echo
echo "===== QUERY 7 SEMANTICS ====="

if grep -Fq "WHEN scored_over_10 = 0 THEN 1" "$q6"; then
    pass "Query 7 contains streak-break grouping logic"
else
    fail "Query 7 missing streak-break grouping logic"
fi

if grep -Fq "consecutive_games_over_10_points" "$q6"; then
    pass "Query 7 returns streak length"
else
    fail "Query 7 missing streak-length output"
fi

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
echo "Week 4 remediation validation completed successfully."
