#!/bin/bash
# Ensures custom hooks are present in ~/.claude/settings.json
# Run after OMC updates or if notifications stop working.
#
# Usage: ./ensure-hooks.sh [--fix]
#   Without --fix: checks and warns
#   With --fix: merges hooks into settings.json

SETTINGS="$HOME/.claude/settings.json"
HOOKS_DEF="$(dirname "$0")/required-hooks.json"

python3 - "$SETTINGS" "$HOOKS_DEF" "$1" <<'PYEOF'
import json, sys, os

settings_path = sys.argv[1]
hooks_path = sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else ""

with open(hooks_path) as f:
    required = json.load(f)

with open(settings_path) as f:
    settings = json.load(f)

hooks = settings.get("hooks", {})
missing = []
for event in required:
    if event not in hooks or not hooks[event]:
        missing.append(event)

if not missing:
    print("All custom hooks present in settings.json")
    sys.exit(0)

print(f"MISSING hooks: {', '.join(missing)}")

if mode != "--fix":
    print("Run with --fix to restore them automatically")
    sys.exit(1)

# Expand ~ in command paths
home = os.path.expanduser("~")
def expand_commands(obj):
    if isinstance(obj, dict):
        return {k: expand_commands(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_commands(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace("~/", home + "/")
    return obj

required = expand_commands(required)

if "hooks" not in settings:
    settings["hooks"] = {}

for event, config in required.items():
    settings["hooks"][event] = config

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print("Hooks restored in settings.json")
PYEOF
