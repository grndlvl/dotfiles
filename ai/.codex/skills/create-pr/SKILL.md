---
name: create-pr
description: Create a GitHub pull request for the current branch, detecting Zivtech ticket-prefix or Conventional Commits title format and default base branch. Use when the user asks to create or open a PR.
---

# Create PR

Read `../_shared/references/git-workflow-core.md`, then create a GitHub PR for the current branch.

Required behavior:

- Detect branch, ticket, base branch, upstream, existing PR, branch commits, and changed files.
- If a PR already exists, report its URL and do not create a duplicate.
- Push unpushed commits first, setting upstream when needed.
- Use a title under 70 chars matching the detected convention.
- Create a PR body with `Summary` and `Test plan`.
- Do not merge.
- Report PR URL, title, base branch, pushed state, and test plan.
