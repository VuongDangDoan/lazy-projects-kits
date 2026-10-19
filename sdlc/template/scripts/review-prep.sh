#!/usr/bin/env bash
# review-prep.sh — single-shot quality summary consumed by /review.
#
# Aggregates the cheap deterministic gates (typecheck, doc-sync, feature-map
# freshness, convention freshness, active-context BR validation) into one
# report. /review opens its checklist only after this prints OK or after each
# block is acknowledged.
#
# Exit codes:
#   0 — all gates pass (review may proceed)
#   1 — one or more BLOCKING gates failed (typecheck, missing Doc Sync Plan)
#   2 — only WARNINGS (drift, stale stamps) — review may proceed but should flag
#
# Usage:
#   scripts/review-prep.sh                    # all configured repos
#   scripts/review-prep.sh <repo-name>        # single-repo ticket (name from project.config.json)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TARGET="${1:-}"
BLOCK=0
WARN=0

banner() {
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "════════════════════════════════════════════════════════════"
}

# 1. Static analysis — BLOCKING
banner "1/5  Static analysis (_source/)"
if [[ -n "$TARGET" ]]; then
    scripts/typecheck-source.sh "$TARGET" || BLOCK=1
else
    scripts/typecheck-source.sh || BLOCK=1
fi

# 2. Feature-map freshness — WARN
banner "2/5  Feature-map §2 freshness"
if scripts/feature-map-freshness.sh --check 2>&1 | tee /dev/stderr | grep -qE '\?  → |[a-f0-9]{7} +→ +[a-f0-9]{7}'; then
    echo "  ⚠ §2 Maintenance is out of date — bump via scripts/feature-map-freshness.sh"
    WARN=1
else
    echo "  ✓ §2 Maintenance is current"
fi

# 3. Convention freshness — WARN
banner "3/5  L0 convention freshness"
scripts/verify-conventions.sh || WARN=1

# 4. Active-context BR validation — BLOCKING (silent BR drift = enforced fiction)
banner "4/5  Active-context BR-IDs vs domain.md §4"
scripts/validate-active-context.py || BLOCK=1

# 5. Role-file convention sync — WARN
banner "5/5  Role-file convention sync"
scripts/verify-role-files.sh || WARN=1

banner "Review prep summary"
if (( BLOCK )); then
    echo "  ✗ BLOCKING: one or more deterministic gates failed."
    echo "    /review must return BLOCKING — do not open the checklist."
    exit 1
fi
if (( WARN )); then
    echo "  ⚠ WARN: drift detected. /review may proceed but must list these in the report."
    exit 2
fi
echo "  ✓ All deterministic gates passed. /review may open the full checklist."
exit 0
