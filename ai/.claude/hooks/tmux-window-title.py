#!/usr/bin/env python3
"""
Claude Code Hook: Update tmux window name based on conversation topic

Fires on:
  - SessionStart: Saves original window name for later restoration
  - Stop: Updates window name based on conversation topic
  - SessionEnd: Restores original window name

Output format: 🤖 topic-name (1-3 words, lowercase, kebab-case)

## How It Works

The hook fires after every Claude response (`Stop` event) and:

1. **Reads the conversation transcript** to understand context
2. **Extracts topic** using these strategies (in order):
   - **File-based:** Most common directory/file being edited → `🤖 hooks-tmux`
   - **Pattern matching:** Detects git, testing, fixing, implementing, refactoring
   - **Keyword extraction:** Finds most frequent meaningful words from your prompts
3. **Updates tmux window** with the generated title

On SessionEnd, restores the original window name that was saved at SessionStart.

## Examples

| What you're doing      | Window title        |
|------------------------|---------------------|
| Editing hooks files    | `🤖 hooks-tmux`     |
| "fix the auth bug"     | `🤖 fix-auth`       |
| "commit my changes"    | `🤖 git-commit`     |
| Running tests          | `🤖 testing`        |
| "refactor the API"     | `🤖 refactor-api`   |
| General chat           | `🤖 claude`         |

## Configuration

- Location: ~/.claude/hooks/tmux-window-title.py
- Settings: ~/.claude/settings.json (hooks.Stop, hooks.SessionStart, hooks.SessionEnd)
- Prefix: Change PREFIX constant below to customize (🤖, 󰚩, 🧠, claude, etc.)
- State file: ~/.claude/.tmux-original-title (stores original window name)
"""

# Customize the prefix here
PREFIX = "🤖"

import json
import sys
import os
import subprocess
import re
from pathlib import Path
from collections import Counter

def get_title_file():
    """Get path to file storing original window title (per-pane)."""
    pane = os.environ.get('TMUX_PANE', 'default').replace('%', '')
    return os.path.expanduser(f"~/.claude/.tmux-original-title-{pane}")

def save_original_title():
    """Save the current tmux window title before Claude modifies it."""
    tmux_pane = os.environ.get('TMUX_PANE')
    if not tmux_pane:
        return False

    try:
        # Get current window name
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#W'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            original_title = result.stdout.strip()
            # Don't save if it's already a Claude title
            if not original_title.startswith(PREFIX):
                title_file = get_title_file()
                with open(title_file, 'w') as f:
                    f.write(original_title)
                return True
    except Exception:
        pass
    return False

def restore_original_title():
    """Restore the original tmux window title, or keep topic if original was generic."""
    tmux_pane = os.environ.get('TMUX_PANE')
    if not tmux_pane:
        return False

    try:
        title_file = get_title_file()
        if os.path.exists(title_file):
            with open(title_file, 'r') as f:
                original_title = f.read().strip()

            # If original was generic "claude", keep the topic but remove the prefix
            if original_title.lower() == 'claude':
                # Get current window name and strip the prefix
                result = subprocess.run(
                    ['tmux', 'display-message', '-p', '#W'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    current = result.stdout.strip()
                    # Remove prefix (e.g., "🤖 hooks-tmux" -> "hooks-tmux")
                    if current.startswith(PREFIX):
                        new_title = current[len(PREFIX):].lstrip()
                        if new_title:
                            subprocess.run(
                                ['tmux', 'rename-window', '-t', tmux_pane, new_title],
                                check=True,
                                capture_output=True,
                                timeout=2
                            )
            elif original_title:
                # Restore the original non-generic title
                subprocess.run(
                    ['tmux', 'rename-window', '-t', tmux_pane, original_title],
                    check=True,
                    capture_output=True,
                    timeout=2
                )

            # Clean up the file
            os.remove(title_file)
            return True
    except Exception:
        pass
    return False

def read_hook_input():
    """Read JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return None

def read_transcript(transcript_path):
    """Read and parse JSONL transcript file."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    entries = []
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except Exception:
        pass

    return entries

def extract_files_from_tools(entries, limit=10):
    """Extract file paths from tool calls in recent entries."""
    files = []
    for entry in entries[-limit:]:
        if entry.get('type') == 'assistant':
            # Content is in message.content, not just content
            content = entry.get('message', {}).get('content', [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get('type') == 'tool_use':
                    tool_input = block.get('input', {})

                    # Check for file_path parameter
                    if 'file_path' in tool_input:
                        files.append(tool_input['file_path'])

                    # Check for path parameter
                    if 'path' in tool_input:
                        files.append(tool_input['path'])

                    # Check for files array
                    if 'files' in tool_input:
                        for f in tool_input['files']:
                            if isinstance(f, dict) and 'path' in f:
                                files.append(f['path'])
                            elif isinstance(f, str):
                                files.append(f)

    return files

def extract_keywords_from_text(text):
    """Extract meaningful keywords from text."""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
        'its', 'our', 'their', 'what', 'which', 'who', 'when', 'where', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'so', 'than', 'too',
        'very', 'just', 'now', 'need', 'want', 'make', 'create', 'add', 'please'
    }

    # Extract words (alphanumeric sequences)
    words = re.findall(r'\b[a-z][a-z0-9]*\b', text.lower())

    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    return keywords

def extract_user_prompts(entries, limit=5):
    """Extract recent user prompts."""
    prompts = []
    for entry in reversed(entries):
        if entry.get('type') == 'user':
            # Content is in message.content as a string (not array)
            content = entry.get('message', {}).get('content', '')
            if isinstance(content, str) and content:
                # Skip system tags and meta messages
                text = content.strip()
                skip_patterns = [
                    '<system-reminder>',
                    '[Request interrupted',
                    'PreToolUse:',
                    'PostToolUse:',
                    'hook additional context',
                ]
                if not any(text.startswith(p) or p in text for p in skip_patterns):
                    prompts.append(content)
            elif isinstance(content, list):
                # Handle array format if present
                for block in content:
                    if block.get('type') == 'text':
                        text = block.get('text', '')
                        if text and not text.strip().startswith('<system-reminder>'):
                            prompts.append(text)
        if len(prompts) >= limit:
            break

    return list(reversed(prompts))

def generate_topic_from_files(files):
    """Generate topic from file paths."""
    if not files:
        return None

    # Extract meaningful parts from paths
    parts = []
    for f in files:
        path = Path(f)

        # Get filename without extension
        name = path.stem

        # Get parent directory name
        if path.parent.name and path.parent.name not in ['.', '..', '']:
            parts.append(path.parent.name)

        # Add filename parts
        if name:
            # Split on common separators
            name_parts = re.split(r'[-_.]', name)
            parts.extend(name_parts)

    # Count occurrences
    counter = Counter(parts)

    # Get most common, exclude common names
    exclude = {'index', 'main', 'test', 'spec', 'utils', 'helpers', 'src', 'lib', 'dist'}
    common = [(word, count) for word, count in counter.most_common(5)
              if word.lower() not in exclude and len(word) > 2]

    if common:
        # Take top 1-2 most common words
        topic_words = [word for word, _ in common[:2]]
        return '-'.join(topic_words[:3]).lower()

    return None

def generate_topic_from_prompts(prompts):
    """Generate topic from user prompts."""
    if not prompts:
        return None

    # Combine recent prompts
    text = ' '.join(prompts[:3])

    # Check for specific patterns

    # Git operations
    git_match = re.search(r'\b(commit|push|pull|merge|rebase|branch|checkout|stash)\b', text, re.IGNORECASE)
    if git_match:
        return f"git-{git_match.group(1).lower()}"

    # Testing
    if re.search(r'\b(test|testing|spec|jest|pytest|unit|integration)\b', text, re.IGNORECASE):
        return 'testing'

    # Debugging/fixing
    fix_match = re.search(r'\b(fix|debug|error|bug|issue)\s+(\w+)', text, re.IGNORECASE)
    if fix_match:
        return f"fix-{fix_match.group(2).lower()}"

    # Implementation
    impl_match = re.search(r'\b(implement|create|add|build)\s+(\w+(?:\s+\w+)?)', text, re.IGNORECASE)
    if impl_match:
        words = impl_match.group(2).lower().split()[:2]
        return '-'.join(words)

    # Refactoring
    if re.search(r'\b(refactor|improve|enhance|optimize)\b', text, re.IGNORECASE):
        # Try to find what's being refactored
        context = re.search(r'\b(?:refactor|improve|enhance|optimize)\s+(\w+(?:\s+\w+)?)', text, re.IGNORECASE)
        if context:
            words = context.group(1).lower().split()[:2]
            return f"refactor-{'-'.join(words)}"
        return 'refactor'

    # Extract keywords
    keywords = extract_keywords_from_text(text)

    if keywords:
        # Count frequency
        counter = Counter(keywords)
        most_common = counter.most_common(3)

        # Take top 1-3 words
        topic_words = [word for word, _ in most_common[:3]]
        return '-'.join(topic_words[:3])

    return None

def generate_topic(hook_input):
    """Generate topic name from conversation context."""
    # Read transcript
    transcript_path = hook_input.get('transcript_path')
    entries = read_transcript(transcript_path)

    if not entries:
        return 'claude'

    # Try multiple strategies

    # 1. Extract from files being edited
    files = extract_files_from_tools(entries)
    topic = generate_topic_from_files(files)
    if topic:
        return topic

    # 2. Extract from user prompts
    prompts = extract_user_prompts(entries)
    topic = generate_topic_from_prompts(prompts)
    if topic:
        return topic

    # 3. Fallback to first significant keyword from latest prompt
    if prompts:
        keywords = extract_keywords_from_text(prompts[-1])
        if keywords:
            return keywords[0]

    return 'claude'

def update_tmux_window(title):
    """Update tmux window name."""
    tmux_pane = os.environ.get('TMUX_PANE')
    if not tmux_pane:
        return False

    full_title = f"{PREFIX} {title}"

    try:
        subprocess.run(
            ['tmux', 'rename-window', '-t', tmux_pane, full_title],
            check=True,
            capture_output=True,
            timeout=2
        )
        return True
    except Exception:
        return False

def main():
    # Check if running in tmux
    if not os.environ.get('TMUX'):
        sys.exit(0)

    # Read hook input
    hook_input = read_hook_input()
    if not hook_input:
        sys.exit(0)

    # Get event type
    event = hook_input.get('hook_event_name', hook_input.get('event', ''))

    if event == 'SessionStart':
        # Save original window title before Claude modifies it
        save_original_title()

    elif event == 'Stop':
        # Update window title based on conversation topic
        topic = generate_topic(hook_input)
        update_tmux_window(topic)

    elif event == 'SessionEnd':
        # Restore original window title when Claude exits
        restore_original_title()

if __name__ == '__main__':
    main()
