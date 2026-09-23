"""Спрощена демонстрація FastAPI для телеметрії.

Показує мінімум: Pydantic-модель із фізичними межами, POST і GET.
Сховище — звичайний список без lock і без 404: це приклад для читання,
а не еталон лабораторної. Повне рішення (lock, 404, `/health`) —
у `solution/main.py`, контракт — у `checks/check_lab.py`.

Запуск із теки `examples/`:

    uvicorn fastapi_telemetry:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title='Telemetry demo')


class Telemetry(BaseModel):
    drone_id: str
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    alt: float = Field(ge=-500.0, le=10000.0)
    battery: int = Field(ge=0, le=100)


store: list[Telemetry] = []


@app.post('/telemetry', status_code=201)
async def add_telemetry(data: Telemetry) -> dict[str, str]:
    store.append(data)
    return {'stored': data.drone_id}


@app.get('/telemetry/{drone_id}')
async def list_telemetry(drone_id: str) -> list[Telemetry]:
    return [item for item in store if item.drone_id == drone_id]
