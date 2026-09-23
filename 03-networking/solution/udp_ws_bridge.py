"""UDP → WebSocket telemetry bridge (еталон лабораторної 03).

Запуск:

    python udp_ws_bridge.py --udp-port 14550 --ws-port 8765

Публічний контракт (його перевіряє `checks/check_lab.py`):
- `parse_packet(data: bytes) -> dict` — валідація JSON-пакета;
- `TelemetryHub.register(websocket)` / `TelemetryHub.broadcast(payload)`;
- `UdpTelemetryProtocol(hub).datagram_received(data, addr)`.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any

import websockets

log = logging.getLogger('udp_ws_bridge')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def parse_packet(data: bytes) -> dict[str, Any]:
    """Повертає JSON-обʼєкт телеметрії, інакше піднімає ValueError."""
    if not data:
        raise ValueError('empty datagram')
    try:
        packet = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'invalid telemetry packet: {exc}') from exc
    if not isinstance(packet, dict):
        raise ValueError('telemetry packet must be a JSON object')
    if 'drone_id' not in packet and 'type' not in packet:
        raise ValueError('packet must contain drone_id or type')
    return packet


class TelemetryHub:
    """Плоский список WebSocket-клієнтів і черга кадрів телеметрії."""

    def __init__(self) -> None:
        self.clients: list[Any] = []

    async def register(self, websocket: Any) -> None:
        self.clients.append(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._forget(websocket)

    def _forget(self, websocket: Any) -> None:
        if websocket in self.clients:
            self.clients.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        recipients = tuple(self.clients)
        if not recipients:
            return
        frame = json.dumps(payload, ensure_ascii=False)
        outcomes = await asyncio.gather(
            *(recipient.send(frame) for recipient in recipients),
            return_exceptions=True,
        )
        for recipient, outcome in zip(recipients, outcomes):
            if isinstance(outcome, Exception):
                log.warning('client dropped after send error: %s', outcome)
                self._forget(recipient)


class UdpTelemetryProtocol(asyncio.DatagramProtocol):
    """Приймає датаграми, відсіює сміття і передає валідні пакети в хаб."""

    def __init__(self, hub: TelemetryHub) -> None:
        self.hub = hub
        self.malformed_packets = 0

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            payload = parse_packet(data)
        except ValueError as exc:
            self.malformed_packets += 1
            log.warning('malformed datagram from %s: %s', addr, exc)
            return
        asyncio.get_running_loop().create_task(self.hub.broadcast(payload))

    def error_received(self, exc: Exception) -> None:
        log.warning('udp transport error: %s', exc)


async def run(udp_port: int, ws_port: int) -> None:
    hub = TelemetryHub()
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UdpTelemetryProtocol(hub), local_addr=('0.0.0.0', udp_port)
    )
    log.info('UDP listening on :%d', udp_port)
    try:
        async with websockets.serve(hub.register, '0.0.0.0', ws_port):
            log.info('WebSocket server on ws://0.0.0.0:%d', ws_port)
            await asyncio.Future()
    finally:
        transport.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--udp-port', type=int, default=14550)
    parser.add_argument('--ws-port', type=int, default=8765)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.udp_port, args.ws_port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
