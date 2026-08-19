#!/usr/bin/env bash

set -euo pipefail

WEEK9="kpis_and_experimentation/week09_kpis_experimentation"
SUBMISSION="$WEEK9/submission/CeasarJackson_KPIs_and_Experimentation.md"
RESULTS="$WEEK9/validation/results"
LOGS="$WEEK9/validation/logs"

mkdir -p "$RESULTS" "$LOGS"

TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
LOG_FILE="$LOGS/week09_validation_${TIMESTAMP}.log"

exec > >(tee "$LOG_FILE") 2>&1

pass() {
    printf 'PASS: %s\n' "$1"
}

fail() {
    printf 'FAIL: %s\n' "$1"
    exit 1
}

echo "======================================================================"
echo " WEEK 09 — KPIs AND EXPERIMENTATION VALIDATION"
echo "======================================================================"

echo
echo "===== BRANCH ====="

EXPECTED_BRANCH="feature/week09-kpis-experimentation"
CURRENT_BRANCH="$(git branch --show-current)"

[[ "$CURRENT_BRANCH" == "$EXPECTED_BRANCH" ]] \
    && pass "correct feature branch" \
    || fail "expected $EXPECTED_BRANCH; found $CURRENT_BRANCH"

echo
echo "===== REQUIRED FILES ====="

[[ -s "$WEEK9/README.md" ]] \
    && pass "README exists and is non-empty" \
    || fail "README missing or empty"

[[ -s "$SUBMISSION" ]] \
    && pass "submission exists and is non-empty" \
    || fail "submission missing or empty"

echo
echo "===== PRODUCT AND USER JOURNEY ====="

grep -qi 'LinkedIn' "$SUBMISSION" \
    && pass "LinkedIn product selection present" \
    || fail "LinkedIn product selection missing"

grep -qi 'My LinkedIn User Journey' "$SUBMISSION" \
    && pass "user journey present" \
    || fail "user journey missing"

echo
echo "===== THREE EXPERIMENTS ====="

for n in 1 2 3; do
    grep -q "Experiment $n" "$SUBMISSION" \
        && pass "Experiment $n present" \
        || fail "Experiment $n missing"
done

echo
echo "===== REQUIRED EXPERIMENT COMPONENTS ====="

TEST_CELLS="$(grep -ic 'Test-Cell Allocation' "$SUBMISSION" || true)"
CONDITIONS="$(grep -ic 'Conditions Being Tested' "$SUBMISSION" || true)"
HYPOTHESES="$(grep -ic '^## .*Hypothesis' "$SUBMISSION" || true)"
LEADING="$(grep -ic '^## .*Leading Metrics' "$SUBMISSION" || true)"
LAGGING="$(grep -ic '^## .*Lagging Metrics' "$SUBMISSION" || true)"
GUARDRAILS="$(grep -ic '^## .*Guardrail Metrics' "$SUBMISSION" || true)"

[[ "$TEST_CELLS" -eq 3 ]] \
    && pass "3 test-cell allocation sections" \
    || fail "expected 3 test-cell sections; found $TEST_CELLS"

[[ "$CONDITIONS" -eq 3 ]] \
    && pass "3 tested-condition sections" \
    || fail "expected 3 condition sections; found $CONDITIONS"

[[ "$HYPOTHESES" -eq 3 ]] \
    && pass "3 hypothesis sections" \
    || fail "expected 3 hypotheses; found $HYPOTHESES"

[[ "$LEADING" -eq 3 ]] \
    && pass "3 leading-metric sections" \
    || fail "expected 3 leading-metric sections; found $LEADING"

[[ "$LAGGING" -eq 3 ]] \
    && pass "3 lagging-metric sections" \
    || fail "expected 3 lagging-metric sections; found $LAGGING"

[[ "$GUARDRAILS" -eq 3 ]] \
    && pass "3 guardrail-metric sections" \
    || fail "expected 3 guardrail sections; found $GUARDRAILS"

echo
echo "===== CONTENT DEPTH ====="

LINES="$(wc -l < "$SUBMISSION" | tr -d ' ')"
WORDS="$(wc -w < "$SUBMISSION" | tr -d ' ')"
HEADINGS="$(grep -c '^#' "$SUBMISSION" || true)"

[[ "$LINES" -ge 200 ]] \
    && pass "substantive line count: $LINES" \
    || fail "submission too short: $LINES lines"

[[ "$WORDS" -ge 1500 ]] \
    && pass "substantive word count: $WORDS" \
    || fail "submission too short: $WORDS words"

[[ "$HEADINGS" -ge 20 ]] \
    && pass "substantive heading count: $HEADINGS" \
    || fail "insufficient heading structure: $HEADINGS"

echo
echo "===== TEST-CELL VALUES ====="

grep -Fq '| Control | 50%' "$SUBMISSION" \
    && pass "50% control allocation present" \
    || fail "50% control allocation missing"

grep -Fq '| Treatment | 50%' "$SUBMISSION" \
    && pass "50% treatment allocation present" \
    || fail "50% treatment allocation missing"

grep -Fq '| Control | 40%' "$SUBMISSION" \
    && pass "40% three-cell control allocation present" \
    || fail "40% control allocation missing"

grep -Fq '| Treatment A | 30%' "$SUBMISSION" \
    && pass "Treatment A 30% allocation present" \
    || fail "Treatment A allocation missing"

grep -Fq '| Treatment B | 30%' "$SUBMISSION" \
    && pass "Treatment B 30% allocation present" \
    || fail "Treatment B allocation missing"

echo
echo "===== WHITESPACE ====="

git diff --check \
    && pass "git diff --check" \
    || fail "whitespace errors detected"

echo
echo "===== SUBMISSION SHA-256 ====="

if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$SUBMISSION" \
        | tee "$RESULTS/submission_sha256.txt"
else
    sha256sum "$SUBMISSION" \
        | tee "$RESULTS/submission_sha256.txt"
fi

pass "submission SHA-256 recorded"

echo
echo "===== SUMMARY ====="
printf 'Lines:    %s\n' "$LINES"
printf 'Words:    %s\n' "$WORDS"
printf 'Headings: %s\n' "$HEADINGS"
printf 'Log:      %s\n' "$LOG_FILE"

echo
echo "======================================================================"
echo " VALIDATION PASSED"
echo "======================================================================"
