#!/usr/bin/env python3
"""Перевірка лабораторної 13: генерація місії з валідацією.

Контракт (див. lab.md): `mission_prompt.py` з моделями `Waypoint`,
`Mission`, функціями `offline_mission` і `generate`. Мережа не потрібна:
перевіряється офлайн-генератор і валідація.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'mission_prompt.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_mission', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_mission'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується без API-ключа: {exc!r}')
    for attr in ('Waypoint', 'Mission', 'offline_mission', 'generate'):
        if not hasattr(module, attr):
            fail(f'у модулі немає `{attr}`')
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module = load_module(args.target)
    from pydantic import ValidationError

    mission = module.offline_mission(50.4501, 30.5234, 100.0, 5)
    if len(mission.waypoints) != 5:
        fail(f'очікували 5 waypoint-ів, отримано {len(mission.waypoints)}')
    if [w.seq for w in mission.waypoints] != [0, 1, 2, 3, 4]:
        fail('seq мають бути неперервними від 0')
    for waypoint in mission.waypoints:
        if abs(waypoint.lat - 50.4501) > 0.01 or abs(waypoint.lon - 30.5234) > 0.01:
            fail(f'waypoint поза межами району: {waypoint}')
        if waypoint.alt != 100.0:
            fail(f'невірна висота: {waypoint.alt}')

    for bad in ({'seq': 0, 'lat': 50.0, 'lon': 30.0, 'alt': 900.0},
                {'seq': 0, 'lat': 100.0, 'lon': 30.0, 'alt': 100.0}):
        try:
            module.Waypoint(**bad)
        except ValidationError:
            continue
        fail(f'Waypoint мав відхилити {bad}')

    os.environ.pop('OPENAI_API_KEY', None)
    fallback = module.generate(50.4501, 30.5234, 100.0, 4)
    if len(fallback.waypoints) != 4:
        fail('generate без API-ключа має використати офлайн-генератор')

    print('PASS: місія валідується, офлайн-режим працює')
    return 0


if __name__ == '__main__':
    sys.exit(main())
