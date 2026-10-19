---
description: Reset session context when moving to another module — archives active-context and starts a fresh one.
argument-hint: [module]
---

# /switch-module — Context Reset

Target module: $ARGUMENTS

Protocol reference: `.agents/orchestration.md` §6. Prevents context pollution — the old module's legacy notes, tickets, and domain focus must not bleed into the new module's session. Run before starting work on a different module.

---

## Valid modules

Read `modules[]` from `project.config.json` and show the user the list (slug + br_prefix) **read from config** — never a hard-coded list. If `$ARGUMENTS` is not one of the configured slugs → stop and show the valid slugs. If `modules[]` is empty (`initialized: false`) → tell the human to run `/onboard` first.

---

## Steps

### 1 — Archive current context + reset to the fresh template

```bash
scripts/archive-active-context.sh [current-module] --reset
```

This archives `active-context.md` to `knowledge/L3-session/history/[YYYY-MM-DD]-[current-module].md` and resets it to the fresh template. **The script's embedded template is CANONICAL** — this command must not maintain or write its own copy of the template.

Before running, note the `language` value in the current active-context (to preserve in Step 2). If `active-context.md` does not exist, there is nothing to archive — ask the human to run `/onboard`, or produce the fresh file by borrowing the script's embedded template; never invent a different structure.

### 2 — Fill module-specific fields in the fresh template

Edit only these fields of the freshly reset `active-context.md` (leave the rest of the template untouched):
- Module: `[new-module]`
- Domain file ref: `knowledge/L1-domain/[new-module]-domain.md` (+ `module-integration-map.md`)
- Legacy scan status: result from Step 3
- **PRESERVE the `language` field** from the archived context (fallback: `project.config.json`)

### 3 — Legacy scan check

Does `knowledge/L2-legacy/scans/[new-module]-legacy-scan.md` exist? (`scripts/legacy-scan-freshness.sh [new-module]` also reports FRESH/STALE/MISSING.)

- Exists + fresh → note the path in active-context.
- Missing or stale → warn: `No fresh legacy scan for [module]. Run /legacy-scan [module] before any Build (Phase 4) work.`

### 4 — Confirm

```
Context switched to: [new-module]
Archived: knowledge/L3-session/history/[date]-[old-module].md
Legacy scan: [path + FRESH | warning]

Update "What I am working on" in active-context.md before running /ba, /build, or Build commands.
```

---

## When to run

| Situation | Run switch-module? |
|---|---|
| Starting work on a different module | ✅ Always |
| Continuing the same module next day | ❌ Just update active-context.md |
| Running /ba or /build for a feature in a different module | ✅ Before it |
| Reviewing a PR for a different module (read-only) | ❌ Not needed |
| Starting a legacy scan for a new module | ✅ Before /legacy-scan |
