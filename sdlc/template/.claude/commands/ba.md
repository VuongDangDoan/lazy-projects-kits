---
description: Phase 1 — Business Analysis. BA Agent writes SRS section + user stories, validates, stops at Gate G1.
argument-hint: [feature description]
---

# /ba — Phase 1 · Business Analysis

Run the BA Agent on: $ARGUMENTS

Flow reference: `.agents/orchestration.md` §1 Phase 1. This command produces the Phase 1 artifacts and stops at **Gate G1** for human approval.

---

## Pre-flight

1. Read `knowledge/L3-session/active-context.md` — module + agreed approach.
   - **If the file is missing:** do NOT invent context. Recreate the fresh template (canonical template is embedded in `scripts/archive-active-context.sh --reset`) or ask the human to run `/onboard`. Never proceed on guessed context.
2. Read `project.config.json` — module list (slug + br_prefix) and `language`. Never hard-code module names.
3. Read `.agents/roles/ba.md` — the role file owns the detailed steps (incl. Step 0 inline brainstorm and clarifying questions). Follow it; do not improvise.
4. Read `.agents/contracts/user-story.schema.md` (v2) — output contract.

On-demand only: `docs/brd.md`, `docs/frd/_index.md`, `knowledge/L1-domain/[module]-domain.summary.md`, `knowledge/L1-domain/module-integration-map.md`.

---

## Execution

1. Follow the BA role flow from `.agents/roles/ba.md`.
2. Allocate each user-story ID by running `scripts/next-id.sh us` — never eyeball directories for the next number.
3. Write the Phase 1 artifacts:
   - `docs/srs/[module]-srs.md` — per-module Software Requirements Specification: create it, or append a section for this feature
   - `docs/user-stories/US-NNN.md` — one file per story, per schema v2
   - `docs/user-stories/_index.md` — updated index
   - `docs/prototypes/[feature].html` — OPTIONAL: self-contained low-fi HTML wireframe, only when the feature has non-obvious UI
4. Validate: run `scripts/validate-us.py docs/user-stories/US-NNN.md` for every story written — must exit 0 before declaring done. On failure, fix and re-run.
5. Record BA decisions in `knowledge/L3-session/active-context.md`.

---

## Gate G1 handoff

End the response with:

```
Phase 1 artifacts ready: SRS §[section], US-NNN[, prototype].
validate-us.py: PASS
Awaiting G1 approval. Next after approval: /sa US-NNN
```

Do not chain into Phase 2 — G1 approval is a human decision.
