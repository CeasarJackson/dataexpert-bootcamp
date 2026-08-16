#!/usr/bin/env bash
# =============================================================================
# DataExpert Boot Camp
# Week 3 Spark Fundamentals — Grade Remediation Validator
#
# Purpose:
#   Validate historical preservation, hardened implementation requirements,
#   and persisted runtime evidence for the Week 3 remediation.
#
# Usage:
#   ./spark_fundamentals/week03_halo/remediation/scripts/validate_week03_remediation.sh
# =============================================================================

set -euo pipefail

WEEK3="spark_fundamentals/week03_halo"
REM="$WEEK3/remediation"
SCRIPT="$WEEK3/scripts/spark_fundamentals_homework.py"

PLAN="$REM/evidence/joined_physical_plan_formatted.txt"
CSV="$REM/evidence/partition_sort_size_results.csv"

ORIGINAL_ZIP="$WEEK3/submission/CeasarJackson_Spark_Fundamentals_Week3_Halo.zip"
EXPECTED_ORIGINAL_HASH="719984774276fc2da7291a4841ea6009608bf685414eddda79de1c0d3b124c79"

PASS_COUNT=0
FAIL_COUNT=0

pass() {
    printf 'PASS: %s\n' "$1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    printf 'FAIL: %s\n' "$1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

echo "======================================================================"
echo " WEEK 3 SPARK FUNDAMENTALS REMEDIATION VALIDATION"
echo "======================================================================"

echo
echo "===== HISTORICAL BASELINE ====="

if git rev-parse -q --verify refs/tags/week03-graded-a >/dev/null; then
    pass "week03-graded-a exists"
else
    fail "week03-graded-a is missing"
fi

ACTUAL_HASH="$(
    shasum -a 256 "$ORIGINAL_ZIP" | awk '{print $1}'
)"

if [[ "$ACTUAL_HASH" == "$EXPECTED_ORIGINAL_HASH" ]]; then
    pass "original graded ZIP remains byte-for-byte unchanged"
else
    fail "original graded ZIP hash changed"
fi

echo
echo "===== HARDENED IMPLEMENTATION ====="

grep -Fq \
    'spark.sql.autoBroadcastJoinThreshold", "-1"' \
    "$SCRIPT" \
    && pass "automatic broadcast joins disabled" \
    || fail "automatic broadcast disablement missing"

grep -Fq \
    '.bucketBy(NUM_BUCKETS, "match_id")' \
    "$SCRIPT" \
    && pass "16-bucket implementation present" \
    || fail "bucket implementation missing"

grep -Fq \
    '.join(mmp, on="match_id", how="left")' \
    "$SCRIPT" \
    && pass "medals_matches_players joins on bucket key match_id" \
    || fail "bucket-aligned mmp join missing"

grep -Fq \
    'sortWithinPartitions' \
    "$SCRIPT" \
    && pass "sortWithinPartitions implementation present" \
    || fail "sortWithinPartitions implementation missing"

grep -Fq \
    'partitionBy(' \
    "$SCRIPT" \
    && pass "physical partitionBy implementation present" \
    || fail "partitionBy implementation missing"

grep -Fq \
    'repartition(' \
    "$SCRIPT" \
    && pass "repartition implementation present" \
    || fail "repartition implementation missing"

grep -Fq \
    'joined_physical_plan_formatted.txt' \
    "$SCRIPT" \
    && pass "physical-plan persistence implemented" \
    || fail "physical-plan persistence missing"

echo
echo "===== RUNTIME BUCKET EVIDENCE ====="

if [[ -s "$PLAN" ]]; then
    pass "persisted formatted physical plan exists"
else
    fail "persisted formatted physical plan missing"
fi

BUCKETED_COUNT="$(
    grep -c 'Bucketed: true' "$PLAN" || true
)"

if (( BUCKETED_COUNT >= 3 )); then
    pass "physical plan contains at least three bucketed scans"
else
    fail "expected at least three bucketed scans; found $BUCKETED_COUNT"
fi

SELECTED_BUCKET_COUNT="$(
    grep -c 'SelectedBucketsCount: 16 out of 16' "$PLAN" || true
)"

if (( SELECTED_BUCKET_COUNT >= 3 )); then
    pass "all three large scans recognize 16 buckets"
else
    fail "expected three 16-of-16 bucket signals; found $SELECTED_BUCKET_COUNT"
fi

SORT_MERGE_COUNT="$(
    grep -c 'SortMergeJoin' "$PLAN" || true
)"

if (( SORT_MERGE_COUNT >= 2 )); then
    pass "physical plan contains both large-table SortMergeJoins"
else
    fail "expected at least two SortMergeJoin signals"
fi

BROADCAST_EXCHANGE_COUNT="$(
    grep -c 'BroadcastExchange' "$PLAN" || true
)"

if (( BROADCAST_EXCHANGE_COUNT >= 2 )); then
    pass "physical plan confirms explicit dimension broadcasts"
else
    fail "expected broadcast exchanges for small dimensions"
fi

HASH_PARTITION_EXCHANGES="$(
    grep -ciE 'Exchange.*hashpartitioning|hashpartitioning.*Exchange' \
        "$PLAN" || true
)"

if (( HASH_PARTITION_EXCHANGES == 0 )); then
    pass "no hash-partition shuffle exchange recorded for bucketed large joins"
else
    fail "unexpected hash-partition exchange detected"
fi

echo
echo "===== PARTITION EXPERIMENT EVIDENCE ====="

if [[ -s "$CSV" ]]; then
    pass "partition-size evidence CSV exists"
else
    fail "partition-size evidence CSV missing"
fi

for experiment in \
    baseline_coalesced \
    partition_playlist_sorted_playlist_map \
    partition_map_sorted_map_playlist \
    partition_playlist_map_sorted_playlist_map
do
    if grep -Fq "$experiment" "$CSV"; then
        pass "size evidence contains $experiment"
    else
        fail "size evidence missing $experiment"
    fi
done

echo
echo "===== PYTHON VALIDATION ====="

if conda run -n dataeng python -m py_compile "$SCRIPT"; then
    pass "hardened Spark homework compiles"
else
    fail "hardened Spark homework compilation failed"
fi

if conda run -n dataeng python -c \
    'import pyspark; assert pyspark.__version__; print(pyspark.__version__)'
then
    pass "PySpark runtime imports"
else
    fail "PySpark runtime import failed"
fi

echo
echo "===== GIT INTEGRITY ====="

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
echo "Week 3 remediation validation completed successfully."
