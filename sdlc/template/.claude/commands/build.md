---
description: Nontech orchestrator — runs Phases 1→2→3 (BA → SA → Planner) with plain-language checkpoints at Gates G1, G2, G3.
argument-hint: [feature description in any language]
---

# /build — Pipeline Orchestrator (Nontech Mode)

Input: $ARGUMENTS

Chains Phase 1 (BA) → Phase 2 (SA) → Phase 3 (Planner) in one flow for non-technical users. The three checkpoints ARE Gates G1, G2, G3 from `.agents/orchestration.md` §1 — /build is **by design** consistent with orchestration §7 (human gates sit at phase boundaries); it only phrases the gates in plain language. Tech users who want step-level control use `/ba` `/sa` `/planner` directly.

---

## Pre-flight

1. Read `project.config.json` — project name, modules, and `language` (`vi` / `en`). This sets the checkpoint language.
2. Read `knowledge/L3-session/active-context.md`.
   - **If missing:** do not invent context — recreate the fresh template (canonical in `scripts/archive-active-context.sh --reset`) or ask the user to run `/onboard` (plain language: "workspace not set up yet").
3. If active-context shows in-progress tickets → warn (in the configured language): "There are unfinished tickets: [IDs]. /build will create new tickets in parallel. Continue? (yes / có / ok)".
4. **Never silently truncate a long description.** If $ARGUMENTS is very long, summarize it into key points, show the summary, and ASK the user to confirm it before starting Phase 1.

---

## Checkpoint protocol (applies at G1, G2, G3)

One compact template per language — fill in phase-specific content, do not duplicate whole sections:

```
EN:  ## [Phase name] complete — Gate G[N]
     [plain-language summary bullets]
     Files: [paths]
     Continue? (yes/ok) · Fix something: "fix: [what to change]" · Stop: "no"

VI:  ## [Tên giai đoạn] hoàn tất — Gate G[N]
     [tóm tắt dễ hiểu]
     Files: [paths]
     Tiếp tục? (có/yes/ok) · Cần sửa: "sửa: [điều cần thay đổi]" · Dừng: "không"
```

**Accept tokens — identical at all 3 checkpoints:** `yes`, `có`, `ok` (any casing) → gate approved, run the next phase.
**Decline:** `no` / `không` → stop; artifacts stay on disk; tell the user they can re-run /build later.
**Correction path — every checkpoint has one:** `fix: …` / `sửa: …` → re-run THAT phase with the correction applied, then re-present the same checkpoint. Stay in nontech mode — NEVER tell the user to run /ba, /sa, or /planner themselves.

---

## Phase 1 — Business Analysis (→ Gate G1)

Run the BA pass with the same mechanics as `/ba` (role `.agents/roles/ba.md`, ID via `scripts/next-id.sh us`, `scripts/validate-us.py` must exit 0).

Outputs: SRS section (`docs/srs/[module]-srs.md`), `docs/user-stories/US-NNN.md` + `_index.md`, optional prototype `docs/prototypes/[feature].html`.

Checkpoint G1 summary: the feature, who uses it, what it can do (ACs in plain language), what is out of scope; link the US file and prototype if produced.

## Phase 2 — Architecture (→ Gate G2)

Run the SA pass with the same mechanics as `/sa` (role `.agents/roles/sa.md`, `scripts/validate-api-contract.py` must exit 0).

Outputs: `architecture/api-contracts/v1/[feature].yaml` (with x-dev-notes) + `architecture/db-schema/entities/[entity].entity.design.ts` (+ state machine / ADR when triggered). **No SQL migration files** — migrations are generated from the entity design during the Build phase.

Checkpoint G2 summary: what the database will store, what the API can do (plain language), who has view / create-edit / delete permissions.

## Phase 3 — Planning (→ Gate G3)

Run the Planner pass with the same mechanics as `/planner` (role `.agents/roles/planner.md`, IDs via `scripts/next-id.sh ticket`, `scripts/validate-ticket.py` must exit 0).

Outputs: `tasks/tickets/TICKET-NNN.md` + updated `tasks/kanban.md` (sprint file only if the team uses sprints).

Checkpoint G3 summary: N pieces of work, execution order, rough size of each.

---

## After G3 approval

Tell the user in plain language that analysis, design, and planning are done, and the next step is the **Build phase**, where code gets written per ticket:

```
EN:  Ready to build! Next step — run per ticket, matching its Layer:
       /dev TICKET-NNN     ← server code (BE)
       /fe TICKET-NNN      ← web interface (FE)
       /mobile TICKET-NNN  ← mobile app (MOBILE)
     Use /status anytime to see overall progress.

VI:  Sẵn sàng viết code! Bước tiếp theo — chạy theo Layer của từng ticket:
       /dev TICKET-NNN     ← code phần server (BE)
       /fe TICKET-NNN      ← code giao diện web (FE)
       /mobile TICKET-NNN  ← code ứng dụng mobile (MOBILE)
     Dùng /status để xem tiến độ tổng thể bất cứ lúc nào.
```

---

## Error handling

- **BA cannot produce a valid US** → stop at Phase 1, ask (in plain language) for a more specific description.
- **SA blocked** (missing domain knowledge, no module match) → stop at Phase 2, explain the blocker in plain language and ask the user for the missing information, then re-run Phase 2 with it — do not send the user to /sa.
- **Planner produces many tickets** → normal behavior for a large feature, not an error.
