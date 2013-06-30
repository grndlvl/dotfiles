if `tty -s`; then
   mesg n
fi

export TERM="xterm-256color"

# Path to your oh-my-zsh configuration.
export ZSH=$HOME/.zsh

# Set to the name theme to load.
# Look in ~/.oh-my-zsh/themes/
ZSH_THEME="af-magic"

# Comment this out to disable weekly auto-update checks
export DISABLE_AUTO_UPDATE="true"

# Which plugins would you like to load? (plugins can be found in ~/.zsh/plugins/*)
# Example format: plugins=(rails git textmate ruby lighthouse)
plugins=(composer debian extract git git-flow jira)

source $ZSH/oh-my-zsh.sh

setopt -o extended_glob

# bind UP and DOWN arrow keys
bindkey "^[[A" history-search-backward
bindkey "^[[B" history-search-forward

# Directory traversal aliases.
alias .='pwd'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'
alias cd..='cd ..'

# more effective clear
alias clear='clear && clear'

# some more ls aliases
alias ll='ls -l'
alias la='ls -A'
alias l='ls -CF'

PATH=$PATH:$HOME/.bin
export PATH

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"
