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


def milestone_rows(text: str) -> list[list[str]]:
    """Рядки таблиці мілстоунів без заголовка й розділювача."""
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith('|') or line.count('|') < 5:
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if all(re.fullmatch(r'[-: ]*', cell) for cell in cells):
            continue
        if any('критерій завершення' in cell.lower() or cell.lower() == 'модулі' for cell in cells):
            continue
        rows.append(cells)
    return rows


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

    milestones = milestone_rows(text)
    if len(milestones) < 8:
        fail(f'очікували 8+ мілстоунів, знайшли {len(milestones)}')

    without_horizon = [row for row in milestones if not re.search(r'\d', ' '.join(row[:2]))]
    if without_horizon:
        fail('кожен мілстоун має містити тижні або дату в перших колонках')

    with_criterion = sum(
        1
        for row in milestones
        if re.search(r'(`|checks/|\.py\b|PASS|\bdocker\b|ACK)', ' '.join(row[2:]))
    )
    if with_criterion < 5:
        fail(f'лише {with_criterion} мілстоунів мають бінарний критерій (команда/артефакт); треба 5+')

    hours = set(re.findall(r'(\d+)\s*(?:год|годин)', lowered))
    if len(hours) < 2:
        fail('немає тижневого бюджету годин: потрібні щонайменше два числа з «год/годин»')

    print('PASS: план містить ціль, трек, бюджет, мілстоуни та метрики')
    return 0


if __name__ == '__main__':
    sys.exit(main())
