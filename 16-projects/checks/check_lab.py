#!/usr/bin/env python3
"""Перевірка лабораторної 16: шаблон портфоліо-проєкту.

Контракт (див. lab.md): `starter-template/` з README (мета, запуск,
архітектура, метрики, тести, обмеження), CI-workflow з pytest,
запускним кодом і тестом, який проходить.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
README_SECTIONS = ('## Мета', '## Швидкий старт', '## Архітектура', '## Метрики', '## Тести', '## Обмеження')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


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
    missing = [section for section in README_SECTIONS if section not in readme_text]
    if missing:
        fail('у README немає розділів: ' + ', '.join(missing))

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

    print('PASS: шаблон містить README, CI, піновані залежності та зелені тести')
    return 0


if __name__ == '__main__':
    sys.exit(main())
