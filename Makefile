PYTHON ?= python3

.PHONY: install prepare test check-docs build check serve

install:
	$(PYTHON) -m pip install -r requirements-pages.txt

prepare:
	$(PYTHON) scripts/prepare-mkdocs.py

test:
	$(PYTHON) -m unittest discover -s tests -v

check-docs:
	$(PYTHON) scripts/check-docs.py

build: prepare
	mkdocs build --strict --config-file mkdocs.generated.yml

check: test check-docs build

serve: prepare
	mkdocs serve --config-file mkdocs.generated.yml
