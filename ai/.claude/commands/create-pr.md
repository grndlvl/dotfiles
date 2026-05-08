---
description: "Open a GitHub PR. Auto-detects format from history; pass a prefix to override (e.g., `/create-pr ZIV-456`). Detects default base branch."
disable-model-invocation: true
allowed-tools: Bash(git push *) Bash(git log *) Bash(git diff *) Bash(git branch *) Bash(git rev-parse *) Bash(git symbolic-ref *) Bash(gh pr create *) Bash(gh pr view *)
---

# Zivtech Create PR

## Current state
```!
BRANCH=$(git branch --show-current)
TICKET=$(echo "$BRANCH" | grep -oE '^[A-Z]+-[0-9]+' || echo "")
BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')
BASE=${BASE:-main}
echo "Branch: $BRANCH"
echo "Ticket: ${TICKET:-(none — branch does not match TICKET-123/desc convention)}"
echo "Base:   $BASE"
echo
echo "Commits on branch:"
git log "origin/$BASE..HEAD" --oneline 2>/dev/null || git log -10 --oneline
echo
echo "Files changed:"
git diff "origin/$BASE..HEAD" --stat 2>/dev/null || git diff --stat
echo
UNPUSHED=$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "Unpushed commits: $UNPUSHED"
echo
echo "Recent base-branch commits (convention ref):"
git log "origin/$BASE" -10 --oneline 2>/dev/null || git log -10 --oneline
```

## Conventions

Two conventions are common in Zivtech repos:

**Zivtech client work** — per `zivtech-development-workflow`:
- All commits on the branch should include the `TICKET-123:` prefix
- PR title prefixed with `TICKET-123: `
- **Do NOT merge the PR** — that is the Lead Developer's responsibility

**Zivtech tooling / library repos**:
- Commits follow Conventional Commits — `feat(scope): description`, etc.
- PR title matches the same `type(scope): ...` style
- Merge policy varies — check with the user before merging

## Task

1. **If `$ARGUMENTS` begins with a prefix-shaped token** (e.g., `ZIV-456`, `feat(auth)`, `fix:`), use it as the PR title prefix.
2. **Otherwise**, match the repo's convention (see recent base-branch commits above):
   - Zivtech client (`TICKET-123:` style) → PR title prefixed with ticket from branch; verify all branch commits include the prefix; ask if missing.
   - Conventional Commits (`feat(...)` / `fix(...)`) → PR title `type(scope): description`; no ticket prefix.
   - Mixed / unclear → stop and ask.
3. If there are unpushed commits, push first (`-u` if no upstream).
4. Keep PR title under 70 chars.
5. Analyze ALL commits on the branch for the PR body — Summary + Test plan sections.
6. Create with `gh pr create` (HEREDOC for body).
7. Return the PR URL. Do not merge.

$ARGUMENTS
