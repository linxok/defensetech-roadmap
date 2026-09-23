#!/usr/bin/env python3
"""Перевірка лабораторної 14: GCS UI.

Контракт (див. lab.md):
- `telemetry-format.mjs` — чисті функції, покриті `node --test`;
- `gcs-page.tsx` — React-компонент з Leaflet-мапою та WebSocket.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
REQUIRED_IN_TSX = ('useEffect', 'new WebSocket', 'MapContainer', 'TileLayer', 'Marker')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    node = shutil.which('node')
    if node is None:
        fail('не знайдено node — встановіть Node.js 20+')

    logic = args.target / 'telemetry-format.mjs'
    test_file = args.target / 'telemetry-format.test.mjs'
    component = args.target / 'gcs-page.tsx'
    for path in (logic, test_file, component):
        if not path.is_file():
            fail(f'{path} не існує')

    result = subprocess.run(
        [node, '--test', str(test_file)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=args.target,
        check=False,
    )
    if result.returncode != 0:
        fail(f'node --test провалився:\n{result.stdout[-600:]}{result.stderr[-600:]}')

    tsx = component.read_text(encoding='utf-8')
    missing = [pattern for pattern in REQUIRED_IN_TSX if pattern not in tsx]
    if missing:
        fail('у компоненті немає: ' + ', '.join(missing))
    if 'localhost:8000' in tsx and 'NEXT_PUBLIC' not in tsx:
        fail('URL WebSocket має бути налаштовуваним (NEXT_PUBLIC_WS_URL)')

    print('PASS: логіка GCS покрита тестами, компонент містить мапу і WS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
