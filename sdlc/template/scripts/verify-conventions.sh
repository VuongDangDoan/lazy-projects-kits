#!/usr/bin/env bash
# verify-conventions.sh — warn when L0 convention docs are stale vs `_source/`.
#
# Each L0 convention doc carries a "verified against actual source code: YYYY-MM-DD" line.
# If any configured _source/ repo has commits newer than that date
# AND the gap is > MAX_DAYS, this script prints a warning. It never blocks (exit 0)
# unless invoked with --strict. Repo names come from project.config.json.
#
# Pre-commit calls this in non-strict mode whenever any L0 file is staged or any
# _source/ commit is newer than the stamp by > MAX_DAYS.
#
# Usage:
#   scripts/verify-conventions.sh             # warn only (exit 0)
#   scripts/verify-conventions.sh --strict    # exit 1 on drift

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/scripts/lib-config.sh"

STRICT=0
[[ "${1:-}" == "--strict" ]] && STRICT=1

MAX_DAYS=14
TODAY_EPOCH=$(date +%s)

declare -a DOCS=(
    "knowledge/L0-global/naming-convention.md"
    "knowledge/L0-global/tech-stack.md"
    "knowledge/L0-global/crud-page-pattern.md"
)

extract_date() {
    # Pull the YYYY-MM-DD from a "verified" line. First match wins.
    grep -iE "verified.*[0-9]{4}-[0-9]{2}-[0-9]{2}" "$1" | head -1 | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -1
}

source_head_date() {
    # Most-recent commit date in _source/$1 as YYYY-MM-DD.
    local repo="$1"
    if [[ ! -d "_source/$repo/.git" ]] && [[ ! -f "_source/$repo/.git" ]]; then
        return 1
    fi
    (cd "_source/$repo" && git log -1 --format="%cs" 2>/dev/null)
}

REPOS=()
while IFS= read -r r; do [[ -n "$r" ]] && REPOS+=("$r"); done < <(cfg_repo_names)

if (( ${#REPOS[@]} == 0 )); then
    echo "note: no repos configured in project.config.json — skipping convention freshness check"
    exit 0
fi

NEWEST_SRC=""
echo "── convention freshness vs _source/ HEAD ──"
for repo in "${REPOS[@]}"; do
    head_date=$(source_head_date "$repo" || true)
    if [[ -z "$head_date" ]]; then
        echo "  ⚠ $repo: could not read _source/$repo HEAD date (symlink broken?)"
        continue
    fi
    echo "  $repo HEAD: $head_date"
    [[ "$head_date" > "$NEWEST_SRC" ]] && NEWEST_SRC="$head_date"
done
echo ""

if [[ -z "$NEWEST_SRC" ]]; then
    echo "⚠ verify-conventions: no readable _source/ repos — skipping" >&2
    exit 0
fi

NEWEST_SRC_EPOCH=$(date -j -f "%Y-%m-%d" "$NEWEST_SRC" "+%s" 2>/dev/null || date -d "$NEWEST_SRC" "+%s" 2>/dev/null)

DRIFT=0

for doc in "${DOCS[@]}"; do
    if [[ ! -f "$doc" ]]; then
        echo "  ⚠ $doc: missing"
        DRIFT=1
        continue
    fi
    stamp=$(extract_date "$doc")
    if [[ -z "$stamp" ]]; then
        echo "  ⚠ $doc: no \"verified ... YYYY-MM-DD\" line found"
        DRIFT=1
        continue
    fi
    stamp_epoch=$(date -j -f "%Y-%m-%d" "$stamp" "+%s" 2>/dev/null || date -d "$stamp" "+%s" 2>/dev/null)
    if (( NEWEST_SRC_EPOCH <= stamp_epoch )); then
        echo "  ✓ $doc: stamp $stamp ≥ source HEAD $NEWEST_SRC"
        continue
    fi
    gap_days=$(( (NEWEST_SRC_EPOCH - stamp_epoch) / 86400 ))
    if (( gap_days > MAX_DAYS )); then
        echo "  ✗ $doc: stamp $stamp is $gap_days days behind source HEAD $NEWEST_SRC (> $MAX_DAYS)"
        DRIFT=1
    else
        echo "  ⚠ $doc: stamp $stamp is $gap_days days behind source HEAD $NEWEST_SRC (within $MAX_DAYS-day grace)"
    fi
done

echo ""
if (( DRIFT )); then
    echo "Conventions are stale. Re-verify against _source/ and bump the stamp date."
    if (( STRICT )); then
        exit 1
    fi
fi
exit 0
