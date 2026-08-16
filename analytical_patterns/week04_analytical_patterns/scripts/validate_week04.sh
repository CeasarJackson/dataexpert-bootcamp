#!/usr/bin/env bash

# =============================================================================
# DataExpert Boot Camp — Week 4 Analytical Patterns Validation
#
# Author: Ceasar Jackson
#
# Purpose:
#   Validate Week 4 post-grade hardening artifacts while ensuring the graded
#   homework submission remains unchanged from the protected baseline tag.
#
# Usage:
#   ./analytical_patterns/week04_analytical_patterns/scripts/validate_week04.sh
# =============================================================================

set -euo pipefail

BASELINE_TAG="week04-graded-a"
SUBMISSION_DIR="homework/knucknuclear"
HARDENING_DIR="analytical_patterns/week04_analytical_patterns"
ZIP_NAME="CeasarJackson_Week4_Analytical_Patterns.zip"
CANONICAL_ZIP="${HARDENING_DIR}/submission/${ZIP_NAME}"

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
echo " WEEK 4 ANALYTICAL PATTERNS VALIDATION"
echo "======================================================================"

echo
echo "===== REPOSITORY ====="

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    pass "inside Git repository"
else
    fail "not inside Git repository"
fi

echo
echo "===== BASELINE TAG ====="

if git rev-parse "$BASELINE_TAG" >/dev/null 2>&1; then
    pass "baseline tag exists: $BASELINE_TAG"
else
    fail "baseline tag missing: $BASELINE_TAG"
fi

echo
echo "===== GRADED SUBMISSION FILES ====="

required_files=(
    "01_player_state_change_tracking.sql"
    "02_grouping_sets_game_details.sql"
    "03_window_functions_game_details.sql"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "${SUBMISSION_DIR}/${file}" ]]; then
        pass "graded file exists: $file"
    else
        fail "graded file missing: $file"
    fi
done

echo
echo "===== GRADED SUBMISSION PRESERVATION ====="

if git diff --quiet "$BASELINE_TAG" -- "$SUBMISSION_DIR"; then
    pass "graded Week 4 submission matches $BASELINE_TAG"
else
    fail "graded Week 4 submission differs from $BASELINE_TAG"
fi

echo
echo "===== REFERENCE SQL ====="

reference_files=(
    "01_player_state_change_tracking_reference.sql"
    "02_grouping_sets_game_details_reference.sql"
    "03_window_functions_game_details_reference.sql"
)

for file in "${reference_files[@]}"; do
    if [[ -f "${HARDENING_DIR}/sql/${file}" ]]; then
        pass "reference SQL exists: $file"
    else
        fail "reference SQL missing: $file"
    fi
done

echo
echo "===== ZIP ARTIFACT ====="

if [[ -f "$ZIP_NAME" ]]; then
    pass "working submission ZIP exists"
else
    fail "working submission ZIP missing"
fi

if [[ -f "$CANONICAL_ZIP" ]]; then
    pass "canonical submission ZIP exists"
else
    fail "canonical submission ZIP missing"
fi

if unzip -t "$ZIP_NAME" >/dev/null 2>&1; then
    pass "working submission ZIP integrity"
else
    fail "working submission ZIP integrity"
fi

if [[ -f "$ZIP_NAME" && -f "$CANONICAL_ZIP" ]]; then
    working_hash="$(shasum -a 256 "$ZIP_NAME" | awk '{print $1}')"
    canonical_hash="$(shasum -a 256 "$CANONICAL_ZIP" | awk '{print $1}')"

    if [[ "$working_hash" == "$canonical_hash" ]]; then
        pass "working and canonical ZIP hashes match"
    else
        fail "working and canonical ZIP hashes differ"
    fi
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
echo "Week 4 validation completed successfully."
