# Лабораторна робота 10: Telemetry Pipeline

## Мета

Побудувати end-to-end pipeline: UDP → FastAPI → RabbitMQ → Worker → PostgreSQL → API.

## Передумови

- Docker і Docker Compose.
- PostgreSQL, RabbitMQ, Redis локально або в контейнерах.

## Кроки

### 1. Docker Compose стек

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
  rabbitmq:
    image: rabbitmq:3-management
  redis:
    image: redis:7
```

### 2. FastAPI gateway

```python
import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
import pika


@asynccontextmanager
async def lifespan(app):
    app.state.connection = await asyncio.to_thread(
        pika.BlockingConnection, pika.ConnectionParameters('localhost')
    )
    app.state.channel = await asyncio.to_thread(app.state.connection.channel)
    await asyncio.to_thread(
        app.state.channel.queue_declare, queue='telemetry', durable=True
    )
    yield
    await asyncio.to_thread(app.state.connection.close)


app = FastAPI(lifespan=lifespan)


@app.post("/telemetry")
async def receive_telemetry(data: dict):
    body = json.dumps(data).encode()
    await asyncio.to_thread(
        app.state.channel.basic_publish,
        exchange='', routing_key='telemetry', body=body,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    return {"status": "queued"}
```

### 3. Worker

```python
import json
import pika
import psycopg2

DSN = "dbname=drone user=postgres password=secret host=localhost"

def callback(ch, method, properties, body):
    data = json.loads(body)
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO telemetry (drone_id, alt) VALUES (%s, %s)",
                (data["drone_id"], data.get("alt")),
            )
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="telemetry", durable=True)
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue="telemetry", on_message_callback=callback)
channel.start_consuming()
```

З’єднання створюються лише всередині циклу воркера, а `ack` — після
успішного запису; інакше при падінні між ack і INSERT дані губляться.

### 4. Тестування

```bash
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" -d '{"drone_id":"001","alt":100}'
```

## Перевірка

Підніміть стек, надішліть пакет і перевірте контракт:

```bash
python checks/check_lab.py --target solution
```

Потім переконайтеся, що рядок з’явився в PostgreSQL: `SELECT count(*) FROM telemetry;`.

## Розбір збоїв

- Сервіс не стартує без брокера — з’єднання має бути в lifespan
- Дані в черзі, але не в БД — воркер не підключився
- Дублі при повторній доставці — немає ON CONFLICT

## Очікуваний результат

- Працюючий pipeline.
- Дані в PostgreSQL.
- README і docker-compose.yml.
