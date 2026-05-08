---
name: commit-message
description: Draft a git commit message without staging or committing, using Zivtech ticket-prefix or Conventional Commits detection plus the workspace Lore commit protocol. Use when the user asks for a commit message or wants to preview a commit message.
---

# Commit Message

Read `../_shared/references/git-workflow-core.md`, then draft a commit message only.

Required behavior:

- Do not stage files.
- Do not commit.
- Gather enough diff and history context to infer the convention.
- Follow the Lore commit protocol.
- Output the commit message only unless a blocker requires a question.
