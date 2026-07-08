# Лабораторна робота 06: MAVLink Gateway

## Мета

Побудувати Python-шлюз, який отримує MAVLink-повідомлення від SITL і передає їх у форматі JSON через WebSocket.

## Передумови

- ArduPilot SITL запущено (`sim_vehicle.py -v ArduCopter`).
- Python 3.11+ і venv.
- Встановлено `pymavlink`, `websockets`.

## Кроки

### 1. Підготовка середовища

```bash
cd ~/projects
python3 -m venv mavlink-lab
source mavlink-lab/bin/activate
pip install pymavlink websockets
```

### 2. Підключення до SITL

```python
from pymavlink import mavutil

conn = mavutil.mavlink_connection('udp:127.0.0.1:14550')
conn.wait_heartbeat()
print(f"Connected to system {conn.target_system}")
```

### 3. Читання повідомлень

```python
while True:
    msg = conn.recv_match(blocking=True)
    if msg is None:
        continue
    print(msg.to_dict())
```

### 4. Фільтрація GPS і батареї

```python
msg = conn.recv_match(type=['GLOBAL_POSITION_INT', 'BATTERY_STATUS'], blocking=True)
if msg.get_type() == 'GLOBAL_POSITION_INT':
    data = {
        'lat': msg.lat / 1e7,
        'lon': msg.lon / 1e7,
        'alt': msg.alt / 1000,
    }
elif msg.get_type() == 'BATTERY_STATUS':
    data = {'battery': msg.battery_remaining}
```

### 5. WebSocket broadcast

```python
import asyncio
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
        await asyncio.wait([c.send(data) for c in clients])

async def main():
    asyncio.create_task(telemetry_loop())
    async with websockets.serve(register, 'localhost', 8765):
        await asyncio.Future()

async def telemetry_loop():
    while True:
        msg = conn.recv_match(blocking=True)
        await broadcast(str(msg.to_dict()))

asyncio.run(main())
```

### 6. Тестування

1. Запустіть SITL.
2. Запустіть шлюз.
3. Відкрийте `examples/websocket_client.html` або `wscat`.
4. Переконайтеся, що JSON надходить.

## Очікуваний результат

- Робочий `mavlink_gateway.py`.
- WebSocket-клієнт, що отримує live telemetry.
- README з інструкцією.
