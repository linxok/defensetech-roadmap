# Лабораторна робота 04: FastAPI Telemetry API

## Мета

Створити FastAPI-сервіс для збору і роздачі телеметрії.

## Передумови

- Python 3.11+
- `fastapi`, `uvicorn`, `pydantic`

## Кроки

### 1. Моделі

```python
from pydantic import BaseModel
from datetime import datetime

class Telemetry(BaseModel):
    drone_id: str
    ts: datetime
    lat: float
    lon: float
    alt: float
    battery: int
```

### 2. API

```python
from fastapi import FastAPI

app = FastAPI()
store = []

@app.post("/telemetry")
async def add_telemetry(data: Telemetry):
    store.append(data)
    return {"status": "ok"}

@app.get("/telemetry/{drone_id}")
async def get_telemetry(drone_id: str):
    return [t for t in store if t.drone_id == drone_id]
```

### 3. Запуск

```bash
uvicorn main:app --reload
```

### 4. Тестування

```bash
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" -d '{"drone_id":"001","ts":"2024-01-01T00:00:00","lat":50.45,"lon":30.52,"alt":100,"battery":87}'
```

## Очікуваний результат

- FastAPI сервіс.
- POST / GET endpoints.
- README.
