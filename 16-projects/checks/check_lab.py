#!/usr/bin/env python3
"""Перевірка лабораторної 16: шаблон портфоліо-проєкту.

Контракт (див. lab.md): `starter-template/` з README (мета, запуск,
архітектура, метрики, тести, обмеження), де кожен розділ має змістовний
абзац без заглушок і в README є числа; CI-workflow з pytest, запускним
кодом і тестом, який проходить.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
README_SECTIONS = ('## Мета', '## Швидкий старт', '## Архітектура', '## Метрики', '## Тести', '## Обмеження')
PLACEHOLDERS = ('одне речення', 'опишіть', 'що свідомо не реалізовано', 'ваша відповідь', 'todo', 'lorem ipsum')
MIN_PROSE_CHARS = 40


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def has_heading(text: str, heading: str) -> bool:
    return re.search(rf'^{re.escape(heading)}\s*$', text, flags=re.MULTILINE) is not None


def section_body(text: str, heading: str) -> str:
    match = re.search(rf'^{re.escape(heading)}\s*$', text, flags=re.MULTILINE)
    if match is None:
        return ''
    rest = text[match.end():]
    next_heading = re.search(r'^## ', rest, flags=re.MULTILINE)
    return rest if next_heading is None else rest[:next_heading.start()]


def prose_lines(section: str) -> list[str]:
    """Рядки поза код-блоками, таблицями, списками й заголовками."""
    result = []
    in_code = False
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith(('|', '#', '- ', '* ', '> ')):
            continue
        result.append(stripped)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    template = args.target / 'starter-template'
    if not template.is_dir():
        fail(f'{template} не існує')

    readme = template / 'README.md'
    if not readme.is_file():
        fail('немає README.md')
    readme_text = readme.read_text(encoding='utf-8')
    missing = [section for section in README_SECTIONS if not has_heading(readme_text, section)]
    if missing:
        fail('у README немає розділів: ' + ', '.join(missing))

    lowered = readme_text.lower()
    placeholders = [marker for marker in PLACEHOLDERS if marker in lowered]
    if placeholders:
        fail('README містить шаблонні заглушки: ' + ', '.join(placeholders))

    for section in README_SECTIONS:
        body = section_body(readme_text, section)
        if not any(len(line) >= MIN_PROSE_CHARS for line in prose_lines(body)):
            fail(f'{section}: потрібен змістовний абзац (≥{MIN_PROSE_CHARS} символів), а не заглушка')

    if not re.search(r'\d', readme_text):
        fail('у README немає жодного числа (метрики, версії, ліміти)')

    ci = template / '.github' / 'workflows' / 'ci.yml'
    if not ci.is_file():
        fail('немає .github/workflows/ci.yml')
    ci_text = ci.read_text(encoding='utf-8')
    if 'pytest' not in ci_text:
        fail('CI має запускати pytest')
    if 'actions/checkout' not in ci_text:
        fail('CI має робити checkout')

    test_file = template / 'tests' / 'test_smoke.py'
    if not test_file.is_file():
        fail('немає tests/test_smoke.py')
    if 'def test_' not in test_file.read_text(encoding='utf-8'):
        fail('тестовий файл не містить тестів')

    requirements = template / 'requirements.txt'
    if not requirements.is_file():
        fail('немає requirements.txt')
    if '==' not in requirements.read_text(encoding='utf-8'):
        fail('залежності мають бути піновані (==)')

    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests', '-q'],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=template,
        check=False,
    )
    if result.returncode != 0:
        fail(f'тести шаблону не проходять:\n{result.stdout[-500:]}{result.stderr[-300:]}')

    print('PASS: README змістовний (без заглушок), CI, піновані залежності та зелені тести')
    return 0


if __name__ == '__main__':
    sys.exit(main())
