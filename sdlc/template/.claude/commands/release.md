---
description: Post-G4 release helper — runs audit, secret scan, and review-prep, then drafts a conventional commit message + PR description. Prints them for the human; never commits or pushes _source/ repos.
argument-hint: [TICKET-ID]
---

# /release — Post-G4 Release Helper

Prepare the human's commit/PR for: $ARGUMENTS

Run AFTER Gate G4 approval for the ticket. This command only aggregates checks and drafts
text — **it never commits or pushes in `_source/` repos** (the human does). Committing the
workspace repo itself is allowed only if the human explicitly asks.

---

## Steps

1. **Load the ticket.** Read `tasks/tickets/$ARGUMENTS.md` — fail fast if missing. Note the
   target repo(s) (BE/FE/Mobile layer) and the linked US. Read
   `tasks/reviews/$ARGUMENTS-review.md` for the final review verdict + QC summary.

2. **Workspace consistency:** run `scripts/audit.sh`. Report FAILing sections; a FAIL here is
   a stop — fix or get explicit human acknowledgment before drafting the release text.

3. **Secret scan:** run `scripts/check-secrets.sh --all`. Any hit on files touched by this
   ticket is a hard stop.

4. **Review prep gates:** run `scripts/review-prep.sh <repo-name>` for each repo the ticket
   touched (names from `project.config.json`). Exit 1 (blocking) = stop; exit 2 (warnings) =
   include the warnings in the PR draft.

5. **Draft commit message:** run `scripts/commit-message.sh $ARGUMENTS` (add `--co-authored`
   if the human wants the Claude trailer). Print the output verbatim in a code block.

6. **Draft PR description** and print it in a code block:

   ```
   ## Summary
   [2-4 lines — what changed and why, from ticket title + AC]

   Ticket: $ARGUMENTS · Story: [US-NNN]

   ## Review & QC
   - Review: [final round verdict from tasks/reviews/$ARGUMENTS-review.md]
   - QC: [verdict + test summary]
   - Typecheck: PASS (review-prep) · Secret scan: clean · Audit: [PASS / acknowledged items]

   ## Doc Sync
   [applied doc updates from the ticket's Doc Sync Plan, or "auto-approve tier — none needed"]

   ## E2E
   [TC-E-NNN result, or "not mandatory — <reason recorded at G4>"]
   ```

7. **Hand off:** end with the exact commands the human runs themselves:

   ```
   cd _source/[repo]
   git checkout -b [type]/$ARGUMENTS-[slug]   # per knowledge/L0-global/git-workflow.md
   git add [files from ticket scope] && git commit -m "$(cd - >/dev/null; scripts/commit-message.sh $ARGUMENTS)"
   git push -u origin HEAD    # then open the PR with the description above
   ```

## Must not

- Run `git commit`, `git push`, or `gh pr create` in any `_source/` repo
- Proceed past a failing audit / secret scan / blocking review-prep without explicit human acknowledgment
