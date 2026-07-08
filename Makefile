# Makefile for DefenseTech Roadmap course

.PHONY: help install serve build lint test clean

help:
	@echo "Available targets:"
	@echo "  install  - install Python dependencies"
	@echo "  serve    - serve MkDocs site locally"
	@echo "  build    - build MkDocs site"
	@echo "  lint     - lint Markdown files"
	@echo "  test     - run structure tests"
	@echo "  clean    - remove build artifacts"

install:
	pip install -r requirements.txt

serve:
	mkdocs serve

build:
	mkdocs build

lint:
	markdownlint-cli2 "**/*.md" || true

test:
	python3 scripts/verify_structure.py

clean:
	rm -rf site/ __pycache__ .pytest_cache
