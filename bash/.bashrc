# If not running interactively, don't do anything (leave this at the top of this file)
[[ $- != *i* ]] && return

# All the default Omarchy aliases and functions
# (don't mess with these directly, just overwrite them here!)
source ~/.local/share/omarchy/default/bash/rc

PATH="~/.local/bin":$PATH

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


export CLAUDE_GLOBAL_INSTRUCTIONS_FILE="$HOME/.config/ai/GLOBAL.md"
claude() {
  command claude \
    --system-prompt "$(cat "$CLAUDE_GLOBAL_INSTRUCTIONS_FILE")" \
    "$@"
}

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

