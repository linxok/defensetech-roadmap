#!/usr/bin/env python3
"""Перевірка лабораторної 01: архітектура UAV.

Контракт (див. lab.md): mermaid-діаграма (`*.mmd` або блок у `*.md`)
з усіма ключовими підсистемами та звʼязками між ними.

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

REQUIRED = {
    'flight controller': ('fc', 'flight', 'autopilot', 'pixhawk'),
    'GPS': ('gps', 'rtk'),
    'IMU': ('imu', 'baro', 'gyro'),
    'ESC/мотори': ('esc', 'motor'),
    'живлення': ('batt', 'power', 'pdb'),
    'телеметрія': ('telem', 'radio', 'mavlink'),
    'GCS': ('gcs', 'qground', 'ground'),
    'companion computer': ('comp', 'jetson', 'raspberry'),
}


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_text(target: Path) -> str:
    if not target.is_dir():
        fail(f'{target} не існує')
    parts = []
    for path in sorted(target.glob('*.mmd')) + sorted(target.glob('*.md')):
        parts.append(path.read_text(encoding='utf-8'))
    if not parts:
        fail(f'{target} не містить .mmd або .md файлів')
    return '\n'.join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    text = load_text(args.target)
    if not re.search(r'graph\s+(TD|LR)', text) and '-->' not in text:
        fail('схема не схожа на mermaid-діаграму (graph TD/LR або -->)')

    lowered = text.lower()
    missing = [name for name, keys in REQUIRED.items() if not any(key in lowered for key in keys)]
    if missing:
        fail('у схемі немає підсистем: ' + ', '.join(missing))

    edges = len(re.findall(r'-->|<-->', text))
    if edges < 6:
        fail(f'звʼязків між підсистемами замало: {edges} (очікували 6+)')

    nodes = set(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*[\[({]', text))
    if len(nodes) < 10:
        fail(f'вузлів на схемі замало: {len(nodes)} (очікували 10+)')

    print(f'PASS: архітектура містить усі підсистеми ({len(nodes)} вузлів, {edges} звʼязків)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
