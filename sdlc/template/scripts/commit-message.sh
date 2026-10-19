#!/usr/bin/env bash
# commit-message.sh — generate a conventional commit message from a ticket file.
#
# Reads tasks/tickets/TICKET-XXX.md and produces a properly-formatted commit
# message. Output goes to stdout — pipe into git or copy/paste.
#
# Usage:
#   scripts/commit-message.sh TICKET-001
#   scripts/commit-message.sh --type=fix TICKET-014
#   scripts/commit-message.sh --co-authored TICKET-001
#
#   git commit -m "$(scripts/commit-message.sh TICKET-001)"
#
# Type detection (auto-derived from ticket title verb):
#   Implement / Add / Create   → feat
#   Fix / Resolve              → fix
#   Refactor / Migrate / Move  → refactor
#   Update / Modify / Change   → feat (override with --type=...)
#   Remove / Delete / Drop     → chore
#   Document                   → docs
#   Test                       → test
#   default                    → feat
#
# Override with --type=feat|fix|chore|docs|test|refactor|perf|build|style|ci

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TYPE_OVERRIDE=""
CO_AUTHORED=0
TICKET_ID=""

for arg in "$@"; do
    case "$arg" in
        --type=*)        TYPE_OVERRIDE="${arg#--type=}" ;;
        --co-authored)   CO_AUTHORED=1 ;;
        --help|-h)
            sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        TICKET-*)        TICKET_ID="$arg" ;;
        *)
            echo "unknown arg: $arg" >&2
            echo "usage: $0 [--type=TYPE] [--co-authored] TICKET-XXX" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$TICKET_ID" ]]; then
    echo "usage: $0 [--type=TYPE] [--co-authored] TICKET-XXX" >&2
    exit 2
fi

TICKET_FILE="tasks/tickets/${TICKET_ID}.md"
if [[ ! -f "$TICKET_FILE" ]]; then
    echo "error: ticket file not found: $TICKET_FILE" >&2
    exit 1
fi

# Extract H1 title: "# TICKET-001 — <Title>" → "<Title>"
# Use POSIX-portable patterns — BSD sed (macOS default) doesn't grok \s.
TITLE="$(grep -m1 -E "^# ${TICKET_ID} +— +" "$TICKET_FILE" 2>/dev/null | sed -E "s/^# ${TICKET_ID} +— +//")"
if [[ -z "$TITLE" ]]; then
    echo "error: could not extract H1 title from $TICKET_FILE" >&2
    exit 1
fi

# Extract metadata fields
get_field() {
    local field="$1"
    grep -m1 -E "^\*\*${field}:\*\*" "$TICKET_FILE" 2>/dev/null \
        | sed -E "s/^\*\*${field}:\*\*[[:space:]]*//" \
        | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'
}

US_ID="$(get_field 'US-ID')"
MODULE="$(get_field 'Module')"
LAYER="$(get_field 'Layer')"

# Derive type from title verb (unless overridden)
if [[ -n "$TYPE_OVERRIDE" ]]; then
    TYPE="$TYPE_OVERRIDE"
else
    first_word="$(echo "$TITLE" | awk '{print tolower($1)}')"
    case "$first_word" in
        implement|add|create|introduce|enable)  TYPE="feat" ;;
        fix|resolve|patch|repair)                TYPE="fix" ;;
        refactor|migrate|move|extract|rename)    TYPE="refactor" ;;
        remove|delete|drop|deprecate)            TYPE="chore" ;;
        document|docs)                            TYPE="docs" ;;
        test)                                     TYPE="test" ;;
        update|modify|change|adjust)              TYPE="feat" ;;
        *)                                        TYPE="feat" ;;
    esac
fi

# Strip the leading verb to get the description body, then sentence-case the
# first letter — UNLESS the first word is an all-caps acronym (CRUD, API, BOM).
DESCRIPTION="$(echo "$TITLE" | awk '
    {
        sub(/^[A-Za-z]+ +/, "")
        n = split($0, words, " ")
        if (n > 0 && length(words[1]) > 1 && toupper(words[1]) == words[1]) {
            # First word is an acronym — keep capitalization as is
            print
        } else {
            # Normal word — lowercase first letter
            first = tolower(substr($0, 1, 1))
            print first substr($0, 2)
        }
    }
')"

# Resolve module scope. Drop spaces, lowercase. Fall back to "core".
SCOPE="$(echo "$MODULE" | tr '[:upper:]' '[:lower:]' | tr -d ' ')"
[[ -z "$SCOPE" ]] && SCOPE="core"

# Build the message — keep it minimal (subject + structured footer)
echo "${TYPE}(${SCOPE}): ${DESCRIPTION}"
echo ""
[[ -n "$LAYER" ]] && echo "Layer: $LAYER"
[[ -n "$US_ID" ]] && echo "US: $US_ID"
echo ""
echo "Ref: ${TICKET_ID}"
