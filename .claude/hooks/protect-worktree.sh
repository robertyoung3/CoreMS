#!/bin/bash
# PreToolUse hook: Prevent checking out upstream-based branches in the main working directory.
# Upstream fix/feature branches must use git worktrees to avoid destroying fork-specific
# untracked files (.env, etc.) whose gitignore entries only exist on fork branches.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.command // empty')

[ -z "$COMMAND" ] && exit 0

# Only check git checkout/switch commands targeting fix/ or upstream-based branches
if echo "$COMMAND" | grep -qP 'git\s+(checkout|switch)\s+.*\bfix/'; then
  # Check if we're in the main working directory (not a worktree)
  MAIN_WORKTREE=$(git worktree list --porcelain 2>/dev/null | head -1 | sed 's/^worktree //')
  CURRENT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)

  if [ "$MAIN_WORKTREE" = "$CURRENT_DIR" ]; then
    cat <<'HOOK_OUTPUT'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "BLOCKED: Cannot checkout fix/ branches in the main working directory. Use a git worktree instead:\n\n  git worktree add /tmp/corems-fix-name upstream/master -b fix/my-fix\n  cd /tmp/corems-fix-name\n\nSee CLAUDE.md for the upstream contribution workflow."
  }
}
HOOK_OUTPUT
    exit 0
  fi
fi

exit 0
