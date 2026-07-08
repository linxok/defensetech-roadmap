import asyncio
import json
import socket
import websockets

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

async def udp_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 14550))
    sock.setblocking(False)
    loop = asyncio.get_running_loop()
    while True:
        data, _ = await loop.sock_recvfrom(sock, 1024)
        try:
            msg = json.loads(data.decode())
            print(f'UDP: {msg}')
            await broadcast(msg)
        except json.JSONDecodeError:
            pass

async def main():
    asyncio.create_task(udp_loop())
    async with websockets.serve(register, 'localhost', 8765):
        print('Gateway on ws://localhost:8765')
        await asyncio.Future()

asyncio.run(main())
