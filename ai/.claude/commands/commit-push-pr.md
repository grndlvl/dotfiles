---
description: "Full ship workflow: commit, push, open PR. Auto-detects format; pass a prefix to override (e.g., `/commit-push-pr ZIV-456`)."
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(gh *) Bash(echo *) Bash(grep *) Bash(sed *)
---

# Zivtech Commit, Push, and Create PR

## Gather current state

Before doing anything else, run these in parallel and use the output to drive the rest of the task:

- `git branch --show-current` to get the current branch.
- Extract a ticket from the branch (first match of `^[A-Z]+-[0-9]+`); if none, the branch does not follow the `TICKET-123/desc` convention.
- `git symbolic-ref --short refs/remotes/origin/HEAD` (strip the `origin/` prefix) to get the base branch; default to `main` if not set.
- `git status --short` to see what's staged/unstaged/untracked.
- `git diff HEAD --stat` to see the change footprint.
- `git log origin/<base>..HEAD --oneline` to see existing commits on this branch (may be empty for a new branch).
- `git log origin/<base> -10 --oneline` to see how the base branch's recent commits are formatted (use this to detect the convention).

## Conventions

Two conventions are common in Zivtech repos:

**Zivtech client work** — per `zivtech-development-workflow`:
- Commit format: `TICKET-123: Description` (capitalized, imperative, < 72 chars)
- PR title prefixed with `TICKET-123: ` matching commit style
- **Do NOT merge the PR** — Lead Developer handles merging

**Zivtech tooling / library repos**:
- Conventional Commits — `feat(scope): description`, `fix(scope): ...`
- PR title matches the same `type(scope): ...` style
- Merge policy varies — check with the user before merging

## Task

1. **If `$ARGUMENTS` begins with a prefix-shaped token** (e.g., `ZIV-456`, `feat(auth)`, `fix:`), use it as the prefix for both the commit and the PR title.
2. **Otherwise**, match the repo's convention (see recent base-branch commits above):
   - Zivtech client (`TICKET-123:` style) → prefix commit and PR title with ticket from branch; ask if missing.
   - Conventional Commits (`feat(...)` / `fix(...)`) → use `type(scope): description` for both commit and PR title.
   - Mixed / unclear → stop and ask.
3. Stage specific files (no `git add .` / `-A`).
4. Commit with HEREDOC message.
5. Push with `-u` if no upstream.
6. Analyze ALL commits on the branch (including the new one) for the PR body.
7. Create the PR with `gh pr create` — title under 70 chars, body has Summary + Test plan.
8. Return the PR URL. Do not merge.

$ARGUMENTS
