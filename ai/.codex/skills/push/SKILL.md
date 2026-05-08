---
name: push
description: Push the current git branch to its remote, setting upstream when needed and avoiding unsafe force-pushes. Use when the user asks to push, push this branch, or publish commits.
---

# Push

Read `../_shared/references/git-workflow-core.md`, then push the current branch.

Required behavior:

- Detect current branch and upstream.
- Show unpushed commits before pushing when possible.
- Use `git push -u origin <branch>` if no upstream exists.
- Use `--force-with-lease` only when the user explicitly requested a force push.
- Report branch, upstream, pushed commits, and resulting remote status.
