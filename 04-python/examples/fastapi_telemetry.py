from fastapi import FastAPI

app = FastAPI()

@app.get("/telemetry/{drone_id}")
async def get_telemetry(drone_id: str):
    return {"drone_id": drone_id, "alt": 120, "battery": 87}
