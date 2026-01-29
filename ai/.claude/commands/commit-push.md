# Commit and Push

Create a commit and push to remote.

## Current State

Branch: `$(git branch --show-current)`

### Git Status
```
$(git status --short)
```

### Git Diff (staged and unstaged)
```
$(git diff HEAD --stat 2>/dev/null || git diff --stat)
```

### Recent Commits (for style reference)
```
$(git log -3 --oneline 2>/dev/null)
```

## Instructions

1. Based on the diff above, create a descriptive commit message
2. Stage the relevant changed files (prefer specific files over `git add .`)
3. Commit with message ending with: `Co-Authored-By: Claude <noreply@anthropic.com>`
4. Push to origin (use `-u` if no upstream set)
5. Report the commit hash and confirm push succeeded

Use HEREDOC for commit message:
```bash
git commit -m "$(cat <<'EOF'
Message here

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

$ARGUMENTS
