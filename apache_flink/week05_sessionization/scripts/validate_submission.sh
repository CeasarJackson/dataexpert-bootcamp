#!/usr/bin/env bash

# ==============================================================================
# DataExpert Boot Camp
# Week 5 — Apache Flink Sessionization Homework
# Final Submission Validator
#
# Author:
#   Ceasar Jackson
#
# Purpose:
#   Perform deterministic, lightweight validation of the grader-facing Week 5
#   Apache Flink homework submission without starting Docker, Kafka, PostgreSQL,
#   or a Flink runtime.
#
# Validates:
#   - Required submission files
#   - Exact grader-facing file count
#   - SHA-256 checksums
#   - Python source syntax
#   - Python 3.7-compatible typing syntax
#   - Five-minute session gap
#   - PyFlink Session API usage
#   - Absence of unsupported SQL SESSION TVF
#   - Required target hosts
#   - Coordinated StatementSet execution
#   - Absence of obvious credential/environment files
#
# Usage:
#   ./apache_flink/week05_sessionization/scripts/validate_submission.sh
#
# Exit codes:
#   0 = all validation checks passed
#   1 = one or more validation checks failed
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(
    cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1
    pwd
)"

WEEK5="$(
    cd "$SCRIPT_DIR/.." >/dev/null 2>&1
    pwd
)"

SUBMISSION="$WEEK5/submission"
HOMEWORK_SCRIPT="$SUBMISSION/flink_sessionization_homework.py"
ANSWERS="$SUBMISSION/HOMEWORK_ANSWERS.md"
SUMMARY_CSV="$SUBMISSION/offline_sessionization_summary.csv"
SUMMARY_JSON="$SUBMISSION/offline_sessionization_summary.json"
CHECKSUMS="$SUBMISSION/SHA256SUMS.txt"

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

section() {
    printf '\n===== %s =====\n' "$1"
}

section "SUBMISSION FILES"

for file in \
    "$HOMEWORK_SCRIPT" \
    "$ANSWERS" \
    "$SUMMARY_CSV" \
    "$SUMMARY_JSON" \
    "$CHECKSUMS"
do
    if [[ -s "$file" ]]; then
        pass "$(basename "$file") exists and is non-empty"
    else
        fail "$(basename "$file") missing or empty"
    fi
done

section "GRADER-FACING FILE COUNT"

FILE_COUNT="$(
    find "$SUBMISSION" \
        -maxdepth 1 \
        -type f \
        | wc -l \
        | tr -d ' '
)"

printf 'SUBMISSION_FILE_COUNT=%s\n' "$FILE_COUNT"

if [[ "$FILE_COUNT" -eq 5 ]]; then
    pass "exactly five grader-facing files"
else
    fail "expected 5 grader-facing files; found $FILE_COUNT"
fi

section "CHECKSUM VERIFICATION"

if (
    cd "$SUBMISSION"
    shasum -a 256 -c SHA256SUMS.txt
); then
    pass "submission checksums verified"
else
    fail "submission checksum verification failed"
fi

section "PYTHON SOURCE"

if python3 -m py_compile "$HOMEWORK_SCRIPT"; then
    pass "submission Python syntax compiles"
else
    fail "submission Python syntax failed"
fi

find "$WEEK5" \
    -type d \
    -name '__pycache__' \
    -prune \
    -exec rm -rf {} + \
    2>/dev/null || true

if grep -Eq \
    'from typing import Final|Final\[|tuple\[[^]]+\]|list\[[^]]+\]|dict\[[^]]+\]|set\[[^]]+\]' \
    "$HOMEWORK_SCRIPT"
then
    fail "Python 3.8+/3.9+ typing syntax detected"
else
    pass "source retains Python 3.7-compatible typing"
fi

section "SESSIONIZATION"

if grep -Fq \
    "SESSION_GAP_MINUTES: int = 5" \
    "$HOMEWORK_SCRIPT"
then
    pass "five-minute session gap constant"
else
    fail "five-minute session gap constant missing"
fi

if grep -Fq \
    "from pyflink.table.window import Session" \
    "$HOMEWORK_SCRIPT"
then
    pass "PyFlink Session API imported"
else
    fail "PyFlink Session API import missing"
fi

if grep -Fq \
    ".with_gap(lit(SESSION_GAP_MINUTES).minutes)" \
    "$HOMEWORK_SCRIPT"
then
    pass "five-minute Session.with_gap() configured"
else
    fail "Session.with_gap() configuration missing"
fi

if grep -Eq \
    'SESSION[[:space:]]*\(' \
    "$HOMEWORK_SCRIPT"
then
    fail "unsupported SQL SESSION TVF detected"
else
    pass "unsupported SQL SESSION TVF absent"
fi

if grep -Ei \
    'Tumble|TUMBLE[[:space:]]*\(' \
    "$HOMEWORK_SCRIPT"
then
    fail "tumbling-window implementation detected"
else
    pass "no tumbling-window implementation"
fi

section "TARGET HOSTS"

for host in \
    "zachwilson.techcreator.io" \
    "zachwilson.tech" \
    "lulu.techcreator.io"
do
    if grep -Fq "$host" "$HOMEWORK_SCRIPT"; then
        pass "$host"
    else
        fail "missing target host: $host"
    fi
done

section "MULTI-SINK EXECUTION"

CREATE_COUNT="$(
    grep -c 'create_statement_set()' "$HOMEWORK_SCRIPT" || true
)"

ADD_COUNT="$(
    grep -c 'statement_set.add_insert_sql(' "$HOMEWORK_SCRIPT" || true
)"

EXECUTE_COUNT="$(
    grep -c 'statement_set.execute()' "$HOMEWORK_SCRIPT" || true
)"

WAIT_COUNT="$(
    grep -c 'table_result.wait()' "$HOMEWORK_SCRIPT" || true
)"

printf 'CREATE_STATEMENT_SET_COUNT=%s\n' "$CREATE_COUNT"
printf 'ADD_INSERT_SQL_COUNT=%s\n' "$ADD_COUNT"
printf 'STATEMENT_SET_EXECUTE_COUNT=%s\n' "$EXECUTE_COUNT"
printf 'TABLE_RESULT_WAIT_COUNT=%s\n' "$WAIT_COUNT"

[[ "$CREATE_COUNT" -eq 1 ]] \
    && pass "one StatementSet creation" \
    || fail "expected exactly one StatementSet creation"

[[ "$ADD_COUNT" -eq 2 ]] \
    && pass "two coordinated sink inserts" \
    || fail "expected exactly two StatementSet inserts"

[[ "$EXECUTE_COUNT" -eq 1 ]] \
    && pass "one coordinated execution" \
    || fail "expected exactly one StatementSet execution"

[[ "$WAIT_COUNT" -eq 1 ]] \
    && pass "foreground job wait preserved" \
    || fail "expected exactly one foreground wait"

section "SECRET HYGIENE"

ENV_FILE_COUNT="$(
    find "$SUBMISSION" \
        -maxdepth 1 \
        -type f \
        \( \
            -name '.env' \
            -o -name '*.env' \
            -o -name 'flink-env.env' \
        \) \
        | wc -l \
        | tr -d ' '
)"

if [[ "$ENV_FILE_COUNT" -eq 0 ]]; then
    pass "no environment credential files"
else
    fail "environment credential file found"
fi

if grep -RniE \
    'pkc-[A-Za-z0-9]+|KAFKA_WEB_TRAFFIC_SECRET[[:space:]]*=[[:space:]]*[^<[:space:]]|KAFKA_WEB_TRAFFIC_KEY[[:space:]]*=[[:space:]]*[^<[:space:]]' \
    "$SUBMISSION" \
    >/dev/null 2>&1
then
    fail "possible credential literal detected"
else
    pass "no obvious credential literals"
fi

section "HOMEWORK ANSWERS"

for phrase in \
    "Sessionizes incoming web events by IP address and host" \
    "five-minute inactivity gap" \
    "zachwilson.techcreator.io" \
    "zachwilson.tech" \
    "lulu.techcreator.io"
do
    if grep -Fqi "$phrase" "$ANSWERS"; then
        pass "answers contain: $phrase"
    else
        fail "answers missing: $phrase"
    fi
done

section "VALIDATION SUMMARY"

printf 'PASS_COUNT=%s\n' "$PASS_COUNT"
printf 'FAIL_COUNT=%s\n' "$FAIL_COUNT"

if [[ "$FAIL_COUNT" -ne 0 ]]; then
    printf '\nFAIL: final submission validation failed\n' >&2
    exit 1
fi

printf '\nPASS: final Week 5 submission validation completed successfully\n'
exit 0
