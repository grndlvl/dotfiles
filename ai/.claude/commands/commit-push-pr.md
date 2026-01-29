# Commit, Push, and Create PR

Full workflow: commit changes, push, and open a pull request.

## Current State

Branch: `$(git branch --show-current)`
Base: `$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo "dev")`

### Git Status
```
$(git status --short)
```

### Changes
```
$(git diff HEAD --stat 2>/dev/null || git diff --stat)
```

### Recent Commits (style reference)
```
$(git log -3 --oneline)
```

### Existing Commits on Branch
```
$(git log origin/dev..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline 2>/dev/null || echo "New branch")
```

## Instructions

1. **Commit**: Stage files and commit with descriptive message ending with `Co-Authored-By: Claude <noreply@anthropic.com>`
2. **Push**: `git push -u origin $(git branch --show-current)`
3. **PR**: Create with `gh pr create`, analyzing ALL commits on branch

PR format:
```bash
gh pr create --title "Title" --body "$(cat <<'EOF'
## Summary
- Changes

## Test plan
- [ ] Steps

Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

4. Return commit hash and PR URL

$ARGUMENTS
