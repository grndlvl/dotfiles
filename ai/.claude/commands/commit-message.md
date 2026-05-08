---
description: "Draft a commit message without committing. Auto-detects format from history; pass a prefix arg to override (e.g., `/commit-message feat(auth)`)."
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git branch *)
---

# Zivtech Commit Message

## Current state
- Branch: !`git branch --show-current`
- Ticket: !`git branch --show-current | grep -oE '^[A-Z]+-[0-9]+' || echo "(none — branch does not match TICKET-123/desc convention)"`
- Status: !`git status --short`
- Staged: !`git diff --cached --stat`
- Unstaged: !`git diff --stat`
- Recent commits (convention ref): !`git log -10 --oneline`

## Conventions

Two conventions are common in Zivtech repos:

**Zivtech client work** — per `zivtech-development-workflow`:
- `TICKET-123: Brief description` (capitalized, imperative, < 72 chars)

**Zivtech tooling / library repos**:
- Conventional Commits — `feat(scope): description`, `fix(scope): ...`, `docs(scope): ...`

## Task

Draft a commit message based on the changes above. Output the message **only** — do not stage or commit.

1. **If `$ARGUMENTS` begins with a prefix-shaped token** (e.g., `ZIV-456`, `feat(auth)`, `fix:`), use it as the prefix.
2. **Otherwise**, match the convention inferred from recent commits above:
   - Zivtech client → use the extracted ticket; if missing, flag at the top of your output.
   - Conventional Commits → pick appropriate `type(scope): description`.
   - Mixed or unclear → ask the user.

$ARGUMENTS
