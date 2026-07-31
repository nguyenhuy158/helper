.PHONY: help run build patch minor major pub test lint fmt clean

VERSION := $(shell cat VERSION)

help:
	@echo "Available commands:"
	@echo "  make run   - Run the tool locally"
	@echo "  make build - Build the package"
	@echo "  make patch - Increment patch version and tag"
	@echo "  make minor - Increment minor version and tag"
	@echo "  make major - Increment major version and tag"
	@echo "  make pub   - Build and publish to PyPI"
	@echo "  make test  - Run tests"
	@echo "  make lint  - Run ruff check + format check"
	@echo "  make fmt   - Auto-format code with ruff"
	@echo "  make clean - Clean build artifacts"

run:
	export PYTHONPATH=$${PYTHONPATH}:$(shell pwd)/src && python3 -m helper.main

build:
	python3 -m build

patch:
	@echo "Current version: $(VERSION)"
	@python3 -c "v = '$(VERSION)'.split('.'); v[2] = str(int(v[2]) + 1); print('.'.join(v))" > VERSION
	@$(MAKE) commit-version

minor:
	@echo "Current version: $(VERSION)"
	@python3 -c "v = '$(VERSION)'.split('.'); v[1] = str(int(v[1]) + 1); v[2] = '0'; print('.'.join(v))" > VERSION
	@$(MAKE) commit-version

major:
	@echo "Current version: $(VERSION)"
	@python3 -c "v = '$(VERSION)'.split('.'); v[0] = str(int(v[0]) + 1); v[1] = '0'; v[2] = '0'; print('.'.join(v))" > VERSION
	@$(MAKE) commit-version

commit-version:
	@NEW_VERSION=$$(cat VERSION); \
	git add VERSION; \
	git commit -m "chore: bump version to $$NEW_VERSION"; \
	git tag v$$NEW_VERSION; \
	git push origin pypi --tags

pub: clean build
	python3 -m twine upload dist/*

test:
	export PYTHONPATH=$${PYTHONPATH}:$(shell pwd)/src && pytest

lint:
	ruff check .
	ruff format --check .

fmt:
	ruff format .
	ruff check --fix .

clean:
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/
