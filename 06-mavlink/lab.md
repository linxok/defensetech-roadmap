# Лабораторна робота 06: MAVLink Gateway

## Мета

Побудувати шлюз `mavlink_gateway.py`, який читає MAVLink-потік і розсилає телеметрію JSON-ом через WebSocket.

## Передумови

- Python 3.11+ і venv:

```bash
python3 -m venv mavlink-lab
source mavlink-lab/bin/activate
pip install pymavlink websockets
```

- Для живої перевірки — ArduPilot SITL: `sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14550`.
- Автоматична перевірка `checks/check_lab.py` офлайн: вона сама пакує MAVLink-кадри через pymavlink, тож SITL для неї не потрібен.

## Контракт

Створіть у своїй робочій теці файл `mavlink_gateway.py` з двома обовʼязковими обʼєктами.

### Функція `mavlink_to_telemetry`

```python
def mavlink_to_telemetry(message) -> dict | None:
    ...
```

- `message` — розпарсене MAVLink-повідомлення pymavlink.
- Повертає JSON-сумісний `dict` або `None`.
- Кожен dict містить поля `type`, `system_id`, `component_id`, `ts`:
  - `type` — рядок з `message.get_type()`;
  - `system_id` — `message.get_srcSystem()`;
  - `component_id` — `message.get_srcComponent()`;
  - `ts` — ISO-8601 UTC, наприклад `datetime.now(timezone.utc).isoformat()`.
- Контрактні типи:
  - `HEARTBEAT` → dict з `type='HEARTBEAT'` і полями `autopilot`, `base_mode`, `custom_mode`, `system_status`;
  - `GLOBAL_POSITION_INT` → dict з `lat = lat / 1e7`, `lon = lon / 1e7`, `alt = alt / 1000.0`, `relative_alt = relative_alt / 1000.0`, `heading = hdg / 100.0` (якщо `hdg == 65535`, то `None`);
  - усі інші типи, зокрема `PING`, → `None`.

Наприклад, кадр з `lat=504501000`, `lon=305234000`, `alt=120000`, `relative_alt=100000`, `hdg=9000` перетворюється на:

```json
{
  "type": "GLOBAL_POSITION_INT",
  "system_id": 7,
  "component_id": 1,
  "ts": "2026-09-23T18:20:00+00:00",
  "lat": 50.4501,
  "lon": 30.5234,
  "alt": 120.0,
  "relative_alt": 100.0,
  "heading": 90.0
}
```

### Клас `TelemetryHub`

```python
class TelemetryHub:
    async def register(self, ws) -> None:
        ...

    async def broadcast(self, payload: dict) -> None:
        ...
```

- `register(ws)` додає клієнта і тримає зʼєднання, доки не завершиться `await ws.wait_closed()`, після чого прибирає клієнта з набору.
- `broadcast(payload)` кодує payload через `json.dumps` і надсилає кожному зареєстрованому клієнту (`await ws.send(data)`).
- Розсилайте через `asyncio.gather(..., return_exceptions=True)`. `asyncio.wait` із корутинами заборонено: у Python 3.11+ це `TypeError: Passing coroutines is forbidden, use tasks explicitly.` Сама лише наявність підрядка `asyncio.wait(` у файлі валить перевірку; `asyncio.wait_for(` — безпечний.

## Кроки

### 1. Читання MAVLink у потоці

```python
import asyncio
import json
from datetime import datetime, timezone

import websockets
from pymavlink import mavutil


async def read_loop(connection, hub, stop):
    while not stop.is_set():
        message = await asyncio.to_thread(
            connection.recv_match, blocking=True, timeout=1.0
        )
        if message is None:
            continue
        payload = mavlink_to_telemetry(message)
        if payload is not None:
            await hub.broadcast(payload)
```

`recv_match(blocking=True)` — синхронний виклик, тому в async-коді його виконують через `asyncio.to_thread`, інакше event loop блокується на секунди.

### 2. Сервер і хаб

```python
async def main():
    connection = await asyncio.to_thread(
        mavutil.mavlink_connection, 'udp:127.0.0.1:14550', source_system=255
    )
    await asyncio.to_thread(connection.wait_heartbeat)
    hub = TelemetryHub()
    stop = asyncio.Event()
    async with websockets.serve(hub.register, '0.0.0.0', 8765):
        reader = asyncio.create_task(read_loop(connection, hub, stop))
        await stop.wait()
        reader.cancel()
        await asyncio.gather(reader, return_exceptions=True)
    await asyncio.to_thread(connection.close)
```

### 3. Запуск

```bash
sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14550
python mavlink_gateway.py --source udp:127.0.0.1:14550 --ws-port 8765
```

Відкрийте `examples/websocket_client.html` (або `wscat -c ws://localhost:8765`) — у сторінці мають зʼявлятися JSON-рядки з `type` `HEARTBEAT` і `GLOBAL_POSITION_INT`.

### 4. Офлайн-перевірка

Якщо `mavlink_gateway.py` лежить поряд із цим `lab.md`, запускайте з теки модуля:

```bash
python checks/check_lab.py --target .
```

Для файлу в іншій теці вкажіть її: `python checks/check_lab.py --target ~/mavlink-lab`.

Скрипт перевіряє саме `mavlink_gateway.py` з цільової теки: пакує pymavlink-фікстури `GLOBAL_POSITION_INT`, `HEARTBEAT` і `PING`, звіряє `type`, `lat` (50.4501) та `alt` (120.0), JSON-сумісність, реєстрацію фейкового клієнта й розсилку. Для еталона використовуйте `--target solution`.

## Очікуваний результат

- `mavlink_gateway.py` проходить `checks/check_lab.py`.
- Live-потік видно у WebSocket-клієнті.
- У коді немає `asyncio.wait(` і блокуючого `recv_match` без `asyncio.to_thread`.

## Розбір збоїв

- `FAIL: у модулі немає mavlink_to_telemetry` — файл лежить не в цільовій теці або названо інакше; перевірте `--target`.
- `невірний lat` — забули поділити `lat` на `1e7` (а `alt` — на `1000`).
- `невірний type` / PING не дає `None` — конвертер транслює зайві типи.
- `TypeError: Passing coroutines is forbidden` — `asyncio.wait` замість `asyncio.gather`.
- `FAIL: блокуючий recv_match викликається без asyncio.to_thread` — читання виконується прямо в async-функції.
- Немає heartbeat — SITL і gateway на різних портах (типово `14550` UDP).
