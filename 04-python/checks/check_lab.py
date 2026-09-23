#!/usr/bin/env python3
"""Перевірка лабораторної 04: FastAPI Telemetry API.

Контракт (див. lab.md):
- модуль з об'єктом `app` (FastAPI) у `main.py`/`app.py`/`fastapi_telemetry.py`;
- POST /telemetry валідує дані (межі батареї, координат, висоти);
- GET /telemetry/{drone_id} повертає збережені дані.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
CANDIDATES = ('main.py', 'app.py', 'fastapi_telemetry.py')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_app(target: Path):
    for name in CANDIDATES:
        path = target / name
        if path.is_file():
            break
    else:
        fail(f'{target} не містить жодного з файлів: {", ".join(CANDIDATES)}')

    spec = importlib.util.spec_from_file_location('student_api', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_api'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - повідомляємо причину
        fail(f'модуль не імпортується: {exc!r}')
    if not hasattr(module, 'app'):
        fail('у модулі немає обʼєкта `app`')
    return module.app


VALID = {
    'drone_id': 'd1',
    'lat': 50.4501,
    'lon': 30.5234,
    'alt': 120.0,
    'battery': 87,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    app = load_app(args.target)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.post('/telemetry', json=VALID)
        if response.status_code not in (200, 201):
            fail(f'валідний POST /telemetry → {response.status_code}: {response.text}')

        for field, bad_value in (('battery', 150), ('lat', 100.0), ('alt', -1000.0)):
            payload = dict(VALID, **{field: bad_value})
            response = client.post('/telemetry', json=payload)
            if response.status_code < 400:
                fail(f'POST з {field}={bad_value} мав бути відхилений, отримано {response.status_code}')

        response = client.get('/telemetry/d1')
        if response.status_code != 200:
            fail(f'GET /telemetry/d1 → {response.status_code}')
        if 'd1' not in json.dumps(response.json()):
            fail('GET не повертає збережене вимірювання для d1')

    print('PASS: API валідує дані, зберігає та віддає телеметрію')
    return 0


if __name__ == '__main__':
    sys.exit(main())
