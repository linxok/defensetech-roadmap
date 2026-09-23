"""Gateway: MAVLink (UDP) → backend HTTP.

Джерело — SITL (`--out=udp:gateway:14550`) або `sim/` (без autopilot).
HTTP-клієнт — httpx.AsyncClient, тому event loop не блокується;
pymavlink читається в окремому потоці.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
from datetime import datetime, timezone
from typing import Any

import httpx
from pymavlink import mavutil

log = logging.getLogger('capstone.gateway')
logging.basicConfig(level=logging.INFO)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000').rstrip('/')
MAVLINK_SOURCE = os.environ.get('MAVLINK_SOURCE', 'udp:0.0.0.0:14550')
HEARTBEAT_TIMEOUT = float(os.environ.get('HEARTBEAT_TIMEOUT', '60'))
POST_TIMEOUT = 5.0
LOG_EVERY = 50

TRACKED_TYPES = {'GLOBAL_POSITION_INT', 'ATTITUDE', 'SYS_STATUS', 'VFR_HUD', 'BATTERY_STATUS'}


def mavlink_to_telemetry(message: Any) -> dict[str, Any] | None:
    kind = message.get_type()
    if kind not in TRACKED_TYPES:
        return None

    payload: dict[str, Any] = {
        'type': kind,
        'system_id': message.get_srcSystem(),
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    if kind == 'GLOBAL_POSITION_INT':
        payload.update(
            lat=message.lat / 1e7,
            lon=message.lon / 1e7,
            alt=message.alt / 1000.0,
            heading=message.hdg / 100.0 if message.hdg != 65535 else None,
        )
    elif kind == 'ATTITUDE':
        payload.update(roll=message.roll, pitch=message.pitch, yaw=message.yaw)
    elif kind == 'SYS_STATUS':
        payload.update(
            battery=message.battery_remaining,
            voltage=message.voltage_battery / 1000.0,
            drop_rate_comm=message.drop_rate_comm / 100.0,
        )
    elif kind == 'BATTERY_STATUS':
        payload.update(battery=message.battery_remaining)
    elif kind == 'VFR_HUD':
        payload.update(
            airspeed=message.airspeed,
            groundspeed=message.groundspeed,
            alt=message.alt,
            climb=message.climb,
        )
    return payload


async def post_with_retry(client: httpx.AsyncClient, payload: dict[str, Any]) -> bool:
    for attempt in range(3):
        try:
            response = await client.post(f'{BACKEND_URL}/telemetry', json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            log.warning('backend post failed (attempt %d/3): %s', attempt + 1, exc)
            await asyncio.sleep(0.5 * (attempt + 1))
    return False


async def forward(connection: Any, stop: asyncio.Event) -> None:
    sent = 0
    async with httpx.AsyncClient(timeout=POST_TIMEOUT) as client:
        while not stop.is_set():
            message = await asyncio.to_thread(
                connection.recv_match, blocking=True, timeout=1.0
            )
            if message is None:
                continue
            payload = mavlink_to_telemetry(message)
            if payload is None:
                continue
            if await post_with_retry(client, payload):
                sent += 1
                if sent % LOG_EVERY == 0:
                    log.info('forwarded %d telemetry frames', sent)


async def run() -> None:
    connection = await asyncio.to_thread(
        mavutil.mavlink_connection, MAVLINK_SOURCE, source_system=254
    )
    await asyncio.wait_for(
        asyncio.to_thread(connection.wait_heartbeat), timeout=HEARTBEAT_TIMEOUT
    )
    log.info('MAVLink connected: system %s', connection.target_system)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    task = asyncio.create_task(forward(connection, stop))
    await stop.wait()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    await asyncio.to_thread(connection.close)


def main() -> None:
    try:
        asyncio.run(run())
    except TimeoutError:
        log.error('no heartbeat from %s in %.0fs', MAVLINK_SOURCE, HEARTBEAT_TIMEOUT)
        raise SystemExit(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
