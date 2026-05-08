---
description: "Stage and commit. Auto-detects Zivtech (TICKET-123:) vs Conventional Commits format; pass a prefix arg to override (e.g., `/commit ZIV-456`)."
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git branch *)
---

# Zivtech Commit

## Current state
- Branch: !`git branch --show-current`
- Ticket: !`git branch --show-current | grep -oE '^[A-Z]+-[0-9]+' || echo "(none — branch does not match TICKET-123/desc convention)"`
- Status: !`git status --short`
- Staged: !`git diff --cached --stat`
- Unstaged: !`git diff --stat`
- Recent commits (convention ref): !`git log -10 --oneline`

## Conventions

Two conventions are common in Zivtech repos — pick whichever matches the recent commits above:

**Zivtech client work** — per `zivtech-development-workflow`:
- Format: `TICKET-123: Brief description` (capitalized, imperative, < 72 chars)
- Branches named `TICKET-123/short-desc`
- Required on client projects

**Zivtech tooling / library repos** (this skills repo, internal infra, etc.):
- Conventional Commits — `feat(scope): description`, `fix(scope): ...`, `docs(scope): ...`
- No ticket prefix
- Branches may be `main` or feature branches

## Task

Commit the current changes, picking the prefix as follows:

1. **If `$ARGUMENTS` begins with a token that looks like a commit prefix** — e.g., `ZIV-456`, `feat(auth)`, `fix:`, `docs(setup)`, `chore` — use that token as the prefix. Anything after the prefix in `$ARGUMENTS` is additional context for the message body.
2. **Otherwise**, infer the convention from recent commits above:
   - `TICKET-123:` style in history → Zivtech client. Prefix with the ticket extracted from the branch. If no ticket was extracted, stop and ask.
   - `feat(...)` / `fix(...)` style → Conventional Commits. Use `type(scope): description`. No ticket prefix.
   - Mixed or unclear → stop and ask the user which to use.
3. Stage specific files; do not use `git add .` or `git add -A`.
4. Use HEREDOC for the commit message so multi-line bodies render correctly.

$ARGUMENTS
