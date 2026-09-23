# Лабораторна робота 07: REST API для ArduPilot SITL

## Мета

Створити FastAPI-сервіс, який через pymavlink керує симульованим UAV: arm, takeoff, mode change, RTL.

## Передумови

- ArduPilot SITL запущено на TCP `127.0.0.1:5762`.
- Встановлено `fastapi`, `uvicorn`, `pymavlink`.

## Кроки

### 1. Структура проєкту

```text
ardupilot-api/
├── main.py
├── requirements.txt
└── README.md
```

### 2. Підключення до SITL

```python
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymavlink import mavutil


@asynccontextmanager
async def lifespan(app):
    app.state.conn = await asyncio.to_thread(
        mavutil.mavlink_connection, 'tcp:127.0.0.1:5762'
    )
    await asyncio.to_thread(app.state.conn.wait_heartbeat)
    yield
    await asyncio.to_thread(app.state.conn.close)


app = FastAPI(lifespan=lifespan)
```

### 3. Endpoints

```python
@app.post("/arm")
async def arm():
    conn = app.state.conn
    await asyncio.to_thread(conn.arducopter_arm)
    return {"status": "armed"}

@app.post("/takeoff")
async def takeoff(alt: float = 10.0):
    conn = app.state.conn
    await asyncio.to_thread(conn.set_mode, 'GUIDED')
    await asyncio.to_thread(
        conn.mav.command_long_send,
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt,
    )
    return {"status": "takeoff", "alt": alt}

@app.post("/rtl")
async def rtl():
    conn = app.state.conn
    await asyncio.to_thread(conn.set_mode, 'RTL')
    return {"status": "rtl"}
```

### 4. Запуск

```bash
uvicorn main:app --reload
```

### 5. Тестування

```bash
curl -X POST http://localhost:8000/arm
curl -X POST "http://localhost:8000/takeoff?alt=20"
curl -X POST http://localhost:8000/rtl
```

## Перевірка

Перевірте API на фейковому дроні, а потім — на SITL:

```bash
python checks/check_lab.py --target solution
```

Очікування: arm/takeoff/rtl повертають 200, takeoff з alt=500 — 400/422, /status віддає heartbeat.

## Розбір збоїв

- З’єднання при імпорті — сервіс не стартує без SITL
- takeoff без GUIDED/ARM ігнорується автопілотом
- Відсутнє очікування COMMAND_ACK — помилки не видно

## Очікуваний результат

- Робочий REST API.
- SITL реагує на команди.
- Документація в README.
