from fastapi import FastAPI, WebSocket
import asyncio
import websockets

app = FastAPI()

async def upstream():
    async with websockets.connect('ws://localhost:8765') as ws:
        while True:
            msg = await ws.recv()
            for client in app.state.ws_clients:
                await client.send_text(msg)

@app.on_event('startup')
async def startup():
    app.state.ws_clients = []
    asyncio.create_task(upstream())

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.state.ws_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    finally:
        app.state.ws_clients.remove(websocket)
