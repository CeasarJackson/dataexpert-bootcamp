#!/usr/bin/env bash
# ==============================================================================
# File: validate_week05_pipeline_maintenance.sh
# Project: DataExpert Boot Camp
# Assignment: Week 5 — Data Pipeline Maintenance
# Author: Ceasar Jackson
#
# Purpose:
#   Perform deterministic validation of the Week 5 Data Pipeline Maintenance
#   homework before submission or archival.
#
# Usage:
#   ./data_pipeline_maintenance/week05_pipeline_maintenance/scripts/validate_week05_pipeline_maintenance.sh
#
# Exit codes:
#   0 - all validation checks passed
#   1 - one or more validation checks failed
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
README="$ROOT/README.md"
SUBMISSION="$ROOT/submission/data_pipeline_maintenance.md"

PASS_COUNT=0

pass() {
    printf 'PASS: %s\n' "$1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

echo "======================================================================"
echo " WEEK 5 DATA PIPELINE MAINTENANCE VALIDATION"
echo "======================================================================"

echo
echo "===== REQUIRED FILES ====="

[[ -s "$README" ]] \
    && pass "README exists and is non-empty" \
    || fail "README missing or empty"

[[ -s "$SUBMISSION" ]] \
    && pass "graded submission exists and is non-empty" \
    || fail "graded submission missing or empty"

echo
echo "===== STUDENT IDENTIFICATION ====="

grep -Fq "Ceasar Jackson" "$SUBMISSION" \
    && pass "student name present" \
    || fail "student name missing"

grep -Fq "knucknuclear" "$SUBMISSION" \
    && pass "Discord username present" \
    || fail "Discord username missing"

echo
echo "===== REQUIRED PIPELINES ====="

for pipeline in \
    "Unit-Level Profit" \
    "Aggregate Profit" \
    "Aggregate Growth" \
    "Daily Growth" \
    "Aggregate Engagement"
do
    grep -Fq "$pipeline" "$SUBMISSION" \
        && pass "$pipeline" \
        || fail "$pipeline missing"
done

echo
echo "===== REQUIRED ASSIGNMENT COMPONENTS ====="

for component in \
    "Pipeline Inventory and Ownership" \
    "Primary Owner" \
    "Secondary Owner" \
    "Fair On-Call Schedule" \
    "Holiday and Time-Off Policy" \
    "Aggregate Profit Pipeline Runbook" \
    "Aggregate Growth Pipeline Runbook" \
    "Aggregate Engagement Pipeline Runbook" \
    "Potential Problems Across All Five Pipelines"
do
    grep -Fq "$component" "$SUBMISSION" \
        && pass "$component" \
        || fail "$component missing"
done

echo
echo "===== CONTENT HYGIENE ====="

if grep -nE '^(heredoc>|quote>|EOF$)' "$README" "$SUBMISSION"; then
    fail "terminal/heredoc artifact detected"
else
    pass "no terminal/heredoc artifacts"
fi

if grep -nE '[[:blank:]]+$' "$README" "$SUBMISSION"; then
    fail "trailing whitespace detected"
else
    pass "no trailing whitespace"
fi

echo
echo "===== FILE STATISTICS ====="

wc -l -w -c "$README" "$SUBMISSION"

echo
echo "===== HASHES ====="

if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$README" "$SUBMISSION"
else
    fail "shasum command unavailable"
fi

echo
echo "======================================================================"
echo " VALIDATION COMPLETE — ${PASS_COUNT} CHECKS PASSED"
echo "======================================================================"
