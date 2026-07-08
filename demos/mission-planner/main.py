from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()
missions = {}

class Waypoint(BaseModel):
    lat: float
    lon: float
    alt: float

class Mission(BaseModel):
    name: str
    waypoints: List[Waypoint]

@app.post('/missions')
async def create_mission(mission: Mission):
    mission_id = len(missions) + 1
    missions[mission_id] = mission
    return {'id': mission_id, 'mission': mission}

@app.get('/missions/{mission_id}')
async def get_mission(mission_id: int):
    return missions.get(mission_id)

@app.post('/missions/{mission_id}/upload')
async def upload_mission(mission_id: int):
    mission = missions.get(mission_id)
    if not mission:
        return {'error': 'not found'}
    # Placeholder for MAVLink upload
    return {'status': 'uploaded', 'waypoints': len(mission.waypoints)}
