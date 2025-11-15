APP_NAME = helper-cli

.PHONY: help build publish test-publish test-publish-patch test-publish-minor test-publish-major patch minor major clean all arch d env f ip kill nix pubip run si sp v

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
	@echo "  si       - System info"
	@echo "  sp       - Speed test"
	@echo "  v        - Virtual environments"

build:
	python -m build

publish:
	make patch
	twine upload dist/*

test-publish:
	make patch
	twine upload --repository testpypi dist/*

test-publish-patch:
	bump2version patch
	make clean
	make build
	twine upload --repository testpypi dist/*

test-publish-minor:
	bump2version minor
	make clean
	make build
	twine upload --repository testpypi dist/*

test-publish-major:
	bump2version major
	make clean
	make build
	twine upload --repository testpypi dist/*

# Tự tăng version patch: 0.1.0 → 0.1.1
patch:
	bump2version patch
	make clean
	make build

# Tăng version minor: 0.1.0 → 0.2.0
minor:
	bump2version minor
	make clean
	make build

# Tăng version major: 1.0.0 → 2.0.0
major:
	bump2version major
	make clean
	make build

clean:
	rm -rf dist build *.egg-info

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
