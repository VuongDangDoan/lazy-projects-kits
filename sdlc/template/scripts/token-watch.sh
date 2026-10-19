#!/usr/bin/env bash
# token-watch.sh — quick token-cost telemetry + threshold alerts for the
# Claude Code session.
#
# Reads `ccusage daily --json` and emits a compact summary:
#   - Today's cost (Opus + Haiku breakdown)
#   - Output / cache-read ratio (high cache-read = many turns over long session)
#   - Threshold check vs $WARN / $ALERT (env-tunable)
#   - Exit code 0 = OK, 1 = WARN, 2 = ALERT (suitable for CI / hooks)
#
# Usage:
#   scripts/token-watch.sh                  # today's totals
#   scripts/token-watch.sh --since 20260513 # window
#   scripts/token-watch.sh --json           # raw passthrough
#
# Env vars (override defaults):
#   TOKEN_WARN_USD=50    Yellow warning threshold (per day, default $50)
#   TOKEN_ALERT_USD=100  Red alert threshold (per day, default $100)
#   TOKEN_CACHE_READ_WARN_M=200  Cache-read warning at >200M tokens/day (suggests session is too long — split it)
#
# Why this exists:
#   The 2026-05-13 US-003 session hit $183 in one day. ~99% of token volume
#   was cache-read (re-loading the same prompt context across many turns).
#   Catching cost trajectory mid-session lets us prune `active-context.md`,
#   end sessions early, or switch subagents to Haiku before the bill compounds.

set -uo pipefail

WARN_USD="${TOKEN_WARN_USD:-50}"
ALERT_USD="${TOKEN_ALERT_USD:-100}"
CACHE_READ_WARN_M="${TOKEN_CACHE_READ_WARN_M:-200}"

# Colors (no-op when not on a TTY).
if [[ -t 1 ]]; then
    RED=$'\e[31m'; YELLOW=$'\e[33m'; GREEN=$'\e[32m'; DIM=$'\e[2m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
else
    RED=""; YELLOW=""; GREEN=""; DIM=""; BOLD=""; RESET=""
fi

ARGS=("daily" "--json")
PASSTHROUGH=0
while (( $# > 0 )); do
    case "$1" in
        --json) PASSTHROUGH=1; shift ;;
        --since|--until|-s|-u) ARGS+=("$1" "$2"); shift 2 ;;
        --help|-h)
            sed -n '2,/^$/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) ARGS+=("$1"); shift ;;
    esac
done

# Pull JSON. npx the latest ccusage so users don't need a global install.
RAW="$(npx -y ccusage@latest "${ARGS[@]}" 2>/dev/null)"
if [[ -z "$RAW" ]]; then
    echo "${RED}token-watch: ccusage returned no data — is Claude Code logged in?${RESET}" >&2
    exit 2
fi

if (( PASSTHROUGH == 1 )); then
    echo "$RAW"
    exit 0
fi

# Parse with jq if present, else fall back to a tiny node one-liner.
parse_field() {
    local field="$1"
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$RAW" | jq -r ".totals.${field} // 0"
    else
        printf '%s' "$RAW" | node -e "
            const d = JSON.parse(require('fs').readFileSync(0, 'utf8'));
            process.stdout.write(String((d.totals && d.totals['${field}']) || 0));
        "
    fi
}

parse_model_cost() {
    local model="$1"
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$RAW" | jq -r --arg m "$model" \
            '.daily[].modelBreakdowns[] | select(.modelName==$m) | .cost' \
            | head -1
    else
        printf '%s' "$RAW" | node -e "
            const d = JSON.parse(require('fs').readFileSync(0, 'utf8'));
            const day = d.daily && d.daily[0];
            const b = day && (day.modelBreakdowns || []).find(x => x.modelName === '${model}');
            process.stdout.write(String((b && b.cost) || 0));
        "
    fi
}

COST="$(parse_field totalCost)"
INPUT="$(parse_field inputTokens)"
OUTPUT="$(parse_field outputTokens)"
CACHE_READ="$(parse_field cacheReadTokens)"
CACHE_CREATE="$(parse_field cacheCreationTokens)"

OPUS_COST="$(parse_model_cost claude-opus-4-7)"
HAIKU_COST="$(parse_model_cost claude-haiku-4-5-20251001)"

# Coerce to numbers, default 0 (so arithmetic in awk below is safe).
[[ -z "$COST" || "$COST" == "null" ]] && COST=0
[[ -z "$OPUS_COST" || "$OPUS_COST" == "null" ]] && OPUS_COST=0
[[ -z "$HAIKU_COST" || "$HAIKU_COST" == "null" ]] && HAIKU_COST=0

# Format helpers.
fmt_usd() { awk -v v="$1" 'BEGIN { printf "$%.2f", v }'; }
fmt_int() { printf "%'d" "$1" 2>/dev/null || printf "%d" "$1"; }
fmt_m()   { awk -v v="$1" 'BEGIN { printf "%.1fM", v/1000000 }'; }
pct()     { awk -v a="$1" -v b="$2" 'BEGIN { if (b == 0) print "0"; else printf "%.0f", (a/b)*100 }'; }

CACHE_READ_M=$(awk -v v="$CACHE_READ" 'BEGIN { printf "%.1f", v/1000000 }')

# Threshold checks.
LEVEL="OK"
EXIT_CODE=0
LEVEL_COLOR="$GREEN"
LEVEL_TEXT="${GREEN}✓ OK${RESET}"

if awk -v c="$COST" -v t="$ALERT_USD" 'BEGIN { exit !(c >= t) }'; then
    LEVEL="ALERT"
    EXIT_CODE=2
    LEVEL_COLOR="$RED"
    LEVEL_TEXT="${RED}${BOLD}⚠ ALERT — daily cost ≥ ${ALERT_USD} USD${RESET}"
elif awk -v c="$COST" -v t="$WARN_USD" 'BEGIN { exit !(c >= t) }'; then
    LEVEL="WARN"
    EXIT_CODE=1
    LEVEL_COLOR="$YELLOW"
    LEVEL_TEXT="${YELLOW}⚠ WARN — daily cost ≥ ${WARN_USD} USD${RESET}"
fi

CACHE_READ_HOT=0
if awk -v v="$CACHE_READ_M" -v t="$CACHE_READ_WARN_M" 'BEGIN { exit !(v >= t) }'; then
    CACHE_READ_HOT=1
fi

# ─── Output ─────────────────────────────────────────────────────────────────
echo
echo "${BOLD}Token watch — Claude Code session${RESET}"
echo "${DIM}─────────────────────────────────────────${RESET}"
printf "  Total cost today    : ${LEVEL_COLOR}%s${RESET}  (warn=$%s · alert=$%s)\n" \
    "$(fmt_usd "$COST")" "$WARN_USD" "$ALERT_USD"
printf "    ├─ Opus  4.7      : %s\n" "$(fmt_usd "$OPUS_COST")"
printf "    └─ Haiku 4.5      : %s\n" "$(fmt_usd "$HAIKU_COST")"
echo
printf "  Input  (uncached)   : %s tokens\n" "$(fmt_int "${INPUT:-0}")"
printf "  Output              : %s tokens  (%s)\n" "$(fmt_int "${OUTPUT:-0}")" "$(fmt_m "${OUTPUT:-0}")"
printf "  Cache create        : %s tokens  (%s)\n" "$(fmt_int "${CACHE_CREATE:-0}")" "$(fmt_m "${CACHE_CREATE:-0}")"
if (( CACHE_READ_HOT == 1 )); then
    printf "  Cache read          : ${YELLOW}%s tokens  (${CACHE_READ_M}M — high; long session)${RESET}\n" \
        "$(fmt_int "${CACHE_READ:-0}")"
else
    printf "  Cache read          : %s tokens  (${CACHE_READ_M}M)\n" "$(fmt_int "${CACHE_READ:-0}")"
fi
echo "${DIM}─────────────────────────────────────────${RESET}"
echo "  Status              : $LEVEL_TEXT"

# Tips when the bill is hot.
if [[ "$LEVEL" != "OK" ]] || (( CACHE_READ_HOT == 1 )); then
    echo
    echo "${BOLD}Hints:${RESET}"
    if (( CACHE_READ_HOT == 1 )); then
        echo "  • Cache-read >${CACHE_READ_WARN_M}M today suggests a long session re-reading"
        echo "    the same context many times. Consider ending the session and"
        echo "    starting fresh (cache TTL resets) or trimming"
        echo "    knowledge/L3-session/active-context.md."
    fi
    # Haiku-vs-Opus ratio tip.
    HAIKU_RATIO_BPS=$(awk -v h="$HAIKU_COST" -v c="$COST" 'BEGIN { if (c==0) print 0; else printf "%.0f", (h/c)*10000 }')
    if (( HAIKU_RATIO_BPS < 200 )); then  # <2% of spend on Haiku
        echo "  • Sub-agent spend is ~100% Opus. Pass model:\"haiku\" to Explore"
        echo "    agents for read-only research — typically 20-30× cheaper."
    fi
    echo "  • Other levers: batch tool calls per turn, offset/limit on big Read,"
    echo "    archive stale legacy-scan §8 appendix entries."
fi
echo

exit "$EXIT_CODE"
