<!-- LAZY-FACTORY-MODE: written by scripts/lazy-init.sh — keep at the top of CLAUDE.md -->
# 0. Running inside Lazy Bot factory — read first, these rules override anything below

This workspace is operated by a **Lazy Bot factory**: each task runs in its own git worktree of
this repo, one phase (stage) per session, and the owner approves every phase gate on Telegram.

- **The code lives in this repo** under `_source/{{NAME}}/` — a real directory, not a symlink.
  Ignore every instruction below about creating `_source/` symlinks or cloning sibling repos.
- **Never `git commit`, `git push` or open PRs.** The factory commits your work (WIP + delivery)
  and opens the pull request. "Commits are made by the human" below means: by the factory.
- **There is no human at the terminal.** When a step below says to ask the human, wait for
  approval or stop at a gate:
  - real question you cannot resolve from the repo → call the factory MCP tool `ask_human`
    (it reaches the owner on Telegram) and continue with the answer;
  - the phase reached its gate ("Awaiting G1 approval", "stops at G2", …) → call the factory
    MCP tool `stage_done` with a 3–6 line summary of what was produced (file paths + IDs).
    Do NOT wait for approval in the same session: the factory asks the owner and starts the
    next phase in a new session.
- **Approvals already given:** if the opening message carries owner feedback for a phase, apply it
  and redo only that phase. Gates of earlier phases are approved (they are merged into this branch).
- One phase per session: do the phase in the opening message, nothing beyond its gate.
- Keep `knowledge/L3-session/active-context.md` updated — the next phase's session starts from it.
