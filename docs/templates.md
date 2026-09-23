# Шаблони та фрагменти

Спільні шаблони для мініпроєктів і самостійних робіт. Модулі
посилаються сюди зі своїх `templates.md` і не дублюють код.

## Шаблон README проєкту

```markdown
# Назва проєкту

Одне речення: яку проблему вирішує.

## Швидкий старт

    docker compose up --build

## Архітектура

Схема (mermaid) і пояснення потоків даних.

## Метрики

- Латентність: X мс (p95)
- Throughput: Y msg/s

## Тести

    pytest -q

## Обмеження

Що не реалізовано і чому.
```

## Dockerfile для Python-сервісу

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml

Секція `version` застаріла в Compose v2 — не додавайте її.

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://app:secret@db:5432/app
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
```

## GitHub Actions: тести

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -q
```

## Async worker, що не блокує event loop

```python
import asyncio
import json


async def consume(message: str) -> None:
    # блокуючу роботу (БД, файли, синхронні клієнти) виносимо в потік
    payload = await asyncio.to_thread(json.loads, message)
    await handle(payload)


async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(consume('{"alt": 120}'))


if __name__ == "__main__":
    asyncio.run(main())
```

## FastAPI з lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started = True
    yield
    app.state.started = False


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": app.state.started}
```

## Тест, який падає на поганому вході

```python
import pytest
from pydantic import ValidationError

from solution.models import Telemetry


def test_rejects_bad_battery():
    with pytest.raises(ValidationError):
        Telemetry(drone_id="d1", battery=101)


def test_accepts_valid():
    assert Telemetry(drone_id="d1", battery=87).battery == 87
```

## MAVLink-повідомлення з фікстури

```python
from pymavlink.dialects.v20 import ardupilotmega as mavlink

master = mavlink.MAVLink(None)


def heartbeat_bytes() -> bytes:
    msg = master.heartbeat_encode(
        type=mavlink.MAV_TYPE_QUADROTOR,
        autopilot=mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        base_mode=0,
        custom_mode=0,
        system_status=mavlink.MAV_STATE_ACTIVE,
    )
    return msg.pack(master)
```

## CMake для C++ проєкту

```cmake
cmake_minimum_required(VERSION 3.22)
project(mavlink_parser CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(parser src/main.cpp)
target_compile_options(parser PRIVATE -Wall -Wextra -Werror)

enable_testing()
add_executable(parser_test tests/parser_test.cpp)
add_test(NAME parser_test COMMAND parser_test)
```

## ROS2 node (rclpy)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Bridge(Node):
    def __init__(self) -> None:
        super().__init__('mavlink_bridge')
        self.pub = self.create_publisher(String, 'telemetry', 10)
        self.create_timer(0.1, self.tick)

    def tick(self) -> None:
        msg = String()
        msg.data = '{"alt": 120.0}'
        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## React-компонент з WebSocket

```tsx
import { useEffect, useState } from 'react';

export default function TelemetryFeed({ url }: { url: string }) {
  const [last, setLast] = useState<string>('—');

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => setLast(event.data);
    return () => ws.close();
  }, [url]);

  return <pre>{last}</pre>;
}
```
