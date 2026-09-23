"""Спрощений REST API над ArduPilot SITL (приклад до модуля 07).

Демонструє мінімум: інʼєкцію дрона через `create_app(drone=None)` і
чотири endpoints. Еталон із таймаутами, очікуванням `COMMAND_ACK` і
мапінгом помилок — `solution/ardupilot_api.py`.

SITL сам відкриває TCP 5762, тому підключенню нічого додатково
відкривати не треба:

    sim_vehicle.py -v ArduCopter
    uvicorn examples.ardupilot_api:app --port 8080

Якщо 5762 зайнятий, підніміть другий порт і задайте `MAVLINK_URL`:

    sim_vehicle.py -v ArduCopter --out=tcpin:0.0.0.0:5763
    MAVLINK_URL=tcp:127.0.0.1:5763 uvicorn examples.ardupilot_api:app --port 8080
"""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pymavlink import mavutil

MAVLINK_URL = os.environ.get('MAVLINK_URL', 'tcp:127.0.0.1:5762')


class SimpleDrone:
    """Мінімальна обгортка pymavlink: без ACK і таймаутів."""

    def __init__(self, url: str = MAVLINK_URL) -> None:
        self.url = url
        self.conn = None

    async def connect(self) -> None:
        self.conn = await asyncio.to_thread(mavutil.mavlink_connection, self.url)
        await asyncio.to_thread(self.conn.wait_heartbeat)

    async def close(self) -> None:
        if self.conn is not None:
            await asyncio.to_thread(self.conn.close)

    async def arm(self) -> None:
        await asyncio.to_thread(self.conn.arducopter_arm)

    async def takeoff(self, altitude: float) -> None:
        await asyncio.to_thread(self.conn.set_mode, 'GUIDED')
        await asyncio.to_thread(
            self.conn.mav.command_long_send,
            self.conn.target_system, self.conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, altitude,
        )

    async def rtl(self) -> None:
        await asyncio.to_thread(self.conn.set_mode, 'RTL')

    async def heartbeat(self) -> dict:
        message = await asyncio.to_thread(
            self.conn.recv_match, type='HEARTBEAT', blocking=True, timeout=2.0
        )
        if message is None:
            raise TimeoutError('no HEARTBEAT')
        return message.to_dict()


def create_app(drone=None) -> FastAPI:
    """Фабрика з інʼєкцією: у тестах передайте FakeDrone замість SITL."""

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.drone = drone or SimpleDrone()
        await application.state.drone.connect()
        try:
            yield
        finally:
            await application.state.drone.close()

    application = FastAPI(title='ArduPilot demo API', lifespan=lifespan)

    @application.post('/arm')
    async def arm():
        await application.state.drone.arm()
        return {'status': 'armed'}

    @application.post('/takeoff')
    async def takeoff(alt: float = 10.0):
        if not 1.0 <= alt <= 120.0:
            raise HTTPException(
                status_code=400, detail='altitude must be in [1, 120] meters'
            )
        await application.state.drone.takeoff(alt)
        return {'status': 'takeoff', 'alt': alt}

    @application.post('/rtl')
    async def rtl():
        await application.state.drone.rtl()
        return {'status': 'rtl'}

    @application.get('/status')
    async def status():
        try:
            return await application.state.drone.heartbeat()
        except TimeoutError as exc:
            raise HTTPException(status_code=504, detail=str(exc)) from exc

    return application


app = create_app()
