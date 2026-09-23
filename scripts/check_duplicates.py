#!/usr/bin/env python3
"""Шукає дослівно дубльовані текстові блоки між модулями курсу.

Правило CONTENT_STANDARD.md: один і той самий текстовий блок не можна
повторювати у двох модулях. Спільні матеріали живуть у docs/ і
підключаються посиланням.

Запуск:
    python3 scripts/check_duplicates.py [--min-length 120] [--all]

    --all  також перевіряти дублювання коду (за замовчуванням — лише текст)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict
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

ALLOWLIST_FILE = Path(__file__).resolve().parent / 'duplicate_allowlist.txt'

MODULE_RE = re.compile(r'^\d{2}-')


def is_module_dir(name: str) -> bool:
    return bool(MODULE_RE.match(name))


def iter_markdown() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(BASE):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.'))
        for name in sorted(filenames):
            if name.endswith('.md'):
                files.append(Path(dirpath) / name)
    return files


def normalize(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def blocks_of(path: Path, include_code: bool) -> list[tuple[str, str]]:
    """Повертає (вид, нормалізований текст) для блоків сторінки."""
    raw = path.read_text(encoding='utf-8', errors='ignore')
    text_without_code = re.sub(r'```.*?```', '\n\n', raw, flags=re.DOTALL)
    result: list[tuple[str, str]] = [('text', normalize(b)) for b in text_without_code.split('\n\n')]
    if include_code:
        for code in re.findall(r'```[^\n]*\n(.*?)```', raw, flags=re.DOTALL):
            result.append(('code', normalize(code)))
    return result


def owner_module(path: Path) -> str | None:
    rel = path.relative_to(BASE)
    if rel.parts and is_module_dir(rel.parts[0]):
        return rel.parts[0]
    return None


def load_allowlist() -> list[str]:
    if not ALLOWLIST_FILE.exists():
        return []
    lines = []
    for line in ALLOWLIST_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(normalize(line))
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-length', type=int, default=120)
    parser.add_argument('--all', action='store_true', help='перевіряти також код-блоки')
    args = parser.parse_args()

    allowlist = load_allowlist()
    seen: dict[tuple[str, str], list[str]] = defaultdict(list)
    labels: dict[tuple[str, str], str] = {}

    for path in iter_markdown():
        module = owner_module(path)
        if module is None:
            continue
        for kind, block in blocks_of(path, include_code=args.all):
            if len(block) < args.min_length:
                continue
            if any(token in block for token in allowlist):
                continue
            key = (kind, block)
            seen[key].append(str(path.relative_to(BASE)))
            labels[key] = kind

    violations = []
    for key, files in seen.items():
        modules = sorted({f.split('/')[0] for f in files})
        if len(modules) > 1:
            violations.append((key, files, modules))

    identical: dict[str, list[str]] = defaultdict(list)
    for path in iter_markdown():
        module = owner_module(path)
        if module is None:
            continue
        digest = hashlib.sha256(normalize(path.read_text(encoding='utf-8', errors='ignore')).encode()).hexdigest()
        identical[digest].append(str(path.relative_to(BASE)))

    for digest, files in sorted(identical.items()):
        modules = sorted({f.split('/')[0] for f in files})
        if len(modules) > 1:
            violations.append(((('file', digest), files, modules)))

    if violations:
        print(f'Знайдено {len(violations)} дубльованих блок(ів):')
        for key, files, modules in violations:
            kind = key[0]
            preview = key[1][:100]
            print(f'\n[{kind}] у модулях: {", ".join(modules)}')
            print(f'  {preview}...')
            for f in files[:4]:
                print(f'    - {f}')
            if len(files) > 4:
                print(f'    ... і ще {len(files) - 4}')
        print('\nПорада: винесіть спільний текст у docs/ і дайте посилання.')
        print('Винятки додаються в scripts/duplicate_allowlist.txt.')
        return 1

    print('Дублікатів не знайдено.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
