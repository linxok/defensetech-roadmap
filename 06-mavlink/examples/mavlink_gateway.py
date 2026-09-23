"""Спрощена демонстрація MAVLink → JSON gateway (модуль 06).

Це навчальний приклад, а не еталон: один WebSocket-клієнт, без
`asyncio.Lock`, черг і відкидання повільних клієнтів. Повна версія —
`solution/mavlink_gateway.py`.

Запуск:

    sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14550
    python examples/mavlink_gateway.py --source udp:127.0.0.1:14550
    # потім відкрийте examples/websocket_client.html
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import websockets
from pymavlink import mavutil

SUPPORTED = {'HEARTBEAT', 'GLOBAL_POSITION_INT'}


def mavlink_to_telemetry(message: Any) -> dict[str, Any] | None:
    """Мінімальний конвертер: HEARTBEAT і GLOBAL_POSITION_INT, решта — None."""
    kind = message.get_type()
    if kind not in SUPPORTED:
        return None
    packet: dict[str, Any] = {
        'type': kind,
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    if kind == 'HEARTBEAT':
        packet['custom_mode'] = message.custom_mode
    else:
        packet['lat'] = message.lat / 1e7
        packet['lon'] = message.lon / 1e7
        packet['alt'] = message.alt / 1000.0
    packet['system_id'] = message.get_srcSystem()
    packet['component_id'] = message.get_srcComponent()
    return packet


class TelemetryHub:
    """Демонстраційний хаб на одного клієнта: без lock і дедуплікації."""

    def __init__(self) -> None:
        self.client: Any = None

    async def register(self, ws: Any) -> None:
        self.client = ws
        try:
            await ws.wait_closed()
        finally:
            self.client = None

    async def broadcast(self, payload: dict[str, Any]) -> None:
        if self.client is None:
            return
        await self.client.send(json.dumps(payload))


async def pump(connection: Any, hub: TelemetryHub) -> None:
    while True:
        frame = await asyncio.to_thread(
            connection.recv_match, blocking=True, timeout=1.0
        )
        if frame is None:
            continue
        packet = mavlink_to_telemetry(frame)
        if packet:
            await hub.broadcast(packet)


async def main(source: str, port: int) -> None:
    connection = await asyncio.to_thread(mavutil.mavlink_connection, source)
    await asyncio.to_thread(connection.wait_heartbeat)
    hub = TelemetryHub()
    async with websockets.serve(hub.register, '127.0.0.1', port):
        print(f'ws://127.0.0.1:{port} (Ctrl+C — вихід)')
        await pump(connection, hub)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='simple MAVLink → WebSocket demo')
    parser.add_argument('--source', default='udp:127.0.0.1:14550')
    parser.add_argument('--ws-port', type=int, default=8765)
    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_args()
    try:
        asyncio.run(main(arguments.source, arguments.ws_port))
    except KeyboardInterrupt:
        pass
