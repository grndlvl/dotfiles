# Push to Remote

Push local commits to the remote branch.

## Current State

Branch: `$(git branch --show-current)`
Tracking: `$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "No upstream set")`

### Unpushed Commits
```
$(git log @{u}..HEAD --oneline 2>/dev/null || git log -5 --oneline)
```

## Instructions

1. Push to the remote
   - If upstream exists: `git push`
   - If no upstream: `git push -u origin $(git branch --show-current)`
2. Confirm push succeeded

Never force push unless explicitly requested.

$ARGUMENTS
