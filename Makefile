# Makefile for DefenseTech Roadmap course

.PHONY: help install serve build lint test check check-duplicates check-references clean

help:
	@echo "Available targets:"
	@echo "  install          - install Python dependencies"
	@echo "  serve            - serve MkDocs site locally"
	@echo "  build            - build MkDocs site (strict)"
	@echo "  lint             - lint Markdown files"
	@echo "  test             - run structure + duplicate + reference + pytest checks"
	@echo "  check            - run module lab checks against solutions"
	@echo "  check-duplicates - fail if text or code is duplicated between modules"
	@echo "  check-references - fail if a referenced file does not exist"
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
	python3 scripts/check_duplicates.py --all
	python3 scripts/check_references.py
	python3 -m pytest -q

check:
	python3 scripts/run_lab_checks.py

check-duplicates:
	python3 scripts/check_duplicates.py --all

check-references:
	python3 scripts/check_references.py

clean:
	rm -rf site/ .mkdocs-build/ .pytest_cache __pycache__
