"""Telemetry API: валідація, сховище, коректні коди відповіді.

Запуск:

    uvicorn main:app --reload

Перевірка (офлайн): див. `../checks/check_lab.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title='Drone Telemetry API', version='1.0.0')


class Telemetry(BaseModel):
    """Одне вимірювання. Межі відповідають фізичним обмеженням дрона."""

    drone_id: str = Field(min_length=1, max_length=64)
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    alt: float = Field(ge=-500.0, le=10000.0)
    battery: int = Field(ge=0, le=100)


class TelemetryStore:
    """Останнє вимірювання на дрон. Потокобезпечний, без зовнішніх залежностей."""

    def __init__(self) -> None:
        self._items: dict[str, Telemetry] = {}
        self._lock = Lock()

    def put(self, item: Telemetry) -> None:
        with self._lock:
            self._items[item.drone_id] = item

    def get(self, drone_id: str) -> Telemetry | None:
        with self._lock:
            return self._items.get(drone_id)

    def all(self) -> list[Telemetry]:
        with self._lock:
            return list(self._items.values())


store = TelemetryStore()


@app.post('/telemetry', status_code=201)
async def ingest(item: Telemetry) -> dict[str, str]:
    store.put(item)
    return {'stored': item.drone_id, 'ts': datetime.now(timezone.utc).isoformat()}


@app.get('/telemetry/{drone_id}')
async def latest(drone_id: str) -> Telemetry:
    item = store.get(drone_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f'no telemetry for {drone_id}')
    return item


@app.get('/telemetry')
async def list_latest() -> list[Telemetry]:
    return store.all()


@app.get('/health')
async def health() -> dict[str, int]:
    return {'drones': len(store.all())}
