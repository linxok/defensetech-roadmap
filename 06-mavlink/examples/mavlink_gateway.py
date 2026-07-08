import asyncio
import json
import websockets
from pymavlink import mavutil

clients = set()

async def register(websocket):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def broadcast(data):
    if clients:
        await asyncio.wait([c.send(json.dumps(data)) for c in clients])

async def telemetry_loop(conn):
    while True:
        msg = conn.recv_match(blocking=True)
        if msg is None:
            continue
        data = msg.to_dict()
        await broadcast(data)

async def main():
    conn = mavutil.mavlink_connection('udp:127.0.0.1:14550')
    conn.wait_heartbeat()
    print(f"Connected to system {conn.target_system}")
    asyncio.create_task(telemetry_loop(conn))
    async with websockets.serve(register, 'localhost', 8765):
        print("WebSocket server on ws://localhost:8765")
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
