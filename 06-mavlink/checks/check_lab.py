#!/usr/bin/env python3
"""Перевірка лабораторної 06: MAVLink → JSON gateway.

Контракт (див. lab.md):
- функція `mavlink_to_telemetry(message)` → dict | None;
- клас `TelemetryHub` з `register(ws)` і `broadcast(payload)`;
- жодних блокуючих викликів в async-коді без `asyncio.to_thread`.

Перевірка офлайн: MAVLink-фікстури пакуються pymavlink і парсяться назад.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent

from pymavlink.dialects.v20 import ardupilotmega as mavlink  # noqa: E402


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_gateway(target: Path):
    path = target / 'mavlink_gateway.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_gateway', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_gateway'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується: {exc!r}')
    for attr in ('mavlink_to_telemetry', 'TelemetryHub'):
        if not hasattr(module, attr):
            fail(f'у модулі немає `{attr}`')
    return module, path


def make_message(encoder: str, system_id: int = 7, **fields):
    class Sink:
        def __init__(self) -> None:
            self.buffer = bytearray()

        def write(self, data: bytes) -> None:
            self.buffer.extend(data)

    sink = Sink()
    sender = mavlink.MAVLink(sink, srcSystem=system_id, srcComponent=1)
    getattr(sender, f'{encoder}_send')(**fields)
    parser = mavlink.MAVLink(None)
    messages = parser.parse_buffer(bytes(sink.buffer)) or []
    if not messages:
        fail(f'не вдалося закодувати {encoder}')
    return messages[0]


class FakeClient:
    def __init__(self) -> None:
        self.received: list[str] = []

    async def send(self, data: str) -> None:
        self.received.append(data)

    async def wait_closed(self) -> None:
        await asyncio.sleep(3600)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module, path = load_gateway(args.target)

    position = make_message(
        'global_position_int',
        time_boot_ms=1000,
        lat=504501000,
        lon=305234000,
        alt=120000,
        relative_alt=100000,
        vx=0,
        vy=0,
        vz=0,
        hdg=9000,
    )
    payload = module.mavlink_to_telemetry(position)
    if not isinstance(payload, dict):
        fail('mavlink_to_telemetry(GLOBAL_POSITION_INT) має повертати dict')
    if payload.get('type') != 'GLOBAL_POSITION_INT':
        fail(f'невірний type: {payload.get("type")!r}')
    if abs(payload.get('lat', 0) - 50.4501) > 1e-4:
        fail(f'невірний lat: {payload.get("lat")!r}')
    if abs(payload.get('alt', 0) - 120.0) > 0.01:
        fail(f'невірний alt: {payload.get("alt")!r}')
    json.dumps(payload)  # контракт: JSON-сумісність

    heartbeat = make_message(
        'heartbeat',
        type=mavlink.MAV_TYPE_QUADROTOR,
        autopilot=mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        base_mode=0,
        custom_mode=0,
        system_status=mavlink.MAV_STATE_ACTIVE,
    )
    heartbeat_payload = module.mavlink_to_telemetry(heartbeat)
    if heartbeat_payload is None or heartbeat_payload.get('type') != 'HEARTBEAT':
        fail('HEARTBEAT має потрапляти в JSON як type=HEARTBEAT')

    ping = make_message(
        'ping',
        time_usec=1,
        seq=1,
        target_system=1,
        target_component=1,
    )
    if module.mavlink_to_telemetry(ping) is not None:
        fail('PING не входить до контракту gateway і має повертати None')

    hub = module.TelemetryHub()
    client = FakeClient()

    async def check_broadcast() -> None:
        task = asyncio.create_task(hub.register(client))
        await asyncio.sleep(0.05)
        await hub.broadcast({'type': 'ATTITUDE', 'roll': 0.1})
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    asyncio.run(check_broadcast())
    if not client.received:
        fail('broadcast не надіслав повідомлення зареєстрованому клієнту')
    if json.loads(client.received[0]).get('type') != 'ATTITUDE':
        fail('broadcast надіслав некоректний JSON')

    source = path.read_text(encoding='utf-8')
    if 'asyncio.wait(' in source:
        fail('використано asyncio.wait замість asyncio.gather')
    if 'recv_match' in source and 'to_thread' not in source:
        fail('блокуючий recv_match викликається без asyncio.to_thread')

    print('PASS: gateway конвертує MAVLink у JSON і коректно розсилає клієнтам')
    return 0


if __name__ == '__main__':
    sys.exit(main())
