"""REST API над ArduPilot SITL.

Передумова (SITL уже слухає TCP 5762 — додатковий --out не потрібен):

    sim_vehicle.py -v ArduCopter

Якщо 5762 зайнятий іншим клієнтом, відкрийте другий порт:

    sim_vehicle.py -v ArduCopter --out=tcpin:0.0.0.0:5763
    export MAVLINK_URL=tcp:127.0.0.1:5763

Запуск:

    MAVLINK_URL=tcp:127.0.0.1:5762 uvicorn ardupilot_api:app --port 8080

Особливості: pymavlink синхронний, тому всі виклики виконуються
в окремому потоці; кожна команда чекає COMMAND_ACK з таймаутом.
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Protocol

from fastapi import FastAPI, HTTPException
from pymavlink import mavutil

log = logging.getLogger('ardupilot_api')
logging.basicConfig(level=logging.INFO)

MAVLINK_URL = os.environ.get('MAVLINK_URL', 'tcp:127.0.0.1:5762')
CONNECT_TIMEOUT = 15.0
ACK_TIMEOUT = 5.0

MODE_GUIDED = 4
MODE_RTL = 6


class DroneConnection(Protocol):
    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def arm(self) -> None: ...

    async def takeoff(self, altitude: float) -> None: ...

    async def rtl(self) -> None: ...

    async def heartbeat(self) -> dict[str, Any]: ...


class MavlinkDrone:
    def __init__(self, url: str) -> None:
        self._url = url
        self._conn: Any = None

    async def connect(self) -> None:
        self._conn = await asyncio.wait_for(
            asyncio.to_thread(mavutil.mavlink_connection, self._url),
            timeout=CONNECT_TIMEOUT,
        )
        await asyncio.wait_for(
            asyncio.to_thread(self._conn.wait_heartbeat), timeout=CONNECT_TIMEOUT
        )
        log.info(
            'connected to system %s component %s',
            self._conn.target_system,
            self._conn.target_component,
        )

    async def close(self) -> None:
        if self._conn is not None:
            await asyncio.to_thread(self._conn.close)
            self._conn = None

    def _require_conn(self) -> Any:
        if self._conn is None:
            raise RuntimeError('MAVLink connection is not established')
        return self._conn

    async def _wait_ack(self, command: int) -> None:
        def wait() -> None:
            while True:
                msg = self._conn.recv_match(
                    type='COMMAND_ACK', blocking=True, timeout=ACK_TIMEOUT
                )
                if msg is None:
                    raise TimeoutError(f'no COMMAND_ACK for {command}')
                if msg.command == command:
                    if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
                        raise RuntimeError(
                            f'command {command} rejected, result={msg.result}'
                        )
                    return

        await asyncio.wait_for(asyncio.to_thread(wait), timeout=ACK_TIMEOUT + 1)

    async def _set_mode(self, custom_mode: int) -> None:
        conn = self._require_conn()
        await asyncio.to_thread(
            conn.mav.set_mode_send,
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            custom_mode,
        )

    async def arm(self) -> None:
        conn = self._require_conn()
        await asyncio.to_thread(
            conn.mav.command_long_send,
            conn.target_system,
            conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0,
        )
        await self._wait_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)

    async def takeoff(self, altitude: float) -> None:
        if not 1.0 <= altitude <= 120.0:
            raise ValueError('altitude must be in [1, 120] meters')
        await self._set_mode(MODE_GUIDED)
        conn = self._require_conn()
        await asyncio.to_thread(
            conn.mav.command_long_send,
            conn.target_system,
            conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0, 0, 0, altitude,
        )
        await self._wait_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)

    async def rtl(self) -> None:
        await self._set_mode(MODE_RTL)

    async def heartbeat(self) -> dict[str, Any]:
        conn = self._require_conn()
        msg = await asyncio.wait_for(
            asyncio.to_thread(
                conn.recv_match, type='HEARTBEAT', blocking=True, timeout=ACK_TIMEOUT
            ),
            timeout=ACK_TIMEOUT + 1,
        )
        if msg is None:
            raise TimeoutError('no HEARTBEAT received')
        data = msg.to_dict()
        data.pop('mavpackettype', None)
        return data


def create_app(drone: DroneConnection | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.drone = drone or MavlinkDrone(MAVLINK_URL)
        await app.state.drone.connect()
        try:
            yield
        finally:
            await app.state.drone.close()

    app = FastAPI(title='ArduPilot Control API', lifespan=lifespan)

    async def call(action, *args):
        try:
            await action(*args)
        except TimeoutError as exc:
            raise HTTPException(status_code=504, detail=str(exc)) from exc
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {'status': 'ok'}

    @app.post('/arm')
    async def arm() -> dict[str, str]:
        return await call(app.state.drone.arm)

    @app.post('/takeoff')
    async def takeoff(alt: float = 10.0) -> dict[str, str]:
        return await call(app.state.drone.takeoff, alt)

    @app.post('/rtl')
    async def rtl() -> dict[str, str]:
        return await call(app.state.drone.rtl)

    @app.get('/status')
    async def status() -> dict[str, Any]:
        try:
            return await app.state.drone.heartbeat()
        except TimeoutError as exc:
            raise HTTPException(status_code=504, detail=str(exc)) from exc

    return app


app = create_app()
