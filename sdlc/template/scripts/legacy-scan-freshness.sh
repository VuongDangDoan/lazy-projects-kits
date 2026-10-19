#!/usr/bin/env bash
# legacy-scan-freshness.sh — report STALE / FRESH / MISSING for a module's legacy scan.
#
# Usage:
#   scripts/legacy-scan-freshness.sh <module>
#
# Output: one of MISSING / STALE / FRESH on stdout, with a reason on stderr.
# Exit code: 0 = FRESH, 1 = STALE, 2 = MISSING, 3 = usage error.
#
# Freshness rule (per legacy-scan.md Skip Conditions):
#   - MISSING: scan file does not exist
#   - STALE:   scan date older than 30 days
#   - FRESH:   scan date within 30 days

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

module="${1:-}"
if [[ -z "$module" ]]; then
    echo "usage: $0 <module>" >&2
    exit 3
fi

SCAN="knowledge/L2-legacy/scans/${module}-legacy-scan.md"

if [[ ! -f "$SCAN" ]]; then
    echo "MISSING"
    echo "no scan file at $SCAN — run /legacy-scan $module [TICKET-ID]" >&2
    exit 2
fi

# Extract scan date — format: **Scan date:** YYYY-MM-DD
scan_date="$(grep -m1 -oE '\*\*Scan date:\*\* [0-9]{4}-[0-9]{2}-[0-9]{2}' "$SCAN" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || true)"

if [[ -z "$scan_date" ]]; then
    echo "STALE"
    echo "scan file exists but **Scan date:** field is missing or malformed" >&2
    exit 1
fi

# Compute age in days (portable: macOS BSD date vs GNU date)
today_epoch="$(date +%s)"
if scan_epoch="$(date -j -f '%Y-%m-%d' "$scan_date" +%s 2>/dev/null)"; then
    : # macOS BSD date worked
elif scan_epoch="$(date -d "$scan_date" +%s 2>/dev/null)"; then
    : # GNU date worked
else
    echo "STALE"
    echo "could not parse scan date '$scan_date'" >&2
    exit 1
fi

age_days=$(( (today_epoch - scan_epoch) / 86400 ))

if (( age_days > 30 )); then
    echo "STALE"
    echo "scan date $scan_date is $age_days days old (threshold: 30 days)" >&2
    exit 1
else
    echo "FRESH"
    echo "scan date $scan_date is $age_days days old (within 30-day threshold)" >&2
    exit 0
fi
