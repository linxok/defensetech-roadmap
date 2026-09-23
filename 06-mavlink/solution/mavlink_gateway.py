"""MAVLink → JSON WebSocket gateway.

Джерело MAVLink: SITL або реальний автопілот.
Запуск:

    sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14550
    python mavlink_gateway.py --source udp:127.0.0.1:14550 --ws-port 8765

Контракт JSON: `{type, system_id, component_id, ts, ...fields}`.
Перевірка схеми: `../checks/check_lab.py --target ../solution`.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
from datetime import datetime, timezone
from typing import Any, Protocol

import websockets
from pymavlink import mavutil

log = logging.getLogger('mavlink_gateway')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

TRACKED_TYPES = {
    'HEARTBEAT',
    'GLOBAL_POSITION_INT',
    'ATTITUDE',
    'BATTERY_STATUS',
    'SYS_STATUS',
    'VFR_HUD',
}


def mavlink_to_telemetry(message: Any) -> dict[str, Any] | None:
    """Перетворює MAVLink-повідомлення у JSON-сумісний словник.

    Повертає None для типів, які gateway не транслює, та для BAD_DATA.
    """
    kind = message.get_type()
    if kind not in TRACKED_TYPES:
        return None

    payload: dict[str, Any] = {
        'type': kind,
        'system_id': message.get_srcSystem(),
        'component_id': message.get_srcComponent(),
        'ts': datetime.now(timezone.utc).isoformat(),
    }

    if kind == 'HEARTBEAT':
        payload.update(
            autopilot=message.autopilot,
            base_mode=message.base_mode,
            custom_mode=message.custom_mode,
            system_status=message.system_status,
        )
    elif kind == 'GLOBAL_POSITION_INT':
        payload.update(
            lat=message.lat / 1e7,
            lon=message.lon / 1e7,
            alt=message.alt / 1000.0,
            relative_alt=message.relative_alt / 1000.0,
            heading=message.hdg / 100.0 if message.hdg != 65535 else None,
        )
    elif kind == 'ATTITUDE':
        payload.update(roll=message.roll, pitch=message.pitch, yaw=message.yaw)
    elif kind == 'BATTERY_STATUS':
        payload.update(
            battery_remaining=message.battery_remaining,
            voltage=sum(v for v in message.voltages if v != 65535) / 1000.0,
        )
    elif kind == 'SYS_STATUS':
        payload.update(
            voltage_battery=message.voltage_battery / 1000.0,
            current_battery=message.current_battery / 100.0,
            battery_remaining=message.battery_remaining,
            drop_rate_comm=message.drop_rate_comm / 100.0,
        )
    elif kind == 'VFR_HUD':
        payload.update(
            airspeed=message.airspeed,
            groundspeed=message.groundspeed,
            heading=message.heading,
            throttle=message.throttle,
            alt=message.alt,
            climb=message.climb,
        )

    return payload


class TelemetryHub:
    """Набір WebSocket-клієнтів і розсилка без блокування одне одного."""

    def __init__(self) -> None:
        self._clients: set[Any] = set()
        self._lock = asyncio.Lock()

    async def register(self, websocket: Any) -> None:
        async with self._lock:
            self._clients.add(websocket)
        log.info('client connected, total=%d', len(self._clients))
        try:
            await websocket.wait_closed()
        finally:
            async with self._lock:
                self._clients.discard(websocket)
            log.info('client disconnected, total=%d', len(self._clients))

    async def broadcast(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            clients = list(self._clients)
        if not clients:
            return
        data = json.dumps(payload)
        results = await asyncio.gather(
            *(client.send(data) for client in clients), return_exceptions=True
        )
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                log.warning('dropping slow client: %s', result)
                async with self._lock:
                    self._clients.discard(client)


async def read_mavlink(
    connection: Any, hub: TelemetryHub, stop: asyncio.Event
) -> None:
    """Читає MAVLink у потоці, щоб не блокувати event loop."""
    while not stop.is_set():
        message = await asyncio.to_thread(
            connection.recv_match, blocking=True, timeout=1.0
        )
        if message is None:
            continue
        payload = mavlink_to_telemetry(message)
        if payload is not None:
            await hub.broadcast(payload)


async def run(source: str, ws_host: str, ws_port: int, heartbeat_timeout: float) -> None:
    connection = await asyncio.to_thread(
        mavutil.mavlink_connection, source, source_system=255
    )
    await asyncio.wait_for(
        asyncio.to_thread(connection.wait_heartbeat), timeout=heartbeat_timeout
    )
    log.info('heartbeat from system %s component %s',
             connection.target_system, connection.target_component)

    hub = TelemetryHub()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async with websockets.serve(hub.register, ws_host, ws_port):
        log.info('WebSocket server on ws://%s:%d', ws_host, ws_port)
        reader = asyncio.create_task(read_mavlink(connection, hub, stop))
        await stop.wait()
        reader.cancel()
        await asyncio.gather(reader, return_exceptions=True)

    await asyncio.to_thread(connection.close)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='udp:127.0.0.1:14550')
    parser.add_argument('--ws-host', default='0.0.0.0')
    parser.add_argument('--ws-port', type=int, default=8765)
    parser.add_argument('--heartbeat-timeout', type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.source, args.ws_host, args.ws_port, args.heartbeat_timeout))
    except KeyboardInterrupt:
        pass
    except TimeoutError:
        log.error('no heartbeat from %s in %.0fs', args.source, args.heartbeat_timeout)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
