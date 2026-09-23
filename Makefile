# Makefile for DefenseTech Roadmap course

.PHONY: help install serve build lint test check check-duplicates clean

help:
	@echo "Available targets:"
	@echo "  install          - install Python dependencies"
	@echo "  serve            - serve MkDocs site locally"
	@echo "  build            - build MkDocs site (strict)"
	@echo "  lint             - lint Markdown files"
	@echo "  test             - run structure + duplicate + pytest checks"
	@echo "  check            - run module lab checks against solutions"
	@echo "  check-duplicates - fail if text is duplicated between modules"
	@echo "  clean            - remove build artifacts"

install:
	pip install -r requirements.txt -r requirements-dev.txt

serve:
	python3 scripts/prepare_docs.py
	mkdocs serve -f .mkdocs-build/mkdocs.yml

build:
	python3 scripts/prepare_docs.py
	mkdocs build --strict -f .mkdocs-build/mkdocs.yml

lint:
	npx --yes markdownlint-cli2

test:
	python3 scripts/verify_structure.py
	python3 scripts/check_duplicates.py
	python3 -m pytest -q

check:
	python3 scripts/run_lab_checks.py

check-duplicates:
	python3 scripts/check_duplicates.py

clean:
	rm -rf site/ .mkdocs-build/ .pytest_cache __pycache__
