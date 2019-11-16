PREFIX ?= /usr
DESTDIR ?=
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
PASSWORD_STORE ?= $(HOME)/.password-store
PASSWORD_STORE_EXTENSION_DIR ?= $(PASSWORD_STORE)/.extensions
BASHCOMPDIR ?= /etc/bash_completion.d
SUDO ?= sudo

all:
	@echo "pass-get is a shell script and does not need compilation, it can be simply executed."
	@echo ""
	@echo "To install it try \"make install\" instead."
	@echo
	@echo "To run pass get one needs to have some tools installed on the system:"
	@echo "     password store"
	@echo "     tail"
	@echo "     grep"
	@echo "     sed"
	@echo "     xclip"

install: install-completion
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)"
	@install -v -m 0755 pass-get.bash "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/get.bash"
	@echo
	@echo "pass-get is installed succesfully"
	@echo

install-user: install-completion
	@install -v -d "$(DESTDIR)$(PASSWORD_STORE_EXTENSION_DIR)"
	@install -v -m 0755 pass-get.bash "$(DESTDIR)$(PASSWORD_STORE_EXTENSION_DIR)/get.bash"
	@echo
	@echo "pass-get is installed succesfully to $(DESTDIR)$(PASSWORD_STORE_EXTENSION_DIR)"
	@echo
	@echo "Don't forget to add PASSWORD_STORE_ENABLE_EXTENSIONS=true to you shell environment"
	@echo

install-completion:
	@$(SUDO) install -v -d -m 0755 "$(DESTDIR)$(BASHCOMPDIR)/"
	@$(SUDO) install -v -m 644 pass-get.completion "$(DESTDIR)$(BASHCOMPDIR)/pass-get"

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/get.bash" \
		"$(DESTDIR)$(BASHCOMPDIR)/pass-get"

lint:
	shellcheck -s bash src/get.bash

.PHONY: install uninstall lint
