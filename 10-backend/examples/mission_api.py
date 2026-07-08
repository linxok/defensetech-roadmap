from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Waypoint(BaseModel):
    lat: float
    lon: float
    alt: float

class Mission(BaseModel):
    drone_id: str
    waypoints: list[Waypoint]

@app.post("/missions")
async def create_mission(mission: Mission):
    return {"status": "created", "waypoints": len(mission.waypoints)}
