import requests

mission = {
    "drone_id": "001",
    "waypoints": [
        {"lat": 50.45, "lon": 30.52, "alt": 100},
        {"lat": 50.46, "lon": 30.53, "alt": 100},
    ]
}
resp = requests.post("http://localhost:8000/missions", json=mission)
print(resp.json())
