# Doc Sync Contract — keep documentation 100% in sync with source code
> Loaded by: Dev Agent, FE Dev Agent, Mobile Dev Agent, SA Agent, /review.
> Trigger: any code change in `_source/` OR any change to architecture artifacts (api-contracts, db-schema, state-machines, ADRs, feature-map).
> Hard rule: **doc updates need human approval at the gate (G4 for Build, G2 for SA) — except the Auto-approve tier (§Auto-approve), which the agent applies itself and lists in the gate report.**

---

## 1. Why this contract exists

The agentic workspace works only if every doc reflects the current state of source. If a row in `architecture/feature-map/<module>.md` is stale, the next agent skips a source scan based on a lie. If a domain entity's columns drift from the actual table, SA designs against fiction.

This contract prevents drift by making doc sync a **mandatory final step** of every code-touching pass — and by making it **human-approved** so silent doc rewrites never happen.

---

## 2. Who must follow it

| Agent | Triggers doc sync? |
|---|---|
| Dev Agent (`/dev`) | Yes — on any code edit in `_source/[BE_REPO]/` |
| FE Dev Agent (`/fe`) | Yes — on any code edit in `_source/[FE_REPO]/` |
| Mobile Dev Agent (`/mobile`) | Yes — on any code edit in `_source/[MOBILE_REPO]/` |
| SA Agent (`/sa`) | Yes — on any change to api-contracts, db-schema, state-machines, ADRs |
| `/review` | Yes — must verify the pass's Doc Sync Plan exists (or auto-approve tier was applied) before declaring PASS |
| BA, Planner, QC, brainstorm, legacy-scan, switch-module | No — these agents do not write code or contracts |

---

## 3. Code-change → doc-update mapping

Use this table to build the **Doc Sync Plan** at the end of every pass. Every check is "if the code change touched X, then doc Y is suspect — list it."

### Backend code changes (`_source/[BE_REPO]/`)

| Code change | Affected doc | What to update |
|---|---|---|
| New / renamed / removed endpoint | `architecture/feature-map/<module>.md` | Add / update / mark `[REMOVED]` row |
| New / changed request or response shape | `architecture/api-contracts/v1/<feature>.yaml` | Update schema, examples |
| New / changed table / column / index | `architecture/db-schema/entities/<entity>.entity.design.*` | Update entity design; the migration itself is generated in `_source/` by Dev |
| New / changed entity | `knowledge/L1-domain/<module>-domain.md` | Update §2 Core Entities table |
| New / changed business rule (validation, threshold, allowed state) | `knowledge/L1-domain/<module>-domain.md` | Update §4 Business Rules |
| New / changed state transition | `architecture/db-schema/state-machines/<entity>-states.md` AND `knowledge/L1-domain/<module>-domain.md` §3 State Machine | Update both |
| New event emitter or event consumer | `knowledge/L1-domain/module-integration-map.md` AND `knowledge/L1-domain/<module>-domain.md` §5/§6 | Add to event catalog + emitted/consumed table |
| Cross-module service call added/removed | `architecture/feature-map.md` §6 AND each affected `architecture/feature-map/<module>.md` "Cross-module touchpoints" section | Mirror in both places |
| New domain term used in code | `knowledge/L0-global/project-glossary.md` | Add row |
| Naming convention used that isn't in the global rule | `knowledge/L0-global/naming-convention.md` | Add rule |
| Legacy table / endpoint touched | `knowledge/L2-legacy/scans/<module>-legacy-scan.md` | Update §7 Action Plan to mark item done |
| External-system sync added / removed for an endpoint | `architecture/feature-map/<module>.md` (External Sync column) AND `architecture/feature-map.md` §6 if cross-module | Update both |
| Permission added / changed on an endpoint | `architecture/feature-map/<module>.md` (Permission column) | Update row |
| Any of the above | `architecture/feature-map.md` §2 Maintenance | Refresh `Last reviewed (date)` and `Last reviewed against [BE_REPO] commit` |
| Test added that covers a cross-module flow | `tests/regression-map.md` | Add to "When you modify X → also test" rules |

### Frontend code changes (`_source/[FE_REPO]/`)

| Code change | Affected doc | What to update |
|---|---|---|
| New / renamed / removed page | `architecture/feature-map/<module>.md` | Add / update / mark `[REMOVED]` row (FE Page column) |
| New / changed permission gate on a page | `architecture/feature-map/<module>.md` (Permission column) | Update row |
| New cross-module FE adapter (module A consuming module B's API) | `architecture/feature-map.md` §6 AND each affected module file | Mirror touchpoint in both places |
| Layer change (BE → BE+FE because a page was added) | `architecture/feature-map/<module>.md` (Layer column) | Update row |
| Any FE change | `architecture/feature-map.md` §2 Maintenance | Refresh `Last reviewed against [FE_REPO] commit` |

### SA artifact changes (`/sa`)

SA already produces docs as primary artifacts. The doc-sync rule for SA is to also propagate the change into:
- `architecture/feature-map/<module>.md` — feature row
- `architecture/feature-map.md` — index header + §6 cross-module rows
- `knowledge/L1-domain/<module>-domain.md` — entity / state machine / BR / events sections
- `knowledge/L1-domain/module-integration-map.md` — event catalog (if new cross-module event)
- Mirror cross-module touchpoints into every affected per-module feature-map file

---

## Auto-approve tier — trivial propagation, no human stop

The agent applies the doc updates itself — no plan approval — when **ALL** of the following hold:

1. Total doc diff ≤ 20 lines
2. No contract, domain-rule, or business-rule content changes — nothing in api-contracts, domain.md §4, or integration-map event payloads
3. Every target is propagation-only: indexes (`_index.md`), summaries (`*.summary.md`), feature-map SHA/freshness rows, kanban status lines

When the tier applies:
- The agent makes the updates directly and **lists them in the G4 report** ("Docs auto-synced: [files]")
- Batching within one ticket is allowed — accumulate trivial propagations and apply once at the end of the pass
- `/review` still verifies the listed updates match the diff

Anything that fails any condition → full plan + human approval at the gate (§4 below).

---

## 4. The protocol — full plan + gate approval

After writing code (or changing contracts), before declaring handoff, the agent MUST output a Doc Sync Plan for everything above the auto-approve tier. The plan is part of the gate package (G4 for Build agents, G2 for SA) — approval happens at that single gate, not as a separate mid-pass stop.

### Step A — Build the plan

Walk the table in §3 against the actual code change. List every doc that needs an update with a one-line description of the change.

### Step B — Output the plan in this exact shape

```
=== DOC SYNC PLAN — TICKET-[ID] ===

Code changes detected:
  - [file path]: [one-line summary]
  - [file path]: [one-line summary]

Documentation updates required:
  [1] architecture/feature-map/<module>.md
      → Add row: <FEATURE-ID> "<Feature name>" (<endpoint or page>)
  [2] knowledge/L1-domain/<module>-domain.md
      → §2 Core Entities: add column <name> to <Entity>
  [3] architecture/api-contracts/v1/<file>.yaml
      → Add response field <name>
  [4] architecture/feature-map.md
      → Refresh §2 Maintenance: Last reviewed against [BE_REPO] = <new SHA>

Approval needed before any of the above is written.

Reply with:
  - "approve all"           → I update every item above
  - "approve [1,3]"          → I update only listed items, skip the rest
  - "skip"                   → I write nothing; you'll handle docs manually
  - "ask: <question>"        → I answer your question, then re-issue the plan
```

### Step C — Wait for human reply

Do not proceed past this point. Do not pre-write any doc edit. Do not partially apply.

### Step D — On approval

- "approve all" → execute every item, then output a confirmation listing what was updated.
- "approve [N,M]" → execute only the listed items; explicitly note which items were skipped and why (so the next pass / `/review` knows there's a known gap).
- "skip" → record the skipped plan in the handoff so `/review` can flag it.
- Hooks/lints failing on a doc edit → revert the edit, re-issue the plan to the human with the failure noted.

### Step E — Final handoff signal

Only after the plan is resolved, emit the normal handoff signal (e.g. "Next command: /review [TICKET-ID]"). Include a one-line **"Docs synced: yes / partial (items skipped: …) / no (user opted out)"** so the next agent and `/review` see the state at a glance.

---

## 5. /review enforcement

`/review` MUST verify Doc Sync was completed before declaring PASS. Add this checklist item to every review:

- [ ] Pass output a Doc Sync Plan OR listed auto-approved updates in its report
- [ ] All approved items in the plan are reflected in the docs (or a skip is documented)
- [ ] No "stealth" doc edits — every doc change in the diff matches an approved plan item or a listed auto-approve item

If the pass produced neither a Doc Sync Plan nor an auto-approve list (and code changed), `/review` returns BLOCKING: "Doc sync skipped. Re-run /dev, /fe, or /mobile to produce the plan."

---

## 6. What NOT to do

- **Do not silently update docs outside the auto-approve tier.** Anything touching contracts, domain rules, or BRs needs the plan + gate approval — the human sees every meaningful divergence between code and docs. Auto-approved items must still be listed in the gate report.
- **Do not batch across tickets.** One ticket = one plan (auto-approve batching within a single ticket is fine). Don't accumulate doc-debt across tickets.
- **Do not skip the freshness header.** Even when no row changes, refresh `Last reviewed (date)` + commit SHA in `architecture/feature-map.md` §2 — that's what tells future agents the map can be trusted.
- **Do not edit docs to match buggy code.** If code is wrong and the doc is right, fix the code instead. The plan should reveal the conflict, not paper over it.
- **Do not move "approve all" into a default.** The human must reply each time. Implicit approval is how docs drift.

---

## 7. Quick reference — minimum plan items per change type

| If you changed… | Minimum plan must include |
|---|---|
| Any BE endpoint | feature-map/<module>.md row + api-contract yaml + feature-map.md freshness |
| Any FE page | feature-map/<module>.md row + feature-map.md freshness |
| Any DB table | migration sql + domain.md §2 entities + feature-map.md freshness |
| Any business rule | domain.md §4 BR table + feature-map.md freshness |
| Any cross-module call | feature-map.md §6 + every affected feature-map/<module>.md touchpoints + feature-map.md freshness |
| Any state transition | state-machines/<entity>.md + domain.md §3 + feature-map.md freshness |
| Any event | module-integration-map.md + domain.md §5/§6 + feature-map.md freshness |
| A doc-only fix (typo, clarification) | The doc itself — auto-approve tier applies if conditions in §Auto-approve hold |
