"""UDP → WebSocket telemetry bridge (еталон лабораторної 03).

Запуск:

    python udp_ws_bridge.py --udp-port 14550 --ws-port 8765

Контракт для перевірки:
- `parse_packet(data: bytes) -> dict` — валідація JSON-пакета;
- `TelemetryHub.register(ws)` / `broadcast(payload)` — async;
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
    if not data:
        raise ValueError('empty datagram')
    try:
        payload = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'invalid telemetry packet: {exc}') from exc
    if not isinstance(payload, dict):
        raise ValueError('telemetry packet must be a JSON object')
    if 'drone_id' not in payload and 'type' not in payload:
        raise ValueError('packet must contain drone_id or type')
    return payload


class TelemetryHub:
    def __init__(self) -> None:
        self._clients: set[Any] = set()
        self._lock = asyncio.Lock()

    async def register(self, websocket: Any) -> None:
        async with self._lock:
            self._clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            async with self._lock:
                self._clients.discard(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            clients = list(self._clients)
        if not clients:
            return
        data = json.dumps(payload, ensure_ascii=False)
        results = await asyncio.gather(
            *(client.send(data) for client in clients), return_exceptions=True
        )
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                log.warning('dropping client: %s', result)
                async with self._lock:
                    self._clients.discard(client)


class UdpTelemetryProtocol(asyncio.DatagramProtocol):
    def __init__(self, hub: TelemetryHub) -> None:
        self.hub = hub
        self.invalid_packets = 0

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            payload = parse_packet(data)
        except ValueError as exc:
            self.invalid_packets += 1
            log.warning('invalid packet from %s: %s', addr, exc)
            return
        asyncio.get_running_loop().create_task(self.hub.broadcast(payload))

    def error_received(self, exc: Exception) -> None:
        log.warning('udp error: %s', exc)


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
