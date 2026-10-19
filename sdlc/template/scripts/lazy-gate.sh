#!/usr/bin/env bash
# lazy-gate.sh <phase> — script gate the Lazy Bot factory runs after each phase, before asking
# the owner to approve (see .lazy/kit.yaml). Exit 0 = artifacts of the phase are present and
# valid; anything else = the phase is redone with this output (last 200 lines).
#
# Runs in the task worktree, without credentials or network.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

phase="${1:-}"
shopt -s nullglob

need() { # need <message> <files…>  (files may be empty)
    local msg="$1"; shift
    (( $# > 0 )) || { echo "✗ $msg"; exit 1; }
}

case "$phase" in
    ba)
        us=(docs/user-stories/US-*.md)
        need "Chưa có user story nào trong docs/user-stories/ — giai đoạn BA phải tạo US-NNN.md" ${us[@]+"${us[@]}"}
        python3 scripts/validate-us.py "${us[@]}"
        ;;
    sa)
        api=(architecture/api-contracts/v1/*.yaml architecture/api-contracts/v1/*.yml)
        ent=(architecture/db-schema/entities/*)
        need "Chưa có API contract / entity design — giai đoạn SA phải tạo trong architecture/" ${api[@]+"${api[@]}"} ${ent[@]+"${ent[@]}"}
        if (( ${#api[@]} > 0 )); then python3 scripts/validate-api-contract.py "${api[@]}"; fi
        ;;
    planner)
        tk=(tasks/tickets/TICKET-*.md)
        need "Chưa có ticket nào trong tasks/tickets/ — giai đoạn Planner phải tạo TICKET-NNN.md" ${tk[@]+"${tk[@]}"}
        python3 scripts/validate-ticket.py "${tk[@]}"
        ;;
    build)
        name=$(python3 -c 'import json;print(json.load(open("project.config.json"))["repos"]["be"]["name"])')
        files=$(find "_source/$name" -type f ! -name .gitkeep 2>/dev/null | head -1)
        [[ -n "$files" ]] || { echo "✗ _source/$name/ chưa có code — giai đoạn Build phải viết code ở đó"; exit 1; }
        todo=$(grep -l '^\*\*Status:\*\* \(Todo\|In Progress\)' tasks/tickets/TICKET-*.md 2>/dev/null)
        [[ -z "$todo" ]] || { echo "✗ Còn ticket chưa xong:"; echo "$todo"; exit 1; }
        scripts/typecheck-source.sh "$name"
        ;;
    *)
        echo "lazy-gate: giai đoạn lạ: '$phase' (ba|sa|planner|build)" >&2; exit 2 ;;
esac
