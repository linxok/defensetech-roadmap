# Лабораторна робота 10: Telemetry Pipeline

## Мета

Побудувати end-to-end pipeline HTTP → FastAPI → RabbitMQ → Worker → PostgreSQL
і перевірити контракт API без брокера.

## Передумови

- Docker і Docker Compose v2 (`docker compose version`).
- Python 3.10+ і залежності: `pip install -r requirements.txt -r requirements-dev.txt`
  (з кореня репозиторію; `requirements-dev.txt` дає `httpx` для `TestClient`).
- Контрактна перевірка не потребує ні Docker, ні брокера.

## Контракт перевірки

`python 10-backend/checks/check_lab.py --target <тека>` очікує `main.py`, у якому:

- імпорт модуля не відкриває жодного зʼєднання;
- є фабрика `create_app(publisher=None) -> FastAPI`;
- `create_app(FakePublisher())` у lifespan викликає `await publisher.connect()`,
  а після виходу — `await publisher.close()`;
- `POST /telemetry` приймає JSON, робить `await publisher.publish(json.dumps(data).encode())`
  і повертає 200 або 202;
- `GET /health` повертає непорожній JSON (наприклад `{"status": "ok"}`).

Потрібна саме фабрика: `app = FastAPI(...)` напряму в модулі не пройде —
потрібні `def create_app(...)` і `app = create_app()` унизу файлу.

## Кроки

### 1. Docker Compose стек

Створіть `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: drone
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: drone
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U drone -d drone"]
      interval: 5s
      retries: 10
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 5s
      retries: 10
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 10
```

`version: '3.8'` не потрібен: Compose v2 ігнорує це поле й попереджає про нього.

```bash
docker compose up -d
docker compose ps
```

Очікувано: postgres, rabbitmq і redis у стані `healthy` (10–20 с).

### 2. База й таблиця telemetry

БД `drone` створює сам контейнер postgres через `POSTGRES_DB`, тому `createdb`
не потрібен. Створіть таблицю:

```bash
docker compose exec postgres psql -U drone -d drone -c "
CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    drone_id TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    alt DOUBLE PRECISION,
    battery INT
);
CREATE INDEX IF NOT EXISTS telemetry_drone_ts_idx ON telemetry (drone_id, ts DESC);"
```

Перевірка:

```bash
docker compose exec postgres psql -U drone -d drone -c "\dt"
```

Очікувано: у списку є таблиця `telemetry`. Воркер також виконує
`CREATE TABLE IF NOT EXISTS` перед першим INSERT, тому повторний запуск
нешкідливий.

### 3. FastAPI gateway — `main.py`

```python
"""Telemetry pipeline: HTTP → RabbitMQ без блокування event loop.

Запуск:

    RABBITMQ_URL=amqp://guest:guest@localhost:5672/ \
        uvicorn main:app --reload

Важливо: з'єднання з брокером створюється у lifespan, а не при імпорті.
Синхронний pika виконується через asyncio.to_thread.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Protocol

import pika
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

log = logging.getLogger('telemetry_pipeline')

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
QUEUE = 'telemetry'


class Publisher(Protocol):
    async def connect(self) -> None: ...

    async def publish(self, body: bytes) -> None: ...

    async def close(self) -> None: ...


class RabbitPublisher:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection: pika.BlockingConnection | None = None
        self._channel: Any = None

    async def connect(self) -> None:
        params = pika.URLParameters(self._url)
        params.blocked_connection_timeout = 10
        self._connection = await asyncio.wait_for(
            asyncio.to_thread(pika.BlockingConnection, params), timeout=10
        )
        self._channel = await asyncio.to_thread(self._connection.channel)
        await asyncio.to_thread(
            self._channel.queue_declare, queue=QUEUE, durable=True
        )

    async def publish(self, body: bytes) -> None:
        if self._channel is None:
            raise RuntimeError('publisher is not connected')
        await asyncio.to_thread(
            self._channel.basic_publish,
            exchange='',
            routing_key=QUEUE,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    async def close(self) -> None:
        if self._connection is not None:
            await asyncio.to_thread(self._connection.close)
            self._connection = None
            self._channel = None


def create_app(publisher: Publisher | None = None) -> FastAPI:
    metrics: dict[str, int] = {'accepted': 0, 'publish_errors': 0}

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.publisher = publisher or RabbitPublisher(RABBITMQ_URL)
        await app.state.publisher.connect()
        try:
            yield
        finally:
            await app.state.publisher.close()

    app = FastAPI(title='Telemetry Pipeline', lifespan=lifespan)

    @app.post('/telemetry', status_code=202)
    async def receive(data: dict) -> dict[str, str]:
        try:
            body = json.dumps(data).encode()
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f'invalid payload: {exc}') from exc
        try:
            await app.state.publisher.publish(body)
        except Exception:
            metrics['publish_errors'] += 1
            log.exception('failed to publish telemetry')
            raise
        metrics['accepted'] += 1
        return {'status': 'queued'}

    @app.get('/health')
    async def health() -> dict[str, str]:
        return {'status': 'ok'}

    @app.get('/metrics')
    async def metrics_endpoint() -> PlainTextResponse:
        lines = (
            '# HELP telemetry_accepted_total Telemetry frames accepted by the API.',
            '# TYPE telemetry_accepted_total counter',
            f"telemetry_accepted_total {metrics['accepted']}",
            '# HELP telemetry_publish_errors_total Failed publishes to the queue.',
            '# TYPE telemetry_publish_errors_total counter',
            f"telemetry_publish_errors_total {metrics['publish_errors']}",
        )
        return PlainTextResponse('\n'.join(lines) + '\n')

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
```

Запуск:

```bash
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ uvicorn main:app --reload
```

Очікуваний вивід: `Uvicorn running on http://127.0.0.1:8000`.

### 4. Worker — `worker.py`

```python
"""Worker: RabbitMQ → PostgreSQL з ретраями та коректним закриттям.

Запуск:

    DATABASE_URL=postgresql://drone:secret@localhost:5432/drone \
    RABBITMQ_URL=amqp://guest:guest@localhost:5672/ \
        python worker.py
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone

import pika
import psycopg2

log = logging.getLogger('telemetry_worker')
logging.basicConfig(level=logging.INFO)

DSN = os.environ.get('DATABASE_URL', 'postgresql://drone:secret@localhost:5432/drone')
BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
QUEUE = 'telemetry'

DDL = """
CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    drone_id TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    alt DOUBLE PRECISION,
    battery INT
)
"""

INSERT = """
INSERT INTO telemetry (drone_id, ts, lat, lon, alt, battery)
VALUES (%s, %s, %s, %s, %s, %s)
"""


def store(data: dict) -> None:
    with psycopg2.connect(DSN, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(
                INSERT,
                (
                    data['drone_id'],
                    datetime.now(timezone.utc),
                    data.get('lat'),
                    data.get('lon'),
                    data.get('alt'),
                    data.get('battery'),
                ),
            )


def on_message(channel, method, properties, body) -> None:
    try:
        data = json.loads(body)
        store(data)
    except (json.JSONDecodeError, KeyError) as exc:
        log.warning('rejecting malformed message: %s', exc)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_once() -> None:
    with pika.BlockingConnection(pika.URLParameters(BROKER_URL)) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
        log.info('worker started, waiting for messages')
        channel.start_consuming()


def main() -> None:
    while True:
        try:
            consume_once()
        except (pika.exceptions.AMQPConnectionError, psycopg2.OperationalError) as exc:
            log.error('broker/db unavailable (%s), retrying in 5s', exc)
            time.sleep(5)


if __name__ == '__main__':
    main()
```

Запуск у другому терміналі:

```bash
DATABASE_URL=postgresql://drone:secret@localhost:5432/drone \
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ \
python worker.py
```

Очікуваний вивід: `worker started, waiting for messages`.

`ack` надсилається лише після успішного INSERT; інакше при падінні між `ack` і
записом дані губляться.

### 5. End-to-end перевірка

```bash
curl -i -X POST http://localhost:8000/telemetry \
  -H "Content-Type: application/json" \
  -d '{"drone_id":"001","alt":100,"battery":87}'
```

Очікувано: `HTTP/1.1 202 Accepted` і тіло `{"status":"queued"}`.

```bash
docker compose exec postgres psql -U drone -d drone -tAc "SELECT count(*) FROM telemetry;"
```

Очікувано: `1` (після другого curl — відповідно більше).

```bash
curl -s http://localhost:8000/metrics
```

Очікувано: Prometheus-текст, зокрема `telemetry_accepted_total 1`.

## Очікуваний результат

- Працюючий pipeline HTTP → RabbitMQ → PostgreSQL.
- `main.py` із `create_app(publisher=None)`, `/health` і `/metrics`.
- Рядок у таблиці `telemetry` після curl.
- `docker-compose.yml` із postgres/rabbitmq/redis.

## Перевірка

Контракт без брокера (імпорт, фабрика, інʼєкція fake-publisher):

```bash
cd <репозиторій>
python 10-backend/checks/check_lab.py --target 10-backend/solution
python 10-backend/checks/check_lab.py --target <тека з main.py>
```

Очікуваний вивід:

```text
PASS: pipeline публікує телеметрію та коректно закриває зʼєднання
```

## Розбір збоїв

- `ModuleNotFoundError: No module named 'fastapi'` — не виконано
  `pip install -r requirements.txt`.
- Сервіс не стартує без брокера — зʼєднання має бути в lifespan, а не при імпорті.
- Дані в черзі, але не в БД — воркер не підключився до RabbitMQ або PostgreSQL;
  його лог показує `broker/db unavailable ... retrying in 5s`.
- Дублі при повторній доставці — немає `ON CONFLICT` (домашнє завдання).
