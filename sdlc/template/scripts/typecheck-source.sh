#!/usr/bin/env bash
# check-source.sh — Static analysis gate for /dev, /fe, and /mobile handoffs.
#
# Stack-agnostic: reads per-repo check config from scripts/.check-config.yml
# Falls back to TypeScript (tsc --noEmit) when no config entry exists.
#
# Config format (scripts/.check-config.yml):
#   [repo-name]: [shell command to run from inside _source/[repo]/ directory]
#
# Examples:
#   my-backend:    python -m mypy src/ --ignore-missing-imports
#   my-frontend:   npx tsc --noEmit
#   my-api:        php artisan lint
#   my-app:        flutter analyze
#   my-service:    go vet ./...
#   my-rails-api:  bundle exec rubocop --no-color
#
# Gate logic: compares current error count against a stored baseline.
# Fails only when current count > baseline (i.e. our changes ADDED errors).
# Baseline files: scripts/.check-baseline-<repo>.txt
#
# Usage:
#   scripts/typecheck-source.sh                        # all repos under _source/
#   scripts/typecheck-source.sh <repo-name>            # single repo
#   scripts/typecheck-source.sh <repo-name> --update-baseline

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CONFIG_FILE="scripts/.check-config.yml"

UPDATE_BASELINE=0
TARGETS=()

while (( $# > 0 )); do
    case "$1" in
        --update-baseline) UPDATE_BASELINE=1; shift ;;
        -h|--help) sed -n '2,28p' "$0"; exit 0 ;;
        --*) echo "unknown flag: $1" >&2; exit 2 ;;
        *) TARGETS+=("$1"); shift ;;
    esac
done

if (( ${#TARGETS[@]} == 0 )); then
    while IFS= read -r d; do TARGETS+=("$(basename "$d")"); done \
        < <(find _source -maxdepth 1 -mindepth 1 \( -type l -o -type d \) 2>/dev/null)
fi

# --- Resolve check command for a repo ---
get_check_cmd() {
    local repo="$1"
    if [[ -f "$CONFIG_FILE" ]]; then
        # Parse simple "repo: command" YAML (no arrays, no nesting)
        local cmd
        cmd=$(grep -E "^${repo}:" "$CONFIG_FILE" 2>/dev/null | head -1 | sed "s/^${repo}:[[:space:]]*//" | tr -d '\r')
        if [[ -n "$cmd" ]]; then
            echo "$cmd"
            return
        fi
    fi
    # Default: TypeScript
    echo "npx --no-install tsc --noEmit -p tsconfig.json"
}

# --- Count errors in command output ---
count_errors() {
    local output="$1"
    local cmd="$2"
    # TypeScript
    if echo "$cmd" | grep -q "tsc"; then
        echo "$output" | grep -cE '\): error TS' || true
        return
    fi
    # mypy (Python)
    if echo "$cmd" | grep -q "mypy"; then
        echo "$output" | grep -cE '^.*\.py:[0-9]+: error:' || true
        return
    fi
    # go vet
    if echo "$cmd" | grep -q "go vet\|golangci"; then
        echo "$output" | grep -cE '^.*\.go:[0-9]+:[0-9]+:' || true
        return
    fi
    # flutter analyze
    if echo "$cmd" | grep -q "flutter"; then
        echo "$output" | grep -cE '^\s+(error|warning) •' || true
        return
    fi
    # Generic: count non-empty lines that look like errors
    echo "$output" | grep -ciE '\berror\b|\bfailed\b|\bERROR\b' || true
}

FAIL=0

for repo in "${TARGETS[@]}"; do
    src="_source/$repo"
    check_cmd=$(get_check_cmd "$repo")
    baseline_file="scripts/.check-baseline-${repo}.txt"

    if [[ ! -d "$src" ]]; then
        echo "✗ $repo: $src not found (symlink missing?)" >&2
        FAIL=1; continue
    fi

    echo "── $repo ── cmd: $check_cmd"
    output=$(cd "$src" && eval "$check_cmd" 2>&1) || true
    current=$(count_errors "$output" "$check_cmd")

    if (( UPDATE_BASELINE == 1 )); then
        printf '%s\n' "$current" > "$baseline_file"
        echo "  baseline updated: $current error(s) recorded in $baseline_file"
        continue
    fi

    if [[ -f "$baseline_file" ]]; then
        baseline=$(cat "$baseline_file" | tr -d '[:space:]')
    else
        baseline=0
        echo "  ⚠ no baseline at $baseline_file — treating as 0"
        echo "    run: scripts/typecheck-source.sh $repo --update-baseline"
    fi

    if (( current > baseline )); then
        echo "  ✗ FAIL: $current error(s), baseline $baseline → added $((current - baseline))"
        echo "$output" | tail -30
        FAIL=1
    elif (( current < baseline )); then
        echo "  ✓ PASS: $current error(s), baseline $baseline (improved by $((baseline - current)))"
        echo "    consider: scripts/typecheck-source.sh $repo --update-baseline"
    else
        echo "  ✓ PASS: $current error(s), matches baseline"
    fi
done

if (( FAIL )); then
    echo ""
    echo "Static analysis gate FAILED. /dev, /fe, or /mobile handoff is blocked until added errors are resolved."
    exit 1
fi

(( UPDATE_BASELINE == 0 )) && echo "" && echo "Static analysis gate PASSED."
exit 0
