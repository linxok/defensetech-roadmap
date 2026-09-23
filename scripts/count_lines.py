#!/usr/bin/env python3
"""Рахує markdown-метрики курсу, ігноруючи службові каталоги."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {
    '.git',
    '.github',
    '.kilo',
    '.mkdocs-build',
    '.pytest_cache',
    '__pycache__',
    'node_modules',
    'site',
    'venv',
}


def main() -> int:
    md_count = 0
    line_count = 0
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for name in filenames:
            if name.endswith('.md'):
                md_count += 1
                with open(Path(dirpath) / name, encoding='utf-8', errors='ignore') as handle:
                    line_count += len(handle.readlines())
    print(f'Markdown files: {md_count}')
    print(f'Markdown lines: {line_count}')
    print(f'Approx pages: {line_count // 50}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
