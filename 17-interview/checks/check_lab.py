#!/usr/bin/env python3
"""Перевірка лабораторної 17: заповнені відповіді для співбесіди.

Контракт (див. lab.md): файл з відповідями (за замовчуванням
`solution/answers-example.md`, у вашому репозиторії — `answers.md`)
містить 10+ розділів, жодних заглушок і конкретику в кожній
відповіді.

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
CANDIDATES = ('answers-example.md', 'answers.md', 'interview-answers.md')
MIN_SECTIONS = 10
MIN_SECTION_CHARS = 250


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    path = next((args.target / name for name in CANDIDATES if (args.target / name).is_file()), None)
    if path is None:
        fail(f'{args.target} не містить файлу відповідей ({", ".join(CANDIDATES)})')

    text = path.read_text(encoding='utf-8')
    if '_Ваша відповідь тут' in text or '- ...' in text:
        fail('у файлі залишились шаблонні заглушки')

    sections = re.split(r'\n## ', text)
    answers = [section.strip() for section in sections[1:] if section.strip()]
    if len(answers) < MIN_SECTIONS:
        fail(f'потрібно {MIN_SECTIONS}+ відповідей, знайдено {len(answers)}')

    short = [a.splitlines()[0] for a in answers if len(a) < MIN_SECTION_CHARS]
    if short:
        fail('відповіді закороткі (без конкретики): ' + '; '.join(short[:3]))

    lowered = text.lower()
    if 'system design' not in lowered and 'архітектур' not in lowered:
        fail('немає жодного system design / архітектурного кейсу')

    with_numbers = sum(1 for a in answers if re.search(r'\d', a))
    if with_numbers < MIN_SECTIONS // 2:
        fail('замало відповідей з конкретними числами, параметрами чи версіями')

    print(f'PASS: {len(answers)} відповідей, заглушок немає, конкретика присутня')
    return 0


if __name__ == '__main__':
    sys.exit(main())
