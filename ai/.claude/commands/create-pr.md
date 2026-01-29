# Create Pull Request

Create a GitHub PR for the current branch.

## Current State

Branch: `$(git branch --show-current)`
Base branch: `$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo "dev")`

### Commits to Include
```
$(git log origin/dev..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline 2>/dev/null || git log -10 --oneline)
```

### Files Changed
```
$(git diff origin/dev..HEAD --stat 2>/dev/null || git diff origin/main..HEAD --stat 2>/dev/null || git diff --stat)
```

### Unpushed?
$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l | xargs -I {} echo "{} unpushed commits")

## Instructions

1. If there are unpushed commits, push first with `-u`
2. Analyze ALL commits above (not just latest) to understand full scope
3. Create PR with `gh pr create`:
   - Title under 70 chars
   - Use body for details

```bash
gh pr create --title "Title" --body "$(cat <<'EOF'
## Summary
- Changes

## Test plan
- [ ] Testing steps

Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

4. Return the PR URL

$ARGUMENTS
