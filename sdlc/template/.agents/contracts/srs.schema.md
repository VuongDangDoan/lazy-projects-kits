# SRS Schema v1.0
> Per-module Software Requirements Specification — BA Agent output (Phase 1).
> File: `docs/srs/[module]-srs.md` — one file per module, created on first touch, appended per feature.
> The SRS is the **narrative complement** to atomic US files, not a duplicate: it gives the
> connected story of the module. Link to US files — do NOT copy ACs into the SRS.

---

## Template

```markdown
# SRS — [Module Name]

**Module:** [module slug from project.config.json]
**Updated:** YYYY-MM-DD
**User stories:** US-NNN, US-NNN, ...

---

## 1. Overview & Actors

[2-5 sentences: what this module does and why it exists.]

| Actor | Role in this module |
|---|---|
| [role] | [what they do here] |

---

## 2. Functional Requirements

> One subsection per feature. FR-IDs: `FR-[MODULE]-NNN` where [MODULE] is the module's
> BR prefix from project.config.json. Each FR maps to a US and its ACs — link, don't copy.

### 2.1 [Feature name]

| ID | Requirement (1-2 lines) | US | ACs |
|---|---|---|---|
| FR-[MODULE]-001 | [what the system must do] | US-NNN | AC1, AC2 |

---

## 3. Non-Functional Requirements

> ONLY deltas from `docs/brd.md` — module-specific performance, volume, or availability
> constraints. If none: "None beyond BRD."

---

## 4. Open Questions

- [question — owner — or "None"]
```

---

## Rules

- **BA appends or edits its own feature sections — never rewrites sections owned by earlier passes.**
  A later pass may correct a stale FR row only if the linked US changed (note the US ref).
- Header `Updated` + `User stories` list refreshed on every BA pass that touches the file.
- FR-IDs are per-module sequential and stable — never reuse after removal (strike the row, keep the ID).
- Every FR row must link to an existing US; a US may back multiple FRs.
- G1 reviews the SRS section together with the US files — a Phase-1 handoff without the SRS section is incomplete.
