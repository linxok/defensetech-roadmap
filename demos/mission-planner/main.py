"""Мінімальний Mission Planner API (демо).

Запуск:

    uvicorn main:app --reload
"""

from __future__ import annotations

from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title='Mission Planner Demo')


class Waypoint(BaseModel):
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    alt: float = Field(gt=0.0, le=500.0)


class Mission(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    waypoints: list[Waypoint]

    @field_validator('waypoints')
    @classmethod
    def at_least_two(cls, value: list[Waypoint]) -> list[Waypoint]:
        if len(value) < 2:
            raise ValueError('mission needs at least 2 waypoints')
        return value


class MissionStore:
    def __init__(self) -> None:
        self._items: dict[int, Mission] = {}
        self._lock = Lock()

    def add(self, mission: Mission) -> int:
        with self._lock:
            mission_id = len(self._items) + 1
            self._items[mission_id] = mission
            return mission_id

    def get(self, mission_id: int) -> Mission | None:
        with self._lock:
            return self._items.get(mission_id)


store = MissionStore()


@app.post('/missions', status_code=201)
async def create_mission(mission: Mission) -> dict:
    mission_id = store.add(mission)
    return {'id': mission_id, 'waypoints': len(mission.waypoints)}


@app.get('/missions/{mission_id}')
async def get_mission(mission_id: int) -> Mission:
    mission = store.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail=f'mission {mission_id} not found')
    return mission


@app.post('/missions/{mission_id}/upload')
async def upload_mission(mission_id: int) -> dict:
    mission = store.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail=f'mission {mission_id} not found')
    return {'status': 'accepted', 'waypoints': len(mission.waypoints)}
