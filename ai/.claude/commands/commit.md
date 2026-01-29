# Commit

Create a git commit for current changes.

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
$(git log -3 --oneline)
```

## Instructions

1. Based on the changes above, create a descriptive commit message
2. Stage relevant files (prefer specific files over `git add .`)
3. Commit with message ending with: `Co-Authored-By: Claude <noreply@anthropic.com>`
4. Report the commit hash

Use HEREDOC for commit message:
```bash
git commit -m "$(cat <<'EOF'
Message here

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

$ARGUMENTS
