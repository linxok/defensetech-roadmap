#!/usr/bin/env python3
"""Перевірка лабораторної 02: systemd + serial daemon.

Контракт (див. lab.md): у target є
- `*.service` — systemd unit із безпечними директивами;
- `*.sh` — скрипт читання serial (з правами на виконання);
- `*.rules` — udev-правило зі стабільним symlink.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def find_one(target: Path, pattern: str):
    matches = sorted(target.glob(pattern))
    return matches[0] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    unit = find_one(args.target, '*.service')
    script = find_one(args.target, '*.sh')
    rules = find_one(args.target, '*.rules')
    if unit is None or script is None or rules is None:
        fail('потрібні *.service, *.sh і *.rules у ' + str(args.target))

    unit_text = unit.read_text(encoding='utf-8')
    for directive in ('[Unit]', '[Service]', '[Install]', 'ExecStart=', 'Restart=on-failure',
                      'After=network-online.target', 'WantedBy=multi-user.target'):
        if directive not in unit_text:
            fail(f'в unit немає `{directive}`')
    if 'User=root' in unit_text:
        fail('сервіс не має працювати від root')
    exec_match = re.search(r'ExecStart=(\S+)', unit_text)
    if exec_match is None or not exec_match.group(1).endswith('.sh'):
        fail('ExecStart має запускати .sh-скрипт читання serial')

    script_text = script.read_text(encoding='utf-8')
    if not script_text.startswith('#!/'):
        fail('скрипт має починатися з shebang')
    if not os.access(script, os.X_OK):
        fail(f'скрипт {script.name} не має права на виконання (chmod +x)')
    if not re.search(r'stty|serial|pyserial|python', script_text):
        fail('скрипт не схожий на роботу з serial-портом')
    if '/dev/' not in script_text:
        fail('скрипт має працювати з пристроєм у /dev/')

    rules_text = rules.read_text(encoding='utf-8')
    if 'SUBSYSTEM=="tty"' not in rules_text:
        fail('udev-правило має стосуватися SUBSYSTEM=="tty"')
    if 'SYMLINK' not in rules_text:
        fail('udev-правило має створювати стабільний SYMLINK')
    if 'GROUP="dialout"' not in rules_text:
        fail('udev-правило має задавати GROUP="dialout"')
    if 'MODE="0660"' not in rules_text:
        fail('udev-правило має задавати MODE="0660" (не 0666)')

    print('PASS: unit, serial-скрипт і udev-правило коректні')
    return 0


if __name__ == '__main__':
    sys.exit(main())
