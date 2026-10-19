---
description: Plain-language progress dashboard — current phase, gate, tickets, and suggested next command. Read-only.
argument-hint: (no arguments)
---

# /status — Project Progress Dashboard

Read-only, token-cheap, always safe to run.

---

## What to read (token discipline — mandatory)

1. `project.config.json` — project name + `language`
2. `knowledge/L3-session/active-context.md` — current module, active ticket, deployment info
3. `tasks/kanban.md` — tickets by status
4. `tasks/tickets/`, `docs/user-stories/`, `tasks/reviews/`, `architecture/api-contracts/v1/` — **count files and title-scan only**; never read full ticket/US files
5. `docs/brd.md` — **first 20 lines only** (name + goals)

**Missing is not an error:** if any directory or file above doesn't exist, treat it as 0 items / "not started" and continue. If active-context.md is missing, show the dashboard from what exists and note: "No active context — run /onboard or /switch-module."

---

## Derive current Phase + Gate from artifacts present

- US files exist, no matching api-contract → Phase 1 done, at G1 / entering Phase 2
- api-contract + entity design exist, no tickets → Phase 2 done, at G2 / entering Phase 3
- Tickets in "To Do" → Phase 3 done, at G3 / entering Phase 4
- Tickets "In Progress" or files in `tasks/reviews/` → Phase 4 (Build) — reviews present means the self-audit loop has run
- `tests/e2e/cases/` has TC-E files for the active work → Phase 5 (E2E)
- Nothing yet → Phase 0: run /onboard or /build

Show it as one line: `Phase: [N] — [name] · Next gate: G[N]`.

---

## Output — single template + label glossary

Read `language` from `project.config.json`. Use ONE template; when `language: vi`, swap labels using the glossary below — do not maintain two duplicated blocks.

```
## Project Status — [PROJECT_NAME] · [TODAY]
Phase: [N] — [name] · Next gate: G[N]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DONE ([N])           ✅ [Feature/US title — US-NNN]
IN PROGRESS ([N])    🔄 [Ticket title — TICKET-NNN ([module])]
REVIEW / QC ([N])    🔍 [Ticket title — TICKET-NNN]
BACKLOG ([N])        📋 [Ticket title — TICKET-NNN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current module: [module] · Active ticket: [TICKET-NNN or None]
Deployment: [platform + URL from active-context, else "Not configured — run /devops"]

Next:
  [suggest by the next actionable ticket's Layer:]
  /dev TICKET-NNN (Layer: BE) | /fe TICKET-NNN (FE) | /mobile TICKET-NNN (MOBILE)
  /build "[feature]" — add a new feature
```

**Label glossary (vi):** Project Status → Tiến độ dự án · Phase → Giai đoạn · Next gate → Gate kế tiếp · DONE → ĐÃ HOÀN THÀNH · IN PROGRESS → ĐANG THỰC HIỆN · REVIEW / QC → ĐANG REVIEW / KIỂM THỬ · BACKLOG → CHƯA BẮT ĐẦU · Current module → Module hiện tại · Active ticket → Ticket đang làm · Deployment → Triển khai · "Not configured — run /devops" → "Chưa cấu hình — chạy /devops" · Next → Lệnh tiếp theo · "add a new feature" → "thêm tính năng mới"

---

## Derived status (when kanban is empty or missing)

- Files in `tasks/tickets/` = BACKLOG minimum
- US files marked "Status: Done" in `_index.md` = DONE
- active-context "Active Ticket" field = IN PROGRESS

## Skip conditions

None — /status is always safe to run.
