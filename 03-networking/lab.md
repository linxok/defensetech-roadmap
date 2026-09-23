# Лабораторна робота 03: UDP → WebSocket bridge

## Мета

Зібрати асинхронний міст: UDP-датаграми з телеметрією проходять валідацію, перетворюються на JSON і розсилаються всім підключеним WebSocket-клієнтам. Битий пакет збільшує лічильник помилок, але не зупиняє процес.

## Передумови

- Python 3.11+.
- Пакет `websockets`.
- Вільні порти 14550 (UDP) і 8765 (WebSocket).

## Контракт перевірки

`checks/check_lab.py` завантажує `solution/udp_ws_bridge.py` і перевіряє рівно три публічні імена:

- `parse_packet(data: bytes) -> dict` — повертає словник або піднімає `ValueError`;
- `TelemetryHub` — з async-методами `register(websocket)` і `broadcast(payload)`;
- `UdpTelemetryProtocol(hub)` — з методом `datagram_received(data, addr)`.

Перевірка окремо забороняє виклик `asyncio.wait(` у вихідному коді — розсилка робиться через `asyncio.gather`.

## Кроки

### 1. Каркас файлу

Створіть `solution/udp_ws_bridge.py` з імпортами та логером.

```python
import argparse
import asyncio
import json
import logging
from typing import Any

import websockets

log = logging.getLogger('udp_ws_bridge')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
```

### 2. Валідатор пакета

Функція приймає сирі байти датаграми. Валідним вважається лише JSON-обʼєкт із полем `drone_id` або `type`; усе інше — `ValueError`.

```python
def parse_packet(data: bytes) -> dict[str, Any]:
    if not data:
        raise ValueError('empty datagram')
    try:
        packet = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'invalid telemetry packet: {exc}') from exc
    if not isinstance(packet, dict):
        raise ValueError('telemetry packet must be a JSON object')
    if 'drone_id' not in packet and 'type' not in packet:
        raise ValueError('packet must contain drone_id or type')
    return packet
```

Відхилятися мають: порожній `b''`, `b'not-json'`, масив `b'[1, 2, 3]'` і обʼєкт без потрібних ключів, наприклад `b'{"foo": 1}'`. Натомість `parse_packet(b'{"drone_id": "d1", "alt": 120}')` повертає словник із `drone_id == 'd1'`.

### 3. Хаб WebSocket-клієнтів

`register` тримає зʼєднання, доки клієнт не закриється, і прибирає його зі списку. `broadcast` надсилає кадр усім через `asyncio.gather(..., return_exceptions=True)`, щоб помилка одного надсилання не зривала розсилку решті.

```python
class TelemetryHub:
    def __init__(self) -> None:
        self.clients: list[Any] = []

    async def register(self, websocket: Any) -> None:
        self.clients.append(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._forget(websocket)

    def _forget(self, websocket: Any) -> None:
        if websocket in self.clients:
            self.clients.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        recipients = tuple(self.clients)
        if not recipients:
            return
        frame = json.dumps(payload, ensure_ascii=False)
        outcomes = await asyncio.gather(
            *(recipient.send(frame) for recipient in recipients),
            return_exceptions=True,
        )
        for recipient, outcome in zip(recipients, outcomes):
            if isinstance(outcome, Exception):
                log.warning('client dropped after send error: %s', outcome)
                self._forget(recipient)
```

### 4. UDP-протокол

Протокол отримує датаграми синхронно, тому валідація виконується одразу, а розсилка планується як задача в поточному event loop. Сміттєвий пакет лише збільшує лічильник `malformed_packets`.

```python
class UdpTelemetryProtocol(asyncio.DatagramProtocol):
    def __init__(self, hub: TelemetryHub) -> None:
        self.hub = hub
        self.malformed_packets = 0

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            payload = parse_packet(data)
        except ValueError as exc:
            self.malformed_packets += 1
            log.warning('malformed datagram from %s: %s', addr, exc)
            return
        asyncio.get_running_loop().create_task(self.hub.broadcast(payload))

    def error_received(self, exc: Exception) -> None:
        log.warning('udp transport error: %s', exc)
```

### 5. Запуск моста

```python
async def run(udp_port: int, ws_port: int) -> None:
    hub = TelemetryHub()
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UdpTelemetryProtocol(hub), local_addr=('0.0.0.0', udp_port)
    )
    log.info('UDP listening on :%d', udp_port)
    try:
        async with websockets.serve(hub.register, '0.0.0.0', ws_port):
            log.info('WebSocket server on ws://0.0.0.0:%d', ws_port)
            await asyncio.Future()
    finally:
        transport.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--udp-port', type=int, default=14550)
    parser.add_argument('--ws-port', type=int, default=8765)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.udp_port, args.ws_port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
```

## Ручна перевірка

Запустіть міст:

```bash
python solution/udp_ws_bridge.py --udp-port 14550 --ws-port 8765
```

В іншому терміналі надішліть коректний і битий пакети:

```bash
python examples/udp_client.py --host 127.0.0.1 --port 14550
```

У журналі моста бита датаграма дає `warning`, а WebSocket-клієнти отримують лише коректний кадр.

## Автоматична перевірка

```bash
python checks/check_lab.py --target solution
```

Очікуваний вивід: `PASS: bridge валідує UDP-пакети та безпечно розсилає їх`.

## Розбір збоїв

- Порт зайнятий — `ss -lunp | grep 14550` покаже процес.
- Пакет не доходить — перевірте адресу: `127.0.0.1` vs `0.0.0.0`.
- Клієнт відключається і не видаляється зі списку — ріст памʼяті.
- `RuntimeError: Passing coroutines` — у коді `asyncio.wait` замість `asyncio.gather`.

## Очікуваний результат

- `udp_ws_bridge.py` із контрактом вище.
- Живий потік телеметрії у WebSocket-клієнта.
- Битий пакет не валить міст.
