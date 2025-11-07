APP_NAME = helper-cli

.PHONY: build publish patch minor major clean

build:
	python -m build

publish:
	make patch
	twine upload dist/*

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
