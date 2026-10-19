#!/usr/bin/env bash
# new-item.sh <slug> — start a work item: research/<slug>/ from templates/brief.md, point
# context/active.md at it and add a line to research/_index.md. A slug already used on this
# branch or on any origin/* branch (another factory's task) gets -2, -3… so items never collide.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
area=research
slug="${1:-}"
[[ "$slug" =~ ^[a-z0-9][a-z0-9-]{0,39}$ ]] || {
    echo "new-item: slug phải là chữ thường không dấu, số, gạch ngang (≤ 40 ký tự): '$slug'" >&2; exit 2; }

taken() { # taken <dir> — exists here or on a remote branch
    [[ -e "$1" ]] && return 0
    local ref
    while read -r ref; do
        git cat-file -e "$ref:$1" 2>/dev/null && return 0
    done < <(git for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null)
    return 1
}
dir="$area/$slug"; n=2
while taken "$dir"; do dir="$area/$slug-$n"; n=$((n + 1)); done

mkdir -p "$dir"
cp templates/brief.md "$dir/brief.md"
cat > context/active.md <<EOT
# Việc đang làm
Thư mục: $dir
Giai đoạn: scope

## Ghi chú cho phiên sau
EOT
printf '| [%s](%s/) | %s | phạm vi — chờ G1 | |\n' "${dir#"$area"/}" "${dir#"$area"/}" "$(date +%Y-%m-%d)" >> "$area/_index.md"
echo "$dir"
