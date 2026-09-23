# Лабораторна робота 04: FastAPI Telemetry API

## Мета

Створити FastAPI-сервіс, який приймає вимірювання телеметрії, валідує
фізичні межі полів і віддає останнє вимірювання кожного дрона.

## Передумови

- Python 3.11+
- `fastapi`, `uvicorn`, `pydantic` (див. `requirements.txt`); для
  `TestClient` — `httpx` з `requirements-dev.txt`.

## Кроки

### 1. Модель із межами

Файл `main.py`. Поля й обмеження мусять бути саме такими: зайве
обов’язкове поле (наприклад, `ts`) зламає валідний POST у перевірці.

```python
from pydantic import BaseModel, Field

class Telemetry(BaseModel):
    drone_id: str = Field(min_length=1, max_length=64)
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    alt: float = Field(ge=-500.0, le=10000.0)
    battery: int = Field(ge=0, le=100)
```

### 2. Сховище й об’єкт app

```python
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Drone Telemetry API")
store: dict[str, Telemetry] = {}

@app.post("/telemetry", status_code=201)
async def add_telemetry(data: Telemetry) -> dict[str, str]:
    store[data.drone_id] = data
    return {"status": "ok", "stored": data.drone_id}

@app.get("/telemetry/{drone_id}")
async def get_telemetry(drone_id: str) -> Telemetry:
    if drone_id not in store:
        raise HTTPException(status_code=404, detail=f"no telemetry for {drone_id}")
    return store[drone_id]
```

### 3. Запуск

```bash
uvicorn main:app --reload
```

### 4. Ручна перевірка

```bash
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" \
  -d '{"drone_id":"001","lat":50.45,"lon":30.52,"alt":100,"battery":87}'
curl http://localhost:8000/telemetry/001
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" \
  -d '{"drone_id":"001","lat":50.45,"lon":30.52,"alt":100,"battery":150}'
```

## Перевірка

Спочатку еталон, потім тека з вашим `main.py`:

```bash
python 04-python/checks/check_lab.py --target 04-python/solution
python 04-python/checks/check_lab.py --target <тека з вашим main.py>
```

Очікування: 201 на валідний POST, 422 на `battery=150`, `lat=100.0`,
`alt=-1000.0`, 200 і згадка `d1` на `GET /telemetry/d1`, 404 на невідомий дрон.

## Розбір збоїв

- 200 замість 201 — клієнт не розрізняє «прийнято» і «записано»; задайте `status_code=201`.
- Валідний POST повертає 422 — у моделі є зайве обов’язкове поле або межі вужчі за тестові дані.
- `lat=100.0` приймається — модель без `Field(ge=..., le=...)`.
- `ModuleNotFoundError: fastapi` — venv не активовано.

## Очікуваний результат

- `main.py` з моделлю, сховищем і двома endpoints.
- README з curl-прикладами.
- `check_lab.py` проходить на вашій теці.
