current_directory := $(shell pwd)
home_directory := ${HOME}

development:
	docker run -v "$(current_directory):/dotfiles" -ti debian:bullseye-slim sh -c "apt update && apt install make stow -y && cd /dotfiles && make install && bash"

install-depedencies:
	sudo apt update && sudo apt install \
		stow

install:
	find $(current_directory) -mindepth 1 -maxdepth 1 -type d \( ! -regex '.*/\..*' \) |  sed 's!.*/!!' | xargs stow --dir="$(current_directory)" --target="$(home_directory)" --restow

uninstall:
	find $(current_directory) -mindepth 1 -maxdepth 1 -type d \( ! -regex '.*/\..*' \) |  sed 's!.*/!!' | xargs stow --dir="$(current_directory)" --target="$(home_directory)" -D
