# Лабораторна робота 07: REST API для ArduPilot SITL

## Мета

Створити FastAPI-сервіс, який через pymavlink керує симульованим UAV: arm, takeoff, mode change, RTL.

## Передумови

- ArduPilot SITL запущено на TCP `127.0.0.1:5762`.
- Встановлено `fastapi`, `uvicorn`, `pymavlink`.

## Кроки

### 1. Структура проєкту

```
ardupilot-api/
├── main.py
├── requirements.txt
└── README.md
```

### 2. Підключення до SITL

```python
from pymavlink import mavutil
from fastapi import FastAPI

app = FastAPI()
conn = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
conn.wait_heartbeat()
```

### 3. Endpoints

```python
@app.post("/arm")
def arm():
    conn.arducopter_arm()
    return {"status": "armed"}

@app.post("/takeoff")
def takeoff(alt: float = 10.0):
    conn.set_mode('GUIDED')
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt
    )
    return {"status": "takeoff", "alt": alt}

@app.post("/rtl")
def rtl():
    conn.set_mode('RTL')
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

## Очікуваний результат

- Робочий REST API.
- SITL реагує на команди.
- Документація в README.
