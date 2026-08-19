#!/usr/bin/env bash
# ==============================================================================
# Script:      cleanup_dataexpert_artifacts.sh
# Author:      Ceasar Jackson
# Project:     DataExpert Boot Camp
# Purpose:     Safely identify and optionally remove redundant generated
#              DataExpert Boot Camp artifacts from the LOCAL repository.
#
# Safety:
#   - DRY-RUN by default.
#   - NEVER moves Git-tracked files.
#   - Protects canonical submission/remediation/archive/grade-feedback paths.
#   - Does NOT delete source Markdown/Python/SQL/Makefile artifacts.
#   - Does NOT use rm.
#   - Moves selected generated artifacts to ~/.Trash.
#   - Requires --execute before changing anything.
#   - Logs all discoveries and actions.
#
# IMPORTANT:
#   This script affects LOCAL FILES ONLY.
#   It cannot remove files from ChatGPT File Library or Project attachments.
#
# Usage:
#   ./scripts/cleanup_dataexpert_artifacts.sh
#   ./scripts/cleanup_dataexpert_artifacts.sh --execute
#   ./scripts/cleanup_dataexpert_artifacts.sh --include-pdf --execute
#
# Recommended first run:
#   ./scripts/cleanup_dataexpert_artifacts.sh
#
# ==============================================================================

set -Eeuo pipefail
IFS=$'\n\t'

readonly SCRIPT_NAME="$(basename "$0")"
readonly TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

# ----------------------------------------------------------------------
# Colors
# ----------------------------------------------------------------------

if [[ -t 1 ]]; then
    readonly RED=$'\033[0;31m'
    readonly GREEN=$'\033[0;32m'
    readonly YELLOW=$'\033[0;33m'
    readonly BLUE=$'\033[0;34m'
    readonly CYAN=$'\033[0;36m'
    readonly BOLD=$'\033[1m'
    readonly RESET=$'\033[0m'
else
    readonly RED=''
    readonly GREEN=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly CYAN=''
    readonly BOLD=''
    readonly RESET=''
fi

# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

EXECUTE=0
INCLUDE_PDF=0

REPO_ROOT=""
LOG_DIR=""
LOG_FILE=""

FOUND_COUNT=0
MOVED_COUNT=0
SKIPPED_COUNT=0

usage() {
    cat <<'EOF'
DataExpert Boot Camp Local Artifact Cleanup

USAGE
    cleanup_dataexpert_artifacts.sh [OPTIONS]

OPTIONS
    --execute
        Actually move matching files to the macOS Trash.
        Without this flag, the script performs a dry-run.

    --include-pdf
        Include generated grader-feedback PDFs as cleanup candidates.

        WARNING:
        Markdown grader-feedback source files remain protected.

    -h, --help
        Show this help message.

EXAMPLES
    # Safe discovery only
    ./scripts/cleanup_dataexpert_artifacts.sh

    # Show PDF files that would also be removed
    ./scripts/cleanup_dataexpert_artifacts.sh --include-pdf

    # Move generated PDFs and other disposable artifacts to Trash
    ./scripts/cleanup_dataexpert_artifacts.sh --include-pdf --execute
EOF
}

log() {
    local level="$1"
    shift
    local message="$*"
    local now

    now="$(date '+%Y-%m-%d %H:%M:%S')"

    printf '[%s] %-7s %s\n' "$now" "$level" "$message" \
        | tee -a "$LOG_FILE"
}

info() {
    printf '%sINFO:%s %s\n' "$CYAN" "$RESET" "$*"
    log "INFO" "$*"
}

pass() {
    printf '%sPASS:%s %s\n' "$GREEN" "$RESET" "$*"
    log "PASS" "$*"
}

warn() {
    printf '%sWARN:%s %s\n' "$YELLOW" "$RESET" "$*"
    log "WARN" "$*"
}

die() {
    printf '%sERROR:%s %s\n' "$RED" "$RESET" "$*" >&2

    if [[ -n "${LOG_FILE:-}" ]]; then
        log "ERROR" "$*"
    fi

    exit 1
}

on_error() {
    local exit_code=$?
    local line_number="${BASH_LINENO[0]:-unknown}"

    printf '%sERROR:%s Script failed near line %s (exit=%s)\n' \
        "$RED" "$RESET" "$line_number" "$exit_code" >&2

    exit "$exit_code"
}

trap on_error ERR

# ----------------------------------------------------------------------
# Arguments
# ----------------------------------------------------------------------

while (( $# > 0 )); do
    case "$1" in
        --execute)
            EXECUTE=1
            ;;
        --include-pdf)
            INCLUDE_PDF=1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Unknown argument: %s\n\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

# ----------------------------------------------------------------------
# Resolve repository
# ----------------------------------------------------------------------

if ! command -v git >/dev/null 2>&1; then
    die "git is required."
fi

if ! REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    die "Run this script from inside the DataExpert Boot Camp Git repository."
fi

cd "$REPO_ROOT"

LOG_DIR="$REPO_ROOT/validation/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/dataexpert_cleanup_${TIMESTAMP}.log"
touch "$LOG_FILE"

info "Repository root: $REPO_ROOT"
info "Log file: $LOG_FILE"

if (( EXECUTE == 0 )); then
    warn "DRY-RUN MODE — no files will be changed."
else
    warn "EXECUTE MODE — selected files will be moved to ~/.Trash."
fi

# ----------------------------------------------------------------------
# Safety checks
# ----------------------------------------------------------------------

repo_name="$(basename "$REPO_ROOT")"

if [[ "$repo_name" != "dataexpert_bootcamp" &&
      "$repo_name" != "dataexpert-bootcamp" ]]; then
    die "Unexpected repository '$repo_name'. Refusing cleanup."
fi

if [[ ! -d "$HOME/.Trash" ]]; then
    die "macOS Trash directory not found: $HOME/.Trash"
fi

# ----------------------------------------------------------------------
# Protected files
#
# Canonical/source artifacts should never be removed by this script.
# ----------------------------------------------------------------------

is_protected() {
    local path="$1"
    local base
    local relative

    base="$(basename "$path")"
    relative="${path#"$REPO_ROOT"/}"

    # ------------------------------------------------------------------
    # Git-tracked files are authoritative repository artifacts.
    #
    # A cleanup utility must never move a tracked file merely because its
    # extension looks generated (for example, a graded/submission ZIP).
    # ------------------------------------------------------------------
    if git ls-files --error-unmatch -- "$relative" >/dev/null 2>&1; then
        return 0
    fi

    # ------------------------------------------------------------------
    # Protect canonical coursework locations even when a file is currently
    # untracked. These directories may intentionally contain submission,
    # remediation, graded, or archival deliverables.
    # ------------------------------------------------------------------
    case "/$relative/" in
        */submission/*)
            return 0
            ;;
        */remediation/*)
            return 0
            ;;
        */archive/*)
            return 0
            ;;
        */grade_feedback/*)
            return 0
            ;;
    esac

    # ------------------------------------------------------------------
    # Protect source/documentation file types regardless of location.
    # ------------------------------------------------------------------
    case "$base" in
        *.md)
            return 0
            ;;
        *.py)
            return 0
            ;;
        *.sql)
            return 0
            ;;
        Makefile)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# ----------------------------------------------------------------------
# Move candidate safely to Trash
# ----------------------------------------------------------------------

trash_file() {
    local source="$1"
    local base destination

    base="$(basename "$source")"
    destination="$HOME/.Trash/$base"

    # Prevent overwriting an existing Trash item.
    if [[ -e "$destination" ]]; then
        destination="$HOME/.Trash/${TIMESTAMP}_${base}"
    fi

    if (( EXECUTE == 0 )); then
        printf '  %sWOULD TRASH%s  %s\n' "$YELLOW" "$RESET" "$source"
        log "DRYRUN" "Would move '$source' -> '$destination'"
        return
    fi

    mv -- "$source" "$destination"

    printf '  %sTRASHED%s      %s\n' "$GREEN" "$RESET" "$source"
    log "MOVED" "'$source' -> '$destination'"

    ((MOVED_COUNT += 1))
}

# ----------------------------------------------------------------------
# Candidate discovery
# ----------------------------------------------------------------------

printf '\n%s%sCandidate scan%s\n' "$BOLD" "$BLUE" "$RESET"
printf '%s\n' '------------------------------------------------------------'

declare -a candidates=()

# Common generated/transient submission artifacts.
while IFS= read -r -d '' file; do
    candidates+=("$file")
done < <(
    find "$REPO_ROOT" \
        -type f \
        \( \
            -name '*.zip' \
            -o -name '*.tar.gz' \
            -o -name '*.tgz' \
            -o -name '*.bak' \
            -o -name '*~' \
            -o -name '.DS_Store' \
        \) \
        -print0
)

# Optionally include generated grader-feedback PDFs.
if (( INCLUDE_PDF == 1 )); then
    while IFS= read -r -d '' file; do
        candidates+=("$file")
    done < <(
        find "$REPO_ROOT" \
            -type f \
            -iname '*grader*feedback*.pdf' \
            -print0
    )
fi

# ----------------------------------------------------------------------
# De-duplicate candidate paths
# ----------------------------------------------------------------------

declare -A seen=()

for candidate in "${candidates[@]}"; do
    [[ -f "$candidate" ]] || continue

    if [[ -n "${seen[$candidate]+x}" ]]; then
        continue
    fi

    seen["$candidate"]=1
    ((FOUND_COUNT += 1))

    relative="${candidate#"$REPO_ROOT"/}"

    if is_protected "$candidate"; then
        printf '  %sPROTECTED%s    %s\n' "$CYAN" "$RESET" "$relative"
        log "SKIP" "Protected file: $relative"
        ((SKIPPED_COUNT += 1))
        continue
    fi

    trash_file "$candidate"
done

# ----------------------------------------------------------------------
# Git safety report
# ----------------------------------------------------------------------

printf '\n%s%sGit status%s\n' "$BOLD" "$BLUE" "$RESET"
printf '%s\n' '------------------------------------------------------------'

git status --short | tee -a "$LOG_FILE" || true

printf '\n%s%sSummary%s\n' "$BOLD" "$BLUE" "$RESET"
printf '%s\n' '------------------------------------------------------------'

printf 'Candidates found : %d\n' "$FOUND_COUNT"
printf 'Protected/skipped: %d\n' "$SKIPPED_COUNT"

if (( EXECUTE == 1 )); then
    printf 'Moved to Trash   : %d\n' "$MOVED_COUNT"
else
    printf 'Files changed     : 0  (dry-run)\n'
fi

printf 'Log               : %s\n' "$LOG_FILE"

if (( EXECUTE == 0 )); then
    printf '\n%sNo files were changed.%s\n' "$GREEN" "$RESET"
    printf 'Review the list above before using --execute.\n'
else
    printf '\n%sCleanup complete.%s\n' "$GREEN" "$RESET"
    printf 'Files are recoverable from macOS Trash.\n'
fi
