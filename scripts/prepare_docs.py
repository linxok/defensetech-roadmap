#!/usr/bin/env python3
"""Готує дзеркало контенту репозиторію для MkDocs.

MkDocs не дозволяє тримати `docs_dir` у корені репозиторію, тому сайт
збирається з копії: `.mkdocs-build/docs/`. Джерело правди — корінь
репозиторію; скрипт лише копіює файли й конфіг.

Запуск:
    python3 scripts/prepare_docs.py
    mkdocs build --strict -f .mkdocs-build/mkdocs.yml
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BUILD = BASE / '.mkdocs-build'
DEST = BUILD / 'docs'

EXCLUDE_DIRS = {
    '.git',
    '.github',
    '.kilo',
    '.mkdocs-build',
    '.pytest_cache',
    '.venv',
    '__pycache__',
    'node_modules',
    'site',
    'venv',
}
EXCLUDE_FILES = {'.DS_Store'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo'}


def ignore(directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in EXCLUDE_DIRS
        or name in EXCLUDE_FILES
        or Path(name).suffix in EXCLUDE_SUFFIXES
    }


def main() -> int:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(BASE, DEST, ignore=ignore, symlinks=True)
    shutil.copy2(BASE / 'mkdocs.yml', BUILD / 'mkdocs.yml')

    pages = sum(1 for _ in DEST.rglob('*.md'))
    files = sum(1 for p in DEST.rglob('*') if p.is_file())
    print(f'Prepared docs mirror: {DEST}')
    print(f'Markdown pages: {pages}; files total: {files}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
