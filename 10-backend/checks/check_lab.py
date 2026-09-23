#!/usr/bin/env python3
"""Перевірка лабораторної 10: Telemetry Pipeline (HTTP → черга).

Контракт (див. lab.md): `create_app(publisher=None)` у `main.py`;
publisher з async-методами connect/publish/close; зʼєднання не
створюються при імпорті.

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


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'main.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_pipeline', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_pipeline'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'імпорт не має відкривати зʼєднань: {exc!r}')
    if not hasattr(module, 'create_app'):
        fail('потрібна фабрика `create_app(publisher=None)`')
    return module


class FakePublisher:
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.connected = False
        self.closed = False

    async def connect(self) -> None:
        self.connected = True

    async def publish(self, body: bytes) -> None:
        self.messages.append(json.loads(body))

    async def close(self) -> None:
        self.closed = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module = load_module(args.target)
    from fastapi.testclient import TestClient

    publisher = FakePublisher()
    app = module.create_app(publisher)
    with TestClient(app) as client:
        payload = {'drone_id': 'd1', 'alt': 120.0, 'battery': 87}
        response = client.post('/telemetry', json=payload)
        if response.status_code not in (200, 202):
            fail(f'POST /telemetry → {response.status_code}: {response.text}')
        if not client.get('/health').json():
            fail('GET /health має повертати статус')

    if not publisher.connected or not publisher.closed:
        fail('lifespan має викликати connect() і close()')
    if publisher.messages != [payload]:
        fail(f'у чергу пішло не те повідомлення: {publisher.messages}')

    print('PASS: pipeline публікує телеметрію та коректно закриває зʼєднання')
    return 0


if __name__ == '__main__':
    sys.exit(main())
