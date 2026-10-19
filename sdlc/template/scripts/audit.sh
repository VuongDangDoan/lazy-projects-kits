#!/usr/bin/env bash
# audit.sh — run every workspace health check and report a single PASS/FAIL summary.
#
# Aggregates:
#   - feature-map-freshness.sh --check  (warn if SHA/date drift)
#   - legacy-scan-freshness.sh <module> (per existing scan file)
#   - validate-feature-map.py           (all feature-map files)
#   - validate-ticket.py                (all tickets)
#   - validate-us.py                    (all user stories)
#
# Exit: 0 = all PASS, 1 = at least one FAIL.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FAIL=0
SECTION_FAIL=()
TOTAL_PASS=0
TOTAL_FAIL=0

section() {
    echo ""
    echo "════════ $1 ════════"
}

run_check() {
    local label="$1"; shift
    if "$@" > /tmp/audit-out.$$ 2>&1; then
        echo "  ✓ $label"
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        local exit_code=$?
        echo "  ✗ $label  (exit $exit_code)"
        sed 's/^/    /' /tmp/audit-out.$$
        FAIL=1
        SECTION_FAIL+=("$label")
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
    rm -f /tmp/audit-out.$$
}

section "1. feature-map.md freshness"
run_check "feature-map-freshness --check" scripts/feature-map-freshness.sh --check

section "2. Legacy scan freshness (per existing scan)"
if compgen -G "knowledge/L2-legacy/scans/*-legacy-scan.md" > /dev/null; then
    for scan in knowledge/L2-legacy/scans/*-legacy-scan.md; do
        module="$(basename "$scan" -legacy-scan.md)"
        run_check "legacy-scan ($module)" scripts/legacy-scan-freshness.sh "$module"
    done
else
    echo "  (no scans yet — skipping)"
fi

section "3. feature-map structural validation"
run_check "validate-feature-map (all)" scripts/validate-feature-map.py

section "3b. feature-map summary freshness"
run_check "feature-map-summary --check --all" scripts/feature-map-summary.py --check --all

section "3c. domain summary freshness"
run_check "domain-summary --check --all" scripts/domain-summary.py --check --all

section "3d. active-context.md size"
ACTIVE_CTX="knowledge/L3-session/active-context.md"
if [[ -f "$ACTIVE_CTX" ]]; then
    lines=$(wc -l < "$ACTIVE_CTX")
    if (( lines > 200 )); then
        echo "  ⚠ active-context.md is $lines lines — consider archiving via scripts/archive-active-context.sh <topic>"
        FAIL=1
        SECTION_FAIL+=("active-context.md size > 200 lines")
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    else
        echo "  ✓ active-context.md is $lines lines (threshold: 200)"
        TOTAL_PASS=$((TOTAL_PASS + 1))
    fi
else
    echo "  (no active-context.md — skipping)"
fi

section "4. ticket validation"
if compgen -G "tasks/tickets/TICKET-*.md" > /dev/null; then
    run_check "validate-ticket (all)" bash -c 'scripts/validate-ticket.py tasks/tickets/TICKET-*.md'
else
    echo "  (no tickets yet — skipping)"
fi

section "5. user-story validation"
if compgen -G "docs/user-stories/US-*.md" > /dev/null; then
    run_check "validate-us (all)" bash -c 'scripts/validate-us.py docs/user-stories/US-*.md'
else
    echo "  (no user stories yet — skipping)"
fi

section "6. domain file validation"
run_check "validate-domain (all)" scripts/validate-domain.py

section "7. legacy scan validation"
run_check "validate-legacy-scan (all)" scripts/validate-legacy-scan.py

section "8. api contract validation"
run_check "validate-api-contract (all)" scripts/validate-api-contract.py

section "9. test case validation"
run_check "validate-test-case (all)" scripts/validate-test-case.py

section "10. e2e case validation"
run_check "validate-e2e-case (all)" scripts/validate-e2e-case.py

section "11. secret scan (all tracked files)"
run_check "check-secrets --all" scripts/check-secrets.sh --all

echo ""
echo "════════ SUMMARY ════════"
echo "  passed: $TOTAL_PASS"
echo "  failed: $TOTAL_FAIL"
if (( FAIL == 0 )); then
    echo ""
    echo "✓ workspace is healthy"
    exit 0
fi
echo ""
echo "✗ workspace has issues:"
for s in "${SECTION_FAIL[@]}"; do
    echo "    - $s"
done
exit 1
