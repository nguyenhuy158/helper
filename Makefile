APP_NAME = helper-cli
VENV_ACTIVATE = . venv/bin/activate &&

.PHONY: help build publish test-publish test-publish-patch test-publish-minor test-publish-major patch minor major clean push-tags rsync lint format test all arch d env f ip kill nix pubip run si sp v

# Default target: show help
help:
	@echo "Available commands:"
	@echo "  help                - Show this help message"
	@echo "  build               - Build the package"
	@echo "  publish             - Publish to PyPI (runs patch first)"
	@echo "  test-publish        - Publish to Test PyPI (runs patch first)"
	@echo "  test-publish-patch  - Publish patch version to Test PyPI"
	@echo "  test-publish-minor  - Publish minor version to Test PyPI"
	@echo "  test-publish-major  - Publish major version to Test PyPI"
	@echo "  patch               - Bump patch version (0.1.0 → 0.1.1)"
	@echo "  minor               - Bump minor version (0.1.0 → 0.2.0)"
	@echo "  major               - Bump major version (1.0.0 → 2.0.0)"
	@echo "  clean               - Clean build artifacts"
	@echo "  lint                - Run pylint on the codebase"
	@echo "  format              - Format code using Black"
	@echo "  test                - Run pytest test suite"
	@echo "  push-tags           - Push all git tags to remote"
	@echo ""
	@echo "CLI Commands (run with helper):"
	@echo "  all      - Show all info"
	@echo "  arch     - Show CPU architecture"
	@echo "  d        - Docker management"
	@echo "  env      - Environment variables"
	@echo "  f        - File operations"
	@echo "  ip       - Internal IP"
	@echo "  kill     - Kill processes by name/port"
	@echo "  nix      - NixOS info"
	@echo "  pubip    - Public IP"
	@echo "  run      - Run snippets"
	@echo "  rsync    - Rsync file synchronization"
	@echo "  si       - System info"
	@echo "  sp       - Speed test"
	@echo "  v        - Virtual environments"

build: lint
	$(VENV_ACTIVATE) python -m build

publish:
	make patch
	$(VENV_ACTIVATE) twine upload dist/*

test-publish:
	make patch
	$(VENV_ACTIVATE) twine upload --repository testpypi dist/*

test-publish-patch:
	$(VENV_ACTIVATE) bump2version patch
	make clean
	make build
	$(VENV_ACTIVATE) twine upload --repository testpypi dist/*

test-publish-minor:
	$(VENV_ACTIVATE) bump2version minor
	make clean
	make build
	$(VENV_ACTIVATE) twine upload --repository testpypi dist/*

test-publish-major:
	$(VENV_ACTIVATE) bump2version major
	make clean
	make build
	$(VENV_ACTIVATE) twine upload --repository testpypi dist/*

# Tự tăng version patch: 0.1.0 → 0.1.1
patch:
	$(VENV_ACTIVATE) bump2version patch
	make clean
	make build

# Tăng version minor: 0.1.0 → 0.2.0
minor:
	$(VENV_ACTIVATE) bump2version minor
	make clean
	make build

# Tăng version major: 1.0.0 → 2.0.0
major:
	$(VENV_ACTIVATE) bump2version major
	make clean
	make build

clean:
	rm -rf dist build *.egg-info

lint:
	$(VENV_ACTIVATE) python -m pip install -e .[dev]
	$(VENV_ACTIVATE) pylint helper

format:
	$(VENV_ACTIVATE) python -m pip install -e .[dev]
	$(VENV_ACTIVATE) black helper

test:
	$(VENV_ACTIVATE) python -m pip install -e .[dev]
	$(VENV_ACTIVATE) pytest

push-tags:
	git push --tags origin

rsync:
	helper rsync

# CLI command shortcuts
all:
	helper all

arch:
	helper arch

d:
	helper d

env:
	helper env

f:
	helper f

ip:
	helper ip

kill:
	helper kill

nix:
	helper nix

pubip:
	helper pubip

run:
	helper run

si:
	helper si

sp:
	helper sp

v:
	helper v
