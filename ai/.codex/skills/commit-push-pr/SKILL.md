---
name: commit-push-pr
description: Full git ship workflow: commit current changes, push the branch, and create a GitHub PR using Zivtech ticket-prefix or Conventional Commits detection plus the workspace Lore commit protocol. Use when the user asks to commit, push, and create a PR.
---

# Commit Push PR

Read `../_shared/references/git-workflow-core.md`, then commit current changes, push the branch, and create a GitHub PR.

Required behavior:

- Gather state and infer convention before staging.
- Stage specific files only.
- Split unrelated concerns into separate commits.
- Use the Lore commit protocol.
- Push after commit succeeds; set upstream when needed.
- If a PR already exists, report its URL and do not create a duplicate.
- Create a PR body with `Summary` and `Test plan`.
- Do not merge.
- Verify with `git status --short`, `git log -1 --stat`, and `gh pr view --json url,title,baseRefName,headRefName`.
- Report commit hash, pushed branch/upstream, PR URL, title, and verification evidence.
