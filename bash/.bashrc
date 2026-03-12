# If not running interactively, don't do anything (leave this at the top of this file)
[[ $- != *i* ]] && return

# All the default Omarchy aliases and functions
# (don't mess with these directly, just overwrite them here!)
source ~/.local/share/omarchy/default/bash/rc

# Add your own exports, aliases, and functions here.
#
# Make an alias for invoking commands you use constantly
# alias p='python'

if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
  tmux a -t default || exec tmux new -s default && exit;
fi

# Directory traversal.
alias .='pwd'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'
alias cd..='cd ..'

# Bind up/down arrow to history search.
bind '"\e[A":history-search-backward'
bind '"\e[B":history-search-forward'

# Old habits die hard.
alias vim='nvim'

# Load keys for keychain.
eval $(keychain --eval --quiet $(find ~/.ssh -maxdepth 1 -type f -name 'id_*' ! -name '*.pub'))

##################################################
# Path exports from 3rd parties.
##################################################

# Add nvm(Node Version Manager).
set -h # Work around "bash: hash: hashing disabled".
export NVM_DIR="$HOME/.config/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
set +h # Work around "bash: hash: hashing disabled".

export PATH="/home/jdelaigle/.lando/bin:$PATH"; #landopath
export PATH="$HOME/.config/composer/vendor/bin:$PATH"

source "/opt/google-cloud-sdk/completion.bash.inc"
source "/opt/google-cloud-sdk/path.bash.inc"

#export ANTHROPIC_BASE_URL="http://127.0.0.1:11434"
#export ANTHROPIC_AUTH_TOKEN="ollama"

alias ai-local='ollama run qwen3-coder'

ai-smart() {
  case "$*" in
    *summarize*|*summary*|*changelog*|*ticket*|*rewrite*|*notes*)
      echo "→ Using local model"
      ollama run qwen2.5-coder:14b-instruct "$@"
      ;;
    *)
      echo "→ Using Claude"
      claude "$@"
      ;;
  esac
}

# Local bin.
export PATH="$HOME/.local/bin:$PATH"

alias opencode-personal='\
XDG_DATA_HOME=$HOME/.local/share/opencode-personal \
XDG_CONFIG_HOME=$HOME/.config/opencode-personal \
env -u OPENAI_API_KEY \
opencode'


# opencode
export PATH=/home/jdelaigle/.opencode/bin:$PATH


# uv (Astral Python package manager)
source "$HOME/.local/bin/env"

alias claude-mem='bun "/home/jdelaigle/.claude/plugins/marketplaces/thedotmack/plugin/scripts/worker-service.cjs"'

export JAVA_HOME=/opt/android-studio/jbr
export PATH=$JAVA_HOME/bin:$PATH

export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$HOME/.maestro/bin

# Load secret keys.
[ -f ~/.secrets ] && source ~/.secrets

# Quick check: ensure Claude Code notification hooks are in settings.json
~/.dotfiles/ai/.claude/hooks/ensure-hooks.sh 2>/dev/null || echo "⚠ Claude hooks missing! Run: ~/.dotfiles/ai/.claude/hooks/ensure-hooks.sh --fix"
