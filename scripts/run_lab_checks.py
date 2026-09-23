#!/usr/bin/env python3
"""Запускає checks/check_lab.py кожного модуля проти його solution/.

Модуль без `checks/check_lab.py` позначається як SKIP — це сигнал, що
лабораторна ще не має автоматичної перевірки (див. CONTENT_STANDARD.md).

Запуск:
    python3 scripts/run_lab_checks.py [--module 06-mavlink]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MODULE_RE = lambda name: len(name) > 2 and name[:2].isdigit() and name[2] == '-'


def modules() -> list[Path]:
    return sorted(
        (path for path in BASE.iterdir() if path.is_dir() and MODULE_RE(path.name)),
        key=lambda path: path.name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', help='перевірити лише один модуль')
    args = parser.parse_args()

    selected = [m for m in modules() if not args.module or m.name == args.module]
    if not selected:
        print(f'модуль {args.module!r} не знайдено')
        return 1

    passed: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for module in selected:
        check = module / 'checks' / 'check_lab.py'
        solution = module / 'solution'
        if not check.is_file():
            skipped.append(module.name)
            print(f'SKIP {module.name}: немає checks/check_lab.py')
            continue
        result = subprocess.run(
            [sys.executable, str(check), '--target', str(solution)],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        last_line = ''
        output = (result.stdout or result.stderr).strip().splitlines()
        if output:
            last_line = output[-1][:160]
        if result.returncode == 0:
            passed.append(module.name)
            print(f'PASS {module.name}: {last_line}')
        else:
            failed.append(module.name)
            print(f'FAIL {module.name}: {last_line}')

    print()
    print(f'Підсумок: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped')
    if failed:
        print('Невдалі: ' + ', '.join(failed))
    if skipped:
        print('Без перевірки: ' + ', '.join(skipped))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
