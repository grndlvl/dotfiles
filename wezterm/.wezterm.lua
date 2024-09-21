-- Pull in the wezterm API
local wezterm = require 'wezterm'

wezterm.log_error('Version ' .. wezterm.version)

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

-- For example, changing the color scheme:
config.color_scheme = 'Monokai (dark) (terminal.sexy)'
config.colors = {
  background = '#272822'
}

config.hide_tab_bar_if_only_one_tab = true
config.enable_wayland = false

config.window_padding = {
}

-- and finally, return the configuration to wezterm
return config
