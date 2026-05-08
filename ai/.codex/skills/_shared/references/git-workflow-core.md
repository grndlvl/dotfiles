# Git Workflow Core

Use these rules for Zivtech git workflow skills.

## Discovery

Before staging, committing, pushing, or creating a PR, gather enough state to avoid guessing:

- `git branch --show-current`
- ticket from branch: first match of `^[A-Z]+-[0-9]+`
- `git status --short`
- staged and unstaged stats: `git diff --cached --stat`, `git diff --stat`
- relevant content diff: `git diff --cached`, `git diff`
- recent convention sample: `git log -10 --oneline`
- for PRs, detect base with `git symbolic-ref --short refs/remotes/origin/HEAD` and strip `origin/`; default to `main` if unavailable
- for push/PR, detect upstream with `git rev-parse --abbrev-ref --symbolic-full-name @{u}` and tolerate no upstream

## Convention Selection

If the user supplies an obvious prefix, use it. Examples:

- `ZIV-456`
- `feat(auth)`
- `fix:`
- `docs(setup)`
- `chore`

Otherwise infer from recent commits:

- Zivtech client history uses `TICKET-123:`. Use the ticket extracted from the branch. If no ticket exists, stop and ask for the prefix.
- Tooling/library history uses Conventional Commits. Use `type(scope): description`.
- Mixed or unclear history means stop and ask which convention to use.

## Commit Rules

- Stage specific files only. Do not use `git add .` or `git add -A`.
- Split unrelated concerns into separate commits.
- Use a HEREDOC or equivalent multi-line-safe method for commit messages.
- Follow the workspace Lore commit protocol. Include useful trailers, and include `Confidence`, `Scope-risk`, `Tested`, and `Not-tested` unless there is a concrete reason not to.

Lore format:

```text
<intent line: why the change was made, not what changed>

<body: narrative context and approach rationale>

Constraint: <external constraint that shaped the decision>
Rejected: <alternative considered> | <reason for rejection>
Confidence: <low|medium|high>
Scope-risk: <narrow|moderate|broad>
Directive: <forward-looking warning for future modifiers>
Tested: <what was verified>
Not-tested: <known gaps>
```

## Push Rules

- Use `git push -u origin <branch>` when there is no upstream.
- Do not force-push unless the user explicitly requested it.
- If force is needed, use `--force-with-lease`, never `--force`.

## PR Rules

- If a PR already exists, report its URL and do not create a duplicate.
- If there are unpushed commits, push first.
- Keep PR titles under 70 chars.
- Analyze all commits and changed files on the branch for the PR body.
- PR body must include `Summary` and `Test plan`.
- Do not merge the PR.

## Verification

Report concrete evidence:

- after commit: `git status --short`, `git log -1 --stat`
- after push: upstream/branch state and unpushed commit check when possible
- after PR: `gh pr view --json url,title,baseRefName,headRefName`
