#!/usr/bin/env python3
"""Перевірка лабораторної 03: UDP → WebSocket bridge.

Контракт (див. lab.md):
- `parse_packet(data: bytes) -> dict` відхиляє не-JSON і не-обʼєкти;
- `TelemetryHub` розсилає payload усім клієнтам через asyncio.gather;
- `UdpTelemetryProtocol(hub).datagram_received` не падає на смітті.

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


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'udp_ws_bridge.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_bridge', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_bridge'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується: {exc!r}')
    for attr in ('parse_packet', 'TelemetryHub', 'UdpTelemetryProtocol'):
        if not hasattr(module, attr):
            fail(f'у модулі немає `{attr}`')
    return module, path


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

    module, path = load_module(args.target)

    valid = module.parse_packet(b'{"drone_id": "d1", "alt": 120}')
    if valid.get('drone_id') != 'd1':
        fail(f'parse_packet загубив дані: {valid!r}')

    for bad in (b'', b'not-json', b'[1, 2, 3]', b'{"foo": 1}'):
        try:
            module.parse_packet(bad)
        except ValueError:
            continue
        fail(f'parse_packet мав відхилити {bad!r}')

    async def scenario() -> None:
        hub = module.TelemetryHub()
        client = FakeClient()
        task = asyncio.create_task(hub.register(client))
        await asyncio.sleep(0.05)

        protocol = module.UdpTelemetryProtocol(hub)
        protocol.datagram_received(b'{"type": "ATTITUDE", "roll": 0.1}', ('127.0.0.1', 9999))
        protocol.datagram_received(b'malformed', ('127.0.0.1', 9999))
        await asyncio.sleep(0.1)

        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        if not client.received:
            fail('broadcast не надіслав валідний пакет клієнту')
        if json.loads(client.received[0]).get('type') != 'ATTITUDE':
            fail('broadcast надіслав некоректний JSON')
        if len(client.received) != 1:
            fail('сміттєвий пакет не мав потрапити в broadcast')

    asyncio.run(scenario())

    source = path.read_text(encoding='utf-8')
    if 'asyncio.wait(' in source:
        fail('використано asyncio.wait замість asyncio.gather')

    print('PASS: bridge валідує UDP-пакети та безпечно розсилає їх')
    return 0


if __name__ == '__main__':
    sys.exit(main())
