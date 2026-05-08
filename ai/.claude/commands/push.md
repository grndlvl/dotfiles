---
description: Push current branch to remote
allowed-tools: Bash(git push *) Bash(git log *) Bash(git branch *) Bash(git rev-parse *)
---

# Push

## Current state
- Branch: !`git branch --show-current`
- Tracking: !`git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no upstream"`
- Unpushed commits: !`git log @{u}..HEAD --oneline 2>/dev/null || git log -5 --oneline`

Push current branch to remote. Use `-u` if no upstream is set.

$ARGUMENTS
