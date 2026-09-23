#!/usr/bin/env python3
"""Перевіряє, що файли, згадані в markdown, справді існують.

Шукаються:
- відносні markdown-посилання;
- шляхи в inline-коді (`` `examples/foo.py` ``) з відомим розширенням.

Шлях вважається битим, якщо він не резолвиться ні від каталогу
markdown-файлу, ні від кореня репозиторію, АЛЕ його батьківський
каталог існує (тобто це посилання на наявну теку, а не інструкція
створити новий файл на кшталт `src/main.cpp`).

Винятки — у `scripts/reference_allowlist.txt` (один підрядок на рядок).

Запуск:
    python3 scripts/check_references.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = Path(__file__).resolve().parent / 'reference_allowlist.txt'

EXCLUDE_DIRS = {'.git', '.github', '.kilo', '.mkdocs-build', 'site', 'venv', 'node_modules', '__pycache__'}

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
TOKEN_RE = re.compile(r'`([^`\n]+)`')
EXTENSIONS = {
    '.md', '.py', '.cpp', '.hpp', '.h', '.cc', '.mjs', '.tsx', '.ts', '.js',
    '.yml', '.yaml', '.json', '.txt', '.sh', '.rules', '.service', '.proto',
    '.toml', '.ini', '.html', '.mmd', '.csv', '.log', '.env',
}
SKIP_PREFIXES = ('http://', 'https://', 'mailto:', '#', '~', '/etc/', '/dev/', '/var/', '/tmp/')


def load_allowlist() -> list[str]:
    if not ALLOWLIST_FILE.is_file():
        return []
    return [
        line.strip()
        for line in ALLOWLIST_FILE.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob('*.md')
        if not any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts)
    )


def resolve(path: Path, raw: str) -> bool | None:
    """True — існує, False — бите посилання, None — не перевіряємо."""
    target = raw.split('#', 1)[0].strip()
    if not target or target.startswith(SKIP_PREFIXES) or '://' in target:
        return None
    if any(symbol in target for symbol in ('*', '{', '}', '<', '>')):
        return None

    parent_exists = False
    for base in (path.parent, ROOT):
        candidate = (base / target).resolve()
        if candidate.exists():
            return True
        if candidate.parent.is_dir():
            parent_exists = True
    return False if parent_exists else None


def find_violations() -> list[str]:
    allowlist = load_allowlist()
    violations: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding='utf-8', errors='replace')
        references: list[str] = LINK_RE.findall(text)
        references += [
            token.strip()
            for token in TOKEN_RE.findall(text)
            if '/' in token and Path(token.strip()).suffix in EXTENSIONS
        ]
        for raw in references:
            if any(entry in raw for entry in allowlist):
                continue
            if resolve(path, raw) is False:
                violations.append(f'{path.relative_to(ROOT)}: {raw}')
    return violations


def main() -> int:
    violations = find_violations()
    if violations:
        print('Биті посилання на файли:')
        for violation in violations:
            print(f'  {violation}')
        print('Якщо посилання навмисне (файл створює студент) — додайте його '
              'в scripts/reference_allowlist.txt')
        return 1
    print('Усі згадані файли існують.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
