# Generate Commit Message

Draft a commit message for current changes without committing.

## Current State

Branch: `$(git branch --show-current)`

### Git Status
```
$(git status --short)
```

### Staged Changes
```
$(git diff --cached --stat)
```

### Unstaged Changes
```
$(git diff --stat)
```

### Recent Commits (style reference)
```
$(git log -5 --oneline)
```

## Instructions

Based on the changes above, draft a commit message that:
- Summarizes the nature of changes (feature, fix, refactor, etc.)
- Focuses on "why" not just "what"
- Follows the commit style shown above
- Ends with `Co-Authored-By: Claude <noreply@anthropic.com>`

**Output the message only** - do not stage or commit. The user will copy/use it manually.

$ARGUMENTS
