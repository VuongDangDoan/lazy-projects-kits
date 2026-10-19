#!/usr/bin/env bash
# check-secrets.sh — scan files for accidentally committed secrets.
#
# Usage:
#   scripts/check-secrets.sh                       # scan staged files (pre-commit mode)
#   scripts/check-secrets.sh path1 path2 ...       # scan specific paths
#   scripts/check-secrets.sh --all                 # scan all git-tracked files
#
# Detects: AWS / GitHub / GitLab / OpenAI / Anthropic / Slack tokens,
#          private keys, JWTs, DB connection strings with passwords,
#          generic password assignments.
#
# Exit:  0 = no secrets found
#        1 = potential secret(s) found
#        2 = usage error
#
# False positives can be skipped by including placeholder words like
# "your-key", "<TOKEN>", "[REPLACE]", "xxxx", "example", "placeholder",
# "fake", "test", or "sample" on the same line.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- Resolve target file list ---
PATHS=()
if [[ "${1:-}" == "--all" ]]; then
    while IFS= read -r line; do
        [[ -n "$line" ]] && PATHS+=("$line")
    done < <(git ls-files)
elif (( $# > 0 )); then
    PATHS=("$@")
else
    while IFS= read -r line; do
        [[ -n "$line" ]] && PATHS+=("$line")
    done < <(git diff --cached --name-only --diff-filter=ACM)
fi

if (( ${#PATHS[@]} == 0 )); then
    echo "✓ no files to scan"
    exit 0
fi

# --- Patterns ---
# Format: "Description|extended-regex"
PATTERNS=(
    "AWS Access Key ID|AKIA[0-9A-Z]{16}"
    "AWS secret (assignment)|aws_secret_access_key[ \\t]*[=:][ \\t]*[\"']?[A-Za-z0-9/+=]{40}[\"']?"
    "GitHub PAT|ghp_[A-Za-z0-9]{36}"
    "GitHub OAuth|gho_[A-Za-z0-9]{36}"
    "GitHub user-to-server|ghu_[A-Za-z0-9]{36}"
    "GitHub server-to-server|ghs_[A-Za-z0-9]{36}"
    "GitHub refresh|ghr_[A-Za-z0-9]{36}"
    "GitLab PAT|glpat-[A-Za-z0-9_-]{20,}"
    "OpenAI key (legacy)|sk-[A-Za-z0-9]{48}"
    "OpenAI key (project)|sk-proj-[A-Za-z0-9_-]{40,}"
    "Anthropic key|sk-ant-[A-Za-z0-9_-]{50,}"
    "Slack token|xox[baprs]-[A-Za-z0-9-]{10,}"
    "Private key block|-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----"
    "JWT|eyJ[A-Za-z0-9_-]{20,}\\.eyJ[A-Za-z0-9_-]{20,}\\.[A-Za-z0-9_-]+"
    "Postgres URL with password|postgres(ql)?://[^:/ ]+:[^@/ ]+@"
    "MongoDB URL with password|mongodb(\\+srv)?://[^:/ ]+:[^@/ ]+@"
    "MySQL URL with password|mysql://[^:/ ]+:[^@/ ]+@"
    "Generic password assignment|(password|passwd|pwd)[ \\t]*[=:][ \\t]*[\"'][^\"' \\t]{8,}[\"']"
    "Generic api_key assignment|api[_-]?key[ \\t]*[=:][ \\t]*[\"'][A-Za-z0-9_-]{20,}[\"']"
)

ALLOWLIST_RE='your-?[a-z_-]+|<[A-Z_]+>|\[[A-Z_]+\]|XXXX+|xxxx+|example|placeholder|fake|sample|REPLACE|TODO'

# --- Scan ---
found=0
files_scanned=0

is_text() {
    # heuristic: skip files that file(1) reports as binary
    if ! file -b --mime "$1" 2>/dev/null | grep -q "charset=binary"; then
        return 0
    fi
    return 1
}

for p in "${PATHS[@]}"; do
    [[ -f "$p" ]] || continue
    is_text "$p" || continue
    files_scanned=$((files_scanned + 1))

    for entry in "${PATTERNS[@]}"; do
        name="${entry%%|*}"
        regex="${entry#*|}"
        while IFS= read -r match; do
            [[ -n "$match" ]] || continue
            line_num="${match%%:*}"
            content="${match#*:}"
            # Skip if line contains an allowlist marker
            if echo "$content" | grep -qiE "$ALLOWLIST_RE"; then
                continue
            fi
            echo ""
            echo "✗ POTENTIAL SECRET in $p:$line_num"
            echo "  type:    $name"
            preview=$(echo "$content" | head -c 100)
            echo "  preview: ${preview}..."
            found=1
        done < <(grep -nEH "$regex" "$p" 2>/dev/null | sed "s|^$p:||")
    done
done

if (( found != 0 )); then
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  potential secrets detected — DO NOT COMMIT until resolved."
    echo ""
    echo "  • False positive? Add a placeholder marker on the same line"
    echo "    (e.g. 'example', '<TOKEN>', 'your-key-here')."
    echo "  • Real secret? Move to .env (gitignored) or a vault."
    echo "  • Override (only if certain): git commit --no-verify"
    echo "════════════════════════════════════════════════════════════"
    exit 1
fi

echo "✓ no secrets detected in $files_scanned file(s)"
exit 0
