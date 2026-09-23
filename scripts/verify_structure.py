#!/usr/bin/env python3
"""Перевіряє структуру курсу та друкує метрики наповнення.

Критерії (див. CONTENT_STANDARD.md):
- 18 модулів і обов'язкові файли в кожному;
- статус у README кожного модуля;
- наявність checks/check_lab.py і solution/ у кожному модулі;
- відсутність видалених шаблонних файлів (further-reading.md).

Виключення зі сканування: .git, .kilo, venv, site, .mkdocs-build.
"""

from __future__ import annotations

import os
import re
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

MODULE_FILES = (
    'README.md',
    'detailed-guide.md',
    'lab.md',
    'practice.md',
    'homework.md',
    'checklist.md',
    'self-assessment.md',
    'faq.md',
    'interview-questions.md',
    'cheat-sheet.md',
    'resources.md',
    'templates.md',
    'mini-project.md',
    'project-ideas.md',
    'real-world-scenario.md',
)

ROOT_FILES = (
    'README.md',
    'LICENSE',
    'CONTRIBUTING.md',
    'ROADMAP.md',
    'QUICKSTART.md',
    'STUDY_SCHEDULE.md',
    'CERTIFICATION_CHECKLIST.md',
    'CONTENT_STANDARD.md',
    'mkdocs.yml',
    'requirements.txt',
    'requirements-dev.txt',
    'requirements-docs.txt',
    'requirements-optional.txt',
)

REMOVED_MODULE_FILES = ('further-reading.md',)
STATUS_RE = re.compile(r'>\s*Статус:\s*(stub|outline|complete)')


def module_dirs() -> list[Path]:
    return sorted(
        path
        for path in BASE.iterdir()
        if path.is_dir() and len(path.name) > 2 and path.name[:2].isdigit() and path.name[2] == '-'
    )


def markdown_stats() -> tuple[int, int]:
    count = 0
    lines = 0
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for name in filenames:
            if name.endswith('.md'):
                count += 1
                with open(Path(dirpath) / name, encoding='utf-8', errors='ignore') as handle:
                    lines += len(handle.readlines())
    return count, lines


def main() -> int:
    errors: list[str] = []
    modules = module_dirs()

    expected = [f'{index:02d}-' for index in range(18)]
    found = [module.name[:3] for module in modules]
    for prefix in expected:
        if prefix not in found:
            errors.append(f'Module {prefix} missing')

    for name in ROOT_FILES:
        if not (BASE / name).exists():
            errors.append(f'{name} missing')

    statuses: dict[str, int] = {}
    for module in modules:
        for name in MODULE_FILES:
            if not (module / name).is_file():
                errors.append(f'{module.name}/{name} missing')
        for name in REMOVED_MODULE_FILES:
            if (module / name).exists():
                errors.append(f'{module.name}/{name} must be removed')
        if not (module / 'checks' / 'check_lab.py').is_file():
            errors.append(f'{module.name}/checks/check_lab.py missing')
        if not (module / 'solution').is_dir():
            errors.append(f'{module.name}/solution missing')

        readme = module / 'README.md'
        if readme.is_file():
            match = STATUS_RE.search(readme.read_text(encoding='utf-8'))
            if match is None:
                errors.append(f'{module.name}/README.md has no status line')
            else:
                statuses[match.group(1)] = statuses.get(match.group(1), 0) + 1

    md_count, line_count = markdown_stats()

    print(f'Modules: {len(modules)}/18')
    print(f'Module statuses: {statuses or "none"}')
    print(f'Markdown files: {md_count}')
    print(f'Markdown lines: {line_count}')
    print(f'Approx pages: {line_count // 50}')

    if errors:
        print('ERRORS:')
        for error in errors:
            print(f'  - {error}')
        return 1

    print('All checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
