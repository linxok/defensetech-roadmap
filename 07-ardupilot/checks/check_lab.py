#!/usr/bin/env python3
"""Перевірка лабораторної 07: REST API над ArduPilot SITL.

Контракт (див. lab.md): `create_app(drone=None)` у `ardupilot_api.py`,
drone-обʼєкт з async-методами connect/close/arm/takeoff/rtl/heartbeat.
Перевірка офлайн — SITL підмінюється фейковим клієнтом.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'ardupilot_api.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_ardupilot', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_ardupilot'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується: {exc!r}')
    if not hasattr(module, 'create_app'):
        fail('потрібна фабрика `create_app(drone=None)` для тестованості')
    return module


class FakeDrone:
    def __init__(self) -> None:
        self.connected = False
        self.closed = False
        self.actions: list[tuple] = []

    async def connect(self) -> None:
        self.connected = True

    async def close(self) -> None:
        self.closed = True

    async def arm(self) -> None:
        self.actions.append(('arm',))

    async def takeoff(self, altitude: float) -> None:
        if not 1.0 <= altitude <= 120.0:
            raise ValueError('altitude must be in [1, 120] meters')
        self.actions.append(('takeoff', altitude))

    async def rtl(self) -> None:
        self.actions.append(('rtl',))

    async def heartbeat(self) -> dict:
        return {'type': 2, 'autopilot': 3, 'base_mode': 81, 'custom_mode': 4}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module = load_module(args.target)
    from fastapi.testclient import TestClient

    drone = FakeDrone()
    app = module.create_app(drone)
    with TestClient(app) as client:
        if client.post('/arm').status_code != 200:
            fail('POST /arm має повертати 200')
        if client.post('/takeoff', params={'alt': 20}).status_code != 200:
            fail('POST /takeoff?alt=20 має повертати 200')
        if client.post('/takeoff', params={'alt': 500}).status_code not in (400, 422):
            fail('takeoff з alt=500 має бути відхилений')
        if client.post('/rtl').status_code != 200:
            fail('POST /rtl має повертати 200')
        status = client.get('/status')
        if status.status_code != 200 or 'custom_mode' not in status.json():
            fail('GET /status має повертати heartbeat')

    if not drone.connected or not drone.closed:
        fail('lifespan має викликати connect() і close()')
    if ('takeoff', 20.0) not in drone.actions:
        fail(f'команда takeoff не дійшла до дрона: {drone.actions}')

    print('PASS: API керує дроном через інʼєкцію та валідує команди')
    return 0


if __name__ == '__main__':
    sys.exit(main())
