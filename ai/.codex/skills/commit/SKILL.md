---
name: commit
description: Stage and commit current git changes using Zivtech ticket-prefix or Conventional Commits detection plus the workspace Lore commit protocol. Use when the user asks to commit, make a commit, save changes to git, or run the commit workflow.
---

# Commit

Read `../_shared/references/git-workflow-core.md`, then commit the current changes.

Required behavior:

- Gather state and infer the commit convention before staging.
- Stage specific files only.
- Split unrelated concerns into separate commits.
- Use the Lore commit protocol.
- Verify with `git status --short` and `git log -1 --stat`.
- Report commit hash, subject, files committed, and verification evidence.
