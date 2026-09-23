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
import asyncio
import json
import websockets

async def ws_handler(websocket):
    server.clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        server.clients.discard(websocket)

async def broadcast(payload):
    if not server.clients:
        return
    data = json.dumps(payload)
    await asyncio.gather(
        *(c.send(data) for c in server.clients), return_exceptions=True
    )
```

### 3. Тестування

```bash
python udp_ws_bridge.py
# in another terminal
python udp_client.py
```

## Перевірка

Надішліть валідний і битий пакети, потім перевірте лічильники:

```bash
python checks/check_lab.py --target solution
```

Валідний пакет доходить до WebSocket-клієнта, битий не валить процес.

## Розбір збоїв

- Порт зайнятий — `ss -lunp | grep 14550` покаже процес
- Пакет не доходить — перевірте адресу: `127.0.0.1` vs `0.0.0.0`
- Клієнт відключається і не видаляється зі списку — ріст пам’яті

## Очікуваний результат

- UDP + WebSocket bridge.
- Клієнт отримує live дані.
