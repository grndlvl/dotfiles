---
name: commit-push
description: Commit current git changes and push the branch using Zivtech ticket-prefix or Conventional Commits detection plus the workspace Lore commit protocol. Use when the user asks to commit and push.
---

# Commit Push

Read `../_shared/references/git-workflow-core.md`, then commit current changes and push the branch.

Required behavior:

- Gather state and infer the commit convention before staging.
- Stage specific files only.
- Split unrelated concerns into separate commits.
- Use the Lore commit protocol.
- Push after commit succeeds; set upstream when needed.
- Verify commit and push state.
- Report commit hash, pushed branch/upstream, files committed, and verification evidence.
