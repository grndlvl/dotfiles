#!/bin/bash
# Smart notification - only suppresses when viewing THIS specific tmux window/pane
# Supports granular detection: different session, window, or pane will still notify

NOTIFICATION_TYPE="$1"

# Get Claude's ACTUAL location using its pane ID (most reliable)
CLAUDE_PANE="$TMUX_PANE"
CLAUDE_SESSION=$(tmux display-message -t "$CLAUDE_PANE" -p '#{session_name}' 2>/dev/null)
CLAUDE_WINDOW=$(tmux display-message -t "$CLAUDE_PANE" -p '#{window_index}' 2>/dev/null)
CLAUDE_PANE_INDEX=$(tmux display-message -t "$CLAUDE_PANE" -p '#{pane_index}' 2>/dev/null)
CLAUDE_WINDOW_NAME=$(tmux display-message -t "$CLAUDE_PANE" -p '#{window_name}' 2>/dev/null)

# Build display string: session:window.pane (name)
TMUX_INFO="$CLAUDE_SESSION:$CLAUDE_WINDOW.$CLAUDE_PANE_INDEX ($CLAUDE_WINDOW_NAME)"

# Get what the USER is currently viewing via most recent client activity
USER_VIEW=$(tmux list-clients -F '#{client_activity} #{session_name}:#{window_index}' 2>/dev/null | sort -rn | head -1 | awk '{print $2}')

# Get the active pane ID in the user's current window (for comparison)
USER_ACTIVE_PANE=$(tmux display-message -t "$USER_VIEW" -p '#{pane_id}' 2>/dev/null)

# 1. Check if Ghostty is even focused
ACTIVE_CLASS=$(hyprctl activewindow -j 2>/dev/null | jq -r '.class // ""')

if [[ ! "$ACTIVE_CLASS" =~ ghostty && ! "$ACTIVE_CLASS" =~ Ghostty ]]; then
  if [ "$NOTIFICATION_TYPE" = "permission" ]; then
    notify-send -t 0 -u critical 'Claude Code' "Permission needed in $TMUX_INFO"
  else
    notify-send -t 0 -u normal 'Claude Code' "Waiting in $TMUX_INFO"
  fi
  exit 0
fi

# 2. Compare: is user viewing Claude's exact session:window AND pane?
CLAUDE_LOC="$CLAUDE_SESSION:$CLAUDE_WINDOW"

# Suppress only if same window AND same pane
if [[ "$CLAUDE_LOC" == "$USER_VIEW" ]] && [[ "$CLAUDE_PANE" == "$USER_ACTIVE_PANE" ]]; then
  exit 0
fi

# User is in Ghostty but different session/window/pane - notify!
if [ "$NOTIFICATION_TYPE" = "permission" ]; then
  notify-send -t 0 -u critical 'Claude Code' "Permission needed in $TMUX_INFO"
else
  notify-send -t 0 -u normal 'Claude Code' "Waiting in $TMUX_INFO"
fi
