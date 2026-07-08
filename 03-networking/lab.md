# Лабораторна робота 03: UDP Telemetry Server

## Мета

Побудувати UDP-сервер, який приймає telemetry-пакети і розсилає їх через WebSocket.

## Передумови

- Python 3.11+
- `asyncio`, `websockets`

## Кроки

### 1. UDP server

```python
import asyncio

class UDPServer:
    def __init__(self):
        self.clients = []

    async def handle(self):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self),
            local_addr=('0.0.0.0', 14550)
        )
        return transport

class UDPProtocol:
    def __init__(self, server):
        self.server = server

    def datagram_received(self, data, addr):
        print(f"UDP: {data.hex()}")
```

### 2. WebSocket server

```python
import websockets

async def ws_handler(websocket, path):
    server.clients.append(websocket)
    try:
        await websocket.wait_closed()
    finally:
        server.clients.remove(websocket)

async def broadcast(data):
    if server.clients:
        await asyncio.wait([c.send(data) for c in server.clients])
```

### 3. Тестування

```bash
python udp_ws_bridge.py
# in another terminal
python udp_client.py
```

## Очікуваний результат

- UDP + WebSocket bridge.
- Клієнт отримує live дані.
