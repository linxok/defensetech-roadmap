#!/usr/bin/env python3
"""Перевірка лабораторної 00: план навчання.

Контракт (див. lab.md): файл `plan.md` (або `learning-plan.md`) з
ціллю, треком, тижневим бюджетом, мілстоунами та метриками.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
CANDIDATES = ('plan.md', 'learning-plan.md', 'plan-example.md')
REQUIRED_SECTIONS = ('ціль', 'трек', 'бюджет', 'мілстоун', 'метрик')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    path = next((args.target / name for name in CANDIDATES if (args.target / name).is_file()), None)
    if path is None:
        fail(f'{args.target} не містить жодного з файлів: {", ".join(CANDIDATES)}')

    text = path.read_text(encoding='utf-8')
    lowered = text.lower()
    for section in REQUIRED_SECTIONS:
        if section not in lowered:
            fail(f'у плані немає розділу про «{section}»')

    rows = [line for line in text.splitlines() if line.count('|') >= 3 and line.startswith('|')]
    if len(rows) < 5:  # заголовок + розділювач + мінімум 3 мілстоуни
        fail(f'очікували таблицю мілстоунів із 3+ рядками, знайдено {len(rows)} рядків')

    if not re.search(r'\d+\s*(год|годин|h)\b', lowered):
        fail('немає тижневого бюджету годин у числах')

    print('PASS: план містить ціль, трек, бюджет, мілстоуни та метрики')
    return 0


if __name__ == '__main__':
    sys.exit(main())
