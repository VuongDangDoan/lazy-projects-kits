#!/usr/bin/env bash
# next-id.sh — print the next sequential ID for a given artifact type.
#
# Usage:
#   scripts/next-id.sh ticket
#   scripts/next-id.sh us
#   scripts/next-id.sh e2e
#   scripts/next-id.sh feature <module>
#
# Prints the next ID to stdout, no extra text. Exits non-zero on error.

set -euo pipefail

# Resolve repo root (script lives in <repo>/scripts/)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

kind="${1:-}"

if [[ -z "$kind" ]]; then
    echo "usage: $0 {ticket|us|e2e|feature <module>}" >&2
    exit 2
fi

# Find the highest 3-digit number after a given prefix in matching files.
# Args: <prefix> <glob...>
max_seq() {
    local prefix="$1"; shift
    local highest=0
    for f in "$@"; do
        # Skip non-existent globs
        [[ -e "$f" ]] || continue
        local name
        name="$(basename "$f")"
        if [[ "$name" =~ ^${prefix}-?([0-9]{3,})\. ]]; then
            local n="${BASH_REMATCH[1]}"
            # Strip leading zeros for arithmetic
            n=$((10#$n))
            (( n > highest )) && highest=$n
        fi
    done
    echo "$highest"
}

# Basenames of the files under <dir> on every origin ref this checkout has: main and the task
# branches other Lazy Bot factories pushed (the factory fetches origin/factory/*), so two
# machines working in parallel do not hand out the same id. Silent outside a git checkout.
remote_names() {
    git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0
    local ref
    for ref in $(git for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null); do
        git ls-tree -r --name-only "$ref" -- "$1" 2>/dev/null
    done
}

# Highest number after <prefix> in the names read from stdin.
max_names() {
    local prefix="$1" highest=0 name n
    while IFS= read -r name; do
        name="$(basename "$name")"
        if [[ "$name" =~ ^${prefix}-?([0-9]{3,})[.-] ]]; then
            n=$((10#${BASH_REMATCH[1]}))
            (( n > highest )) && highest=$n
        fi
    done
    echo "$highest"
}

# max of the local files and the same directory on the other branches
next_after() {
    local local_max="$1" remote_max
    remote_max=$(remote_names "$2" | max_names "$3")
    (( remote_max > local_max )) && local_max=$remote_max
    echo "$local_max"
}

case "$kind" in
    ticket)
        h=$(max_seq "TICKET" tasks/tickets/TICKET-*.md)
        h=$(next_after "$h" tasks/tickets TICKET)
        printf "TICKET-%03d\n" $((h + 1))
        ;;
    us)
        h=$(max_seq "US" docs/user-stories/US-*.md)
        h=$(next_after "$h" docs/user-stories US)
        printf "US-%03d\n" $((h + 1))
        ;;
    e2e)
        # E2E cases are nested under tests/e2e/cases/<module>/TC-E-<NNN>-*.md
        highest=0
        while IFS= read -r f; do
            name="$(basename "$f")"
            if [[ "$name" =~ ^TC-E-([0-9]{3,})- ]]; then
                n=$((10#${BASH_REMATCH[1]}))
                (( n > highest )) && highest=$n
            fi
        done < <(find tests/e2e/cases -type f -name 'TC-E-*.md' 2>/dev/null)
        highest=$(next_after "$highest" tests/e2e/cases TC-E)
        printf "TC-E-%03d\n" $((highest + 1))
        ;;
    feature)
        module="${2:-}"
        if [[ -z "$module" ]]; then
            echo "usage: $0 feature <module>" >&2
            exit 2
        fi
        map="architecture/feature-map/${module}.md"
        if [[ ! -f "$map" ]]; then
            echo "error: feature map not found: $map" >&2
            exit 1
        fi
        # Extract the prefix used in this module by finding the first "| XXX-NNN |" row
        prefix="$(grep -oE '^\| [A-Z]+-[0-9]+' "$map" | head -1 | tr -d '| ' | sed -E 's/-[0-9]+$//')"
        if [[ -z "$prefix" ]]; then
            module_uc="$(printf '%s' "$module" | tr '[:lower:]' '[:upper:]')"
            echo "error: no existing feature ID found in $map — cannot infer prefix" >&2
            echo "       set the first row manually (e.g. | ${module_uc}-001 | ... |) then re-run" >&2
            exit 1
        fi
        # Find the highest number with this prefix
        highest=0
        while IFS= read -r n; do
            n=$((10#$n))
            (( n > highest )) && highest=$n
        done < <(grep -oE "^\| ${prefix}-[0-9]+" "$map" | grep -oE '[0-9]+$')
        printf "%s-%03d\n" "$prefix" $((highest + 1))
        ;;
    adr)
        # ADRs live at architecture/decisions/NNN-<kebab-title>.md
        highest=0
        while IFS= read -r f; do
            name="$(basename "$f")"
            if [[ "$name" =~ ^([0-9]{3,})- ]]; then
                n=$((10#${BASH_REMATCH[1]}))
                (( n > highest )) && highest=$n
            fi
        done < <(find architecture/decisions -type f -name '[0-9]*.md' 2>/dev/null)
        printf "%03d\n" $((highest + 1))
        ;;
    *)
        echo "unknown kind: $kind" >&2
        echo "usage: $0 {ticket|us|e2e|adr|feature <module>}" >&2
        exit 2
        ;;
esac
