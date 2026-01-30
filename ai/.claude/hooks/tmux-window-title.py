#!/usr/bin/env python3
"""
Claude Code Hook: Update tmux window name based on conversation topic

Fires on:
  - SessionStart: Saves original window name for later restoration
  - UserPromptSubmit: Sets initial topic from first prompt
  - Stop: Updates window name based on conversation topic
  - SessionEnd: Restores original window name

Output format: 🤖 topic-name (1-3 words, lowercase, kebab-case)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# =============================================================================
# CONFIGURATION
# =============================================================================

PREFIX = "🤖"
TMUX_TIMEOUT = 2  # seconds

# =============================================================================
# CONSTANTS (Pre-computed for speed)
# =============================================================================

# Unified stopwords for all filtering operations
STOPWORDS = frozenset({
    # Articles & determiners
    'a', 'an', 'the', 'this', 'that', 'these', 'those', 'some', 'all', 'any',
    # Pronouns
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
    'it', 'its', 'they', 'them', 'their', 'who', 'which', 'what', 'where', 'when', 'why', 'how',
    # Prepositions & conjunctions
    'to', 'for', 'in', 'on', 'at', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
    'through', 'during', 'and', 'or', 'but', 'so', 'if', 'then', 'than',
    # Verbs (common/auxiliary)
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might',
    # Filler words
    'just', 'very', 'too', 'also', 'now', 'only', 'same', 'more', 'most', 'other',
    'each', 'every', 'both', 'few', 'no', 'nor', 'not', 'such',
    # Common request words (not useful for topic)
    'please', 'help', 'need', 'want', 'like', 'let', 'lets', 'make', 'create', 'add',
})

# Technical nouns that indicate the subject (frozen set for O(1) lookup)
TECH_NOUNS = frozenset({
    'api', 'auth', 'authentication', 'authorization', 'button', 'cache', 'cli',
    'component', 'config', 'configuration', 'database', 'db', 'dialog', 'dropdown',
    'endpoint', 'error', 'feature', 'field', 'file', 'filter', 'form', 'function',
    'handler', 'header', 'hook', 'icon', 'input', 'layout', 'link', 'list', 'loader',
    'login', 'logout', 'menu', 'middleware', 'migration', 'modal', 'module', 'navbar',
    'navigation', 'notification', 'page', 'pagination', 'panel', 'parser', 'password',
    'permission', 'plugin', 'popup', 'profile', 'query', 'route', 'router', 'schema',
    'script', 'search', 'section', 'selector', 'server', 'service', 'session', 'settings',
    'sidebar', 'signup', 'slider', 'socket', 'state', 'storage', 'style', 'tab', 'table',
    'template', 'test', 'theme', 'title', 'toast', 'token', 'toolbar', 'tooltip', 'ui',
    'upload', 'url', 'user', 'validation', 'view', 'widget', 'window', 'wizard', 'worker',
})

# File path components to exclude from topic generation
EXCLUDED_PATH_PARTS = frozenset({'index', 'main', 'test', 'spec', 'utils', 'helpers', 'src', 'lib', 'dist'})

# =============================================================================
# PRE-COMPILED REGEX PATTERNS (compiled once at module load)
# =============================================================================

# Text normalization
RE_CODE_BLOCK = re.compile(r'```[\s\S]*?```')
RE_INLINE_CODE = re.compile(r'`[^`]+`')
RE_QUOTES = re.compile(r'["]')  # Only double quotes; preserve apostrophes for contractions
RE_WHITESPACE = re.compile(r'\s+')
RE_WORD = re.compile(r'\b([a-z][a-z0-9]*)\b', re.IGNORECASE)
RE_WORD_WITH_SEPARATORS = re.compile(r'\b([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)\b', re.IGNORECASE)

# Action patterns: (compiled_regex, prefix_or_none)
ACTION_PATTERNS: list[tuple[re.Pattern, str | None]] = [
    # fix/debug/resolve/investigate X
    (re.compile(r'\b(?:fix|debug|resolve|investigate)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'fix'),
    # implement/create/add/build/write/make X
    (re.compile(r'\b(?:implement|create|add|build|write|make)\s+(?:a\s+|an\s+|the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)*(?:\s+[a-z][a-z0-9]*)?)', re.I), None),
    # update/modify/change/edit/tweak X
    (re.compile(r'\b(?:update|modify|change|edit|tweak)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'update'),
    # refactor/improve/enhance/optimize/cleanup X
    (re.compile(r'\b(?:refactor|improve|enhance|optimize|cleanup|clean\s+up)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'refactor'),
    # test/verify/validate X
    (re.compile(r'\b(?:test|verify|validate)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'test'),
    # check X (but not "check out")
    (re.compile(r'\bcheck\s+(?!out\b)(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'test'),
    # review/audit/analyze/examine X
    (re.compile(r'\b(?:review|audit|analyze|examine)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'review'),
    # deploy/release/publish/ship [to] X
    (re.compile(r'\b(?:deploy|release|publish|ship)\s+(?:to\s+)?(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'deploy'),
    # setup/configure/install X
    (re.compile(r'\b(?:setup|set\s+up|configure|install)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'setup'),
    # remove/delete/drop/eliminate X
    (re.compile(r'\b(?:remove|delete|drop|eliminate)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'remove'),
    # migrate/convert/transform/port X
    (re.compile(r'\b(?:migrate|convert|transform|port)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), 'migrate'),
    # work on/look at/check out/focus on X
    (re.compile(r'\b(?:work\s+on|look\s+at|check\s+out|focus\s+on)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I), None),
]

# Git operations
RE_GIT_OP = re.compile(r'\b(commit|push|pull|merge|rebase|branch|checkout|stash|cherry-?pick|reset|revert)\b', re.I)

# Question patterns
RE_QUESTION = re.compile(r'\b(?:how\s+(?:to|do\s+(?:i|we))|what\s+is|why\s+is|where\s+is)\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I)

# Help patterns
RE_HELP = re.compile(r'\bhelp\s+(?:me\s+)?with\s+(?:the\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)', re.I)

# Broken/failing patterns
RE_BROKEN = re.compile(r"\b([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)\s+(?:isn't|is\s+not|doesn't|does\s+not|won't|is\s+broken|is\s+failing)", re.I)
RE_BROKEN_NOUN = re.compile(r'\b(?:my|the)\s+(?:broken\s+)?([a-z][a-z0-9]*(?:[-_][a-z0-9]+)?)\s*(?:bug|error|issue|problem)?', re.I)
RE_ERROR_CONTEXT = re.compile(r'\b(?:fix|debug|broken|error|bug|issue|problem)\b', re.I)

# System message detection
SKIP_PATTERNS = ('<system-reminder>', '[Request interrupted', 'PreToolUse:', 'PostToolUse:', 'hook additional context')

# =============================================================================
# TMUX HELPERS
# =============================================================================

def get_tmux_pane() -> str | None:
    """Get current tmux pane ID, or None if not in tmux."""
    return os.environ.get('TMUX_PANE')


def run_tmux_command(args: list[str], timeout: int = TMUX_TIMEOUT) -> subprocess.CompletedProcess | None:
    """Run a tmux command and return result, or None on failure."""
    try:
        return subprocess.run(
            ['tmux'] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return None


def get_current_window_name() -> str | None:
    """Get the current tmux window name."""
    result = run_tmux_command(['display-message', '-p', '#W'])
    return result.stdout.strip() if result and result.returncode == 0 else None


def set_window_name(pane: str, name: str) -> bool:
    """Set tmux window name for a pane."""
    result = run_tmux_command(['rename-window', '-t', pane, name])
    return result is not None and result.returncode == 0


# =============================================================================
# TITLE STATE MANAGEMENT
# =============================================================================

def get_title_file() -> Path:
    """Get path to file storing original window title (per-pane)."""
    pane = os.environ.get('TMUX_PANE', 'default').replace('%', '')
    return Path.home() / '.claude' / f'.tmux-original-title-{pane}'


def save_original_title() -> bool:
    """Save current tmux window title before Claude modifies it."""
    if not get_tmux_pane():
        return False

    original = get_current_window_name()
    if original and not original.startswith(PREFIX):
        try:
            get_title_file().write_text(original)
            return True
        except OSError:
            pass
    return False


def restore_original_title() -> bool:
    """Restore original tmux window title on session end."""
    pane = get_tmux_pane()
    if not pane:
        return False

    title_file = get_title_file()
    if not title_file.exists():
        return False

    try:
        original = title_file.read_text().strip()

        if original.lower() == 'claude':
            # Keep topic but remove prefix
            current = get_current_window_name()
            if current and current.startswith(PREFIX):
                new_title = current[len(PREFIX):].lstrip()
                if new_title:
                    set_window_name(pane, new_title)
        elif original:
            set_window_name(pane, original)

        title_file.unlink()
        return True
    except OSError:
        return False


def window_has_prefix() -> bool:
    """Check if tmux window already has Claude prefix."""
    name = get_current_window_name()
    return name.startswith(PREFIX) if name else False


def update_tmux_window(topic: str) -> bool:
    """Update tmux window with topic."""
    pane = get_tmux_pane()
    return set_window_name(pane, f"{PREFIX} {topic}") if pane else False


# =============================================================================
# INPUT HELPERS
# =============================================================================

def read_hook_input() -> dict[str, Any] | None:
    """Read JSON hook input from stdin."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def read_transcript(path: str | None) -> list[dict]:
    """Read and parse JSONL transcript file."""
    if not path or not os.path.exists(path):
        return []

    entries = []
    try:
        with open(path) as f:
            for line in f:
                if line := line.strip():
                    entries.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        pass
    return entries


# =============================================================================
# TOPIC EXTRACTION
# =============================================================================

def normalize_text(text: str) -> str:
    """Remove markdown formatting and normalize whitespace."""
    text = RE_CODE_BLOCK.sub(' ', text)
    text = RE_INLINE_CODE.sub(' ', text)
    text = RE_QUOTES.sub(' ', text)
    return RE_WHITESPACE.sub(' ', text).strip()


def is_system_message(text: str) -> bool:
    """Check if text is a system/meta message to skip."""
    return text.startswith('<') or any(p in text for p in SKIP_PATTERNS)


def clean_subject(subject: str, max_words: int = 2) -> str | None:
    """Clean and filter a subject string, returning kebab-case or None."""
    words = [w for w in subject.lower().split() if w not in STOPWORDS][:max_words]
    return '-'.join(words) if words else None


def extract_topic_from_prompt(prompt: str) -> str | None:
    """
    Extract a concise topic from a user prompt.

    Strategy order:
    1. Action + subject patterns (most reliable)
    2. Git operations
    3. Question/help patterns
    4. Broken/failing patterns
    5. Technical noun detection
    6. First meaningful words fallback
    """
    if not prompt:
        return None

    text = prompt.strip()
    if is_system_message(text):
        return None

    text = normalize_text(text)

    # 1. Action patterns
    for pattern, prefix in ACTION_PATTERNS:
        if match := pattern.search(text):
            if subject := clean_subject(match.group(1)):
                return f"{prefix}-{subject}" if prefix else subject

    # 2. Git operations
    if match := RE_GIT_OP.search(text):
        return f"git-{match.group(1).lower().replace('-', '')}"

    # 3. Question patterns
    if match := RE_QUESTION.search(text):
        return f"help-{match.group(1).lower()}"

    # 4. Help patterns
    if match := RE_HELP.search(text):
        return f"help-{match.group(1).lower()}"

    # 5. Broken/failing patterns
    if match := RE_BROKEN.search(text):
        return f"fix-{match.group(1).lower()}"

    if RE_ERROR_CONTEXT.search(text):
        if match := RE_BROKEN_NOUN.search(text):
            subject = match.group(1).lower()
            if subject not in {'my', 'the', 'a', 'an', 'broken'}:
                return f"fix-{subject}"

    # 6. Technical noun detection
    for word in RE_WORD_WITH_SEPARATORS.findall(text.lower()):
        if word in TECH_NOUNS:
            return word
        # Check if word contains a tech noun (e.g., "userAuth" contains "auth")
        for noun in TECH_NOUNS:
            if word.endswith(noun) or word.startswith(noun):
                return word

    # 7. First meaningful words fallback
    words = [w for w in RE_WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 2]
    if words:
        return '-'.join(words[:3])

    return None


def extract_files_from_tools(entries: list[dict], limit: int = 10) -> list[str]:
    """Extract file paths from tool calls in recent transcript entries."""
    files = []
    for entry in entries[-limit:]:
        if entry.get('type') != 'assistant':
            continue
        content = entry.get('message', {}).get('content', [])
        if not isinstance(content, list):
            continue

        for block in content:
            if block.get('type') != 'tool_use':
                continue
            tool_input = block.get('input', {})

            # Collect paths from various tool input formats
            if path := tool_input.get('file_path'):
                files.append(path)
            if path := tool_input.get('path'):
                files.append(path)
            for f in tool_input.get('files', []):
                if isinstance(f, dict) and (path := f.get('path')):
                    files.append(path)
                elif isinstance(f, str):
                    files.append(f)

    return files


def generate_topic_from_files(files: list[str]) -> str | None:
    """Generate topic from file paths by finding common path components."""
    if not files:
        return None

    parts: list[str] = []
    for f in files:
        path = Path(f)
        if path.parent.name and path.parent.name not in {'.', '..', ''}:
            parts.append(path.parent.name)
        if name := path.stem:
            parts.extend(re.split(r'[-_.]', name))

    # Find most common meaningful parts
    counter = Counter(parts)
    common = [
        word for word, _ in counter.most_common(5)
        if word.lower() not in EXCLUDED_PATH_PARTS and len(word) > 2
    ]

    if common:
        return '-'.join(common[:2]).lower()
    return None


def extract_user_prompts(entries: list[dict], limit: int = 5) -> list[str]:
    """Extract recent user prompts from transcript, filtering system messages."""
    prompts = []
    for entry in reversed(entries):
        if entry.get('type') != 'user':
            continue

        content = entry.get('message', {}).get('content', '')

        if isinstance(content, str) and content:
            if not is_system_message(content):
                prompts.append(content)
        elif isinstance(content, list):
            for block in content:
                if block.get('type') == 'text':
                    text = block.get('text', '')
                    if text and not is_system_message(text):
                        prompts.append(text)

        if len(prompts) >= limit:
            break

    return list(reversed(prompts))


def generate_topic(hook_input: dict) -> str:
    """Generate topic name from conversation context using multiple strategies."""

    # Strategy 1: Direct prompt (fastest for UserPromptSubmit)
    if direct_prompt := hook_input.get('prompt'):
        if topic := extract_topic_from_prompt(direct_prompt):
            return topic

    # Strategy 2: Transcript analysis
    entries = read_transcript(hook_input.get('transcript_path'))

    if not entries:
        # Fallback for direct prompt without pattern match
        if direct_prompt:
            words = [w for w in RE_WORD.findall(direct_prompt.lower()) if w not in STOPWORDS and len(w) > 2]
            if words:
                return words[0]
        return 'claude'

    # Strategy 3: Files being edited
    if topic := generate_topic_from_files(extract_files_from_tools(entries)):
        return topic

    # Strategy 4: User prompts from transcript
    prompts = extract_user_prompts(entries)
    for prompt in reversed(prompts):
        if topic := extract_topic_from_prompt(prompt):
            return topic

    # Strategy 5: Keyword fallback from last prompt
    if prompts:
        words = [w for w in RE_WORD.findall(prompts[-1].lower()) if w not in STOPWORDS and len(w) > 2]
        if words:
            return words[0]

    return 'claude'


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """Main entry point for the hook."""
    # Early exit if not in tmux
    if not os.environ.get('TMUX'):
        sys.exit(0)

    hook_input = read_hook_input()
    if not hook_input:
        sys.exit(0)

    event = hook_input.get('hook_event_name', hook_input.get('event', ''))

    if event == 'SessionStart':
        save_original_title()
    elif event == 'UserPromptSubmit':
        # Only on first prompt (skip if already has prefix)
        if not window_has_prefix():
            update_tmux_window(generate_topic(hook_input))
    elif event == 'Stop':
        update_tmux_window(generate_topic(hook_input))
    elif event == 'SessionEnd':
        restore_original_title()


if __name__ == '__main__':
    main()
