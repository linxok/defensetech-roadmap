#!/usr/bin/env python3
"""Перевірка лабораторної 08: менеджер параметрів PX4.

Контракт (див. lab.md): `px4_param.py` з чистими функціями
`validate_name`, `format_param`, `format_params` і CLI `get/set/list`.
MAVSDK-частина потребує SITL, тому офлайн перевіряється логіка та CLI.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
Param = namedtuple('Param', 'name value')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'px4_param.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_px4', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_px4'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується: {exc!r}')
    for attr in ('validate_name', 'format_param', 'format_params', 'parse_args'):
        if not hasattr(module, attr):
            fail(f'у модулі немає `{attr}`')
    return module, path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module, path = load_module(args.target)

    if module.validate_name('MPC_XY_VEL_MAX') != 'MPC_XY_VEL_MAX':
        fail('валідне імʼя параметра відхилено')
    for bad in ('mpc_xy', 'MPC-XY', 'A' * 40, ''):
        try:
            module.validate_name(bad)
        except SystemExit:
            continue
        fail(f'невалідне імʼя {bad!r} не відхилено')

    formatted = module.format_param('MPC_XY_P', 0.85)
    if 'MPC_XY_P' not in formatted or '0.85' not in formatted:
        fail(f'format_param повертає некоректний рядок: {formatted!r}')

    lines = module.format_params([Param('B_PARAM', 2.0), Param('A_PARAM', 1.0)])
    if lines != ['A_PARAM = 1', 'B_PARAM = 2']:
        fail(f'format_params має сортувати та форматувати: {lines}')

    parsed = module.parse_args(['get', 'MPC_XY_P'])
    if parsed.command != 'get' or parsed.name != 'MPC_XY_P':
        fail('CLI не розбирає `get MPC_XY_P`')

    help_result = subprocess.run(
        [sys.executable, str(path), '--help'],
        capture_output=True,
        timeout=30,
        check=False,
    )
    if help_result.returncode != 0:
        fail(f'`--help` завершується з кодом {help_result.returncode}')

    print('PASS: валідація імен, форматування та CLI працюють')
    return 0


if __name__ == '__main__':
    sys.exit(main())
