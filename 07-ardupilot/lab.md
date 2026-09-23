# Лабораторна робота 07: REST API для ArduPilot SITL

## Мета

Створити FastAPI-сервіс `ardupilot_api.py`, який через pymavlink керує симульованим UAV (arm, takeoff, RTL) і перевіряється офлайн через інʼєкцію фейкового дрона.

## Передумови

- Python 3.11+ і venv:

```bash
python3 -m venv ardupilot-lab
source ardupilot-lab/bin/activate
pip install fastapi uvicorn pymavlink httpx
```

- ArduPilot SITL. SITL сам відкриває TCP `5762`, тому окремий `--out` для нього не потрібен (і призведе до «address already in use»):

```bash
sim_vehicle.py -v ArduCopter
```

- Якщо порт `5762` уже зайнятий іншим клієнтом, підніміть другий порт і вкажіть його через `MAVLINK_URL`:

```bash
sim_vehicle.py -v ArduCopter --out=tcpin:0.0.0.0:5763
export MAVLINK_URL=tcp:127.0.0.1:5763
```

## Контракт

Створіть у своїй робочій теці файл `ardupilot_api.py` з фабрикою `create_app(drone=None) -> FastAPI`.

- `drone` — обʼєкт з async-методами `connect()`, `close()`, `arm()`, `takeoff(altitude: float)`, `rtl()`, `heartbeat() -> dict`.
- Якщо `drone is None`, фабрика створює `MavlinkDrone` з `MAVLINK_URL` (типово `tcp:127.0.0.1:5762`, перекривається однойменною змінною середовища).
- `lifespan` викликає `await drone.connect()` на старті та `await drone.close()` на зупинці.
- Endpoints:
  - `POST /arm` → 200;
  - `POST /takeoff?alt=<float>` → 200, якщо `1 <= alt <= 120`, інакше 400;
  - `POST /rtl` → 200;
  - `GET /status` → JSON з heartbeat, обовʼязкове поле `custom_mode`.
- Жодного MAVLink-зʼєднання при імпорті модуля — тільки в `lifespan`.

## Кроки

### 1. Клас дрона

```python
import asyncio

from pymavlink import mavutil

CONNECT_TIMEOUT = 15.0


class MavlinkDrone:
    def __init__(self, url: str) -> None:
        self._url = url
        self._conn = None

    async def connect(self) -> None:
        self._conn = await asyncio.wait_for(
            asyncio.to_thread(mavutil.mavlink_connection, self._url),
            timeout=CONNECT_TIMEOUT,
        )
        await asyncio.wait_for(
            asyncio.to_thread(self._conn.wait_heartbeat),
            timeout=CONNECT_TIMEOUT,
        )

    async def close(self) -> None:
        if self._conn is not None:
            await asyncio.to_thread(self._conn.close)
            self._conn = None

    async def arm(self) -> None:
        await asyncio.to_thread(self._conn.arducopter_arm)

    async def takeoff(self, altitude: float) -> None:
        await asyncio.to_thread(self._conn.set_mode, 'GUIDED')
        await asyncio.to_thread(
            self._conn.mav.command_long_send,
            self._conn.target_system, self._conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, altitude,
        )

    async def rtl(self) -> None:
        await asyncio.to_thread(self._conn.set_mode, 'RTL')

    async def heartbeat(self) -> dict:
        message = await asyncio.wait_for(
            asyncio.to_thread(
                self._conn.recv_match,
                type='HEARTBEAT', blocking=True, timeout=5.0,
            ),
            timeout=6.0,
        )
        if message is None:
            raise TimeoutError('no HEARTBEAT received')
        return message.to_dict()
```

### 2. Фабрика з інʼєкцією

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

MAVLINK_URL = os.environ.get('MAVLINK_URL', 'tcp:127.0.0.1:5762')


def create_app(drone=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.drone = drone or MavlinkDrone(MAVLINK_URL)
        await application.state.drone.connect()
        try:
            yield
        finally:
            await application.state.drone.close()

    application = FastAPI(title='ArduPilot Control API', lifespan=lifespan)

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
        return await application.state.drone.heartbeat()

    return application


app = create_app()
```

### 3. Тест інʼєкції (офлайн)

```python
from fastapi.testclient import TestClient


class FakeDrone:
    def __init__(self):
        self.actions = []
        self.connected = False
        self.closed = False

    async def connect(self):
        self.connected = True

    async def close(self):
        self.closed = True

    async def arm(self):
        self.actions.append(('arm',))

    async def takeoff(self, altitude):
        self.actions.append(('takeoff', altitude))

    async def rtl(self):
        self.actions.append(('rtl',))

    async def heartbeat(self):
        return {'type': 2, 'custom_mode': 4}


def test_command_reaches_injected_drone():
    drone = FakeDrone()
    with TestClient(create_app(drone)) as client:
        assert client.post('/takeoff', params={'alt': 20}).status_code == 200
        assert client.post('/takeoff', params={'alt': 500}).status_code == 400
    assert drone.connected and drone.closed
    assert ('takeoff', 20.0) in drone.actions
```

### 4. Запуск із SITL

```bash
uvicorn ardupilot_api:app --port 8080
curl -X POST http://localhost:8080/arm
curl -X POST "http://localhost:8080/takeoff?alt=20"
curl -X POST http://localhost:8080/rtl
curl http://localhost:8080/status
```

## Перевірка

Якщо `ardupilot_api.py` лежить поряд із цим `lab.md`, запускайте з теки модуля:

```bash
python checks/check_lab.py --target .
```

Для файлу в іншій теці вкажіть її: `python checks/check_lab.py --target ~/ardupilot-lab`.

Скрипт імпортує `ardupilot_api.py` з цільової теки, підставляє власний `FakeDrone`, проганяє `/arm`, `/takeoff?alt=20`, `/takeoff?alt=500`, `/rtl`, `/status` і перевіряє, що `lifespan` викликав `connect()` та `close()`, а команда `takeoff(20.0)` дійшла до дрона. Для еталона — `--target solution`.

## Очікуваний результат

- `/arm`, `/rtl`, `/takeoff?alt=20` повертають 200.
- `/takeoff?alt=500` відхиляється з 400.
- `/status` містить `custom_mode`.
- MAVLink-зʼєднання створюється лише в `lifespan`.

## Розбір збоїв

- `OSError: [Errno 98] Address already in use` — `--out=tcpin:0.0.0.0:5762` конфліктує зі стандартним портом SITL; приберіть `--out` або відкрийте інший порт.
- `FAIL: потрібна фабрика create_app(drone=None)` — сервіс створено через `app = FastAPI(...)` без фабрики; перепишіть під `create_app`.
- `FAIL: lifespan має викликати connect() і close()` — забули `await` у `lifespan`.
- `/takeoff?alt=500` повертає 200 — немає перевірки діапазону `[1, 120]`.
- `Зʼєднання при імпорті` — `mavutil.mavlink_connection` викликається на рівні модуля, а не в `lifespan`.
