---
description: "Commit and push. Auto-detects format from history; pass a prefix arg to override (e.g., `/commit-push ZIV-456`)."
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git push *) Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git branch *) Bash(git rev-parse *)
---

# Zivtech Commit and Push

## Current state
- Branch: !`git branch --show-current`
- Ticket: !`git branch --show-current | grep -oE '^[A-Z]+-[0-9]+' || echo "(none — branch does not match TICKET-123/desc convention)"`
- Tracking: !`git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no upstream"`
- Status: !`git status --short`
- Staged: !`git diff --cached --stat`
- Unstaged: !`git diff --stat`
- Recent commits (convention ref): !`git log -10 --oneline`

## Conventions

Two conventions are common in Zivtech repos:

**Zivtech client work** — per `zivtech-development-workflow`:
- `TICKET-123: Brief description` (capitalized, imperative, < 72 chars)
- Use rebase, not merge — `git pull --rebase`, never `git merge`

**Zivtech tooling / library repos**:
- Conventional Commits — `feat(scope): description`, `fix(scope): ...`

Use `git push -u origin <branch>` if no upstream is set.

## Task

1. **If `$ARGUMENTS` begins with a prefix-shaped token** (e.g., `ZIV-456`, `feat(auth)`, `fix:`), use it as the commit prefix.
2. **Otherwise**, match the repo's convention (see recent commits above):
   - Zivtech client (`TICKET-123:` style) → prefix with ticket from branch; ask if missing.
   - Conventional Commits (`feat(...)` / `fix(...)`) → use `type(scope): description`; no ticket prefix.
   - Mixed / unclear → stop and ask.
3. Stage specific files; do not use `git add .` or `git add -A`.
4. Commit with a HEREDOC message.
5. Push with `-u` if no upstream.

$ARGUMENTS
